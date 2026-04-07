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
Tests for Multi-Armed Bandit Module
"""

import pytest
from datetime import datetime

from claw_rl.mab import (
    MultiArmedBandit,
    Strategy,
    StrategyPerformance,
    BanditConfig,
    StrategyType,
)
from claw_rl.mab.mab import ThompsonSampler, EpsilonGreedy, UCB1
from claw_rl.mab.thompson_sampling import (
    BetaDistribution,
    ThompsonSamplingStrategy,
)
from claw_rl.mab.epsilon_greedy import (
    EpsilonGreedyStrategy,
    DecayMode,
)


class TestStrategy:
    """Tests for Strategy"""
    
    def test_create_strategy(self):
        """Test creating a strategy"""
        strategy = Strategy(
            strategy_id="strat_001",
            name="Test Strategy",
            strategy_type=StrategyType.BEHAVIOR,
        )
        
        assert strategy.strategy_id == "strat_001"
        assert strategy.name == "Test Strategy"
        assert strategy.strategy_type == StrategyType.BEHAVIOR
    
    def test_strategy_to_dict(self):
        """Test strategy serialization"""
        strategy = Strategy(
            strategy_id="strat_002",
            name="Prompt Strategy",
            strategy_type=StrategyType.PROMPT,
            parameters={"temperature": 0.7},
        )
        
        data = strategy.to_dict()
        assert data["strategy_id"] == "strat_002"
        assert data["name"] == "Prompt Strategy"
        assert data["strategy_type"] == "prompt"
        assert data["parameters"]["temperature"] == 0.7
    
    def test_strategy_from_dict(self):
        """Test strategy deserialization"""
        data = {
            "strategy_id": "strat_003",
            "name": "Model Strategy",
            "strategy_type": "model",
            "parameters": {"model": "gpt-4"},
        }
        
        strategy = Strategy.from_dict(data)
        assert strategy.strategy_id == "strat_003"
        assert strategy.strategy_type == StrategyType.MODEL


class TestStrategyPerformance:
    """Tests for StrategyPerformance"""
    
    def test_initial_performance(self):
        """Test initial performance state"""
        perf = StrategyPerformance(strategy_id="strat_001")
        
        assert perf.total_trials == 0
        assert perf.total_rewards == 0.0
        assert perf.average_reward == 0.0
    
    def test_update_with_success(self):
        """Test updating with success"""
        perf = StrategyPerformance(strategy_id="strat_001")
        
        perf.update(1.0)  # Success
        
        assert perf.total_trials == 1
        assert perf.total_rewards == 1.0
        assert perf.average_reward == 1.0
        assert perf.alpha == 2.0  # Started at 1.0, +1 for success
    
    def test_update_with_failure(self):
        """Test updating with failure"""
        perf = StrategyPerformance(strategy_id="strat_001")
        
        perf.update(0.0)  # Failure
        
        assert perf.total_trials == 1
        assert perf.total_rewards == 0.0
        assert perf.average_reward == 0.0
        assert perf.beta == 2.0  # Started at 1.0, +1 for failure
    
    def test_multiple_updates(self):
        """Test multiple updates"""
        perf = StrategyPerformance(strategy_id="strat_001")
        
        for i in range(10):
            reward = 1.0 if i % 2 == 0 else 0.0
            perf.update(reward)
        
        assert perf.total_trials == 10
        assert perf.total_rewards == 5.0
        assert perf.average_reward == 0.5
    
    def test_performance_to_dict(self):
        """Test performance serialization"""
        perf = StrategyPerformance(strategy_id="strat_001")
        perf.update(1.0)
        
        data = perf.to_dict()
        assert data["strategy_id"] == "strat_001"
        assert data["total_trials"] == 1
        assert data["alpha"] == 2.0


class TestThompsonSampler:
    """Tests for Thompson Sampler"""
    
    def test_sample_beta_distribution(self):
        """Test sampling from Beta distribution"""
        sampler = ThompsonSampler(seed=42)
        perf = StrategyPerformance(strategy_id="strat_001")
        perf.update(1.0)  # 1 success
        perf.update(1.0)  # 2 successes
        perf.update(0.0)  # 1 failure
        
        samples = [sampler.sample(perf) for _ in range(100)]
        
        # Samples should be between 0 and 1
        assert all(0 <= s <= 1 for s in samples)
        
        # Mean should be around 2/3 (2 successes, 1 failure)
        mean_sample = sum(samples) / len(samples)
        assert 0.5 < mean_sample < 0.9


class TestEpsilonGreedy:
    """Tests for Epsilon-Greedy"""
    
    def test_initial_epsilon(self):
        """Test initial epsilon value"""
        eg = EpsilonGreedy(epsilon=0.1)
        
        assert eg.epsilon == 0.1
    
    def test_explore_decision(self):
        """Test explore decision"""
        eg = EpsilonGreedy(epsilon=1.0, seed=42)  # Always explore
        
        assert eg.should_explore()
    
    def test_exploit_decision(self):
        """Test exploit decision"""
        eg = EpsilonGreedy(epsilon=0.0, seed=42)  # Never explore
        
        assert not eg.should_explore()
    
    def test_epsilon_decay(self):
        """Test epsilon decay"""
        eg = EpsilonGreedy(epsilon=0.1, decay=0.9, min_epsilon=0.01)
        
        initial = eg.epsilon
        eg.decay_epsilon()
        
        assert eg.epsilon < initial
        assert eg.epsilon == initial * 0.9


class TestUCB1:
    """Tests for UCB1"""
    
    def test_ucb_calculation(self):
        """Test UCB calculation"""
        ucb = UCB1(c=2.0)
        perf = StrategyPerformance(strategy_id="strat_001")
        perf.update(1.0)
        perf.update(0.5)
        perf.update(0.0)
        
        ucb_value = ucb.calculate_ucb(perf, total_trials=3)
        
        # UCB should be average + exploration bonus
        assert ucb_value > perf.average_reward
    
    def test_ucb_unexplored(self):
        """Test UCB for unexplored strategy"""
        ucb = UCB1(c=2.0)
        perf = StrategyPerformance(strategy_id="strat_001")
        
        # Unexplored strategy should have infinite UCB
        ucb_value = ucb.calculate_ucb(perf, total_trials=10)
        
        assert ucb_value == float('inf')


class TestMultiArmedBandit:
    """Tests for Multi-Armed Bandit"""
    
    def test_register_strategy(self):
        """Test registering strategies"""
        mab = MultiArmedBandit()
        
        strategy = Strategy(
            strategy_id="strat_001",
            name="Strategy 1",
        )
        
        mab.register_strategy(strategy)
        
        assert len(mab.strategies) == 1
        assert "strat_001" in mab.strategies
    
    def test_register_duplicate_strategy(self):
        """Test registering duplicate strategy"""
        mab = MultiArmedBandit()
        
        strategy = Strategy(strategy_id="strat_001", name="Strategy 1")
        mab.register_strategy(strategy)
        
        with pytest.raises(Exception):
            mab.register_strategy(strategy)
    
    def test_select_strategy_single(self):
        """Test selecting with single strategy"""
        mab = MultiArmedBandit()
        
        strategy = Strategy(strategy_id="strat_001", name="Strategy 1")
        mab.register_strategy(strategy)
        
        selected = mab.select_strategy()
        
        assert selected.strategy_id == "strat_001"
    
    def test_select_strategy_thompson_sampling(self):
        """Test Thompson Sampling selection"""
        config = BanditConfig(algorithm="thompson_sampling", seed=42)
        mab = MultiArmedBandit(config=config)
        
        for i in range(3):
            mab.register_strategy(Strategy(
                strategy_id=f"strat_{i:03d}",
                name=f"Strategy {i}",
            ))
        
        # Add some history
        mab.update("strat_000", 1.0)
        mab.update("strat_000", 1.0)
        mab.update("strat_001", 0.5)
        mab.update("strat_002", 0.0)
        
        selected = mab.select_strategy()
        
        assert selected is not None
    
    def test_select_strategy_epsilon_greedy(self):
        """Test Epsilon-Greedy selection"""
        config = BanditConfig(algorithm="epsilon_greedy", epsilon=0.3, seed=42)
        mab = MultiArmedBandit(config=config)
        
        for i in range(3):
            mab.register_strategy(Strategy(
                strategy_id=f"strat_{i:03d}",
                name=f"Strategy {i}",
            ))
        
        selected = mab.select_strategy()
        
        assert selected is not None
    
    def test_select_strategy_ucb1(self):
        """Test UCB1 selection"""
        config = BanditConfig(algorithm="ucb1", seed=42)
        mab = MultiArmedBandit(config=config)
        
        for i in range(3):
            mab.register_strategy(Strategy(
                strategy_id=f"strat_{i:03d}",
                name=f"Strategy {i}",
            ))
        
        selected = mab.select_strategy()
        
        assert selected is not None
    
    def test_update_performance(self):
        """Test updating performance"""
        mab = MultiArmedBandit()
        
        strategy = Strategy(strategy_id="strat_001", name="Strategy 1")
        mab.register_strategy(strategy)
        
        mab.update("strat_001", 1.0)
        mab.update("strat_001", 0.5)
        
        perf = mab.get_performance("strat_001")
        
        assert perf.total_trials == 2
        assert perf.total_rewards == 1.5
        assert perf.average_reward == 0.75
    
    def test_get_best_strategy(self):
        """Test getting best strategy"""
        mab = MultiArmedBandit()
        
        mab.register_strategy(Strategy(strategy_id="strat_001", name="Strategy 1"))
        mab.register_strategy(Strategy(strategy_id="strat_002", name="Strategy 2"))
        
        mab.update("strat_001", 0.5)
        mab.update("strat_001", 0.5)
        mab.update("strat_002", 1.0)
        mab.update("strat_002", 1.0)
        
        best = mab.get_best_strategy()
        
        assert best.strategy_id == "strat_002"
    
    def test_warm_start(self):
        """Test warm start behavior"""
        config = BanditConfig(warm_start_trials=5, seed=42)
        mab = MultiArmedBandit(config=config)
        
        for i in range(3):
            mab.register_strategy(Strategy(
                strategy_id=f"strat_{i:03d}",
                name=f"Strategy {i}",
            ))
        
        # Initially, should explore under-explored strategies
        selections = []
        for _ in range(10):
            selected = mab.select_strategy()
            selections.append(selected.strategy_id)
        
        # Should have selected different strategies during warm start
        assert len(set(selections)) > 1
    
    def test_get_stats(self):
        """Test getting statistics"""
        mab = MultiArmedBandit()
        
        mab.register_strategy(Strategy(strategy_id="strat_001", name="Strategy 1"))
        mab.update("strat_001", 1.0)
        
        stats = mab.get_stats()
        
        assert stats["total_strategies"] == 1
        assert stats["total_trials"] == 1
    
    def test_reset(self):
        """Test resetting bandit"""
        mab = MultiArmedBandit()
        
        mab.register_strategy(Strategy(strategy_id="strat_001", name="Strategy 1"))
        mab.update("strat_001", 1.0)
        
        mab.reset()
        
        perf = mab.get_performance("strat_001")
        assert perf.total_trials == 0


class TestThompsonSamplingStrategy:
    """Tests for Thompson Sampling Strategy"""
    
    def test_register_strategy(self):
        """Test registering strategy"""
        ts = ThompsonSamplingStrategy(seed=42)
        ts.register_strategy("strat_001")
        
        assert "strat_001" in ts.distributions
    
    def test_update_success(self):
        """Test updating with success"""
        ts = ThompsonSamplingStrategy(seed=42)
        ts.register_strategy("strat_001")
        ts.update("strat_001", success=True)
        
        dist = ts.get_distribution("strat_001")
        assert dist.alpha == 2.0
        assert dist.beta == 1.0
    
    def test_update_failure(self):
        """Test updating with failure"""
        ts = ThompsonSamplingStrategy(seed=42)
        ts.register_strategy("strat_001")
        ts.update("strat_001", success=False)
        
        dist = ts.get_distribution("strat_001")
        assert dist.alpha == 1.0
        assert dist.beta == 2.0
    
    def test_select_strategy(self):
        """Test strategy selection"""
        ts = ThompsonSamplingStrategy(seed=42)
        ts.register_strategy("strat_001")
        ts.register_strategy("strat_002")
        
        # Give strat_001 better performance
        ts.update("strat_001", success=True)
        ts.update("strat_001", success=True)
        ts.update("strat_002", success=False)
        
        selected = ts.select_strategy()
        assert selected in ["strat_001", "strat_002"]


class TestEpsilonGreedyStrategy:
    """Tests for Epsilon Greedy Strategy"""
    
    def test_register_strategy(self):
        """Test registering strategy"""
        egs = EpsilonGreedyStrategy(seed=42)
        egs.register_strategy("strat_001")
        
        assert "strat_001" in egs.strategy_rewards
    
    def test_always_explore(self):
        """Test always explore mode"""
        egs = EpsilonGreedyStrategy(initial_epsilon=1.0, seed=42)
        
        assert egs.should_explore()
    
    def test_never_explore(self):
        """Test never explore mode"""
        egs = EpsilonGreedyStrategy(initial_epsilon=0.0, seed=42)
        
        assert not egs.should_explore()
    
    def test_update_and_select(self):
        """Test update and selection"""
        egs = EpsilonGreedyStrategy(initial_epsilon=0.0, seed=42)
        egs.register_strategy("strat_001")
        egs.register_strategy("strat_002")
        
        # Give strat_001 better performance
        egs.update("strat_001", reward=1.0)
        egs.update("strat_002", reward=0.0)
        
        # With epsilon=0, should always select best
        selected = egs.select_strategy()
        assert selected == "strat_001"
    
    def test_exponential_decay(self):
        """Test exponential decay"""
        egs = EpsilonGreedyStrategy(
            initial_epsilon=0.1,
            decay_rate=0.9,
            decay_mode=DecayMode.EXPONENTIAL,
        )
        
        initial = egs.epsilon
        # Decay happens in update()
        egs.register_strategy("strat_001")
        for _ in range(10):
            egs.update("strat_001", reward=1.0)
        
        assert egs.epsilon < initial
        # After 10 updates, epsilon should be initial * decay_rate^10
        expected = initial * (0.9 ** 10)
        assert abs(egs.epsilon - expected) < 0.001
    
    def test_linear_decay(self):
        """Test linear decay"""
        egs = EpsilonGreedyStrategy(
            initial_epsilon=0.1,
            decay_mode=DecayMode.LINEAR,
        )
        egs.total_steps = 100
        
        for _ in range(50):
            egs._decay_epsilon()
        
        # After 50% of steps, epsilon should be ~50% of initial
        assert egs.epsilon < egs.initial_epsilon


class TestBetaDistribution:
    """Tests for Beta Distribution"""
    
    def test_initial_distribution(self):
        """Test initial Beta(1,1) distribution"""
        beta = BetaDistribution()
        
        assert beta.alpha == 1.0
        assert beta.beta == 1.0
    
    def test_update_success(self):
        """Test update with success"""
        beta = BetaDistribution()
        beta.update(success=True)
        
        assert beta.alpha == 2.0
        assert beta.beta == 1.0
    
    def test_update_failure(self):
        """Test update with failure"""
        beta = BetaDistribution()
        beta.update(success=False)
        
        assert beta.alpha == 1.0
        assert beta.beta == 2.0
    
    def test_mean(self):
        """Test mean calculation"""
        beta = BetaDistribution(alpha=2.0, beta=2.0)
        
        assert beta.mean() == 0.5
    
    def test_variance(self):
        """Test variance calculation"""
        beta = BetaDistribution(alpha=2.0, beta=2.0)
        
        # Variance of Beta(2,2) = 4 / (16 * 5) = 0.05
        assert abs(beta.variance() - 0.05) < 0.01
    
    def test_sample(self):
        """Test sampling from distribution"""
        beta = BetaDistribution(alpha=2.0, beta=2.0)
        
        samples = [beta.sample() for _ in range(100)]
        
        # All samples should be between 0 and 1
        assert all(0 <= s <= 1 for s in samples)
        
        # Mean should be around 0.5
        mean_sample = sum(samples) / len(samples)
        assert 0.3 < mean_sample < 0.7
