"""Middleware for logging, CORS, and security."""
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from core.logging_config import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        """
        Log request and response details.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware/handler in the chain
            
        Returns:
            Response: The HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started | "
            f"ID: {request_id} | "
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed | "
            f"ID: {request_id} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.4f}s"
        )
        
        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        return response


def setup_cors(app, allowed_origins: list[str]):
    """
    Configure CORS middleware.
    
    Args:
        app: The FastAPI application
        allowed_origins: List of allowed origins
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    logger.info(f"CORS configured with origins: {allowed_origins}")
