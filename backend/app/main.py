"""Main FastAPI application."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.app import models  # noqa: F401 ensures models are registered
from backend.app.api import api_router, websockets
from backend.app.config import settings
from backend.app.database import Base, engine
from backend.app.middleware.analytics import AnalyticsMiddleware
from backend.app.middleware.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Creates database tables on startup.
    """
    Base.metadata.create_all(bind=engine)
    yield


# Ensure tables exist for contexts that bypass lifespan (e.g., some tests)
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add analytics middleware
app.add_middleware(AnalyticsMiddleware)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "AutoGen Agent Studio API", "version": settings.app_version}


# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Include WebSocket routes
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])


@app.get(f"{settings.api_v1_prefix}/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
