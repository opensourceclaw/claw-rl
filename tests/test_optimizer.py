"""
Tests for Strategy Optimizer

Tests for:
- StrategyOptimizer
- StrategyParameter
- OptimizationResult
"""

import pytest
from datetime import datetime, timedelta

from claw_rl.learning.optimizer import (
    OptimizationStrategy,
    AdjustmentDirection,
    StrategyParameter,
    OptimizationResult,
    StrategyOptimizer,
)
from claw_rl.feedback.collector import Feedback, FeedbackCollector


class TestStrategyParameter:
    """Test StrategyParameter dataclass."""
    
    def test_parameter_creation(self):
        """Test creating a parameter."""
        param = StrategyParameter(
            name="learning_rate",
            current_value=0.1,
            min_value=0.01,
            max_value=0.5,
        )
        
        assert param.name == "learning_rate"
        assert param.current_value == 0.1
        assert param.min_value == 0.01
        assert param.max_value == 0.5
    
    def test_parameter_adjust_increase(self):
        """Test increasing parameter."""
        param = StrategyParameter(
            name="test",
            current_value=0.5,
            min_value=0.0,
            max_value=1.0,
            adjustment_rate=0.1,
        )
        
        new_value = param.adjust(AdjustmentDirection.INCREASE)
        
        assert new_value == 0.6
        assert param.current_value == 0.6
        assert param.total_adjustments == 1
    
    def test_parameter_adjust_decrease(self):
        """Test decreasing parameter."""
        param = StrategyParameter(
            name="test",
            current_value=0.5,
            min_value=0.0,
            max_value=1.0,
            adjustment_rate=0.1,
        )
        
        new_value = param.adjust(AdjustmentDirection.DECREASE)
        
        assert new_value == 0.4
        assert param.current_value == 0.4
    
    def test_parameter_adjust_maintain(self):
        """Test maintaining parameter."""
        param = StrategyParameter(
            name="test",
            current_value=0.5,
            min_value=0.0,
            max_value=1.0,
        )
        
        new_value = param.adjust(AdjustmentDirection.MAINTAIN)
        
        assert new_value == 0.5
    
    def test_parameter_adjust_bounds(self):
        """Test parameter bounds."""
        param = StrategyParameter(
            name="test",
            current_value=0.95,
            min_value=0.0,
            max_value=1.0,
            adjustment_rate=0.1,
        )
        
        # Should not exceed max
        new_value = param.adjust(AdjustmentDirection.INCREASE)
        assert new_value == 1.0  # Capped at max
        
        # Should not go below min
        param.current_value = 0.05
        new_value = param.adjust(AdjustmentDirection.DECREASE)
        assert new_value == 0.0  # Capped at min
    
    def test_parameter_to_dict(self):
        """Test converting parameter to dict."""
        param = StrategyParameter(
            name="test",
            current_value=0.5,
            min_value=0.0,
            max_value=1.0,
        )
        
        d = param.to_dict()
        
        assert d["name"] == "test"
        assert d["current_value"] == 0.5


class TestStrategyOptimizer:
    """Test StrategyOptimizer."""
    
    @pytest.fixture
    def optimizer(self):
        """Create a fresh optimizer."""
        return StrategyOptimizer()
    
    @pytest.fixture
    def collector(self):
        """Create a FeedbackCollector."""
        return FeedbackCollector()
    
    def test_optimizer_creation(self, optimizer):
        """Test creating optimizer."""
        assert optimizer.optimization_strategy == OptimizationStrategy.GRADIENT
        assert "learning_rate" in optimizer.parameters
        assert "exploration_rate" in optimizer.parameters
    
    def test_add_parameter(self, optimizer):
        """Test adding custom parameter."""
        optimizer.add_parameter(
            name="custom_param",
            initial_value=0.5,
            min_value=0.0,
            max_value=1.0,
        )
        
        assert "custom_param" in optimizer.parameters
        assert optimizer.get_parameter("custom_param") == 0.5
    
    def test_set_parameter(self, optimizer):
        """Test setting parameter value."""
        optimizer.set_parameter("learning_rate", 0.3)
        
        assert optimizer.get_parameter("learning_rate") == 0.3
    
    def test_set_parameter_bounds(self, optimizer):
        """Test setting parameter respects bounds."""
        optimizer.set_parameter("learning_rate", 1.0)  # Above max
        
        assert optimizer.get_parameter("learning_rate") == 0.5  # Max value
    
    def test_collect_feedback(self, optimizer, collector):
        """Test collecting feedback."""
        fb = collector.collect_thumbs_up()
        optimizer.collect_feedback(fb)
        
        # Should have collected feedback
        assert len(optimizer._explicit_feedbacks) == 1
    
    def test_collect_implicit(self, optimizer):
        """Test collecting implicit signal."""
        from claw_rl.feedback.implicit import ImplicitSignal, ImplicitSignalType
        
        signal = ImplicitSignal(
            signal_type=ImplicitSignalType.CONTINUATION.value,
            signal="positive",
            confidence=0.6,
            timestamp=datetime.now().isoformat(),
            reason="User continued",
        )
        optimizer.collect_implicit(signal)
        
        assert len(optimizer._implicit_signals) == 1
    
    def test_optimize_positive_feedback(self, optimizer, collector):
        """Test optimization with positive feedback."""
        optimizer.collect_feedback(collector.collect_thumbs_up())
        optimizer.collect_feedback(collector.collect_thumbs_up())
        
        result = optimizer.optimize()
        
        assert result.feedback_count == 2
        assert result.overall_direction == "maintain"  # Positive -> maintain
        assert result.confidence > 0
    
    def test_optimize_negative_feedback(self, optimizer, collector):
        """Test optimization with negative feedback."""
        optimizer.collect_feedback(collector.collect_thumbs_down())
        optimizer.collect_feedback(collector.collect_thumbs_down())
        
        result = optimizer.optimize()
        
        assert result.feedback_count == 2
        assert result.overall_direction == "decrease"  # Negative -> decrease
    
    def test_optimize_mixed_feedback(self, optimizer, collector):
        """Test optimization with mixed feedback."""
        optimizer.collect_feedback(collector.collect_thumbs_up())
        optimizer.collect_feedback(collector.collect_thumbs_down())
        
        result = optimizer.optimize()
        
        assert result.feedback_count == 2
        # Mixed feedback - result depends on weighting
    
    def test_optimize_empty(self, optimizer):
        """Test optimization with no feedback."""
        result = optimizer.optimize()
        
        assert result.feedback_count == 0
        assert result.confidence == 0.0
        assert result.overall_direction == "maintain"
    
    def test_get_optimization_history(self, optimizer, collector):
        """Test getting optimization history."""
        optimizer.collect_feedback(collector.collect_thumbs_up())
        optimizer.optimize()
        
        optimizer.collect_feedback(collector.collect_thumbs_down())
        optimizer.optimize()
        
        history = optimizer.get_optimization_history()
        
        assert len(history) == 2
    
    def test_get_parameter_status(self, optimizer):
        """Test getting parameter status."""
        status = optimizer.get_parameter_status()
        
        assert "learning_rate" in status
        assert "exploration_rate" in status
        assert "current_value" in status["learning_rate"]
    
    def test_get_statistics(self, optimizer, collector):
        """Test getting statistics."""
        optimizer.collect_feedback(collector.collect_thumbs_up())
        optimizer.optimize()
        
        stats = optimizer.get_statistics()
        
        assert "total_optimizations" in stats
        assert stats["total_optimizations"] == 1
    
    def test_reset_parameters(self, optimizer):
        """Test resetting parameters."""
        optimizer.set_parameter("learning_rate", 0.3)
        optimizer.set_parameter("exploration_rate", 0.1)
        
        optimizer.reset_parameters()
        
        # Should be back to defaults
        assert optimizer.get_parameter("learning_rate") == 0.1
        assert optimizer.get_parameter("exploration_rate") == 0.2


class TestOptimizationResult:
    """Test OptimizationResult dataclass."""
    
    def test_result_creation(self):
        """Test creating optimization result."""
        result = OptimizationResult(
            timestamp="2026-04-03T07:00:00",
            feedback_count=5,
            signal_breakdown={"positive": 3, "negative": 2},
            overall_direction="maintain",
            confidence=0.8,
        )
        
        assert result.feedback_count == 5
        assert result.overall_direction == "maintain"
        assert result.confidence == 0.8
    
    def test_result_to_dict(self):
        """Test converting result to dict."""
        result = OptimizationResult(
            timestamp="2026-04-03T07:00:00",
            feedback_count=5,
            signal_breakdown={},
            overall_direction="maintain",
            confidence=0.8,
        )
        
        d = result.to_dict()
        
        assert d["feedback_count"] == 5
        assert d["confidence"] == 0.8


class TestStrategyOptimizerEdgeCases:
    """Test StrategyOptimizer edge cases."""
    
    @pytest.fixture
    def optimizer(self):
        """Create a strategy optimizer."""
        return StrategyOptimizer()
    
    @pytest.fixture
    def collector(self):
        """Create a feedback collector."""
        return FeedbackCollector()
    
    def test_multiple_parameter_adjustments(self, optimizer, collector):
        """Test adjusting multiple parameters."""
        # Collect multiple feedback
        for _ in range(5):
            optimizer.collect_feedback(collector.collect_thumbs_up())
        
        result = optimizer.optimize()
        
        # Should have adjusted parameters
        assert result.feedback_count == 5
    
    def test_parameter_bounds(self, optimizer):
        """Test parameter value bounds."""
        # Try to set parameter beyond max
        optimizer.set_parameter("learning_rate", 1.0)
        
        # Parameter should be clamped to max
        value = optimizer.get_parameter("learning_rate")
        assert 0.0 <= value <= 1.0
    
    def test_optimization_with_low_confidence(self, optimizer, collector):
        """Test optimization with low confidence feedback."""
        # Only one feedback
        optimizer.collect_feedback(collector.collect_thumbs_up())
        
        result = optimizer.optimize()
        
        # Low confidence due to few samples
        assert result.confidence < 1.0
    
    def test_optimization_history_limit(self, optimizer, collector):
        """Test optimization history limit."""
        # Run many optimizations
        for _ in range(20):
            optimizer.collect_feedback(collector.collect_thumbs_up())
            optimizer.optimize()
        
        history = optimizer.get_optimization_history()
        
        # History might be limited
        assert len(history) > 0
    
    def test_reset_with_custom_defaults(self, optimizer):
        """Test reset with custom defaults."""
        # Set custom values
        optimizer.set_parameter("learning_rate", 0.5)
        
        # Reset to defaults
        optimizer.reset_parameters()
        
        # Should be back to original defaults
        assert optimizer.get_parameter("learning_rate") != 0.5
    
    def test_optimization_with_all_positive(self, optimizer, collector):
        """Test optimization with all positive feedback."""
        for _ in range(10):
            optimizer.collect_feedback(collector.collect_thumbs_up())
        
        result = optimizer.optimize()
        
        assert result.feedback_count == 10
        # Should suggest increase or maintain
        assert result.overall_direction in ["increase", "maintain"]
    
    def test_optimization_with_all_negative(self, optimizer, collector):
        """Test optimization with all negative feedback."""
        for _ in range(10):
            optimizer.collect_feedback(collector.collect_thumbs_down())
        
        result = optimizer.optimize()
        
        assert result.feedback_count == 10
        # Should suggest decrease
        assert result.overall_direction in ["decrease", "maintain"]
    
    def test_parameter_status_all(self, optimizer):
        """Test getting all parameter statuses."""
        status = optimizer.get_parameter_status()
        
        # Should have status for all parameters
        assert isinstance(status, dict)
        assert len(status) > 0
    
    def test_collect_feedback_batch(self, optimizer, collector):
        """Test collecting feedback batch."""
        feedbacks = [
            collector.collect_thumbs_up(),
            collector.collect_thumbs_down(),
            collector.collect_thumbs_up(),
        ]
        
        optimizer.collect_feedback_batch(feedbacks)
        
        # Should have collected all feedback
        assert len(optimizer._explicit_feedbacks) == 3
    
    def test_optimize_with_many_feedbacks(self, optimizer, collector):
        """Test optimization with many feedbacks."""
        # Add many feedbacks
        for _ in range(20):
            optimizer.collect_feedback(collector.collect_thumbs_up())
        
        result = optimizer.optimize()
        
        # Should have optimized
        assert result is not None
        assert result.feedback_count == 20
