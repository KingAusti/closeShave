"""Tests for API routes"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "merchants" in data
    assert isinstance(data["merchants"], list)


def test_get_merchants():
    """Test get merchants endpoint"""
    response = client.get("/api/merchants")
    assert response.status_code == 200
    data = response.json()
    assert "merchants" in data
    assert isinstance(data["merchants"], list)
    if len(data["merchants"]) > 0:
        merchant = data["merchants"][0]
        assert "name" in merchant
        assert "enabled" in merchant
        assert "version" in merchant


def test_validate_search_empty_query():
    """Test validation with empty query"""
    response = client.post("/api/validate", json={"query": ""})
    # Should return 422 validation error or 400
    assert response.status_code in [400, 422]


def test_validate_search_valid_query():
    """Test validation with valid query"""
    response = client.post("/api/validate", json={"query": "laptop"})
    # Should return 200 or handle gracefully
    assert response.status_code in [200, 422]
    if response.status_code == 200:
        data = response.json()
        assert "is_valid" in data
        assert "suggestions" in data


def test_search_products_empty_query():
    """Test search with empty query"""
    response = client.post("/api/search", json={"query": ""})
    # Should return validation error
    assert response.status_code in [400, 422]


def test_search_products_valid_query():
    """Test search with valid query"""
    response = client.post(
        "/api/search",
        json={
            "query": "test product",
            "max_results": 5
        }
    )
    # Should return 200 (even if no results)
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total_results" in data
    assert "search_time" in data
    assert isinstance(data["products"], list)


def test_image_proxy_no_url():
    """Test image proxy without URL"""
    response = client.get("/api/image-proxy")
    assert response.status_code == 422  # Validation error


def test_image_proxy_invalid_url():
    """Test image proxy with invalid URL"""
    response = client.get("/api/image-proxy?url=invalid")
    assert response.status_code in [400, 422, 502]


def test_image_proxy_private_ip():
    """Test image proxy with private IP"""
    response = client.get("/api/image-proxy?url=http://127.0.0.1/image.jpg")
    assert response.status_code in [403, 502]

