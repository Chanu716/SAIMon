"""
SAIMon API - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
import logging

from config import settings
from routers import health, metrics, anomalies, models, alerts
from database import engine, Base

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'saimon_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'saimon_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting SAIMon API...")
    
    # Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("SAIMon API started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SAIMon API...")


# Create FastAPI app
app = FastAPI(
    title="SAIMon API",
    description="Smart AI Monitoring - Intelligent anomaly detection for infrastructure",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(metrics.router, prefix="/api/v1", tags=["Metrics"])
app.include_router(anomalies.router, prefix="/api/v1", tags=["Anomalies"])
app.include_router(models.router, prefix="/api/v1", tags=["Models"])
app.include_router(alerts.router, prefix="/api/v1", tags=["Alerts"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SAIMon API",
        "version": "1.0.0",
        "description": "Smart AI Monitoring System",
        "docs": "/docs"
    }


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
