"""Main FastAPI application with improved structure."""
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from core import config
from core.logging_config import logger
from core.middleware import LoggingMiddleware, setup_cors
from api.routers import bus, direction, bus_stop, apple_shortcuts

# Description for API documentation
description = """
API non-officielle fournissant des informations sur les lignes de bus,
directions, arrêts et horaires de la ville de Chambéry.

Tous les endpoints retournent du JSON. La plupart acceptent des query parameters
pour filtrer les résultats.
"""

# Tags metadata for better organization
tags_metadata = [
    {
        "name": "bus",
        "description": "Opérations sur les lignes de bus. Récupérer toutes les lignes ou filtrer par direction.",
    },
    {
        "name": "direction",
        "description": "Opérations sur les directions. Récupérer toutes les directions ou filtrer par bus/arrêt.",
    },
    {
        "name": "bus_stop",
        "description": "Opérations sur les arrêts de bus. Inclut la recherche et les horaires en temps réel.",
    },
    {
        "name": "apple_shortcuts",
        "description": "Endpoints compatibles Apple Shortcuts (format dict au lieu de list).",
    },
]

# Create FastAPI application
app = FastAPI(
    title="SynchroBus API",
    description=description,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    contact={
        "name": "SynchroBus API",
        "url": "https://github.com/leodbrs/synchrobus-api",
    },
)

# Configure CORS
setup_cors(app, config.CORS_ORIGINS)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(bus.router)
app.include_router(direction.router)
app.include_router(bus_stop.router)
app.include_router(apple_shortcuts.router)

logger.info("All routers registered successfully")


@app.get("/", include_in_schema=False)
def root():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {"status": "healthy", "version": "2.0.0"}


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("=" * 50)
    logger.info("SynchroBus API starting up...")
    logger.info(f"Environment: {config.LOG_LEVEL}")
    logger.info(f"CORS Origins: {config.CORS_ORIGINS}")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("SynchroBus API shutting down...")
