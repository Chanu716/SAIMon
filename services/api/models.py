"""
Database models (SQLAlchemy ORM)
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ARRAY, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database import Base


class Metric(Base):
    """Metric metadata"""
    __tablename__ = "metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    metric_type = Column(String(50), nullable=False)
    description = Column(Text)
    labels = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    anomalies = relationship("Anomaly", back_populates="metric")
    models = relationship("MLModel", back_populates="metric")


class MLModel(Base):
    """ML model metadata"""
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(100), nullable=False)
    metric_id = Column(UUID(as_uuid=True), ForeignKey("metrics.id"))
    config = Column(JSON)
    performance_metrics = Column(JSON)
    file_path = Column(String(500))
    is_active = Column(Boolean, default=False, index=True)
    trained_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    metric = relationship("Metric", back_populates="models")
    anomalies = relationship("Anomaly", back_populates="model")


class Anomaly(Base):
    """Detected anomalies"""
    __tablename__ = "anomalies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_id = Column(UUID(as_uuid=True), ForeignKey("metrics.id"), index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_models.id"))
    timestamp = Column(DateTime, nullable=False, index=True)
    value = Column(Float, nullable=False)
    expected_value = Column(Float)
    anomaly_score = Column(Float, nullable=False)
    severity = Column(String(50), nullable=False, index=True)
    labels = Column(JSON)
    context = Column(JSON)  # Renamed from metadata to avoid SQLAlchemy conflict
    is_confirmed = Column(Boolean, default=None)
    confirmed_by = Column(String(255))
    confirmed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    metric = relationship("Metric", back_populates="anomalies")
    model = relationship("MLModel", back_populates="anomalies")
    alerts = relationship("Alert", back_populates="anomaly")


class Alert(Base):
    """Alert records"""
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_id = Column(UUID(as_uuid=True), ForeignKey("metrics.id"))
    anomaly_id = Column(UUID(as_uuid=True), ForeignKey("anomalies.id"))
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    channels = Column(ARRAY(String))
    status = Column(String(50), default="pending", index=True)
    sent_at = Column(DateTime)
    acknowledged_by = Column(String(255))
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    context = Column(JSON)  # Renamed from metadata to avoid SQLAlchemy conflict
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    anomaly = relationship("Anomaly", back_populates="alerts")


class TrainingJob(Base):
    """Model training job tracking"""
    __tablename__ = "training_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_models.id"))
    metric_id = Column(UUID(as_uuid=True), ForeignKey("metrics.id"))
    status = Column(String(50), nullable=False, index=True)
    config = Column(JSON)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    metrics = Column(JSON)
    error_message = Column(Text)
    logs = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
