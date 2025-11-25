"""Custom exception classes for the CloseShave application"""

from typing import Any


class CloseShaveException(Exception):
    """Base exception for all CloseShave exceptions"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for JSON response"""
        result = {
            "error": self.error_code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


class ValidationError(CloseShaveException):
    """Raised when input validation fails"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message, status_code=400, error_code="VALIDATION_ERROR", details=details
        )


class ScraperError(CloseShaveException):
    """Raised when a scraper encounters an error"""

    def __init__(
        self, message: str, merchant: str | None = None, details: dict[str, Any] | None = None
    ):
        error_details = details or {}
        if merchant:
            error_details["merchant"] = merchant
        super().__init__(
            message=message, status_code=502, error_code="SCRAPER_ERROR", details=error_details
        )


class RateLimitError(CloseShaveException):
    """Raised when rate limit is exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        error_details = details or {}
        if retry_after:
            error_details["retry_after"] = retry_after
        super().__init__(
            message=message, status_code=429, error_code="RATE_LIMIT_ERROR", details=error_details
        )


class DatabaseError(CloseShaveException):
    """Raised when database operations fail"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message, status_code=500, error_code="DATABASE_ERROR", details=details
        )


class ConfigurationError(CloseShaveException):
    """Raised when configuration is invalid or missing"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message, status_code=500, error_code="CONFIGURATION_ERROR", details=details
        )


class ImageProxyError(CloseShaveException):
    """Raised when image proxy operations fail"""

    def __init__(self, message: str, status_code: int = 502, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code="IMAGE_PROXY_ERROR",
            details=details,
        )
