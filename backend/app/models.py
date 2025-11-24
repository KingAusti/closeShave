"""Data models for the application"""

from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime


class Product(BaseModel):
    """Product model"""
    title: str
    price: float
    base_price: float = Field(description="Price before shipping and tax")
    shipping_cost: float = 0.0
    tax: float = 0.0
    total_price: float = Field(description="Total price including shipping and tax")
    image_url: str
    direct_image_url: str = Field(description="Direct link to image")
    product_url: str
    merchant: str
    availability: str = "in_stock"  # in_stock, out_of_stock, limited
    merchant_id: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None


class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, description="Product search query")
    merchants: Optional[List[str]] = None
    max_results: int = Field(default=20, ge=1, le=100)
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    brand: Optional[str] = None
    barcode: Optional[str] = None
    include_out_of_stock: bool = True


class SearchResponse(BaseModel):
    """Search response model"""
    products: List[Product]
    total_results: int
    search_time: float
    cached: bool = False
    location: Optional[dict] = None


class MerchantInfo(BaseModel):
    """Merchant information"""
    name: str
    enabled: bool
    version: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    merchants: List[MerchantInfo]


class ValidationRequest(BaseModel):
    """Search validation request model"""
    query: str = Field(..., min_length=1, description="Search query to validate")


class ValidationResponse(BaseModel):
    """Search validation response model"""
    is_valid: bool = Field(description="Whether the query is valid")
    has_results: bool = Field(description="Whether the query returns results")
    suggestions: List[str] = Field(default_factory=list, description="Suggested search terms")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")

