"""Data models for the application"""

from pydantic import BaseModel, Field


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
    merchant_id: str | None = None
    brand: str | None = None
    rating: float | None = None
    review_count: int | None = None


class SearchRequest(BaseModel):
    """Search request model"""

    query: str = Field(..., min_length=1, description="Product search query")
    merchants: list[str] | None = None
    max_results: int = Field(default=20, ge=1, le=100)
    min_price: float | None = None
    max_price: float | None = None
    brand: str | None = None
    barcode: str | None = None
    include_out_of_stock: bool = True


class SearchResponse(BaseModel):
    """Search response model"""

    products: list[Product]
    total_results: int
    search_time: float
    cached: bool = False
    location: dict | None = None


class MerchantInfo(BaseModel):
    """Merchant information"""

    name: str
    enabled: bool
    version: str


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    merchants: list[MerchantInfo]


class ValidationRequest(BaseModel):
    """Search validation request model"""

    query: str = Field(..., min_length=1, description="Search query to validate")


class ValidationResponse(BaseModel):
    """Search validation response model"""

    is_valid: bool = Field(description="Whether the query is valid")
    has_results: bool = Field(description="Whether the query returns results")
    suggestions: list[str] = Field(default_factory=list, description="Suggested search terms")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")
