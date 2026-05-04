"""
Adapters - Framework-specific implementations

This module provides adapter implementations for various frameworks.
Adapters convert framework-specific data to common protocol formats.
"""

from .base_adapter import BaseObserverAdapter, BaseDecisionMakerAdapter, BaseExecutorAdapter, BaseSignalAdapter
from .openclaw_adapter import OpenClawObserverAdapter, OpenClawSignalAdapter

# Bridge adapters (version-strategy pattern for OpenClaw bridge decoupling)
from .bridge_base import BaseBridgeStrategy, BridgeAdapterError
from .bridge_v1 import V1BridgeStrategy
from .bridge_v2 import V2BridgeStrategy
from .bridge_adapter import RLBridgeAdapter
from .bridge_registry import BridgeAdapterRegistry

__all__ = [
    # Base adapters
    'BaseObserverAdapter',
    'BaseDecisionMakerAdapter',
    'BaseExecutorAdapter',
    'BaseSignalAdapter',
    # OpenClaw adapters
    'OpenClawObserverAdapter',
    'OpenClawSignalAdapter',
    # Bridge adapters
    'BaseBridgeStrategy',
    'BridgeAdapterError',
    'V1BridgeStrategy',
    'V2BridgeStrategy',
    'RLBridgeAdapter',
    'BridgeAdapterRegistry',
]
