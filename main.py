"""
FastAPI application with MCP integration
"""

import tomllib
import uvicorn
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from fastapi_pagination import add_pagination

from config import settings
from app.db.database import init_db_async
from app.db.redis_cache import redis_cache
from app.routes.expenses import router as expenses_router


# -------------------------------------------------------------------
# Lifespan events
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""

    # Initialize database
    await init_db_async()
    
    # Connect to Redis
    await redis_cache.connect()
    
    yield
    
    # Shutdown
    await redis_cache.disconnect()


# -------------------------------------------------------------------
# Rate limiter
# -------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

# -------------------------------------------------------------------
# FastAPI App
# -------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    description="A REST API for managing expenses with MCP integration and observability",
    version=settings.app_version,
    lifespan=lifespan
)

# Add rate limiting handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(expenses_router, prefix=settings.api_v1_str)

# Add Pagination
add_pagination(app)


# -------------------------------------------------------------------
# Read PyProject Settings + Run Uvicorn
# -------------------------------------------------------------------
if __name__ == "__main__":
    config = tomllib.loads(Path("pyproject.toml").read_text())
    fastapi_config = config["tool"]["fastapi"]

    uvicorn.run(
        fastapi_config["entrypoint"],
        host=fastapi_config.get("host", "127.0.0.1"),
        port=fastapi_config.get("port", 8001),
        reload=fastapi_config.get("reload", False),
        workers=fastapi_config.get("workers", 2),
    )
