"""Chinese Feedback Parser — 中文反馈识别 for claw-rl v2.13.0."""

import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class FeedbackSignal(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


POSITIVE_PATTERNS = [
    "好的", "可以", "没问题", "对", "是的", "正确",
    "很好", "太棒了", "完美", "谢谢", "感谢",
    "就是这样", "正是", "符合预期", "不错", "挺好的",
    "非常棒", "厉害", "赞", "好主意", "同意",
    "没问题了", "了解了", "明白了",
]

NEGATIVE_PATTERNS = [
    "不对", "错误", "不是", "不行", "不要",
    "重做", "修改", "改一下", "换个方式",
    "不太对", "有问题", "不符合", "不满意",
    "错了", "不太好", "不太好使", "不太行",
    "重新来", "再试一次", "改一下这里",
]


class ChineseFeedbackParser:
    """Parse Chinese feedback text into positive/negative/neutral signals."""

    def parse(self, text: str) -> FeedbackSignal:
        """Analyze feedback text and return signal type."""
        if not text or not isinstance(text, str):
            return FeedbackSignal.NEUTRAL

        # Check negative first (prevent false positives like "不太对" matching "对")
        for pattern in NEGATIVE_PATTERNS:
            if pattern in text:
                logger.debug("Negative feedback detected: '%s'", pattern)
                return FeedbackSignal.NEGATIVE

        for pattern in POSITIVE_PATTERNS:
            if pattern in text:
                logger.debug("Positive feedback detected: '%s'", pattern)
                return FeedbackSignal.POSITIVE

        return FeedbackSignal.NEUTRAL

    def parse_with_confidence(self, text: str) -> tuple:
        """Parse with confidence level."""
        signal = self.parse(text)
        if signal == FeedbackSignal.NEUTRAL:
            return signal, 0.3
        # Count pattern matches for confidence
        patterns = POSITIVE_PATTERNS if signal == FeedbackSignal.POSITIVE else NEGATIVE_PATTERNS
        count = sum(1 for p in patterns if p in text)
        confidence = min(1.0, count * 0.3 + 0.4)
        return signal, confidence
