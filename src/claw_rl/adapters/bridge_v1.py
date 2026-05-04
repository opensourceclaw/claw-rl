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
V1BridgeStrategy: OpenClaw v1.x backward-compatible bridge strategy.

Simplified features:
- LearningLoop only (no BinaryRLJudge or OPDHintExtractor)
- Ping support
- Rules with pattern/response/source/reward fields
"""

from typing import Any, Dict, List

from .bridge_base import BaseBridgeStrategy


class V1BridgeStrategy(BaseBridgeStrategy):
    """Strategy for OpenClaw v1.x (backward-compatible, LearningLoop-only)."""

    def get_version(self) -> str:
        return "1.0.0"

    def get_initialize_response(self, workspace: str) -> Dict[str, Any]:
        return {"status": "ok", "message": "initialized", "workspace": workspace}

    def format_collect_feedback_result(
        self, reward: Any, confidence: Any = None, hints: List = None
    ) -> Dict[str, Any]:
        return {
            "status": "feedback_collected",
            "reward": reward,
            "hints": hints or [],
        }

    def format_extract_hint_result(self, hint: Any) -> Dict[str, Any]:
        return {"status": "error", "error": "Hint extraction not supported in v1"}

    def format_rules(self, learnings: List[Any], context: str = "") -> List[Dict[str, Any]]:
        if not learnings:
            return []
        rules = []
        for r in learnings:
            if isinstance(r, dict):
                for h in r.get("hints", []):
                    rules.append({
                        "pattern": h.get("hint_type", ""),
                        "response": h.get("content", ""),
                        "source": "hint",
                        "reward": r.get("reward", 0),
                        "feedback": r.get("feedback", "")[:100],
                    })
                rules.append({
                    "pattern": "learned",
                    "response": r.get("feedback", "")[:200],
                    "source": "feedback",
                    "reward": r.get("reward", 0),
                    "action": r.get("action", "")[:100],
                })
            else:
                rules.append({
                    "pattern": "learned",
                    "response": str(r)[:200],
                    "source": "feedback",
                    "reward": 0,
                    "action": "",
                })
        return rules

    def format_status(self, stats: Dict[str, Any], components: Dict[str, bool]) -> Dict[str, Any]:
        return {
            "status": "ok",
            "initialized": components.get("learning_loop", False),
            "statistics": stats,
        }

    def format_shutdown_response(self, request_count: int, avg_latency: float) -> Dict[str, Any]:
        return {"status": "shutting_down"}

    def supports_judge(self) -> bool:
        return False

    def supports_hint(self) -> bool:
        return False

    def supports_ping(self) -> bool:
        return True
