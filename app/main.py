from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
import logging
from app.config import settings
from app.database import init_db, close_db
from app.api.v1.router import api_router
from app.schemas.common import HealthResponse, MessageResponse
import os


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup
    logger.info("Starting up Property Listing Service...")
    # Note: Database tables are created via Alembic migrations
    # await init_db()  # Uncomment for development without Alembic
    logger.info("Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Property Listing Service...")
    await close_db()
    logger.info("Service stopped")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Property Listing Microservice for Rental Marketplace Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

origins = [
    "https://dev.eygar.com",
    "http://localhost:3000",  # optional for local dev
    "http://127.0.0.1:3000",
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if settings.ENVIRONMENT == "development":
    if os.path.exists("media"):
        app.mount("/media", StaticFiles(directory="media"), name="media")

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validation error"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        service=settings.APP_NAME,
        version="1.0.0"
    )


@app.get("/", response_model=MessageResponse, tags=["root"])
async def root():
    """
    Root endpoint with service information.
    """
    return MessageResponse(
        message=f"Welcome to {settings.APP_NAME}",
        detail=f"API documentation available at /docs"
    )


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
