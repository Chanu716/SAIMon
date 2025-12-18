"""
Anomaly detection endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid

from database import get_db
import models as db_models

router = APIRouter()


class AnomalyCreate(BaseModel):
    """Schema for creating an anomaly"""
    metric_name: str
    timestamp: str
    value: float
    expected_value: float = 0.0
    anomaly_score: float
    severity: str
    algorithm: str = "unknown"
    labels: Dict = {}


@router.post("/anomalies")
async def create_anomaly(
    anomaly: AnomalyCreate,
    db: Session = Depends(get_db)
):
    """Create a new anomaly record"""
    # Get or create metric
    metric = db.query(db_models.Metric).filter(
        db_models.Metric.name == anomaly.metric_name
    ).first()
    
    if not metric:
        metric = db_models.Metric(
            id=uuid.uuid4(),
            name=anomaly.metric_name,
            metric_type="system",
            labels=anomaly.labels
        )
        db.add(metric)
        db.flush()
    
    # Create anomaly
    db_anomaly = db_models.Anomaly(
        id=uuid.uuid4(),
        metric_id=metric.id,
        timestamp=datetime.fromisoformat(anomaly.timestamp) if isinstance(anomaly.timestamp, str) else anomaly.timestamp,
        value=anomaly.value,
        expected_value=anomaly.expected_value,
        anomaly_score=anomaly.anomaly_score,
        severity=anomaly.severity,
        labels=anomaly.labels
    )
    
    db.add(db_anomaly)
    db.commit()
    db.refresh(db_anomaly)
    
    return {
        "message": "Anomaly created successfully",
        "anomaly_id": str(db_anomaly.id)
    }


@router.get("/anomalies")
async def list_anomalies(
    metric_name: Optional[str] = None,
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List detected anomalies with filters"""
    query = db.query(db_models.Anomaly)
    
    # Apply filters
    if metric_name:
        metric = db.query(db_models.Metric).filter(
            db_models.Metric.name == metric_name
        ).first()
        if metric:
            query = query.filter(db_models.Anomaly.metric_id == metric.id)
    
    if severity:
        query = query.filter(db_models.Anomaly.severity == severity)
    
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(db_models.Anomaly.timestamp >= start)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(db_models.Anomaly.timestamp <= end)
    
    # Order by timestamp descending
    query = query.order_by(db_models.Anomaly.timestamp.desc())
    
    total = query.count()
    anomalies = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "anomalies": anomalies
    }


@router.get("/anomalies/{anomaly_id}")
async def get_anomaly(anomaly_id: str, db: Session = Depends(get_db)):
    """Get specific anomaly details"""
    anomaly = db.query(db_models.Anomaly).filter(
        db_models.Anomaly.id == anomaly_id
    ).first()
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    return anomaly


@router.post("/anomalies/{anomaly_id}/confirm")
async def confirm_anomaly(
    anomaly_id: str,
    confirmed: bool,
    user: str = "system",
    db: Session = Depends(get_db)
):
    """Confirm or reject an anomaly (user feedback)"""
    anomaly = db.query(db_models.Anomaly).filter(
        db_models.Anomaly.id == anomaly_id
    ).first()
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    anomaly.is_confirmed = confirmed
    anomaly.confirmed_by = user
    anomaly.confirmed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(anomaly)
    
    return {
        "message": "Anomaly confirmation updated",
        "anomaly_id": anomaly_id,
        "is_confirmed": confirmed
    }


@router.get("/anomalies/stats/summary")
async def get_anomaly_stats(
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db)
):
    """Get anomaly statistics summary"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Total anomalies
    total = db.query(db_models.Anomaly).filter(
        db_models.Anomaly.timestamp >= start_time
    ).count()
    
    # By severity
    severities = {}
    for severity in ['low', 'medium', 'high', 'critical']:
        count = db.query(db_models.Anomaly).filter(
            db_models.Anomaly.timestamp >= start_time,
            db_models.Anomaly.severity == severity
        ).count()
        severities[severity] = count
    
    # Confirmation stats
    confirmed = db.query(db_models.Anomaly).filter(
        db_models.Anomaly.timestamp >= start_time,
        db_models.Anomaly.is_confirmed == True
    ).count()
    
    false_positives = db.query(db_models.Anomaly).filter(
        db_models.Anomaly.timestamp >= start_time,
        db_models.Anomaly.is_confirmed == False
    ).count()
    
    return {
        "time_range_hours": hours,
        "total_anomalies": total,
        "by_severity": severities,
        "confirmed": confirmed,
        "false_positives": false_positives,
        "pending_review": total - confirmed - false_positives
    }
