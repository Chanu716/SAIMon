"""
Configuration loader for ML Engine
"""
import yaml
import os
from pathlib import Path


def load_config(config_path: str = None) -> dict:
    """Load ML configuration from YAML file"""
    if not config_path:
        config_path = os.getenv('ML_CONFIG_PATH', '/app/config/ml_config.yml')
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables if present
    config['prometheus_url'] = os.getenv('PROMETHEUS_URL', 'http://prometheus:9090')
    config['database_url'] = os.getenv('DATABASE_URL', 'postgresql://saimon:saimon123@postgres:5432/saimon')
    config['redis_url'] = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    config['model_path'] = os.getenv('ML_MODEL_PATH', '/app/models')
    
    return config
