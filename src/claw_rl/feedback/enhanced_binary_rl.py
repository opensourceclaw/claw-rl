"""
Enhanced Binary RL Judge (P0-3)

Multi-signal binary feedback classification with:
1. Pattern classifier (fast, explicit signals)
2. Semantic classifier (implicit signals)
3. Context enhancement (conversation context)
4. Confidence calibration (historical accuracy)

Target: Binary RL accuracy ~75% → >90%
"""

import re
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from .binary_rl import BinaryRLJudge, RewardResult


@dataclass
class JudgeResult:
    """Enhanced judgment result with multi-signal details."""
    is_positive: bool
    confidence: float
    reward: int  # -1, 0, or +1
    signals: Dict[str, float]  # Per-signal contribution
    pattern_matched: Optional[str] = None
    semantic_label: Optional[str] = None
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "is_positive": self.is_positive,
            "confidence": self.confidence,
            "reward": self.reward,
            "signals": self.signals,
            "pattern_matched": self.pattern_matched,
            "semantic_label": self.semantic_label,
            "reason": self.reason,
        }


class PatternClassifier:
    """Fast, explicit pattern-based classification.

    Categorizes feedback into positive/negative/neutral using regex patterns.
    More granular than the original BinaryRLJudge with categorized patterns.
    """

    POSITIVE_PATTERNS: Dict[str, List[str]] = {
        "gratitude": [
            r"(?i)\b(thanks|thank you|thank)\b",
            r"(谢谢|感谢|感恩|谢了|多谢)",
        ],
        "approval": [
            r"(?i)\b(great|awesome|good|perfect|excellent|correct|right)\b",
            r"(很好|很棒|不错|太好了|太棒了|完美|好的|解决|清楚|正是|满意|认可|赞|准确|正确)",
            r"(?i)\b(that's (exactly|right|correct))\b",
            r"(✅|👍)",
        ],
        "success": [
            r"(?i)\b(it works|working|worked|fixed|resolved|done)\b",
            r"(可以了|好了|搞定了|解决了|完成了|成功)",
        ],
    }

    NEGATIVE_PATTERNS: Dict[str, List[str]] = {
        "error": [
            r"(?i)\b(wrong|incorrect|bad|error|mistake|bug|fail|broken|issue)\b",
            r"(错误|不对|错了|问题|失败|bug|有问题|不对的|搞错了|不行)",
            r"(❌|👎)",
        ],
        "correction": [
            r"(?i)\b(don't|do not|never|shouldn't|mustn't)\b",
            r"(?i)\b(should|must|need to|have to|please)\b",
            r"(不要|不能|不应该|应该|需要|必须|要|得)",
        ],
        "dissatisfaction": [
            r"(?i)\b(not good|not great|disappoint(?:ing|ed|ment)?|unsatisf(?:y|ied|ying))\b",
            r"(不好|不满意|不行|差|糟糕|烦|无语)",
        ],
    }

    def __init__(self):
        self._compiled_pos: Dict[str, List[re.Pattern]] = {}
        self._compiled_neg: Dict[str, List[re.Pattern]] = {}
        for cat, pats in self.POSITIVE_PATTERNS.items():
            self._compiled_pos[cat] = [re.compile(p) for p in pats]
        for cat, pats in self.NEGATIVE_PATTERNS.items():
            self._compiled_neg[cat] = [re.compile(p) for p in pats]

    def classify(self, feedback: str) -> Tuple[str, float, Optional[str]]:
        """Classify feedback as positive/negative/neutral.

        Args:
            feedback: User feedback text

        Returns:
            Tuple of (label, confidence, matched_pattern_category)
        """
        if not feedback:
            return "neutral", 0.5, None

        pos_score = 0
        pos_category = None
        neg_score = 0
        neg_category = None

        for cat, patterns in self._compiled_pos.items():
            matches = sum(1 for p in patterns if p.search(feedback))
            if matches > pos_score:
                pos_score = matches
                pos_category = cat

        for cat, patterns in self._compiled_neg.items():
            matches = sum(1 for p in patterns if p.search(feedback))
            if matches > neg_score:
                neg_score = matches
                neg_category = cat

        if pos_score > neg_score:
            confidence = min(0.95, 0.7 + 0.1 * pos_score)
            return "positive", confidence, pos_category
        elif neg_score > pos_score:
            confidence = min(0.95, 0.7 + 0.1 * neg_score)
            return "negative", confidence, neg_category
        else:
            return "neutral", 0.4, None


class SemanticClassifier:
    """Semantic understanding for implicit feedback signals.

    Detects implicit sentiment and intent beyond simple pattern matching.
    Uses lightweight heuristics for fast classification.
    """

    # Implicit sentiment indicators
    IMPLICIT_POSITIVE = [
        r"(?i)\b(cool|nice|useful|helpful|interesting|makes sense|got it)\b",
        r"(有意思|有道理|懂了|明白|了解|收到|get)",
    ]

    IMPLICIT_NEGATIVE = [
        r"(?i)\b(confusing|unclear|not sure|hmm|uh|meh|whatever)\b",
        r"(不太对|有点问题|不太清楚|不是这个|算了吧|算了)",
    ]

    # Question/curiosity signals (neutral but engaged)
    CURIOSITY = [
        r"(?i)\b(can you|could you|how about|what if|is it possible)\b",
        r"(能不能|可不可以|怎么样|会不会|如果)",
    ]

    def __init__(self):
        self._pos_patterns = [re.compile(p) for p in self.IMPLICIT_POSITIVE]
        self._neg_patterns = [re.compile(p) for p in self.IMPLICIT_NEGATIVE]
        self._curiosity_patterns = [re.compile(p) for p in self.CURIOSITY]

    def classify(self, feedback: str) -> Tuple[str, float]:
        """Classify implicit sentiment.

        Args:
            feedback: User feedback text

        Returns:
            Tuple of (label: positive/negative/neutral, confidence)
        """
        if not feedback:
            return "neutral", 0.3

        pos_matches = sum(1 for p in self._pos_patterns if p.search(feedback))
        neg_matches = sum(1 for p in self._neg_patterns if p.search(feedback))

        if pos_matches > 0 and neg_matches == 0:
            return "positive", min(0.7, 0.4 + 0.15 * pos_matches)
        elif neg_matches > 0 and pos_matches == 0:
            return "negative", min(0.7, 0.4 + 0.15 * neg_matches)
        elif neg_matches > 0 and pos_matches > 0:
            # Mixed signals → neutral with low confidence
            return "neutral", 0.3

        # Check for curiosity/engagement
        curious = sum(1 for p in self._curiosity_patterns if p.search(feedback))
        if curious > 0:
            return "neutral", 0.5

        return "neutral", 0.2


class ConfidenceCalibrator:
    """Calibrate confidence scores based on historical accuracy.

    Tracks per-pattern accuracy to adjust confidence estimates.
    Higher reliability patterns get higher calibrated confidence.
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self._history: List[Tuple[str, bool, float]] = []  # (category, correct, raw_conf)

    def calibrate(self, label: str, raw_confidence: float,
                  pattern_category: Optional[str] = None) -> Tuple[str, float]:
        """Calibrate confidence using historical accuracy.

        Args:
            label: Classification label (positive/negative/neutral)
            raw_confidence: Raw confidence from classifiers
            pattern_category: Which pattern category was matched

        Returns:
            Tuple of (label, calibrated_confidence)
        """
        if not self._history:
            # No history: slightly reduce confidence
            return label, raw_confidence * 0.9

        # Calculate historical accuracy per category
        category_key = pattern_category or label
        category_history = [
            (correct, conf) for cat, correct, conf in self._history[-self.window_size:]
            if cat == category_key
        ]

        if not category_history:
            calibrated = raw_confidence * 0.9
        else:
            accuracy = sum(1 for c, _ in category_history if c) / len(category_history)
            avg_raw_conf = sum(conf for _, conf in category_history) / len(category_history)

            # Blend historical accuracy with raw confidence
            # ECE-inspired: push toward actual accuracy
            calibrated = 0.7 * raw_confidence + 0.3 * accuracy

            # If our confidence is consistently over/under confident, adjust
            if avg_raw_conf > 0 and abs(raw_confidence - accuracy) > 0.2:
                calibrated = raw_confidence * (accuracy / avg_raw_conf)

        return label, min(1.0, max(0.0, calibrated))

    def record(self, category: str, correct: bool, raw_confidence: float):
        """Record a judgment for calibration learning.

        Args:
            category: Pattern category
            correct: Whether the judgment was correct
            raw_confidence: Raw confidence score
        """
        self._history.append((category, correct, raw_confidence))
        if len(self._history) > self.window_size * 10:
            self._history = self._history[-self.window_size:]

    def get_accuracy(self, category: Optional[str] = None) -> float:
        """Get historical accuracy for a category, or overall."""
        if not self._history:
            return 0.0
        if category:
            relevant = [(c, cor) for c, cor, _ in self._history if c == category]
            if not relevant:
                return 0.0
            return sum(1 for _, cor in relevant if cor) / len(relevant)
        return sum(1 for _, cor, _ in self._history if cor) / len(self._history)


class EnhancedBinaryRLJudge:
    """Multi-signal binary feedback classification with confidence calibration.

    Combines four signal sources:
    1. PatternClassifier: fast regex-based explicit signals
    2. SemanticClassifier: implicit sentiment understanding
    3. Legacy BinaryRLJudge: for backward compatibility
    4. ConfidenceCalibrator: adjusts confidence from history

    Usage:
        judge = EnhancedBinaryRLJudge()
        result = judge.judge("thanks, great work!", context)
        # -> JudgeResult(is_positive=True, confidence=0.92, reward=1)
    """

    def __init__(self):
        self.pattern_classifier = PatternClassifier()
        self.semantic_classifier = SemanticClassifier()
        self.calibrator = ConfidenceCalibrator()
        self.legacy_judge = BinaryRLJudge()

        # Signal weights
        self.pattern_weight = 0.5
        self.semantic_weight = 0.3
        self.legacy_weight = 0.2

        self._stats = {"judgments": 0, "positive": 0, "negative": 0, "neutral": 0}

    def judge(
        self,
        feedback: str,
        context: Optional[Dict] = None,
    ) -> JudgeResult:
        """Classify feedback with multiple signals.

        Args:
            feedback: User feedback text
            context: Optional conversation context with action/history

        Returns:
            JudgeResult with reward, confidence, and signal details
        """
        self._stats["judgments"] += 1

        # Signal 1: Pattern classification (explicit signals)
        pat_label, pat_conf, pat_category = self.pattern_classifier.classify(feedback)

        # Signal 2: Semantic classification (implicit signals)
        sem_label, sem_conf = self.semantic_classifier.classify(feedback)

        # Signal 3: Legacy judge for backward compatibility
        try:
            reward, leg_conf = self.legacy_judge.judge(feedback, "")
            leg_label = "positive" if reward > 0 else ("negative" if reward < 0 else "neutral")
        except Exception:
            leg_label, leg_conf = "neutral", 0.3

        # Combine signals with weighted voting
        combined_label, combined_conf = self._combine_signals(
            pat_label, pat_conf,
            sem_label, sem_conf,
            leg_label, leg_conf,
        )

        # Signal 4: Confidence calibration
        calibrated_label, calibrated_conf = self.calibrator.calibrate(
            combined_label, combined_conf, pat_category
        )

        # Determine reward value
        reward = self._label_to_reward(calibrated_label)

        # Update stats
        self._stats[calibrated_label] += 1

        # Build reason string
        reason = self._build_reason(pat_label, sem_label, leg_label, calibrated_label)

        return JudgeResult(
            is_positive=calibrated_label == "positive",
            confidence=calibrated_conf,
            reward=reward,
            signals={
                "pattern": pat_conf,
                "semantic": sem_conf,
                "legacy": leg_conf,
            },
            pattern_matched=pat_category,
            semantic_label=sem_label,
            reason=reason,
        )

    def judge_with_details(
        self,
        feedback: str,
        context: Optional[Dict] = None,
    ) -> JudgeResult:
        """Alias for judge() with full result."""
        return self.judge(feedback, context)

    def record_validation(self, feedback: str, expected_label: str):
        """Record validated feedback for calibration.

        Args:
            feedback: Original feedback text
            expected_label: Ground truth label (positive/negative/neutral)
        """
        pat_label, pat_conf, pat_category = self.pattern_classifier.classify(feedback)
        correct = pat_label == expected_label
        self.calibrator.record(pat_category or pat_label, correct, pat_conf)

    def get_statistics(self) -> Dict:
        """Get judge statistics."""
        return {
            **self._stats,
            "accuracy": self.calibrator.get_accuracy(),
        }

    def _combine_signals(
        self,
        pat_label: str, pat_conf: float,
        sem_label: str, sem_conf: float,
        leg_label: str, leg_conf: float,
    ) -> Tuple[str, float]:
        """Combine multiple signals into a single label and confidence."""

        def label_value(label: str) -> int:
            return {"positive": 1, "neutral": 0, "negative": -1}.get(label, 0)

        # Weighted score
        weighted = (
            self.pattern_weight * pat_conf * label_value(pat_label) +
            self.semantic_weight * sem_conf * label_value(sem_label) +
            self.legacy_weight * leg_conf * label_value(leg_label)
        )

        total_weight = (
            self.pattern_weight * pat_conf +
            self.semantic_weight * sem_conf +
            self.legacy_weight * leg_conf
        )

        if total_weight == 0:
            return "neutral", 0.3

        normalized = weighted / total_weight

        # Confidence: average of contributing confidences weighted by agreement
        labels = [pat_label, sem_label, leg_label]
        majority = "neutral"

        # Count label agreement
        pos_votes = labels.count("positive")
        neg_votes = labels.count("negative")

        if pos_votes > neg_votes:
            majority = "positive"
        elif neg_votes > pos_votes:
            majority = "negative"

        # Average confidence of agreeing signals
        confs = []
        for label, conf in [(pat_label, pat_conf), (sem_label, sem_conf), (leg_label, leg_conf)]:
            if label == majority:
                confs.append(conf)
        avg_conf = sum(confs) / max(len(confs), 1)

        return majority, min(1.0, avg_conf)

    @staticmethod
    def _label_to_reward(label: str) -> int:
        return {"positive": 1, "negative": -1, "neutral": 0}.get(label, 0)

    @staticmethod
    def _build_reason(pat: str, sem: str, leg: str, final: str) -> str:
        parts = []
        if pat != "neutral":
            parts.append(f"pattern:{pat}")
        if sem != "neutral":
            parts.append(f"semantic:{sem}")
        if leg != "neutral":
            parts.append(f"legacy:{leg}")
        return f"{' + '.join(parts)} → {final}" if parts else f"all neutral → {final}"


__all__ = [
    'EnhancedBinaryRLJudge',
    'PatternClassifier',
    'SemanticClassifier',
    'ConfidenceCalibrator',
    'JudgeResult',
]
