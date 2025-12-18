"""
Anomaly Detection Engine
Implements multiple ML algorithms for anomaly detection
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
from scipy import stats
import joblib
from pathlib import Path
from datetime import datetime
from loguru import logger


class AnomalyDetectorEngine:
    """Main anomaly detection engine with multiple algorithms"""
    
    def __init__(self, config: dict):
        """Initialize the anomaly detector"""
        self.config = config
        self.models = {}
        self.scalers = {}
        self.model_path = Path(config.get('model_path', '/app/models'))
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.anomaly_config = config.get('anomaly_detection', {})
        self.threshold = self.anomaly_config.get('threshold', 0.7)
        self.window_size = self.anomaly_config.get('window_size', 60)
        self.min_consecutive = self.anomaly_config.get('min_consecutive', 3)
        
        logger.info("Anomaly Detector Engine initialized")
    
    def train_all_models(self):
        """Train models for all configured metrics"""
        logger.info("Training models for all metrics...")
        
        from data_collector import PrometheusDataCollector
        collector = PrometheusDataCollector(self.config)
        
        metrics_config = self.config.get('data_collection', {}).get('metrics', [])
        
        for metric_config in metrics_config:
            metric_name = metric_config['name']
            try:
                # Fetch training data
                data = collector.fetch_training_data(metric_name)
                
                if len(data) < self.config.get('data_collection', {}).get('min_data_points', 1000):
                    logger.warning(f"Insufficient data for {metric_name}, skipping training")
                    continue
                
                # Train models
                self.train_metric_models(metric_name, data)
                
            except Exception as e:
                logger.error(f"Error training models for {metric_name}: {e}")
    
    def train_metric_models(self, metric_name: str, data: pd.DataFrame):
        """
        Train anomaly detection models for a specific metric
        
        Args:
            metric_name: Name of the metric
            data: DataFrame with timestamp and value columns
        """
        logger.info(f"Training models for metric: {metric_name}")
        
        # Prepare features
        features = self._prepare_features(data)
        
        if features is None or len(features) == 0:
            logger.warning(f"No features available for {metric_name}")
            return
        
        # Get enabled models from config
        models_config = self.config.get('models', {})
        
        # Train Statistical Models
        if models_config.get('statistical', {}).get('zscore', {}).get('enabled', True):
            self._train_zscore(metric_name, features)
        
        # Train Unsupervised ML Models
        if models_config.get('unsupervised', {}).get('isolation_forest', {}).get('enabled', True):
            self._train_isolation_forest(metric_name, features)
        
        if models_config.get('unsupervised', {}).get('one_class_svm', {}).get('enabled', False):
            self._train_one_class_svm(metric_name, features)
        
        logger.info(f"Completed training for {metric_name}")
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features from raw time series data"""
        if data.empty or 'value' not in data.columns:
            return None
        
        values = data['value'].values
        
        # Feature engineering: rolling statistics
        feature_config = self.config.get('feature_engineering', {})
        rolling_windows = feature_config.get('rolling_windows', [5, 10, 30])
        
        features_list = [values]
        
        for window in rolling_windows:
            if len(values) > window:
                rolling_mean = pd.Series(values).rolling(window=window, min_periods=1).mean().values
                rolling_std = pd.Series(values).rolling(window=window, min_periods=1).std().fillna(0).values
                features_list.extend([rolling_mean, rolling_std])
        
        # Stack features
        features = np.column_stack(features_list)
        
        return features
    
    def _train_zscore(self, metric_name: str, features: np.ndarray):
        """Train Z-Score based anomaly detection"""
        try:
            config = self.config.get('models', {}).get('statistical', {}).get('zscore', {})
            threshold = config.get('threshold', 3.0)
            
            # Calculate mean and std
            mean = np.mean(features[:, 0])
            std = np.std(features[:, 0])
            
            model_data = {
                'type': 'zscore',
                'mean': float(mean),
                'std': float(std),
                'threshold': threshold
            }
            
            # Save model
            model_key = f"{metric_name}_zscore"
            self.models[model_key] = model_data
            self._save_model(model_key, model_data)
            
            logger.info(f"Trained Z-Score model for {metric_name}")
            
        except Exception as e:
            logger.error(f"Error training Z-Score for {metric_name}: {e}")
    
    def _train_isolation_forest(self, metric_name: str, features: np.ndarray):
        """Train Isolation Forest model"""
        try:
            config = self.config.get('models', {}).get('unsupervised', {}).get('isolation_forest', {})
            
            # Scale features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Train model
            model = IsolationForest(
                contamination=config.get('contamination', 0.1),
                n_estimators=config.get('n_estimators', 100),
                max_samples=config.get('max_samples', 256),
                random_state=config.get('random_state', 42)
            )
            
            model.fit(features_scaled)
            
            # Save model and scaler
            model_key = f"{metric_name}_isolation_forest"
            self.models[model_key] = model
            self.scalers[model_key] = scaler
            
            self._save_model(model_key, {'model': model, 'scaler': scaler})
            
            logger.info(f"Trained Isolation Forest for {metric_name}")
            
        except Exception as e:
            logger.error(f"Error training Isolation Forest for {metric_name}: {e}")
    
    def _train_one_class_svm(self, metric_name: str, features: np.ndarray):
        """Train One-Class SVM model"""
        try:
            config = self.config.get('models', {}).get('unsupervised', {}).get('one_class_svm', {})
            
            # Scale features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Train model
            model = OneClassSVM(
                kernel=config.get('kernel', 'rbf'),
                gamma=config.get('gamma', 'auto'),
                nu=config.get('nu', 0.1)
            )
            
            model.fit(features_scaled)
            
            # Save model and scaler
            model_key = f"{metric_name}_one_class_svm"
            self.models[model_key] = model
            self.scalers[model_key] = scaler
            
            self._save_model(model_key, {'model': model, 'scaler': scaler})
            
            logger.info(f"Trained One-Class SVM for {metric_name}")
            
        except Exception as e:
            logger.error(f"Error training One-Class SVM for {metric_name}: {e}")
    
    def detect_anomalies(self, metrics_data: dict) -> list:
        """
        Detect anomalies in metrics data
        
        Args:
            metrics_data: Dictionary mapping metric names to DataFrames
        
        Returns:
            List of detected anomalies
        """
        all_anomalies = []
        
        for metric_name, data in metrics_data.items():
            try:
                anomalies = self._detect_metric_anomalies(metric_name, data)
                all_anomalies.extend(anomalies)
            except Exception as e:
                logger.error(f"Error detecting anomalies for {metric_name}: {e}")
        
        return all_anomalies
    
    def _detect_metric_anomalies(self, metric_name: str, data: pd.DataFrame) -> list:
        """Detect anomalies for a specific metric"""
        if data.empty:
            return []
        
        # Prepare features
        features = self._prepare_features(data)
        if features is None:
            return []
        
        anomalies = []
        
        # Try each available model
        models_to_try = [
            (f"{metric_name}_zscore", self._predict_zscore),
            (f"{metric_name}_isolation_forest", self._predict_isolation_forest),
            (f"{metric_name}_one_class_svm", self._predict_one_class_svm)
        ]
        
        for model_key, predict_func in models_to_try:
            if model_key in self.models:
                try:
                    scores = predict_func(model_key, features)
                    
                    # Find anomalies above threshold
                    for idx, score in enumerate(scores):
                        if score > self.threshold:
                            severity = self._calculate_severity(score)
                            
                            anomaly = {
                                'metric_name': metric_name,
                                'timestamp': data.iloc[idx]['timestamp'],
                                'value': float(data.iloc[idx]['value']),
                                'anomaly_score': float(score),
                                'severity': severity,
                                'model_type': model_key.split('_')[-1],
                                'detected_at': datetime.utcnow()
                            }
                            anomalies.append(anomaly)
                            
                except Exception as e:
                    logger.error(f"Error predicting with {model_key}: {e}")
        
        return anomalies
    
    def _predict_zscore(self, model_key: str, features: np.ndarray) -> np.ndarray:
        """Predict anomalies using Z-Score"""
        model_data = self.models[model_key]
        values = features[:, 0]
        
        z_scores = np.abs((values - model_data['mean']) / (model_data['std'] + 1e-10))
        
        # Normalize to 0-1 range
        normalized_scores = z_scores / model_data['threshold']
        return np.clip(normalized_scores, 0, 1)
    
    def _predict_isolation_forest(self, model_key: str, features: np.ndarray) -> np.ndarray:
        """Predict anomalies using Isolation Forest"""
        model = self.models[model_key]
        scaler = self.scalers[model_key]
        
        features_scaled = scaler.transform(features)
        
        # Get anomaly scores (negative scores are more anomalous)
        scores = model.decision_function(features_scaled)
        
        # Convert to 0-1 range (higher is more anomalous)
        normalized_scores = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        
        return normalized_scores
    
    def _predict_one_class_svm(self, model_key: str, features: np.ndarray) -> np.ndarray:
        """Predict anomalies using One-Class SVM"""
        model = self.models[model_key]
        scaler = self.scalers[model_key]
        
        features_scaled = scaler.transform(features)
        
        # Get anomaly scores
        scores = model.decision_function(features_scaled)
        
        # Convert to 0-1 range
        normalized_scores = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        
        return normalized_scores
    
    def _calculate_severity(self, score: float) -> str:
        """Calculate severity level based on anomaly score"""
        severity_levels = self.anomaly_config.get('severity_levels', {})
        
        if score >= severity_levels.get('critical', 0.99):
            return 'critical'
        elif score >= severity_levels.get('high', 0.95):
            return 'high'
        elif score >= severity_levels.get('medium', 0.85):
            return 'medium'
        else:
            return 'low'
    
    def save_anomalies(self, anomalies: list):
        """Save detected anomalies to database"""
        if not anomalies:
            return
            
        logger.info(f"Saving {len(anomalies)} anomalies to database")
        
        import httpx
        from datetime import datetime
        
        for anomaly in anomalies:
            logger.info(
                f"Anomaly detected: {anomaly['metric_name']} "
                f"at {anomaly['timestamp']} "
                f"(score: {anomaly['anomaly_score']:.3f}, severity: {anomaly['severity']})"
            )
            
            # Prepare anomaly data for API
            anomaly_data = {
                "metric_name": anomaly['metric_name'],
                "timestamp": anomaly['timestamp'].isoformat() if isinstance(anomaly['timestamp'], datetime) else str(anomaly['timestamp']),
                "value": float(anomaly['value']),
                "expected_value": float(anomaly.get('expected_value', 0)),
                "anomaly_score": float(anomaly['anomaly_score']),
                "severity": anomaly['severity'],
                "algorithm": anomaly.get('algorithm', 'unknown'),
                "labels": anomaly.get('labels', {})
            }
            
            # Send to API
            try:
                api_url = self.config.get('api', {}).get('url', 'http://saimon-api:8000')
                response = httpx.post(
                    f"{api_url}/api/v1/anomalies",
                    json=anomaly_data,
                    timeout=5.0
                )
                if response.status_code not in [200, 201]:
                    logger.warning(f"Failed to save anomaly: HTTP {response.status_code}")
            except Exception as e:
                logger.error(f"Error saving anomaly to API: {e}")
    
    def _save_model(self, model_key: str, model_data):
        """Save model to disk and register in database"""
        try:
            # Save to disk
            model_file = self.model_path / f"{model_key}.pkl"
            joblib.dump(model_data, model_file)
            logger.info(f"Saved model to disk: {model_key}")
            
            # Register in database via API
            self._register_model_in_db(model_key, str(model_file), model_data)
            
        except Exception as e:
            logger.error(f"Error saving model {model_key}: {e}")
    
    def _register_model_in_db(self, model_key: str, file_path: str, model_data):
        """Register trained model in database via API"""
        import httpx
        from datetime import datetime
        
        try:
            # Parse model key: "{metric_name}_{model_type}"
            # Known model types: zscore, isolation_forest, one_class_svm
            model_type = None
            metric_name = None
            
            if model_key.endswith('_zscore'):
                model_type = 'zscore'
                metric_name = model_key[:-len('_zscore')]
            elif model_key.endswith('_isolation_forest'):
                model_type = 'isolation_forest'
                metric_name = model_key[:-len('_isolation_forest')]
            elif model_key.endswith('_one_class_svm'):
                model_type = 'one_class_svm'
                metric_name = model_key[:-len('_one_class_svm')]
            else:
                logger.warning(f"Unknown model key format: {model_key}")
                return
            
            # Get metric_id from API
            metric_id = None
            try:
                with httpx.Client(timeout=30.0) as client:
                    response = client.get(f"http://saimon-api:8000/api/v1/metrics/{metric_name}")
                    if response.status_code == 200:
                        metric_info = response.json()
                        metric_id = metric_info.get("id")
                        logger.info(f"Found metric_id: {metric_id} for metric: {metric_name}")
                    else:
                        logger.warning(f"Metric {metric_name} not found in database, will create model without metric_id")
            except Exception as e:
                logger.warning(f"Error fetching metric {metric_name}: {e}")
            
            # Prepare model config based on type
            config = {}
            performance_metrics = {}
            
            if model_type == "zscore" and isinstance(model_data, dict):
                config = {
                    "mean": model_data.get("mean"),
                    "std": model_data.get("std"),
                    "threshold": model_data.get("threshold")
                }
            elif model_type in ["isolation_forest", "one_class_svm"]:
                # For ML models, store basic info
                config = {
                    "model_type": model_type,
                    "trained_at": datetime.utcnow().isoformat()
                }
            
            # Create model record via API
            payload = {
                "name": metric_name,
                "version": f"1.0-{model_type}",  # Make version unique per model type
                "model_type": model_type,
                "metric_id": metric_id,
                "config": config,
                "performance_metrics": performance_metrics,
                "file_path": file_path,
                "is_active": True,
                "trained_at": datetime.utcnow().isoformat()
            }
            
            api_url = "http://saimon-api:8000/api/v1/models"
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(api_url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Registered model in database: {model_key}, ID: {result.get('model_id')}")
                else:
                    logger.error(f"Failed to register model in database: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error registering model {model_key} in database: {e}")

    
    def _load_model(self, model_key: str):
        """Load model from disk"""
        try:
            model_file = self.model_path / f"{model_key}.pkl"
            if model_file.exists():
                return joblib.load(model_file)
            return None
        except Exception as e:
            logger.error(f"Error loading model {model_key}: {e}")
            return None
