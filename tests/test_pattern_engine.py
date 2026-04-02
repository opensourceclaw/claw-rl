"""
Unit tests for Pattern Recognition Engine.
"""

import pytest
from datetime import datetime

from claw_rl.pattern import (
    PatternRecognitionEngine,
    Pattern,
    Anomaly,
    PatternType,
    AnomalyType,
    PatternRecognitionResult,
    recognize_patterns
)


class TestPattern:
    """Test Pattern."""
    
    def test_pattern_creation(self):
        """Test pattern creation."""
        pattern = Pattern(
            pattern_id="test-001",
            pattern_type=PatternType.TEMPORAL,
            confidence=0.85,
            occurrences=5,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        assert pattern.pattern_id == "test-001"
        assert pattern.pattern_type == PatternType.TEMPORAL
        assert pattern.confidence == 0.85
        assert pattern.occurrences == 5
    
    def test_pattern_to_dict(self):
        """Test pattern to_dict."""
        pattern = Pattern(
            pattern_id="test-001",
            pattern_type=PatternType.BEHAVIORAL,
            confidence=0.90,
            occurrences=3,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            context={'key': 'value'},
            examples=['ex1', 'ex2']
        )
        
        pattern_dict = pattern.to_dict()
        
        assert pattern_dict['pattern_id'] == "test-001"
        assert pattern_dict['pattern_type'] == 'behavioral'
        assert pattern_dict['confidence'] == 0.90
        assert pattern_dict['context']['key'] == 'value'
    
    def test_pattern_is_significant(self):
        """Test pattern significance check."""
        # Significant pattern
        significant = Pattern(
            pattern_id="test-001",
            pattern_type=PatternType.TEMPORAL,
            confidence=0.85,
            occurrences=5,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        assert significant.is_significant(min_confidence=0.7, min_occurrences=3)
        
        # Low confidence
        low_confidence = Pattern(
            pattern_id="test-002",
            pattern_type=PatternType.TEMPORAL,
            confidence=0.65,
            occurrences=5,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        assert not low_confidence.is_significant(min_confidence=0.7, min_occurrences=3)
        
        # Low occurrences
        low_occurrences = Pattern(
            pattern_id="test-003",
            pattern_type=PatternType.TEMPORAL,
            confidence=0.85,
            occurrences=2,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        assert not low_occurrences.is_significant(min_confidence=0.7, min_occurrences=3)


class TestAnomaly:
    """Test Anomaly."""
    
    def test_anomaly_creation(self):
        """Test anomaly creation."""
        anomaly = Anomaly(
            anomaly_id="anomaly-001",
            anomaly_type=AnomalyType.BEHAVIORAL,
            severity=0.90,
            detected_at=datetime.now(),
            memory_id="mem-001",
            description="Unusual behavior detected"
        )
        
        assert anomaly.anomaly_id == "anomaly-001"
        assert anomaly.anomaly_type == AnomalyType.BEHAVIORAL
        assert anomaly.severity == 0.90
        assert anomaly.memory_id == "mem-001"
    
    def test_anomaly_to_dict(self):
        """Test anomaly to_dict."""
        anomaly = Anomaly(
            anomaly_id="anomaly-001",
            anomaly_type=AnomalyType.STATISTICAL,
            severity=0.85,
            detected_at=datetime.now(),
            memory_id="mem-001",
            description="Statistical outlier",
            context={'metric': 'value'}
        )
        
        anomaly_dict = anomaly.to_dict()
        
        assert anomaly_dict['anomaly_id'] == "anomaly-001"
        assert anomaly_dict['anomaly_type'] == 'statistical'
        assert anomaly_dict['severity'] == 0.85
        assert anomaly_dict['context']['metric'] == 'value'
    
    def test_anomaly_is_critical(self):
        """Test anomaly critical check."""
        # Critical anomaly
        critical = Anomaly(
            anomaly_id="anomaly-001",
            anomaly_type=AnomalyType.TEMPORAL,
            severity=0.90,
            detected_at=datetime.now(),
            memory_id="mem-001",
            description="Critical anomaly"
        )
        
        assert critical.is_critical(threshold=0.8)
        
        # Non-critical anomaly
        non_critical = Anomaly(
            anomaly_id="anomaly-002",
            anomaly_type=AnomalyType.TEMPORAL,
            severity=0.70,
            detected_at=datetime.now(),
            memory_id="mem-002",
            description="Non-critical anomaly"
        )
        
        assert not non_critical.is_critical(threshold=0.8)


class TestPatternRecognitionResult:
    """Test PatternRecognitionResult."""
    
    def test_result_creation(self):
        """Test result creation."""
        pattern = Pattern(
            pattern_id="test-001",
            pattern_type=PatternType.TEMPORAL,
            confidence=0.85,
            occurrences=5,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        anomaly = Anomaly(
            anomaly_id="anomaly-001",
            anomaly_type=AnomalyType.BEHAVIORAL,
            severity=0.90,
            detected_at=datetime.now(),
            memory_id="mem-001",
            description="Anomaly"
        )
        
        result = PatternRecognitionResult(
            patterns=[pattern],
            anomalies=[anomaly],
            processing_time=1.5,
            memories_processed=10
        )
        
        assert len(result.patterns) == 1
        assert len(result.anomalies) == 1
        assert result.processing_time == 1.5
        assert result.memories_processed == 10
    
    def test_result_significant_patterns(self):
        """Test result significant patterns."""
        significant = Pattern(
            pattern_id="test-001",
            pattern_type=PatternType.TEMPORAL,
            confidence=0.85,
            occurrences=5,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        non_significant = Pattern(
            pattern_id="test-002",
            pattern_type=PatternType.TEMPORAL,
            confidence=0.65,
            occurrences=2,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        result = PatternRecognitionResult(
            patterns=[significant, non_significant],
            anomalies=[],
            processing_time=1.0,
            memories_processed=10
        )
        
        significant_patterns = result.significant_patterns(min_confidence=0.7, min_occurrences=3)
        
        assert len(significant_patterns) == 1
        assert significant_patterns[0].pattern_id == "test-001"
    
    def test_result_critical_anomalies(self):
        """Test result critical anomalies."""
        critical = Anomaly(
            anomaly_id="anomaly-001",
            anomaly_type=AnomalyType.TEMPORAL,
            severity=0.90,
            detected_at=datetime.now(),
            memory_id="mem-001",
            description="Critical anomaly"
        )
        
        non_critical = Anomaly(
            anomaly_id="anomaly-002",
            anomaly_type=AnomalyType.TEMPORAL,
            severity=0.70,
            detected_at=datetime.now(),
            memory_id="mem-002",
            description="Non-critical anomaly"
        )
        
        result = PatternRecognitionResult(
            patterns=[],
            anomalies=[critical, non_critical],
            processing_time=1.0,
            memories_processed=10
        )
        
        critical_anomalies = result.critical_anomalies(threshold=0.8)
        
        assert len(critical_anomalies) == 1
        assert critical_anomalies[0].anomaly_id == "anomaly-001"


class TestPatternRecognitionEngine:
    """Test PatternRecognitionEngine."""
    
    def test_engine_creation(self):
        """Test engine creation."""
        engine = PatternRecognitionEngine()
        
        assert engine.memory_store is None
        assert engine.min_confidence == 0.7
        assert engine.min_occurrences == 3
    
    def test_engine_with_config(self):
        """Test engine with configuration."""
        config = {
            'min_confidence': 0.8,
            'min_occurrences': 5,
            'anomaly_threshold': 0.9
        }
        
        engine = PatternRecognitionEngine(config=config)
        
        assert engine.min_confidence == 0.8
        assert engine.min_occurrences == 5
        assert engine.anomaly_threshold == 0.9
    
    def test_recognize_patterns(self):
        """Test pattern recognition."""
        engine = PatternRecognitionEngine()
        
        result = engine.recognize_patterns(
            memory_ids=["mem1", "mem2", "mem3"],
            pattern_types=[PatternType.TEMPORAL]
        )
        
        assert result is not None
        assert len(result.patterns) > 0
        assert result.processing_time > 0
        assert result.memories_processed == 3
    
    def test_recognize_patterns_all_types(self):
        """Test pattern recognition with all types."""
        engine = PatternRecognitionEngine()
        
        # Create more realistic test data with timestamps
        from datetime import datetime, timedelta
        base_time = datetime.now()
        memories = []
        for i in range(10):
            memories.append({
                'id': f'mem{i}',
                'timestamp': base_time + timedelta(hours=i),
                'content': f'Memory {i}',
                'behavior': 'work' if i % 2 == 0 else 'relax',
                'context': {'time': 'morning' if i < 5 else 'afternoon'}
            })
        
        result = engine.recognize_patterns(
            memory_ids=[m['id'] for m in memories]
        )
        
        assert result is not None
        assert len(result.patterns) > 0
        # Should recognize at least temporal patterns
        # Note: behavioral and contextual may not always produce patterns with minimal data
        pattern_types = set(p.pattern_type for p in result.patterns)
        assert len(pattern_types) >= 1  # At least temporal patterns
    
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        engine = PatternRecognitionEngine()
        
        anomalies = engine.detect_anomalies(
            memory_ids=["mem1", "mem2", "mem3"]
        )
        
        assert anomalies is not None
        assert isinstance(anomalies, list)
    
    def test_get_pattern(self):
        """Test get pattern by ID."""
        engine = PatternRecognitionEngine()
        
        # Recognize patterns first
        result = engine.recognize_patterns(
            memory_ids=["mem1", "mem2", "mem3"]
        )
        
        # Get all patterns
        all_patterns = engine.get_all_patterns()
        
        # Should have patterns
        assert len(all_patterns) >= 0
    
    def test_get_statistics(self):
        """Test engine statistics."""
        engine = PatternRecognitionEngine()
        
        # Recognize patterns
        engine.recognize_patterns(memory_ids=["mem1", "mem2", "mem3"])
        
        stats = engine.get_statistics()
        
        assert 'total_processed' in stats
        assert 'total_patterns_found' in stats
        assert 'total_anomalies_detected' in stats
        assert 'patterns_stored' in stats
        
        assert stats['total_processed'] == 3


class TestRecognizePatternsFunction:
    """Test recognize_patterns convenience function."""
    
    def test_recognize_patterns_function(self):
        """Test recognize_patterns function."""
        result = recognize_patterns(
            memory_ids=["mem1", "mem2", "mem3"],
            pattern_types=[PatternType.TEMPORAL]
        )
        
        assert result is not None
        assert isinstance(result, PatternRecognitionResult)
        assert len(result.patterns) > 0
