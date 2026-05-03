"""claw-rl v2.10.0 - Experience Quality Evaluator."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class QualityResult:
    score: float = 0.0
    is_quality: bool = False
    dimensions: Dict[str, float] = field(default_factory=dict)


class QualityEvaluator:
    """Evaluate experience quality for consolidation.

    Scores experiences on relevance, consistency, and impact.
    """

    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold

    def evaluate(self, experience: Dict[str, Any]) -> QualityResult:
        reward = experience.get("reward", 0.0)
        content_len = len(experience.get("content", ""))
        relevance = min(1.0, content_len / 100) if content_len > 0 else 0.0
        score = 0.5 * reward + 0.5 * relevance
        return QualityResult(
            score=round(score, 3),
            is_quality=score >= self.threshold,
            dimensions={"reward": reward, "relevance": relevance},
        )
