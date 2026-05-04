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
BridgeAdapterRegistry: Version detection and strategy/adapter factory for bridges.

Detection priority:
1. OPENCLAW_VERSION environment variable
2. Configuration file (~/.openclaw/openclaw.json)
3. Default: v2 (current)
"""

import json
import os
from pathlib import Path
from typing import Optional

from .bridge_base import BaseBridgeStrategy, BridgeAdapterError
from .bridge_v1 import V1BridgeStrategy
from .bridge_v2 import V2BridgeStrategy
from .bridge_adapter import RLBridgeAdapter


class BridgeAdapterRegistry:
    """Factory for creating version-appropriate bridge adapters."""

    _strategies = {
        "v1": V1BridgeStrategy,
        "1": V1BridgeStrategy,
        "v2": V2BridgeStrategy,
        "2": V2BridgeStrategy,
    }

    @classmethod
    def detect_version_key(cls) -> str:
        """Detect the OpenClaw version key for bridge strategy selection."""
        # 1. Environment variable
        env_version = os.environ.get("OPENCLAW_VERSION")
        if env_version:
            env_version = env_version.strip()
            major = env_version.split(".")[0]
            key = f"v{major}"
            if key in cls._strategies:
                return key
            return key

        # 2. Configuration file
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        try:
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                    version = str(config.get("version", "2")).strip()
                    major = version.split(".")[0]
                    key = f"v{major}"
                    if key in cls._strategies:
                        return key
                    return key
        except (json.JSONDecodeError, IOError, OSError):
            pass

        # 3. Default
        return "v2"

    @classmethod
    def create_strategy(cls, version_key: Optional[str] = None) -> BaseBridgeStrategy:
        """Create a version-specific bridge strategy."""
        if version_key is None:
            version_key = cls.detect_version_key()

        strategy_cls = cls._strategies.get(version_key)
        if strategy_cls is None:
            raise BridgeAdapterError(
                f"Unknown bridge adapter version: '{version_key}'. "
                f"Supported: {list(cls._strategies.keys())}"
            )

        return strategy_cls()

    @classmethod
    def create_adapter(cls, version_key: Optional[str] = None) -> RLBridgeAdapter:
        """Create a full RLBridgeAdapter with the detected strategy."""
        strategy = cls.create_strategy(version_key)
        return RLBridgeAdapter(strategy)
