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
Adaptive Multi-Armed Bandit (v2.1.0)

Implements context-aware strategy selection with:
- Meta-Learner for strategy selection
- Dynamic parameter adjustment
- Context feature extraction
- Performance tracking

Based on research:
- Contextual Bandits (LinUCB)
- Meta-Learning for Strategy Selection
- Dynamic Exploration/Exploitation
"""

from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import random
import math
import json
import logging

logger = logging.getLogger(__name__)


class AdaptationMode(Enum):
    """Adaptation modes"""
    STATIC = "static"           # No adaptation
    CONTEXTUAL = "contextual"   # Context-aware
    REACTIVE = "reactive"       # React to performance changes
    HYBRID = "hybrid"           # Combination


@dataclass
class ContextFeatures:
    """
    Context features for strategy selection.
    
    These features help the Meta-Learner choose the best strategy.
    """
    # Data characteristics
    data_size: int = 0              # Number of data points
    data_variance: float = 0.0      # Variance in data
    
    # Temporal features
    hour_of_day: int = 12           # 0-23
    day_of_week: int = 0            # 0-6 (Mon=0)
    
    # Performance history
    recent_success_rate: float = 0.5  # Last 10 operations
    cumulative_reward: float = 0.0
    
    # Operation context
    operation_type: str = "unknown"  # file, code, analysis, etc.
    user_id: str = ""
    session_id: str = ""
    
    # System state
    memory_usage: float = 0.0       # 0-1
    latency_budget_ms: float = 1000 # Max acceptable latency
    
    def to_vector(self) -> List[float]:
        """Convert to feature vector for ML"""
        return [
            self.data_size / 1000.0,  # Normalized
            self.data_variance,
            self.hour_of_day / 24.0,
            self.day_of_week / 7.0,
            self.recent_success_rate,
            math.tanh(self.cumulative_reward / 100),  # Normalized
            1.0 if self.operation_type == "file" else 0.0,
            1.0 if self.operation_type == "code" else 0.0,
            1.0 if self.operation_type == "analysis" else 0.0,
            self.memory_usage,
            self.latency_budget_ms / 1000.0,
        ]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'data_size': self.data_size,
            'data_variance': self.data_variance,
            'hour_of_day': self.hour_of_day,
            'day_of_week': self.day_of_week,
            'recent_success_rate': self.recent_success_rate,
            'cumulative_reward': self.cumulative_reward,
            'operation_type': self.operation_type,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'memory_usage': self.memory_usage,
            'latency_budget_ms': self.latency_budget_ms,
        }


@dataclass
class StrategyPerformance:
    """Track performance of a strategy"""
    strategy_id: str
    total_selections: int = 0
    successful_selections: int = 0
    total_reward: float = 0.0
    avg_latency_ms: float = 0.0
    last_used: Optional[datetime] = None
    context_performance: Dict[str, float] = field(default_factory=dict)  # context -> avg_reward
    
    @property
    def success_rate(self) -> float:
        if self.total_selections == 0:
            return 0.5
        return self.successful_selections / self.total_selections
    
    @property
    def avg_reward(self) -> float:
        if self.total_selections == 0:
            return 0.0
        return self.total_reward / self.total_selections
    
    def update(self, reward: float, latency_ms: float = 0.0, context_key: str = ""):
        """Update performance metrics"""
        self.total_selections += 1
        self.total_reward += reward
        if reward > 0:
            self.successful_selections += 1
        
        # Update latency (exponential moving average)
        if self.avg_latency_ms == 0:
            self.avg_latency_ms = latency_ms
        else:
            self.avg_latency_ms = 0.9 * self.avg_latency_ms + 0.1 * latency_ms
        
        # Update context-specific performance
        if context_key:
            if context_key not in self.context_performance:
                self.context_performance[context_key] = reward
            else:
                # Exponential moving average
                self.context_performance[context_key] = (
                    0.8 * self.context_performance[context_key] + 0.2 * reward
                )
        
        self.last_used = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'strategy_id': self.strategy_id,
            'total_selections': self.total_selections,
            'successful_selections': self.successful_selections,
            'total_reward': self.total_reward,
            'avg_latency_ms': self.avg_latency_ms,
            'success_rate': self.success_rate,
            'avg_reward': self.avg_reward,
            'context_performance': self.context_performance,
        }


class MetaLearner:
    """
    Meta-Learner for strategy selection.

    Learns which strategy works best in which context using two-tier matching:
    1. Coarse key: Fast O(1) lookup via discretized context key
    2. Similarity: Cosine similarity on 11-dim feature vectors for finer matching

    The similarity-based approach kicks in when there are enough (>5) context
    entries to make meaningful comparisons. Otherwise falls back to coarse key.
    """

    def __init__(self, learning_rate: float = 0.1, similarity_threshold: float = 0.6):
        """
        Initialize Meta-Learner.

        Args:
            learning_rate: Learning rate for updates
            similarity_threshold: Minimum cosine similarity for context matching (0.0-1.0)
        """
        self.learning_rate = learning_rate
        self.similarity_threshold = similarity_threshold
        self.strategy_performance: Dict[str, StrategyPerformance] = {}
        self.context_strategy_map: Dict[str, str] = {}  # context_key -> best_strategy
        self.history: List[Tuple[str, str, float]] = []  # (context, strategy, reward)
        # Cache: context vector -> (context_key, vector) for similarity search
        self._context_vectors: List[Tuple[str, List[float]]] = []
        self._max_context_cache = 500
    
    def register_strategy(self, strategy_id: str):
        """Register a strategy"""
        if strategy_id not in self.strategy_performance:
            self.strategy_performance[strategy_id] = StrategyPerformance(strategy_id=strategy_id)
    
    def get_context_key(self, context: ContextFeatures) -> str:
        """
        Generate context key for lookup.
        
        Uses coarse-grained context to ensure enough samples per context.
        """
        # Discretize continuous features
        data_size_bucket = "small" if context.data_size < 10 else ("medium" if context.data_size < 100 else "large")
        success_bucket = "low" if context.recent_success_rate < 0.3 else ("medium" if context.recent_success_rate < 0.7 else "high")
        
        return f"{context.operation_type}|{data_size_bucket}|{success_bucket}"
    
    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two feature vectors."""
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(ai * bi for ai, bi in zip(a, b))
        norm_a = math.sqrt(sum(ai * ai for ai in a))
        norm_b = math.sqrt(sum(bi * bi for bi in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def find_similar_contexts(
        self, context: ContextFeatures, top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Find top-K historically similar contexts using cosine similarity.

        Args:
            context: Current context features
            top_k: Number of similar contexts to return

        Returns:
            List of (context_key, similarity_score) sorted by similarity descending
        """
        query_vec = context.to_vector()
        scores: List[Tuple[str, float]] = []

        for cached_key, cached_vec in self._context_vectors:
            sim = self._cosine_similarity(query_vec, cached_vec)
            if sim >= self.similarity_threshold:
                scores.append((cached_key, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def _cache_context_vector(self, context_key: str, context: ContextFeatures):
        """Cache a context vector for future similarity search."""
        vec = context.to_vector()
        self._context_vectors.append((context_key, vec))
        if len(self._context_vectors) > self._max_context_cache:
            self._context_vectors = self._context_vectors[-self._max_context_cache:]

    def predict_with_similarity(
        self, context: ContextFeatures, top_k: int = 3
    ) -> Optional[str]:
        """
        Predict best strategy using cosine similarity on feature vectors.

        Finds historically similar contexts and uses their strategy performance
        as weighted votes. Falls back to coarse key prediction if insufficient data.

        Args:
            context: Current context features
            top_k: Number of similar contexts to consider

        Returns:
            Best strategy ID, or None if no strategies
        """
        if not self.strategy_performance:
            return None

        similar = self.find_similar_contexts(context, top_k=top_k)

        if not similar:
            # Fall back to coarse key prediction
            return self.predict_best_strategy(context)

        # Weighted voting: each similar context votes for its best strategy
        strategy_scores: Dict[str, float] = {}
        total_weight = 0.0

        for ctx_key, similarity in similar:
            if ctx_key not in self.context_strategy_map:
                continue
            best_sid = self.context_strategy_map[ctx_key]
            weight = similarity * similarity  # Square to emphasize strong matches
            strategy_scores[best_sid] = strategy_scores.get(best_sid, 0.0) + weight
            total_weight += weight

        if strategy_scores and total_weight > 0:
            # Return strategy with highest weighted score
            return max(strategy_scores, key=strategy_scores.get)

        # Fall back to coarse key
        return self.predict_best_strategy(context)

    def predict_best_strategy(self, context: ContextFeatures) -> Optional[str]:
        """
        Predict best strategy for given context.
        
        Args:
            context: Current context features
            
        Returns:
            Best strategy ID, or None if no strategies
        """
        if not self.strategy_performance:
            return None
        
        context_key = self.get_context_key(context)
        
        # Check if we have a learned mapping
        if context_key in self.context_strategy_map:
            return self.context_strategy_map[context_key]
        
        # Otherwise, select strategy with best context-specific performance
        best_strategy = None
        best_score = -float('inf')
        
        for sid, perf in self.strategy_performance.items():
            if context_key in perf.context_performance:
                score = perf.context_performance[context_key]
            else:
                # Fall back to overall performance with exploration bonus
                exploration_bonus = 1.0 / (perf.total_selections + 1)
                score = perf.avg_reward + exploration_bonus
            
            if score > best_score:
                best_score = score
                best_strategy = sid
        
        return best_strategy or list(self.strategy_performance.keys())[0]
    
    def update(
        self,
        strategy_id: str,
        reward: float,
        context: ContextFeatures,
        latency_ms: float = 0.0
    ):
        """
        Update Meta-Learner with new observation.
        
        Args:
            strategy_id: Strategy that was used
            reward: Reward received
            context: Context when strategy was used
            latency_ms: Latency of the operation
        """
        self.register_strategy(strategy_id)
        
        context_key = self.get_context_key(context)
        
        # Update strategy performance
        self.strategy_performance[strategy_id].update(
            reward=reward,
            latency_ms=latency_ms,
            context_key=context_key
        )
        
        # Record history
        self.history.append((context_key, strategy_id, reward))
        
        # Update context-strategy mapping
        self._update_mapping(context_key)

        # Cache context vector for future similarity search
        self._cache_context_vector(context_key, context)

    def _update_mapping(self, context_key: str):
        """Update best strategy for a context"""
        # Find strategy with best average performance for this context
        best_strategy = None
        best_avg = -float('inf')
        
        for sid, perf in self.strategy_performance.items():
            if context_key in perf.context_performance:
                avg = perf.context_performance[context_key]
                if avg > best_avg:
                    best_avg = avg
                    best_strategy = sid
        
        if best_strategy:
            self.context_strategy_map[context_key] = best_strategy
    
    def get_stats(self) -> Dict:
        """Get Meta-Learner statistics"""
        return {
            'strategies': len(self.strategy_performance),
            'context_mappings': len(self.context_strategy_map),
            'history_size': len(self.history),
            'context_vectors_cached': len(self._context_vectors),
            'similarity_enabled': len(self._context_vectors) > 5,
            'strategy_performance': {
                sid: perf.to_dict()
                for sid, perf in self.strategy_performance.items()
            },
        }


class AdaptiveMAB:
    """
    Adaptive Multi-Armed Bandit (v2.1.0)
    
    Features:
    - Context-aware strategy selection
    - Meta-Learner for automatic adaptation
    - Dynamic parameter adjustment
    - Multiple base strategies (Thompson, ε-Greedy, UCB)
    - Performance tracking and optimization
    
    Usage:
        mab = AdaptiveMAB()
        
        # Register strategies
        mab.register_strategy("thompson")
        mab.register_strategy("epsilon_greedy")
        mab.register_strategy("ucb")
        
        # Select strategy based on context
        context = ContextFeatures(
            operation_type="file",
            data_size=50,
            recent_success_rate=0.7
        )
        strategy = mab.select_strategy(context)
        
        # Update with result
        mab.update(strategy, reward=1.0, latency_ms=10.5, context=context)
    """
    
    def __init__(
        self,
        adaptation_mode: AdaptationMode = AdaptationMode.HYBRID,
        seed: Optional[int] = None,
        config: Optional[Dict] = None
    ):
        """
        Initialize Adaptive MAB.
        
        Args:
            adaptation_mode: How to adapt strategy selection
            seed: Random seed
            config: Configuration options
        """
        self.adaptation_mode = adaptation_mode
        self.rng = random.Random(seed)
        self.config = config or {}
        
        # Components
        self.meta_learner = MetaLearner(
            learning_rate=self.config.get('learning_rate', 0.1)
        )
        
        # Strategy registry
        self.strategies: Dict[str, StrategyPerformance] = {}
        
        # Dynamic parameters
        self.current_epsilon = self.config.get('initial_epsilon', 0.1)
        self.min_epsilon = self.config.get('min_epsilon', 0.01)
        self.epsilon_decay = self.config.get('epsilon_decay', 0.995)
        
        # Performance tracking
        self.total_selections = 0
        self.total_reward = 0.0
        self.recent_rewards: List[float] = []
        self.recent_window = self.config.get('recent_window', 20)
        
        # State
        self.last_context: Optional[ContextFeatures] = None
        self.last_strategy: Optional[str] = None
        
        # Metrics
        self._metrics = {
            'selections': 0,
            'explorations': 0,
            'exploitations': 0,
            'context_switches': 0,
            'strategy_switches': 0,
        }
    
    def register_strategy(self, strategy_id: str, metadata: Optional[Dict] = None):
        """
        Register a strategy.
        
        Args:
            strategy_id: Unique strategy identifier
            metadata: Optional strategy metadata
        """
        if strategy_id not in self.strategies:
            self.strategies[strategy_id] = StrategyPerformance(strategy_id=strategy_id)
            self.meta_learner.register_strategy(strategy_id)
        
        if metadata:
            self.strategies[strategy_id].context_performance['_metadata'] = metadata
    
    def select_strategy(self, context: Optional[ContextFeatures] = None) -> str:
        """
        Select a strategy based on context.
        
        Args:
            context: Current context features
            
        Returns:
            Selected strategy ID
        """
        if not self.strategies:
            raise ValueError("No strategies registered")
        
        self._metrics['selections'] += 1
        
        # Track context switches
        if self.last_context and context:
            if self.get_context_key(context) != self.get_context_key(self.last_context):
                self._metrics['context_switches'] += 1
        
        self.last_context = context
        
        # Select based on adaptation mode
        if self.adaptation_mode == AdaptationMode.STATIC:
            strategy = self._select_static()
        elif self.adaptation_mode == AdaptationMode.CONTEXTUAL:
            strategy = self._select_contextual(context)
        elif self.adaptation_mode == AdaptationMode.REACTIVE:
            strategy = self._select_reactive()
        else:  # HYBRID
            strategy = self._select_hybrid(context)
        
        # Track strategy switches
        if self.last_strategy and strategy != self.last_strategy:
            self._metrics['strategy_switches'] += 1
        
        self.last_strategy = strategy
        return strategy
    
    def get_context_key(self, context: Optional[ContextFeatures]) -> str:
        """Get context key"""
        if context:
            return self.meta_learner.get_context_key(context)
        return "default"
    
    def _select_static(self) -> str:
        """Static selection - always use best overall"""
        best = max(self.strategies.keys(), key=lambda s: self.strategies[s].avg_reward)
        self._metrics['exploitations'] += 1
        return best
    
    def _select_contextual(self, context: Optional[ContextFeatures]) -> str:
        """Contextual selection - use similarity-based Meta-Learner prediction"""
        if context:
            # Prefer similarity-based prediction when enough history exists
            if len(self.meta_learner._context_vectors) > 5:
                predicted = self.meta_learner.predict_with_similarity(context)
            else:
                predicted = self.meta_learner.predict_best_strategy(context)
            if predicted:
                self._metrics['exploitations'] += 1
                return predicted

        # Fallback to best overall
        return self._select_static()
    
    def _select_reactive(self) -> str:
        """Reactive selection - react to recent performance"""
        # If recent performance is good, exploit; otherwise explore
        if self.recent_rewards:
            recent_avg = sum(self.recent_rewards[-5:]) / min(5, len(self.recent_rewards))
            
            if recent_avg < 0.3:
                # Poor performance - explore
                self._metrics['explorations'] += 1
                return self.rng.choice(list(self.strategies.keys()))
        
        # Good performance - exploit best
        self._metrics['exploitations'] += 1
        return self._select_static()
    
    def _select_hybrid(self, context: Optional[ContextFeatures]) -> str:
        """
        Hybrid selection - combine contextual + reactive + exploration.

        Uses similarity-based prediction when enough context history exists,
        falling back to coarse key prediction for cold start.

        This is the recommended mode for production use.
        """
        # Epsilon-greedy with contextual bias
        if self.rng.random() < self.current_epsilon:
            # Explore
            self._metrics['explorations'] += 1
            return self.rng.choice(list(self.strategies.keys()))

        # Exploit with contextual awareness
        self._metrics['exploitations'] += 1

        if context:
            # Use similarity-based prediction when enough history
            if len(self.meta_learner._context_vectors) > 5:
                predicted = self.meta_learner.predict_with_similarity(context)
            else:
                predicted = self.meta_learner.predict_best_strategy(context)
            if predicted:
                return predicted

        return self._select_static()
    
    def update(
        self,
        strategy_id: str,
        reward: float,
        latency_ms: float = 0.0,
        context: Optional[ContextFeatures] = None
    ):
        """
        Update with observation.
        
        Args:
            strategy_id: Strategy that was used
            reward: Reward received (-1, 0, 1)
            latency_ms: Operation latency
            context: Context when strategy was used
        """
        if strategy_id not in self.strategies:
            self.register_strategy(strategy_id)
        
        # Update strategy performance
        context_key = self.get_context_key(context) if context else ""
        self.strategies[strategy_id].update(
            reward=reward,
            latency_ms=latency_ms,
            context_key=context_key
        )
        
        # Update Meta-Learner
        if context:
            self.meta_learner.update(
                strategy_id=strategy_id,
                reward=reward,
                context=context,
                latency_ms=latency_ms
            )
        
        # Update global stats
        self.total_selections += 1
        self.total_reward += reward
        self.recent_rewards.append(reward)
        if len(self.recent_rewards) > self.recent_window:
            self.recent_rewards.pop(0)
        
        # Adapt epsilon
        self._adapt_parameters()
    
    def _adapt_parameters(self):
        """Dynamically adapt parameters based on performance"""
        # Decay epsilon
        self.current_epsilon = max(
            self.min_epsilon,
            self.current_epsilon * self.epsilon_decay
        )
        
        # If recent performance is poor, increase exploration
        if len(self.recent_rewards) >= 5:
            recent_avg = sum(self.recent_rewards[-5:]) / 5
            if recent_avg < 0.2:
                # Boost exploration temporarily
                self.current_epsilon = min(0.3, self.current_epsilon * 2)
    
    def get_best_strategy(self, context: Optional[ContextFeatures] = None) -> str:
        """Get current best strategy"""
        if context:
            predicted = self.meta_learner.predict_best_strategy(context)
            if predicted:
                return predicted
        
        return max(self.strategies.keys(), key=lambda s: self.strategies[s].avg_reward)
    
    def get_strategy_stats(self, strategy_id: str) -> Optional[Dict]:
        """Get stats for a specific strategy"""
        if strategy_id in self.strategies:
            return self.strategies[strategy_id].to_dict()
        return None
    
    def get_all_stats(self) -> Dict:
        """Get comprehensive statistics"""
        return {
            'mode': self.adaptation_mode.value,
            'epsilon': self.current_epsilon,
            'total_selections': self.total_selections,
            'total_reward': self.total_reward,
            'avg_reward': self.total_reward / self.total_selections if self.total_selections > 0 else 0,
            'strategies': {
                sid: perf.to_dict()
                for sid, perf in self.strategies.items()
            },
            'meta_learner': self.meta_learner.get_stats(),
            'metrics': self._metrics,
        }
    
    def reset(self):
        """Reset all state"""
        self.strategies.clear()
        self.meta_learner = MetaLearner(
            learning_rate=self.config.get('learning_rate', 0.1)
        )
        self.total_selections = 0
        self.total_reward = 0.0
        self.recent_rewards.clear()
        self.current_epsilon = self.config.get('initial_epsilon', 0.1)
        self._metrics = {
            'selections': 0,
            'explorations': 0,
            'exploitations': 0,
            'context_switches': 0,
            'strategy_switches': 0,
        }
