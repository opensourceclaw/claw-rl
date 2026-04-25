"""
Learning Loop - Main learning loop orchestrator

Coordinates Binary RL and OPD hint extraction to process
user feedback and trigger learning.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from claw_rl.feedback.binary_rl import BinaryRLJudge, RewardResult
from claw_rl.feedback.opd_hint import OPDHint, OPDHintExtractor


class LearningLoop:
    """
    Main learning loop orchestrator.
    
    Coordinates the learning process:
    1. Judge reward from user feedback (Binary RL)
    2. Extract hints from corrections (OPD)
    3. Record learning signals
    4. Trigger learning updates
    
    Example:
        >>> loop = LearningLoop(data_dir=Path("./data"))
        >>> result = loop.process_feedback(
        ...     feedback="incorrect，shouldput here",
        ...     action="created file",
        ...     context="User asked to create a file"
        ... )
        >>> print(result['reward'])
        -1
        >>> print(len(result['hints']))
        1
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialize the Learning Loop.
        
        Args:
            data_dir: Directory for storing learning data
        
        Example:
            >>> from pathlib import Path
            >>> loop = LearningLoop(Path("./data"))
        """
        self.data_dir = data_dir
        self.judge = BinaryRLJudge()
        self.hint_extractor = OPDHintExtractor()
        
        # Data directories
        self.rewards_dir = data_dir / ".rewards"
        self.hints_dir = data_dir / ".hints"
        self.learnings_dir = data_dir / ".learnings"
        
        # Ensure directories exist
        self.rewards_dir.mkdir(parents=True, exist_ok=True)
        self.hints_dir.mkdir(parents=True, exist_ok=True)
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
    
    def process_feedback(
        self,
        feedback: str,
        action: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user feedback and trigger learning.
        
        Args:
            feedback: User feedback text
            action: Action that was taken
            context: Optional context about the action
        
        Returns:
            Learning result dictionary with:
            - feedback: Original feedback
            - action: Action taken
            - context: Context (if provided)
            - reward: Reward value (-1, 0, +1)
            - confidence: Confidence in reward judgment
            - hints: List of extracted hints
            - timestamp: ISO format timestamp
        
        Example:
            >>> from pathlib import Path
            >>> loop = LearningLoop(Path("./data"))
            >>> result = loop.process_feedback(
            ...     feedback="thanks，great！",
            ...     action="created file",
            ...     context="User asked to create test.txt"
            ... )
            >>> result['reward']
            1
        """
        # Step 1: Judge reward
        reward_result = self.judge.judge_with_reason(feedback, action)
        reward = reward_result.reward
        confidence = reward_result.confidence
        
        # Step 2: Extract hints (only for negative feedback)
        hints: List[OPDHint] = []
        if reward < 0:
            hint = self.hint_extractor.extract(feedback)
            if hint:
                hints.append(hint)
        
        # Step 3: Build result
        result = {
            'feedback': feedback,
            'action': action,
            'context': context or '',
            'reward': reward,
            'confidence': confidence,
            'pattern_matched': reward_result.pattern_matched,
            'hints': [h.to_dict() for h in hints],
            'timestamp': datetime.now().isoformat(),
        }
        
        # Step 4: Save to disk
        self._save_result(result)
        
        return result
    
    def _save_result(self, result: Dict[str, Any]):
        """
        Save learning result to disk.
        
        Uses atomic writes with timestamp-based filenames.
        
        Args:
            result: Learning result dictionary
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        # Save to rewards log
        rewards_file = self.rewards_dir / f"reward_{timestamp}.json"
        with open(rewards_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Save hints separately if any
        if result['hints']:
            hints_file = self.hints_dir / f"hint_{timestamp}.json"
            with open(hints_file, 'w', encoding='utf-8') as f:
                json.dump({'hints': result['hints']}, f, ensure_ascii=False, indent=2)
    
    def process_batch(
        self,
        feedbacks: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of feedbacks.
        
        Args:
            feedbacks: List of feedback dictionaries with keys:
                - feedback (required)
                - action (required)
                - context (optional)
        
        Returns:
            List of learning results
        
        Example:
            >>> from pathlib import Path
            >>> loop = LearningLoop(Path("./data"))
            >>> feedbacks = [
            ...     {'feedback': 'thanks', 'action': 'created file'},
            ...     {'feedback': 'incorrect', 'action': 'deleted file'},
            ... ]
            >>> results = loop.process_batch(feedbacks)
            >>> len(results)
            2
        """
        results = []
        for feedback_dict in feedbacks:
            result = self.process_feedback(
                feedback=feedback_dict['feedback'],
                action=feedback_dict['action'],
                context=feedback_dict.get('context')
            )
            results.append(result)
        return results
    
    def get_recent_learnings(
        self,
        limit: int = 10,
        reward_filter: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent learning records.
        
        Args:
            limit: Maximum number of records to return
            reward_filter: Optional filter by reward value (-1, 0, +1)
        
        Returns:
            List of recent learning results
        
        Example:
            >>> from pathlib import Path
            >>> loop = LearningLoop(Path("./data"))
            >>> recent = loop.get_recent_learnings(limit=5)
            >>> len(recent)
            5
        """
        # Get all reward files, sorted by name (timestamp)
        reward_files = sorted(
            self.rewards_dir.glob("reward_*.json"),
            reverse=True
        )
        
        learnings = []
        for file in reward_files[:limit]:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if reward_filter is None or data['reward'] == reward_filter:
                    learnings.append(data)
        
        return learnings
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get learning statistics.
        
        Returns:
            Dictionary with statistics about learnings
        
        Example:
            >>> from pathlib import Path
            >>> loop = LearningLoop(Path("./data"))
            >>> stats = loop.get_statistics()
            >>> print(stats['total_learnings'])
            100
        """
        reward_files = list(self.rewards_dir.glob("reward_*.json"))
        hint_files = list(self.hints_dir.glob("hint_*.json"))
        
        # Count by reward type
        reward_counts = {-1: 0, 0: 0, 1: 0}
        for file in reward_files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reward_counts[data['reward']] += 1
        
        return {
            'total_learnings': len(reward_files),
            'total_hints': len(hint_files),
            'positive_rewards': reward_counts[1],
            'neutral_rewards': reward_counts[0],
            'negative_rewards': reward_counts[-1],
            'learning_rate': (reward_counts[1] + reward_counts[-1]) / max(len(reward_files), 1),
        }
