"""Tests for utility functions"""

import pytest
from app.utils.price_parser import PriceParser


def test_calculate_tax():
    """Test tax calculation"""
    price = 100.0
    tax_rate = 0.08  # 8%
    tax = PriceParser.calculate_tax(price, tax_rate)
    assert tax == 8.0


def test_calculate_total():
    """Test total price calculation"""
    base_price = 100.0
    shipping = 5.0
    tax = 8.0
    total = PriceParser.calculate_total(base_price, shipping, tax)
    assert total == 113.0


def test_parse_price():
    """Test price parsing"""
    # Test various price formats
    assert PriceParser.parse_price("$10.99") == 10.99
    assert PriceParser.parse_price("10.99") == 10.99
    assert PriceParser.parse_price("$1,234.56") == 1234.56


def test_get_cache_key():
    """Test cache key generation"""
    from app.api.routes import get_cache_key
    
    key1 = get_cache_key("laptop", "amazon", {"max_results": 20})
    key2 = get_cache_key("laptop", "amazon", {"max_results": 20})
    key3 = get_cache_key("laptop", "ebay", {"max_results": 20})
    
    # Same inputs should produce same key
    assert key1 == key2
    # Different inputs should produce different keys
    assert key1 != key3

