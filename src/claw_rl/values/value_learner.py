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
Value Learner - Implicit Value Learning
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import re

from claw_mem.values import UserValueStore


class LearningSource(Enum):
    """Learning Source Type"""
    EXPLICIT_CORRECTION = "explicit_correction"  # 明确纠正
    REPEATED_BEHAVIOR = "repeated_behavior"       # 重复行为
    REJECTED_SUGGESTION = "rejected_suggestion"   # 拒绝建议
    POSITIVE_FEEDBACK = "positive_feedback"       # 正面反馈
    NEGATIVE_FEEDBACK = "negative_feedback"       # 负面反馈


@dataclass
class Interaction:
    """交互记录"""
    user_id: str
    user_input: str
    agent_response: str
    user_feedback: Optional[str] = None
    feedback_type: Optional[str] = None  # "positive", "negative", "correction"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "user_input": self.user_input,
            "agent_response": self.agent_response,
            "user_feedback": self.user_feedback,
            "feedback_type": self.feedback_type,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ExtractedPrinciple:
    """提取的原then"""
    principle: str
    source: LearningSource
    confidence: float
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "principle": self.principle,
            "source": self.source.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "timestamp": self.timestamp.isoformat(),
        }


class ValueLearner:
    """Value Learning器 - 从交互中隐式学习user价value观"""

    def __init__(self, value_store: Optional[UserValueStore] = None):
        """initialize学习器

        Args:
            value_store: user价value观存储，if为 None thencreate新的
        """
        self.value_store = value_store or UserValueStore()

        # 学习历史
        self._interaction_history: List[Interaction] = []
        self._extracted_principles: Dict[str, List[ExtractedPrinciple]] = {}

    def learn_from_interaction(self, user_id: str, interaction: Dict[str, Any]) -> List[ExtractedPrinciple]:
        """从交互中学习价value观

        Args:
            user_id: user ID
            interaction: 交互data

        Returns:
            List[ExtractedPrinciple]: 提取的原thenlist
        """
        # create交互记录
        interaction_record = Interaction(
            user_id=user_id,
            user_input=interaction.get("user_input", ""),
            agent_response=interaction.get("agent_response", ""),
            user_feedback=interaction.get("user_feedback"),
            feedback_type=interaction.get("feedback_type")
        )

        self._interaction_history.append(interaction_record)

        # 根据反馈class型学习
        extracted = []

        if interaction_record.feedback_type == "correction":
            # user明确纠正
            principle = self.extract_principle(interaction_record)
            if principle:
                extracted.append(principle)
                self._save_learned_principle(user_id, principle)

        elif interaction_record.feedback_type == "negative":
            # 负面反馈 - 可能触犯了红线
            red_line = self._infer_red_line(interaction_record)
            if red_line:
                self.value_store.save_red_line(user_id, red_line)
                extracted.append(ExtractedPrinciple(
                    principle=f"notshould: {red_line}",
                    source=LearningSource.REJECTED_SUGGESTION,
                    confidence=0.8,
                    evidence=[interaction_record.agent_response]
                ))

        elif interaction_record.feedback_type == "positive":
            # 正面反馈 - 确认when前做法
            principle = self.extract_principle_from_positive(interaction_record)
            if principle:
                extracted.append(principle)

        return extracted

    def extract_principle(self, interaction: Interaction) -> Optional[ExtractedPrinciple]:
        """从纠正反馈中提取原then

        Args:
            interaction: 交互记录

        Returns:
            Optional[ExtractedPrinciple]: 提取的原then
        """
        if not interaction.user_feedback:
            return None

        feedback = interaction.user_feedback.lower()

        # 常见的纠正模式
        correction_patterns = [
            (r"don't(.*?)$", r"\1"),
            (r"notshould(.*?)$", r"\1"),
            (r"don't(.*?)$", r"\1"),
            (r"don't做(.*?)$", r"\1"),
            (r"禁止(.*?)$", r"\1"),
        ]

        for pattern, replacement in correction_patterns:
            match = re.search(pattern, feedback)
            if match:
                principle_text = match.group(1).strip()
                return ExtractedPrinciple(
                    principle=f"notshould{principle_text}",
                    source=LearningSource.EXPLICIT_CORRECTION,
                    confidence=0.9,
                    evidence=[interaction.user_feedback, interaction.agent_response]
                )

        # if没有match模式，直接使用反馈作为原then
        return ExtractedPrinciple(
            principle=interaction.user_feedback,
            source=LearningSource.EXPLICIT_CORRECTION,
            confidence=0.7,
            evidence=[interaction.user_feedback]
        )

    def extract_principle_from_positive(self, interaction: Interaction) -> Optional[ExtractedPrinciple]:
        """从正面反馈中提取原then

        Args:
            interaction: 交互记录

        Returns:
            Optional[ExtractedPrinciple]: 提取的原then
        """
        if not interaction.user_feedback:
            return None

        # 正面反馈模式
        positive_patterns = [
            r"great",
            r"good",
            r"correct",
            r"correct",
            r"satisfied",
            r"正是",
        ]

        feedback = interaction.user_feedback.lower()
        if any(re.search(p, feedback) for p in positive_patterns):
            # 从 Agent response中提取被认可的部分
            return ExtractedPrinciple(
                principle=f"保持: {interaction.agent_response[:100]}",
                source=LearningSource.POSITIVE_FEEDBACK,
                confidence=0.6,
                evidence=[interaction.agent_response]
            )

        return None

    def detect_preference(self, user_id: str, behavior: str) -> Dict[str, Any]:
        """从行为中检测偏好

        Args:
            user_id: user ID
            behavior: 行为描述

        Returns:
            Dict: detected preference
        """
        preferences = {}

        # 简单的偏好模式检测
        behavior_lower = behavior.lower()

        # 风格偏好
        if any(word in behavior_lower for word in ["简洁", "简单", "short", "brief"]):
            preferences["style"] = "concise"
        elif any(word in behavior_lower for word in ["详细", "详细说明", "详细solution释"]):
            preferences["style"] = "detailed"

        # 语气偏好
        if any(word in behavior_lower for word in ["正式", "professional"]):
            preferences["tone"] = "formal"
        elif any(word in behavior_lower for word in ["随意", "casual"]):
            preferences["tone"] = "casual"

        # format偏好
        if any(word in behavior_lower for word in ["list", "list", " bullet"]):
            preferences["format"] = "list"
        elif any(word in behavior_lower for word in ["段落", "paragraph"]):
            preferences["format"] = "paragraph"

        return preferences

    def update_red_line(self, user_id: str, new_line: str) -> None:
        """updateuser红线

        Args:
            user_id: user ID
            new_line: 新红线
        """
        self.value_store.save_red_line(user_id, new_line)

    def _infer_red_line(self, interaction: Interaction) -> Optional[str]:
        """推断红线

        Args:
            interaction: 交互记录

        Returns:
            Optional[str]: 推断的红线
        """
        if not interaction.agent_response:
            return None

        response = interaction.agent_response.lower()

        # 常见的触犯红线的content
        red_line_patterns = {
            "攻击性语言": ["骂", "滚", "傻", "笨", "蠢"],
            "notwhen建议": ["do wrong", "骗人", "作弊"],
            "隐私相关": ["泄露", "expose", "公开"],
        }

        for line_type, keywords in red_line_patterns.items():
            if any(kw in response for kw in keywords):
                return line_type

        return None

    def _save_learned_principle(self, user_id: str, principle: ExtractedPrinciple) -> None:
        """save学习到的原then

        Args:
            user_id: user ID
            principle: 提取的原then
        """
        self.value_store.save_principle(user_id, principle.principle)

        if user_id not in self._extracted_principles:
            self._extracted_principles[user_id] = []

        self._extracted_principles[user_id].append(principle)

    def get_interaction_history(self, user_id: str) -> List[Interaction]:
        """getuser的交互历史

        Args:
            user_id: user ID

        Returns:
            List[Interaction]: 交互历史
        """
        return [i for i in self._interaction_history if i.user_id == user_id]

    def get_learned_principles(self, user_id: str) -> List[ExtractedPrinciple]:
        """get学习到的原then

        Args:
            user_id: user ID

        Returns:
            List[ExtractedPrinciple]: 原thenlist
        """
        return self._extracted_principles.get(user_id, [])


__all__ = [
    "Interaction",
    "ExtractedPrinciple",
    "LearningSource",
    "ValueLearner",
]
