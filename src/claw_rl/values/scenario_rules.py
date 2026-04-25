# Copyright 2026 Peter Cheng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Scenario Rules - Scenario Rules
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import re


class ScenarioType(Enum):
    """Scenario Type"""
    INVESTMENT = "investment"    # investment
    MEDICAL = "medical"          # medical
    LEGAL = "legal"              # legal
    FINANCIAL = "financial"      # finance
    GENERAL = "general"          # 通用


@dataclass
class ScenarioRule:
    """Scenario Rules"""
    scenario: ScenarioType
    name: str
    description: str
    keywords: List[str]
    required_statements: List[str]  # 必须包含的声明
    prohibited_actions: List[str]   # 禁止的行为
    severity: str = "high"


class ScenarioRules:
    """Scenario Rules管理器"""

    # 预定义Scenario Rules
    SCENARIO_RULES = {
        ScenarioType.INVESTMENT: ScenarioRule(
            scenario=ScenarioType.INVESTMENT,
            name="investmentScenario Rules",
            description="investment相关建议的规then",
            keywords=["investment", "股票", "基金", "financial management", "炒", "买", "卖", "盈利", "收益"],
            required_statements=[
                "investment有风险",
                "请谨慎",
                "not保证收益",
                "可能亏损"
            ],
            prohibited_actions=[
                "杠杆",
                "满仓",
                "all-in",
                "稳赚",
                "一定赚钱"
            ],
            severity="high"
        ),
        ScenarioType.MEDICAL: ScenarioRule(
            scenario=ScenarioType.MEDICAL,
            name="medicalScenario Rules",
            description="medicalhealth相关建议的规then",
            keywords=["医生", "诊断", "治疗", "药", "医院", "health", "疾病", "症状"],
            required_statements=[
                "请咨询专业医生",
                "not专业medical建议",
                "建议then医"
            ],
            prohibited_actions=[
                "确诊",
                "diagnosed as",
                "自行服药",
                "notneed看医生"
            ],
            severity="critical"
        ),
        ScenarioType.LEGAL: ScenarioRule(
            scenario=ScenarioType.LEGAL,
            name="legalScenario Rules",
            description="legal相关建议的规then",
            keywords=["律师", "legal", "诉讼", "起诉", "法院", "犯罪", "违法"],
            required_statements=[
                "请咨询专业律师",
                "notlegal建议",
                "建议咨询律师"
            ],
            prohibited_actions=[
                "可以起诉",
                "not违法",
                "no problem",
                "not会坐牢"
            ],
            severity="high"
        ),
        ScenarioType.FINANCIAL: ScenarioRule(
            scenario=ScenarioType.FINANCIAL,
            name="financeScenario Rules",
            description="finance税务相关建议的规then",
            keywords=["税", "退税", "避税", "省钱", "逃税", "发票"],
            required_statements=[
                "请合规操作",
                "遵守税法",
                "建议咨询税务师"
            ],
            prohibited_actions=[
                "逃税",
                "避税",
                "少交税",
                "not用交税"
            ],
            severity="critical"
        ),
    }

    def __init__(self):
        """initializeScenario Rules"""
        self._rules = self.SCENARIO_RULES.copy()
        self._custom_rules: Dict[ScenarioType, ScenarioRule] = {}

    def detect_scenario(self, text: str) -> List[ScenarioType]:
        """检测文本涉及的场景

        Args:
            text: 待检测的文本

        Returns:
            List[ScenarioType]: match的Scenario Typelist
        """
        detected = []
        text_lower = text.lower()

        for scenario, rule in self._rules.items():
            # check关key词
            for keyword in rule.keywords:
                if keyword in text_lower:
                    detected.append(scenario)
                    break

        return detected

    def check_scenario(self, text: str, scenario: ScenarioType) -> Dict[str, Any]:
        """check文本是否符合Scenario Rules

        Args:
            text: 待check的文本
            scenario: Scenario Type

        Returns:
            Dict: check结果
        """
        rule = self._rules.get(scenario)
        if not rule:
            return {
                "passed": True,
                "violations": [],
                "warnings": []
            }

        violations = []
        warnings = []
        text_lower = text.lower()

        # check禁止的行为
        for prohibited in rule.prohibited_actions:
            if prohibited in text_lower:
                violations.append({
                    "type": "prohibited_action",
                    "content": prohibited,
                    "rule": rule.name,
                    "severity": rule.severity
                })

        # check是否包含必需的声明
        for required in rule.required_statements:
            if required not in text_lower:
                warnings.append({
                    "type": "missing_statement",
                    "content": required,
                    "rule": rule.name
                })

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "scenario": scenario.value,
            "rule_name": rule.name
        }

    def get_rule(self, scenario: ScenarioType) -> Optional[ScenarioRule]:
        """getScenario Rules"""
        return self._rules.get(scenario)

    def add_custom_rule(self, rule: ScenarioRule) -> None:
        """add自定义规then"""
        self._custom_rules[rule.scenario] = rule

    def remove_custom_rule(self, scenario: ScenarioType) -> bool:
        """remove自定义规then"""
        if scenario in self._custom_rules:
            del self._custom_rules[scenario]
            return True
        return False

    def get_all_scenarios(self) -> List[ScenarioType]:
        """get所有Scenario Type"""
        return list(self._rules.keys())


__all__ = [
    "ScenarioType",
    "ScenarioRule",
    "ScenarioRules",
]
