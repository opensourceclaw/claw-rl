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
Thompson Sampling Implementation

Provides Beta distribution-based Thompson Sampling for strategy selection.
"""

from dataclasses import dataclass
from typing import Optional
import math
import random


@dataclass
class BetaDistribution:
    """
    Beta distribution for Thompson Sampling.
    
    Used to model the probability of success for each strategy.
    
    Attributes:
        alpha: Shape parameter (successes + 1)
        beta: Shape parameter (failures + 1)
    """
    alpha: float = 1.0
    beta: float = 1.0
    
    def update(self, success: bool):
        """
        Update distribution with new observation.
        
        Args:
            success: Whether the trial was successful
        """
        if success:
            self.alpha += 1
        else:
            self.beta += 1
    
    def sample(self, rng: Optional[random.Random] = None) -> float:
        """
        Sample from the Beta distribution.
        
        Args:
            rng: Optional random number generator
            
        Returns:
            Sample value between 0 and 1
        """
        if rng is None:
            rng = random
        
        # Use gamma distribution method
        x = self._gamma_sample(self.alpha, 1.0, rng)
        y = self._gamma_sample(self.beta, 1.0, rng)
        
        return x / (x + y)
    
    def _gamma_sample(self, shape: float, scale: float, rng: random.Random) -> float:
        """Generate gamma-distributed random number"""
        # Marsaglia and Tsang's method
        if shape < 1:
            return self._gamma_sample(shape + 1, scale, rng) * (rng.random() ** (1.0 / shape))
        
        d = shape - 1.0 / 3.0
        c = 1.0 / math.sqrt(9.0 * d)
        
        while True:
            x = rng.gauss(0, 1)
            v = 1.0 + c * x
            
            if v <= 0:
                continue
            
            v = v * v * v
            u = rng.random()
            
            if u < 1.0 - 0.0331 * (x * x) * (x * x):
                return d * v * scale
            
            if math.log(u) < 0.5 * x * x + d * (1.0 - v + math.log(v)):
                return d * v * scale
    
    def mean(self) -> float:
        """Get the mean of the distribution"""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self) -> float:
        """Get the variance of the distribution"""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "alpha": self.alpha,
            "beta": self.beta,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BetaDistribution":
        """Create from dictionary"""
        return cls(
            alpha=data.get("alpha", 1.0),
            beta=data.get("beta", 1.0),
        )


class ThompsonSamplingStrategy:
    """
    Thompson Sampling strategy implementation.
    
    Provides intelligent exploration/exploitation balance using
    Bayesian inference with Beta distributions.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize Thompson Sampling strategy.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.rng = random.Random(seed)
        self.distributions: dict = {}
    
    def register_strategy(self, strategy_id: str):
        """
        Register a strategy for Thompson Sampling.
        
        Args:
            strategy_id: Strategy identifier
        """
        if strategy_id not in self.distributions:
            self.distributions[strategy_id] = BetaDistribution()
    
    def update(self, strategy_id: str, success: bool):
        """
        Update strategy distribution with new observation.
        
        Args:
            strategy_id: Strategy that was used
            success: Whether it was successful
        """
        if strategy_id not in self.distributions:
            self.register_strategy(strategy_id)
        
        self.distributions[strategy_id].update(success)
    
    def sample(self, strategy_id: str) -> float:
        """
        Sample from strategy's distribution.
        
        Args:
            strategy_id: Strategy to sample
            
        Returns:
            Sampled probability
        """
        if strategy_id not in self.distributions:
            return 0.5  # Default for unknown strategies
        
        return self.distributions[strategy_id].sample(self.rng)
    
    def select_strategy(self) -> Optional[str]:
        """
        Select strategy with highest sampled probability.
        
        Returns:
            Selected strategy ID, or None if no strategies
        """
        if not self.distributions:
            return None
        
        samples = {
            sid: dist.sample(self.rng)
            for sid, dist in self.distributions.items()
        }
        
        return max(samples, key=samples.get)
    
    def get_distribution(self, strategy_id: str) -> Optional[BetaDistribution]:
        """Get distribution for a strategy"""
        return self.distributions.get(strategy_id)
    
    def get_all_distributions(self) -> dict:
        """Get all distributions"""
        return self.distributions.copy()
    
    def get_best_strategy(self) -> Optional[str]:
        """
        Get strategy with highest mean.
        
        Returns:
            Best strategy ID, or None if no strategies
        """
        if not self.distributions:
            return None
        
        return max(self.distributions.keys(), key=lambda sid: self.distributions[sid].mean())
    
    def reset(self):
        """Reset all distributions"""
        self.distributions.clear()
