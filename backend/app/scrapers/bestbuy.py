"""Best Buy scraper"""

from bs4 import BeautifulSoup

from app.models import Product
from app.scrapers.base import BaseScraper


class BestBuyScraper(BaseScraper):
    """Scraper for Best Buy"""

    def __init__(self):
        super().__init__("bestbuy")

    def _parse_results(self, soup: BeautifulSoup, max_results: int) -> list[Product]:
        """Parse Best Buy search results"""
        products = []
        container_selector = self.selectors.get("product_container", ".sku-item")
        containers = soup.select(container_selector)[:max_results]

        for container in containers:
            try:
                # Title
                title_elem = container.select_one(self.selectors.get("title", ".sku-title h4 a"))
                title = self._extract_text(title_elem)
                if not title:
                    continue

                # Price
                price_elem = container.select_one(
                    self.selectors.get("price", ".priceView-customer-price span")
                )
                base_price = self._extract_price(price_elem) or 0.0

                # Image
                image_elem = container.select_one(self.selectors.get("image", ".product-image img"))
                image_url = self._extract_image_url(image_elem, "https://www.bestbuy.com")
                direct_image_url = image_url

                # Link
                link_elem = container.select_one(self.selectors.get("link", ".sku-title h4 a"))
                product_url = self._extract_url(link_elem, "https://www.bestbuy.com")

                # Availability
                availability_elem = container.select_one(
                    self.selectors.get("availability", ".fulfillment-fulfillment-summary")
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
                    merchant="bestbuy",
                    availability=availability,
                )
                products.append(product)
            except Exception:
                continue

        return products
