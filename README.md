# SAIMon - Smart AI Monitoring System

<div align="center">

**An intelligent monitoring system that learns your infrastructure's behavior and detects anomalies automatically**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

*A collaborative project by [Chanu716](https://github.com/Chanu716) and [Charmi Seera](https://github.com/Charmiseera)*

</div>

---

## Why We Built This

Imagine your server's CPU usage gradually creeping from 60% to 75% over a week. Traditional monitoring? Silent. It's under the 80% threshold. But that subtle change might indicate a memory leak that'll crash your system next Tuesday.

Or picture this: Your API response times spike to 200ms during lunch hour - completely normal for your e-commerce site. But your static threshold triggers an alert anyway. After the third false alarm this week, you start ignoring notifications.

We built SAIMon because **monitoring shouldn't work this way**.

### The Core Idea

Instead of setting arbitrary thresholds, what if your monitoring system could *learn* what's normal for your infrastructure? What if it understood that 85% CPU during deployments is fine, but 60% at 3 AM is suspicious?

SAIMon observes your system's behavior over time and builds a baseline understanding. When metrics deviate from learned patterns - even within "acceptable" ranges - it flags them. You get context-aware alerts: what changed, by how much, and confidence scores.

No guessing thresholds. No alert fatigue. Just intelligent detection that adapts to your system's personality.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Your Infrastructure                           │
│                    (Servers, Databases, Services)                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │ System Metrics
                             ▼
                    ┌─────────────────┐
                    │   Prometheus    │ ◄─── Node Exporter
                    │ (Metrics Store) │      (Collects CPU, Memory, etc.)
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
      ┌──────────────────┐      ┌──────────────────┐
      │   ML Engine      │      │     Grafana      │
      │                  │      │  (Dashboards)    │
      │  • Z-Score       │      └──────────────────┘
      │  • Isolation     │
      │    Forest        │
      │  • Training      │
      │  • Detection     │
      └────────┬─────────┘
               │ Detected Anomalies
               ▼
      ┌──────────────────┐
      │   FastAPI        │
      │  (REST API)      │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │   PostgreSQL     │
      │  (Database)      │
      └──────────────────┘
```

**Components:**
- **Prometheus**: Collects and stores time-series metrics every 15 seconds
- **ML Engine**: Python service that trains models and detects anomalies
- **FastAPI**: REST API for querying anomalies and managing models
- **PostgreSQL**: Stores detected anomalies, model metadata, and metric information
- **Grafana**: Visualization dashboards and real-time monitoring
- **Redis**: Caching layer for performance optimization

---

## How It Works

### Detection Approach

We use two complementary techniques to catch different types of anomalies:

**Statistical Baseline (Z-Score)**: Calculates how far metrics deviate from historical averages. Great for catching sudden spikes or drops. If your CPU suddenly jumps to 95% when it normally hovers around 40%, the Z-score will be high.

**Pattern Recognition (Isolation Forest)**: Builds an ensemble of decision trees to identify unusual patterns. This catches subtle anomalies that pure statistics miss - like gradual degradation or unusual combinations of metrics.

Both run every 5 minutes on recent data. When either model flags something unusual, you get an anomaly record with severity scoring.

### Training Pipeline

Models retrain automatically every night using the past week's data. This keeps them current as your infrastructure evolves. New deployment increased baseline memory usage? The models adapt. Traffic patterns shifted? They learn the new normal.

Minimum requirement: 1000 data points per metric (about 4 hours at 15-second intervals). If you just added a new metric, SAIMon waits until there's enough history to train reliably.

### 2. Detection Phase

Every 5 minutes, SAIMon:
- Fetches the latest metrics from Prometheus
- Runs them through both models
- Calculates anomaly scores (0 to 1, where higher = more anomalous)
- Classifies severity (low/medium/high/critical)
- Stores everything in PostgreSQL for analysis

### What You Get

**Real-time Anomaly Detection**: Checks your metrics every 5 minutes, flags unusual patterns

**Automatic Learning**: Models retrain daily on the past week's data - no manual tuning needed

**Multiple Detection Methods**: Z-Score catches sudden changes, Isolation Forest finds subtle patterns

**Full History**: Every anomaly stored with context - what happened, expected vs actual values, confidence scores

**REST API**: Query anomalies programmatically, integrate with your existing tools

**Visual Dashboards**: Grafana integration for real-time monitoring and historical analysis

---

## What We've Achieved

Since deploying SAIMon on our infrastructure:

- **750+ anomalies detected** across CPU, memory, disk, and network metrics
- **2 models trained** and actively monitoring (statistical + ML-based)
- **6 different metrics** being tracked continuously
- **Sub-5-minute detection** from metric collection to alert
- **Zero manual threshold tuning** required

The system runs 24/7, automatically adapting as our infrastructure changes. We've caught several issues before they became user-facing - including a gradual memory leak that traditional monitoring completely missed.

---

## Technical Overview

### Built With

**Backend**: Python 3.11, FastAPI for REST API, SQLAlchemy ORM  
**ML Stack**: Scikit-learn (Isolation Forest), NumPy, Pandas, SciPy  
**Data Storage**: PostgreSQL (anomalies, models, metrics), Redis (caching)  
**Monitoring**: Prometheus (metric collection), Grafana (visualization)  
**Infrastructure**: Docker Compose (7 containerized services)  

### Architecture Highlights

**Microservices Design**: Each component (ML engine, API, database, monitoring) runs independently in Docker containers. Services communicate via HTTP APIs and database connections.

**Async Processing**: ML training runs on a schedule (nightly), while anomaly detection operates continuously every 5 minutes. This keeps the system responsive while maintaining up-to-date models.

**Time-Series Optimization**: PostgreSQL indexes on timestamp fields, Prometheus for efficient metric queries, Redis for caching frequently-accessed data.

---

## 🚀 Quick Start Guide

### **Prerequisites**
```bash
- Docker & Docker Compose (v20.10+)
- Python 3.11+
- Git
- 4GB+ RAM for all services
```

### **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/Chanu716/SAIMon.git
cd SAIMon
```

2. **Start all services** (7 containers)
```bash
docker-compose up -d
```

3. **Verify services are running**
```bash
docker-compose ps
# All 7 services should show "Up"
```

4. **Run setup validation**
```bash
pip install -r requirements.txt
python scripts/test_setup.py
# Expected: 5/5 tests passed ✅
```

### **Access the Application**

| Service | URL | Purpose |
|---------|-----|---------|
| **Prometheus** | http://localhost:9090 | Raw metrics & queries |
| **Grafana** | http://localhost:3000 | Visualization dashboards (admin/admin) |
| **SAIMon API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| **PostgreSQL** | localhost:5432 | Database (saimon/saimon) |

### **Quick API Examples**

```bash
# View detected anomalies
curl http://localhost:8000/api/v1/anomalies?limit=10

# Check trained ML models
curl http://localhost:8000/api/v1/models

# View system health
curl http://localhost:8000/health

# Get anomaly statistics
curl http://localhost:8000/api/v1/anomalies/stats
```

### **Grafana Setup** (First Time)

1. Open http://localhost:3000 (login: admin/admin)
2. Add Prometheus data source:
   - URL: `http://prometheus:9090`
   - Click "Save & Test"
3. Import Node Exporter dashboard:
   - Dashboard ID: **1860**
   - Select Prometheus as data source
4. Import SAIMon anomaly dashboard:
   - Upload `grafana/dashboards/saimon-anomalies.json`

---

## 📁 Project Structure

```
SAIMon/
├── services/
│   ├── api/                          # FastAPI REST API
│   │   ├── main.py                   # Application entry point
│   │   ├── models.py                 # SQLAlchemy ORM models
│   │   ├── database.py               # Database connection
│   │   ├── routers/                  # API endpoints
│   │   │   ├── anomalies.py          # GET/POST anomalies
│   │   │   ├── models.py             # ML model management
│   │   │   ├── metrics.py            # Metric queries
│   │   │   ├── alerts.py             # Alert configuration
│   │   │   └── health.py             # Health checks
│   │   └── requirements.txt          # Python dependencies
│   │
│   └── ml_engine/                    # Machine Learning Service
│       ├── main.py                   # Scheduling & orchestration
│       ├── anomaly_detector.py       # ML algorithms implementation
│       ├── data_collector.py         # Prometheus data fetching
│       ├── config.py                 # Configuration loader
│       └── requirements.txt          # ML dependencies
│
├── config/
│   ├── prometheus.yml                # Prometheus scrape config
│   ├── ml_config.yml                 # ML hyperparameters
│   ├── db/init.sql                   # Database schema
│   └── grafana/                      # Grafana provisioning
│
├── grafana/dashboards/               # Custom dashboards
│   └── saimon-anomalies.json         # ML anomaly dashboard
│
├── notebooks/                        # Jupyter notebooks
│   └── 01_anomaly_detection_experiments.ipynb
│
├── scripts/                          # Utility scripts
│   ├── test_setup.py                 # Validation script
│   └── generate_test_metrics.py      # Test data generator
│
├── docs/                             # Comprehensive documentation
│   ├── VIEWING_DATA.md               # Grafana & Prometheus guide
│   ├── COMPLETE_OVERVIEW.md          # System overview
│   ├── QUICKSTART.md                 # Quick setup guide
│   └── TROUBLESHOOTING.md            # Common issues
│
├── docker-compose.yml                # Multi-container orchestration
├── requirements.txt                  # Root Python dependencies
├── .gitignore                        # Git ignore patterns
└── README.md                         # This file
```

---

## Under the Hood

Want to see how it actually works? Here are some key pieces:

### Model Training

The Z-Score model is straightforward - calculate mean and standard deviation from historical data:

```python
def _train_zscore(self, metric_name: str, features: np.ndarray):
    mean = np.mean(features[:, 0])
    std = np.std(features[:, 0])
    threshold = 3.0  # 3 standard deviations = 99.7% of normal data
    
    model_data = {'mean': mean, 'std': std, 'threshold': threshold}
    self._save_model(metric_name, model_data)
```

Isolation Forest is more complex - it builds 100 decision trees and measures how quickly each point gets isolated:

```python
def _train_isolation_forest(self, metric_name: str, features: np.ndarray):
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    model = IsolationForest(
        contamination=0.1,      # Expect ~10% anomalies
        n_estimators=100,       # 100 trees in the forest
        max_samples=256         # Sample size per tree
    )
    model.fit(features_scaled)
```

### REST API

The API lets you query anomalies with filters and pagination:

```python
@router.get("/anomalies")
async def list_anomalies(
    severity: Optional[str] = None,
    metric_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Anomaly)
    if severity:
        query = query.filter(Anomaly.severity == severity)
    
    return query.offset(skip).limit(limit).all()
```

### Database Schema

Anomalies are stored with full context for later analysis:

```sql
CREATE TABLE anomalies (
    id UUID PRIMARY KEY,
    metric_id UUID REFERENCES metrics(id),
    timestamp TIMESTAMP NOT NULL,
    value DOUBLE PRECISION,
    expected_value DOUBLE PRECISION,
    anomaly_score DOUBLE PRECISION,
    severity VARCHAR(20),
    
    INDEX (timestamp DESC),  -- Fast time-range queries
    INDEX (metric_id),        -- Fast metric filtering
    INDEX (severity)          -- Fast severity filtering
);
```

All code is in the repo if you want to dig deeper!

---

## Testing

We included a validation script to verify everything's working:

```python
def test_api_health():
    """Make sure the API is up"""
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200

def test_models_trained():
    """Check that models exist and are accessible"""
    response = requests.get("http://localhost:8000/api/v1/models")
    data = response.json()
    assert data["total"] >= 2  # Should have Z-Score + Isolation Forest

def test_anomalies_detected():
    """Verify anomalies are being saved"""
    response = requests.get("http://localhost:8000/api/v1/anomalies?limit=1")
    data = response.json()
    assert data["total"] > 0
```

Run it: `python scripts/test_setup.py`

---

## Performance

Some numbers from our deployment:

- **Detection**: Less than 1 second from metric scrape to anomaly flag
- **Training**: About 30 seconds per metric (with 1000+ historical points)
- **API**: ~50ms average response time
- **Storage**: Growing at ~1MB/day (6 metrics + 750 anomalies)
- **Memory**: ML engine uses ~200MB RAM
- **Throughput**: Processing 5,760 data points per metric daily

---

## What's Next

We're exploring several directions to make SAIMon even more capable:

**Better Patterns**: LSTM autoencoders to catch time-based sequences (like "CPU always spikes 2 hours after deployment")

**Smarter Alerts**: Direct Slack/email integration so you get notified immediately, not just logged

**Multi-metric Correlation**: Detecting when CPU + memory + disk all trend weird simultaneously (current version checks metrics independently)

**Explainability**: Adding SHAP analysis so when an anomaly fires, you can see *which features* triggered it

**Seasonal Patterns**: Using Facebook Prophet for systems with daily/weekly cycles (like e-commerce traffic)

If you're interested in contributing to any of these, we'd love the help!

---

## 📚 Documentation

Comprehensive guides available in `docs/`:
- **[VIEWING_DATA.md](docs/VIEWING_DATA.md)**: Complete Grafana & Prometheus tutorial
- **[COMPLETE_OVERVIEW.md](docs/COMPLETE_OVERVIEW.md)**: System architecture deep dive
- **[QUICKSTART.md](docs/QUICKSTART.md)**: 5-minute setup guide
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**: Common issues & solutions

---

## 🤝 Contributing

We welcome contributions! Whether you're interested in:
- 🐛 **Bug fixes**: Improve stability and error handling
- ✨ **New features**: Add algorithms, metrics, or integrations
- 📖 **Documentation**: Enhance guides or add tutorials
- 🧪 **Testing**: Expand test coverage or add benchmarks

**Collaboration Process:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 The Team

Built collaboratively by **[Chanu716](https://github.com/Chanu716)** and **[Charmi Seera](https://github.com/Charmiseera)**.

We started this project to solve a real problem with traditional monitoring systems. Along the way, we learned a lot about time-series analysis, ensemble methods, and building production ML systems. If you're working on similar problems or want to discuss the approach, feel free to reach out!

---

<div align="center">

### **⭐ If you find this useful, please star the repository! ⭐**

Questions? Open an issue or start a discussion.

Built with ❤️ for better infrastructure monitoring

</div>
