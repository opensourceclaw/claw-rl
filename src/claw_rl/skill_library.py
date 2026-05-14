"""Skill Library — reusable skill storage and state-matched retrieval for claw-rl v3.0.0."""

import logging
import math
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """A reusable learned skill."""

    name: str
    state_pattern: str  # pattern matching trigger
    action: str         # what action to take
    reward: float = 0.0
    usage_count: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillLibrary:
    """Reusable skill storage with state-based retrieval.

    Stores (state, action, reward) tuples as skills, retrieves by
    pattern matching against current state, and supports RL-based
    reward updates for continuous improvement.
    """

    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._state_index: Dict[str, List[str]] = defaultdict(list)

    # ── CRUD ────────────────────────────────────────

    def add_skill(
        self,
        name: str,
        state_pattern: str,
        action: str,
        reward: float = 0.0,
        metadata: Optional[Dict] = None,
    ) -> Skill:
        """Register a new skill."""
        skill = Skill(
            name=name,
            state_pattern=state_pattern,
            action=action,
            reward=reward,
            metadata=metadata or {},
        )
        self._skills[skill.id] = skill
        self._index_state(skill)
        logger.debug("Skill added: %s (reward=%.2f)", name, reward)
        return skill

    def _index_state(self, skill: Skill) -> None:
        """Index skill by keywords in its state pattern."""
        keywords = set(skill.state_pattern.lower().split())
        for kw in keywords:
            self._state_index[kw].append(skill.id)

    # ── Query ───────────────────────────────────────

    def find_skills(self, state: str, top_k: int = 5) -> List[Skill]:
        """Find skills matching a given state description."""
        query_keywords = set(state.lower().split())
        if not query_keywords:
            return []

        scored: Dict[str, float] = {}
        for kw in query_keywords:
            for sid in self._state_index.get(kw, []):
                if sid in self._skills:
                    skill = self._skills[sid]
                    # Score: reward * usage bonus
                    usage_bonus = math.log(skill.usage_count + 1) * 0.1
                    scored[sid] = scored.get(sid, 0) + skill.reward * (1.0 + usage_bonus)

        sorted_ids = sorted(scored, key=scored.get, reverse=True)
        return [self._skills[sid] for sid in sorted_ids[:top_k]]

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self._skills.get(skill_id)

    # ── Improvement ──────────────────────────────

    def improve_skill(self, skill_id: str, reward_delta: float) -> bool:
        """RL-based reward update for a skill."""
        skill = self._skills.get(skill_id)
        if not skill:
            return False
        skill.reward = max(0.0, min(1.0, skill.reward + reward_delta))
        skill.usage_count += 1
        return True

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._skills)
        avg_reward = (
            sum(s.reward for s in self._skills.values()) / total
            if total else 0.0
        )
        return {
            "total_skills": total,
            "avg_reward": round(avg_reward, 4),
            "indexed_states": len(self._state_index),
        }
