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
V2BridgeStrategy: OpenClaw v2.x bridge strategy.

Features:
- BinaryRLJudge for direct reward judgment
- OPDHintExtractor for hint extraction
- Component-based status reporting
"""

from typing import Any, Dict, List

from .bridge_base import BaseBridgeStrategy


class V2BridgeStrategy(BaseBridgeStrategy):
    """Strategy for OpenClaw v2.x (current, component-based)."""

    def get_version(self) -> str:
        return "2.0.0"

    def get_initialize_response(self, workspace: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "workspace": workspace,
        }

    def format_collect_feedback_result(
        self, reward: Any, confidence: Any = None, hints: List = None
    ) -> Dict[str, Any]:
        return {
            "status": "success",
            "reward": reward,
            "confidence": confidence if confidence is not None else 0.0,
        }

    def format_extract_hint_result(self, hint: Any) -> Dict[str, Any]:
        if hint:
            return {
                "status": "success",
                "hint": hint.to_dict() if hasattr(hint, "to_dict") else str(hint),
            }
        return {"status": "success", "hint": None}

    def format_rules(self, learnings: List[Any], context: str = "") -> List[Dict[str, Any]]:
        if not learnings:
            return []
        rules = []
        if learnings:
            for learning in learnings:
                if isinstance(learning, dict):
                    rules.append({
                        "content": learning.get("hint", str(learning)),
                        "score": learning.get("score", 1.0),
                    })
                else:
                    rules.append({
                        "content": str(learning),
                        "score": 1.0,
                    })
        return rules

    def format_status(self, stats: Dict[str, Any], components: Dict[str, bool]) -> Dict[str, Any]:
        return {
            "initialized": True,
            "components": components,
        }

    def format_shutdown_response(self, request_count: int, avg_latency: float) -> Dict[str, Any]:
        return {
            "status": "success",
            "total_requests": request_count,
            "avg_latency_ms": avg_latency,
        }

    def supports_judge(self) -> bool:
        return True

    def supports_hint(self) -> bool:
        return True

    def supports_ping(self) -> bool:
        return False
