#!/usr/bin/env python3
"""
Tests for ScenarioRules
"""

import pytest
from claw_rl.values import ScenarioType, ScenarioRule, ScenarioRules


class TestScenarioRule:
    """Test ScenarioRule"""

    def test_creation(self):
        """Test rule creation"""
        rule = ScenarioRule(
            scenario=ScenarioType.INVESTMENT,
            name="Test Rule",
            description="Test description",
            keywords=["test"],
            required_statements=["statement"],
            prohibited_actions=["action"]
        )

        assert rule.scenario == ScenarioType.INVESTMENT
        assert rule.severity == "high"


class TestScenarioRules:
    """Test ScenarioRules"""

    @pytest.fixture
    def rules(self):
        """Create scenario rules"""
        return ScenarioRules()

    def test_detect_investment_scenario(self, rules):
        """Test investment scenario detection"""
        text = "我想投资股票,应该怎么做?"
        detected = rules.detect_scenario(text)

        assert ScenarioType.INVESTMENT in detected

    def test_detect_medical_scenario(self, rules):
        """Test medical scenario detection"""
        text = "我感冒了,应该吃什么药?"
        detected = rules.detect_scenario(text)

        assert ScenarioType.MEDICAL in detected

    def test_detect_legal_scenario(self, rules):
        """Test legal scenario detection"""
        text = "我想起诉某人,应该怎么做?"
        detected = rules.detect_scenario(text)

        assert ScenarioType.LEGAL in detected

    def test_detect_financial_scenario(self, rules):
        """Test financial scenario detection"""
        text = "如何合理避税?"
        detected = rules.detect_scenario(text)

        assert ScenarioType.FINANCIAL in detected

    def test_check_investment_rule_pass(self, rules):
        """Test investment rule check passes"""
        text = "投资有风险,请谨慎,不保证收益,可能亏损"
        result = rules.check_scenario(text, ScenarioType.INVESTMENT)

        assert result["passed"] is True

    def test_check_investment_rule_fail_prohibited(self, rules):
        """Test investment rule fails on prohibited actions"""
        text = "这是一个稳赚的投资机会"
        result = rules.check_scenario(text, ScenarioType.INVESTMENT)

        assert result["passed"] is False
        assert len(result["violations"]) > 0

    def test_check_investment_rule_fail_missing_statement(self, rules):
        """Test investment rule fails on missing statements"""
        text = "这是一个投资机会"
        result = rules.check_scenario(text, ScenarioType.INVESTMENT)

        # Should have warnings about missing statements
        assert len(result["warnings"]) > 0

    def test_check_medical_rule(self, rules):
        """Test medical scenario check"""
        text = "我建议你吃点感冒药"
        result = rules.check_scenario(text, ScenarioType.MEDICAL)

        # Should warn about missing professional consultation
        assert len(result["warnings"]) > 0

    def test_get_all_scenarios(self, rules):
        """Test get all scenarios"""
        scenarios = rules.get_all_scenarios()

        assert ScenarioType.INVESTMENT in scenarios
        assert ScenarioType.MEDICAL in scenarios
        assert ScenarioType.LEGAL in scenarios
        assert ScenarioType.FINANCIAL in scenarios


class TestScenarioRulesIntegration:
    """Integration tests for scenario rules"""

    def test_multiple_scenario_detection(self):
        """Test detecting multiple scenarios"""
        rules = ScenarioRules()
        text = "我想要投资股票,顺便看看法律问题"

        detected = rules.detect_scenario(text)

        assert len(detected) >= 1
