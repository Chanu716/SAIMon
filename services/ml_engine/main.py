"""
SAIMon ML Engine - Main entry point
Handles model training, inference, and anomaly detection
"""
import time
import schedule
from loguru import logger
from config import load_config
from data_collector import PrometheusDataCollector
from anomaly_detector import AnomalyDetectorEngine

# Load configuration
config = load_config()

# Initialize components
data_collector = PrometheusDataCollector(config)
anomaly_detector = AnomalyDetectorEngine(config)

logger.info("SAIMon ML Engine starting...")


def train_models():
    """Scheduled model training job"""
    logger.info("Starting scheduled model training...")
    try:
        # This will be implemented in Phase 3
        anomaly_detector.train_all_models()
        logger.info("Model training completed successfully")
    except Exception as e:
        logger.error(f"Model training failed: {e}")


def run_inference():
    """Run anomaly detection on recent data"""
    logger.info("Running anomaly detection...")
    try:
        # Collect recent data
        data = data_collector.fetch_recent_metrics()
        
        # Detect anomalies
        anomalies = anomaly_detector.detect_anomalies(data)
        
        if anomalies:
            logger.info(f"Detected {len(anomalies)} anomalies")
            # Save anomalies to database
            anomaly_detector.save_anomalies(anomalies)
        
    except Exception as e:
        logger.error(f"Inference failed: {e}")


def main():
    """Main loop"""
    # Schedule training (e.g., daily at 2 AM)
    schedule.every().day.at("02:00").do(train_models)
    
    # Schedule inference (e.g., every 5 minutes)
    schedule.every(5).minutes.do(run_inference)
    
    logger.info("ML Engine is running. Press Ctrl+C to stop.")
    
    # Initial training on startup
    logger.info("Running initial model training...")
    train_models()
    
    # Run initial inference
    run_inference()
    
    # Main loop
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("ML Engine shutting down...")
    except Exception as e:
        logger.error(f"ML Engine error: {e}")
