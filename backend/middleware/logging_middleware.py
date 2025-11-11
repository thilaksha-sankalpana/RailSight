# backend/middleware/logging_middleware.py
"""
Middleware for request/response logging
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = id(request)
        
        # Log request
        logger.info(
            f"➡️  [{request_id}] {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Track execution time
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"⬅️  [{request_id}] {request.method} {request.url.path} "
                f"→ {response.status_code} ({duration:.2f}s)"
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = str(request_id)
            response.headers["X-Process-Time"] = f"{duration:.4f}"
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"❌ [{request_id}] {request.method} {request.url.path} "
                f"→ ERROR ({duration:.2f}s): {str(e)}"
            )
            raise


class PerformanceMonitorMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor slow requests
    """
    
    SLOW_REQUEST_THRESHOLD = 2.0  # seconds
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Log slow requests
        if duration > self.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"⚠️  SLOW REQUEST: {request.method} {request.url.path} "
                f"took {duration:.2f}s (threshold: {self.SLOW_REQUEST_THRESHOLD}s)"
            )
        
        return response