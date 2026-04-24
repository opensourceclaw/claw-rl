#!/usr/bin/env python3
"""
Tests for EthicsRuleBase
"""

import pytest
from claw_rl.ethics import (
    EthicsRule,
    RuleCategory,
    ViolationSeverity,
    CheckResult,
    EthicsRuleBase,
)


class TestEthicsRule:
    """Test EthicsRule"""

    def test_creation(self):
        """Test rule creation"""
        rule = EthicsRule(
            id="test_rule",
            name="Test Rule",
            description="A test rule",
            category=RuleCategory.LEGAL,
            pattern="test",
            severity=ViolationSeverity.MEDIUM
        )

        assert rule.id == "test_rule"
        assert rule.name == "Test Rule"
        assert rule.enabled is True

    def test_to_dict(self):
        """Test to_dict"""
        rule = EthicsRule(
            id="r1",
            name="Rule 1",
            description="Desc",
            category=RuleCategory.SAFETY,
            pattern="pattern",
            severity=ViolationSeverity.HIGH
        )

        d = rule.to_dict()
        assert d["id"] == "r1"
        assert d["category"] == "safety"
        assert d["severity"] == "high"


class TestEthicsRuleBase:
    """Test EthicsRuleBase"""

    @pytest.fixture
    def rule_base(self):
        """Create rule base"""
        return EthicsRuleBase()

    def test_default_rules_loaded(self, rule_base):
        """Test default rules are loaded"""
        rules = rule_base.get_all_rules()
        assert len(rules) > 0

    def test_check_action_pass(self, rule_base):
        """Test check action passes"""
        result = rule_base.check_action("Hello, how are you?")

        assert result.passed is True
        assert len(result.violations) == 0

    def test_check_action_fraud(self, rule_base):
        """Test check detects fraud"""
        result = rule_base.check_action("This is a 诈骗 scheme")

        assert result.passed is False
        assert len(result.violations) > 0

    def test_check_action_harm(self, rule_base):
        """Test check detects harm"""
        result = rule_base.check_action("Let's do some 暴力")

        assert result.passed is False

    def test_add_rule(self, rule_base):
        """Test add rule"""
        new_rule = EthicsRule(
            id="custom_rule",
            name="Custom Rule",
            description="Custom description",
            category=RuleCategory.CUSTOM,
            pattern="custom",
            severity=ViolationSeverity.LOW
        )

        rule_base.add_rule(new_rule)
        rules = rule_base.get_all_rules()

        assert any(r.id == "custom_rule" for r in rules)

    def test_remove_rule(self, rule_base):
        """Test remove rule"""
        result = rule_base.remove_rule("legal_fraud")
        assert result is True

        # Should not be found
        result = rule_base.check_action("诈骗")
        assert result.passed is True

    def test_get_rules_by_category(self, rule_base):
        """Test get rules by category"""
        legal_rules = rule_base.get_rules_by_category(RuleCategory.LEGAL)

        assert len(legal_rules) > 0
        assert all(r.category == RuleCategory.LEGAL for r in legal_rules)

    def test_enable_disable_rule(self, rule_base):
        """Test enable/disable rule"""
        # Disable
        rule_base.disable_rule("legal_fraud")
        result = rule_base.check_action("这是一个诈骗")

        assert result.passed is True

        # Enable
        rule_base.enable_rule("legal_fraud")
        result = rule_base.check_action("这是一个诈骗")

        assert result.passed is False


class TestCheckResult:
    """Test CheckResult"""

    def test_passed_result(self):
        """Test passed result"""
        result = CheckResult(passed=True)

        assert result.passed is True
        assert result.violations == []
        assert result.warnings == []

    def test_failed_result(self):
        """Test failed result"""
        result = CheckResult(
            passed=False,
            violations=[{"rule_id": "r1", "severity": "high"}],
            warnings=["Warning message"]
        )

        assert result.passed is False
        assert len(result.violations) == 1

    def test_to_dict(self):
        """Test to_dict"""
        result = CheckResult(
            passed=False,
            violations=[{"id": "v1"}]
        )

        d = result.to_dict()
        assert d["passed"] is False
        assert len(d["violations"]) == 1
