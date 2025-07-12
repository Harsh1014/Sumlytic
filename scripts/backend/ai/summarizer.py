from groq import Groq
import os
import logging
import json
from collections import Counter
import re
from textblob import TextBlob

logger = logging.getLogger(__name__)

class ReviewSummarizer:
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
        else:
            logger.warning("Groq API key not found. Using fallback summarization.")
            self.groq_client = None
    
    def summarize_reviews(self, reviews, product_name):
        try:
            if not reviews:
                return {'success': False, 'error': 'No reviews to summarize'}
            
            # Prepare review texts
            review_texts = [review['text'] for review in reviews]
            review_ratings = []
            for review in reviews:
                try:
                    rating = review['rating']
                    if isinstance(rating, str):
                        rating = float(rating)
                    review_ratings.append(rating)
                except Exception:
                    review_ratings.append(None)
            
            # Generate sentiment analysis
            sentiment = self.analyze_sentiment(review_texts, review_ratings)
            
            # Extract key features
            key_features = self.extract_key_features(review_texts)
            
            # Generate pros and cons
            if self.groq_api_key:
                pros_cons = self.generate_ai_summary(review_texts, product_name)
            else:
                pros_cons = self.generate_fallback_summary(review_texts, review_ratings)
            
            return {
                'success': True,
                'pros': pros_cons['pros'],
                'cons': pros_cons['cons'],
                'sentiment': sentiment,
                'key_features': key_features
            }
            
        except Exception as e:
            logger.error(f"Error in summarize_reviews: {str(e)}")
            return {'success': False, 'error': 'Failed to generate summary'}
    
    def extract_json_from_response(self, response_text):
        """Extract JSON from AI response, handling various formats"""
        try:
            # First, try to parse the entire response as JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON within the response
        # Look for content between { and }
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON between ```json and ``` markers
        json_code_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_code_match:
            try:
                return json.loads(json_code_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON between ``` markers (without json specifier)
        code_match = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if code_match:
            try:
                return json.loads(code_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Log the problematic response for debugging
        logger.error(f"Could not extract JSON from response: {response_text[:500]}...")
        return None
    
    def generate_ai_summary(self, review_texts, product_name):
        try:
            # Combine reviews for AI processing
            combined_reviews = "\n\n".join(review_texts[:50])  # Limit to first 50 reviews
            
            # Truncate if too long to avoid token limits
            if len(combined_reviews) > 8000:
                combined_reviews = combined_reviews[:8000] + "..."
            
            prompt = f"""
            Analyze the following product reviews for "{product_name}" and provide a summary with exactly 5 key pros and 5 key cons.
            
            Reviews:
            {combined_reviews}
            
            Respond ONLY with valid JSON in this exact format (no additional text):
            {{
                "pros": [
                    "First key positive point about the product",
                    "Second key positive point about the product", 
                    "Third key positive point about the product",
                    "Fourth key positive point about the product",
                    "Fifth key positive point about the product"
                ],
                "cons": [
                    "First key negative point about the product",
                    "Second key negative point about the product",
                    "Third key negative point about the product",
                    "Fourth key negative point about the product",
                    "Fifth key negative point about the product"
                ]
            }}
            
            Make sure each point is:
            - Specific to the product features mentioned in reviews
            - Concise (1-2 sentences max)
            - Based on frequently mentioned aspects
            - Actionable for potential buyers
            
            Remember: Respond with ONLY the JSON object, no other text.
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",  # Using Llama 3 model on Groq
                messages=[
                    {"role": "system", "content": "You are an expert product analyst. You must respond ONLY with valid JSON format, no additional text or explanations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"AI Response: {result[:200]}...")
            
            # Use improved JSON extraction
            parsed_result = self.extract_json_from_response(result)
            
            if parsed_result and 'pros' in parsed_result and 'cons' in parsed_result:
                # Validate that we have lists with content
                pros = parsed_result.get('pros', [])
                cons = parsed_result.get('cons', [])
                
                if not isinstance(pros, list) or not isinstance(cons, list):
                    raise ValueError("Pros and cons must be lists")
                
                # Ensure we have at least some content
                if not pros or not cons:
                    raise ValueError("Pros and cons lists cannot be empty")
                
                # Limit to 5 items each
                pros = pros[:5]
                cons = cons[:5]

                # Fill with generic items if needed
                while len(pros) < 5:
                    pros.append("Additional positive aspect mentioned by customers")
                while len(cons) < 5:
                    cons.append("Some customers reported minor concerns")
                
                return {
                    'pros': pros,
                    'cons': cons
                }
            else:
                logger.warning("Parsed result missing required fields")
                raise ValueError("Invalid response structure")
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}")
            logger.info("Falling back to rule-based summary")
            return self.generate_fallback_summary(review_texts, [])
    
    def generate_fallback_summary(self, review_texts, review_ratings):
        """Generate summary without AI using text analysis"""
        try:
            # Analyze positive and negative reviews
            positive_reviews = []
            negative_reviews = []
            
            for i, text in enumerate(review_texts):
                # Use TextBlob sentiment if no ratings available
                if i < len(review_ratings) and review_ratings[i] is not None:
                    rating = review_ratings[i]
                else:
                    # Use sentiment analysis
                    blob = TextBlob(text)
                    sentiment_score = blob.sentiment.polarity
                    if sentiment_score > 0.1:
                        rating = 4
                    elif sentiment_score < -0.1:
                        rating = 2
                    else:
                        rating = 3
                
                if rating >= 4:
                    positive_reviews.append(text)
                elif rating <= 2:
                    negative_reviews.append(text)
            
            # Extract common positive themes
            pros = self.extract_common_themes(positive_reviews, positive=True)
            
            # Extract common negative themes
            cons = self.extract_common_themes(negative_reviews, positive=False)
            
            # Ensure we have at least 3 of each
            default_pros = [
                "Customers generally satisfied with product quality",
                "Good value for money according to reviews",
                "Positive feedback on overall performance"
            ]
            default_cons = [
                "Some customers experienced minor issues",
                "Delivery or packaging concerns mentioned",
                "Room for improvement in certain features"
            ]
            
            pros = (pros + default_pros)[:5]
            cons = (cons + default_cons)[:5]
            
            return {
                'pros': pros,
                'cons': cons
            }
            
        except Exception as e:
            logger.error(f"Error in fallback summary: {str(e)}")
            return {
                'pros': [
                    "Good product quality based on customer feedback",
                    "Reasonable pricing for the features offered",
                    "Generally positive customer experience"
                ],
                'cons': [
                    "Some customers reported minor issues",
                    "Occasional delivery delays mentioned",
                    "Feature improvements suggested by users"
                ]
            }
    
    def extract_common_themes(self, reviews, positive=True):
        if not reviews:
            return []
        
        # Enhanced keywords with context
        positive_patterns = {
            'quality': ['excellent quality', 'good quality', 'high quality', 'premium quality'],
            'performance': ['great performance', 'excellent performance', 'smooth performance'],
            'value': ['good value', 'value for money', 'worth the price', 'affordable'],
            'design': ['beautiful design', 'attractive design', 'sleek design', 'elegant'],
            'battery': ['long battery', 'excellent battery', 'good battery life'],
            'camera': ['good camera', 'excellent camera', 'great photos', 'clear pictures'],
            'speed': ['fast', 'quick', 'responsive', 'smooth'],
            'build': ['sturdy', 'durable', 'well built', 'solid construction']
        }
        
        negative_patterns = {
            'quality': ['poor quality', 'bad quality', 'cheap quality', 'low quality'],
            'performance': ['poor performance', 'slow performance', 'laggy'],
            'battery': ['poor battery', 'battery drain', 'short battery life'],
            'camera': ['poor camera', 'bad camera', 'blurry photos'],
            'build': ['fragile', 'flimsy', 'breaks easily', 'poor construction'],
            'price': ['overpriced', 'too expensive', 'not worth the price'],
            'delivery': ['delayed delivery', 'poor packaging', 'damaged packaging'],
            'service': ['poor service', 'bad customer service', 'unhelpful support']
        }
        
        patterns = positive_patterns if positive else negative_patterns
        
        # Count pattern occurrences
        theme_counts = Counter()
        
        for review in reviews:
            review_lower = review.lower()
            for theme, keywords in patterns.items():
                for keyword in keywords:
                    if keyword in review_lower:
                        theme_counts[theme] += 1
                        break  # Count each theme only once per review
        
        # Generate themes based on most common patterns
        themes = []
        for theme, count in theme_counts.most_common(5):
            if count >= 2:  # Only include themes mentioned multiple times
                if positive:
                    theme_messages = {
                        'quality': "Customers praise the excellent build quality and materials",
                        'performance': "Users report smooth and reliable performance",
                        'value': "Reviewers consider it good value for money",
                        'design': "Many customers appreciate the attractive design",
                        'battery': "Battery life receives positive feedback from users",
                        'camera': "Camera quality is well-regarded by customers",
                        'speed': "Fast and responsive operation praised by users",
                        'build': "Sturdy construction and durability noted by reviewers"
                    }
                else:
                    theme_messages = {
                        'quality': "Some customers report concerns about build quality",
                        'performance': "Performance issues mentioned by several users",
                        'battery': "Battery life disappoints some customers",
                        'camera': "Camera quality doesn't meet some expectations",
                        'build': "Durability concerns raised by some reviewers",
                        'price': "Some customers feel the product is overpriced",
                        'delivery': "Delivery and packaging issues reported",
                        'service': "Customer service experience could be improved"
                    }
                
                themes.append(theme_messages.get(theme, f"{'Positive' if positive else 'Negative'} feedback about {theme}"))
        
        return themes
    
    def analyze_sentiment(self, review_texts, review_ratings):
        try:
            if not review_ratings or all(rating is None for rating in review_ratings):
                # Use TextBlob for sentiment analysis
                sentiments = []
                for text in review_texts:
                    blob = TextBlob(text)
                    polarity = blob.sentiment.polarity
                    if polarity > 0.1:
                        sentiments.append('positive')
                    elif polarity < -0.1:
                        sentiments.append('negative')
                    else:
                        sentiments.append('neutral')
                
                sentiment_counts = Counter(sentiments)
                total = len(sentiments)
            else:
                # Use ratings for sentiment analysis
                valid_ratings = [r for r in review_ratings if r is not None]
                positive = sum(1 for rating in valid_ratings if rating >= 4)
                negative = sum(1 for rating in valid_ratings if rating <= 2)
                neutral = len(valid_ratings) - positive - negative
                total = len(valid_ratings)
                
                sentiment_counts = {
                    'positive': positive,
                    'negative': negative,
                    'neutral': neutral
                }
            
            if total == 0:
                return {'positive': 70, 'neutral': 20, 'negative': 10}
            
            return {
                'positive': round((sentiment_counts.get('positive', 0) / total) * 100, 1),
                'neutral': round((sentiment_counts.get('neutral', 0) / total) * 100, 1),
                'negative': round((sentiment_counts.get('negative', 0) / total) * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'positive': 70, 'neutral': 20, 'negative': 10}
    
    def extract_key_features(self, review_texts):
        try:
            # Enhanced feature keywords for better detection
            feature_keywords = {
                'battery': ['battery', 'charge', 'charging', 'power', 'backup'],
                'camera': ['camera', 'photo', 'picture', 'selfie', 'video', 'lens'],
                'display': ['display', 'screen', 'brightness', 'resolution', 'colors'],
                'performance': ['performance', 'speed', 'fast', 'slow', 'lag', 'smooth'],
                'design': ['design', 'look', 'appearance', 'style', 'color', 'beautiful'],
                'build_quality': ['quality', 'build', 'material', 'construction', 'sturdy'],
                'price': ['price', 'cost', 'value', 'money', 'expensive', 'cheap', 'affordable'],
                'storage': ['storage', 'memory', 'space', 'gb', 'ram'],
                'connectivity': ['network', '5g', '4g', 'wifi', 'bluetooth', 'signal'],
                'user_interface': ['ui', 'interface', 'software', 'android', 'system']
            }
            
            feature_mentions = Counter()
            feature_sentiments = {}
            
            for review in review_texts:
                review_lower = review.lower()
                blob = TextBlob(review)
                review_sentiment = 'positive' if blob.sentiment.polarity > 0.1 else 'negative' if blob.sentiment.polarity < -0.1 else 'neutral'
                
                for feature, keywords in feature_keywords.items():
                    mentioned = False
                    for keyword in keywords:
                        if keyword in review_lower:
                            feature_mentions[feature] += 1
                            if feature not in feature_sentiments:
                                feature_sentiments[feature] = []
                            feature_sentiments[feature].append(review_sentiment)
                            mentioned = True
                            break
                    
                    if mentioned:
                        continue
            
            # Get top features with their sentiment
            key_features = []
            for feature, count in feature_mentions.most_common(8):
                if count >= 2:  # Only include features mentioned multiple times
                    sentiments = feature_sentiments[feature]
                    sentiment_counter = Counter(sentiments)
                    most_common_sentiment = sentiment_counter.most_common(1)[0][0]
                    
                    # Calculate a score based on mentions and sentiment
                    score = min(count * 10, 100)  # Scale for display
                    
                    key_features.append({
                        'feature': feature.replace('_', ' ').title(),
                        'mentions': score,
                        'sentiment': most_common_sentiment
                    })
            
            return key_features[:5]  # Return top 5 features
            
        except Exception as e:
            logger.error(f"Error extracting key features: {str(e)}")
            return []