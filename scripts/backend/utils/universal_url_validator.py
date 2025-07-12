import re
from urllib.parse import urlparse
import requests
from .config_loader import config_loader

class UniversalURLValidator:
    def __init__(self):
        # Load configuration
        self.config_loader = config_loader
    
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
        
            # Check if domain is blocked
            domain = parsed_url.netloc.lower()
            blocked_domains = self.config_loader.get_blocked_domains()
            for blocked_domain in blocked_domains:
                if blocked_domain in domain:
                    return {
                        'valid': False, 
                        'error': f'Social media and video platforms are not supported'
                    }
        
            # Get known working domains from config
            enabled_websites = self.config_loader.get_enabled_websites()
            known_working_domains = []
            for website_config in enabled_websites.values():
                known_working_domains.extend(website_config.get('domains', []))
            
            # Remove wildcard domains for accessibility check
            known_working_domains = [d for d in known_working_domains if d != '*']
            
            should_check_accessibility = not any(known_domain in domain for known_domain in known_working_domains)
        
            # Only check accessibility for unknown domains, with shorter timeout
            if should_check_accessibility:
                try:
                    response = requests.head(url, timeout=5, allow_redirects=True)
                    if response.status_code >= 400:
                        # Try GET request as fallback
                        try:
                            response = requests.get(url, timeout=5, stream=True)
                            response.raise_for_status()
                        except requests.RequestException:
                            return {'valid': False, 'error': 'URL is not accessible'}
                except requests.RequestException:
                    # For unknown domains that fail accessibility check, still allow but warn
                    pass
        
            # Determine platform type using config loader
            platform = self.config_loader.identify_website(url)
        
            if not platform:
                return {'valid': False, 'error': 'Unsupported website'}
        
            return {
                'valid': True,
                'platform': platform,
                'normalized_url': url
            }
        
        except Exception as e:
            return {'valid': False, 'error': 'Invalid URL format'}
    
    def validate_url_simple(self, url):
        """Simple validation without accessibility check - for testing"""
        try:
            if not url or not isinstance(url, str):
                return {'valid': False, 'error': 'Invalid URL provided'}
        
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
        
            parsed_url = urlparse(url)
        
            if not parsed_url.netloc:
                return {'valid': False, 'error': 'Invalid URL format'}
        
            # Check if domain is blocked
            domain = parsed_url.netloc.lower()
            blocked_domains = self.config_loader.get_blocked_domains()
            for blocked_domain in blocked_domains:
                if blocked_domain in domain:
                    return {
                        'valid': False, 
                        'error': f'Social media and video platforms are not supported'
                    }
        
            # Determine platform type using config loader
            platform = self.config_loader.identify_website(url)
        
            if not platform:
                return {'valid': False, 'error': 'Unsupported website'}
        
            return {
                'valid': True,
                'platform': platform,
                'normalized_url': url
            }
        
        except Exception as e:
            return {'valid': False, 'error': 'Invalid URL format'}
    
    def get_supported_platforms(self):
        """Get list of supported platforms from configuration"""
        return self.config_loader.get_supported_platforms()
    
    def get_website_info(self, platform):
        """Get detailed information about a website platform"""
        return self.config_loader.get_website_info(platform)
