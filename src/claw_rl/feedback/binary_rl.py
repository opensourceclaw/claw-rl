"""
Binary RL Judge - Reward judgment from user feedback

This module implements binary reinforcement learning reward judgment
based on pattern matching of user feedback.
"""

import re
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class RewardResult:
    """Binary RL reward result."""
    reward: int  # -1, 0, or +1
    confidence: float  # 0.0 to 1.0
    pattern_matched: Optional[str]  # Which pattern matched (for debugging)


class BinaryRLJudge:
    """
    Binary RL reward judge with pattern matching.
    
    Analyzes user feedback to determine reward signals:
    - +1: Positive feedback (thanks，great，etc.)
    - 0: Neutral feedback
    - -1: Negative feedback (incorrect，wrong，should，etc.)
    
    Example:
        >>> judge = BinaryRLJudge()
        >>> reward, confidence = judge.judge("thanks，great！", "created file")
        >>> print(reward)
        1
    """
    
    # Positive feedback patterns (thanks，great，etc.)
    POSITIVE_PATTERNS: List[str] = [
        # Gratitude
        r'thanks',
        r'thank you',
        r'多谢',
        r'太thank you了',
        
        # Approval
        r'great',
        r'awesome',
        r'good',
        r'okay',
        r'correct',
        r'对了',
        r'perfect',
        r'satisfied',
        r'like',
        r'赞同',
        r'支持',
        
        # Continuation (implies satisfaction)
        r'continue',
        r'again',
        r'还有吗',
        
        # Emoji (positive)
        r'👍',
        r'👌',
        r'✅',
        r'😊',
        r'😄',
    ]
    
    # Negative feedback patterns (incorrect，wrong，should，etc.)
    NEGATIVE_PATTERNS: List[str] = [
        # Incorrect
        r'incorrect',
        r'wrong',
        r'error',
        r'notcorrect',
        r'错的',
        r'有问题',
        
        # Correction
        r'should',
        r'should是',
        r'要',
        r'need',
        r'得',
        
        # Dissatisfaction
        r'notsatisfied',
        r'notlike',
        r'反对',
        r'disappointed',
        r'not好',
        
        # Rejection
        r"don't",
        r"don't",
        r'not',
        r'incorrect',
        
        # Questioning
        r'为什么',
        r'怎么',
        r'难道',
    ]
    
    def __init__(self):
        """Initialize the Binary RL Judge."""
        # Compile patterns for efficiency
        self._positive_regex = [re.compile(p) for p in self.POSITIVE_PATTERNS]
        self._negative_regex = [re.compile(p) for p in self.NEGATIVE_PATTERNS]
    
    def judge(self, feedback: str, action: Optional[str] = None) -> Tuple[int, float]:
        """
        Judge reward from user feedback.
        
        Args:
            feedback: User feedback text
            action: Optional action context (for future use)
        
        Returns:
            (reward, confidence): 
                - reward: +1 (positive), 0 (neutral), -1 (negative)
                - confidence: 0.0 to 1.0, confidence in the judgment
        
        Examples:
            >>> judge = BinaryRLJudge()
            >>> judge.judge("thanks，great！")
            (1, 0.9)
            
            >>> judge.judge("incorrect，shouldput here")
            (-1, 0.95)
            
            >>> judge.judge("嗯")
            (0, 0.5)
        """
        if not feedback or not feedback.strip():
            return (0, 0.0)
        
        # Check negative patterns FIRST (corrections are more important)
        for i, regex in enumerate(self._negative_regex):
            if regex.search(feedback):
                pattern_name = self.NEGATIVE_PATTERNS[i]
                # Higher confidence for explicit correction patterns
                confidence = 0.95 if 'should' in pattern_name or 'wrong' in pattern_name else 0.9
                return (-1, confidence)
        
        # Check positive patterns
        for i, regex in enumerate(self._positive_regex):
            if regex.search(feedback):
                pattern_name = self.POSITIVE_PATTERNS[i]
                # Higher confidence for explicit patterns
                confidence = 0.95 if 'thanks' in pattern_name or 'great' in pattern_name else 0.9
                return (+1, confidence)
        
        # Neutral (no pattern matched)
        return (0, 0.5)
    
    def judge_with_reason(self, feedback: str, action: Optional[str] = None) -> RewardResult:
        """
        Judge reward with detailed reason.
        
        Args:
            feedback: User feedback text
            action: Optional action context
        
        Returns:
            RewardResult with reward, confidence, and matched pattern
        
        Example:
            >>> judge = BinaryRLJudge()
            >>> result = judge.judge_with_reason("thanks！")
            >>> print(result.reward)
            1
            >>> print(result.pattern_matched)
            'thanks'
        """
        if not feedback or not feedback.strip():
            return RewardResult(reward=0, confidence=0.0, pattern_matched=None)
        
        feedback_lower = feedback.lower()
        
        # Check negative patterns FIRST (corrections are more important)
        for i, regex in enumerate(self._negative_regex):
            if regex.search(feedback_lower):
                return RewardResult(
                    reward=-1,
                    confidence=0.95 if 'should' in self.NEGATIVE_PATTERNS[i] or 'wrong' in self.NEGATIVE_PATTERNS[i] else 0.9,
                    pattern_matched=self.NEGATIVE_PATTERNS[i]
                )
        
        # Check positive patterns
        for i, regex in enumerate(self._positive_regex):
            if regex.search(feedback_lower):
                return RewardResult(
                    reward=+1,
                    confidence=0.95 if 'thanks' in self.POSITIVE_PATTERNS[i] or 'great' in self.POSITIVE_PATTERNS[i] else 0.9,
                    pattern_matched=self.POSITIVE_PATTERNS[i]
                )
        
        # Neutral
        return RewardResult(reward=0, confidence=0.5, pattern_matched=None)
    
    def get_statistics(self) -> dict:
        """
        Get statistics about pattern coverage.
        
        Returns:
            Dictionary with pattern counts and info
        
        Example:
            >>> judge = BinaryRLJudge()
            >>> stats = judge.get_statistics()
            >>> print(stats['positive_patterns'])
            20
        """
        return {
            'positive_patterns': len(self.POSITIVE_PATTERNS),
            'negative_patterns': len(self.NEGATIVE_PATTERNS),
            'total_patterns': len(self.POSITIVE_PATTERNS) + len(self.NEGATIVE_PATTERNS),
        }
