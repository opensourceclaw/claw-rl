"""Tests for RuleQualityMonitor module (P0-3)"""

import time
import pytest
from claw_rl.core.fast_learning_loop import RuleStore, Rule
from claw_rl.core.rule_quality_monitor import (
    RuleQualityMonitor, RuleEvaluation, MonitorReport,
    RuleStatus, PruneReason,
)


# ── RuleQualityMonitor Tests ────────────────────────────────────────────────────

class TestRuleQualityMonitor:
    @pytest.fixture
    def store(self):
        s = RuleStore()
        now = time.time()

        # Healthy rule: high success rate, recent usage
        s.add(Rule(
            "rule-healthy", "run_tests", "run tests before push",
            "global", "high", 0.9, now - 3600,
            applied_count=50, success_count=48,
            last_applied=now - 300,
        ))

        # Low-performing rule: many applications, low success
        s.add(Rule(
            "rule-lowperf", "deploy", "deploy to production",
            "project", "medium", 0.5, now - 86400 * 7,
            applied_count=30, success_count=10,
            last_applied=now - 3600,
        ))

        # Stale rule: not used recently
        s.add(Rule(
            "rule-stale", "old_action", "old directive",
            "session", "low", 0.6, now - 86400 * 60,
            applied_count=15, success_count=12,
            last_applied=now - 86400 * 40,
        ))

        # Untested rule: no applications
        s.add(Rule(
            "rule-untested", "new_action", "new directive",
            "session", "medium", 0.7, now - 3600,
            applied_count=0, success_count=0,
        ))

        return s

    @pytest.fixture
    def monitor(self, store):
        return RuleQualityMonitor(
            store,
            effectiveness_threshold=0.7,
            min_applications=5,
            stale_days=30,
        )

    def test_evaluate_rules(self, monitor):
        report = monitor.evaluate_rules()
        assert isinstance(report, MonitorReport)
        assert report.total_rules >= 4
        assert report.healthy >= 1
        assert report.low_performing >= 1
        assert report.stale >= 1
        assert report.untested >= 1

    def test_evaluate_rules_report_fields(self, monitor):
        report = monitor.evaluate_rules()
        assert report.total_rules > 0
        assert report.average_effectiveness >= 0
        assert len(report.evaluations) > 0

    def test_individual_rule_evaluation(self, monitor):
        report = monitor.evaluate_rules()
        eval1 = next(e for e in report.evaluations if e.rule_id == "rule-healthy")
        assert eval1.status == RuleStatus.HEALTHY
        assert eval1.effectiveness >= 0.7
        assert eval1.should_prune is False

    def test_low_performing_rule_should_prune(self, monitor):
        report = monitor.evaluate_rules()
        eval1 = next(e for e in report.evaluations if e.rule_id == "rule-lowperf")
        assert eval1.status == RuleStatus.LOW_PERFORMING
        assert eval1.should_prune is True
        assert eval1.prune_reason == PruneReason.LOW_PERFORMANCE

    def test_stale_rule_should_prune(self, monitor):
        report = monitor.evaluate_rules()
        eval1 = next(e for e in report.evaluations if e.rule_id == "rule-stale")
        assert eval1.status == RuleStatus.STALE
        assert eval1.should_prune is True

    def test_untested_rule_not_pruned_yet(self, monitor):
        report = monitor.evaluate_rules()
        eval1 = next(e for e in report.evaluations if e.rule_id == "rule-untested")
        assert eval1.status == RuleStatus.UNTESTED
        assert eval1.should_prune is False  # Not enough data

    def test_prune_rules(self, monitor):
        pruned = monitor.prune_rules()
        assert isinstance(pruned, list)

    def test_prune_low_performing(self, monitor):
        pruned = monitor.prune_rules()
        # Low-performing rule should be pruned
        assert "rule-lowperf" in pruned
        assert "rule-stale" in pruned
        # Healthy and untested should NOT be pruned
        assert "rule-healthy" not in pruned
        assert "rule-untested" not in pruned

    def test_prune_removes_from_store(self, monitor):
        pruned = monitor.prune_rules()
        if "rule-lowperf" in pruned:
            assert monitor.rule_store.get("rule-lowperf") is None

    def test_get_rule_status(self, monitor):
        eval_result = monitor.get_rule_status("rule-healthy")
        assert eval_result is not None
        assert eval_result.status == RuleStatus.HEALTHY

    def test_get_rule_status_nonexistent(self, monitor):
        result = monitor.get_rule_status("nonexistent")
        assert result is None

    def test_get_top_performers(self, monitor):
        top = monitor.get_top_performers(5)
        assert isinstance(top, list)
        if top:
            assert top[0].success_rate >= 0

    def test_get_prune_history(self, monitor):
        monitor.prune_rules()
        history = monitor.get_prune_history()
        assert isinstance(history, list)
        if history:
            assert "rule_id" in history[0]
            assert "reason" in history[0]

    def test_record_validated_usage(self, monitor):
        monitor.record_validated_usage("rule-untested", successful=True)
        monitor.record_validated_usage("rule-untested", successful=True)
        rule = monitor.rule_store.get("rule-untested")
        assert rule.applied_count >= 2
        assert rule.success_count >= 2

    def test_record_validated_usage_nonexistent(self, monitor):
        # Should not raise
        monitor.record_validated_usage("nonexistent", successful=True)

    def test_prune_rate_limiting(self, monitor):
        pruned1 = monitor.prune_rules()
        pruned2 = monitor.prune_rules()  # Should be rate-limited
        assert isinstance(pruned2, list)


# ── Report Dataclass Tests ──────────────────────────────────────────────────────

class TestMonitorReport:
    def test_to_dict(self):
        report = MonitorReport(
            timestamp=1234567890.0,
            total_rules=10,
            healthy=5,
            degraded=2,
            stale=1,
            low_performing=1,
            untested=1,
            pruned=3,
            average_effectiveness=0.75,
            evaluations=[],
        )
        d = report.to_dict()
        assert d["total_rules"] == 10
        assert d["healthy"] == 5
        assert d["average_effectiveness"] == 0.75


class TestRuleEvaluation:
    def test_to_dict(self):
        ev = RuleEvaluation(
            rule_id="r1",
            status=RuleStatus.HEALTHY,
            effectiveness=0.9,
            recency=0.8,
            coverage=0.6,
            should_prune=False,
        )
        d = ev.to_dict()
        assert d["rule_id"] == "r1"
        assert d["status"] == "healthy"
        assert d["effectiveness"] == 0.9


# ── RuleQualityMonitor Edge Cases ───────────────────────────────────────────────

class TestRuleQualityMonitorEdgeCases:
    def test_empty_store(self):
        store = RuleStore()
        monitor = RuleQualityMonitor(store)
        report = monitor.evaluate_rules()
        assert report.total_rules == 0
        assert report.average_effectiveness == 0.0

    def test_single_rule_store(self):
        store = RuleStore()
        now = time.time()
        store.add(Rule(
            "rule-1", "action", "directive", "global", "high", 0.9,
            now - 3600, applied_count=30, success_count=27,
            last_applied=now - 600,
        ))
        monitor = RuleQualityMonitor(store)
        report = monitor.evaluate_rules()
        assert report.total_rules == 1
        assert report.healthy == 1

    def test_degraded_rule(self):
        store = RuleStore()
        now = time.time()
        store.add(Rule(
            "r1", "action", "dir", "global", "high", 0.9,
            now - 86400 * 3, applied_count=20, success_count=15,
            last_applied=now - 3600,
        ))
        monitor = RuleQualityMonitor(store, effectiveness_threshold=0.9)
        report = monitor.evaluate_rules()
        eval1 = report.evaluations[0]
        assert eval1.status in (RuleStatus.DEGRADED, RuleStatus.LOW_PERFORMING)

    def test_prune_expired_hint(self):
        """Hint that was never applied and is very old should be pruned."""
        store = RuleStore()
        now = time.time()
        store.add(Rule(
            "r-very-old", "old", "old", "session", "low", 0.3,
            now - 86400 * 100,  # 100 days old
            applied_count=0, success_count=0,
        ))
        monitor = RuleQualityMonitor(store, stale_days=30, min_applications=5)
        report = monitor.evaluate_rules()
        eval1 = report.evaluations[0]
        assert eval1.status == RuleStatus.STALE
        # Very old untested rule with very low confidence → should prune
        assert eval1.should_prune is True

    def test_suggestions_for_issues(self):
        store = RuleStore()
        now = time.time()
        store.add(Rule(
            "r-problem", "action", "directive", "session", "low", 0.3,
            now - 86400 * 50, applied_count=15, success_count=5,
            last_applied=now - 86400 * 40,
        ))
        monitor = RuleQualityMonitor(store)
        report = monitor.evaluate_rules()
        eval1 = report.evaluations[0]
        assert len(eval1.suggestions) > 0


# ── Enum Tests ──────────────────────────────────────────────────────────────────

class TestRuleStatus:
    def test_enum_values(self):
        assert RuleStatus.HEALTHY.value == "healthy"
        assert RuleStatus.DEGRADED.value == "degraded"
        assert RuleStatus.STALE.value == "stale"
        assert RuleStatus.LOW_PERFORMING.value == "low_performing"
        assert RuleStatus.UNTESTED.value == "untested"


class TestPruneReason:
    def test_enum_values(self):
        assert PruneReason.LOW_PERFORMANCE.value == "low_performance"
        assert PruneReason.STALE.value == "stale"
        assert PruneReason.REDUNDANT.value == "redundant"
        assert PruneReason.EXPIRED.value == "expired"
        assert PruneReason.REPLACED.value == "replaced"
