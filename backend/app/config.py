"""Configuration management"""

import json
import os
from pathlib import Path
from typing import Dict, Any

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


class Config:
    """Configuration manager"""
    
    def __init__(self):
        self.settings_path = CONFIG_DIR / "settings.json"
        self.scrapers_path = CONFIG_DIR / "scrapers.json"
        self.version_path = CONFIG_DIR / "version.json"
        self.settings = self._load_settings()
        self.scrapers = self._load_scrapers()
        self.version = self._load_version()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file"""
        if self.settings_path.exists():
            with open(self.settings_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_scrapers(self) -> Dict[str, Any]:
        """Load scraper configurations"""
        if self.scrapers_path.exists():
            with open(self.scrapers_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_version(self) -> Dict[str, Any]:
        """Load version information"""
        if self.version_path.exists():
            with open(self.version_path, 'r') as f:
                return json.load(f)
        return {"version": "0.1.0", "scrapers": {}}
    
    def get_merchant_enabled(self, merchant: str) -> bool:
        """Check if a merchant is enabled"""
        return self.settings.get("merchants", {}).get(merchant, False)
    
    def get_scraper_config(self, merchant: str) -> Dict[str, Any]:
        """Get scraper configuration for a merchant"""
        return self.scrapers.get(merchant, {})
    
    def get_request_delay(self) -> float:
        """Get request delay in seconds"""
        return self.settings.get("scraping", {}).get("request_delay", 1.0)
    
    def get_timeout(self) -> int:
        """Get request timeout in seconds"""
        return self.settings.get("scraping", {}).get("timeout", 30)
    
    def get_max_retries(self) -> int:
        """Get maximum retry attempts"""
        return self.settings.get("scraping", {}).get("max_retries", 3)
    
    def get_user_agents(self) -> list:
        """Get list of user agents"""
        return self.settings.get("scraping", {}).get("user_agents", [])
    
    def get_cache_ttl_hours(self) -> int:
        """Get cache TTL in hours"""
        return self.settings.get("cache", {}).get("ttl_hours", 1)
    
    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled"""
        return self.settings.get("cache", {}).get("enabled", True)
    
    def get_geolocation_api_key(self) -> str:
        """Get geolocation API key"""
        return os.getenv("GEOLOCATION_API_KEY", 
                        self.settings.get("geolocation", {}).get("api_key", ""))
    
    def get_geolocation_provider(self) -> str:
        """Get geolocation provider"""
        return self.settings.get("geolocation", {}).get("provider", "ip-api.com")
    
    def is_tax_enabled(self) -> bool:
        """Check if tax calculation is enabled"""
        return self.settings.get("tax", {}).get("enabled", True)
    
    def is_shipping_enabled(self) -> bool:
        """Check if shipping calculation is enabled"""
        return self.settings.get("shipping", {}).get("enabled", True)


# Global config instance
config = Config()

