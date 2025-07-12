from flask import Flask, request, jsonify
from flask_cors import CORS
from database.db import db
from datetime import datetime, timezone
import os
import logging

# Handle .env file loading with better error handling
try:
    from dotenv import load_dotenv
    try:
        load_dotenv(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            load_dotenv(encoding='latin-1')
            print("Warning: .env file loaded with latin-1 encoding")
        except:
            print("Warning: Could not load .env file due to encoding issues")
except ImportError:
    print("Warning: python-dotenv not installed")
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

# Import scrapers
from scraper.universal_scraper import UniversalReviewScraper
from scraper.flipkart_scraper import FlipkartScraper
from scraper.amazon_scraper import AmazonScraper
from ai.summarizer import ReviewSummarizer
from database.models import db, Product, Review, Analysis
from utils.universal_url_validator import UniversalURLValidator
from utils.rate_limiter import RateLimiter
from utils.config_loader import config_loader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///review_summarizer.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize extensions
db.init_app(app)
rate_limiter = RateLimiter()

# Initialize scrapers and AI
universal_scraper = UniversalReviewScraper()
flipkart_scraper = FlipkartScraper()
amazon_scraper = AmazonScraper()
summarizer = ReviewSummarizer()
url_validator = UniversalURLValidator()

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/api/analyze', methods=['POST'])
def analyze_reviews():
    try:
        # Rate limiting
        client_ip = request.remote_addr
        if not rate_limiter.allow_request(client_ip):
            return jsonify({'error': 'Too many requests. Please wait before trying again.'}), 429

        data = request.get_json()
        product_url = data.get('url')

        if not product_url:
            return jsonify({'error': 'Product URL is required'}), 400

        # Validate URL
        validation_result = url_validator.validate_url(product_url)
        if not validation_result['valid']:
            logger.error(f"URL validation failed for {product_url}: {validation_result['error']}")
            return jsonify({'error': validation_result['error']}), 400

        logger.info(f"URL validation successful. Platform: {validation_result['platform']}")
        platform = validation_result['platform']
        
        # Check if analysis already exists
        existing_product = Product.query.filter_by(url=product_url).first()

        # Choose scraper based on platform
        if platform == 'flipkart':
            scraper = flipkart_scraper
            logger.info("Using specialized Flipkart scraper")
        elif platform == 'amazon':
            scraper = amazon_scraper
            logger.info("Using specialized Amazon scraper")
        else:
            scraper = universal_scraper
            logger.info(f"Using universal scraper for platform: {platform}")

        # Scrape product and reviews
        logger.info(f"Starting scraping for URL: {product_url}")
        scraping_result = scraper.scrape_product(product_url)
        
        if not scraping_result['success']:
            return jsonify({'error': scraping_result['error']}), 400

        product_data = scraping_result['product']
        reviews_data = scraping_result['reviews']

        if len(reviews_data) == 0:
            return jsonify({'error': 'No reviews found for this product'}), 400

        # Save or update product
        if existing_product:
            product = existing_product
            product.name = product_data['name']
            product.image_url = product_data['image_url']
            product.price = product_data.get('price')
            product.rating = product_data.get('rating')
            product.last_analyzed = datetime.now(timezone.utc)
        else:
            product = Product(
                url=product_url,
                name=product_data['name'],
                image_url=product_data['image_url'],
                price=product_data.get('price'),
                rating=product_data.get('rating'),
                platform=platform,
                last_analyzed=datetime.now(timezone.utc)
            )
            db.session.add(product)
        
        db.session.commit()

        # Save reviews
        Review.query.filter_by(product_id=product.id).delete()  # Clear old reviews
        for review_data in reviews_data:
            review = Review(
                product_id=product.id,
                text=review_data['text'],
                rating=review_data['rating'],
                author=review_data.get('author'),
                date=review_data.get('date')
            )
            db.session.add(review)
        
        db.session.commit()

        # Generate AI summary
        logger.info("Generating AI summary")
        summary_result = summarizer.summarize_reviews(reviews_data, product_data['name'])
        
        if not summary_result['success']:
            return jsonify({'error': 'Failed to generate summary'}), 500

        # Save analysis
        analysis = Analysis(
            product_id=product.id,
            total_reviews=len(reviews_data),
            summary_pros=summary_result['pros'],
            summary_cons=summary_result['cons'],
            sentiment_positive=summary_result['sentiment']['positive'],
            sentiment_neutral=summary_result['sentiment']['neutral'],
            sentiment_negative=summary_result['sentiment']['negative'],
            key_features=summary_result['key_features']
        )
        db.session.add(analysis)
        db.session.commit()

        # Prepare response
        response_data = {
            'productName': product.name,
            'productImage': product.image_url,
            'productPrice': product.price,
            'productRating': product.rating,
            'platform': platform,
            'totalReviews': len(reviews_data),
            'averageRating': (sum(r['rating'] for r in reviews_data) / len(reviews_data)) if reviews_data else 0,
            'summary': {
                'pros': summary_result['pros'],
                'cons': summary_result['cons']
            },
            'sentiment': summary_result['sentiment'],
            'keyFeatures': summary_result['key_features'],
            'analysisId': analysis.id,
            'createdAt': analysis.created_at.isoformat()
        }

        logger.info(f"Analysis completed successfully for product: {product.name}")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error in analyze_reviews: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error occurred'}), 500

@app.route('/api/supported-platforms', methods=['GET'])
def get_supported_platforms():
    """Get list of supported platforms"""
    try:
        platforms = url_validator.get_supported_platforms()
        return jsonify({
            'platforms': platforms,
            'message': 'Universal scraper supports most e-commerce and review websites'
        })
    except Exception as e:
        logger.error(f"Error getting supported platforms: {str(e)}")
        return jsonify({'error': 'Failed to fetch supported platforms'}), 500

@app.route('/api/history', methods=['GET'])
def get_analysis_history():
    try:
        analyses = db.session.query(Analysis, Product).join(Product).order_by(Analysis.created_at.desc()).limit(20).all()
        
        history = []
        for analysis, product in analyses:
            history.append({
                'id': analysis.id,
                'productName': product.name,
                'productImage': product.image_url,
                'platform': product.platform,
                'totalReviews': analysis.total_reviews,
                'createdAt': analysis.created_at.isoformat(),
                'sentiment': {
                    'positive': analysis.sentiment_positive,
                    'neutral': analysis.sentiment_neutral,
                    'negative': analysis.sentiment_negative
                }
            })
        
        return jsonify({'history': history})
    
    except Exception as e:
        logger.error(f"Error in get_analysis_history: {str(e)}")
        return jsonify({'error': 'Failed to fetch history'}), 500

@app.route('/api/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis_by_id(analysis_id):
    try:
        analysis = db.session.query(Analysis, Product).join(Product).filter(Analysis.id == analysis_id).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        analysis_obj, product = analysis
        
        response_data = {
            'productName': product.name,
            'productImage': product.image_url,
            'productPrice': product.price,
            'productRating': product.rating,
            'platform': product.platform,
            'totalReviews': analysis_obj.total_reviews,
            'summary': {
                'pros': analysis_obj.summary_pros,
                'cons': analysis_obj.summary_cons
            },
            'sentiment': {
                'positive': analysis_obj.sentiment_positive,
                'neutral': analysis_obj.sentiment_neutral,
                'negative': analysis_obj.sentiment_negative
            },
            'keyFeatures': analysis_obj.key_features,
            'analysisId': analysis_obj.id,
            'createdAt': analysis_obj.created_at.isoformat()
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error in get_analysis_by_id: {str(e)}")
        return jsonify({'error': 'Failed to fetch analysis'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'features': [
            'Universal web scraping',
            'AI-powered review detection',
            'Multi-platform support',
            'Intelligent content extraction'
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
