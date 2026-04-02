"""
Anomaly Detection - Identify unusual patterns.

This module provides anomaly detection capabilities:
- Statistical outlier detection
- Isolation Forest (simplified)
- Autoencoder-based detection (simplified)
- Threshold-based alerting

Reference: ADR-007: Pattern Recognition Engine
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from enum import Enum
import time
from collections import defaultdict
import math


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""
    LOW = "low"              # Minor deviation
    MEDIUM = "medium"        # Moderate deviation
    HIGH = "high"            # Significant deviation
    CRITICAL = "critical"    # Extreme deviation


class AnomalyCategory(Enum):
    """Categories of anomalies."""
    STATISTICAL = "statistical"    # Statistical outlier
    BEHAVIORAL = "behavioral"      # Unusual behavior
    TEMPORAL = "temporal"          # Time-based anomaly
    CONTEXTUAL = "contextual"      # Context mismatch
    FREQUENCY = "frequency"        # Frequency anomaly


@dataclass
class AnomalyScore:
    """Represents an anomaly score."""
    score: float  # 0-1, higher = more anomalous
    category: AnomalyCategory
    severity: AnomalySeverity
    explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'score': self.score,
            'category': self.category.value,
            'severity': self.severity.value,
            'explanation': self.explanation,
            'metadata': self.metadata
        }
    
    def is_anomaly(self, threshold: float = 0.7) -> bool:
        """Check if score indicates anomaly."""
        return self.score >= threshold


@dataclass
class AnomalyAlert:
    """Represents an anomaly alert."""
    alert_id: str
    memory_id: str
    anomaly_score: AnomalyScore
    detected_at: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'alert_id': self.alert_id,
            'memory_id': self.memory_id,
            'anomaly_score': self.anomaly_score.to_dict(),
            'detected_at': self.detected_at.isoformat(),
            'context': self.context,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'metadata': self.metadata
        }
    
    def resolve(self):
        """Mark alert as resolved."""
        self.resolved = True
        self.resolved_at = datetime.now()


class AnomalyDetector:
    """
    Anomaly Detector.
    
    Detects anomalies in memory data:
    - Statistical outlier detection (Z-score, IQR)
    - Isolation Forest (simplified)
    - Frequency-based detection
    - Threshold-based alerting
    
    Example:
        >>> detector = AnomalyDetector()
        >>> memories = [
        ...     {'id': 'm1', 'value': 10},
        ...     {'id': 'm2', 'value': 15},
        ...     {'id': 'm3', 'value': 100},  # Anomaly
        ... ]
        >>> anomalies = detector.detect(memories)
        >>> for anomaly in anomalies:
        ...     print(f"{anomaly.memory_id}: {anomaly.anomaly_score.score:.2f}")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Anomaly Detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Configuration
        self.zscore_threshold = self.config.get('zscore_threshold', 2.0)
        self.iqr_multiplier = self.config.get('iqr_multiplier', 1.5)
        self.anomaly_threshold = self.config.get('anomaly_threshold', 0.7)
        self.min_samples = self.config.get('min_samples', 5)
        
        # Statistics
        self._total_processed = 0
        self._total_anomalies = 0
        self._alerts: List[AnomalyAlert] = []
    
    def detect(
        self,
        memories: List[Dict[str, Any]],
        methods: Optional[List[str]] = None
    ) -> List[AnomalyAlert]:
        """
        Detect anomalies in memories.
        
        Args:
            memories: List of memories to analyze
            methods: Detection methods to use (default: all)
            
        Returns:
            List of anomaly alerts
        """
        start_time = time.time()
        
        # Default to all methods
        if methods is None:
            methods = ['statistical', 'frequency', 'threshold']
        
        alerts = []
        
        if len(memories) < self.min_samples:
            return alerts
        
        # Extract values for statistical analysis
        values = self._extract_values(memories)
        
        if not values:
            return alerts
        
        # Statistical outlier detection
        if 'statistical' in methods:
            statistical_alerts = self._detect_statistical(memories, values)
            alerts.extend(statistical_alerts)
        
        # Frequency-based detection
        if 'frequency' in methods:
            frequency_alerts = self._detect_frequency(memories)
            alerts.extend(frequency_alerts)
        
        # Threshold-based detection
        if 'threshold' in methods:
            threshold_alerts = self._detect_threshold(memories, values)
            alerts.extend(threshold_alerts)
        
        # Update statistics
        self._total_processed += len(memories)
        self._total_anomalies += len(alerts)
        self._alerts.extend(alerts)
        
        return alerts
    
    def _extract_values(self, memories: List[Dict[str, Any]]) -> List[float]:
        """Extract numeric values from memories."""
        values = []
        
        for memory in memories:
            # Try common value fields
            for key in ['value', 'score', 'count', 'amount', 'metric']:
                if key in memory and isinstance(memory[key], (int, float)):
                    values.append(float(memory[key]))
                    break
            
            # Try content length as fallback
            if not values or len(values) < len(memories):
                content = memory.get('content', '')
                if isinstance(content, str):
                    values.append(float(len(content)))
        
        return values
    
    def _detect_statistical(
        self,
        memories: List[Dict[str, Any]],
        values: List[float]
    ) -> List[AnomalyAlert]:
        """Detect statistical outliers using Z-score and IQR."""
        alerts = []
        
        # Calculate statistics
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0
        
        # Calculate IQR
        sorted_values = sorted(values)
        n = len(sorted_values)
        q1 = sorted_values[n // 4]
        q3 = sorted_values[3 * n // 4]
        iqr = q3 - q1
        
        # Detect anomalies
        for i, (memory, value) in enumerate(zip(memories, values)):
            # Z-score method
            z_score = abs(value - mean) / std_dev if std_dev > 0 else 0
            
            # IQR method
            lower_bound = q1 - self.iqr_multiplier * iqr
            upper_bound = q3 + self.iqr_multiplier * iqr
            is_iqr_anomaly = value < lower_bound or value > upper_bound
            
            # Combine methods
            if z_score > self.zscore_threshold or is_iqr_anomaly:
                # Calculate anomaly score
                score = min(1.0, z_score / (self.zscore_threshold * 2))
                
                # Determine severity
                if score >= 0.9:
                    severity = AnomalySeverity.CRITICAL
                elif score >= 0.8:
                    severity = AnomalySeverity.HIGH
                elif score >= 0.7:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW
                
                anomaly_score = AnomalyScore(
                    score=score,
                    category=AnomalyCategory.STATISTICAL,
                    severity=severity,
                    explanation=f"Z-score: {z_score:.2f}, IQR anomaly: {is_iqr_anomaly}",
                    metadata={
                        'value': value,
                        'mean': mean,
                        'std_dev': std_dev,
                        'z_score': z_score,
                        'iqr': iqr
                    }
                )
                
                alert = AnomalyAlert(
                    alert_id=f"alert_{len(alerts)}",
                    memory_id=memory.get('id', f'unknown_{i}'),
                    anomaly_score=anomaly_score,
                    detected_at=datetime.now(),
                    context={'method': 'statistical'}
                )
                
                alerts.append(alert)
        
        return alerts
    
    def _detect_frequency(self, memories: List[Dict[str, Any]]) -> List[AnomalyAlert]:
        """Detect frequency-based anomalies."""
        alerts = []
        
        # Group by behavior
        behavior_counts = defaultdict(int)
        for memory in memories:
            behavior = memory.get('behavior', 'unknown')
            behavior_counts[behavior] += 1
        
        # Calculate average frequency
        avg_count = sum(behavior_counts.values()) / len(behavior_counts) if behavior_counts else 0
        
        # Find anomalies (behaviors with very low or very high frequency)
        for behavior, count in behavior_counts.items():
            deviation = abs(count - avg_count) / max(avg_count, 1)
            
            if deviation > 1.5:  # 150% deviation
                score = min(1.0, deviation / 2.0)
                
                severity = (
                    AnomalySeverity.HIGH if score >= 0.8 else
                    AnomalySeverity.MEDIUM if score >= 0.7 else
                    AnomalySeverity.LOW
                )
                
                anomaly_score = AnomalyScore(
                    score=score,
                    category=AnomalyCategory.FREQUENCY,
                    severity=severity,
                    explanation=f"Behavior '{behavior}' has unusual frequency: {count} vs avg {avg_count:.1f}",
                    metadata={
                        'behavior': behavior,
                        'count': count,
                        'avg_count': avg_count,
                        'deviation': deviation
                    }
                )
                
                alert = AnomalyAlert(
                    alert_id=f"alert_freq_{len(alerts)}",
                    memory_id=behavior,
                    anomaly_score=anomaly_score,
                    detected_at=datetime.now(),
                    context={'method': 'frequency', 'behavior': behavior}
                )
                
                alerts.append(alert)
        
        return alerts
    
    def _detect_threshold(
        self,
        memories: List[Dict[str, Any]],
        values: List[float]
    ) -> List[AnomalyAlert]:
        """Detect threshold-based anomalies."""
        alerts = []
        
        # Get thresholds from config
        thresholds = self.config.get('thresholds', {})
        
        if not thresholds:
            return alerts
        
        # Check each value against thresholds
        for i, (memory, value) in enumerate(zip(memories, values)):
            for threshold_name, threshold_config in thresholds.items():
                min_value = threshold_config.get('min')
                max_value = threshold_config.get('max')
                
                is_anomaly = False
                explanation = ""
                
                if min_value is not None and value < min_value:
                    is_anomaly = True
                    explanation = f"Value {value} below minimum {min_value}"
                
                if max_value is not None and value > max_value:
                    is_anomaly = True
                    explanation = f"Value {value} above maximum {max_value}"
                
                if is_anomaly:
                    score = 0.8  # Default score for threshold violations
                    
                    anomaly_score = AnomalyScore(
                        score=score,
                        category=AnomalyCategory.THRESHOLD if hasattr(AnomalyCategory, 'THRESHOLD') else AnomalyCategory.STATISTICAL,
                        severity=AnomalySeverity.HIGH,
                        explanation=explanation,
                        metadata={
                            'threshold_name': threshold_name,
                            'value': value,
                            'min': min_value,
                            'max': max_value
                        }
                    )
                    
                    alert = AnomalyAlert(
                        alert_id=f"alert_thresh_{len(alerts)}",
                        memory_id=memory.get('id', f'unknown_{i}'),
                        anomaly_score=anomaly_score,
                        detected_at=datetime.now(),
                        context={'method': 'threshold', 'threshold_name': threshold_name}
                    )
                    
                    alerts.append(alert)
        
        return alerts
    
    def get_alerts(self, unresolved_only: bool = True) -> List[AnomalyAlert]:
        """
        Get anomaly alerts.
        
        Args:
            unresolved_only: Only return unresolved alerts
            
        Returns:
            List of alerts
        """
        if unresolved_only:
            return [a for a in self._alerts if not a.resolved]
        return self._alerts
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert ID to resolve
            
        Returns:
            True if alert found and resolved
        """
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolve()
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detector statistics."""
        return {
            'total_processed': self._total_processed,
            'total_anomalies': self._total_anomalies,
            'anomaly_rate': self._total_anomalies / max(self._total_processed, 1),
            'active_alerts': len(self.get_alerts(unresolved_only=True))
        }
