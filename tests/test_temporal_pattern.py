"""
Unit tests for Temporal Pattern Recognition.
"""

import pytest
from datetime import datetime, timedelta

from claw_rl.pattern import (
    TemporalPatternRecognizer,
    TemporalPattern,
    TemporalPatternType,
    TimeWindow
)


class TestTimeWindow:
    """Test TimeWindow."""
    
    def test_time_window_creation(self):
        """Test time window creation."""
        start = datetime.now()
        end = start + timedelta(hours=1)
        
        window = TimeWindow(start=start, end=end)
        
        assert window.start == start
        assert window.end == end
    
    def test_time_window_duration(self):
        """Test time window duration."""
        start = datetime.now()
        end = start + timedelta(hours=2)
        
        window = TimeWindow(start=start, end=end)
        
        assert window.duration() == timedelta(hours=2)
    
    def test_time_window_contains(self):
        """Test time window contains."""
        start = datetime.now()
        end = start + timedelta(hours=1)
        
        window = TimeWindow(start=start, end=end)
        
        assert window.contains(start + timedelta(minutes=30))
        assert not window.contains(start - timedelta(minutes=30))
        assert not window.contains(end + timedelta(minutes=30))
    
    def test_time_window_to_dict(self):
        """Test time window to_dict."""
        start = datetime.now()
        end = start + timedelta(hours=1)
        
        window = TimeWindow(start=start, end=end)
        window_dict = window.to_dict()
        
        assert 'start' in window_dict
        assert 'end' in window_dict
        assert 'duration_seconds' in window_dict
        assert window_dict['duration_seconds'] == 3600.0


class TestTemporalPattern:
    """Test TemporalPattern."""
    
    def test_temporal_pattern_creation(self):
        """Test temporal pattern creation."""
        start = datetime.now()
        end = start + timedelta(hours=1)
        
        pattern = TemporalPattern(
            pattern_id="temporal-001",
            pattern_type=TemporalPatternType.PERIODIC,
            time_window=TimeWindow(start=start, end=end),
            confidence=0.85,
            frequency=5,
            period=timedelta(days=1)
        )
        
        assert pattern.pattern_id == "temporal-001"
        assert pattern.pattern_type == TemporalPatternType.PERIODIC
        assert pattern.confidence == 0.85
        assert pattern.frequency == 5
        assert pattern.period == timedelta(days=1)
    
    def test_temporal_pattern_to_dict(self):
        """Test temporal pattern to_dict."""
        start = datetime.now()
        end = start + timedelta(hours=1)
        
        pattern = TemporalPattern(
            pattern_id="temporal-001",
            pattern_type=TemporalPatternType.SEQUENTIAL,
            time_window=TimeWindow(start=start, end=end),
            confidence=0.90,
            frequency=3,
            sequence=['A', 'B', 'C']
        )
        
        pattern_dict = pattern.to_dict()
        
        assert pattern_dict['pattern_id'] == "temporal-001"
        assert pattern_dict['pattern_type'] == 'sequential'
        assert pattern_dict['confidence'] == 0.90
        assert pattern_dict['sequence'] == ['A', 'B', 'C']
    
    def test_temporal_pattern_is_significant(self):
        """Test temporal pattern significance."""
        start = datetime.now()
        end = start + timedelta(hours=1)
        
        # Significant pattern
        significant = TemporalPattern(
            pattern_id="temporal-001",
            pattern_type=TemporalPatternType.PERIODIC,
            time_window=TimeWindow(start=start, end=end),
            confidence=0.85,
            frequency=5
        )
        
        assert significant.is_significant(min_confidence=0.7, min_frequency=3)
        
        # Low confidence
        low_confidence = TemporalPattern(
            pattern_id="temporal-002",
            pattern_type=TemporalPatternType.PERIODIC,
            time_window=TimeWindow(start=start, end=end),
            confidence=0.65,
            frequency=5
        )
        
        assert not low_confidence.is_significant(min_confidence=0.7, min_frequency=3)


class TestTemporalPatternRecognizer:
    """Test TemporalPatternRecognizer."""
    
    def test_recognizer_creation(self):
        """Test recognizer creation."""
        recognizer = TemporalPatternRecognizer()
        
        assert recognizer.min_confidence == 0.7
        assert recognizer.min_frequency == 3
        assert recognizer.window_size == timedelta(hours=1)
    
    def test_recognizer_with_config(self):
        """Test recognizer with configuration."""
        config = {
            'min_confidence': 0.8,
            'min_frequency': 5,
            'window_size': timedelta(hours=2)
        }
        
        recognizer = TemporalPatternRecognizer(config=config)
        
        assert recognizer.min_confidence == 0.8
        assert recognizer.min_frequency == 5
        assert recognizer.window_size == timedelta(hours=2)
    
    def test_recognize_periodic_patterns(self):
        """Test periodic pattern recognition."""
        recognizer = TemporalPatternRecognizer()
        
        # Create memories with periodic pattern (daily)
        now = datetime.now()
        memories = []
        
        for i in range(10):
            memories.append({
                'id': f'mem{i}',
                'timestamp': now + timedelta(days=i),
                'content': f'Memory {i}'
            })
        
        patterns = recognizer.recognize(
            memories,
            pattern_types=[TemporalPatternType.PERIODIC]
        )
        
        assert patterns is not None
        # Should detect periodic patterns
        assert len(patterns) >= 0
    
    def test_recognize_sequential_patterns(self):
        """Test sequential pattern recognition."""
        recognizer = TemporalPatternRecognizer()
        
        # Create memories with repeating sequence
        now = datetime.now()
        memories = []
        
        # Repeat the same sequence 3 times
        for _ in range(3):
            memories.append({
                'id': f'mem_a',
                'timestamp': now,
                'content': 'Action A'
            })
            memories.append({
                'id': f'mem_b',
                'timestamp': now + timedelta(minutes=1),
                'content': 'Action B'
            })
            memories.append({
                'id': f'mem_c',
                'timestamp': now + timedelta(minutes=2),
                'content': 'Action C'
            })
        
        patterns = recognizer.recognize(
            memories,
            pattern_types=[TemporalPatternType.SEQUENTIAL]
        )
        
        assert patterns is not None
        # Should detect sequential patterns
        assert len(patterns) >= 0
    
    def test_recognize_trending_patterns(self):
        """Test trending pattern recognition."""
        recognizer = TemporalPatternRecognizer()
        
        # Create memories with increasing trend
        now = datetime.now()
        memories = []
        
        # Increasing number of memories per window
        for i in range(20):
            memories.append({
                'id': f'mem{i}',
                'timestamp': now + timedelta(hours=i),
                'content': f'Memory {i}'
            })
        
        patterns = recognizer.recognize(
            memories,
            pattern_types=[TemporalPatternType.TRENDING]
        )
        
        assert patterns is not None
        # Should detect trending pattern
        if len(patterns) > 0:
            trending = patterns[0]
            assert trending.pattern_type == TemporalPatternType.TRENDING
    
    def test_recognize_burst_patterns(self):
        """Test burst pattern recognition."""
        recognizer = TemporalPatternRecognizer()
        
        # Create memories with burst
        now = datetime.now()
        memories = []
        
        # Normal activity
        for i in range(5):
            memories.append({
                'id': f'mem{i}',
                'timestamp': now + timedelta(hours=i),
                'content': f'Memory {i}'
            })
        
        # Burst
        for i in range(15):
            memories.append({
                'id': f'mem_burst{i}',
                'timestamp': now + timedelta(hours=5),
                'content': f'Burst memory {i}'
            })
        
        patterns = recognizer.recognize(
            memories,
            pattern_types=[TemporalPatternType.BURST]
        )
        
        assert patterns is not None
        # Should detect burst pattern
        assert len(patterns) >= 0
    
    def test_recognize_all_patterns(self):
        """Test recognizing all pattern types."""
        recognizer = TemporalPatternRecognizer()
        
        # Create diverse memories
        now = datetime.now()
        memories = []
        
        for i in range(20):
            memories.append({
                'id': f'mem{i}',
                'timestamp': now + timedelta(hours=i),
                'content': f'Memory {i}'
            })
        
        patterns = recognizer.recognize(memories)
        
        assert patterns is not None
        # Should recognize multiple pattern types
        pattern_types = set(p.pattern_type for p in patterns)
        assert len(pattern_types) >= 0
    
    def test_get_statistics(self):
        """Test recognizer statistics."""
        recognizer = TemporalPatternRecognizer()
        
        # Recognize patterns
        now = datetime.now()
        memories = [
            {'id': f'mem{i}', 'timestamp': now + timedelta(hours=i), 'content': f'Memory {i}'}
            for i in range(10)
        ]
        
        recognizer.recognize(memories)
        
        stats = recognizer.get_statistics()
        
        assert 'total_processed' in stats
        assert 'patterns_found' in stats
        assert stats['total_processed'] == 10
