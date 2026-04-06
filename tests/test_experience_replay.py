"""
Tests for Experience Replay
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import json

from claw_rl.learning.experience_replay import (
    ExperienceReplay,
    Experience,
    SamplingStrategy,
)


class TestExperience:
    """Tests for Experience."""
    
    def test_create_experience(self):
        """Test creating an experience."""
        exp = Experience(
            experience_id="exp_001",
            state={"context": "chat"},
            action={"response": "concise"},
            reward=1.0,
        )
        
        assert exp.experience_id == "exp_001"
        assert exp.state == {"context": "chat"}
        assert exp.action == {"response": "concise"}
        assert exp.reward == 1.0
        assert exp.done is False
        assert exp.priority == 1.0
    
    def test_experience_to_dict(self):
        """Test converting experience to dict."""
        exp = Experience(
            experience_id="exp_002",
            state={"x": 1},
            action={"y": 2},
            reward=0.5,
            next_state={"x": 2},
            done=True,
            priority=2.0,
        )
        
        result = exp.to_dict()
        
        assert result["experience_id"] == "exp_002"
        assert result["state"] == {"x": 1}
        assert result["action"] == {"y": 2}
        assert result["reward"] == 0.5
        assert result["next_state"] == {"x": 2}
        assert result["done"] is True
        assert result["priority"] == 2.0
    
    def test_experience_from_dict(self):
        """Test creating experience from dict."""
        data = {
            "experience_id": "exp_003",
            "state": {"a": 1},
            "action": {"b": 2},
            "reward": -0.5,
            "next_state": {"a": 2},
            "done": False,
            "priority": 3.0,
        }
        
        exp = Experience.from_dict(data)
        
        assert exp.experience_id == "exp_003"
        assert exp.state == {"a": 1}
        assert exp.action == {"b": 2}
        assert exp.reward == -0.5
        assert exp.priority == 3.0
    
    def test_compute_hash(self):
        """Test hash computation."""
        exp1 = Experience(
            experience_id="exp_001",
            state={"x": 1},
            action={"y": 2},
            reward=1.0,
        )
        
        exp2 = Experience(
            experience_id="exp_002",  # Different ID
            state={"x": 1},
            action={"y": 2},
            reward=1.0,
        )
        
        exp3 = Experience(
            experience_id="exp_003",
            state={"x": 2},  # Different state
            action={"y": 2},
            reward=1.0,
        )
        
        # Same content should produce same hash
        assert exp1.compute_hash() == exp2.compute_hash()
        
        # Different content should produce different hash
        assert exp1.compute_hash() != exp3.compute_hash()


class TestExperienceReplay:
    """Tests for ExperienceReplay."""
    
    @pytest.fixture
    def buffer(self):
        """Create an experience replay buffer."""
        # Use a unique temp directory for each test to avoid persistence conflicts
        import uuid
        with tempfile.TemporaryDirectory() as tmpdir:
            unique_dir = Path(tmpdir) / str(uuid.uuid4())
            unique_dir.mkdir(parents=True, exist_ok=True)
            yield ExperienceReplay(
                max_size=100,
                data_dir=unique_dir,
            )
    
    def test_create_buffer(self):
        """Test creating a buffer."""
        buffer = ExperienceReplay(max_size=1000, data_dir=None)
        assert len(buffer) == 0
    
    def test_add_experience(self, buffer):
        """Test adding an experience."""
        exp = Experience(
            experience_id="exp_001",
            state={"x": 1},
            action={"y": 2},
            reward=1.0,
        )
        
        result = buffer.add(exp)
        
        assert result is True
        assert len(buffer) == 1
    
    def test_add_duplicate(self, buffer):
        """Test adding a duplicate experience."""
        exp = Experience(
            experience_id="exp_001",
            state={"x": 1},
            action={"y": 2},
            reward=1.0,
        )
        
        buffer.add(exp)
        result = buffer.add(exp)
        
        assert result is False
        assert len(buffer) == 1
    
    def test_add_duplicate_disabled(self):
        """Test adding duplicates with deduplication disabled."""
        buffer = ExperienceReplay(max_size=100, deduplication=False, data_dir=None)
        
        exp = Experience(
            experience_id="exp_001",
            state={"x": 1},
            action={"y": 2},
            reward=1.0,
        )
        
        buffer.add(exp)
        result = buffer.add(exp)
        
        assert result is True
        assert len(buffer) == 2
    
    def test_max_size_limit(self):
        """Test max size limit."""
        buffer = ExperienceReplay(max_size=5)
        
        for i in range(10):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
            )
            buffer.add(exp)
        
        assert len(buffer) <= 5
    
    def test_sample_uniform(self, buffer):
        """Test uniform sampling."""
        for i in range(20):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
            )
            buffer.add(exp)
        
        experiences, weights, indices = buffer.sample(
            batch_size=5,
            strategy=SamplingStrategy.UNIFORM,
        )
        
        assert len(experiences) == 5
        assert len(weights) == 5
        assert len(indices) == 5
    
    def test_sample_prioritized(self, buffer):
        """Test prioritized sampling."""
        # Add experiences with different priorities
        for i in range(10):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
                priority=float(i + 1),  # Higher priority for later
            )
            buffer.add(exp)
        
        experiences, weights, indices = buffer.sample(
            batch_size=5,
            strategy=SamplingStrategy.PRIORITIZED,
        )
        
        assert len(experiences) == 5
    
    def test_sample_recent(self, buffer):
        """Test recent sampling."""
        for i in range(20):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
            )
            buffer.add(exp)
        
        experiences, weights, indices = buffer.sample(
            batch_size=5,
            strategy=SamplingStrategy.RECENT,
        )
        
        assert len(experiences) == 5
        # Recent experiences should come from the later part of the buffer
        # The recent_size is batch_size * 3 = 15, so indices should be >= 5
        assert all(i >= 5 for i in indices)
    
    def test_sample_balanced(self, buffer):
        """Test balanced sampling."""
        # Add experiences with different rewards
        for i in range(30):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i % 3),  # Rewards: 0, 1, 2
            )
            buffer.add(exp)
        
        experiences, weights, indices = buffer.sample(
            batch_size=9,
            strategy=SamplingStrategy.BALANCED,
        )
        
        assert len(experiences) == 9
        # Should have samples from all reward levels
    
    def test_sample_empty_buffer(self):
        """Test sampling from empty buffer."""
        # Use a fresh buffer without data_dir to avoid persistence
        buffer = ExperienceReplay(data_dir=None)
        experiences, weights, indices = buffer.sample(batch_size=5)
        
        assert experiences == []
        assert weights == []
        assert indices == []
        assert weights == []
        assert indices == []
    
    def test_sample_batch_size_larger_than_buffer(self, buffer):
        """Test sampling when batch size is larger than buffer."""
        for i in range(5):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
            )
            buffer.add(exp)
        
        experiences, weights, indices = buffer.sample(batch_size=10)
        
        assert len(experiences) == 5
    
    def test_update_priority(self, buffer):
        """Test updating priority."""
        exp = Experience(
            experience_id="exp_001",
            state={"x": 1},
            action={"y": 2},
            reward=1.0,
            priority=1.0,
        )
        buffer.add(exp)
        
        buffer.update_priority(0, 5.0)
        
        assert buffer.get(0).priority == 5.0 + buffer.epsilon
    
    def test_update_priorities(self, buffer):
        """Test updating multiple priorities."""
        for i in range(5):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
            )
            buffer.add(exp)
        
        buffer.update_priorities(
            indices=[0, 1, 2],
            priorities=[2.0, 3.0, 4.0],
        )
        
        assert buffer.get(0).priority > 1.0
        assert buffer.get(1).priority > 1.0
        assert buffer.get(2).priority > 1.0
    
    def test_get_experience(self, buffer):
        """Test getting an experience."""
        exp = Experience(
            experience_id="exp_001",
            state={"x": 1},
            action={"y": 2},
            reward=1.0,
        )
        buffer.add(exp)
        
        result = buffer.get(0)
        
        assert result.experience_id == "exp_001"
    
    def test_get_out_of_range(self, buffer):
        """Test getting out of range experience."""
        result = buffer.get(100)
        assert result is None
    
    def test_clear(self, buffer):
        """Test clearing buffer."""
        for i in range(10):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
            )
            buffer.add(exp)
        
        buffer.clear()
        
        assert len(buffer) == 0
    
    def test_get_statistics(self, buffer):
        """Test getting statistics."""
        for i in range(10):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
                priority=float(i + 1),
            )
            buffer.add(exp)
        
        stats = buffer.get_statistics()
        
        assert stats["size"] == 10
        assert stats["total_added"] == 10
        assert stats["avg_reward"] == 4.5  # (0+1+...+9) / 10
    
    def test_get_reward_distribution(self, buffer):
        """Test getting reward distribution."""
        for i in range(10):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i % 3),  # 0, 1, 2 repeated
            )
            buffer.add(exp)
        
        dist = buffer.get_reward_distribution()
        
        assert isinstance(dist, dict)
        # Should have distribution across reward levels
    
    def test_persistence(self):
        """Test persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            
            # Create and save experiences
            buffer1 = ExperienceReplay(max_size=100, data_dir=data_dir)
            for i in range(5):
                exp = Experience(
                    experience_id=f"exp_{i:03d}",
                    state={"x": i},
                    action={"y": i},
                    reward=float(i),
                )
                buffer1.add(exp)
            
            # Load in new instance
            buffer2 = ExperienceReplay(max_size=100, data_dir=data_dir)
            
            assert len(buffer2) == 5
    
    def test_beta_increment(self, buffer):
        """Test beta increment on sampling."""
        initial_beta = buffer.beta
        
        for i in range(10):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
            )
            buffer.add(exp)
        
        buffer.sample(batch_size=5)
        
        assert buffer.beta > initial_beta
    
    def test_repr(self, buffer):
        """Test string representation."""
        result = repr(buffer)
        
        assert "ExperienceReplay" in result
        assert "size=" in result
        assert "max_size=" in result


class TestSamplingStrategies:
    """Tests for different sampling strategies."""
    
    def test_uniform_equal_probability(self):
        """Test uniform sampling has equal probability."""
        buffer = ExperienceReplay(max_size=100, deduplication=False, data_dir=None)
        
        for i in range(10):
            exp = Experience(
                experience_id=f"exp_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
            )
            buffer.add(exp)
        
        # Sample many times and count
        counts = {i: 0 for i in range(10)}
        for _ in range(1000):
            _, _, indices = buffer.sample(batch_size=1, strategy=SamplingStrategy.UNIFORM)
            for idx in indices:
                counts[idx] += 1
        
        # All should be roughly equal (within statistical variance)
        avg_count = sum(counts.values()) / 10
        for count in counts.values():
            assert 0.5 * avg_count < count < 1.5 * avg_count
    
    def test_prioritized_higher_priority_more_likely(self):
        """Test prioritized sampling favors higher priority."""
        buffer = ExperienceReplay(
            max_size=100,
            sampling_strategy=SamplingStrategy.PRIORITIZED,
            deduplication=False,
            data_dir=None,
        )
        
        # Add low priority experiences
        for i in range(5):
            exp = Experience(
                experience_id=f"low_{i:03d}",
                state={"x": i},
                action={"y": i},
                reward=float(i),
                priority=0.1,
            )
            buffer.add(exp)
        
        # Add high priority experiences
        for i in range(5):
            exp = Experience(
                experience_id=f"high_{i:03d}",
                state={"x": i + 10},
                action={"y": i + 10},
                reward=float(i + 10),
                priority=10.0,
            )
            buffer.add(exp)
        
        # Sample many times and count
        high_count = 0
        low_count = 0
        for _ in range(1000):
            exps, _, _ = buffer.sample(batch_size=1)
            if exps[0].priority > 1.0:
                high_count += 1
            else:
                low_count += 1
        
        # High priority should be sampled more often
        assert high_count > low_count
