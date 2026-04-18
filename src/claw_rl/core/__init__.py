"""
Core - Core components for C-P-A learning loop

This module provides the core C-P-A (Continuous Planning and Autonomous)
learning loop implementation.
"""

from .cpa_loop import CPALoop, CPALoopConfig
from .bridge import ClawRLBridge
from .learning_loop import LearningLoop
from .memory_bridge import ClawMemBridge
from .learning_daemon import LearningDaemon
from .memory_consciousness_sync import (
    MemoryConsciousnessSync,
    Learning,
    SyncResult,
    SyncDirection,
    SyncStatus,
)

__all__ = [
    # C-P-A Loop (Sprint 3)
    'CPALoop',
    'CPALoopConfig',
    # Legacy (Sprint 1-2)
    'LearningLoop',
    'ClawRLBridge',
    'ClawMemBridge',
    'LearningDaemon',
    # v2.1.0 Memory-Consciousness Sync
    'MemoryConsciousnessSync',
    'Learning',
    'SyncResult',
    'SyncDirection',
    'SyncStatus',
]
