"""
Tests for claw-rl Visualization Module (v2.4.0)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from datetime import datetime


class TestRuleQuality:
    """Test RuleQuality enum"""

    def test_quality_values(self):
        from claw_rl.visualization import RuleQuality
        assert RuleQuality.HIGH.value == "high"
        assert RuleQuality.MEDIUM.value == "medium"
        assert RuleQuality.LOW.value == "low"
        assert RuleQuality.UNKNOWN.value == "unknown"


class TestRuleMetrics:
    """Test RuleMetrics dataclass"""

    def test_creation(self):
        from claw_rl.visualization import RuleMetrics, RuleQuality
        metrics = RuleMetrics(
            rule_id="rule-1",
            confidence=0.8,
            usage_count=10,
            success_rate=0.9
        )
        assert metrics.rule_id == "rule-1"
        assert metrics.confidence == 0.8
        assert metrics.usage_count == 10


class TestRuleVisualizer:
    """Test RuleVisualizer"""

    @pytest.fixture
    def visualizer(self):
        from claw_rl.visualization import get_visualizer
        import claw_rl.visualization as viz_module
        viz_module._visualizer = None
        return get_visualizer()

    def test_register_rule(self, visualizer):
        """Test rule registration"""
        visualizer.register_rule("rule-1", 0.5)
        metrics = visualizer.get_rule_metrics("rule-1")
        assert metrics is not None
        assert metrics.rule_id == "rule-1"
        assert metrics.confidence == 0.5

    def test_update_metrics_success(self, visualizer):
        """Test updating metrics with success"""
        visualizer.register_rule("rule-1", 0.5)
        visualizer.update_metrics("rule-1", success=True)

        metrics = visualizer.get_rule_metrics("rule-1")
        assert metrics.usage_count == 1
        assert metrics.success_rate == 1.0

    def test_update_metrics_failure(self, visualizer):
        """Test updating metrics with failure"""
        visualizer.register_rule("rule-1", 0.5)
        visualizer.update_metrics("rule-1", success=False)

        metrics = visualizer.get_rule_metrics("rule-1")
        assert metrics.usage_count == 1
        assert metrics.success_rate == 0.0

    def test_quality_summary(self, visualizer):
        """Test quality summary"""
        visualizer.register_rule("rule-1", 0.5)
        visualizer.register_rule("rule-2", 0.7)

        # Update enough to get quality
        for _ in range(6):
            visualizer.update_metrics("rule-1", success=True)

        summary = visualizer.get_quality_summary()
        assert "high" in summary
        assert "unknown" in summary

    def test_top_rules(self, visualizer):
        """Test getting top rules"""
        visualizer.register_rule("rule-1", 0.5)
        visualizer.register_rule("rule-2", 0.8)
        visualizer.register_rule("rule-3", 0.6)

        top = visualizer.get_top_rules(2)
        assert len(top) == 2
        assert top[0].rule_id == "rule-2"  # Highest confidence

    def test_render_text_report(self, visualizer):
        """Test text report rendering"""
        visualizer.register_rule("rule-1", 0.7)

        report = visualizer.render_text_report()
        assert "Rule Visualization Report" in report
        assert "rule-1" in report
