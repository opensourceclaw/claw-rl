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
Scenario Rules - 场景规则
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import re


class ScenarioType(Enum):
    """场景类型"""
    INVESTMENT = "investment"    # 投资
    MEDICAL = "medical"          # 医疗
    LEGAL = "legal"              # 法律
    FINANCIAL = "financial"      # 财务
    GENERAL = "general"          # 通用


@dataclass
class ScenarioRule:
    """场景规则"""
    scenario: ScenarioType
    name: str
    description: str
    keywords: List[str]
    required_statements: List[str]  # 必须包含的声明
    prohibited_actions: List[str]   # 禁止的行为
    severity: str = "high"


class ScenarioRules:
    """场景规则管理器"""

    # 预定义场景规则
    SCENARIO_RULES = {
        ScenarioType.INVESTMENT: ScenarioRule(
            scenario=ScenarioType.INVESTMENT,
            name="投资场景规则",
            description="投资相关建议的规则",
            keywords=["投资", "股票", "基金", "理财", "炒", "买", "卖", "盈利", "收益"],
            required_statements=[
                "投资有风险",
                "请谨慎",
                "不保证收益",
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
            name="医疗场景规则",
            description="医疗健康相关建议的规则",
            keywords=["医生", "诊断", "治疗", "药", "医院", "健康", "疾病", "症状"],
            required_statements=[
                "请咨询专业医生",
                "不是专业医疗建议",
                "建议就医"
            ],
            prohibited_actions=[
                "确诊",
                "诊断为",
                "自行服药",
                "不需要看医生"
            ],
            severity="critical"
        ),
        ScenarioType.LEGAL: ScenarioRule(
            scenario=ScenarioType.LEGAL,
            name="法律场景规则",
            description="法律相关建议的规则",
            keywords=["律师", "法律", "诉讼", "起诉", "法院", "犯罪", "违法"],
            required_statements=[
                "请咨询专业律师",
                "不是法律建议",
                "建议咨询律师"
            ],
            prohibited_actions=[
                "可以起诉",
                "不违法",
                "没问题",
                "不会坐牢"
            ],
            severity="high"
        ),
        ScenarioType.FINANCIAL: ScenarioRule(
            scenario=ScenarioType.FINANCIAL,
            name="财务场景规则",
            description="财务税务相关建议的规则",
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
                "不用交税"
            ],
            severity="critical"
        ),
    }

    def __init__(self):
        """初始化场景规则"""
        self._rules = self.SCENARIO_RULES.copy()
        self._custom_rules: Dict[ScenarioType, ScenarioRule] = {}

    def detect_scenario(self, text: str) -> List[ScenarioType]:
        """检测文本涉及的场景

        Args:
            text: 待检测的文本

        Returns:
            List[ScenarioType]: 匹配的场景类型列表
        """
        detected = []
        text_lower = text.lower()

        for scenario, rule in self._rules.items():
            # 检查关键词
            for keyword in rule.keywords:
                if keyword in text_lower:
                    detected.append(scenario)
                    break

        return detected

    def check_scenario(self, text: str, scenario: ScenarioType) -> Dict[str, Any]:
        """检查文本是否符合场景规则

        Args:
            text: 待检查的文本
            scenario: 场景类型

        Returns:
            Dict: 检查结果
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

        # 检查禁止的行为
        for prohibited in rule.prohibited_actions:
            if prohibited in text_lower:
                violations.append({
                    "type": "prohibited_action",
                    "content": prohibited,
                    "rule": rule.name,
                    "severity": rule.severity
                })

        # 检查是否包含必需的声明
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
        """获取场景规则"""
        return self._rules.get(scenario)

    def add_custom_rule(self, rule: ScenarioRule) -> None:
        """添加自定义规则"""
        self._custom_rules[rule.scenario] = rule

    def remove_custom_rule(self, scenario: ScenarioType) -> bool:
        """移除自定义规则"""
        if scenario in self._custom_rules:
            del self._custom_rules[scenario]
            return True
        return False

    def get_all_scenarios(self) -> List[ScenarioType]:
        """获取所有场景类型"""
        return list(self._rules.keys())


__all__ = [
    "ScenarioType",
    "ScenarioRule",
    "ScenarioRules",
]
