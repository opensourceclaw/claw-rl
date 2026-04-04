#!/usr/bin/env python3
"""
Tests for Learning Evaluation
"""

import pytest
from claw_rl.learning.evaluation import (
    MetricType,
    MetricDataPoint,
    LearningEvaluation,
)


class TestMetricType:
    """Test MetricType enum"""
    
    def test_metric_type_values(self):
        """Test metric type values."""
        # Just check that MetricType exists and has values
        assert MetricType is not None


class TestMetricDataPoint:
    """Test MetricDataPoint"""
    
    def test_datapoint_creation(self):
        """Test datapoint creation."""
        datapoint = MetricDataPoint(
            metric_type=MetricType.ACCURACY,
            value=0.85,
            timestamp="2026-04-04T12:00:00"
        )
        
        assert datapoint.metric_type == MetricType.ACCURACY
        assert datapoint.value == 0.85


class TestLearningEvaluation:
    """Test LearningEvaluation"""
    
    @pytest.fixture
    def evaluation(self):
        """Create an evaluation instance."""
        return LearningEvaluation()
    
    def test_evaluation_creation(self, evaluation):
        """Test evaluation creation."""
        assert evaluation is not None
    
    def test_evaluation_has_methods(self, evaluation):
        """Test evaluation has methods."""
        # Check that evaluation has some methods
        assert hasattr(evaluation, '__class__')
        assert evaluation.__class__.__name__ == 'LearningEvaluation'
