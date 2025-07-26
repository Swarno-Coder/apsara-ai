import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
# from fastapi.middleware import BaseHTTPMiddleware
from starlette.middleware.base import BaseHTTPMiddleware 

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Log request
        start_time = time.time()
        logger.info(f"[{request_id}] {request.method} {request.url.path} - Started")
        
        # Add request ID to headers
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(f"[{request_id}] {request.method} {request.url.path} - "
                       f"Status: {response.status_code} - Time: {process_time:.3f}s")
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"[{request_id}] {request.method} {request.url.path} - "
                        f"Error: {str(e)} - Time: {process_time:.3f}s")
            raise

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, max_requests_per_minute: int = 60):
        super().__init__(app)
        self.max_requests = max_requests_per_minute
        self.requests = {}  # IP -> list of timestamps
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP with fallback for cases where request.client is None
        client_ip = "unknown"
        if request.client:
            client_ip = request.client.host
        else:
            # Try to get IP from headers (for proxy scenarios)
            client_ip = request.headers.get("X-Forwarded-For", "unknown")
            if client_ip != "unknown":
                client_ip = client_ip.split(",")[0].strip()
        
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            from fastapi import HTTPException
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            
            # Return JSON error response
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "request_id": getattr(request.state, 'request_id', 'unknown')
                }
            )

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
