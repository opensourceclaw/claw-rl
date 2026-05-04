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
Bridge adapter base classes for claw-rl OpenClaw version decoupling.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BridgeAdapterError(Exception):
    """Error raised for bridge adapter issues (version detection, config)."""
    pass


class BaseBridgeStrategy(ABC):
    """
    Abstract strategy for version-specific bridge behavior.

    Each strategy encapsulates:
    - What core components to create during initialization
    - How to format responses for collect_feedback, extract_hint, get_rules, status
    - Which optional features are supported (judge, hint extraction, ping)
    """

    @abstractmethod
    def get_version(self) -> str:
        """Return the targeted OpenClaw version string."""
        ...

    @abstractmethod
    def get_initialize_response(self, workspace: str) -> Dict[str, Any]:
        """Build the initialize response dict."""
        ...

    @abstractmethod
    def format_collect_feedback_result(
        self, reward: Any, confidence: Any = None, hints: List = None
    ) -> Dict[str, Any]:
        """Normalize feedback processing results into version-specific dict."""
        ...

    @abstractmethod
    def format_extract_hint_result(self, hint: Any) -> Dict[str, Any]:
        """Normalize hint extraction result."""
        ...

    @abstractmethod
    def format_rules(self, learnings: List[Any], context: str = "") -> List[Dict[str, Any]]:
        """Convert raw learnings into version-specific rule dicts."""
        ...

    @abstractmethod
    def format_status(self, stats: Dict[str, Any], components: Dict[str, bool]) -> Dict[str, Any]:
        """Build version-specific status response."""
        ...

    @abstractmethod
    def format_shutdown_response(self, request_count: int, avg_latency: float) -> Dict[str, Any]:
        """Build version-specific shutdown response."""
        ...

    def supports_judge(self) -> bool:
        """Whether BinaryRLJudge is available for direct reward judgment."""
        return False

    def supports_hint(self) -> bool:
        """Whether OPDHintExtractor is available for hint extraction."""
        return False

    def supports_ping(self) -> bool:
        """Whether the ping handler is supported."""
        return False
