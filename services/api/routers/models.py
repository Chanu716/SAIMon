"""
ML model management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from database import get_db
import models as db_models

router = APIRouter()


class ModelCreate(BaseModel):
    """Schema for creating a new model"""
    name: str
    version: str
    model_type: str
    metric_id: Optional[UUID] = None
    config: Optional[dict] = None
    performance_metrics: Optional[dict] = None
    file_path: Optional[str] = None
    is_active: bool = False
    trained_at: Optional[datetime] = None


@router.get("/models")
async def list_models(
    active_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all ML models"""
    query = db.query(db_models.MLModel)
    
    if active_only:
        query = query.filter(db_models.MLModel.is_active == True)
    
    total = query.count()
    models = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "models": models
    }


@router.post("/models")
async def create_model(model: ModelCreate, db: Session = Depends(get_db)):
    """Create a new ML model record"""
    try:
        # Check if metric exists if metric_id is provided
        if model.metric_id:
            metric = db.query(db_models.Metric).filter(
                db_models.Metric.id == model.metric_id
            ).first()
            if not metric:
                raise HTTPException(status_code=404, detail=f"Metric with id {model.metric_id} not found")
        
        # Create model record
        db_model = db_models.MLModel(
            name=model.name,
            version=model.version,
            model_type=model.model_type,
            metric_id=model.metric_id,
            config=model.config,
            performance_metrics=model.performance_metrics,
            file_path=model.file_path,
            is_active=model.is_active,
            trained_at=model.trained_at or datetime.utcnow()
        )
        
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        
        return {
            "message": "Model created successfully",
            "model_id": str(db_model.id),
            "model": db_model
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating model: {str(e)}")



@router.get("/models/{model_id}")
async def get_model(model_id: str, db: Session = Depends(get_db)):
    """Get specific model details"""
    model = db.query(db_models.MLModel).filter(
        db_models.MLModel.id == model_id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return model


@router.post("/models/{model_id}/activate")
async def activate_model(model_id: str, db: Session = Depends(get_db)):
    """Activate a model (deactivate others for the same metric)"""
    model = db.query(db_models.MLModel).filter(
        db_models.MLModel.id == model_id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Deactivate other models for the same metric
    if model.metric_id:
        db.query(db_models.MLModel).filter(
            db_models.MLModel.metric_id == model.metric_id,
            db_models.MLModel.id != model_id
        ).update({"is_active": False})
    
    # Activate this model
    model.is_active = True
    db.commit()
    db.refresh(model)
    
    return {
        "message": "Model activated successfully",
        "model_id": model_id
    }


@router.get("/training-jobs")
async def list_training_jobs(
    status: Optional[str] = Query(None, regex="^(queued|running|completed|failed)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List training jobs"""
    query = db.query(db_models.TrainingJob)
    
    if status:
        query = query.filter(db_models.TrainingJob.status == status)
    
    query = query.order_by(db_models.TrainingJob.created_at.desc())
    
    total = query.count()
    jobs = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "jobs": jobs
    }


@router.get("/training-jobs/{job_id}")
async def get_training_job(job_id: str, db: Session = Depends(get_db)):
    """Get training job details"""
    job = db.query(db_models.TrainingJob).filter(
        db_models.TrainingJob.id == job_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    return job
