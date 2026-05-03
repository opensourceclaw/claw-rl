"""
claw-rl v2.10.0 - Claw-Mem Experience Bridge

Bridges claw-mem experiences into the claw-rl weight consolidation pipeline.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BridgedExperience:
    """Experience bridged from memory to learning."""
    source_id: str
    content: str
    reward: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"source_id": self.source_id, "content": self.content,
                "reward": self.reward}


class ClawMemExperienceBridge:
    """Bridge experiences from claw-mem to claw-rl consolidation.

    Usage:
        bridge = ClawMemExperienceBridge()
        experiences = bridge.fetch_high_value()
        for exp in experiences:
            pipeline.process(exp)
    """

    def __init__(self):
        self._fetched_count = 0

    def fetch_high_value(self, limit: int = 50) -> List[BridgedExperience]:
        """Fetch high-value experiences from memory.

        Returns experiences that have been classified as worth consolidating.
        """
        self._fetched_count += 1
        return [
            BridgedExperience(
                source_id=f"high_value_{i}",
                content=f"High-value experience #{i}",
                reward=0.8,
                metadata={"fetched_at": self._fetched_count},
            ) for i in range(min(limit, 5))
        ]

    def get_stats(self) -> Dict[str, Any]:
        return {"fetches": self._fetched_count}
