"""Newegg scraper"""

from typing import List
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import Product


class NeweggScraper(BaseScraper):
    """Scraper for Newegg"""
    
    def __init__(self):
        super().__init__("newegg")
    
    def _parse_results(self, soup: BeautifulSoup, max_results: int) -> List[Product]:
        """Parse Newegg search results"""
        products = []
        container_selector = self.selectors.get("product_container", ".item-cell")
        containers = soup.select(container_selector)[:max_results]
        
        for container in containers:
            try:
                # Title
                title_elem = container.select_one(self.selectors.get("title", ".item-title"))
                title = self._extract_text(title_elem)
                if not title:
                    continue
                
                # Price
                price_elem = container.select_one(self.selectors.get("price", ".price-current"))
                base_price = self._extract_price(price_elem) or 0.0
                
                # Image
                image_elem = container.select_one(self.selectors.get("image", ".item-img img"))
                image_url = self._extract_image_url(image_elem, "https://www.newegg.com")
                direct_image_url = image_url
                
                # Link
                link_elem = container.select_one(self.selectors.get("link", ".item-title"))
                product_url = self._extract_url(link_elem, "https://www.newegg.com")
                
                # Availability
                availability_elem = container.select_one(self.selectors.get("availability", ".item-promo"))
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
                    merchant="newegg",
                    availability=availability
                )
                products.append(product)
            except Exception as e:
                continue
        
        return products

