"""FastAPI main application"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import config, LOGS_DIR
from app.api.routes import router
from app.utils.database import db

# Set up logging
LOGS_DIR.mkdir(exist_ok=True)
log_file = LOGS_DIR / "scraper.log"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=7),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CloseShave Web Scraper API",
    description="API for searching products across multiple merchants",
    version=config.version.get("version", "0.1.0")
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
    await db.init_db()
    logger.info("Database initialized")
    await db.cleanup_expired()
    logger.info("Cleaned up expired cache entries")


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
        "status": "running"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

