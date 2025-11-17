"""
Structured logging configuration using structlog
"""
import logging
import structlog
from typing import Any
import sys


def setup_logging(log_level: str = "INFO", json_logs: bool = True) -> None:
    """
    Setup structured logging with structlog
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Configure processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if json_logs:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console output for development
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> Any:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (defaults to calling module)
    
    Returns:
        structlog logger instance
    """
    return structlog.get_logger(name)


# Logging middleware for FastAPI
class LoggingMiddleware:
    """Middleware to log all requests and responses"""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("api")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        request_id = scope.get("headers", {}).get(b"x-request-id", b"").decode()
        
        # Log request
        self.logger.info(
            "request_started",
            method=scope["method"],
            path=scope["path"],
            request_id=request_id,
        )
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Log response
                self.logger.info(
                    "request_completed",
                    method=scope["method"],
                    path=scope["path"],
                    status_code=message["status"],
                    request_id=request_id,
                )
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            self.logger.error(
                "request_failed",
                method=scope["method"],
                path=scope["path"],
                error=str(e),
                request_id=request_id,
            )
            raise

