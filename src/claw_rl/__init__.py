"""
claw-rl: Self-Learning Module for AI Agents

This package provides self-learning capabilities for AI agents:
- Pattern Recognition: Recognize patterns from historical memory
- Feedback Loop: Optimize policies based on feedback
- Core: Learning loop, daemon, and memory bridge
- Learning: Calibration, strategy, and value learning
- Context: Context-aware learning
- Hooks: Pre/post session hooks

Version: 2.0.0-beta.3
"""

__version__ = "2.0.0-rc.2"
__author__ = "OpenClaw Team"

# Pattern Recognition (Sprint 1)
from .pattern import (
    PatternRecognitionEngine,
    Pattern,
    Anomaly,
    PatternType,
    AnomalyType,
    PatternRecognitionResult,
    recognize_patterns
)

# Feedback Loop (v2.0.0b2 migrated)
from .feedback import (
    BinaryRLJudge,
    RewardResult,
    OPDHint,
    OPDHintExtractor,
)

# Core
from .core import (
    LearningLoop,
    ClawRLBridge,
    ClawMemBridge,
    LearningDaemon,
    CPALoop,
    CPALoopConfig,
)

# Learning
from .learning import (
    CalibrationLearner,
    StrategyLearner,
    ValuePreferenceLearner,
)

# Context
from .context import (
    ContextLearner,
)

# Hooks
from .hooks import (
    PreSessionHook,
    PostSessionHook,
)

# Auto-activate
from .auto_activate import (
    AutoActivator,
    get_activator,
    is_active,
)

__all__ = [
    # Version
    '__version__',
    '__author__',
    
    # Pattern Recognition
    'PatternRecognitionEngine',
    'Pattern',
    'Anomaly',
    'PatternType',
    'AnomalyType',
    'PatternRecognitionResult',
    'recognize_patterns',
    
    # Feedback
    'BinaryRLJudge',
    'RewardResult',
    'OPDHint',
    'OPDHintExtractor',
    
    # Core
    'LearningLoop',
    'ClawRLBridge',
    'ClawMemBridge',
    'LearningDaemon',
    'CPALoop',
    'CPALoopConfig',
    
    # Learning
    'CalibrationLearner',
    'StrategyLearner',
    'ValuePreferenceLearner',
    
    # Context
    'ContextLearner',
    
    # Hooks
    'PreSessionHook',
    'PostSessionHook',
    
    # Auto-activate
    'AutoActivator',
    'get_activator',
    'is_active',
]
