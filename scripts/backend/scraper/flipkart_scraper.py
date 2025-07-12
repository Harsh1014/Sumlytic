import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import re
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

logger = logging.getLogger(__name__)

class FlipkartScraper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]
        
        # Updated selectors for 2024-2025 - more comprehensive
        self.selectors = {
            'product_name': [
                # Updated for 2025
                'h1[data-testid="product-title"]',
                'h1.yhB1nd',
                'span.VU-ZEz',
                'span.B_NuCI', 
                'h1._35KyD6',
                'h1[data-tkid]',
                '.pdp-product-name',
                '.B_NuCI',
                'h1.x-product-title-label',
                '[data-automation-id="product-title"]',
                '.pdp-mod-product-badge-title',
                # Reviews page specific selectors
                '._3eAQiD h1',
                '.c-product-name',
                '._3eAQiD span',
                '._35KyD6 span'
            ],
            'product_image': [
                # Updated for 2025
                'img[data-testid="product-image"]',
                'img._396cs4._2amPTt._3qGmMb._3exPp9',
                'img._396cs4._2amPTt',
                'img._396cs4._3exPp9', 
                'img._396cs4',
                'img._2r_T1I',
                '.CXW8mj img',
                '._396cs4 img',
                '.product-image img',
                # Reviews page specific
                '._3eAQiD img',
                '.c-product-image img',
                '._2r_T1I._3Ov-Bg img'
            ],
            'product_price': [
                # Updated for 2025
                'div.Nx9bqj.CxhGGd',
                'div._30jeq3._16Jk6d',
                'div._1_WHN1',
                '.CEmiEU .sr_P9z',
                'div._30jeq3',
                '[data-testid="product-price"]',
                '.pdp-price',
                '._16Jk6d',
                '.CEmiEU'
            ],
            'product_rating': [
                # Updated for 2025
                'div.XQDdHH',
                'div._3LWZlK',
                '.hGSR34',
                '._2d4LTz',
                'div._3LWZlK',
                '[data-testid="product-rating"]',
                '.gUuXy-',
                '._3LWZlK._1BLPMq'
            ],
            'review_blocks': [
                # Updated selectors for reviews
                'div.cPHDOP',
                'div._27M-vq',
                'div.col.EPCmJX',
                '[data-testid="review-block"]',
                '.review-item',
                'div[data-testid="review-card"]',
                '.review-container'
            ],
            'review_rating': [
                # Review rating selectors
                'div.XQDdHH',
                'div._3LWZlK',
                '.review-rating',
                '[data-testid="review-rating"]',
                '.gUuXy-',
                '._3LWZlK._1BLPMq',
                'div._3LWZlK.gUuXy-'
            ],
            'review_text': [
                # Review text selectors
                'div.ZmyHeo',
                'p._2-N8zT',
                '.review-text',
                '[data-testid="review-text"]',
                'div.t-ZTKy div div',
                '.qwjRop div div'
            ],
            'review_title': [
                # Review title selectors
                'p.z9E0IG',
                'div.t-ZTKy',
                '.review-title',
                '[data-testid="review-title"]'
            ],
            'reviewer_name': [
                # Reviewer name selectors
                'p._2sc7ZR._3jizYG',
                'p._2sc7ZR',
                '.reviewer-name',
                '[data-testid="reviewer-name"]'
            ],
            'review_date': [
                # Review date selectors
                'p.CRxhOx',
                'p._2sc7ZR',
                '.review-date',
                '[data-testid="review-date"]'
            ]
        }

    def get_chrome_options(self):
        """Configure Chrome options for better stealth"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument(f"--user-agent={random.choice(self.user_agents)}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return options

    def get_html_with_requests(self, url):
        """Try requests first (faster)"""
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(url, timeout=10)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.warning(f"Requests failed: {e}")
            return None

    def get_html_with_selenium(self, url):
        """Fallback to Selenium if requests fails"""
        driver = None
        try:
            options = self.get_chrome_options()
            driver = webdriver.Chrome(options=options)
            
            # Execute stealth script
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(random.uniform(3, 6))
            
            html = driver.page_source
            return BeautifulSoup(html, 'html.parser')
            
        except Exception as e:
            logger.error(f"Selenium failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def get_html(self, url):
        """Try requests first, fallback to Selenium"""
        soup = self.get_html_with_requests(url)
        if soup:
            return soup
        
        logger.info("Falling back to Selenium...")
        return self.get_html_with_selenium(url)

    def extract_with_selectors(self, soup, selectors, extract_type='text'):
        """Extract content using multiple selectors"""
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    if extract_type == 'text':
                        text = element.get_text(strip=True)
                        if text:
                            return text
                    elif extract_type == 'src':
                        src = element.get('src')
                        if src:
                            return src
                    elif extract_type == 'href':
                        href = element.get('href')
                        if href:
                            return href
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        return None

    def get_product_url_from_reviews_url(self, reviews_url):
        """Extract product URL from reviews URL"""
        try:
            # Extract product ID from reviews URL
            if '/product-reviews/' in reviews_url:
                parts = reviews_url.split('/product-reviews/')
                if len(parts) > 1:
                    product_id = parts[1].split('?')[0]
                    # Construct product URL
                    product_url = f"https://www.flipkart.com/p/{product_id}"
                    return product_url
            return None
        except Exception as e:
            logger.error(f"Error extracting product URL: {e}")
            return None

    def extract_product_info(self, soup, url):
        """Extract product information with improved selectors and fallback handling"""
        try:
            # If we're on a reviews page, try to get product info from there first
            if '/product-reviews/' in url:
                # Try to extract from reviews page
                name = self.extract_with_selectors(soup, self.selectors['product_name'])
                image_url = self.extract_with_selectors(soup, self.selectors['product_image'], 'src')
                
                # If we couldn't get product info from reviews page, try the product page
                if not name:
                    product_url = self.get_product_url_from_reviews_url(url)
                    if product_url:
                        logger.info(f"Trying to get product info from: {product_url}")
                        product_soup = self.get_html(product_url)
                        if product_soup:
                            name = self.extract_with_selectors(product_soup, self.selectors['product_name'])
                            image_url = self.extract_with_selectors(product_soup, self.selectors['product_image'], 'src')
                            
                            # Get price and rating from product page
                            price = None
                            price_text = self.extract_with_selectors(product_soup, self.selectors['product_price'])
                            if price_text:
                                price_match = re.search(r'₹([\d,]+)', price_text)
                                if price_match:
                                    price = price_match.group(1).replace(',', '')
                            
                            rating = None
                            rating_text = self.extract_with_selectors(product_soup, self.selectors['product_rating'])
                            if rating_text:
                                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                                if rating_match:
                                    rating = float(rating_match.group(1))
                            
                            if name:
                                logger.info(f"Product name found from product page: {name}")
                                return {
                                    'name': name,
                                    'image_url': image_url or 'https://via.placeholder.com/300x300?text=No+Image',
                                    'price': price,
                                    'rating': rating,
                                    'url': url
                                }
            else:
                # Regular product page
                name = self.extract_with_selectors(soup, self.selectors['product_name'])
                image_url = self.extract_with_selectors(soup, self.selectors['product_image'], 'src')
                
                price = None
                price_text = self.extract_with_selectors(soup, self.selectors['product_price'])
                if price_text:
                    price_match = re.search(r'₹([\d,]+)', price_text)
                    if price_match:
                        price = price_match.group(1).replace(',', '')
                
                rating = None
                rating_text = self.extract_with_selectors(soup, self.selectors['product_rating'])
                if rating_text:
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))

            # If we still don't have a name, provide a fallback
            if not name:
                # Try to extract from URL or provide a generic name
                if '/product-reviews/' in url:
                    name = "Product from Flipkart Reviews"
                else:
                    name = "Flipkart Product"
                logger.warning(f"Could not extract product name, using fallback: {name}")

            # Ensure we have an image URL
            if not image_url:
                image_url = 'https://via.placeholder.com/300x300?text=No+Image'

            return {
                'name': name,
                'image_url': image_url,
                'price': price,
                'rating': rating,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error extracting product info: {str(e)}")
            # Return fallback data to avoid database errors
            return {
                'name': "Flipkart Product",
                'image_url': 'https://via.placeholder.com/300x300?text=No+Image',
                'price': None,
                'rating': None,
                'url': url
            }

    def cus_rev(self, soup):
        """Extract customer reviews with improved selectors and rating parsing"""
        reviews = []
        review_blocks = []
        
        # Find review blocks
        for selector in self.selectors['review_blocks']:
            blocks = soup.select(selector)
            if blocks:
                review_blocks = blocks
                logger.info(f"Found {len(blocks)} review blocks with selector: {selector}")
                break

        if not review_blocks:
            logger.warning("No review blocks found")
            return reviews

        for block in review_blocks:
            try:
                # Extract rating
                rating_text = self.extract_with_selectors(block, self.selectors['review_rating'])
                rating = None
                if rating_text:
                    # Try to extract numeric rating
                    rating_match = re.search(r'(\d+)', rating_text)
                    if rating_match:
                        rating = int(rating_match.group(1))
                        if rating > 5:  # Sometimes it's out of 10, convert to 5
                            rating = min(5, rating // 2)
                
                # Extract review text
                review_text = self.extract_with_selectors(block, self.selectors['review_text'])
                
                # Extract review title
                review_title = self.extract_with_selectors(block, self.selectors['review_title'])
                
                # Extract reviewer name
                reviewer_name = self.extract_with_selectors(block, self.selectors['reviewer_name'])
                
                # Extract review date
                review_date = self.extract_with_selectors(block, self.selectors['review_date'])

                # Only add review if we have essential information
                if review_text and len(review_text.strip()) > 10:  # Minimum review length
                    # If no rating found, try to infer from text
                    if rating is None:
                        # Try to find star ratings in the text
                        star_match = re.search(r'(\d+)\s*star', review_text.lower())
                        if star_match:
                            rating = int(star_match.group(1))
                        else:
                            # Default to 3 if no rating found
                            rating = 3
                    
                    review = {
                        'rating': rating,
                        'text': review_text,
                        'title': review_title or '',
                        'author': reviewer_name or 'Anonymous',
                        'date': review_date or ''
                    }
                    reviews.append(review)
                    
            except Exception as e:
                logger.error(f"Error extracting individual review: {str(e)}")
                continue

        logger.info(f"Successfully extracted {len(reviews)} reviews")
        return reviews

    def find_reviews_link(self, soup, base_url):
        """Find reviews link with improved detection"""
        try:
            # Look for review links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True).lower()
                
                # Check if it's a reviews link
                if any(keyword in text for keyword in ['review', 'reviews', 'rating']) and href:
                    if '/product-reviews/' in href or 'reviews' in href:
                        full_url = urljoin(base_url, href)
                        logger.info(f"Found reviews link: {full_url}")
                        return full_url
            
            # Try to construct reviews URL from product URL
            if '/p/' in base_url:
                product_id = base_url.split('/p/')[-1].split('?')[0]
                reviews_url = f"https://www.flipkart.com/product-reviews/{product_id}"
                return reviews_url
                
            return None
        except Exception as e:
            logger.error(f"Error finding reviews link: {e}")
            return None

    def scrape_product_reviews(self, base_url, max_pages=3):
        """Scrape reviews with pagination"""
        reviews = []
        page = 1
        
        while page <= max_pages:
            try:
                if page == 1:
                    page_url = base_url
                else:
                    # Add page parameter
                    separator = '&' if '?' in base_url else '?'
                    page_url = f"{base_url}{separator}page={page}"
                
                logger.info(f"Scraping reviews page {page}: {page_url}")
                
                soup = self.get_html(page_url)
                if not soup:
                    logger.error(f"Failed to get HTML for page {page}")
                    break
                
                page_reviews = self.cus_rev(soup)
                
                if not page_reviews:
                    logger.info(f"No reviews found on page {page}")
                    if page == 1:
                        # If no reviews on first page, still continue to try other pages
                        page += 1
                        continue
                    else:
                        break
                
                reviews.extend(page_reviews)
                logger.info(f"Found {len(page_reviews)} reviews on page {page}")
                
                # Check if there's a next page
                next_page_exists = soup.find('a', {'aria-label': 'Next'}) or soup.find('span', text='Next')
                if not next_page_exists and page > 1:
                    logger.info("No more pages available")
                    break
                
                page += 1
                
                # Be respectful with delays
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                break
        
        return reviews

    def scrape_product(self, url):
        """Main scraping method with better error handling"""
        try:
            logger.info(f"Starting to scrape: {url}")
            
            # Get main product page
            soup = self.get_html(url)
            if not soup:
                return {'success': False, 'error': 'Failed to load product page'}
            
            # Extract product information (now with better fallback handling)
            product_data = self.extract_product_info(soup, url)
            if not product_data or not product_data.get('name'):
                logger.warning("No product data extracted, using fallback")
                product_data = {
                    'name': "Flipkart Product",
                    'image_url': 'https://via.placeholder.com/300x300?text=No+Image',
                    'price': None,
                    'rating': None,
                    'url': url
                }
            
            # Handle reviews
            reviews_data = []
            
            if '/product-reviews/' in url:
                # Direct reviews page
                reviews_data = self.scrape_product_reviews(url)
            else:
                # Find reviews link
                reviews_link = self.find_reviews_link(soup, url)
                if reviews_link:
                    reviews_data = self.scrape_product_reviews(reviews_link)
                else:
                    # Try to extract reviews from current page
                    reviews_data = self.cus_rev(soup)
            
            if not reviews_data:
                logger.warning("No reviews found")
                return {'success': False, 'error': 'No reviews found for this product'}
            
            return {
                'success': True,
                'product': product_data,
                'reviews': reviews_data,
                'total_reviews': len(reviews_data),
                'scraped_url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping product: {str(e)}")
            return {'success': False, 'error': f'Scraping failed: {str(e)}'}

# # Example usage
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
#     scraper = FlipkartScraper()
    
#     # Test with the problematic URL
#     test_url = "https://www.flipkart.com/vivo-t4-ultra-5g-phoenix-gold-256-gb/product-reviews/itm9cfd8118c9ce0?pid=MOBHCJMRHSP2HPZZ&lid=LSTMOBHCJMRHSP2HPZZ3KHQDL&marketplace=FLIPKART"
    
#     result = scraper.scrape_product(test_url)
    
#     if result['success']:
#         product = result.get('product', {})
#         print(f"✅ Product: {product.get('name', 'N/A')}")
#         print(f"✅ Price: ₹{product.get('price', 'N/A')}")
#         print(f"✅ Rating: {product.get('rating', 'N/A')}")
#         print(f"✅ Total reviews scraped: {result['total_reviews']}")
        
#         # Show first few reviews
#         for i, review in enumerate(result['reviews'][:3], 1):
#             print(f"\n📝 Review {i}:")
#             print(f"   Rating: {review.get('rating', 'N/A')}")
#             print(f"   Author: {review.get('author', 'N/A')}")
#             print(f"   Date: {review.get('date', 'N/A')}")
#             print(f"   Review: {review.get('text', 'N/A')[:100]}...")
#     else:
#         print(f"❌ Error: {result['error']}")