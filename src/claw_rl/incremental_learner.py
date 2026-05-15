"""Incremental Learner — fast learning cycle for claw-rl v2.13.0."""

import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class IncrementalLearner:
    """Immediate high-priority learning + batched low-priority learning.

    Reduces perceived learning cycle from ~48h to <12h.
    """

    def __init__(self, merge_interval: float = 3600):
        self.merge_interval = merge_interval
        self._pending: List[Dict] = []
        self._applied: List[Dict] = []
        self._last_merge = time.time()

    def learn_immediate(self, feedback: Dict) -> Optional[Dict]:
        """Immediately learn high-priority feedback."""
        if feedback.get("priority", "normal") == "high":
            rule = self._extract_rule(feedback)
            self._applied.append(rule)
            logger.info("Immediate rule applied: %s", rule.get("name"))
            return rule
        self._pending.append(feedback)
        return None

    def learn_batch(self) -> List[Dict]:
        """Batch-merge low-priority feedback if interval elapsed."""
        now = time.time()
        if now - self._last_merge < self.merge_interval:
            return []
        if not self._pending:
            return []

        merged = self._merge_rules(self._pending)
        self._applied.extend(merged)
        self._pending.clear()
        self._last_merge = now
        logger.info("Batch merged %d rules", len(merged))
        return merged

    def _extract_rule(self, feedback: Dict) -> Dict:
        return {
            "name": feedback.get("action", "auto_rule"),
            "reward": feedback.get("reward", 0.5),
            "pattern": feedback.get("context", ""),
            "timestamp": time.time(),
        }

    def _merge_rules(self, pending: List[Dict]) -> List[Dict]:
        """Merge similar pending rules."""
        merged = []
        seen = set()
        for fb in pending:
            key = fb.get("action", "")
            if key not in seen:
                seen.add(key)
                merged.append(self._extract_rule(fb))
        return merged

    def get_stats(self) -> Dict[str, Any]:
        return {"applied": len(self._applied), "pending": len(self._pending), "last_merge": self._last_merge}
