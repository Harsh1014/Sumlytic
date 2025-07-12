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
from textblob import TextBlob
from collections import Counter
import difflib

logger = logging.getLogger(__name__)

class UniversalReviewScraper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        # Universal patterns for detecting reviews
        self.review_indicators = {
            'text_patterns': [
                r'\b(review|rating|star|customer|buyer|user|feedback|opinion|experience)\b',
                r'\b(good|bad|excellent|poor|amazing|terrible|love|hate|recommend|avoid)\b',
                r'\b(quality|price|value|delivery|service|product|item)\b',
                r'\b(satisfied|disappointed|happy|unhappy|pleased|frustrated)\b'
            ],
            'class_patterns': [
                r'review', r'rating', r'comment', r'feedback', r'testimonial',
                r'customer', r'user', r'buyer', r'opinion', r'experience'
            ],
            'id_patterns': [
                r'review', r'rating', r'comment', r'feedback'
            ],
            'attribute_patterns': [
                r'review', r'rating', r'comment', r'testimonial'
            ]
        }
        
        # Common product info patterns
        self.product_patterns = {
            'title': [
                'h1', 'h2', '.title', '.product-title', '.product-name',
                '[data-testid*="title"]', '[data-testid*="name"]',
                '.pdp-product-name', '.product-info h1', '.product-info h2'
            ],
            'image': [
                '.product-image img', '.main-image img', '.hero-image img',
                '[data-testid*="image"] img', '.gallery img', '.product-photo img'
            ],
            'price': [
                '.price', '.cost', '.amount', '[data-testid*="price"]',
                '.product-price', '.current-price', '.sale-price'
            ],
            'rating': [
                '.rating', '.stars', '.score', '[data-testid*="rating"]',
                '.product-rating', '.average-rating'
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
            
            response = session.get(url, timeout=15)
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
            WebDriverWait(driver, 15).until(
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

    def calculate_review_score(self, element):
        """Calculate how likely an element is to be a review"""
        score = 0
        text = element.get_text(strip=True).lower()
        
        # Text length scoring (reviews are usually 20-2000 characters)
        text_length = len(text)
        if 20 <= text_length <= 2000:
            score += 10
        elif 10 <= text_length <= 20:
            score += 5
        elif text_length > 2000:
            score -= 5
        
        # Content pattern matching
        for pattern in self.review_indicators['text_patterns']:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches * 3
        
        # HTML structure scoring
        class_attr = element.get('class', [])
        id_attr = element.get('id', '')
        
        # Check class names
        for class_name in class_attr:
            for pattern in self.review_indicators['class_patterns']:
                if re.search(pattern, class_name, re.IGNORECASE):
                    score += 5
        
        # Check ID
        for pattern in self.review_indicators['id_patterns']:
            if re.search(pattern, id_attr, re.IGNORECASE):
                score += 5
        
        # Check for rating indicators (stars, numbers)
        if re.search(r'\b[1-5]\s*(star|out of|/5)\b', text, re.IGNORECASE):
            score += 8
        
        # Check for common review phrases
        review_phrases = [
            'i bought', 'purchased', 'received', 'delivery', 'shipping',
            'would recommend', 'not recommend', 'satisfied', 'disappointed',
            'good quality', 'poor quality', 'value for money', 'waste of money'
        ]
        
        for phrase in review_phrases:
            if phrase in text:
                score += 4
        
        # Penalty for very short or very long texts
        if text_length < 10:
            score -= 10
        elif text_length > 3000:
            score -= 5
        
        return score

    def detect_reviews_automatically(self, soup):
        """Automatically detect review elements using AI-like scoring"""
        potential_reviews = []
        
        # Get all text-containing elements
        all_elements = soup.find_all(['div', 'p', 'span', 'article', 'section', 'li'])
        
        for element in all_elements:
            score = self.calculate_review_score(element)
            
            if score >= 15:  # Threshold for considering as review
                potential_reviews.append({
                    'element': element,
                    'score': score,
                    'text': element.get_text(strip=True)
                })
        
        # Sort by score and return top candidates
        potential_reviews.sort(key=lambda x: x['score'], reverse=True)
        
        # Filter out duplicates and nested elements
        filtered_reviews = []
        seen_texts = set()
        
        for review in potential_reviews:
            text = review['text']
            
            # Skip if we've seen very similar text
            is_duplicate = False
            for seen_text in seen_texts:
                if difflib.SequenceMatcher(None, text.lower(), seen_text.lower()).ratio() > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate and len(text) > 20:
                filtered_reviews.append(review)
                seen_texts.add(text.lower())
                
                if len(filtered_reviews) >= 50:  # Limit to top 50 reviews
                    break
        
        logger.info(f"Detected {len(filtered_reviews)} potential reviews")
        return filtered_reviews

    def extract_rating_from_text(self, text, element):
        """Extract rating from text or nearby elements"""
        # Look for explicit ratings
        rating_patterns = [
            r'(\d+)\s*(?:out of|/)\s*5',
            r'(\d+)\s*star',
            r'rating:\s*(\d+)',
            r'(\d+\.?\d*)\s*/\s*5',
            r'★{1,5}',  # Star symbols
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if '★' in pattern:
                    return len(match.group())
                else:
                    rating = float(match.group(1))
                    return min(5, rating)  # Cap at 5
        
        # Look in nearby elements for rating
        parent = element.parent
        if parent:
            parent_text = parent.get_text()
            for pattern in rating_patterns:
                match = re.search(pattern, parent_text, re.IGNORECASE)
                if match:
                    if '★' in pattern:
                        return len(match.group())
                    else:
                        rating = float(match.group(1))
                        return min(5, rating)
        
        # Use sentiment analysis as fallback
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        
        if sentiment > 0.3:
            return 5
        elif sentiment > 0.1:
            return 4
        elif sentiment > -0.1:
            return 3
        elif sentiment > -0.3:
            return 2
        else:
            return 1

    def extract_author_from_element(self, element):
        """Extract author name from review element or nearby elements"""
        # Look for author patterns in the element and its siblings
        author_patterns = [
            r'by\s+([A-Za-z\s]+)',
            r'reviewer:\s*([A-Za-z\s]+)',
            r'customer:\s*([A-Za-z\s]+)',
            r'user:\s*([A-Za-z\s]+)',
        ]
        
        text = element.get_text()
        for pattern in author_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Look in nearby elements
        parent = element.parent
        if parent:
            siblings = parent.find_all(['span', 'div', 'p'], limit=5)
            for sibling in siblings:
                sibling_text = sibling.get_text(strip=True)
                if len(sibling_text) < 50:  # Author names are usually short
                    for pattern in author_patterns:
                        match = re.search(pattern, sibling_text, re.IGNORECASE)
                        if match:
                            return match.group(1).strip()
        
        return "Anonymous"

    def extract_date_from_element(self, element):
        """Extract date from review element or nearby elements"""
        date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b',
            r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4})\b',
            r'\b(\d{2,4}-\d{1,2}-\d{1,2})\b',
        ]
        
        text = element.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Look in nearby elements
        parent = element.parent
        if parent:
            siblings = parent.find_all(['span', 'div', 'p', 'time'], limit=5)
            for sibling in siblings:
                sibling_text = sibling.get_text(strip=True)
                for pattern in date_patterns:
                    match = re.search(pattern, sibling_text, re.IGNORECASE)
                    if match:
                        return match.group(1)
        
        return None

    def extract_product_info_universal(self, soup, url):
        """Extract product information using universal patterns"""
        try:
            # Extract product name
            name = None
            for selector in self.product_patterns['title']:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 5 and len(text) < 200:
                        name = text
                        break
                if name:
                    break
            
            # Fallback: use page title
            if not name:
                title_tag = soup.find('title')
                if title_tag:
                    name = title_tag.get_text(strip=True)
            
            # Extract product image
            image_url = None
            for selector in self.product_patterns['image']:
                elements = soup.select(selector)
                for element in elements:
                    src = element.get('src') or element.get('data-src')
                    if src:
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            parsed_url = urlparse(url)
                            src = f"{parsed_url.scheme}://{parsed_url.netloc}{src}"
                        image_url = src
                        break
                if image_url:
                    break
            
            # Extract price
            price = None
            for selector in self.product_patterns['price']:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    price_match = re.search(r'[\$₹€£¥]?([\d,]+\.?\d*)', text)
                    if price_match:
                        price = price_match.group(1).replace(',', '')
                        break
                if price:
                    break
            
            # Extract rating
            rating = None
            for selector in self.product_patterns['rating']:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    rating_match = re.search(r'(\d+\.?\d*)', text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        if rating > 5:
                            rating = rating / 2  # Convert from 10-point scale
                        break
                if rating:
                    break
            
            return {
                'name': name or "Product",
                'image_url': image_url or 'https://via.placeholder.com/300x300?text=No+Image',
                'price': price,
                'rating': rating,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error extracting product info: {str(e)}")
            return {
                'name': "Product",
                'image_url': 'https://via.placeholder.com/300x300?text=No+Image',
                'price': None,
                'rating': None,
                'url': url
            }

    def scrape_product(self, url):
        """Main scraping method for any website"""
        try:
            logger.info(f"Starting universal scraping for: {url}")
            
            # Get HTML content
            soup = self.get_html(url)
            if not soup:
                return {'success': False, 'error': 'Failed to load webpage'}
            
            # Extract product information
            product_data = self.extract_product_info_universal(soup, url)
            
            # Detect and extract reviews
            detected_reviews = self.detect_reviews_automatically(soup)
            
            if not detected_reviews:
                return {'success': False, 'error': 'No reviews found on this page'}
            
            # Process detected reviews
            reviews_data = []
            for review_data in detected_reviews:
                element = review_data['element']
                text = review_data['text']
                
                # Skip very short reviews
                if len(text) < 20:
                    continue
                
                rating = self.extract_rating_from_text(text, element)
                author = self.extract_author_from_element(element)
                date = self.extract_date_from_element(element)
                
                reviews_data.append({
                    'text': text,
                    'rating': rating,
                    'author': author,
                    'date': date,
                    'score': review_data['score']
                })
            
            if not reviews_data:
                return {'success': False, 'error': 'No valid reviews found'}
            
            logger.info(f"Successfully extracted {len(reviews_data)} reviews")
            
            return {
                'success': True,
                'product': product_data,
                'reviews': reviews_data,
                'total_reviews': len(reviews_data),
                'scraped_url': url
            }
            
        except Exception as e:
            logger.error(f"Error in universal scraping: {str(e)}")
            return {'success': False, 'error': f'Scraping failed: {str(e)}'}

    def find_review_pages(self, soup, base_url):
        """Find additional review pages or pagination"""
        review_links = []
        
        # Look for review-related links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            text = link.get_text(strip=True).lower()
            
            if any(keyword in text for keyword in ['review', 'more review', 'all review', 'next', 'page']):
                if href.startswith('/'):
                    href = urljoin(base_url, href)
                review_links.append(href)
        
        return review_links[:3]  # Limit to 3 additional pages

    def scrape_with_pagination(self, url, max_pages=3):
        """Scrape reviews with pagination support"""
        all_reviews = []
        visited_urls = set()
        urls_to_visit = [url]
        
        page_count = 0
        while urls_to_visit and page_count < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
                
            visited_urls.add(current_url)
            
            logger.info(f"Scraping page {page_count + 1}: {current_url}")
            
            soup = self.get_html(current_url)
            if not soup:
                continue
            
            # Extract reviews from current page
            detected_reviews = self.detect_reviews_automatically(soup)
            
            for review_data in detected_reviews:
                element = review_data['element']
                text = review_data['text']
                
                if len(text) < 20:
                    continue
                
                rating = self.extract_rating_from_text(text, element)
                author = self.extract_author_from_element(element)
                date = self.extract_date_from_element(element)
                
                all_reviews.append({
                    'text': text,
                    'rating': rating,
                    'author': author,
                    'date': date,
                    'score': review_data['score']
                })
            
            # Find additional review pages
            if page_count == 0:  # Only look for pagination on first page
                additional_urls = self.find_review_pages(soup, current_url)
                urls_to_visit.extend(additional_urls)
            
            page_count += 1
            
            # Be respectful with delays
            if page_count < max_pages:
                time.sleep(random.uniform(2, 4))
        
        return all_reviews
