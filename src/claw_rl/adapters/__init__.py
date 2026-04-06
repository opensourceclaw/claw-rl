"""
Adapters - Framework-specific implementations

This module provides adapter implementations for various frameworks.
Adapters convert framework-specific data to common protocol formats.
"""

from .base_adapter import BaseObserverAdapter, BaseDecisionMakerAdapter, BaseExecutorAdapter, BaseSignalAdapter
from .openclaw_adapter import OpenClawObserverAdapter, OpenClawSignalAdapter

__all__ = [
    # Base adapters
    'BaseObserverAdapter',
    'BaseDecisionMakerAdapter',
    'BaseExecutorAdapter',
    'BaseSignalAdapter',
    # OpenClaw adapters
    'OpenClawObserverAdapter',
    'OpenClawSignalAdapter',
]
