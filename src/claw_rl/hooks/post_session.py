# Copyright 2026 Peter Cheng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
claw-rl Post-Session Hook

Collects rewards and hints after session ends.
"""

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import json


@dataclass
class Turn:
    """A single turn in a conversation"""
    turn_id: int
    action: str
    next_state: str  # User response
    reward: Optional[int] = None


@dataclass
class PostSessionInput:
    """Input for post-session hook"""
    session_id: str
    user_id: str
    turns: List[Turn]


@dataclass
class PostSessionOutput:
    """Output from post-session hook"""
    rewards_recorded: int
    hints_extracted: int
    learning_triggered: bool
    summary: str


class PostSessionHook:
    """
    Post-Session Hook
    
    Collects rewards and hints after session ends.
    
    Usage:
        hook = PostSessionHook()
        result = hook.execute(PostSessionInput(
            session_id="session_001",
            user_id="peter",
            turns=[
                Turn(turn_id=1, action="Created file", next_state="thanks,great!"),
                Turn(turn_id=2, action="Edited file", next_state="incorrect,shouldput here")
            ]
        ))
        print(result.summary)
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize Post-Session Hook
        
        Args:
            data_dir: Optional custom data directory
        """
        self.data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
        
        # Ensure directories exist
        (self.data_dir / 'rewards').mkdir(parents=True, exist_ok=True)
        (self.data_dir / 'hints').mkdir(parents=True, exist_ok=True)
    
    def execute(self, input: PostSessionInput) -> PostSessionOutput:
        """
        Execute post-session hook
        
        Args:
            input: Session input with turns
            
        Returns:
            PostSessionOutput: Summary of rewards and hints collected
        """
        rewards_recorded = 0
        hints_extracted = 0
        
        for turn in input.turns:
            # Judge reward
            reward = self._judge_reward(turn.action, turn.next_state)
            turn.reward = reward
            
            # Record reward if not neutral
            if reward != 0:
                self._record_reward(input.session_id, turn)
                rewards_recorded += 1
            
            # Extract hint if correction
            if reward == -1:
                hint = self._extract_hint(turn.next_state)
                if hint:
                    self._record_hint(input.session_id, hint, turn.action)
                    hints_extracted += 1
        
        # Check if learning should be triggered
        learning_triggered = self._check_learning_trigger(input.session_id)
        
        return PostSessionOutput(
            rewards_recorded=rewards_recorded,
            hints_extracted=hints_extracted,
            learning_triggered=learning_triggered,
            summary=f"Recorded {rewards_recorded} rewards, extracted {hints_extracted} hints"
        )
    
    def _judge_reward(self, action: str, response: str) -> int:
        """
        Judge reward from user response (rule-based)
        
        Args:
            action: Agent action
            response: User response
            
        Returns:
            int: Reward (+1, -1, or 0)
        """
        response_lower = response.lower()
        
        # Positive signals
        positive_keywords = ['thanks', 'thank you', 'okay', 'great', 'good', '可以', 'correct', 'correct', 'perfect', 'thanks', 'good', 'great', 'nice']
        for keyword in positive_keywords:
            if keyword in response_lower:
                return +1
        
        # Continue conversation (implicit satisfaction)
        continue_keywords = ['then', '接下来', 'continue', '还有', '另外', '那', 'and then', 'next', 'continue']
        for keyword in continue_keywords:
            if keyword in response_lower:
                return +1
        
        # Negative signals
        negative_keywords = ['incorrect', 'wrong', 'should', 'dont', 'not okay', 'not good', 'retry', 'fix', 'wrong', 'error', 'incorrect', 'should']
        for keyword in negative_keywords:
            if keyword in response_lower:
                return -1
        
        # Repeat question (dissatisfaction)
        if '?' in response and len(response) < 50:
            # Short question might indicate confusion
            return -1
        
        # Neutral
        return 0
    
    def _extract_hint(self, correction: str) -> Optional[str]:
        """
        Extract actionable hint from user correction
        
        Args:
            correction: User correction text
            
        Returns:
            Optional[str]: Extracted hint or None
        """
        import re
        
        # Pattern: "should X" -> "before operation X"
        if 'should' in correction:
            match = re.search(r'should(.+)', correction)
            if match:
                return f"before operation{match.group(1).strip()}"
        
        # Pattern: "dont X" -> "avoid X"
        if 'dont' in correction:
            match = re.search(r'dont(.+)', correction)
            if match:
                return f"avoid{match.group(1).strip()}"
        
        # Pattern: "first X 再 Y" -> "order:first X 再 Y"
        if 'first' in correction and '再' in correction:
            return f"order:{correction}"
        
        # Pattern: "用 X method" -> "优first使用 X"
        if '用' in correction and 'method' in correction:
            match = re.search(r'用(.+)method', correction)
            if match:
                return f"优first使用{match.group(1).strip()}method"
        
        # Default: use original correction
        return correction.strip() if len(correction) < 100 else None
    
    def _record_reward(self, session_id: str, turn: Turn) -> None:
        """
        Record reward to file
        
        Args:
            session_id: Session identifier
            turn: Turn with reward
        """
        today = datetime.now().strftime('%Y-%m-%d')
        rewards_file = self.data_dir / 'rewards' / f'{today}.jsonl'
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'turn_id': turn.turn_id,
            'action': turn.action,
            'next_state': turn.next_state,
            'reward': turn.reward
        }
        
        with open(rewards_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def _record_hint(self, session_id: str, hint: str, action: str) -> None:
        """
        Record hint to file
        
        Args:
            session_id: Session identifier
            hint: Extracted hint
            action: Original action
        """
        today = datetime.now().strftime('%Y-%m-%d')
        hints_file = self.data_dir / 'hints' / f'{today}.jsonl'
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'hint': hint,
            'original_action': action
        }
        
        with open(hints_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def _check_learning_trigger(self, session_id: str) -> bool:
        """
        Check if learning should be triggered (negative reward accumulation)
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if learning should be triggered
        """
        today = datetime.now().strftime('%Y-%m-%d')
        rewards_file = self.data_dir / 'rewards' / f'{today}.jsonl'
        
        if not rewards_file.exists():
            return False
        
        # Count negative rewards today
        negative_count = 0
        try:
            with open(rewards_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    if data.get('reward', 0) == -1:
                        negative_count += 1
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        
        # Trigger learning if >= 3 negative rewards
        return negative_count >= 3
