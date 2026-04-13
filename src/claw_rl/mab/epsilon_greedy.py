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
Epsilon-Greedy Implementation

Provides simple exploration/exploitation balance with configurable epsilon.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import random
import math


class DecayMode:
    """Decay modes for epsilon"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    NONE = "none"


@dataclass
class EpsilonGreedyConfig:
    """Configuration for Epsilon-Greedy"""
    initial_epsilon: float = 0.1
    min_epsilon: float = 0.01
    decay_rate: float = 0.99
    decay_mode: str = DecayMode.EXPONENTIAL
    total_steps: int = 10000  # For linear decay


class EpsilonGreedyStrategy:
    """
    Epsilon-Greedy strategy implementation.
    
    Simple but effective exploration/exploitation balance:
    - With probability epsilon: explore (random selection)
    - With probability 1-epsilon: exploit (select best)
    
    Features:
    - Configurable epsilon decay
    - Linear or exponential decay
    - Minimum epsilon threshold
    """
    
    def __init__(
        self,
        initial_epsilon: float = 0.1,
        min_epsilon: float = 0.01,
        decay_rate: float = 0.99,
        decay_mode: str = DecayMode.EXPONENTIAL,
        seed: Optional[int] = None,
    ):
        """
        Initialize Epsilon-Greedy strategy.
        
        Args:
            initial_epsilon: Initial exploration rate
            min_epsilon: Minimum exploration rate
            decay_rate: Rate at which epsilon decays
            decay_mode: How epsilon decays (linear/exponential/none)
            seed: Random seed for reproducibility
        """
        self.initial_epsilon = initial_epsilon
        self.epsilon = initial_epsilon
        self.min_epsilon = min_epsilon
        self.decay_rate = decay_rate
        self.decay_mode = decay_mode
        self.rng = random.Random(seed)
        
        self.step_count = 0
        self.total_steps = 10000  # For linear decay
        
        # Track performance
        self.strategy_rewards: Dict[str, float] = {}
        self.strategy_counts: Dict[str, int] = {}
    
    def register_strategy(self, strategy_id: str):
        """
        Register a strategy.
        
        Args:
            strategy_id: Strategy identifier
        """
        if strategy_id not in self.strategy_rewards:
            self.strategy_rewards[strategy_id] = 0.0
            self.strategy_counts[strategy_id] = 0
    
    def update(self, strategy_id: str, reward: float):
        """
        Update strategy performance.
        
        Args:
            strategy_id: Strategy that was used
            reward: Reward received
        """
        if strategy_id not in self.strategy_rewards:
            self.register_strategy(strategy_id)
        
        self.strategy_rewards[strategy_id] += reward
        self.strategy_counts[strategy_id] += 1
        
        # Decay epsilon after update
        self._decay_epsilon()
    
    def _decay_epsilon(self):
        """Apply epsilon decay"""
        if self.decay_mode == DecayMode.NONE:
            return
        
        if self.decay_mode == DecayMode.EXPONENTIAL:
            self.epsilon = max(self.min_epsilon, self.epsilon * self.decay_rate)
        
        elif self.decay_mode == DecayMode.LINEAR:
            self.step_count += 1
            progress = self.step_count / self.total_steps
            self.epsilon = max(
                self.min_epsilon,
                self.initial_epsilon * (1 - progress)
            )
    
    def should_explore(self) -> bool:
        """
        Determine if should explore.
        
        Returns:
            True if should explore, False if should exploit
        """
        return self.rng.random() < self.epsilon
    
    def select_strategy(self) -> Optional[str]:
        """
        Select a strategy using epsilon-greedy.
        
        Returns:
            Selected strategy ID, or None if no strategies
        """
        if not self.strategy_rewards:
            return None
        
        if self.should_explore():
            # Explore: random selection
            return self.rng.choice(list(self.strategy_rewards.keys()))
        else:
            # Exploit: select best
            return self._get_best_strategy()
    
    def _get_best_strategy(self) -> Optional[str]:
        """Get strategy with highest average reward"""
        if not self.strategy_counts:
            return None
        
        averages = {}
        for sid in self.strategy_rewards:
            if self.strategy_counts[sid] > 0:
                averages[sid] = self.strategy_rewards[sid] / self.strategy_counts[sid]
        
        if not averages:
            return self.rng.choice(list(self.strategy_rewards.keys()))
        
        return max(averages, key=averages.get)
    
    def get_average_reward(self, strategy_id: str) -> float:
        """Get average reward for a strategy"""
        if strategy_id not in self.strategy_counts or self.strategy_counts[strategy_id] == 0:
            return 0.0
        return self.strategy_rewards[strategy_id] / self.strategy_counts[strategy_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get strategy statistics"""
        return {
            "epsilon": self.epsilon,
            "decay_mode": self.decay_mode,
            "step_count": self.step_count,
            "strategies": len(self.strategy_rewards),
            "best_strategy": self._get_best_strategy(),
        }
    
    def reset(self):
        """Reset strategy"""
        self.epsilon = self.initial_epsilon
        self.step_count = 0
        self.strategy_rewards.clear()
        self.strategy_counts.clear()
