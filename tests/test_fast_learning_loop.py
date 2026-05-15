"""Tests for FastLearningLoop module (P0-3)"""

import pytest
from claw_rl.feedback.enhanced_opd import ImprovedOPDExtractor, Hint, Priority, Scope
from claw_rl.core.fast_learning_loop import (
    FastLearningLoop, RuleStore, RuleValidator, ConflictResolver,
    Rule, ApplyResult,
)


# ── RuleStore Tests ─────────────────────────────────────────────────────────────

class TestRuleStore:
    @pytest.fixture
    def store(self):
        return RuleStore()

    def test_add_and_get(self, store):
        rule = Rule(
            rule_id="rule-1", action="test_action",
            directive="do test thing", scope="session",
            priority="high", confidence=0.8, created_at=1234567890.0,
        )
        store.add(rule)
        retrieved = store.get("rule-1")
        assert retrieved is not None
        assert retrieved.rule_id == "rule-1"

    def test_find_by_action(self, store):
        store.add(Rule("r1", "create", "do X", "session", "high", 0.8, 0))
        store.add(Rule("r2", "delete", "do Y", "session", "medium", 0.7, 0))
        store.add(Rule("r3", "create", "do Z", "global", "low", 0.6, 0))

        found = store.find_by_action("create")
        assert len(found) == 2

    def test_find_conflicts(self, store):
        store.add(Rule("r1", "create", "do this", "session", "high", 0.8, 0))
        hint = Hint(action="create", directive="avoid this", scope=Scope.SESSION,
                     priority=Priority.HIGH, actionability=0.7, confidence=0.7)
        conflicts = store.find_conflicts(hint)
        assert len(conflicts) >= 1

    def test_no_conflict_different_action(self, store):
        store.add(Rule("r1", "create", "do X", "session", "high", 0.8, 0))
        hint = Hint(action="delete", directive="do X", scope=Scope.SESSION,
                     priority=Priority.HIGH, actionability=0.7, confidence=0.7)
        conflicts = store.find_conflicts(hint)
        assert len(conflicts) == 0

    def test_no_conflict_same_direction(self, store):
        store.add(Rule("r1", "create", "do this", "session", "high", 0.8, 0))
        hint = Hint(action="create", directive="also do this", scope=Scope.SESSION,
                     priority=Priority.HIGH, actionability=0.7, confidence=0.7)
        conflicts = store.find_conflicts(hint)
        assert len(conflicts) == 0  # Same direction, not contradictory

    def test_get_all(self, store):
        store.add(Rule("r1", "a", "x", "s", "h", 0.8, 0))
        store.add(Rule("r2", "b", "y", "s", "m", 0.7, 0))
        assert len(store.get_all()) == 2

    def test_remove(self, store):
        store.add(Rule("r1", "a", "x", "s", "h", 0.8, 0))
        store.remove("r1")
        assert store.get("r1") is None
        assert store.find_by_action("a") == []

    def test_size(self, store):
        assert store.size() == 0
        store.add(Rule("r1", "a", "x", "s", "h", 0.8, 0))
        assert store.size() == 1

    def test_remove_nonexistent(self, store):
        store.remove("nonexistent")  # Should not raise


# ── Rule Dataclass Tests ────────────────────────────────────────────────────────

class TestRule:
    def test_success_rate_zero_applications(self):
        rule = Rule("id", "action", "directive", "scope", "high", 0.8, 0)
        assert rule.success_rate == 0.0

    def test_success_rate_half(self):
        rule = Rule("id", "action", "dir", "scope", "high", 0.8, 0,
                    applied_count=10, success_count=5)
        assert rule.success_rate == 0.5

    def test_success_rate_all(self):
        rule = Rule("id", "action", "dir", "scope", "high", 0.8, 0,
                    applied_count=10, success_count=10)
        assert rule.success_rate == 1.0

    def test_to_dict(self):
        rule = Rule("id", "action", "dir", "scope", "high", 0.8, 100.0)
        d = rule.to_dict()
        assert d["rule_id"] == "id"
        assert d["applied_count"] == 0
        assert d["success_rate"] == 0.0


# ── RuleValidator Tests ─────────────────────────────────────────────────────────

class TestRuleValidator:
    @pytest.fixture
    def validator(self):
        return RuleValidator()

    def test_valid_hint(self, validator):
        hint = Hint(
            action="create_file", directive="put file in src/",
            scope=Scope.PROJECT, priority=Priority.HIGH,
            actionability=0.7, confidence=0.7,
        )
        assert validator.validate(hint) is True

    def test_low_actionability(self, validator):
        hint = Hint(
            action="test", directive="something",
            scope=Scope.CONTEXT, priority=Priority.LOW,
            actionability=0.2, confidence=0.8,
        )
        assert validator.validate(hint) is False

    def test_low_confidence(self, validator):
        hint = Hint(
            action="test", directive="do something specific",
            scope=Scope.CONTEXT, priority=Priority.LOW,
            actionability=0.7, confidence=0.1,
        )
        assert validator.validate(hint) is False

    def test_empty_directive(self, validator):
        hint = Hint(
            action="test", directive="ab",  # Too short
            scope=Scope.CONTEXT, priority=Priority.LOW,
            actionability=0.7, confidence=0.7,
        )
        assert validator.validate(hint) is False

    def test_empty_action(self, validator):
        hint = Hint(
            action="", directive="some directive",
            scope=Scope.CONTEXT, priority=Priority.LOW,
            actionability=0.7, confidence=0.7,
        )
        assert validator.validate(hint) is False


# ── ConflictResolver Tests ──────────────────────────────────────────────────────

class TestConflictResolver:
    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    @pytest.fixture
    def store(self):
        s = RuleStore()
        s.add(Rule("r1", "create", "avoid X", "session", "high", 0.9, 0,
                   applied_count=100, success_count=95))
        return s

    def test_resolve_no_conflicts(self, resolver):
        hint = Hint(action="create", directive="do something", scope=Scope.SESSION,
                     priority=Priority.HIGH, actionability=0.8, confidence=0.8)
        result = resolver.resolve(hint, [])
        assert result == hint  # Unchanged

    def test_resolve_with_conflicts_hint_wins(self, resolver, store):
        hint = Hint(action="create", directive="do X", scope=Scope.SESSION,
                     priority=Priority.HIGH, actionability=0.9, confidence=0.95)
        conflicts = store.find_conflicts(hint)
        result = resolver.resolve(hint, conflicts)
        assert result == hint  # New hint is stronger

    def test_resolve_with_conflicts_rule_wins(self, resolver, store):
        hint = Hint(action="create", directive="do X", scope=Scope.SESSION,
                     priority=Priority.LOW, actionability=0.5, confidence=0.5)
        conflicts = store.find_conflicts(hint)
        result = resolver.resolve(hint, conflicts)
        # Should demote the hint
        assert result.priority != Priority.HIGH

    def test_resolve_all(self, resolver, store):
        hints = [
            Hint(action="create", directive="do A", scope=Scope.SESSION,
                 priority=Priority.HIGH, actionability=0.9, confidence=0.9),
            Hint(action="delete", directive="do B", scope=Scope.SESSION,
                 priority=Priority.MEDIUM, actionability=0.7, confidence=0.7),
        ]
        resolved = resolver.resolve_all(hints, store)
        assert len(resolved) == 2
        assert all(isinstance(h, Hint) for h in resolved)


# ── FastLearningLoop Tests ──────────────────────────────────────────────────────

class TestFastLearningLoop:
    @pytest.fixture
    def loop(self):
        return FastLearningLoop()

    def test_apply_hint_creates_rule(self, loop):
        hint = Hint(
            action="run_tests", directive="always run tests before push",
            scope=Scope.GLOBAL, priority=Priority.HIGH,
            actionability=0.8, confidence=0.8,
        )
        result = loop.apply_hint(hint)
        assert isinstance(result, ApplyResult)
        assert result.success is True
        assert result.created is True
        assert result.rule_id is not None
        assert loop.rule_store.size() >= 1

    def test_apply_hint_rejected_low_quality(self, loop):
        hint = Hint(
            action="test", directive="ab",
            scope=Scope.CONTEXT, priority=Priority.LOW,
            actionability=0.2, confidence=0.2,
        )
        result = loop.apply_hint(hint)
        assert result.success is False
        assert result.reason == "validation_failed"

    def test_apply_hint_duplicate_updates(self, loop):
        hint = Hint(
            action="run_tests", directive="run tests before push",
            scope=Scope.GLOBAL, priority=Priority.HIGH,
            actionability=0.8, confidence=0.8,
        )
        result1 = loop.apply_hint(hint)
        result2 = loop.apply_hint(hint)
        # Second call should update, not create new
        assert result2.updated is True

    def test_apply_hints_multiple(self, loop):
        hints = [
            Hint(action="a1", directive="do action one", scope=Scope.SESSION,
                 priority=Priority.HIGH, actionability=0.8, confidence=0.8),
            Hint(action="a2", directive="do action two", scope=Scope.SESSION,
                 priority=Priority.MEDIUM, actionability=0.7, confidence=0.7),
        ]
        results = loop.apply_hints(hints)
        assert len(results) == 2
        assert all(r.success for r in results)

    def test_record_feedback(self, loop):
        hint = Hint(action="run", directive="do run", scope=Scope.SESSION,
                     priority=Priority.HIGH, actionability=0.8, confidence=0.8)
        result = loop.apply_hint(hint)
        loop.record_feedback(result.rule_id, successful=True)
        loop.record_feedback(result.rule_id, successful=True)
        loop.record_feedback(result.rule_id, successful=False)

        rule = loop.rule_store.get(result.rule_id)
        assert rule.applied_count == 3
        assert rule.success_count == 2
        assert rule.success_rate == pytest.approx(2 / 3)

    def test_record_feedback_nonexistent_rule(self, loop):
        # Should not raise
        loop.record_feedback("nonexistent", successful=True)

    def test_get_statistics(self, loop):
        hint = Hint(action="run", directive="do run", scope=Scope.SESSION,
                     priority=Priority.HIGH, actionability=0.8, confidence=0.8)
        loop.apply_hint(hint)
        stats = loop.get_statistics()
        assert stats["store_size"] >= 1
        assert stats["applied"] >= 1

    def test_apply_invalid_hint(self, loop):
        hint = Hint(action="", directive="do", scope=Scope.CONTEXT,
                     priority=Priority.LOW, actionability=0.5, confidence=0.5)
        result = loop.apply_hint(hint)
        assert result.success is False

    def test_apply_hint_with_conflict(self, loop):
        # First, add a rule
        loop.apply_hint(Hint(
            action="run", directive="avoid running",
            scope=Scope.SESSION, priority=Priority.HIGH,
            actionability=0.8, confidence=0.9,
        ))
        # Then try to add a conflicting hint
        hint = Hint(action="run", directive="do run everything",
                     scope=Scope.SESSION, priority=Priority.HIGH,
                     actionability=0.9, confidence=0.95,
        )
        result = loop.apply_hint(hint)
        assert result.success is True

    def test_apply_result_to_dict(self, loop):
        hint = Hint(action="run", directive="do run", scope=Scope.SESSION,
                     priority=Priority.HIGH, actionability=0.8, confidence=0.8)
        result = loop.apply_hint(hint)
        d = result.to_dict()
        assert d["success"] is True
        assert "rule_id" in d

    def test_rule_store_find_conflicts_chinese(self):
        store = RuleStore()
        store.add(Rule("r1", "test_action", "避免使用X", "session", "high", 0.8, 0))
        hint = Hint(action="test_action", directive="要使用X",
                     scope=Scope.SESSION, priority=Priority.HIGH,
                     actionability=0.7, confidence=0.7)
        conflicts = store.find_conflicts(hint)
        assert len(conflicts) >= 1
