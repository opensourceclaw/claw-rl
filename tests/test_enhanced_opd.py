"""Tests for ImprovedOPDExtractor module (P0-3)"""

import pytest
from claw_rl.feedback.enhanced_opd import (
    ImprovedOPDExtractor, Hint, Priority, Scope,
)


# ── ImprovedOPDExtractor Tests ──────────────────────────────────────────────────

class TestImprovedOPDExtractor:
    @pytest.fixture
    def extractor(self):
        return ImprovedOPDExtractor()

    def test_extract_should_pattern(self, extractor):
        hint = extractor.extract("should place file in src/ directory")
        assert hint is not None
        assert isinstance(hint, Hint)
        assert hint.directive != ""
        assert hint.action != ""
        assert hint.actionability >= 0.0

    def test_extract_should_not_pattern(self, extractor):
        hint = extractor.extract("don't use global variables in production")
        assert hint is not None
        assert "avoid" in hint.directive.lower()

    def test_extract_sequence_pattern(self, extractor):
        hint = extractor.extract("first run the tests, then deploy")
        assert hint is not None
        assert isinstance(hint, Hint)

    def test_extract_conditional_pattern(self, extractor):
        hint = extractor.extract("if the build fails, then check the logs")
        assert hint is not None
        assert "if" in hint.directive.lower()

    def test_extract_action_required(self, extractor):
        hint = extractor.extract("please update the documentation")
        assert hint is not None
        assert hint.directive != ""

    def test_extract_chinese_should(self, extractor):
        hint = extractor.extract("应该把文件放在 src 目录下")
        assert hint is not None

    def test_extract_chinese_should_not(self, extractor):
        hint = extractor.extract("不要在生产环境使用 debug 模式")
        assert hint is not None

    def test_extract_chinese_sequence(self, extractor):
        hint = extractor.extract("先测试再部署")
        assert hint is not None

    def test_extract_priority_high(self, extractor):
        hint = extractor.extract("must fix this critical bug immediately")
        assert hint is not None
        assert hint.priority == Priority.HIGH

    def test_extract_priority_medium(self, extractor):
        hint = extractor.extract("should update the config file")
        assert hint is not None
        assert hint.priority == Priority.MEDIUM

    def test_extract_priority_low(self, extractor):
        hint = extractor.extract("prefer using spaces over tabs")
        assert hint is not None
        assert hint.priority in (Priority.LOW, Priority.MEDIUM)

    def test_extract_scope_global(self, extractor):
        hint = extractor.extract("always run the linter before committing")
        assert hint is not None
        assert hint.scope == Scope.GLOBAL

    def test_extract_actionability_high(self, extractor):
        hint = extractor.extract("should create file at src/claw_mem/memory.py with config class")
        assert hint is not None
        assert hint.actionability >= 0.4  # Should be relatively actionable

    def test_extract_actionability_low(self, extractor):
        hint = extractor.extract("should do something about things")
        assert hint is not None
        assert hint.actionability <= 0.7  # Vague, less actionable

    def test_extract_examples(self, extractor):
        hint = extractor.extract("should run tests before push")
        assert hint is not None
        assert len(hint.examples) >= 1  # At least one example

    def test_extract_empty_feedback(self, extractor):
        hint = extractor.extract("")
        assert hint is None

    def test_extract_no_pattern_match(self, extractor):
        hint = extractor.extract("the weather is nice today")
        assert hint is None

    def test_extract_all(self, extractor):
        corrections = [
            "should add unit tests",
            "don't use hardcoded values",
            "first validate input, then process",
        ]
        hints = extractor.extract_all(corrections)
        assert len(hints) == 3
        assert all(isinstance(h, Hint) for h in hints)

    def test_extract_all_deduplication(self, extractor):
        corrections = [
            "should run tests",
            "should run tests",  # Duplicate
        ]
        hints = extractor.extract_all(corrections)
        assert len(hints) == 1  # Deduplicated

    def test_extract_method_hint_directive_clarity(self, extractor):
        hint = extractor.extract("must create the module at src/memory.py with error handling")
        assert hint is not None
        # File path makes specificity higher
        assert hint.actionability >= 0.5

    def test_get_statistics(self, extractor):
        extractor.extract("should do X")
        extractor.extract("don't do Y")
        stats = extractor.get_statistics()
        assert stats["extractions"] >= 2
        assert stats["hints"] >= 2

    def test_extract_preference_pattern(self, extractor):
        hint = extractor.extract("I prefer using snake_case for Python")
        assert hint is not None

    def test_extract_with_context(self, extractor):
        context = {"action": "created_file", "project": "claw-mem"}
        hint = extractor.extract("should put file in tests/ directory", context)
        assert hint is not None
        assert isinstance(hint, Hint)


# ── Hint Dataclass Tests ───────────────────────────────────────────────────────

class TestHint:
    def test_default_values(self):
        hint = Hint(action="test_action", directive="test directive")
        assert hint.action == "test_action"
        assert hint.directive == "test directive"
        assert hint.scope == Scope.CONTEXT
        assert hint.priority == Priority.MEDIUM
        assert hint.actionability == 0.5
        assert hint.confidence == 0.5
        assert hint.examples == []

    def test_to_dict(self):
        hint = Hint(
            action="create_file",
            directive="put file in src/",
            scope=Scope.PROJECT,
            priority=Priority.HIGH,
            actionability=0.85,
            confidence=0.7,
            examples=["example 1"],
        )
        d = hint.to_dict()
        assert d["action"] == "create_file"
        assert d["scope"] == "project"
        assert d["priority"] == "high"
        assert d["actionability"] == 0.85


# ── Priority Enum Tests ─────────────────────────────────────────────────────────

class TestPriority:
    def test_high_to_int(self):
        assert Priority.HIGH.to_int() == 5

    def test_medium_to_int(self):
        assert Priority.MEDIUM.to_int() == 3

    def test_low_to_int(self):
        assert Priority.LOW.to_int() == 1


# ── Scope Enum Tests ────────────────────────────────────────────────────────────

class TestScope:
    def test_enum_values(self):
        assert Scope.GLOBAL.value == "global"
        assert Scope.PROJECT.value == "project"
        assert Scope.SESSION.value == "session"
        assert Scope.CONTEXT.value == "context"


# ── Edge Case Tests ─────────────────────────────────────────────────────────────

class TestImprovedOPDExtractorEdgeCases:
    @pytest.fixture
    def extractor(self):
        return ImprovedOPDExtractor()

    def test_whitespace_only(self, extractor):
        hint = extractor.extract("   ")
        assert hint is None

    def test_very_long_feedback(self, extractor):
        long_text = "should " + "x " * 100
        hint = extractor.extract(long_text)
        assert hint is not None

    def test_special_characters(self, extractor):
        hint = extractor.extract("should handle \"quoted\" and 'paths'")
        assert hint is not None

    def test_mixed_chinese_english(self, extractor):
        hint = extractor.extract("应该 run the tests 然后再 deploy")
        assert hint is not None
