import pytest
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import Product
from typing import List

class MockScraper(BaseScraper):
    def _parse_results(self, soup: BeautifulSoup, max_results: int) -> List[Product]:
        return []

@pytest.fixture
def scraper():
    return MockScraper("test_merchant")

def test_resolve_url_absolute(scraper):
    assert scraper._resolve_url("http://example.com/product") == "http://example.com/product"
    assert scraper._resolve_url("https://example.com/product") == "https://example.com/product"

def test_resolve_url_relative_root(scraper):
    base_url = "https://example.com/search"
    assert scraper._resolve_url("/product", base_url) == "https://example.com/product"

def test_resolve_url_relative_path(scraper):
    base_url = "https://example.com/search"
    assert scraper._resolve_url("product", base_url) == "https://example.com/search/product"

def test_extract_url(scraper):
    soup = BeautifulSoup('<a href="/product">Link</a>', 'lxml')
    element = soup.find('a')
    base_url = "https://example.com"
    assert scraper._extract_url(element, base_url) == "https://example.com/product"

def test_extract_image_url(scraper):
    soup = BeautifulSoup('<img src="/image.jpg" />', 'lxml')
    element = soup.find('img')
    base_url = "https://example.com"
    assert scraper._extract_image_url(element, base_url) == "https://example.com/image.jpg"

def test_extract_image_url_data_src(scraper):
    soup = BeautifulSoup('<img data-src="/image.jpg" />', 'lxml')
    element = soup.find('img')
    base_url = "https://example.com"
    assert scraper._extract_image_url(element, base_url) == "https://example.com/image.jpg"
