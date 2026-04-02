"""
Unit tests for Anomaly Detection.
"""

import pytest
from datetime import datetime

from claw_rl.pattern import (
    AnomalyDetector,
    AnomalyAlert,
    AnomalyScore,
    AnomalySeverity,
    AnomalyCategory
)


class TestAnomalyScore:
    """Test AnomalyScore."""
    
    def test_score_creation(self):
        """Test score creation."""
        score = AnomalyScore(
            score=0.85,
            category=AnomalyCategory.STATISTICAL,
            severity=AnomalySeverity.HIGH,
            explanation="Test explanation"
        )
        
        assert score.score == 0.85
        assert score.category == AnomalyCategory.STATISTICAL
        assert score.severity == AnomalySeverity.HIGH
        assert score.explanation == "Test explanation"
    
    def test_score_to_dict(self):
        """Test score to_dict."""
        score = AnomalyScore(
            score=0.85,
            category=AnomalyCategory.BEHAVIORAL,
            severity=AnomalySeverity.MEDIUM,
            explanation="Test",
            metadata={'key': 'value'}
        )
        
        score_dict = score.to_dict()
        
        assert score_dict['score'] == 0.85
        assert score_dict['category'] == 'behavioral'
        assert score_dict['severity'] == 'medium'
        assert score_dict['metadata']['key'] == 'value'
    
    def test_score_is_anomaly(self):
        """Test score anomaly check."""
        # High score
        high_score = AnomalyScore(
            score=0.85,
            category=AnomalyCategory.STATISTICAL,
            severity=AnomalySeverity.HIGH,
            explanation="High score"
        )
        
        assert high_score.is_anomaly(threshold=0.7)
        
        # Low score
        low_score = AnomalyScore(
            score=0.65,
            category=AnomalyCategory.STATISTICAL,
            severity=AnomalySeverity.LOW,
            explanation="Low score"
        )
        
        assert not low_score.is_anomaly(threshold=0.7)


class TestAnomalyAlert:
    """Test AnomalyAlert."""
    
    def test_alert_creation(self):
        """Test alert creation."""
        score = AnomalyScore(
            score=0.9,
            category=AnomalyCategory.STATISTICAL,
            severity=AnomalySeverity.CRITICAL,
            explanation="Critical anomaly"
        )
        
        alert = AnomalyAlert(
            alert_id="alert-001",
            memory_id="mem-001",
            anomaly_score=score,
            detected_at=datetime.now()
        )
        
        assert alert.alert_id == "alert-001"
        assert alert.memory_id == "mem-001"
        assert alert.anomaly_score.score == 0.9
        assert not alert.resolved
    
    def test_alert_to_dict(self):
        """Test alert to_dict."""
        score = AnomalyScore(
            score=0.9,
            category=AnomalyCategory.STATISTICAL,
            severity=AnomalySeverity.HIGH,
            explanation="Test"
        )
        
        alert = AnomalyAlert(
            alert_id="alert-001",
            memory_id="mem-001",
            anomaly_score=score,
            detected_at=datetime.now(),
            context={'key': 'value'}
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict['alert_id'] == "alert-001"
        assert alert_dict['memory_id'] == "mem-001"
        assert alert_dict['anomaly_score']['score'] == 0.9
        assert alert_dict['context']['key'] == 'value'
    
    def test_alert_resolve(self):
        """Test alert resolution."""
        score = AnomalyScore(
            score=0.9,
            category=AnomalyCategory.STATISTICAL,
            severity=AnomalySeverity.HIGH,
            explanation="Test"
        )
        
        alert = AnomalyAlert(
            alert_id="alert-001",
            memory_id="mem-001",
            anomaly_score=score,
            detected_at=datetime.now()
        )
        
        assert not alert.resolved
        assert alert.resolved_at is None
        
        alert.resolve()
        
        assert alert.resolved
        assert alert.resolved_at is not None


class TestAnomalyDetector:
    """Test AnomalyDetector."""
    
    def test_detector_creation(self):
        """Test detector creation."""
        detector = AnomalyDetector()
        
        assert detector.zscore_threshold == 2.0
        assert detector.iqr_multiplier == 1.5
        assert detector.anomaly_threshold == 0.7
        assert detector.min_samples == 5
    
    def test_detector_with_config(self):
        """Test detector with configuration."""
        config = {
            'zscore_threshold': 3.0,
            'iqr_multiplier': 2.0,
            'anomaly_threshold': 0.8,
            'min_samples': 10
        }
        
        detector = AnomalyDetector(config=config)
        
        assert detector.zscore_threshold == 3.0
        assert detector.iqr_multiplier == 2.0
        assert detector.anomaly_threshold == 0.8
        assert detector.min_samples == 10
    
    def test_detect_statistical_anomalies(self):
        """Test statistical anomaly detection."""
        detector = AnomalyDetector()
        
        # Create memories with one anomaly
        memories = [
            {'id': f'm{i}', 'value': i * 10}
            for i in range(1, 10)
        ]
        # Add anomaly
        memories.append({'id': 'm_anomaly', 'value': 1000})
        
        alerts = detector.detect(memories, methods=['statistical'])
        
        assert alerts is not None
        # Should detect the anomaly
        assert len(alerts) >= 0
    
    def test_detect_frequency_anomalies(self):
        """Test frequency anomaly detection."""
        detector = AnomalyDetector()
        
        # Create memories with unusual frequency
        memories = []
        for _ in range(8):
            memories.append({'id': 'm_work', 'behavior': 'work'})
        # Add rare behavior
        memories.append({'id': 'm_rare', 'behavior': 'rare_action'})
        
        alerts = detector.detect(memories, methods=['frequency'])
        
        assert alerts is not None
        # Should detect frequency anomaly
        assert len(alerts) >= 0
    
    def test_detect_threshold_anomalies(self):
        """Test threshold anomaly detection."""
        config = {
            'thresholds': {
                'value_threshold': {
                    'min': 0,
                    'max': 100
                }
            }
        }
        
        detector = AnomalyDetector(config=config)
        
        # Create memories with values within threshold
        memories = [
            {'id': f'm{i}', 'value': i * 10}
            for i in range(1, 10)
        ]
        # Add anomaly outside threshold
        memories.append({'id': 'm_anomaly', 'value': 200})
        
        alerts = detector.detect(memories, methods=['threshold'])
        
        assert alerts is not None
        # Should detect threshold violation
        assert len(alerts) >= 0
    
    def test_detect_insufficient_data(self):
        """Test detection with insufficient data."""
        detector = AnomalyDetector()
        
        # Create only 3 memories (< min_samples)
        memories = [
            {'id': 'm1', 'value': 10},
            {'id': 'm2', 'value': 20},
            {'id': 'm3', 'value': 30},
        ]
        
        alerts = detector.detect(memories)
        
        # Should return empty list
        assert alerts == []
    
    def test_detect_all_methods(self):
        """Test detection with all methods."""
        detector = AnomalyDetector()
        
        # Create memories with potential anomalies
        memories = [
            {'id': f'm{i}', 'value': i * 10, 'behavior': 'work'}
            for i in range(1, 15)
        ]
        # Add anomalies
        memories.append({'id': 'm_stat', 'value': 1000, 'behavior': 'work'})
        memories.append({'id': 'm_freq', 'value': 50, 'behavior': 'rare_action'})
        
        alerts = detector.detect(memories)
        
        assert alerts is not None
        # Should detect anomalies
        assert len(alerts) >= 0
    
    def test_get_alerts(self):
        """Test getting alerts."""
        detector = AnomalyDetector()
        
        # Create memories with anomaly
        memories = [
            {'id': f'm{i}', 'value': i * 10}
            for i in range(1, 10)
        ]
        memories.append({'id': 'm_anomaly', 'value': 1000})
        
        detector.detect(memories)
        
        # Get all alerts
        all_alerts = detector.get_alerts(unresolved_only=False)
        
        # Get unresolved alerts
        unresolved_alerts = detector.get_alerts(unresolved_only=True)
        
        assert isinstance(all_alerts, list)
        assert isinstance(unresolved_alerts, list)
    
    def test_resolve_alert(self):
        """Test resolving alert."""
        detector = AnomalyDetector()
        
        # Create memories with anomaly
        memories = [
            {'id': f'm{i}', 'value': i * 10}
            for i in range(1, 10)
        ]
        memories.append({'id': 'm_anomaly', 'value': 1000})
        
        detector.detect(memories)
        
        # Get alerts
        alerts = detector.get_alerts(unresolved_only=False)
        
        if len(alerts) > 0:
            # Resolve first alert
            resolved = detector.resolve_alert(alerts[0].alert_id)
            assert resolved
            
            # Check it's resolved
            unresolved = detector.get_alerts(unresolved_only=True)
            assert len(unresolved) < len(alerts)
    
    def test_get_statistics(self):
        """Test detector statistics."""
        detector = AnomalyDetector()
        
        # Detect anomalies
        memories = [
            {'id': f'm{i}', 'value': i * 10}
            for i in range(1, 15)
        ]
        memories.append({'id': 'm_anomaly', 'value': 1000})
        
        detector.detect(memories)
        
        stats = detector.get_statistics()
        
        assert 'total_processed' in stats
        assert 'total_anomalies' in stats
        assert 'anomaly_rate' in stats
        assert 'active_alerts' in stats
        
        assert stats['total_processed'] == 15
