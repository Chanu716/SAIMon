"""
Metrics management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import httpx

from database import get_db
from config import settings
import models as db_models

router = APIRouter()


@router.get("/metrics")
async def list_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all registered metrics"""
    metrics = db.query(db_models.Metric).offset(skip).limit(limit).all()
    total = db.query(db_models.Metric).count()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "metrics": metrics
    }


@router.get("/metrics/{metric_name}")
async def get_metric(metric_name: str, db: Session = Depends(get_db)):
    """Get specific metric details"""
    metric = db.query(db_models.Metric).filter(db_models.Metric.name == metric_name).first()
    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric {metric_name} not found")
    return metric


@router.get("/metrics/{metric_name}/data")
async def get_metric_data(
    metric_name: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    step: str = "1m"
):
    """Fetch time series data from Prometheus"""
    try:
        # Default time range: last 1 hour
        if not end:
            end = datetime.utcnow()
        else:
            end = datetime.fromisoformat(end)
        
        if not start:
            start = end - timedelta(hours=1)
        else:
            start = datetime.fromisoformat(start)
        
        # Query Prometheus
        async with httpx.AsyncClient() as client:
            params = {
                "query": metric_name,
                "start": start.timestamp(),
                "end": end.timestamp(),
                "step": step
            }
            response = await client.get(
                f"{settings.PROMETHEUS_URL}/api/v1/query_range",
                params=params,
                timeout=settings.PROMETHEUS_TIMEOUT
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch data from Prometheus"
                )
            
            data = response.json()
            return {
                "metric": metric_name,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "step": step,
                "data": data.get("data", {})
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/discover")
async def discover_metrics(db: Session = Depends(get_db)):
    """Auto-discover metrics from Prometheus"""
    try:
        async with httpx.AsyncClient() as client:
            # Get all metric names
            response = await client.get(
                f"{settings.PROMETHEUS_URL}/api/v1/label/__name__/values",
                timeout=settings.PROMETHEUS_TIMEOUT
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to discover metrics"
                )
            
            data = response.json()
            metric_names = data.get("data", [])
            
            # Register new metrics
            new_metrics = []
            for name in metric_names:
                existing = db.query(db_models.Metric).filter(
                    db_models.Metric.name == name
                ).first()
                
                if not existing:
                    metric = db_models.Metric(
                        name=name,
                        metric_type="unknown",
                        description=f"Auto-discovered metric: {name}"
                    )
                    db.add(metric)
                    new_metrics.append(name)
            
            db.commit()
            
            return {
                "total_discovered": len(metric_names),
                "new_metrics": len(new_metrics),
                "metrics": new_metrics
            }
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
