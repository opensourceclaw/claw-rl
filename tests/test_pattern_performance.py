"""
Performance benchmarks for Pattern Recognition Engine.

Reference: ADR-007: Pattern Recognition Engine
Performance Requirements:
- Pattern recognition (100 memories) < 100ms
- Anomaly detection (100 memories) < 50ms
"""

import pytest
import time
from datetime import datetime, timedelta

from claw_rl.pattern import (
    PatternRecognitionEngine,
    TemporalPatternRecognizer,
    BehavioralPatternClusterer,
    ContextualAssociationAnalyzer,
    AnomalyDetector,
    PatternType
)


def generate_test_memories(count: int) -> list:
    """Generate test memories for performance testing."""
    memories = []
    base_time = datetime.now()
    
    for i in range(count):
        memories.append({
            'id': f'mem_{i}',
            'timestamp': base_time + timedelta(hours=i),
            'content': f'Test memory {i} ' * (i % 10 + 1),
            'behavior': ['work', 'relax', 'learn', 'exercise'][i % 4],
            'context': {
                'time': ['morning', 'afternoon', 'evening'][i % 3],
                'location': ['home', 'office', 'cafe'][i % 3]
            },
            'value': i * 10
        })
    
    return memories


class TestPatternRecognitionPerformance:
    """Performance tests for Pattern Recognition Engine."""
    
    def test_engine_recognition_performance_100_memories(self):
        """Test pattern recognition performance with 100 memories.
        
        Target: < 100ms
        """
        engine = PatternRecognitionEngine()
        memories = generate_test_memories(100)
        memory_ids = [m['id'] for m in memories]
        
        # Warm up
        engine.recognize_patterns(memory_ids[:10])
        
        # Benchmark
        start_time = time.time()
        result = engine.recognize_patterns(memory_ids)
        elapsed_time = (time.time() - start_time) * 1000  # ms
        
        print(f"\nPattern Recognition (100 memories): {elapsed_time:.2f}ms")
        
        # Assertions
        assert result is not None
        assert elapsed_time < 100, f"Pattern recognition took {elapsed_time:.2f}ms (target: <100ms)"
    
    def test_temporal_recognition_performance(self):
        """Test temporal pattern recognition performance.
        
        Target: < 50ms for 100 memories
        """
        recognizer = TemporalPatternRecognizer()
        memories = generate_test_memories(100)
        
        # Warm up
        recognizer.recognize(memories[:10])
        
        # Benchmark
        start_time = time.time()
        patterns = recognizer.recognize(memories)
        elapsed_time = (time.time() - start_time) * 1000  # ms
        
        print(f"\nTemporal Recognition (100 memories): {elapsed_time:.2f}ms")
        
        # Assertions
        assert patterns is not None
        assert elapsed_time < 50, f"Temporal recognition took {elapsed_time:.2f}ms (target: <50ms)"
    
    def test_behavioral_clustering_performance(self):
        """Test behavioral clustering performance.
        
        Target: < 50ms for 100 memories
        """
        clusterer = BehavioralPatternClusterer()
        memories = generate_test_memories(100)
        
        # Warm up
        clusterer.cluster(memories[:10])
        
        # Benchmark
        start_time = time.time()
        patterns = clusterer.cluster(memories)
        elapsed_time = (time.time() - start_time) * 1000  # ms
        
        print(f"\nBehavioral Clustering (100 memories): {elapsed_time:.2f}ms")
        
        # Assertions
        assert patterns is not None
        assert elapsed_time < 50, f"Behavioral clustering took {elapsed_time:.2f}ms (target: <50ms)"
    
    def test_contextual_analysis_performance(self):
        """Test contextual association analysis performance.
        
        Target: < 50ms for 100 memories
        """
        analyzer = ContextualAssociationAnalyzer()
        memories = generate_test_memories(100)
        
        # Warm up
        analyzer.analyze(memories[:10])
        
        # Benchmark
        start_time = time.time()
        patterns = analyzer.analyze(memories)
        elapsed_time = (time.time() - start_time) * 1000  # ms
        
        print(f"\nContextual Analysis (100 memories): {elapsed_time:.2f}ms")
        
        # Assertions
        assert patterns is not None
        assert elapsed_time < 50, f"Contextual analysis took {elapsed_time:.2f}ms (target: <50ms)"
    
    def test_anomaly_detection_performance(self):
        """Test anomaly detection performance.
        
        Target: < 50ms for 100 memories
        """
        detector = AnomalyDetector()
        memories = generate_test_memories(100)
        
        # Add some anomalies
        memories[50]['value'] = 10000  # Outlier
        memories[75]['value'] = 15000  # Outlier
        
        # Warm up
        detector.detect(memories[:10])
        
        # Benchmark
        start_time = time.time()
        alerts = detector.detect(memories)
        elapsed_time = (time.time() - start_time) * 1000  # ms
        
        print(f"\nAnomaly Detection (100 memories): {elapsed_time:.2f}ms")
        
        # Assertions
        assert alerts is not None
        assert elapsed_time < 50, f"Anomaly detection took {elapsed_time:.2f}ms (target: <50ms)"
    
    def test_engine_incremental_performance(self):
        """Test incremental pattern recognition performance.
        
        Target: < 10ms per memory
        """
        engine = PatternRecognitionEngine()
        
        # Process 10 memories incrementally
        times = []
        for i in range(10):
            memories = generate_test_memories(1)
            memory_ids = [m['id'] for m in memories]
            
            start_time = time.time()
            result = engine.recognize_patterns(memory_ids)
            elapsed_time = (time.time() - start_time) * 1000  # ms
            times.append(elapsed_time)
        
        avg_time = sum(times) / len(times)
        print(f"\nIncremental Recognition (per memory): {avg_time:.2f}ms")
        
        # Assertions
        assert avg_time < 10, f"Incremental recognition took {avg_time:.2f}ms (target: <10ms)"
    
    def test_engine_memory_usage(self):
        """Test memory usage for pattern recognition.
        
        Target: < 10MB for 100 memories
        """
        import sys
        
        engine = PatternRecognitionEngine()
        memories = generate_test_memories(100)
        memory_ids = [m['id'] for m in memories]
        
        # Measure memory before
        mem_before = sys.getsizeof(engine._patterns)
        
        # Process memories
        result = engine.recognize_patterns(memory_ids)
        
        # Measure memory after
        mem_after = sys.getsizeof(engine._patterns)
        mem_increase = (mem_after - mem_before) / 1024  # KB
        
        print(f"\nMemory Usage: {mem_increase:.2f}KB")
        
        # Note: This is a simple check. Real memory profiling would require more sophisticated tools.
        assert mem_increase < 10240, f"Memory usage increased by {mem_increase:.2f}KB (target: <10MB)"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
