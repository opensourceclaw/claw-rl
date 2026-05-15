"""
claw-rl Feedback Module

Binary RL and OPD Hint extraction for feedback-driven learning.
P0-3: Enhanced Binary RL + Improved OPD for >90% accuracy.
"""

from .binary_rl import BinaryRLJudge, RewardResult
from .opd_hint import OPDHint, OPDHintExtractor
from .llm_enhanced_prm import (
    LLMEnhancedPRMJudge,
    JudgeResult,
    LLMBackend,
)
from .collector import (
    Feedback,
    FeedbackType,
    FeedbackSource,
    FeedbackCollector,
)
from .storage import FeedbackStorage
from .implicit import (
    ImplicitSignalType,
    UserAction,
    ImplicitSignal,
    ImplicitFeedbackInference,
)
from .signal_fusion import (
    SignalSource,
    FusedSignal,
    SignalFusion,
    fuse_feedbacks,
)
# P0-3: Enhanced Binary RL + Improved OPD
from .enhanced_binary_rl import (
    EnhancedBinaryRLJudge,
    PatternClassifier,
    SemanticClassifier,
    ConfidenceCalibrator,
)
from .enhanced_opd import (
    ImprovedOPDExtractor,
    Hint,
    Priority,
    Scope,
)

__all__ = [
    # Binary RL
    'BinaryRLJudge',
    'RewardResult',
    # OPD Hint
    'OPDHint',
    'OPDHintExtractor',
    # LLM-Enhanced PRM
    'LLMEnhancedPRMJudge',
    'JudgeResult',
    'LLMBackend',
    # Feedback Collector
    'Feedback',
    'FeedbackType',
    'FeedbackSource',
    'FeedbackCollector',
    # Feedback Storage
    'FeedbackStorage',
    # Implicit Feedback
    'ImplicitSignalType',
    'UserAction',
    'ImplicitSignal',
    'ImplicitFeedbackInference',
    # Signal Fusion
    'SignalSource',
    'FusedSignal',
    'SignalFusion',
    'fuse_feedbacks',
    # P0-3 Enhanced Binary RL + Improved OPD
    'EnhancedBinaryRLJudge',
    'PatternClassifier',
    'SemanticClassifier',
    'ConfidenceCalibrator',
    'ImprovedOPDExtractor',
    'Hint',
    'Priority',
    'Scope',
]
