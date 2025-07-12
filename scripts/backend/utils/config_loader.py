import json
import os
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

class WebsiteConfigLoader:
    def __init__(self, config_path: str = None):
        """Initialize the configuration loader"""
        if config_path is None:
            # Default path relative to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, '..', '..', '..')
            config_path = os.path.join(project_root, 'config', 'websites.json')
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def reload_config(self):
        """Reload the configuration from file"""
        self.config = self._load_config()
    
    def get_website_config(self, website_key: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific website"""
        return self.config.get('websites', {}).get(website_key)
    
    def get_all_websites(self) -> Dict[str, Any]:
        """Get all website configurations"""
        return self.config.get('websites', {})
    
    def get_enabled_websites(self) -> Dict[str, Any]:
        """Get only enabled website configurations"""
        websites = self.config.get('websites', {})
        return {k: v for k, v in websites.items() if v.get('enabled', True)}
    
    def get_websites_by_category(self, category: str) -> Dict[str, Any]:
        """Get websites filtered by category"""
        websites = self.get_enabled_websites()
        return {k: v for k, v in websites.items() if v.get('category') == category}
    
    def get_websites_by_scraper(self, scraper: str) -> Dict[str, Any]:
        """Get websites filtered by scraper type"""
        websites = self.get_enabled_websites()
        return {k: v for k, v in websites.items() if v.get('scraper') == scraper}
    
    def get_blocked_domains(self) -> List[str]:
        """Get list of blocked domains"""
        return self.config.get('blocked_domains', [])
    
    def get_categories(self) -> Dict[str, Any]:
        """Get all categories"""
        return self.config.get('categories', {})
    
    def get_scrapers(self) -> Dict[str, Any]:
        """Get all scrapers"""
        return self.config.get('scrapers', {})
    
    def get_settings(self) -> Dict[str, Any]:
        """Get application settings"""
        return self.config.get('settings', {})
    
    def identify_website(self, url: str) -> Optional[str]:
        """Identify which website a URL belongs to"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            path = parsed_url.path.lower()
            
            # Check if domain is blocked
            blocked_domains = self.get_blocked_domains()
            for blocked_domain in blocked_domains:
                if blocked_domain in domain:
                    return None
            
            # Check each website configuration
            websites = self.get_enabled_websites()
            
            # Sort by priority (lower number = higher priority)
            sorted_websites = sorted(websites.items(), key=lambda x: x[1].get('priority', 999))
            
            for website_key, website_config in sorted_websites:
                if self._matches_website_config(domain, path, website_config):
                    return website_key
            
            return None
            
        except Exception:
            return None
    
    def _matches_website_config(self, domain: str, path: str, config: Dict[str, Any]) -> bool:
        """Check if a domain and path match a website configuration"""
        domains = config.get('domains', [])
        patterns = config.get('patterns', [])
        
        # Check domain match
        domain_matches = False
        for config_domain in domains:
            if config_domain == '*' or config_domain in domain:
                domain_matches = True
                break
        
        if not domain_matches:
            return False
        
        # Check pattern match
        pattern_matches = False
        for pattern in patterns:
            if pattern == '*' or re.search(pattern, path):
                pattern_matches = True
                break
        
        return pattern_matches
    
    def get_website_info(self, website_key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a website"""
        website_config = self.get_website_config(website_key)
        if not website_config:
            return None
        
        category_key = website_config.get('category')
        scraper_key = website_config.get('scraper')
        
        category_info = self.get_categories().get(category_key, {})
        scraper_info = self.get_scrapers().get(scraper_key, {})
        
        return {
            'key': website_key,
            'config': website_config,
            'category': category_info,
            'scraper': scraper_info
        }
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of all supported platform keys"""
        return list(self.get_enabled_websites().keys())
    
    def get_website_names(self) -> Dict[str, str]:
        """Get mapping of website keys to display names"""
        websites = self.get_enabled_websites()
        return {k: v.get('name', k) for k, v in websites.items()}
    
    def add_website(self, key: str, config: Dict[str, Any]) -> bool:
        """Add a new website configuration"""
        try:
            websites = self.config.get('websites', {})
            websites[key] = config
            self.config['websites'] = websites
            self._save_config()
            return True
        except Exception:
            return False
    
    def update_website(self, key: str, config: Dict[str, Any]) -> bool:
        """Update an existing website configuration"""
        try:
            websites = self.config.get('websites', {})
            if key in websites:
                websites[key].update(config)
                self.config['websites'] = websites
                self._save_config()
                return True
            return False
        except Exception:
            return False
    
    def remove_website(self, key: str) -> bool:
        """Remove a website configuration"""
        try:
            websites = self.config.get('websites', {})
            if key in websites:
                del websites[key]
                self.config['websites'] = websites
                self._save_config()
                return True
            return False
        except Exception:
            return False
    
    def enable_website(self, key: str) -> bool:
        """Enable a website"""
        return self.update_website(key, {'enabled': True})
    
    def disable_website(self, key: str) -> bool:
        """Disable a website"""
        return self.update_website(key, {'enabled': False})
    
    def _save_config(self):
        """Save the configuration back to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise IOError(f"Failed to save configuration: {e}")
    
    def validate_config(self) -> List[str]:
        """Validate the configuration and return any errors"""
        errors = []
        
        websites = self.config.get('websites', {})
        categories = self.config.get('categories', {})
        scrapers = self.config.get('scrapers', {})
        
        # Check for missing categories
        for key, config in websites.items():
            category = config.get('category')
            if category and category not in categories:
                errors.append(f"Website '{key}' references unknown category '{category}'")
        
        # Check for missing scrapers
        for key, config in websites.items():
            scraper = config.get('scraper')
            if scraper and scraper not in scrapers:
                errors.append(f"Website '{key}' references unknown scraper '{scraper}'")
        
        return errors

# Global instance for easy access
config_loader = WebsiteConfigLoader() 