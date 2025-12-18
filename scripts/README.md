# SAIMon Helper Scripts

This directory contains utility scripts for development and operations.

## Available Scripts

### 1. `start.sh` / `start.bat`
Start all SAIMon services

### 2. `stop.sh` / `stop.bat`
Stop all services gracefully

### 3. `logs.sh` / `logs.bat`
View logs from all or specific services

### 4. `test_setup.py`
Verify that the installation is working correctly

### 5. `generate_test_metrics.py`
Generate synthetic metrics with anomalies for testing

### 6. `train_models.py`
Manually trigger model training

### 7. `backup_db.sh`
Backup PostgreSQL database

## Usage Examples

```bash
# Start services
./scripts/start.sh

# View logs
./scripts/logs.sh saimon-api

# Run setup test
python scripts/test_setup.py

# Generate test data
python scripts/generate_test_metrics.py --duration 3600 --anomaly-rate 0.1
```
