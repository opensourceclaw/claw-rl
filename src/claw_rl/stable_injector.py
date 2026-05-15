"""Stable Rule Injector — dual-confirmation + auto-rollback for claw-rl v2.13.0."""

import copy
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StableRuleInjector:
    """Rule injection with backup, verification, and automatic rollback."""

    def __init__(self):
        self._rules: List[Dict] = []
        self._backups: List[List[Dict]] = []
        self._injection_log: List[Dict] = []

    def inject_rule(self, rule: Dict) -> bool:
        """Inject a rule with backup-verify-commit cycle."""
        # 1. Backup
        backup = copy.deepcopy(self._rules)
        self._backups.append(backup)

        # 2. Inject
        self._rules.append(rule)

        # 3. Verify
        if self._verify_rule(rule):
            self._log(rule, True)
            return True

        # 4. Rollback on failure
        self._rules = self._backups.pop()
        self._log(rule, False)
        logger.warning("Rule injection failed, rolled back")
        return False

    def inject_batch(self, rules: List[Dict]) -> int:
        """Inject multiple rules, return success count."""
        return sum(1 for r in rules if self.inject_rule(r))

    def _verify_rule(self, rule: Dict) -> bool:
        """Verify rule is valid after injection."""
        # Check rule is present
        if rule not in self._rules:
            return False
        # Check required fields
        if not rule.get("name"):
            return False
        return True

    def _log(self, rule: Dict, success: bool) -> None:
        self._injection_log.append({"rule": rule.get("name"), "success": success})

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._injection_log)
        successes = sum(1 for e in self._injection_log if e["success"])
        return {
            "total_rules": len(self._rules),
            "total_injections": total,
            "success_rate": round(successes / max(1, total), 4),
        }
