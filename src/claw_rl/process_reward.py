"""Process Reward Model — step-level reward evaluation for claw-rl v3.0.0."""

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProcessRewardResult:
    """Result of process-level reward evaluation."""

    scores: List[float] = field(default_factory=list)
    weighted_score: float = 0.0
    feedback: str = ""
    total_steps: int = 0


class ProcessRewardModel:
    """Step-level reward evaluation with weighted scoring.

    Evaluates each step in a multi-step process and generates
    a natural language feedback summary plus a weighted composite score.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            "correctness": 0.4,
            "efficiency": 0.2,
            "completeness": 0.2,
            "clarity": 0.2,
        }

    def evaluate_step(self, description: str, outcome: float) -> float:
        """Evaluate a single step and return a reward score.

        Score is a combination of outcome and heuristics:
        - Outcome contributes 60%
        - Description quality contributes 40% (length, keywords)
        """
        outcome_score = max(0.0, min(1.0, outcome))

        # Heuristic quality from description
        quality = 0.5  # baseline
        if len(description) > 20:
            quality += 0.1
        for kw in ["completed", "success", "correct", "optimal"]:
            if kw in description.lower():
                quality += 0.05

        return round(outcome_score * 0.6 + min(1.0, quality) * 0.4, 4)

    def evaluate_sequence(
        self, steps: List[Dict[str, Any]]
    ) -> ProcessRewardResult:
        """Evaluate a sequence of steps and produce a weighted result.

        Args:
            steps: List of {"description": str, "outcome": float} dicts

        Returns:
            ProcessRewardResult with scores and feedback
        """
        scores = []
        for i, step in enumerate(steps):
            desc = step.get("description", f"step_{i}")
            outcome = step.get("outcome", 0.5)
            score = self.evaluate_step(desc, outcome)
            scores.append(score)

        result = ProcessRewardResult(
            scores=scores,
            weighted_score=self.get_weighted_score(scores),
            total_steps=len(steps),
        )

        # Generate feedback
        avg = result.weighted_score
        if avg > 0.8:
            result.feedback = "Process executed excellently across all steps."
        elif avg > 0.6:
            result.feedback = "Process completed adequately, minor improvements possible."
        elif avg > 0.4:
            result.feedback = "Process needs improvement in several areas."
        else:
            result.feedback = "Process requires significant revision."

        logger.debug("Process reward: avg=%.2f across %d steps", avg, len(steps))
        return result

    def get_weighted_score(self, scores: List[float]) -> float:
        """Compute weighted average of step scores."""
        if not scores:
            return 0.0
        # Apply exponential weighting: later steps matter less
        n = len(scores)
        decay = sum(
            scores[i] * math.exp(-0.1 * (n - 1 - i)) for i in range(n)
        )
        norm = sum(math.exp(-0.1 * (n - 1 - i)) for i in range(n))
        return round(decay / norm, 4) if norm > 0 else 0.0
