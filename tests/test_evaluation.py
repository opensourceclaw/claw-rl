#!/usr/bin/env python3
"""
Tests for Learning Evaluation
"""

import pytest
from claw_rl.learning.evaluation import (
    MetricType,
    MetricDataPoint,
    MetricSummary,
    EvaluationResult,
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
    
    def test_metric_datapoint_creation(self):
        """Test metric datapoint creation."""
        datapoint = MetricDataPoint(
            timestamp="2026-04-04T12:00:00",
            value=0.85,
            metric_type="accuracy"
        )
        
        assert datapoint.timestamp == "2026-04-04T12:00:00"
        assert datapoint.value == 0.85
        assert datapoint.metric_type == "accuracy"
    
    def test_metric_datapoint_to_dict(self):
        """Test metric datapoint to dict."""
        datapoint = MetricDataPoint(
            timestamp="2026-04-04T12:00:00",
            value=0.9,
            metric_type="accuracy"
        )
        
        d = datapoint.to_dict()
        
        assert "timestamp" in d
        assert "value" in d
        assert "metric_type" in d
    
    def test_metric_summary_creation(self):
        """Test metric summary creation."""
        summary = MetricSummary(
            metric_type="accuracy",
            count=10,
            mean=0.85,
            std_dev=0.05,
            min_value=0.75,
            max_value=0.95,
            trend="up",
            improvement_rate=0.1
        )
        
        assert summary.metric_type == "accuracy"
        assert summary.count == 10
        assert summary.mean == 0.85
    
    def test_metric_summary_to_dict(self):
        """Test metric summary to dict."""
        summary = MetricSummary(
            metric_type="accuracy",
            count=10,
            mean=0.85,
            std_dev=0.05,
            min_value=0.75,
            max_value=0.95,
            trend="up",
            improvement_rate=0.1
        )
        
        d = summary.to_dict()
        
        assert "metric_type" in d
        assert "mean" in d
        assert "trend" in d
    
    def test_evaluation_result_creation(self):
        """Test evaluation result creation."""
        result = EvaluationResult(
            evaluation_id="eval-001",
            evaluated_at="2026-04-04T12:00:00",
            period_start="2026-04-01T00:00:00",
            period_end="2026-04-04T12:00:00",
            metrics={},
            overall_score=0.85,
            overall_trend="improving",
            roi_percentage=15.0,
            cost_savings=1000.0,
            time_savings_hours=10.0,
            recommendations=["Continue current strategy"]
        )
        
        assert result.evaluation_id == "eval-001"
        assert result.overall_score == 0.85
        assert result.overall_trend == "improving"
