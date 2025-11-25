"""Walmart scraper"""

from bs4 import BeautifulSoup

from app.models import Product
from app.scrapers.base import BaseScraper


class WalmartScraper(BaseScraper):
    """Scraper for Walmart"""

    def __init__(self):
        super().__init__("walmart")

    def _parse_results(self, soup: BeautifulSoup, max_results: int) -> list[Product]:
        """Parse Walmart search results"""
        products = []
        container_selector = self.selectors.get("product_container", "[data-testid='item-stack']")
        containers = soup.select(container_selector)[:max_results]

        for container in containers:
            try:
                # Title
                title_elem = container.select_one(
                    self.selectors.get("title", "[data-automation-id='product-title']")
                )
                title = self._extract_text(title_elem)
                if not title:
                    continue

                # Price
                price_elem = container.select_one(self.selectors.get("price", "[itemprop='price']"))
                base_price = self._extract_price(price_elem) or 0.0

                # Image
                image_elem = container.select_one(
                    self.selectors.get("image", "img[data-testid='product-image']")
                )
                image_url = self._extract_image_url(image_elem, "https://www.walmart.com")
                direct_image_url = image_url

                # Link
                link_elem = container.select_one(
                    self.selectors.get("link", "a[data-testid='product-title']")
                )
                product_url = self._extract_url(link_elem, "https://www.walmart.com")

                # Availability
                availability_elem = container.select_one(
                    self.selectors.get("availability", "[data-testid='product-availability']")
                )
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
                    merchant="walmart",
                    availability=availability,
                )
                products.append(product)
            except Exception:
                continue

        return products
