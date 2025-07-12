# Website Configuration System

This directory contains the centralized configuration for all websites supported by the QuickReview application.

## Files

- `websites.json` - Main configuration file containing all website definitions
- `README.md` - This documentation file

## Configuration Structure

The `websites.json` file contains the following sections:

### Websites

Each website has the following properties:

- `name` - Display name for the website
- `domains` - Array of domain names that match this website
- `patterns` - Array of URL patterns that match this website
- `category` - Category key (ecommerce, reviews, travel, generic)
- `scraper` - Scraper type to use (amazon, flipkart, universal)
- `enabled` - Whether the website is enabled
- `priority` - Priority for matching (lower number = higher priority)
- `description` - Description of the website
- `icon` - Emoji icon for display

### Categories

Defines different types of websites:

- `ecommerce` - Online shopping platforms
- `reviews` - Review and rating platforms  
- `travel` - Travel booking platforms
- `generic` - Other websites

### Scrapers

Defines available scraping methods:

- `amazon` - Specialized Amazon scraper
- `flipkart` - Specialized Flipkart scraper
- `universal` - Generic scraper for most websites

### Blocked Domains

List of domains that are not supported (social media, etc.)

### Settings

Global application settings for scraping behavior.

## Adding a New Website

To add a new website, edit `websites.json` and add a new entry to the `websites` object:

```json
{
  "websites": {
    "mywebsite": {
      "name": "My Website",
      "domains": ["mywebsite.com", "www.mywebsite.com"],
      "patterns": ["/product/", "/item/"],
      "category": "ecommerce",
      "scraper": "universal",
      "enabled": true,
      "priority": 3,
      "description": "My e-commerce website",
      "icon": "🛒"
    }
  }
}
```

## Removing a Website

To remove a website, either:

1. Delete the entry from `websites.json`
2. Set `"enabled": false` to disable it temporarily

## API Endpoints

The backend provides these endpoints for managing websites:

- `GET /api/websites` - Get all website configurations
- `GET /api/websites/<key>` - Get specific website info
- `POST /api/websites/<key>/enable` - Enable a website
- `POST /api/websites/<key>/disable` - Disable a website
- `POST /api/websites` - Add a new website
- `DELETE /api/websites/<key>` - Remove a website
- `POST /api/websites/validate` - Validate configuration

## Frontend Integration

The frontend automatically loads website configurations from the API and displays them in the URL input component. The website manager component provides a UI for adding/removing websites.

## Priority System

Websites are matched by priority (lower number = higher priority):

1. Specialized scrapers (amazon, flipkart)
2. Major e-commerce sites
3. Review platforms
4. Generic e-commerce
5. Generic websites

## Wildcard Domains

Use `"*"` as a domain to match any domain. This is useful for generic patterns like WordPress sites.

## Pattern Matching

URL patterns use regex syntax. Common patterns:

- `/product/` - Matches URLs containing "/product/"
- `/\\d+/buy` - Matches URLs with numbers followed by "/buy"
- `*` - Matches any URL pattern

## Validation

The configuration system validates:

- Required fields are present
- Categories exist
- Scrapers exist
- No duplicate keys

## Benefits

This centralized system provides:

1. **Easy Management** - Add/remove websites by editing JSON
2. **Consistency** - Same configuration used across backend and frontend
3. **Flexibility** - Support for different categories and scrapers
4. **Maintainability** - Clear structure and documentation
5. **API Integration** - RESTful endpoints for programmatic access 