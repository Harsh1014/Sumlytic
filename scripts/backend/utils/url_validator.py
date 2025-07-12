import re
from urllib.parse import urlparse

class URLValidator:
    def __init__(self):
        self.supported_platforms = {
            'flipkart': {
                'domains': ['flipkart.com', 'www.flipkart.com'],
                'patterns': [r'/p/', r'/product/']
            },
            'amazon': {
                'domains': ['amazon.in', 'www.amazon.in', 'amazon.com', 'www.amazon.com'],
                'patterns': [r'/dp/', r'/product/', r'/gp/product/']
            },
            'myntra': {
                'domains': ['myntra.com', 'www.myntra.com'],
                'patterns': [r'/\d+/buy']
            },
            'snapdeal': {
                'domains': ['snapdeal.com', 'www.snapdeal.com'],
                'patterns': [r'/product/']
            }
        }
    
    def validate_url(self, url):
        try:
            # Basic URL validation
            if not url or not isinstance(url, str):
                return {'valid': False, 'error': 'Invalid URL provided'}
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed_url = urlparse(url)
            
            if not parsed_url.netloc:
                return {'valid': False, 'error': 'Invalid URL format'}
            
            # Check if URL is from supported platform
            platform = self.identify_platform(parsed_url.netloc, parsed_url.path)
            
            if not platform:
                supported_sites = ', '.join(self.supported_platforms.keys())
                return {
                    'valid': False, 
                    'error': f'Unsupported website. We currently support: {supported_sites}'
                }
            
            return {
                'valid': True,
                'platform': platform,
                'normalized_url': url
            }
            
        except Exception as e:
            return {'valid': False, 'error': 'Invalid URL format'}
    
    def identify_platform(self, domain, path):
        domain_lower = domain.lower()
        
        for platform, config in self.supported_platforms.items():
            # Check domain
            if any(supported_domain in domain_lower for supported_domain in config['domains']):
                # Check path patterns
                if any(re.search(pattern, path) for pattern in config['patterns']):
                    return platform
                # For some platforms, just domain match is enough
                elif platform in ['flipkart', 'amazon']:
                    return platform
        
        return None
    
    def get_supported_platforms(self):
        return list(self.supported_platforms.keys())
