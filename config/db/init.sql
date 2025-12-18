-- SAIMon Database Initialization Script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Metrics table - stores metric metadata
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    metric_type VARCHAR(50) NOT NULL, -- counter, gauge, histogram, summary
    description TEXT,
    labels JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models table - stores ML model metadata
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    model_type VARCHAR(100) NOT NULL, -- isolation_forest, lstm, etc.
    metric_id UUID REFERENCES metrics(id),
    config JSONB,
    performance_metrics JSONB,
    file_path VARCHAR(500),
    is_active BOOLEAN DEFAULT false,
    trained_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, version)
);

-- Anomalies table - stores detected anomalies
CREATE TABLE IF NOT EXISTS anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_id UUID REFERENCES metrics(id),
    model_id UUID REFERENCES ml_models(id),
    timestamp TIMESTAMP NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    expected_value DOUBLE PRECISION,
    anomaly_score DOUBLE PRECISION NOT NULL,
    severity VARCHAR(50) NOT NULL, -- low, medium, high, critical
    labels JSONB,
    context JSONB, -- Renamed from metadata to avoid SQLAlchemy conflict
    is_confirmed BOOLEAN DEFAULT NULL, -- null=pending, true=confirmed, false=false_positive
    confirmed_by VARCHAR(255),
    confirmed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table - stores alert configurations and history
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_id UUID REFERENCES metrics(id),
    anomaly_id UUID REFERENCES anomalies(id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    channels VARCHAR(100)[], -- slack, email, webhook
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, failed, acknowledged
    sent_at TIMESTAMP,
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    context JSONB, -- Renamed from metadata to avoid SQLAlchemy conflict
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training jobs table - tracks model training jobs
CREATE TABLE IF NOT EXISTS training_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml_models(id),
    status VARCHAR(50) NOT NULL, -- queued, running, completed, failed
    metric_id UUID REFERENCES metrics(id),
    config JSONB,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    metrics JSONB, -- training metrics (accuracy, loss, etc.)
    error_message TEXT,
    logs TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model predictions table - stores predictions for monitoring
CREATE TABLE IF NOT EXISTS model_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml_models(id),
    metric_id UUID REFERENCES metrics(id),
    timestamp TIMESTAMP NOT NULL,
    actual_value DOUBLE PRECISION,
    predicted_value DOUBLE PRECISION NOT NULL,
    prediction_interval_lower DOUBLE PRECISION,
    prediction_interval_upper DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    is_anomaly BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User feedback table - for learning from user input
CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    anomaly_id UUID REFERENCES anomalies(id),
    user_id VARCHAR(255),
    feedback_type VARCHAR(50) NOT NULL, -- correct, false_positive, severity_change
    old_value VARCHAR(255),
    new_value VARCHAR(255),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System configuration table
CREATE TABLE IF NOT EXISTS system_config (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_by VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_metrics_name ON metrics(name);
CREATE INDEX idx_anomalies_timestamp ON anomalies(timestamp DESC);
CREATE INDEX idx_anomalies_metric_id ON anomalies(metric_id);
CREATE INDEX idx_anomalies_severity ON anomalies(severity);
CREATE INDEX idx_anomalies_created_at ON anomalies(created_at DESC);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX idx_ml_models_active ON ml_models(is_active);
CREATE INDEX idx_training_jobs_status ON training_jobs(status);
CREATE INDEX idx_predictions_timestamp ON model_predictions(timestamp DESC);

-- Create views for common queries
CREATE OR REPLACE VIEW v_active_models AS
SELECT 
    m.*,
    met.name as metric_name,
    met.metric_type
FROM ml_models m
LEFT JOIN metrics met ON m.metric_id = met.id
WHERE m.is_active = true;

CREATE OR REPLACE VIEW v_recent_anomalies AS
SELECT 
    a.*,
    m.name as metric_name,
    mod.name as model_name,
    mod.model_type
FROM anomalies a
LEFT JOIN metrics m ON a.metric_id = m.id
LEFT JOIN ml_models mod ON a.model_id = mod.id
WHERE a.created_at > NOW() - INTERVAL '24 hours'
ORDER BY a.created_at DESC;

CREATE OR REPLACE VIEW v_alert_summary AS
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    severity,
    status,
    COUNT(*) as alert_count
FROM alerts
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', created_at), severity, status
ORDER BY hour DESC;

-- Insert default configuration
INSERT INTO system_config (key, value, description) VALUES
('anomaly_detection', '{"enabled": true, "threshold": 0.7, "min_consecutive": 3}', 'Anomaly detection settings'),
('alerting', '{"enabled": true, "cooldown_minutes": 15, "channels": ["slack"]}', 'Alert configuration'),
('training', '{"auto_train": true, "schedule": "0 2 * * *", "retrain_interval_hours": 24}', 'Training configuration')
ON CONFLICT (key) DO NOTHING;

-- Create function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for metrics table
CREATE TRIGGER update_metrics_updated_at BEFORE UPDATE ON metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO saimon;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO saimon;
