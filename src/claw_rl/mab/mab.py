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
Multi-Armed Bandit Core

Provides intelligent strategy selection with exploration/exploitation balance.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import random
import math
import logging

logger = logging.getLogger(__name__)


class BanditError(Exception):
    """Base exception for bandit errors"""
    pass


class StrategyError(BanditError):
    """Strategy related error"""
    pass


class SelectionError(BanditError):
    """Selection related error"""
    pass


class StrategyType(Enum):
    """Types of strategies"""
    BEHAVIOR = "behavior"      # Behavioral strategies
    PROMPT = "prompt"          # Prompt templates
    MODEL = "model"            # Model selection
    PARAMETER = "parameter"    # Parameter tuning
    CUSTOM = "custom"          # Custom strategies


@dataclass
class Strategy:
    """
    A strategy in the bandit.
    
    Attributes:
        strategy_id: Unique identifier
        name: Strategy name
        strategy_type: Type of strategy
        description: Strategy description
        parameters: Strategy parameters
        created_at: Creation timestamp
        metadata: Additional metadata
    """
    strategy_id: str
    name: str
    strategy_type: StrategyType = StrategyType.BEHAVIOR
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "strategy_type": self.strategy_type.value,
            "description": self.description,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Strategy":
        """Create from dictionary"""
        return cls(
            strategy_id=data["strategy_id"],
            name=data["name"],
            strategy_type=StrategyType(data.get("strategy_type", "behavior")),
            description=data.get("description", ""),
            parameters=data.get("parameters", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            metadata=data.get("metadata", {}),
        )


@dataclass
class StrategyPerformance:
    """
    Performance metrics for a strategy.
    
    Attributes:
        strategy_id: Strategy ID
        total_trials: Total number of trials
        total_rewards: Total rewards received
        average_reward: Average reward per trial
        success_rate: Success rate (0.0 - 1.0)
        variance: Reward variance
        last_updated: Last update timestamp
    """
    strategy_id: str
    total_trials: int = 0
    total_rewards: float = 0.0
    average_reward: float = 0.0
    success_rate: float = 0.0
    variance: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    # For Thompson Sampling (Beta distribution parameters)
    alpha: float = 1.0  # Successes + 1
    beta: float = 1.0   # Failures + 1
    
    # For UCB1
    upper_confidence_bound: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "strategy_id": self.strategy_id,
            "total_trials": self.total_trials,
            "total_rewards": self.total_rewards,
            "average_reward": self.average_reward,
            "success_rate": self.success_rate,
            "variance": self.variance,
            "last_updated": self.last_updated.isoformat(),
            "alpha": self.alpha,
            "beta": self.beta,
            "upper_confidence_bound": self.upper_confidence_bound,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StrategyPerformance":
        """Create from dictionary"""
        return cls(
            strategy_id=data["strategy_id"],
            total_trials=data.get("total_trials", 0),
            total_rewards=data.get("total_rewards", 0.0),
            average_reward=data.get("average_reward", 0.0),
            success_rate=data.get("success_rate", 0.0),
            variance=data.get("variance", 0.0),
            last_updated=datetime.fromisoformat(data["last_updated"]) if "last_updated" in data else datetime.now(),
            alpha=data.get("alpha", 1.0),
            beta=data.get("beta", 1.0),
            upper_confidence_bound=data.get("upper_confidence_bound", 0.0),
        )
    
    def update(self, reward: float):
        """Update performance with new reward"""
        self.total_trials += 1
        self.total_rewards += reward
        
        # Update average
        old_avg = self.average_reward
        self.average_reward = self.total_rewards / self.total_trials
        
        # Update variance (online algorithm)
        if self.total_trials > 1:
            self.variance = ((self.total_trials - 2) / (self.total_trials - 1)) * self.variance + \
                           ((reward - old_avg) ** 2) / self.total_trials
        
        # Update success rate (assuming binary reward for simplicity)
        if reward > 0.5:
            self.alpha += 1  # Success
            self.success_rate = (self.alpha - 1) / self.total_trials
        else:
            self.beta += 1   # Failure
            self.success_rate = (self.alpha - 1) / self.total_trials
        
        self.last_updated = datetime.now()


@dataclass
class BanditConfig:
    """Configuration for Multi-Armed Bandit"""
    algorithm: str = "thompson_sampling"  # thompson_sampling, epsilon_greedy, ucb1
    epsilon: float = 0.1  # For epsilon-greedy
    epsilon_decay: float = 0.99  # Decay rate
    epsilon_min: float = 0.01  # Minimum epsilon
    ucb_c: float = 2.0  # UCB exploration parameter
    warm_start_trials: int = 10  # Minimum trials before using strategy
    exploration_bonus: float = 0.1  # Bonus for exploration
    seed: Optional[int] = None  # Random seed


class ThompsonSampler:
    """
    Thompson Sampling algorithm.
    
    Uses Beta distribution for each strategy and samples
    from the posterior to select strategies.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize Thompson Sampler"""
        self.rng = random.Random(seed)
    
    def sample(self, performance: StrategyPerformance) -> float:
        """Sample from Beta distribution"""
        # Beta distribution sample using numpy-style algorithm
        # Using the gamma distribution method
        alpha = max(0.001, performance.alpha)
        beta = max(0.001, performance.beta)
        
        # Approximate Beta sampling
        x = self._gamma_sample(alpha, 1.0)
        y = self._gamma_sample(beta, 1.0)
        
        return x / (x + y)
    
    def _gamma_sample(self, shape: float, scale: float) -> float:
        """Generate gamma-distributed random number"""
        # Marsaglia and Tsang's method
        if shape < 1:
            return self._gamma_sample(shape + 1, scale) * (self.rng.random() ** (1.0 / shape))
        
        d = shape - 1.0 / 3.0
        c = 1.0 / math.sqrt(9.0 * d)
        
        while True:
            x = self.rng.gauss(0, 1)
            v = 1.0 + c * x
            
            if v <= 0:
                continue
            
            v = v * v * v
            u = self.rng.random()
            
            if u < 1.0 - 0.0331 * (x * x) * (x * x):
                return d * v * scale
            
            if math.log(u) < 0.5 * x * x + d * (1.0 - v + math.log(v)):
                return d * v * scale


class EpsilonGreedy:
    """
    Epsilon-Greedy algorithm.
    
    With probability epsilon, explore randomly.
    With probability 1-epsilon, exploit the best strategy.
    """
    
    def __init__(self, epsilon: float = 0.1, decay: float = 0.99, min_epsilon: float = 0.01, seed: Optional[int] = None):
        """Initialize Epsilon-Greedy"""
        self.epsilon = epsilon
        self.decay = decay
        self.min_epsilon = min_epsilon
        self.rng = random.Random(seed)
    
    def should_explore(self) -> bool:
        """Determine if should explore"""
        return self.rng.random() < self.epsilon
    
    def decay_epsilon(self):
        """Decay epsilon"""
        self.epsilon = max(self.min_epsilon, self.epsilon * self.decay)


class UCB1:
    """
    Upper Confidence Bound 1 algorithm.
    
    Selects strategy with highest upper confidence bound.
    """
    
    def __init__(self, c: float = 2.0):
        """Initialize UCB1"""
        self.c = c
    
    def calculate_ucb(self, performance: StrategyPerformance, total_trials: int) -> float:
        """Calculate upper confidence bound"""
        if performance.total_trials == 0:
            return float('inf')
        
        exploration_term = self.c * math.sqrt(
            math.log(total_trials) / performance.total_trials
        )
        
        return performance.average_reward + exploration_term


class MultiArmedBandit:
    """
    Multi-Armed Bandit for intelligent strategy selection.
    
    This is the core component that makes claw-rl different from
    simple feedback collection - it provides sophisticated
    exploration/exploitation balance.
    
    Features:
    - Thompson Sampling (default)
    - Epsilon-Greedy
    - UCB1
    - Automatic exploration/exploitation balance
    - Strategy performance tracking
    """
    
    def __init__(self, config: Optional[BanditConfig] = None):
        """
        Initialize Multi-Armed Bandit.
        
        Args:
            config: Bandit configuration
        """
        self.config = config or BanditConfig()
        
        self.strategies: Dict[str, Strategy] = {}
        self.performances: Dict[str, StrategyPerformance] = {}
        self.total_trials: int = 0
        
        # Initialize algorithms
        self.thompson_sampler = ThompsonSampler(seed=self.config.seed)
        self.epsilon_greedy = EpsilonGreedy(
            epsilon=self.config.epsilon,
            decay=self.config.epsilon_decay,
            min_epsilon=self.config.epsilon_min,
            seed=self.config.seed,
        )
        self.ucb1 = UCB1(c=self.config.ucb_c)
        
        # Random generator
        self.rng = random.Random(self.config.seed)
    
    def register_strategy(self, strategy: Strategy) -> None:
        """
        Register a new strategy.
        
        Args:
            strategy: Strategy to register
            
        Raises:
            StrategyError: If strategy already exists
        """
        if strategy.strategy_id in self.strategies:
            raise StrategyError(f"Strategy {strategy.strategy_id} already registered")
        
        self.strategies[strategy.strategy_id] = strategy
        self.performances[strategy.strategy_id] = StrategyPerformance(
            strategy_id=strategy.strategy_id
        )
        
        logger.info(f"Registered strategy: {strategy.name} ({strategy.strategy_id})")
    
    def unregister_strategy(self, strategy_id: str) -> None:
        """
        Unregister a strategy.
        
        Args:
            strategy_id: Strategy ID to unregister
        """
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            del self.performances[strategy_id]
            logger.info(f"Unregistered strategy: {strategy_id}")
    
    def select_strategy(self, context: Optional[Dict[str, Any]] = None) -> Optional[Strategy]:
        """
        Select a strategy using the configured algorithm.
        
        Args:
            context: Optional context for strategy selection
            
        Returns:
            Selected strategy, or None if no strategies available
            
        Raises:
            SelectionError: If selection fails
        """
        if not self.strategies:
            logger.warning("No strategies registered")
            return None
        
        # If only one strategy, return it
        if len(self.strategies) == 1:
            return list(self.strategies.values())[0]
        
        # Check if we need warm start
        under_explored = [
            sid for sid, perf in self.performances.items()
            if perf.total_trials < self.config.warm_start_trials
        ]
        
        if under_explored:
            # Explore under-explored strategies
            strategy_id = self.rng.choice(under_explored)
            return self.strategies[strategy_id]
        
        # Use configured algorithm
        if self.config.algorithm == "thompson_sampling":
            return self._select_thompson_sampling()
        elif self.config.algorithm == "epsilon_greedy":
            return self._select_epsilon_greedy()
        elif self.config.algorithm == "ucb1":
            return self._select_ucb1()
        else:
            raise SelectionError(f"Unknown algorithm: {self.config.algorithm}")
    
    def _select_thompson_sampling(self) -> Strategy:
        """Select using Thompson Sampling"""
        samples = {}
        
        for strategy_id, performance in self.performances.items():
            samples[strategy_id] = self.thompson_sampler.sample(performance)
        
        # Select strategy with highest sample
        best_strategy_id = max(samples, key=samples.get)
        return self.strategies[best_strategy_id]
    
    def _select_epsilon_greedy(self) -> Strategy:
        """Select using Epsilon-Greedy"""
        if self.epsilon_greedy.should_explore():
            # Explore: random strategy
            strategy_id = self.rng.choice(list(self.strategies.keys()))
            return self.strategies[strategy_id]
        else:
            # Exploit: best average reward
            best_strategy_id = max(
                self.performances.keys(),
                key=lambda sid: self.performances[sid].average_reward
            )
            return self.strategies[best_strategy_id]
    
    def _select_ucb1(self) -> Strategy:
        """Select using UCB1"""
        best_strategy_id = None
        best_ucb = float('-inf')
        
        for strategy_id, performance in self.performances.items():
            ucb = self.ucb1.calculate_ucb(performance, self.total_trials)
            if ucb > best_ucb:
                best_ucb = ucb
                best_strategy_id = strategy_id
        
        return self.strategies[best_strategy_id]
    
    def update(self, strategy_id: str, reward: float) -> None:
        """
        Update strategy performance with reward.
        
        Args:
            strategy_id: Strategy that was used
            reward: Reward received (0.0 to 1.0 for binary, or any float)
            
        Raises:
            StrategyError: If strategy not found
        """
        if strategy_id not in self.performances:
            raise StrategyError(f"Strategy {strategy_id} not found")
        
        self.performances[strategy_id].update(reward)
        self.total_trials += 1
        
        # Decay epsilon for epsilon-greedy
        if self.config.algorithm == "epsilon_greedy":
            self.epsilon_greedy.decay_epsilon()
        
        logger.debug(
            f"Updated strategy {strategy_id}: reward={reward:.3f}, "
            f"avg={self.performances[strategy_id].average_reward:.3f}"
        )
    
    def get_best_strategy(self) -> Optional[Strategy]:
        """
        Get the currently best performing strategy.
        
        Returns:
            Best strategy, or None if no strategies
        """
        if not self.performances:
            return None
        
        best_strategy_id = max(
            self.performances.keys(),
            key=lambda sid: self.performances[sid].average_reward
        )
        
        return self.strategies.get(best_strategy_id)
    
    def get_performance(self, strategy_id: str) -> Optional[StrategyPerformance]:
        """Get performance for a strategy"""
        return self.performances.get(strategy_id)
    
    def get_all_performances(self) -> Dict[str, StrategyPerformance]:
        """Get all strategy performances"""
        return self.performances.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bandit statistics"""
        performances = list(self.performances.values())
        
        if not performances:
            return {
                "total_strategies": 0,
                "total_trials": 0,
                "algorithm": self.config.algorithm,
            }
        
        return {
            "total_strategies": len(self.strategies),
            "total_trials": self.total_trials,
            "algorithm": self.config.algorithm,
            "best_strategy": self.get_best_strategy().name if self.get_best_strategy() else None,
            "average_reward": sum(p.average_reward for p in performances) / len(performances),
            "exploration_rate": self.epsilon_greedy.epsilon if self.config.algorithm == "epsilon_greedy" else None,
        }
    
    def reset(self):
        """Reset all performances"""
        for strategy_id in self.performances:
            self.performances[strategy_id] = StrategyPerformance(strategy_id=strategy_id)
        self.total_trials = 0
        self.epsilon_greedy = EpsilonGreedy(
            epsilon=self.config.epsilon,
            decay=self.config.epsilon_decay,
            min_epsilon=self.config.epsilon_min,
            seed=self.config.seed,
        )
        logger.info("Reset all strategy performances")
