"""eBay scraper"""

from typing import List
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import Product


class EbayScraper(BaseScraper):
    """Scraper for eBay"""
    
    def __init__(self):
        super().__init__("ebay")
    
    def _parse_results(self, soup: BeautifulSoup, max_results: int) -> List[Product]:
        """Parse eBay search results"""
        products = []
        container_selector = self.selectors.get("product_container", ".s-item")
        containers = soup.select(container_selector)[:max_results]
        
        for container in containers:
            try:
                # Skip header items
                if "s-item__header" in str(container.get("class", [])):
                    continue
                
                # Title
                title_elem = container.select_one(self.selectors.get("title", ".s-item__title"))
                title = self._extract_text(title_elem)
                if not title or "Shop on eBay" in title:
                    continue
                
                # Price
                price_elem = container.select_one(self.selectors.get("price", ".s-item__price"))
                base_price = self._extract_price(price_elem) or 0.0
                
                # Image
                image_elem = container.select_one(self.selectors.get("image", ".s-item__image img"))
                image_url = self._extract_image_url(image_elem, "https://www.ebay.com")
                direct_image_url = image_url
                
                # Link
                link_elem = container.select_one(self.selectors.get("link", ".s-item__link"))
                product_url = self._extract_url(link_elem, "https://www.ebay.com")
                
                # Availability
                availability_elem = container.select_one(self.selectors.get("availability", ".s-item__availability"))
                availability = self._determine_availability(availability_elem)
                
                product = Product(
                    title=title,
                    price=base_price,
                    base_price=base_price,
                    shipping_cost=0.0,
                    tax=0.0,
                    total_price=base_price,
                    image_url=image_url,
                    direct_image_url=direct_image_url,
                    product_url=product_url,
                    merchant="ebay",
                    availability=availability
                )
                products.append(product)
            except Exception as e:
                continue
        
        return products

