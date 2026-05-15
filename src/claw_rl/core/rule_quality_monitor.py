"""
Rule Quality Monitor (P0-3)

Monitors and maintains rule quality over time:
1. Effectiveness tracking (success rate, coverage)
2. Rule pruning (low-performing, stale, redundant)
3. Version management (change tracking)

Target: rule effectiveness >70%, auto-pruning
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .fast_learning_loop import Rule, RuleStore


class RuleStatus(Enum):
    """Quality status of a rule."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    STALE = "stale"
    LOW_PERFORMING = "low_performing"
    UNTESTED = "untested"


class PruneReason(Enum):
    """Reason for pruning a rule."""
    LOW_PERFORMANCE = "low_performance"
    STALE = "stale"
    REDUNDANT = "redundant"
    EXPIRED = "expired"
    REPLACED = "replaced"


@dataclass
class RuleEvaluation:
    """Evaluation result for a single rule."""
    rule_id: str
    status: RuleStatus
    effectiveness: float  # 0.0-1.0
    recency: float       # 0.0-1.0 (1 = recently used)
    coverage: float      # 0.0-1.0 (% of relevant contexts)
    should_prune: bool = False
    prune_reason: Optional[PruneReason] = None
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "status": self.status.value,
            "effectiveness": self.effectiveness,
            "recency": self.recency,
            "coverage": self.coverage,
            "should_prune": self.should_prune,
            "prune_reason": self.prune_reason.value if self.prune_reason else None,
            "suggestions": self.suggestions,
        }


@dataclass
class MonitorReport:
    """Full quality monitoring report."""
    timestamp: float
    total_rules: int
    healthy: int
    degraded: int
    stale: int
    low_performing: int
    untested: int
    pruned: int
    average_effectiveness: float
    evaluations: List[RuleEvaluation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "total_rules": self.total_rules,
            "healthy": self.healthy,
            "degraded": self.degraded,
            "stale": self.stale,
            "low_performing": self.low_performing,
            "untested": self.untested,
            "pruned": self.pruned,
            "average_effectiveness": self.average_effectiveness,
            "evaluations": [e.to_dict() for e in self.evaluations[:20]],
        }


class RuleQualityMonitor:
    """Monitor and maintain rule quality over time.

    Continuously evaluates rules for effectiveness, detects degradation,
    and prunes low-performing, stale, or redundant rules.

    Usage:
        monitor = RuleQualityMonitor(rule_store)
        report = monitor.evaluate_rules()
        pruned = monitor.prune_low_performing_rules()
    """

    # Default thresholds
    DEFAULT_EFFECTIVENESS_THRESHOLD = 0.7
    DEFAULT_MIN_APPLICATIONS = 10
    DEFAULT_STALE_DAYS = 30
    DEFAULT_PRUNE_INTERVAL = 3600  # seconds

    def __init__(
        self,
        rule_store: RuleStore,
        effectiveness_threshold: float = DEFAULT_EFFECTIVENESS_THRESHOLD,
        min_applications: int = DEFAULT_MIN_APPLICATIONS,
        stale_days: int = DEFAULT_STALE_DAYS,
        prune_interval: int = DEFAULT_PRUNE_INTERVAL,
    ):
        self.rule_store = rule_store
        self.effectiveness_threshold = effectiveness_threshold
        self.min_applications = min_applications
        self.stale_days = stale_days
        self.prune_interval = prune_interval

        self._last_prune_time = 0.0
        self._prune_history: List[Dict] = []
        self._version_history: Dict[str, List[Dict]] = {}  # rule_id → versions
        self._evaluations_cache: Optional[MonitorReport] = None
        self._cache_time = 0.0

    def evaluate_rules(self) -> MonitorReport:
        """Evaluate all rules and generate quality report.

        Returns:
            MonitorReport with rule status and recommendations
        """
        now = time.time()

        # Use cache if recent (within 60s)
        if self._evaluations_cache and (now - self._cache_time) < 60:
            return self._evaluations_cache

        evaluations: List[RuleEvaluation] = []
        counts = {s: 0 for s in RuleStatus}

        for rule in self.rule_store.get_all():
            eval_result = self._evaluate_rule(rule, now)
            evaluations.append(eval_result)
            counts[eval_result.status] += 1

        # Compute average effectiveness
        avg_eff = 0.0
        if evaluations:
            avg_eff = sum(e.effectiveness for e in evaluations) / len(evaluations)

        report = MonitorReport(
            timestamp=now,
            total_rules=len(evaluations),
            healthy=counts.get(RuleStatus.HEALTHY, 0),
            degraded=counts.get(RuleStatus.DEGRADED, 0),
            stale=counts.get(RuleStatus.STALE, 0),
            low_performing=counts.get(RuleStatus.LOW_PERFORMING, 0),
            untested=counts.get(RuleStatus.UNTESTED, 0),
            pruned=len(self._prune_history),
            average_effectiveness=avg_eff,
            evaluations=evaluations,
        )

        self._evaluations_cache = report
        self._cache_time = now

        return report

    def prune_rules(self) -> List[str]:
        """Prune low-performing and stale rules.

        Returns:
            List of pruned rule IDs
        """
        now = time.time()

        # Rate-limit pruning
        if now - self._last_prune_time < self.prune_interval:
            return []

        report = self.evaluate_rules()
        pruned_ids: List[str] = []

        for eval_result in report.evaluations:
            if eval_result.should_prune:
                # Record before pruning
                rule = self.rule_store.get(eval_result.rule_id)
                if rule:
                    self._record_version(rule, "pruned")
                    self._prune_history.append({
                        "rule_id": eval_result.rule_id,
                        "reason": eval_result.prune_reason.value if eval_result.prune_reason else "unknown",
                        "timestamp": now,
                        "directive": rule.directive,
                        "effectiveness": eval_result.effectiveness,
                    })

                self.rule_store.remove(eval_result.rule_id)
                pruned_ids.append(eval_result.rule_id)

        self._last_prune_time = now
        # Clear cache after pruning
        self._evaluations_cache = None

        return pruned_ids

    def get_rule_status(self, rule_id: str) -> Optional[RuleEvaluation]:
        """Get quality evaluation for a specific rule."""
        rule = self.rule_store.get(rule_id)
        if not rule:
            return None
        return self._evaluate_rule(rule, time.time())

    def get_top_performers(self, top_k: int = 10) -> List[Rule]:
        """Get top-performing rules by effectiveness."""
        report = self.evaluate_rules()
        evaluations = [e for e in report.evaluations if e.status in (RuleStatus.HEALTHY, RuleStatus.DEGRADED)]
        evaluations.sort(key=lambda e: e.effectiveness, reverse=True)

        top_rules = []
        for e in evaluations[:top_k]:
            rule = self.rule_store.get(e.rule_id)
            if rule:
                top_rules.append(rule)
        return top_rules

    def get_prune_history(self, limit: int = 20) -> List[Dict]:
        """Get recent pruning history."""
        return self._prune_history[-limit:]

    def record_validated_usage(self, rule_id: str, successful: bool):
        """Record a validated usage of a rule.

        Call this when you have confirmed whether a rule was effective.
        This updates the rule's metrics and triggers quality re-evaluation.

        Args:
            rule_id: Rule identifier
            successful: Whether the rule was effective
        """
        rule = self.rule_store.get(rule_id)
        if not rule:
            return

        rule.applied_count += 1
        rule.last_applied = time.time()
        if successful:
            rule.success_count += 1

        # Record version history
        self._record_version(rule, "used")

    # ── Private methods ────────────────────────────────────────────────────────

    def _evaluate_rule(self, rule: Rule, now: float) -> RuleEvaluation:
        """Evaluate a single rule's quality.

        Returns:
            RuleEvaluation with status and recommendations
        """
        effectiveness = self._compute_effectiveness(rule)
        recency = self._compute_recency(rule, now)
        coverage = self._compute_coverage(rule)
        status = self._determine_status(rule, effectiveness, recency)
        should_prune, reason = self._should_prune(
            rule, effectiveness, recency
        )
        suggestions = self._generate_suggestions(rule, status, effectiveness)

        return RuleEvaluation(
            rule_id=rule.rule_id,
            status=status,
            effectiveness=effectiveness,
            recency=recency,
            coverage=coverage,
            should_prune=should_prune,
            prune_reason=reason,
            suggestions=suggestions,
        )

    def _compute_effectiveness(self, rule: Rule) -> float:
        """Compute effectiveness score (0.0-1.0).

        Factors:
        - success_rate: % of applications that succeeded
        - confidence: rule confidence
        """
        success_rate = rule.success_rate

        # Blend success rate with confidence
        if rule.applied_count == 0:
            return rule.confidence * 0.5  # Half of confidence for untested rules

        # More weight to success rate as we get more data
        data_weight = min(1.0, rule.applied_count / self.min_applications)
        return data_weight * success_rate + (1 - data_weight) * rule.confidence * 0.7

    def _compute_recency(self, rule: Rule, now: float) -> float:
        """Compute recency score (0.0-1.0, 1 = very recent)."""
        if rule.last_applied is None:
            if rule.applied_count == 0:
                return 0.0
            # Created-recently rules get partial recency
            age_days = (now - rule.created_at) / 86400
            return max(0.0, 1.0 - age_days / self.stale_days)

        hours_since = (now - rule.last_applied) / 3600
        # Exponential decay with ~72h half-life
        import math
        return math.exp(-math.log(2) * hours_since / 72)

    def _compute_coverage(self, rule: Rule) -> float:
        """Estimate rule coverage (% of relevant contexts)."""
        # Simple heuristic: more applications → potentially wider coverage
        if rule.applied_count == 0:
            return 0.0
        return min(1.0, rule.applied_count / 50.0)

    def _determine_status(
        self, rule: Rule, effectiveness: float, recency: float
    ) -> RuleStatus:
        """Determine rule quality status."""
        if rule.applied_count == 0:
            # Check if created recently enough
            age_days = (time.time() - rule.created_at) / 86400
            if age_days > self.stale_days:
                return RuleStatus.STALE
            return RuleStatus.UNTESTED

        if effectiveness < self.effectiveness_threshold:
            return RuleStatus.LOW_PERFORMING

        if recency < 0.2:
            return RuleStatus.STALE

        if effectiveness < self.effectiveness_threshold + 0.1:
            return RuleStatus.DEGRADED

        return RuleStatus.HEALTHY

    def _should_prune(
        self, rule: Rule, effectiveness: float, recency: float
    ) -> tuple:
        """Decide if a rule should be pruned."""
        # Not enough data to decide
        if rule.applied_count < self.min_applications:
            # But if it's very stale, prune anyway
            if recency < 0.05 and effectiveness < 0.3:
                return True, PruneReason.STALE
            return False, None

        # Low performance
        if effectiveness < self.effectiveness_threshold:
            return True, PruneReason.LOW_PERFORMANCE

        # Very stale
        if recency < 0.05:
            return True, PruneReason.STALE

        return False, None

    def _generate_suggestions(
        self, rule: Rule, status: RuleStatus, effectiveness: float
    ) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []

        if status == RuleStatus.LOW_PERFORMING:
            suggestions.append(
                f"Review directive '{rule.directive[:60]}...' - "
                f"effectiveness {effectiveness:.1%}"
            )

        if status == RuleStatus.STALE:
            suggestions.append(
                f"Rule not used recently - consider refreshing or removing"
            )

        if status == RuleStatus.UNTESTED:
            suggestions.append(
                f"Rule needs more applications for evaluation "
                f"(current: {rule.applied_count}/{self.min_applications})"
            )

        if status == RuleStatus.DEGRADED:
            suggestions.append(
                f"Effectiveness declining ({effectiveness:.1%}) - "
                f"check for context changes"
            )

        return suggestions

    def _record_version(self, rule: Rule, event: str):
        """Record a version snapshot for change tracking."""
        now = time.time()
        self._version_history.setdefault(rule.rule_id, []).append({
            "event": event,
            "timestamp": now,
            "applied_count": rule.applied_count,
            "success_count": rule.success_count,
            "confidence": rule.confidence,
        })

        # Limit history per rule
        if len(self._version_history[rule.rule_id]) > 50:
            self._version_history[rule.rule_id] = \
                self._version_history[rule.rule_id][-30:]


__all__ = [
    'RuleQualityMonitor',
    'RuleEvaluation',
    'MonitorReport',
    'RuleStatus',
    'PruneReason',
]
