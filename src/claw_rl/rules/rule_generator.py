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
Rule Generator - 将 Judge 结果convert为结构化规then
"""

import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class JudgeResult:
    """Judge 结果data模型"""

    def __init__(
        self,
        score: float,
        feedback: str,
        issues: list = None,
        code: str = "",
        language: str = "python"
    ):
        self.score = score
        self.feedback = feedback
        self.issues = issues or []
        self.code = code
        self.language = language


class RuleGenerator:
    """规then生成器 - 将 Judge 结果convert为可复用的规then"""

    # 规thenclass型映射
    RULE_TYPE_MAP = {
        'print': 'code_quality',
        'logging': 'code_quality',
        'error': 'error_handling',
        'exception': 'error_handling',
        'security': 'security',
        'vulnerability': 'security',
        'performance': 'performance',
        'slow': 'performance',
        'memory': 'performance',
        'style': 'code_style',
        'format': 'code_style',
        'convention': 'code_style',
    }

    # 严重程degree关key词映射
    SEVERITY_KEYWORDS = {
        'critical': ['critical', '严重', '危险', 'vulnerability', '安全漏洞'],
        'major': ['error', 'error', 'exception', 'bug', '问题'],
        'minor': ['warning', 'warning', '建议', 'consider', 'should'],
        'info': ['info', '提示', 'information', 'note'],
    }

    _rule_counter = 0

    @classmethod
    def generate_rule(cls, judge_result: JudgeResult) -> Dict[str, Any]:
        """将 Judge 结果convert为规then

        Args:
            judge_result: Judge 评估结果

        Returns:
            Dict: 结构化规then
        """
        # 提取代码模式
        pattern = cls._extract_pattern(judge_result)

        # 生成改进建议
        suggestion = cls._extract_suggestion(judge_result)

        # calculate严重程degree
        severity = cls._calculate_severity(judge_result)

        # 确定规thenclass型
        rule_type = cls._determine_rule_type(judge_result)

        # 生成规thenID
        rule_id = cls._generate_rule_id()

        # build规then
        rule = {
            "id": rule_id,
            "type": rule_type,
            "pattern": pattern,
            "suggestion": suggestion,
            "severity": severity,
            "version": "1.0",
            "confidence": min(judge_result.score, 1.0),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "language": judge_result.language,
                "issue_count": len(judge_result.issues),
                "original_feedback": judge_result.feedback[:200]
            }
        }

        return rule

    @classmethod
    def _extract_pattern(cls, result: JudgeResult) -> str:
        """提取代码模式

        Args:
            result: Judge 结果

        Returns:
            str: 代码模式字符串
        """
        if not result.code:
            return ".*"

        # 简单的模式提取:查找问题代码片段
        if result.issues:
            # 从第一个issue中提取模式
            issue = result.issues[0]
            if isinstance(issue, dict) and 'line' in issue:
                lines = result.code.split('\n')
                if issue['line'] <= len(lines):
                    problematic_line = lines[issue['line'] - 1].strip()
                    # 提取有问题的代码模式
                    return cls._simplify_pattern(problematic_line)

        # defaultreturn代码开头的模式
        first_line = result.code.split('\n')[0].strip() if result.code else ".*"
        return cls._simplify_pattern(first_line)

    @classmethod
    def _simplify_pattern(cls, code_line: str) -> str:
        """简化代码行为正then表达式模式

        Args:
            code_line: 代码行

        Returns:
            str: 正then表达式模式
        """
        # remove具体变量名,保留结构
        pattern = re.sub(r'\b\w+\b', 'WORD', code_line)
        # 转义特殊字符
        pattern = re.escape(pattern)
        # 恢复通配符
        pattern = pattern.replace('WORD', r'\w+')
        return pattern

    @classmethod
    def _extract_suggestion(cls, result: JudgeResult) -> str:
        """生成改进建议

        Args:
            result: Judge 结果

        Returns:
            str: 改进建议
        """
        if result.issues and isinstance(result.issues[0], dict):
            issue = result.issues[0]
            if 'suggestion' in issue:
                return issue['suggestion']

        # 从feedback中提取建议
        if result.feedback:
            # 取feedback前100字符作为建议
            return result.feedback[:100]

        return "Review and improve the code quality"

    @classmethod
    def _calculate_severity(cls, result: JudgeResult) -> str:
        """calculate严重程degree

        Args:
            result: Judge 结果

        Returns:
            str: 严重程degree (critical/major/minor/info)
        """
        feedback_lower = result.feedback.lower()

        # checkfeedback中的关key词
        for severity, keywords in cls.SEVERITY_KEYWORDS.items():
            if any(kw in feedback_lower for kw in keywords):
                return severity

        # 基于分数推断
        if result.score < 0.5:
            return 'major'
        elif result.score < 0.8:
            return 'minor'
        return 'info'

    @classmethod
    def _determine_rule_type(cls, result: JudgeResult) -> str:
        """确定规thenclass型

        Args:
            result: Judge 结果

        Returns:
            str: 规thenclass型
        """
        feedback_lower = result.feedback.lower()

        # check关key词映射
        for keyword, rule_type in cls.RULE_TYPE_MAP.items():
            if keyword in feedback_lower:
                return rule_type

        # defaultclass型
        return 'general'

    @classmethod
    def _generate_rule_id(cls) -> str:
        """生成规thenID

        Returns:
            str: 规thenID
        """
        cls._rule_counter += 1
        return f"rule_{cls._rule_counter:04d}"


__all__ = [
    'RuleGenerator',
    'JudgeResult',
]
