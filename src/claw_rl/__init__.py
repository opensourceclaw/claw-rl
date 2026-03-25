"""
claw-rl - OpenClaw Reinforcement Learning System

Product Brand: NeoMind
Binary RL and OPD Learning for OpenClaw.
"""

__version__ = "0.7.0"
__author__ = "Peter Cheng"
__email__ = "peter@neoclaw.org"
__description__ = "claw-rl - Binary RL and OPD Learning (Product Brand: NeoMind)"

from .binary_rl import BinaryRLJudge
from .opd_hint import OPDHint, OPDHintExtractor
from .learning_loop import LearningLoop

__all__ = [
    "BinaryRLJudge",
    "OPDHint",
    "OPDHintExtractor",
    "LearningLoop",
]
