"""
FastAPI application with MCP integration
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

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


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A REST API for managing expenses with MCP integration",
    version=settings.app_version,
    lifespan=lifespan
)

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

# Root endpoint

# Convert FastAPI app to MCP server
mcp = FastMCP.from_fastapi(app=app)

# Add MCP Resource
