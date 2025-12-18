"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import httpx

from database import get_db
from config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "SAIMon API"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check including dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "SAIMon API",
        "dependencies": {}
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["dependencies"]["database"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Prometheus
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.PROMETHEUS_URL}/api/v1/status/config", timeout=5)
            if response.status_code == 200:
                health_status["dependencies"]["prometheus"] = "healthy"
            else:
                health_status["dependencies"]["prometheus"] = f"unhealthy: status {response.status_code}"
                health_status["status"] = "degraded"
    except Exception as e:
        health_status["dependencies"]["prometheus"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis (optional - implement if needed)
    # health_status["dependencies"]["redis"] = "healthy"
    
    return health_status
