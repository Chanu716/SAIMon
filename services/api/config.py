"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "SAIMon"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Prometheus
    PROMETHEUS_URL: str = "http://prometheus:9090"
    PROMETHEUS_TIMEOUT: int = 30
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Database
    DATABASE_URL: str = "postgresql://saimon:saimon123@postgres:5432/saimon"
    
    # Grafana
    GRAFANA_URL: str = "http://grafana:3000"
    GRAFANA_USER: str = "admin"
    GRAFANA_PASSWORD: str = "admin"
    
    # ML Configuration
    ML_MODEL_PATH: str = "/app/models"
    ML_CONFIG_PATH: str = "/app/config/ml_config.yml"
    
    # Anomaly Detection
    ANOMALY_THRESHOLD: float = 0.7
    ANOMALY_WINDOW_SIZE: int = 60
    MIN_CONSECUTIVE_ANOMALIES: int = 3
    
    # Alerting
    ENABLE_ALERTING: bool = True
    ALERT_COOLDOWN_MINUTES: int = 15
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://grafana:3000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
