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
Rule Validator - 规则验证器
"""

import re
from typing import Dict, Any, List, Tuple


class ValidationError(Exception):
    """验证错误"""
    pass


class RuleValidator:
    """规则验证器 - 验证规则格式和冲突"""

    # 必需字段
    REQUIRED_FIELDS = ['id', 'type', 'pattern', 'suggestion', 'severity']

    # 有效严重程度
    VALID_SEVERITIES = ['critical', 'major', 'minor', 'info']

    # 有效规则类型
    VALID_TYPES = [
        'code_quality',
        'error_handling',
        'security',
        'performance',
        'code_style',
        'general'
    ]

    @classmethod
    def validate_rule(cls, rule: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证规则格式

        Args:
            rule: 规则字典

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误列表)
        """
        errors = []

        # 检查必需字段
        for field in cls.REQUIRED_FIELDS:
            if field not in rule:
                errors.append(f"Missing required field: {field}")

        # 验证ID格式
        if 'id' in rule:
            if not cls._validate_id(rule['id']):
                errors.append(f"Invalid ID format: {rule['id']}")

        # 验证类型
        if 'type' in rule:
            if rule['type'] not in cls.VALID_TYPES:
                errors.append(f"Invalid type: {rule['type']}")

        # 验证严重程度
        if 'severity' in rule:
            if rule['severity'] not in cls.VALID_SEVERITIES:
                errors.append(f"Invalid severity: {rule['severity']}")

        # 验证pattern
        if 'pattern' in rule:
            if not cls._validate_pattern(rule['pattern']):
                errors.append(f"Invalid pattern: {rule['pattern']}")

        # 验证confidence
        if 'confidence' in rule:
            if not (0 <= rule['confidence'] <= 1):
                errors.append(f"Confidence must be between 0 and 1")

        return len(errors) == 0, errors

    @classmethod
    def check_conflicts(
        cls,
        rule: Dict[str, Any],
        existing_rules: List[Dict[str, Any]]
    ) -> List[str]:
        """检查规则冲突

        Args:
            rule: 新规则
            existing_rules: 现有规则列表

        Returns:
            List[str]: 冲突描述列表
        """
        conflicts = []
        rule_pattern = rule.get('pattern', '')
        rule_type = rule.get('type', '')

        for existing in existing_rules:
            # 检查pattern冲突
            if existing.get('pattern') == rule_pattern:
                conflicts.append(
                    f"Pattern conflict with rule {existing.get('id')}: "
                    f"same pattern '{rule_pattern}'"
                )

            # 检查类型和severity组合冲突
            if (existing.get('type') == rule_type and
                existing.get('severity') == rule.get('severity')):
                # 检查suggestion是否相似
                if cls._similar_suggestions(
                    rule.get('suggestion', ''),
                    existing.get('suggestion', '')
                ):
                    conflicts.append(
                        f"Potential conflict with rule {existing.get('id')}: "
                        f"similar suggestion"
                    )

        return conflicts

    @classmethod
    def calculate_coverage(
        cls,
        rule: Dict[str, Any],
        samples: List[str]
    ) -> float:
        """计算规则覆盖率

        Args:
            rule: 规则
            samples: 代码样本列表

        Returns:
            float: 覆盖率 (0-1)
        """
        if not samples:
            return 0.0

        pattern = rule.get('pattern', '')
        if not pattern:
            return 0.0

        try:
            regex = re.compile(pattern)
            matches = sum(1 for sample in samples if regex.search(sample))
            return matches / len(samples)
        except re.error:
            # 如果pattern不是有效的正则表达式，直接字符串匹配
            matches = sum(1 for sample in samples if pattern in sample)
            return matches / len(samples)

    @classmethod
    def _validate_id(cls, rule_id: str) -> bool:
        """验证ID格式

        Args:
            rule_id: 规则ID

        Returns:
            bool: 是否有效
        """
        return bool(re.match(r'^rule_\d{4,}$', rule_id))

    @classmethod
    def _validate_pattern(cls, pattern: str) -> bool:
        """验证pattern格式

        Args:
            pattern: 模式字符串

        Returns:
            bool: 是否有效
        """
        if not pattern:
            return False

        # 尝试编译为正则表达式
        try:
            re.compile(pattern)
            return True
        except re.error:
            # 如果不是正则表达式，至少应该是非空字符串
            return len(pattern) > 0

    @classmethod
    def _similar_suggestions(cls, s1: str, s2: str, threshold: float = 0.7) -> bool:
        """检查两个建议是否相似

        Args:
            s1: 建议1
            s2: 建议2
            threshold: 相似度阈值

        Returns:
            bool: 是否相似
        """
        # 简单的词袋相似度
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())

        if not words1 or not words2:
            return False

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold


__all__ = [
    'RuleValidator',
    'ValidationError',
]
