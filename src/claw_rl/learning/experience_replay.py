"""
Experience Replay - Buffer for storing and sampling past experiences

This module provides an experience replay buffer for reinforcement learning,
supporting prioritized sampling and experience deduplication.
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import random
import math
from collections import defaultdict


class SamplingStrategy(Enum):
    """Strategy for sampling experiences."""
    UNIFORM = "uniform"
    PRIORITIZED = "prioritized"
    RECENT = "recent"
    BALANCED = "balanced"


@dataclass
class Experience:
    """
    A single experience entry in the replay buffer.
    
    Attributes:
        experience_id: Unique identifier
        state: State before action
        action: Action taken
        reward: Reward received
        next_state: State after action
        done: Whether episode ended
        priority: Priority for sampling (higher = more likely)
        timestamp: When experience was recorded
        metadata: Additional metadata
    """
    experience_id: str
    state: Dict[str, Any]
    action: Dict[str, Any]
    reward: float
    next_state: Dict[str, Any] = field(default_factory=dict)
    done: bool = False
    priority: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "experience_id": self.experience_id,
            "state": self.state,
            "action": self.action,
            "reward": self.reward,
            "next_state": self.next_state,
            "done": self.done,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Experience':
        """Create from dictionary."""
        return cls(
            experience_id=data["experience_id"],
            state=data["state"],
            action=data["action"],
            reward=data["reward"],
            next_state=data.get("next_state", {}),
            done=data.get("done", False),
            priority=data.get("priority", 1.0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )
    
    def compute_hash(self) -> str:
        """Compute hash for deduplication."""
        import hashlib
        content = json.dumps({
            "state": self.state,
            "action": self.action,
            "reward": self.reward,
        }, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()


class ExperienceReplay:
    """
    Experience replay buffer for reinforcement learning.
    
    Features:
    - Store experiences with priority
    - Multiple sampling strategies
    - Experience deduplication
    - Persistence support
    - Priority queue for efficient sampling
    
    Example:
        >>> buffer = ExperienceReplay(max_size=10000)
        >>> 
        >>> # Add experience
        >>> exp = Experience(
        ...     experience_id="exp_001",
        ...     state={"context": "chat"},
        ...     action={"response": "concise"},
        ...     reward=1.0,
        ... )
        >>> buffer.add(exp)
        >>> 
        >>> # Sample batch
        >>> batch = buffer.sample(batch_size=32)
    """
    
    def __init__(
        self,
        max_size: int = 10000,
        sampling_strategy: SamplingStrategy = SamplingStrategy.PRIORITIZED,
        alpha: float = 0.6,
        beta: float = 0.4,
        beta_increment: float = 0.001,
        epsilon: float = 1e-6,
        deduplication: bool = True,
        data_dir: Optional[Path] = None,
    ):
        """
        Initialize Experience Replay.
        
        Args:
            max_size: Maximum buffer size
            sampling_strategy: Strategy for sampling
            alpha: Priority exponent (0 = uniform, 1 = full priority)
            beta: Importance sampling exponent
            beta_increment: Beta increment per sample
            epsilon: Small value to avoid zero priority
            deduplication: Whether to deduplicate experiences
            data_dir: Optional directory for persistence
        """
        self.max_size = max_size
        self.sampling_strategy = sampling_strategy
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = beta_increment
        self.epsilon = epsilon
        self.deduplication = deduplication
        self.data_dir = data_dir
        
        self._buffer: List[Experience] = []
        self._priority_sum: float = 0.0
        self._hash_set: set = set()
        self._position: int = 0
        self._stats: Dict[str, Any] = {
            "total_added": 0,
            "total_sampled": 0,
            "duplicates_skipped": 0,
        }
        
        # Create data directory and load existing data only if data_dir is set
        if self.data_dir:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self._load()
    
    def add(self, experience: Experience) -> bool:
        """
        Add an experience to the buffer.
        
        Args:
            experience: Experience to add
            
        Returns:
            True if added, False if duplicate and deduplication enabled
        """
        # Check for duplicates
        if self.deduplication:
            exp_hash = experience.compute_hash()
            if exp_hash in self._hash_set:
                self._stats["duplicates_skipped"] += 1
                return False
            self._hash_set.add(exp_hash)
        
        # Buffer is full, remove oldest
        if len(self._buffer) >= self.max_size:
            removed = self._buffer[self._position]
            self._priority_sum -= removed.priority ** self.alpha
            self._buffer[self._position] = experience
        else:
            self._buffer.append(experience)
        
        # Update position
        self._position = (self._position + 1) % self.max_size
        
        # Update priority sum
        self._priority_sum += experience.priority ** self.alpha
        self._stats["total_added"] += 1
        
        # Persist
        if self.data_dir:
            self._save_experience(experience)
        
        return True
    
    def sample(
        self,
        batch_size: int = 32,
        strategy: Optional[SamplingStrategy] = None,
    ) -> Tuple[List[Experience], List[float], List[int]]:
        """
        Sample a batch of experiences.
        
        Args:
            batch_size: Number of experiences to sample
            strategy: Override default sampling strategy
            
        Returns:
            Tuple of (experiences, importance_weights, indices)
        """
        if not self._buffer:
            return [], [], []
        
        strategy = strategy or self.sampling_strategy
        batch_size = min(batch_size, len(self._buffer))
        
        if strategy == SamplingStrategy.UNIFORM:
            experiences, indices = self._sample_uniform(batch_size)
        elif strategy == SamplingStrategy.PRIORITIZED:
            experiences, indices = self._sample_prioritized(batch_size)
        elif strategy == SamplingStrategy.RECENT:
            experiences, indices = self._sample_recent(batch_size)
        else:  # BALANCED
            experiences, indices = self._sample_balanced(batch_size)
        
        # Calculate importance weights
        weights = self._calculate_importance_weights(experiences, indices)
        
        # Update stats
        self._stats["total_sampled"] += batch_size
        
        # Increment beta
        self.beta = min(1.0, self.beta + self.beta_increment)
        
        return experiences, weights, indices
    
    def update_priority(self, index: int, priority: float) -> None:
        """
        Update the priority of an experience.
        
        Args:
            index: Index of the experience
            priority: New priority
        """
        if 0 <= index < len(self._buffer):
            old_priority = self._buffer[index].priority
            self._priority_sum -= old_priority ** self.alpha
            self._buffer[index].priority = priority + self.epsilon
            self._priority_sum += self._buffer[index].priority ** self.alpha
    
    def update_priorities(self, indices: List[int], priorities: List[float]) -> None:
        """
        Update priorities for multiple experiences.
        
        Args:
            indices: List of indices
            priorities: List of new priorities
        """
        for index, priority in zip(indices, priorities):
            self.update_priority(index, priority)
    
    def get(self, index: int) -> Optional[Experience]:
        """
        Get an experience by index.
        
        Args:
            index: Index of the experience
            
        Returns:
            Experience if found, None otherwise
        """
        if 0 <= index < len(self._buffer):
            return self._buffer[index]
        return None
    
    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer.clear()
        self._priority_sum = 0.0
        self._hash_set.clear()
        self._position = 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get buffer statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self._buffer:
            return {
                "size": 0,
                "max_size": self.max_size,
                "priority_sum": 0.0,
                "avg_priority": 0.0,
                "avg_reward": 0.0,
                "total_added": self._stats["total_added"],
                "total_sampled": self._stats["total_sampled"],
                "duplicates_skipped": self._stats["duplicates_skipped"],
            }
        
        return {
            "size": len(self._buffer),
            "max_size": self.max_size,
            "priority_sum": self._priority_sum,
            "avg_priority": sum(e.priority for e in self._buffer) / len(self._buffer),
            "avg_reward": sum(e.reward for e in self._buffer) / len(self._buffer),
            "total_added": self._stats["total_added"],
            "total_sampled": self._stats["total_sampled"],
            "duplicates_skipped": self._stats["duplicates_skipped"],
        }
    
    def get_reward_distribution(self, bins: int = 10) -> Dict[str, int]:
        """
        Get reward distribution.
        
        Args:
            bins: Number of bins
            
        Returns:
            Dictionary with bin counts
        """
        if not self._buffer:
            return {}
        
        rewards = [e.reward for e in self._buffer]
        min_reward = min(rewards)
        max_reward = max(rewards)
        
        if min_reward == max_reward:
            return {f"{min_reward:.2f}": len(rewards)}
        
        bin_width = (max_reward - min_reward) / bins
        distribution = defaultdict(int)
        
        for reward in rewards:
            bin_index = int((reward - min_reward) / bin_width)
            bin_index = min(bin_index, bins - 1)
            bin_start = min_reward + bin_index * bin_width
            bin_end = bin_start + bin_width
            distribution[f"{bin_start:.2f}-{bin_end:.2f}"] += 1
        
        return dict(distribution)
    
    def _sample_uniform(self, batch_size: int) -> Tuple[List[Experience], List[int]]:
        """Uniform random sampling."""
        indices = random.sample(range(len(self._buffer)), batch_size)
        experiences = [self._buffer[i] for i in indices]
        return experiences, indices
    
    def _sample_prioritized(self, batch_size: int) -> Tuple[List[Experience], List[int]]:
        """Priority-based sampling."""
        if self._priority_sum <= 0:
            return self._sample_uniform(batch_size)
        
        indices = []
        experiences = []
        
        for _ in range(batch_size):
            # Sample based on priority
            target = random.random() * self._priority_sum
            cumulative = 0.0
            
            for i, exp in enumerate(self._buffer):
                cumulative += exp.priority ** self.alpha
                if cumulative >= target:
                    indices.append(i)
                    experiences.append(exp)
                    break
        
        return experiences, indices
    
    def _sample_recent(self, batch_size: int) -> Tuple[List[Experience], List[int]]:
        """Sample from recent experiences."""
        recent_size = min(batch_size * 3, len(self._buffer))
        start_index = max(0, len(self._buffer) - recent_size)
        
        indices = random.sample(
            range(start_index, len(self._buffer)),
            min(batch_size, recent_size)
        )
        experiences = [self._buffer[i] for i in indices]
        return experiences, indices
    
    def _sample_balanced(self, batch_size: int) -> Tuple[List[Experience], List[int]]:
        """Sample balanced across reward levels."""
        # Group by reward
        reward_groups = defaultdict(list)
        for i, exp in enumerate(self._buffer):
            reward_key = round(exp.reward, 1)
            reward_groups[reward_key].append(i)
        
        # Sample from each group
        indices = []
        per_group = max(1, batch_size // len(reward_groups))
        
        for group_indices in reward_groups.values():
            sample_size = min(per_group, len(group_indices))
            indices.extend(random.sample(group_indices, sample_size))
        
        # Trim to batch size
        if len(indices) > batch_size:
            indices = random.sample(indices, batch_size)
        
        experiences = [self._buffer[i] for i in indices]
        return experiences, indices
    
    def _calculate_importance_weights(
        self,
        experiences: List[Experience],
        indices: List[int],
    ) -> List[float]:
        """Calculate importance sampling weights."""
        if not experiences or self._priority_sum <= 0:
            return [1.0] * len(experiences)
        
        weights = []
        for i, exp in zip(indices, experiences):
            priority_prob = (exp.priority ** self.alpha) / self._priority_sum
            weight = (1.0 / (len(self._buffer) * priority_prob)) ** self.beta
            weights.append(weight)
        
        # Normalize weights
        max_weight = max(weights)
        weights = [w / max_weight for w in weights]
        
        return weights
    
    def _save_experience(self, experience: Experience) -> None:
        """Save an experience to disk."""
        if not self.data_dir:
            return
        
        exp_file = self.data_dir / f"{experience.experience_id}.json"
        with open(exp_file, "w", encoding="utf-8") as f:
            json.dump(experience.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _load(self) -> None:
        """Load experiences from disk."""
        if not self.data_dir:
            return
        
        for exp_file in self.data_dir.glob("*.json"):
            try:
                with open(exp_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                experience = Experience.from_dict(data)
                
                # Add to buffer (without deduplication check since loading)
                self._buffer.append(experience)
                self._priority_sum += experience.priority ** self.alpha
                
                if len(self._buffer) >= self.max_size:
                    break
            except (json.JSONDecodeError, KeyError):
                continue
        
        self._position = len(self._buffer) % self.max_size
    
    def __len__(self) -> int:
        """Return buffer size."""
        return len(self._buffer)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ExperienceReplay("
            f"size={len(self._buffer)}, "
            f"max_size={self.max_size}, "
            f"strategy={self.sampling_strategy.value}"
            f")"
        )
