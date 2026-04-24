#!/usr/bin/env python3
"""
Tests for ValueReasoner
"""

import pytest
from datetime import datetime
from claw_rl.values import (
    ValueReasoner,
    ReasoningContext,
    ReasoningResult,
    ReasoningType,
)


class TestReasoningContext:
    """Test ReasoningContext"""

    def test_creation(self):
        """Test creation"""
        ctx = ReasoningContext(
            user_id="user1",
            action="test action",
            context="test context"
        )

        assert ctx.user_id == "user1"
        assert ctx.action == "test action"


class TestReasoningResult:
    """Test ReasoningResult"""

    def test_creation(self):
        """Test creation"""
        result = ReasoningResult(
            reasoning_type=ReasoningType.ETHICS_ASSESSMENT,
            decision="allow",
            confidence=0.8,
            explanation="Test explanation"
        )

        assert result.decision == "allow"
        assert result.confidence == 0.8


class TestValueReasoner:
    """Test ValueReasoner"""

    @pytest.fixture
    def reasoner(self):
        """Create reasoner"""
        return ValueReasoner()

    def test_creation(self, reasoner):
        """Test creation"""
        assert reasoner is not None

    def test_assess_ethics_allow(self, reasoner):
        """Test ethics assessment - allow"""
        ctx = ReasoningContext(
            user_id="user1",
            action="Say hello",
            context="greeting"
        )

        result = reasoner.assess_ethics("Say hello", ctx)

        assert result.decision in ["allow", "warn"]
        assert result.reasoning_type == ReasoningType.ETHICS_ASSESSMENT

    def test_assess_ethics_deny(self, reasoner):
        """Test ethics assessment - deny"""
        ctx = ReasoningContext(
            user_id="user1",
            action="伤害某人",
            context="test"
        )

        result = reasoner.assess_ethics("伤害某人", ctx)

        assert result.decision == "deny"

    def test_resolve_conflict_no_conflict(self, reasoner):
        """Test resolve conflict - no conflict"""
        values_a = {"principles": ["be honest"]}
        values_b = {"principles": ["be honest"]}

        result = reasoner.resolve_conflict(values_a, values_b)

        assert result.decision == "allow"

    def test_resolve_conflict_with_conflict(self, reasoner):
        """Test resolve conflict - with conflict"""
        values_a = {"red_lines": ["no violence"]}
        values_b = {"red_lines": ["no lying"]}

        result = reasoner.resolve_conflict(values_a, values_b)

        assert result.decision in ["human", "warn"]

    def test_generate_explanation(self, reasoner):
        """Test generate explanation"""
        decision = {"decision": "deny", "reason": "Test reason"}

        result = reasoner.generate_explanation(decision)

        assert result.reasoning_type == ReasoningType.EXPLANATION
        assert "拒绝" in result.explanation

    def test_reason_ambiguous_case(self, reasoner):
        """Test ambiguous case reasoning"""
        ctx = ReasoningContext(
            user_id="user1",
            action="Give advice",
            context="complex situation"
        )

        result = reasoner.reason_ambiguous_case(ctx)

        assert result.reasoning_type == ReasoningType.AMBIGUOUS_CASE
