"""
Fast Learning Loop (P0-3)

Immediate rule application with validation and conflict resolution.
Extends LearningLoop with faster feedback integration and rule quality tracking.

Pipeline:
1. Validate hint quality
2. Check for conflicts with existing rules
3. Apply rule immediately
4. Track effectiveness over time

Target: learning latency <50ms, rule effectiveness >70%
"""

import time
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from claw_rl.feedback.enhanced_opd import Hint, Priority


@dataclass
class Rule:
    """A learning rule with metadata."""
    rule_id: str
    action: str
    directive: str
    scope: str
    priority: str
    confidence: float
    created_at: float
    applied_count: int = 0
    success_count: int = 0
    last_applied: Optional[float] = None
    hints_source: List[str] = field(default_factory=list)  # Source hint directives

    @property
    def success_rate(self) -> float:
        if self.applied_count == 0:
            return 0.0
        return self.success_count / self.applied_count

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "action": self.action,
            "directive": self.directive,
            "scope": self.scope,
            "priority": self.priority,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "applied_count": self.applied_count,
            "success_count": self.success_count,
            "last_applied": self.last_applied,
            "success_rate": self.success_rate,
        }


@dataclass
class ApplyResult:
    """Result of applying a hint as a rule."""
    success: bool
    rule_id: Optional[str] = None
    created: bool = False
    updated: bool = False
    conflict_resolved: bool = False
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "rule_id": self.rule_id,
            "created": self.created,
            "updated": self.updated,
            "conflict_resolved": self.conflict_resolved,
            "reason": self.reason,
        }


class RuleStore:
    """In-memory rule storage with indexing."""

    def __init__(self):
        self._rules: Dict[str, Rule] = {}
        self._by_action: Dict[str, List[str]] = {}  # action → rule_ids

    def add(self, rule: Rule):
        self._rules[rule.rule_id] = rule
        self._by_action.setdefault(rule.action, []).append(rule.rule_id)

    def get(self, rule_id: str) -> Optional[Rule]:
        return self._rules.get(rule_id)

    def find_by_action(self, action: str) -> List[Rule]:
        ids = self._by_action.get(action, [])
        return [self._rules[rid] for rid in ids if rid in self._rules]

    def find_conflicts(self, hint: Hint) -> List[Rule]:
        """Find rules that conflict with a hint."""
        conflicts = []
        existing = self.find_by_action(hint.action)
        for rule in existing:
            # Check for contradictory directives
            if self._are_contradictory(rule.directive, hint.directive):
                conflicts.append(rule)
        return conflicts

    def get_all(self) -> List[Rule]:
        return list(self._rules.values())

    def remove(self, rule_id: str):
        rule = self._rules.pop(rule_id, None)
        if rule and rule.action in self._by_action:
            self._by_action[rule.action] = [
                rid for rid in self._by_action[rule.action] if rid != rule_id
            ]

    def size(self) -> int:
        return len(self._rules)

    @staticmethod
    def _are_contradictory(dir1: str, dir2: str) -> bool:
        """Check if two directives contradict each other."""
        d1_lower = dir1.lower()
        d2_lower = dir2.lower()

        # Negation patterns (EN + ZH)
        negation_patterns = ("avoid", "don't", "do not", "不要", "避免", "不能", "不应该", "不该", "禁止")
        neg1 = any(kw in d1_lower for kw in negation_patterns)
        neg2 = any(kw in d2_lower for kw in negation_patterns)

        # If one is positive and one negative, check content overlap
        if neg1 != neg2:
            # Extract core content by stripping negation words
            content1 = d1_lower
            content2 = d2_lower
            for kw in negation_patterns:
                content1 = content1.replace(kw, "").strip()
                content2 = content2.replace(kw, "").strip()

            # Split content into words (handle both EN and CJK)
            words1 = set(content1.split())
            words2 = set(content2.split())

            # Also add CJK bigram comparison for Chinese text
            import re
            cjk1 = ''.join(re.findall(r'[\u4e00-\u9fff]', content1))
            cjk2 = ''.join(re.findall(r'[\u4e00-\u9fff]', content2))

            overlap = len(words1 & words2)

            # Check CJK overlap (at least 2 chars in common)
            if cjk1 and cjk2:
                cjk_overlap = len(set(cjk1) & set(cjk2))
                if cjk_overlap >= 2:
                    return True

            if overlap > 0:
                return True

        return False


class RuleValidator:
    """Validate hints before learning."""

    MIN_ACTIONABILITY = 0.4
    MIN_CONFIDENCE = 0.3
    MIN_DIRECTIVE_LENGTH = 3

    def validate(self, hint: Hint) -> bool:
        """Validate if a hint is worth learning.

        Checks:
        - Actionability score
        - Confidence level
        - Directive completeness
        - Action validity

        Args:
            hint: Hint to validate

        Returns:
            True if valid, False otherwise
        """
        if hint.actionability < self.MIN_ACTIONABILITY:
            return False
        if hint.confidence < self.MIN_CONFIDENCE:
            return False
        if len(hint.directive.strip()) < self.MIN_DIRECTIVE_LENGTH:
            return False
        if not hint.action or len(hint.action.strip()) < 2:
            return False
        return True

    def validate_rules(self, rules: List[Rule]) -> List[Rule]:
        """Filter valid rules."""
        return [r for r in rules if self._is_valid_rule(r)]

    @staticmethod
    def _is_valid_rule(rule: Rule) -> bool:
        if not rule.directive or len(rule.directive.strip()) < 3:
            return False
        if rule.confidence < 0.2:
            return False
        return True


class ConflictResolver:
    """Resolve conflicts between new hints and existing rules."""

    def resolve(self, hint: Hint, conflicts: List[Rule]) -> Hint:
        """Resolve conflicts between a new hint and existing rules.

        Strategy:
        - Higher confidence wins
        - Higher actionability wins
        - If tie, keep the newer one

        Args:
            hint: New hint being applied
            conflicts: Conflicting existing rules

        Returns:
            Modified hint (may be unchanged if new hint wins)
        """
        if not conflicts:
            return hint

        # Find the strongest conflicting rule
        strongest = max(conflicts, key=lambda r: r.confidence * 0.6 + r.success_rate * 0.4)

        # Compare confidence-weighted scores
        hint_score = hint.confidence * 0.6 + hint.actionability * 0.4
        rule_score = strongest.confidence * 0.6 + strongest.success_rate * 0.4

        if hint_score > rule_score:
            # New hint is better, return unchanged (old rule should be demoted)
            return hint
        else:
            # Existing rule is better, reduce new hint priority
            if hint.priority == Priority.HIGH:
                hint = Hint(
                    action=hint.action,
                    directive=hint.directive,
                    scope=hint.scope,
                    priority=Priority.MEDIUM,
                    actionability=hint.actionability * 0.8,
                    confidence=hint.confidence * 0.8,
                    examples=hint.examples,
                )
        return hint

    def resolve_all(self, hints: List[Hint], rule_store: RuleStore) -> List[Hint]:
        """Resolve conflicts for all hints at once."""
        resolved = []
        for hint in hints:
            conflicts = rule_store.find_conflicts(hint)
            resolved.append(self.resolve(hint, conflicts))
        return resolved


class FastLearningLoop:
    """Immediate rule application with validation and conflict resolution.

    Process:
    1. Validate hint quality
    2. Check for conflicts with existing rules
    3. Apply rule to store
    4. Track effectiveness metrics

    Usage:
        store = RuleStore()
        validator = RuleValidator()
        resolver = ConflictResolver()
        loop = FastLearningLoop(store, validator, resolver)
        result = loop.apply_hint(hint)
    """

    def __init__(
        self,
        rule_store: Optional[RuleStore] = None,
        validator: Optional[RuleValidator] = None,
        conflict_resolver: Optional[ConflictResolver] = None,
    ):
        self.rule_store = rule_store or RuleStore()
        self.validator = validator or RuleValidator()
        self.conflict_resolver = conflict_resolver or ConflictResolver()

        self._stats = {
            "applied": 0,
            "rejected": 0,
            "updated": 0,
            "conflicts_resolved": 0,
        }

    def apply_hint(self, hint: Hint) -> ApplyResult:
        """Apply hint immediately with validation and conflict checking.

        Args:
            hint: Hint to apply

        Returns:
            ApplyResult with status and rule details
        """
        t0 = time.perf_counter()

        # Step 1: Validate
        if not self.validator.validate(hint):
            self._stats["rejected"] += 1
            return ApplyResult(success=False, reason="validation_failed")

        # Step 2: Check conflicts
        conflicts = self.rule_store.find_conflicts(hint)
        if conflicts:
            resolved_hint = self.conflict_resolver.resolve(hint, conflicts)
            self._stats["conflicts_resolved"] += 1
        else:
            resolved_hint = hint

        # Step 3: Generate rule ID and create rule
        rule_id = self._generate_rule_id(resolved_hint)
        now = time.time()

        # Check if similar rule already exists
        existing = self.rule_store.get(rule_id)
        if existing:
            # Update existing rule with new information
            existing.confidence = max(existing.confidence, resolved_hint.confidence)
            existing.hints_source.append(resolved_hint.directive)
            if len(existing.hints_source) > 10:
                existing.hints_source = existing.hints_source[-10:]
            self._stats["updated"] += 1

            elapsed_ms = (time.perf_counter() - t0) * 1000
            return ApplyResult(
                success=True,
                rule_id=rule_id,
                updated=True,
                conflict_resolved=bool(conflicts),
                reason=f"Updated existing rule ({elapsed_ms:.1f}ms)",
            )

        # Create new rule
        rule = Rule(
            rule_id=rule_id,
            action=resolved_hint.action,
            directive=resolved_hint.directive,
            scope=resolved_hint.scope.value,
            priority=resolved_hint.priority.value,
            confidence=resolved_hint.confidence,
            created_at=now,
            hints_source=[resolved_hint.directive],
        )

        self.rule_store.add(rule)

        # Step 4: Track
        self._track_effectiveness(rule)

        self._stats["applied"] += 1
        elapsed_ms = (time.perf_counter() - t0) * 1000

        return ApplyResult(
            success=True,
            rule_id=rule_id,
            created=True,
            conflict_resolved=bool(conflicts),
            reason=f"Rule created ({elapsed_ms:.1f}ms)",
        )

    def apply_hints(self, hints: List[Hint]) -> List[ApplyResult]:
        """Apply multiple hints as rules.

        Args:
            hints: List of Hint objects

        Returns:
            List of ApplyResult objects
        """
        # Resolve conflicts first across all hints
        resolved_hints = self.conflict_resolver.resolve_all(hints, self.rule_store)

        results = []
        for hint in resolved_hints:
            result = self.apply_hint(hint)
            results.append(result)
        return results

    def record_feedback(self, rule_id: str, successful: bool):
        """Record success/failure feedback for a rule.

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

    def _track_effectiveness(self, rule: Rule):
        """Initialize effectiveness tracking for a new rule."""
        # Initialize with zero counts
        rule.applied_count = 0
        rule.success_count = 0
        rule.last_applied = None

    def get_statistics(self) -> Dict:
        """Get learning loop statistics."""
        return {
            **self._stats,
            "store_size": self.rule_store.size(),
            "total_rules": self.rule_store.size(),
        }

    @staticmethod
    def _generate_rule_id(hint: Hint) -> str:
        """Generate a unique rule ID from a hint."""
        content = f"{hint.action}:{hint.directive}"
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"rule_{hash_suffix}"


__all__ = [
    'FastLearningLoop',
    'RuleStore',
    'RuleValidator',
    'ConflictResolver',
    'Rule',
    'ApplyResult',
]
