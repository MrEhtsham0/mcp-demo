"""
FastAPI application with MCP integration
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi_pagination import add_pagination
# from fastmcp import FastMCP

from config import settings
from app.core.database import init_db_async
from app.core.redis_cache import redis_cache
from app.routes.expenses import router as expenses_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    await init_db_async()
    await redis_cache.connect()
    yield
    # Shutdown
    await redis_cache.disconnect()


# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A REST API for managing expenses with MCP integration",
    version=settings.app_version,
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(expenses_router, prefix=settings.api_v1_str)

# Add pagination support
add_pagination(app)

# Root endpoint

# Convert FastAPI app to MCP server
# mcp = FastMCP.from_fastapi(app=app)

# Add MCP Resource

"""
1=>Caching using redis
2=>Rate limiting using slowapi
3=>Logging using logging
4=>Error handling using fastapi
5=>Authentication using fastapi
6=>Authorization using fastapi
7=>Database using sqlmodel
8=>Redis using aioredis
9=>MCP using fastmcp
"""
