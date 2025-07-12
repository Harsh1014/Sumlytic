import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

class AmazonScraper:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
    def get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
    
    def scrape_product(self, url):
        try:
            logger.info(f"Scraping Amazon product: {url}")
            
            # Get product page
            response = self.session.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information
            product_data = self.extract_product_info(soup, url)
            if not product_data:
                return {'success': False, 'error': 'Could not extract product information'}
            
            # Get reviews
            reviews_data = self.scrape_reviews(url, soup)
            
            return {
                'success': True,
                'product': product_data,
                'reviews': reviews_data
            }
            
        except requests.RequestException as e:
            logger.error(f"Request error while scraping Amazon: {str(e)}")
            return {'success': False, 'error': 'Failed to fetch product page'}
        except Exception as e:
            logger.error(f"Error scraping Amazon product: {str(e)}")
            return {'success': False, 'error': 'Failed to scrape product data'}
    
    def extract_product_info(self, soup, url):
        try:
            # Product name
            name_selectors = [
                '#productTitle',
                'h1.a-size-large',
                'h1#title',
                '.product-title'
            ]
            
            name = None
            for selector in name_selectors:
                name_elem = soup.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    break
            
            if not name:
                return None
            
            # Product image
            image_url = None
            img_selectors = [
                '#landingImage',
                '#imgBlkFront',
                '.a-dynamic-image',
                '#main-image'
            ]
            
            for selector in img_selectors:
                img_elem = soup.select_one(selector)
                if img_elem and img_elem.get('src'):
                    image_url = img_elem.get('src')
                    break
            
            # Product price
            price = None
            price_selectors = [
                '.a-price-whole',
                '#priceblock_dealprice',
                '#priceblock_ourprice',
                '.a-price .a-offscreen'
            ]
            
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'[\$₹]?([\d,]+)', price_text)
                    if price_match:
                        price = price_match.group(1).replace(',', '')
                    break
            
            # Product rating
            rating = None
            rating_selectors = [
                '.a-icon-alt',
                '#acrPopover',
                '.a-star-5'
            ]
            
            for selector in rating_selectors:
                rating_elem = soup.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True) if hasattr(rating_elem, 'get_text') else str(rating_elem)
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        if rating > 5:  # Sometimes it's out of 10
                            rating = rating / 2
                    break
            
            return {
                'name': name,
                'image_url': image_url,
                'price': price,
                'rating': rating
            }
            
        except Exception as e:
            logger.error(f"Error extracting product info: {str(e)}")
            return None
    
    def scrape_reviews(self, product_url, soup):
        reviews = []
        
        try:
            # Look for reviews on the same page first
            review_elements = soup.select('[data-hook="review"]')
            
            if not review_elements:
                # Try to find reviews link and navigate
                reviews_link = self.find_reviews_link(soup, product_url)
                if reviews_link:
                    reviews = self.scrape_reviews_page(reviews_link)
            else:
                reviews = self.extract_reviews_from_elements(review_elements)
            
            # If still no reviews, try common review patterns
            if not reviews:
                reviews = self.scrape_fallback_reviews(soup)
            
            logger.info(f"Scraped {len(reviews)} reviews from Amazon")
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping reviews: {str(e)}")
            return []
    
    def find_reviews_link(self, soup, base_url):
        try:
            # Look for reviews link
            reviews_links = soup.find_all('a', href=True)
            for link in reviews_links:
                href = link.get('href')
                text = link.get_text(strip=True).lower()
                if ('review' in text or 'customer' in text) and href:
                    if href.startswith('/'):
                        return urljoin('https://amazon.com', href)
                    return href
            return None
        except:
            return None
    
    def scrape_reviews_page(self, reviews_url):
        reviews = []
        try:
            response = self.session.get(reviews_url, headers=self.get_headers())
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            review_elements = soup.select('[data-hook="review"]')
            
            reviews = self.extract_reviews_from_elements(review_elements)
            
            # Try to get more pages
            page_count = 0
            while len(reviews) < 50 and page_count < 3:  # Limit to 3 additional pages
                next_link = soup.select_one('li.a-last a')
                if not next_link or not next_link.get('href'):
                    break
                
                time.sleep(random.uniform(2, 4))  # Rate limiting
                
                next_url = urljoin(reviews_url, next_link.get('href'))
                response = self.session.get(next_url, headers=self.get_headers())
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                review_elements = soup.select('[data-hook="review"]')
                
                page_reviews = self.extract_reviews_from_elements(review_elements)
                reviews.extend(page_reviews)
                page_count += 1
            
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping reviews page: {str(e)}")
            return []
    
    def extract_reviews_from_elements(self, review_elements):
        reviews = []
        
        for element in review_elements:
            try:
                # Extract review text
                text_elem = element.select_one('[data-hook="review-body"] span')
                if not text_elem:
                    continue
                
                review_text = text_elem.get_text(strip=True)
                if len(review_text) < 10:  # Skip very short reviews
                    continue
                
                # Extract rating
                rating = 5  # Default rating
                rating_elem = element.select_one('.a-icon-alt')
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    rating_match = re.search(r'(\d+)', rating_text)
                    if rating_match:
                        rating = int(rating_match.group(1))
                
                # Extract author
                author = "Anonymous"
                author_elem = element.select_one('.a-profile-name')
                if author_elem:
                    author = author_elem.get_text(strip=True)
                
                # Extract date
                date = None
                date_elem = element.select_one('[data-hook="review-date"]')
                if date_elem:
                    date = date_elem.get_text(strip=True)
                
                reviews.append({
                    'text': review_text,
                    'rating': rating,
                    'author': author,
                    'date': date
                })
                
            except Exception as e:
                logger.error(f"Error extracting individual review: {str(e)}")
                continue
        
        return reviews
    
    def scrape_fallback_reviews(self, soup):
        """Fallback method to extract reviews using common patterns"""
        reviews = []
        
        try:
            # Try to find any text that looks like reviews
            all_divs = soup.find_all('div')
            
            for div in all_divs:
                text = div.get_text(strip=True)
                
                # Check if this looks like a review (length and content)
                if (50 < len(text) < 1000 and 
                    any(word in text.lower() for word in ['good', 'bad', 'excellent', 'poor', 'quality', 'product', 'buy', 'recommend'])):
                    
                    reviews.append({
                        'text': text,
                        'rating': 4,  # Default rating
                        'author': 'Anonymous',
                        'date': None
                    })
                    
                    if len(reviews) >= 20:  # Limit fallback reviews
                        break
            
            return reviews
            
        except Exception as e:
            logger.error(f"Error in fallback review scraping: {str(e)}")
            return []
