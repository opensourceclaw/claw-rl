"""
Protocols - Abstract interfaces for framework-agnostic learning

This module defines abstract protocols (interfaces) that enable claw-rl
to work with any framework through adapter implementations.
"""

from .observer import ObserverProtocol
from .decision_maker import DecisionMakerProtocol
from .executor import ExecutorProtocol
from .signal_adapter import SignalAdapterProtocol

__all__ = [
    'ObserverProtocol',
    'DecisionMakerProtocol',
    'ExecutorProtocol',
    'SignalAdapterProtocol',
]
