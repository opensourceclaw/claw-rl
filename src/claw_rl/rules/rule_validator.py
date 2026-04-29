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
Rule Validator - 规thenvalidate器
"""

import re
from typing import Dict, Any, List, Tuple


class ValidationError(Exception):
    """validateerror"""
    pass


class RuleValidator:
    """规thenvalidate器 - validate规thenformat和冲突"""

    # 必需字段
    REQUIRED_FIELDS = ['id', 'type', 'pattern', 'suggestion', 'severity']

    # valid严重程degree
    VALID_SEVERITIES = ['critical', 'major', 'minor', 'info']

    # valid规thenclass型
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
        """validate规thenformat

        Args:
            rule: 规thendict

        Returns:
            Tuple[bool, List[str]]: (是否valid, errorlist)
        """
        errors = []

        # check必需字段
        for field in cls.REQUIRED_FIELDS:
            if field not in rule:
                errors.append(f"Missing required field: {field}")

        # validateIDformat
        if 'id' in rule:
            if not cls._validate_id(rule['id']):
                errors.append(f"Invalid ID format: {rule['id']}")

        # validateclass型
        if 'type' in rule:
            if rule['type'] not in cls.VALID_TYPES:
                errors.append(f"Invalid type: {rule['type']}")

        # validate严重程degree
        if 'severity' in rule:
            if rule['severity'] not in cls.VALID_SEVERITIES:
                errors.append(f"Invalid severity: {rule['severity']}")

        # validatepattern
        if 'pattern' in rule:
            if not cls._validate_pattern(rule['pattern']):
                errors.append(f"Invalid pattern: {rule['pattern']}")

        # validateconfidence
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
        """check规then冲突

        Args:
            rule: 新规then
            existing_rules: 现有规thenlist

        Returns:
            List[str]: 冲突描述list
        """
        conflicts = []
        rule_pattern = rule.get('pattern', '')
        rule_type = rule.get('type', '')

        for existing in existing_rules:
            # checkpattern冲突
            if existing.get('pattern') == rule_pattern:
                conflicts.append(
                    f"Pattern conflict with rule {existing.get('id')}: "
                    f"same pattern '{rule_pattern}'"
                )

            # checkclass型和severitygroup合冲突
            if (existing.get('type') == rule_type and
                existing.get('severity') == rule.get('severity')):
                # checksuggestion是否相似
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
        """calculate规then覆盖率

        Args:
            rule: 规then
            samples: 代码样本list

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
            # ifpatternnotvalid的正then表达式,直接字符串match
            matches = sum(1 for sample in samples if pattern in sample)
            return matches / len(samples)

    @classmethod
    def _validate_id(cls, rule_id: str) -> bool:
        """validateIDformat

        Args:
            rule_id: 规thenID

        Returns:
            bool: 是否valid
        """
        return bool(re.match(r'^rule_\d{4,}$', rule_id))

    @classmethod
    def _validate_pattern(cls, pattern: str) -> bool:
        """validatepatternformat

        Args:
            pattern: 模式字符串

        Returns:
            bool: 是否valid
        """
        if not pattern:
            return False

        # 尝试编译为正then表达式
        try:
            re.compile(pattern)
            return True
        except re.error:
            # ifnot正then表达式,至少should是非空字符串
            return len(pattern) > 0

    @classmethod
    def _similar_suggestions(cls, s1: str, s2: str, threshold: float = 0.7) -> bool:
        """check两个建议是否相似

        Args:
            s1: 建议1
            s2: 建议2
            threshold: 相似degree阈value

        Returns:
            bool: 是否相似
        """
        # 简单的词袋相似degree
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
