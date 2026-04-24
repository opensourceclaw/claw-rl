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
Ethics Rule Base - 伦理规则库
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RuleCategory(Enum):
    """规则分类"""
    LEGAL = "legal"          # 法律法规
    SAFETY = "safety"        # 安全底线
    ETHICS = "ethics"        # 通用伦理
    CUSTOM = "custom"        # 自定义规则


class ViolationSeverity(Enum):
    """违规严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EthicsRule:
    """伦理规则"""
    id: str
    name: str
    description: str
    category: RuleCategory
    pattern: str  # 正则表达式或关键词
    severity: ViolationSeverity = ViolationSeverity.MEDIUM
    message: str = ""
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "pattern": self.pattern,
            "severity": self.severity.value,
            "message": self.message,
            "enabled": self.enabled,
        }


@dataclass
class CheckResult:
    """检查结果"""
    passed: bool
    violations: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "violations": self.violations,
            "warnings": self.warnings,
        }


class EthicsRuleBase:
    """伦理规则库"""

    # 内置规则
    DEFAULT_RULES = [
        # 法律法规
        EthicsRule(
            id="legal_fraud",
            name="禁止欺诈",
            description="不得进行欺诈行为",
            category=RuleCategory.LEGAL,
            pattern=r"(诈骗|欺诈|骗钱|假冒)",
            severity=ViolationSeverity.CRITICAL,
            message="检测到疑似欺诈内容"
        ),
        EthicsRule(
            id="legal_copyright",
            name="尊重版权",
            description="不得侵犯版权",
            category=RuleCategory.LEGAL,
            pattern=r"(盗版|侵权|破解)",
            severity=ViolationSeverity.HIGH,
            message="检测到疑似侵权内容"
        ),
        # 安全底线
        EthicsRule(
            id="safety_harm",
            name="禁止伤害",
            description="不得伤害他人",
            category=RuleCategory.SAFETY,
            pattern=r"(杀人|伤害|暴力|攻击)",
            severity=ViolationSeverity.CRITICAL,
            message="检测到疑似伤害内容"
        ),
        EthicsRule(
            id="safety_privacy",
            name="保护隐私",
            description="不得泄露隐私",
            category=RuleCategory.SAFETY,
            pattern=r"(泄露.*密码|泄露.*地址|泄露.*电话)",
            severity=ViolationSeverity.HIGH,
            message="检测到疑似隐私泄露"
        ),
        EthicsRule(
            id="safety_malware",
            name="禁止恶意软件",
            description="不得创建恶意软件",
            category=RuleCategory.SAFETY,
            pattern=r"(病毒|木马|蠕虫|勒索)",
            severity=ViolationSeverity.CRITICAL,
            message="检测到疑似恶意软件相关内容"
        ),
        # 通用伦理
        EthicsRule(
            id="ethics_honest",
            name="诚实守信",
            description="应保持诚实",
            category=RuleCategory.ETHICS,
            pattern=r"(欺骗|说谎|虚假)",
            severity=ViolationSeverity.MEDIUM,
            message="检测到疑似不诚实内容"
        ),
        EthicsRule(
            id="ethics_fair",
            name="公平公正",
            description="应公平对待",
            category=RuleCategory.ETHICS,
            pattern=r"(歧视|偏见|不公平)",
            severity=ViolationSeverity.HIGH,
            message="检测到疑似歧视内容"
        ),
    ]

    def __init__(self):
        """初始化规则库"""
        self._rules: Dict[str, EthicsRule] = {}
        self._rules_by_category: Dict[RuleCategory, List[EthicsRule]] = {}

        # 加载内置规则
        for rule in self.DEFAULT_RULES:
            self._add_rule_internal(rule)

    def check_action(self, action: str) -> CheckResult:
        """检查动作是否合规

        Args:
            action: 待检查的动作或内容

        Returns:
            CheckResult: 检查结果
        """
        violations = []
        warnings = []

        for rule in self._rules.values():
            if not rule.enabled:
                continue

            # 使用正则表达式匹配
            try:
                if re.search(rule.pattern, action, re.IGNORECASE):
                    violations.append({
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "severity": rule.severity.value,
                        "message": rule.message or rule.description,
                    })

                    if rule.severity == ViolationSeverity.LOW:
                        warnings.append(rule.message or rule.description)
            except re.error:
                # 如果正则表达式无效，使用简单的子串匹配
                if rule.pattern.lower() in action.lower():
                    violations.append({
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "severity": rule.severity.value,
                        "message": rule.message or rule.description,
                    })

        return CheckResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings
        )

    def add_rule(self, rule: EthicsRule) -> None:
        """添加规则

        Args:
            rule: 伦理规则
        """
        self._add_rule_internal(rule)

    def remove_rule(self, rule_id: str) -> bool:
        """移除规则

        Args:
            rule_id: 规则 ID

        Returns:
            bool: 是否成功移除
        """
        if rule_id in self._rules:
            rule = self._rules[rule_id]
            del self._rules[rule_id]
            if rule.category in self._rules_by_category:
                self._rules_by_category[rule.category] = [
                    r for r in self._rules_by_category[rule.category]
                    if r.id != rule_id
                ]
            return True
        return False

    def get_rules_by_category(self, category: RuleCategory) -> List[EthicsRule]:
        """获取分类规则

        Args:
            category: 规则分类

        Returns:
            List[EthicsRule]: 规则列表
        """
        return self._rules_by_category.get(category, [])

    def get_all_rules(self) -> List[EthicsRule]:
        """获取所有规则"""
        return list(self._rules.values())

    def enable_rule(self, rule_id: str) -> bool:
        """启用规则"""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """禁用规则"""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = False
            return True
        return False

    def _add_rule_internal(self, rule: EthicsRule) -> None:
        """内部添加规则方法"""
        self._rules[rule.id] = rule

        if rule.category not in self._rules_by_category:
            self._rules_by_category[rule.category] = []
        self._rules_by_category[rule.category].append(rule)


__all__ = [
    "EthicsRule",
    "RuleCategory",
    "ViolationSeverity",
    "CheckResult",
    "EthicsRuleBase",
]
