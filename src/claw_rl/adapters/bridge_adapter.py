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
RLBridgeAdapter: Core adapter wrapping claw-rl components with version strategy.

Responsibilities:
- Initialize core components (BinaryRLJudge, OPDHintExtractor, LearningLoop)
- Route bridge operations to the right component APIs
- Delegate response formatting to strategy
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .bridge_base import BaseBridgeStrategy


class RLBridgeAdapter:
    """
    Generic adapter for claw-rl bridge operations.

    Wraps the core components (BinaryRLJudge, OPDHintExtractor, LearningLoop)
    and delegates version-specific formatting to the strategy.
    """

    def __init__(self, strategy: BaseBridgeStrategy):
        self.strategy = strategy
        self.binary_rl = None
        self.opd_hint = None
        self.learning_loop = None
        self.workspace: Optional[str] = None

    @property
    def version(self) -> str:
        return self.strategy.get_version()

    @property
    def initialized(self) -> bool:
        return self.learning_loop is not None

    @property
    def components(self) -> Dict[str, bool]:
        return {
            "binary_rl": self.binary_rl is not None,
            "opd_hint": self.opd_hint is not None,
            "learning_loop": self.learning_loop is not None,
        }

    # ---- Initialization -----------------------------------------------

    def initialize(self, workspace: str) -> Dict[str, Any]:
        """Initialize core components from the configured strategy."""
        self.workspace = workspace
        data_dir = Path(workspace) / "data" / "claw-rl"

        # Import here to avoid module-level deps
        from claw_rl.core.learning_loop import LearningLoop
        self.learning_loop = LearningLoop(data_dir=data_dir)

        if self.strategy.supports_judge():
            from claw_rl.feedback.binary_rl import BinaryRLJudge
            self.binary_rl = BinaryRLJudge()

        if self.strategy.supports_hint():
            from claw_rl.feedback.opd_hint import OPDHintExtractor
            self.opd_hint = OPDHintExtractor()

        return self.strategy.get_initialize_response(workspace)

    # ---- Operations ---------------------------------------------------

    def collect_feedback(self, feedback: str, action: str = "", context: str = "") -> Dict[str, Any]:
        if not self.initialized:
            return {"error": "Bridge not initialized"}

        if self.binary_rl:
            # V2 path: use BinaryRLJudge for direct reward
            reward, confidence = self.binary_rl.judge(feedback=feedback, action=action)
            result = self.strategy.format_collect_feedback_result(reward, confidence)
        else:
            # V1 path: use LearningLoop.process_feedback
            result_raw = self.learning_loop.process_feedback(feedback, action, context)
            result = self.strategy.format_collect_feedback_result(
                result_raw.get("reward", 0),
                hints=result_raw.get("hints", []),
            )
        return result

    def extract_hint(self, feedback: str) -> Dict[str, Any]:
        if not self.initialized:
            return {"error": "Bridge not initialized"}

        if self.opd_hint:
            hint = self.opd_hint.extract(feedback=feedback)
            return self.strategy.format_extract_hint_result(hint)
        else:
            return self.strategy.format_extract_hint_result(None)

    def get_rules(self, top_k: int = 10, context: str = "") -> Dict[str, Any]:
        if not self.initialized:
            return {"error": "Bridge not initialized"}

        if context:
            learnings = self.learning_loop.get_recent_learnings(
                limit=top_k, context_filter=context
            )
        else:
            learnings = self.learning_loop.get_recent_learnings(limit=top_k)

        rules = self.strategy.format_rules(learnings, context)

        return {
            "status": "success",
            "rules": rules,
            "count": len(rules),
        }

    def status(self) -> Dict[str, Any]:
        if not self.initialized:
            return {"error": "Bridge not initialized"}

        stats = self.learning_loop.get_statistics()
        base = self.strategy.format_status(stats, self.components)
        base["workspace"] = self.workspace or ""
        return base

    def process_learning(self) -> Dict[str, Any]:
        if not self.initialized:
            return {"error": "Bridge not initialized"}

        stats = self.learning_loop.get_statistics()
        return {
            "status": "success",
            "statistics": stats,
        }

    def shutdown(self, request_count: int = 0, avg_latency: float = 0.0) -> Dict[str, Any]:
        return self.strategy.format_shutdown_response(request_count, avg_latency)

    def ping(self) -> Dict[str, Any]:
        return {"pong": True}
