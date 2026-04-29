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
Value Reasoner - LLM Value Reasoning
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum


class ReasoningType(Enum):
    """推理class型"""
    ETHICS_ASSESSMENT = "ethics_assessment"     # 伦理评估
    CONFLICT_RESOLUTION = "conflict_resolution" # 冲突solution决
    AMBIGUOUS_CASE = "ambiguous_case"           # ambiguous scenario
    EXPLANATION = "explanation"                 # 决策solution释


@dataclass
class ReasoningContext:
    """推理上下文"""
    user_id: str
    action: str
    context: str
    user_values: Optional[Dict[str, Any]] = None
    ethics_result: Optional[Dict[str, Any]] = None
    scenario: Optional[str] = None


@dataclass
class ReasoningResult:
    """推理结果"""
    reasoning_type: ReasoningType
    decision: str  # "allow", "deny", "warn", "human"
    confidence: float
    explanation: str
    considerations: List[str] = field(default_factory=list)
    ethical_basis: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reasoning_type": self.reasoning_type.value,
            "decision": self.decision,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "considerations": self.considerations,
            "ethical_basis": self.ethical_basis,
            "timestamp": self.timestamp.isoformat(),
        }


class ValueReasoner:
    """Value Reasoning器 - 使用 LLM 进行复杂道德推理"""

    def __init__(self, llm_provider: Optional[Any] = None):
        """initialize推理器

        Args:
            llm_provider: LLM 提供者,if为 None then使用模拟推理
        """
        self.llm_provider = llm_provider

        # 预定义的伦理原then(用于无 LLM 的回退)
        self._default_principles = [
            "not伤害他人",
            "尊重user自主权",
            "保持诚实",
            "保护隐私",
            "遵守legal",
        ]

    def reason_ambiguous_case(self, context: ReasoningContext) -> ReasoningResult:
        """ambiguous scenario推理

        Args:
            context: 推理上下文

        Returns:
            ReasoningResult: 推理结果
        """
        # if有 LLM,使用 LLM 推理
        if self.llm_provider:
            return self._llm_reason(context, ReasoningType.AMBIGUOUS_CASE)

        # 否then使用规then回退
        return self._rule_based_reason(context)

    def resolve_conflict(self, values_a: Dict[str, Any], values_b: Dict[str, Any]) -> ReasoningResult:
        """多价value观冲突协调

        Args:
            values_a: 第一group价value观
            values_b: 第二group价value观

        Returns:
            ReasoningResult: 推理结果
        """
        # extract conflict points
        conflicts = []
        for key in values_a:
            if key in values_b and values_a[key] != values_b[key]:
                conflicts.append({
                    "key": key,
                    "value_a": values_a[key],
                    "value_b": values_b[key]
                })

        if not conflicts:
            return ReasoningResult(
                reasoning_type=ReasoningType.CONFLICT_RESOLUTION,
                decision="allow",
                confidence=1.0,
                explanation="没有发现价value观冲突",
                considerations=["价value观一致"]
            )

        # 简单的冲突solution决策略
        # 优first级:红线 > 原then > 偏好
        resolution = self._resolve_by_priority(values_a, values_b, conflicts)

        return ReasoningResult(
            reasoning_type=ReasoningType.CONFLICT_RESOLUTION,
            decision=resolution["decision"],
            confidence=0.7,
            explanation=resolution["explanation"],
            considerations=[f"冲突点: {c['key']}" for c in conflicts],
            ethical_basis={"conflicts": conflicts, "resolution": resolution}
        )

    def generate_explanation(self, decision: Dict[str, Any]) -> ReasoningResult:
        """生成决策solution释

        Args:
            decision: 决策data

        Returns:
            ReasoningResult: 包含solution释的推理结果
        """
        decision_type = decision.get("decision", "unknown")
        reason = decision.get("reason", "")

        # 生成solution释
        explanation = self._generate_explanation_text(decision_type, reason)

        return ReasoningResult(
            reasoning_type=ReasoningType.EXPLANATION,
            decision=decision_type,
            confidence=0.9,
            explanation=explanation,
            considerations=[f"决策class型: {decision_type}", f"reason: {reason}"]
        )

    def assess_ethics(self, action: str, context: ReasoningContext) -> ReasoningResult:
        """伦理评估

        Args:
            action: 待评估的动作
            context: 推理上下文

        Returns:
            ReasoningResult: 伦理评估结果
        """
        # 基本伦理check
        ethical_issues = []

        # check是否触犯基本原then
        action_lower = action.lower()

        harm_keywords = ["伤害", "杀", "攻击", "暴力"]
        for kw in harm_keywords:
            if kw in action_lower:
                ethical_issues.append(f"可能造成伤害: {kw}")

        dishonest_keywords = ["欺骗", "说谎", "虚假"]
        for kw in dishonest_keywords:
            if kw in action_lower:
                ethical_issues.append(f"可能not诚实: {kw}")

        privacy_keywords = ["泄露", "expose", "偷看"]
        for kw in privacy_keywords:
            if kw in action_lower:
                ethical_issues.append(f"可能侵犯隐私: {kw}")

        # 做出决策
        if any("伤害" in issue for issue in ethical_issues):
            decision = "deny"
            confidence = 0.95
        elif ethical_issues:
            decision = "warn"
            confidence = 0.7
        else:
            decision = "allow"
            confidence = 0.8

        return ReasoningResult(
            reasoning_type=ReasoningType.ETHICS_ASSESSMENT,
            decision=decision,
            confidence=confidence,
            explanation=self._generate_explanation_text(decision, "; ".join(ethical_issues) if ethical_issues else "通过伦理check"),
            considerations=ethical_issues,
            ethical_basis={"issues": ethical_issues, "action": action}
        )

    def _llm_reason(self, context: ReasoningContext, reasoning_type: ReasoningType) -> ReasoningResult:
        """使用 LLM 进行推理"""
        # build提示
        prompt = self._build_prompt(context, reasoning_type)

        # 调用 LLM
        response = self.llm_provider.complete(prompt)

        # parse结果
        return self._parse_llm_response(response, reasoning_type)

    def _rule_based_reason(self, context: ReasoningContext) -> ReasoningResult:
        """基于规then的推理(无 LLM 的回退)"""
        action = context.action.lower()

        # 简单规then
        if any(kw in action for kw in ["伤害", "杀", "攻击"]):
            return ReasoningResult(
                reasoning_type=ReasoningType.AMBIGUOUS_CASE,
                decision="deny",
                confidence=0.9,
                explanation="action may cause harm",
                considerations=["安全优first"]
            )

        if context.user_values:
            red_lines = context.user_values.get("red_lines", [])
            for line in red_lines:
                if line.lower() in action:
                    return ReasoningResult(
                        reasoning_type=ReasoningType.AMBIGUOUS_CASE,
                        decision="deny",
                        confidence=0.95,
                        explanation=f"触犯user红线: {line}",
                        considerations=["user红线优first"]
                    )

        return ReasoningResult(
            reasoning_type=ReasoningType.AMBIGUOUS_CASE,
            decision="allow",
            confidence=0.6,
            explanation="未发现明显问题",
            considerations=["default允许"]
        )

    def _resolve_by_priority(self, values_a: Dict[str, Any], values_b: Dict[str, Any], conflicts: List[Dict]) -> Dict[str, Any]:
        """按优first级solution决冲突"""
        # 优first级:red_lines > principles > preferences

        # check红线冲突
        red_lines_a = values_a.get("red_lines", [])
        red_lines_b = values_b.get("red_lines", [])

        if red_lines_a and red_lines_b:
            return {
                "decision": "human",
                "explanation": "两个价value观都有红线,need人工确认"
            }

        # check原then冲突
        principles_a = values_a.get("principles", [])
        principles_b = values_b.get("principles", [])

        if principles_a and principles_b:
            return {
                "decision": "warn",
                "explanation": "原then存在冲突,建议谨慎process"
            }

        return {
            "decision": "allow",
            "explanation": "仅偏好冲突,可协商solution决"
        }

    def _generate_explanation_text(self, decision: str, reason: str) -> str:
        """生成solution释文本"""
        decision_text = {
            "allow": "允许",
            "deny": "拒绝",
            "warn": "warning后execute",
            "human": "need人工确认"
        }

        return f"决策: {decision_text.get(decision, decision)}.reason: {reason}"

    def _build_prompt(self, context: ReasoningContext, reasoning_type: ReasoningType) -> str:
        """build LLM 提示"""
        return f"""请analyze以下场景并给出伦理决策:

userID: {context.user_id}
动作: {context.action}
上下文: {context.context}

请判断: 允许(allow)/拒绝(deny)/warning(warn)/人工确认(human)
并给出solution释."""

    def _parse_llm_response(self, response: str, reasoning_type: ReasoningType) -> ReasoningResult:
        """parse LLM response"""
        # 简单parse(实际should更复杂)
        decision = "allow"
        if "拒绝" in response or "deny" in response.lower():
            decision = "deny"
        elif "warning" in response or "warn" in response.lower():
            decision = "warn"
        elif "确认" in response or "human" in response.lower():
            decision = "human"

        return ReasoningResult(
            reasoning_type=reasoning_type,
            decision=decision,
            confidence=0.8,
            explanation=response[:200],
            considerations=["基于 LLM 推理"]
        )


__all__ = [
    "ReasoningType",
    "ReasoningContext",
    "ReasoningResult",
    "ValueReasoner",
]
