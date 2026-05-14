"""Self-Play RL — zero-data reinforcement learning for claw-rl v3.0.0."""

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List

from claw_rl.triad import TriadArchitecture, TriadResult

logger = logging.getLogger(__name__)


@dataclass
class SelfPlayResult:
    """Result of a Self-Play RL session."""

    cycles: int = 0
    score_progression: List[float] = field(default_factory=list)
    final_level: float = 0.5
    skills_created: int = 0
    avg_learning_gain: float = 0.0


class SelfPlayRL:
    """Zero-data Self-Play reinforcement learning.

    Uses the Triad architecture in a closed loop:
    1. Proposer generates tasks at increasing difficulty
    2. Solver executes with learned skills
    3. Judge evaluates and provides feedback
    4. Skills improve, difficulty escalates
    """

    def __init__(self, triad: TriadArchitecture = None):
        self.triad = triad or TriadArchitecture()
        self._results: List[SelfPlayResult] = []

    def run_session(
        self,
        cycles: int = 20,
        start_level: float = 0.3,
        escalation: float = 0.05,
    ) -> SelfPlayResult:
        """Run a Self-Play session with escalating difficulty.

        Args:
            cycles: Number of triads to run
            start_level: Initial difficulty (0-1)
            escalation: Difficulty increase per cycle

        Returns:
            SelfPlayResult with progression metrics
        """
        level = start_level
        scores = []

        for _ in range(cycles):
            result = self.triad.run_cycle(level)
            scores.append(result.judgement.score)

            # Escalate difficulty on success, reduce on failure
            if result.judgement.success:
                level = min(1.0, level + escalation)
            else:
                level = max(0.1, level - escalation * 0.5)

            # Occasionally add a new skill from successful patterns
            if result.judgement.success and result.judgement.score > 0.7:
                self.triad.skill_library.add_skill(
                    name=f"auto_skill_{len(scores)}",
                    state_pattern=result.task.description,
                    action=f"Auto-learned action for: {result.task.description[:50]}",
                    reward=result.judgement.score,
                )

        stats = self.triad.get_stats()
        sp_result = SelfPlayResult(
            cycles=cycles,
            score_progression=scores,
            final_level=round(level, 2),
            skills_created=stats["skill_count"],
            avg_learning_gain=round(
                sum(r.learning_gain for r in self.triad._history[-cycles:]) / max(1, cycles), 4
            ),
        )
        self._results.append(sp_result)
        logger.info(
            "Self-Play complete: %d cycles, final level=%.2f, avg score=%.2f",
            cycles, level, sum(scores) / len(scores),
        )
        return sp_result

    def get_latest_result(self) -> SelfPlayResult:
        return self._results[-1] if self._results else SelfPlayResult()
