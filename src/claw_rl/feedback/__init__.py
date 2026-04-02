"""
claw-rl Feedback Module

Binary RL and OPD Hint extraction for feedback-driven learning.
"""

from .binary_rl import BinaryRLJudge, RewardResult
from .opd_hint import OPDHint, OPDHintExtractor
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

__all__ = [
    # Binary RL
    'BinaryRLJudge',
    'RewardResult',
    # OPD Hint
    'OPDHint',
    'OPDHintExtractor',
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
]
