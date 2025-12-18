"""
Prometheus Data Collector
Fetches metrics from Prometheus for ML training and inference
"""
from prometheus_api_client import PrometheusConnect
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger


class PrometheusDataCollector:
    """Collects time series data from Prometheus"""
    
    def __init__(self, config: dict):
        """Initialize Prometheus connection"""
        self.config = config
        self.prometheus_url = config.get('prometheus_url', 'http://prometheus:9090')
        self.prom = PrometheusConnect(url=self.prometheus_url, disable_ssl=True)
        logger.info(f"Connected to Prometheus at {self.prometheus_url}")
    
    def fetch_metric_data(self, metric_name: str, start_time: datetime, end_time: datetime, step: str = '1m') -> pd.DataFrame:
        """
        Fetch time series data for a specific metric
        
        Args:
            metric_name: Name of the Prometheus metric
            start_time: Start time for data retrieval
            end_time: End time for data retrieval
            step: Query resolution step (e.g., '1m', '5m', '1h')
        
        Returns:
            DataFrame with timestamp and value columns
        """
        try:
            logger.info(f"Fetching data for metric: {metric_name}")
            
            # Query Prometheus
            result = self.prom.custom_query_range(
                query=metric_name,
                start_time=start_time,
                end_time=end_time,
                step=step
            )
            
            if not result:
                logger.warning(f"No data returned for metric: {metric_name}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            data_points = []
            for metric_result in result:
                metric_labels = metric_result['metric']
                values = metric_result['values']
                
                for timestamp, value in values:
                    data_points.append({
                        'timestamp': datetime.fromtimestamp(float(timestamp)),
                        'value': float(value),
                        'labels': metric_labels
                    })
            
            df = pd.DataFrame(data_points)
            logger.info(f"Fetched {len(df)} data points for {metric_name}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching metric {metric_name}: {e}")
            return pd.DataFrame()
    
    def fetch_recent_metrics(self, lookback_minutes: int = 60) -> dict:
        """
        Fetch recent data for all configured metrics
        
        Args:
            lookback_minutes: How many minutes of data to fetch
        
        Returns:
            Dictionary mapping metric names to DataFrames
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=lookback_minutes)
        
        metrics_config = self.config.get('data_collection', {}).get('metrics', [])
        
        all_data = {}
        for metric_config in metrics_config:
            metric_name = metric_config['name']
            df = self.fetch_metric_data(metric_name, start_time, end_time)
            
            if not df.empty:
                all_data[metric_name] = df
        
        return all_data
    
    def fetch_training_data(self, metric_name: str, lookback_hours: int = None) -> pd.DataFrame:
        """
        Fetch historical data for model training
        
        Args:
            metric_name: Name of the metric
            lookback_hours: How many hours of historical data (default from config)
        
        Returns:
            DataFrame with training data
        """
        if lookback_hours is None:
            lookback_hours = self.config.get('data_collection', {}).get('lookback_hours', 168)
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=lookback_hours)
        
        logger.info(f"Fetching {lookback_hours} hours of training data for {metric_name}")
        
        return self.fetch_metric_data(metric_name, start_time, end_time, step='1m')
    
    def get_available_metrics(self) -> list:
        """Get list of all available metrics from Prometheus"""
        try:
            metrics = self.prom.all_metrics()
            logger.info(f"Found {len(metrics)} metrics in Prometheus")
            return metrics
        except Exception as e:
            logger.error(f"Error fetching available metrics: {e}")
            return []
