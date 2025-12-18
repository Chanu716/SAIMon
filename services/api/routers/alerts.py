"""
Alert management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
import models as db_models

router = APIRouter()


@router.get("/alerts")
async def list_alerts(
    status: Optional[str] = Query(None, regex="^(pending|sent|failed|acknowledged|resolved)$"),
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List alerts with filters"""
    query = db.query(db_models.Alert)
    
    if status:
        query = query.filter(db_models.Alert.status == status)
    
    if severity:
        query = query.filter(db_models.Alert.severity == severity)
    
    query = query.order_by(db_models.Alert.created_at.desc())
    
    total = query.count()
    alerts = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "alerts": alerts
    }


@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """Get specific alert details"""
    alert = db.query(db_models.Alert).filter(
        db_models.Alert.id == alert_id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    user: str = "system",
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    alert = db.query(db_models.Alert).filter(
        db_models.Alert.id == alert_id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "acknowledged"
    alert.acknowledged_by = user
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    return {
        "message": "Alert acknowledged",
        "alert_id": alert_id
    }


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    """Resolve an alert"""
    alert = db.query(db_models.Alert).filter(
        db_models.Alert.id == alert_id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    return {
        "message": "Alert resolved",
        "alert_id": alert_id
    }
