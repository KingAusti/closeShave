"""Amazon scraper"""

from bs4 import BeautifulSoup

from app.models import Product
from app.scrapers.base import BaseScraper


class AmazonScraper(BaseScraper):
    """Scraper for Amazon"""

    def __init__(self):
        super().__init__("amazon")

    def _parse_results(self, soup: BeautifulSoup, max_results: int) -> list[Product]:
        """Parse Amazon search results"""
        products = []
        container_selector = self.selectors.get(
            "product_container", "[data-component-type='s-search-result']"
        )
        containers = soup.select(container_selector)[:max_results]

        for container in containers:
            try:
                # Title
                title_elem = container.select_one(self.selectors.get("title", "h2 a span"))
                title = self._extract_text(title_elem)
                if not title:
                    continue

                # Price
                price_elem = container.select_one(
                    self.selectors.get("price", ".a-price .a-offscreen")
                )
                base_price = self._extract_price(price_elem) or 0.0

                # Image
                image_elem = container.select_one(self.selectors.get("image", ".s-image"))
                image_url = self._extract_image_url(image_elem, "https://www.amazon.com")
                direct_image_url = image_url

                # Link
                link_elem = container.select_one(self.selectors.get("link", "h2 a"))
                product_url = self._extract_url(link_elem, "https://www.amazon.com")

                # Availability
                availability_elem = container.select_one(
                    self.selectors.get("availability", ".a-color-state, .a-color-success")
                )
                availability = self._determine_availability(availability_elem)

                # Merchant ID (ASIN)
                merchant_id = container.get("data-asin", "")

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
                    merchant="amazon",
                    availability=availability,
                    merchant_id=merchant_id,
                )
                products.append(product)
            except Exception:
                continue

        return products
