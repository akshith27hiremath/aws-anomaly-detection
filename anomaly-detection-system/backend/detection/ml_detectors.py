"""
Machine Learning-based anomaly detection algorithms.
Implements Isolation Forest and Local Outlier Factor.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from backend.utils.config import get_detection_config
from backend.utils.helpers import calculate_confidence

logger = logging.getLogger(__name__)


class IsolationForestDetector:
    """
    Anomaly detection using Isolation Forest algorithm.
    Effective for high-dimensional data and doesn't assume data distribution.
    """

    def __init__(
        self,
        contamination: float = 0.1,
        n_estimators: int = 100,
        max_samples: int = 256
    ):
        """
        Initialize Isolation Forest detector.

        Args:
            contamination: Expected proportion of outliers
            n_estimators: Number of base estimators
            max_samples: Number of samples to draw for each tree
        """
        self.config = get_detection_config()

        # Load from config if available
        params = self.config.get_detection_params('isolation_forest')
        if params:
            contamination = params.get('contamination', contamination)
            n_estimators = params.get('n_estimators', n_estimators)
            max_samples = params.get('max_samples', max_samples)

        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            max_samples=max_samples,
            random_state=42,
            n_jobs=-1
        )
        self.is_fitted = False

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None,
        features: Optional[np.ndarray] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using Isolation Forest.

        Args:
            values: List of values (used for 1D detection)
            timestamps: Optional timestamps
            features: Optional multi-dimensional feature matrix

        Returns:
            List of detected anomalies
        """
        if len(values) < 10:
            logger.warning("Insufficient data for Isolation Forest")
            return []

        # Prepare data
        if features is not None:
            X = features
        else:
            X = np.array(values).reshape(-1, 1)

        # Fit and predict
        try:
            predictions = self.model.fit_predict(X)
            scores = self.model.score_samples(X)
            self.is_fitted = True

            # Find anomalies (predictions == -1)
            anomalies = []
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:
                    # Convert anomaly score to confidence
                    # Scores are negative, more negative = more anomalous
                    normalized_score = abs(score)
                    confidence = min(normalized_score * 2, 1.0)

                    anomaly = {
                        'index': i,
                        'value': float(values[i]),
                        'anomaly_score': float(score),
                        'confidence': float(confidence),
                        'method': 'isolation_forest'
                    }

                    if timestamps and i < len(timestamps):
                        anomaly['timestamp'] = timestamps[i]

                    anomalies.append(anomaly)

            return anomalies

        except Exception as e:
            logger.error(f"Error in Isolation Forest detection: {e}")
            return []

    def predict(
        self,
        values: List[float],
        features: Optional[np.ndarray] = None
    ) -> List[Dict[str, Any]]:
        """
        Predict anomalies on new data using fitted model.

        Args:
            values: List of values
            features: Optional feature matrix

        Returns:
            List of detected anomalies
        """
        if not self.is_fitted:
            logger.warning("Model not fitted, using fit_predict instead")
            return self.detect(values, features=features)

        if features is not None:
            X = features
        else:
            X = np.array(values).reshape(-1, 1)

        try:
            predictions = self.model.predict(X)
            scores = self.model.score_samples(X)

            anomalies = []
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:
                    normalized_score = abs(score)
                    confidence = min(normalized_score * 2, 1.0)

                    anomalies.append({
                        'index': i,
                        'value': float(values[i]),
                        'anomaly_score': float(score),
                        'confidence': float(confidence),
                        'method': 'isolation_forest'
                    })

            return anomalies

        except Exception as e:
            logger.error(f"Error in Isolation Forest prediction: {e}")
            return []


class LOFDetector:
    """
    Local Outlier Factor detector.
    Identifies outliers based on local density deviation.
    """

    def __init__(
        self,
        n_neighbors: int = 20,
        contamination: float = 0.1
    ):
        """
        Initialize LOF detector.

        Args:
            n_neighbors: Number of neighbors for density estimation
            contamination: Expected proportion of outliers
        """
        self.config = get_detection_config()

        # Load from config
        params = self.config.get_detection_params('local_outlier_factor')
        if params:
            n_neighbors = params.get('n_neighbors', n_neighbors)
            contamination = params.get('contamination', contamination)

        self.n_neighbors = n_neighbors
        self.contamination = contamination
        self.model = LocalOutlierFactor(
            n_neighbors=n_neighbors,
            contamination=contamination,
            novelty=False
        )

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None,
        features: Optional[np.ndarray] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using LOF.

        Args:
            values: List of values
            timestamps: Optional timestamps
            features: Optional feature matrix

        Returns:
            List of detected anomalies
        """
        if len(values) < self.n_neighbors + 1:
            logger.warning("Insufficient data for LOF")
            return []

        # Prepare data
        if features is not None:
            X = features
        else:
            X = np.array(values).reshape(-1, 1)

        try:
            predictions = self.model.fit_predict(X)
            scores = self.model.negative_outlier_factor_

            anomalies = []
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:
                    # LOF scores are negative, more negative = more anomalous
                    # Convert to confidence (0-1)
                    confidence = min(abs(score) / 10.0, 1.0)

                    anomaly = {
                        'index': i,
                        'value': float(values[i]),
                        'lof_score': float(score),
                        'confidence': float(confidence),
                        'method': 'lof'
                    }

                    if timestamps and i < len(timestamps):
                        anomaly['timestamp'] = timestamps[i]

                    anomalies.append(anomaly)

            return anomalies

        except Exception as e:
            logger.error(f"Error in LOF detection: {e}")
            return []


class EnsembleMLDetector:
    """
    Ensemble of ML-based anomaly detectors.
    """

    def __init__(self):
        """Initialize ensemble ML detector."""
        self.detectors = [
            IsolationForestDetector(),
            LOFDetector()
        ]

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None,
        features: Optional[np.ndarray] = None,
        min_consensus: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using ensemble of ML methods.

        Args:
            values: List of values
            timestamps: Optional timestamps
            features: Optional feature matrix
            min_consensus: Minimum detectors that must agree

        Returns:
            List of anomalies
        """
        all_detections = {}

        for detector in self.detectors:
            try:
                detections = detector.detect(values, timestamps, features)
                for detection in detections:
                    idx = detection['index']
                    if idx not in all_detections:
                        all_detections[idx] = {
                            'index': idx,
                            'value': detection['value'],
                            'detections': [],
                            'methods': []
                        }
                    all_detections[idx]['detections'].append(detection)
                    all_detections[idx]['methods'].append(detection['method'])
            except Exception as e:
                logger.error(f"Error in {detector.__class__.__name__}: {e}")

        # Filter by consensus
        anomalies = []
        for idx, detection_group in all_detections.items():
            if len(detection_group['detections']) >= min_consensus:
                confidences = [d['confidence'] for d in detection_group['detections']]
                ensemble_confidence = np.mean(confidences)

                anomaly = {
                    'index': idx,
                    'value': detection_group['value'],
                    'confidence': float(ensemble_confidence),
                    'consensus_count': len(detection_group['detections']),
                    'methods': detection_group['methods'],
                    'method': 'ml_ensemble'
                }

                if timestamps and idx < len(timestamps):
                    anomaly['timestamp'] = timestamps[idx]

                anomalies.append(anomaly)

        return anomalies
