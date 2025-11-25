"""FastAPI main application"""

import logging
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import LOGS_DIR, config
from app.exceptions import CloseShaveException
from app.utils.database import db

# Set up logging
LOGS_DIR.mkdir(exist_ok=True)
log_file = LOGS_DIR / "scraper.log"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=7),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CloseShave Web Scraper API",
    description="API for searching products across multiple merchants",
    version=config.version.get("version", "0.1.0"),
)

# CORS middleware
# Allow requests from localhost (dev) and from frontend container (Docker)
cors_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost",  # Docker frontend on port 80
    "http://localhost:80",
    "http://frontend",  # Docker service name
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting CloseShave Web Scraper API")
    try:
        await db.init_db()
        logger.info("Database initialized")
        await db.cleanup_expired()
        logger.info("Cleaned up expired cache entries")
    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down CloseShave Web Scraper API")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "CloseShave Web Scraper API",
        "version": config.version.get("version", "0.1.0"),
        "status": "running",
    }


@app.exception_handler(CloseShaveException)
async def closeshave_exception_handler(request: Request, exc: CloseShaveException):
    """Handle CloseShave custom exceptions"""
    logger.warning(
        f"CloseShave exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        },
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
    )
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
