"""Base scraper class"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
from app.config import config
from app.utils.rate_limiter import RateLimiter
from app.utils.price_parser import PriceParser
from app.models import Product

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all merchant scrapers"""
    
    def __init__(self, merchant_name: str):
        self.merchant_name = merchant_name
        self.config = config.get_scraper_config(merchant_name)
        self.rate_limiter = RateLimiter(config.get_request_delay())
        self.price_parser = PriceParser()
        self.requires_js = self.config.get("requires_js", False)
        self.selectors = self.config.get("selectors", {})
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        if self.requires_js:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
    
    def get_search_url(self, query: str) -> str:
        """Get search URL for query"""
        url_template = self.selectors.get("search_url", "")
        return url_template.format(query=query.replace(" ", "+"))
    
    async def search(self, query: str, max_results: int = 20) -> List[Product]:
        """Search for products"""
        search_url = self.get_search_url(query)
        domain = self._get_domain(search_url)
        
        # Check robots.txt and rate limit
        allowed = await self.rate_limiter.check_robots_txt(search_url)
        if not allowed:
            return []
        
        await self.rate_limiter.wait_if_needed(domain)
        
        try:
            if self.requires_js:
                return await self._search_with_playwright(search_url, max_results)
            else:
                return await self._search_with_requests(search_url, max_results)
        except Exception as e:
            logger.error(f"Error searching {self.merchant_name}: {e}", exc_info=True)
            return []
    
    async def _search_with_requests(self, url: str, max_results: int) -> List[Product]:
        """Search using requests and BeautifulSoup"""
        user_agents = config.get_user_agents()
        headers = {
            "User-Agent": user_agents[0] if user_agents else 
                         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with httpx.AsyncClient(timeout=config.get_timeout(), headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            return self._parse_results(soup, max_results)
    
    async def _search_with_playwright(self, url: str, max_results: int) -> List[Product]:
        """Search using Playwright"""
        if not self.page:
            raise RuntimeError("Playwright page not initialized")
        
        await self.page.goto(url, wait_until="networkidle")
        await self.page.wait_for_timeout(2000)  # Wait for JS to render
        
        html = await self.page.content()
        soup = BeautifulSoup(html, 'lxml')
        return self._parse_results(soup, max_results)
    
    @abstractmethod
    def _parse_results(self, soup: BeautifulSoup, max_results: int) -> List[Product]:
        """Parse search results from BeautifulSoup"""
        pass
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _extract_price(self, element) -> Optional[float]:
        """Extract price from element"""
        if not element:
            return None
        
        price_text = element.get_text(strip=True) if hasattr(element, 'get_text') else str(element)
        return self.price_parser.parse_price(price_text)
    
    def _extract_text(self, element, default: str = "") -> str:
        """Extract text from element"""
        if not element:
            return default
        return element.get_text(strip=True) if hasattr(element, 'get_text') else str(element)
    
    def _extract_url(self, element, base_url: str = "") -> str:
        """Extract URL from element"""
        if not element:
            return ""
        
        if hasattr(element, 'get'):
            href = element.get('href', '')
        else:
            href = str(element)
        
        if href.startswith('http'):
            return href
        elif href.startswith('/'):
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{href}"
        else:
            return f"{base_url}/{href}" if base_url else href
    
    def _extract_image_url(self, element, base_url: str = "") -> str:
        """Extract image URL from element"""
        if not element:
            return ""
        
        if hasattr(element, 'get'):
            src = element.get('src', '') or element.get('data-src', '')
        else:
            src = str(element)
        
        if src.startswith('http'):
            return src
        elif src.startswith('/'):
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{src}"
        else:
            return f"{base_url}/{src}" if base_url else src
    
    def _determine_availability(self, element) -> str:
        """Determine product availability"""
        if not element:
            return "in_stock"
        
        text = self._extract_text(element).lower()
        if any(word in text for word in ['out of stock', 'unavailable', 'sold out']):
            return "out_of_stock"
        elif any(word in text for word in ['limited', 'few left', 'only']):
            return "limited"
        return "in_stock"

