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
Tests for Adaptive Multi-Armed Bandit (v2.1.0)
"""

import pytest
from datetime import datetime

from claw_rl.mab.adaptive import (
    AdaptiveMAB,
    ContextFeatures,
    StrategyPerformance,
    MetaLearner,
    AdaptationMode,
)


class TestContextFeatures:
    """Tests for ContextFeatures"""
    
    def test_to_vector(self):
        """Test conversion to feature vector"""
        ctx = ContextFeatures(
            data_size=50,
            data_variance=0.3,
            hour_of_day=14,
            day_of_week=2,
            recent_success_rate=0.7,
            cumulative_reward=25.0,
            operation_type="file",
            memory_usage=0.5,
            latency_budget_ms=500
        )
        
        vector = ctx.to_vector()
        
        assert len(vector) == 11
        assert 0 <= vector[0] <= 1  # Normalized data_size
        assert vector[2] == 14 / 24.0  # Normalized hour
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        ctx = ContextFeatures(
            operation_type="code",
            data_size=100
        )
        
        d = ctx.to_dict()
        
        assert d['operation_type'] == "code"
        assert d['data_size'] == 100


class TestStrategyPerformance:
    """Tests for StrategyPerformance"""
    
    def test_init(self):
        """Test initialization"""
        perf = StrategyPerformance(strategy_id="test-strategy")
        
        assert perf.total_selections == 0
        assert perf.success_rate == 0.5  # Default for no data
    
    def test_update(self):
        """Test update with observation"""
        perf = StrategyPerformance(strategy_id="test")
        
        perf.update(reward=1.0, latency_ms=10.0, context_key="file|small")
        
        assert perf.total_selections == 1
        assert perf.total_reward == 1.0
        assert perf.successful_selections == 1
        assert perf.success_rate == 1.0
        assert perf.avg_reward == 1.0
    
    def test_multiple_updates(self):
        """Test multiple updates"""
        perf = StrategyPerformance(strategy_id="test")
        
        perf.update(reward=1.0)
        perf.update(reward=0.0)
        perf.update(reward=1.0)
        perf.update(reward=-1.0)
        
        assert perf.total_selections == 4
        assert perf.total_reward == 1.0
        assert perf.successful_selections == 2
        assert perf.success_rate == 0.5
        assert perf.avg_reward == 0.25
    
    def test_context_performance(self):
        """Test context-specific performance tracking"""
        perf = StrategyPerformance(strategy_id="test")
        
        perf.update(reward=1.0, context_key="file")
        perf.update(reward=0.5, context_key="file")
        perf.update(reward=0.0, context_key="code")
        
        assert "file" in perf.context_performance
        assert "code" in perf.context_performance
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        perf = StrategyPerformance(strategy_id="test")
        perf.update(reward=1.0)
        
        d = perf.to_dict()
        
        assert d['strategy_id'] == "test"
        assert d['total_selections'] == 1
        assert 'success_rate' in d
        assert 'avg_reward' in d


class TestMetaLearner:
    """Tests for MetaLearner"""
    
    def test_init(self):
        """Test initialization"""
        learner = MetaLearner()
        
        assert len(learner.strategy_performance) == 0
        assert len(learner.context_strategy_map) == 0
    
    def test_register_strategy(self):
        """Test strategy registration"""
        learner = MetaLearner()
        
        learner.register_strategy("thompson")
        
        assert "thompson" in learner.strategy_performance
    
    def test_get_context_key(self):
        """Test context key generation"""
        learner = MetaLearner()
        
        ctx1 = ContextFeatures(operation_type="file", data_size=5, recent_success_rate=0.8)
        ctx2 = ContextFeatures(operation_type="file", data_size=150, recent_success_rate=0.2)
        ctx3 = ContextFeatures(operation_type="code", data_size=50, recent_success_rate=0.5)
        
        key1 = learner.get_context_key(ctx1)
        key2 = learner.get_context_key(ctx2)
        key3 = learner.get_context_key(ctx3)
        
        assert "file" in key1
        assert "file" in key2
        assert "code" in key3
        # Different context features should produce different keys
        assert key1 != key2
    
    def test_predict_best_strategy(self):
        """Test strategy prediction"""
        learner = MetaLearner()
        learner.register_strategy("s1")
        learner.register_strategy("s2")
        
        ctx = ContextFeatures(operation_type="file", data_size=10)
        
        predicted = learner.predict_best_strategy(ctx)
        
        assert predicted in ["s1", "s2"]
    
    def test_update(self):
        """Test update with observation"""
        learner = MetaLearner()
        learner.register_strategy("s1")
        
        ctx = ContextFeatures(operation_type="file", data_size=10)
        
        learner.update("s1", reward=1.0, context=ctx, latency_ms=10.0)
        
        assert len(learner.history) == 1
        assert learner.strategy_performance["s1"].total_selections == 1
    
    def test_update_mapping(self):
        """Test that mapping is updated after observations"""
        learner = MetaLearner()
        learner.register_strategy("s1")
        learner.register_strategy("s2")
        
        ctx = ContextFeatures(operation_type="file", data_size=10)
        
        # s1 performs well
        learner.update("s1", reward=1.0, context=ctx)
        learner.update("s1", reward=1.0, context=ctx)
        
        # s2 performs poorly
        learner.update("s2", reward=0.0, context=ctx)
        learner.update("s2", reward=-1.0, context=ctx)
        
        # s1 should be predicted as best for this context
        predicted = learner.predict_best_strategy(ctx)
        
        # s1 should be preferred (higher avg reward)
        assert predicted == "s1"
    
    def test_get_stats(self):
        """Test statistics retrieval"""
        learner = MetaLearner()
        learner.register_strategy("s1")
        learner.update("s1", reward=1.0, context=ContextFeatures())
        
        stats = learner.get_stats()
        
        assert stats['strategies'] == 1
        assert stats['history_size'] == 1


class TestAdaptiveMAB:
    """Tests for AdaptiveMAB"""
    
    def test_init(self):
        """Test initialization"""
        mab = AdaptiveMAB()
        
        assert mab.adaptation_mode == AdaptationMode.HYBRID
        assert len(mab.strategies) == 0
    
    def test_init_with_mode(self):
        """Test initialization with mode"""
        mab = AdaptiveMAB(adaptation_mode=AdaptationMode.CONTEXTUAL)
        
        assert mab.adaptation_mode == AdaptationMode.CONTEXTUAL
    
    def test_register_strategy(self):
        """Test strategy registration"""
        mab = AdaptiveMAB()
        
        mab.register_strategy("thompson")
        mab.register_strategy("epsilon_greedy")
        
        assert len(mab.strategies) == 2
        assert "thompson" in mab.strategies
    
    def test_select_strategy_no_strategies(self):
        """Test selection with no strategies"""
        mab = AdaptiveMAB()
        
        with pytest.raises(ValueError):
            mab.select_strategy()
    
    def test_select_strategy_static(self):
        """Test static selection"""
        mab = AdaptiveMAB(adaptation_mode=AdaptationMode.STATIC)
        mab.register_strategy("s1")
        mab.register_strategy("s2")
        
        # Update to make s1 better
        mab.update("s1", reward=1.0)
        mab.update("s2", reward=0.0)
        
        selected = mab.select_strategy()
        
        # Should select s1 (higher avg reward)
        assert selected == "s1"
    
    def test_select_strategy_contextual(self):
        """Test contextual selection"""
        mab = AdaptiveMAB(adaptation_mode=AdaptationMode.CONTEXTUAL)
        mab.register_strategy("s1")
        mab.register_strategy("s2")
        
        ctx = ContextFeatures(operation_type="file", data_size=10)
        
        selected = mab.select_strategy(ctx)
        
        assert selected in ["s1", "s2"]
    
    def test_update(self):
        """Test update with observation"""
        mab = AdaptiveMAB()
        mab.register_strategy("s1")
        
        ctx = ContextFeatures(operation_type="file")
        mab.update("s1", reward=1.0, latency_ms=10.0, context=ctx)
        
        assert mab.total_selections == 1
        assert mab.total_reward == 1.0
        assert len(mab.recent_rewards) == 1
    
    def test_epsilon_decay(self):
        """Test epsilon decay"""
        mab = AdaptiveMAB(config={'initial_epsilon': 0.5, 'epsilon_decay': 0.9})
        mab.register_strategy("s1")
        
        initial = mab.current_epsilon
        
        for _ in range(10):
            mab.update("s1", reward=1.0)
        
        # Epsilon should have decayed
        assert mab.current_epsilon < initial
    
    def test_adapt_parameters_poor_performance(self):
        """Test parameter adaptation for poor performance"""
        mab = AdaptiveMAB(config={'initial_epsilon': 0.05})
        mab.register_strategy("s1")
        
        # Simulate poor performance
        for _ in range(10):
            mab.update("s1", reward=-1.0)
        
        # Epsilon should have been boosted
        # (depends on recent rewards being low)
        assert mab.current_epsilon >= 0.05
    
    def test_get_best_strategy(self):
        """Test getting best strategy"""
        mab = AdaptiveMAB()
        mab.register_strategy("s1")
        mab.register_strategy("s2")
        
        mab.update("s1", reward=1.0)
        mab.update("s2", reward=0.0)
        
        best = mab.get_best_strategy()
        
        assert best == "s1"
    
    def test_get_strategy_stats(self):
        """Test getting strategy stats"""
        mab = AdaptiveMAB()
        mab.register_strategy("s1")
        mab.update("s1", reward=1.0)
        
        stats = mab.get_strategy_stats("s1")
        
        assert stats is not None
        assert stats['strategy_id'] == "s1"
        assert stats['total_selections'] == 1
    
    def test_get_all_stats(self):
        """Test getting all stats"""
        mab = AdaptiveMAB()
        mab.register_strategy("s1")
        mab.update("s1", reward=1.0)
        
        stats = mab.get_all_stats()
        
        assert 'mode' in stats
        assert 'epsilon' in stats
        assert 'strategies' in stats
        assert 'meta_learner' in stats
    
    def test_reset(self):
        """Test reset"""
        mab = AdaptiveMAB()
        mab.register_strategy("s1")
        mab.update("s1", reward=1.0)
        
        mab.reset()
        
        assert len(mab.strategies) == 0
        assert mab.total_selections == 0
        assert mab.total_reward == 0.0


class TestAdaptationModes:
    """Tests for different adaptation modes"""
    
    @pytest.fixture
    def mab_with_strategies(self):
        """Create MAB with registered strategies"""
        mab = AdaptiveMAB(seed=42)
        mab.register_strategy("thompson")
        mab.register_strategy("epsilon")
        mab.register_strategy("ucb")
        return mab
    
    def test_static_mode(self, mab_with_strategies):
        """Test STATIC mode"""
        mab = mab_with_strategies
        mab.adaptation_mode = AdaptationMode.STATIC
        
        # Make thompson best
        mab.update("thompson", reward=1.0)
        mab.update("thompson", reward=1.0)
        mab.update("epsilon", reward=0.0)
        
        # Should always select thompson
        for _ in range(5):
            assert mab.select_strategy() == "thompson"
    
    def test_contextual_mode(self, mab_with_strategies):
        """Test CONTEXTUAL mode"""
        mab = mab_with_strategies
        mab.adaptation_mode = AdaptationMode.CONTEXTUAL
        
        ctx1 = ContextFeatures(operation_type="file", data_size=10)
        ctx2 = ContextFeatures(operation_type="code", data_size=10)
        
        # Train with different contexts
        mab.update("thompson", reward=1.0, context=ctx1)
        mab.update("epsilon", reward=1.0, context=ctx2)
        
        # Should select different strategies for different contexts
        # (This is probabilistic, so just verify it works)
        s1 = mab.select_strategy(ctx1)
        s2 = mab.select_strategy(ctx2)
        
        assert s1 in ["thompson", "epsilon", "ucb"]
        assert s2 in ["thompson", "epsilon", "ucb"]
    
    def test_reactive_mode(self, mab_with_strategies):
        """Test REACTIVE mode"""
        mab = mab_with_strategies
        mab.adaptation_mode = AdaptationMode.REACTIVE
        
        # Good performance - should exploit
        mab.update("thompson", reward=1.0)
        mab.update("thompson", reward=1.0)
        
        selected = mab.select_strategy()
        assert selected == "thompson"
    
    def test_hybrid_mode(self, mab_with_strategies):
        """Test HYBRID mode"""
        mab = mab_with_strategies
        mab.adaptation_mode = AdaptationMode.HYBRID
        mab.current_epsilon = 0.5  # High epsilon for testing
        
        ctx = ContextFeatures(operation_type="file", data_size=10)
        
        selections = set()
        for _ in range(20):
            s = mab.select_strategy(ctx)
            selections.add(s)
            mab.update(s, reward=1.0, context=ctx)
        
        # Should explore different strategies
        assert len(selections) > 1


class TestEdgeCases:
    """Tests for edge cases"""
    
    def test_single_strategy(self):
        """Test with single strategy"""
        mab = AdaptiveMAB()
        mab.register_strategy("only-one")
        
        for _ in range(5):
            selected = mab.select_strategy()
            assert selected == "only-one"
    
    def test_empty_context(self):
        """Test with empty context"""
        mab = AdaptiveMAB()
        mab.register_strategy("s1")
        
        selected = mab.select_strategy(context=None)
        
        assert selected == "s1"
    
    def test_extreme_rewards(self):
        """Test with extreme reward values"""
        mab = AdaptiveMAB()
        mab.register_strategy("s1")
        
        mab.update("s1", reward=100.0)  # Very high
        mab.update("s1", reward=-100.0)  # Very low
        
        stats = mab.get_strategy_stats("s1")
        
        assert stats['total_reward'] == 0.0
    
    def test_rapid_context_changes(self):
        """Test rapid context changes"""
        mab = AdaptiveMAB(adaptation_mode=AdaptationMode.CONTEXTUAL)
        mab.register_strategy("s1")
        mab.register_strategy("s2")
        
        last_context_key = None
        for i in range(10):
            ctx = ContextFeatures(
                operation_type="file" if i % 2 == 0 else "code",
                data_size=i * 10
            )
            
            # Track context changes
            current_key = mab.meta_learner.get_context_key(ctx)
            if last_context_key and current_key != last_context_key:
                # Context changed
                pass
            last_context_key = current_key
            
            mab.update("s1" if i % 2 == 0 else "s2", reward=1.0, context=ctx)
        
        # Should handle rapid changes without error
        stats = mab.get_all_stats()
        # Context switches tracked in meta_learner
        assert stats['meta_learner']['context_mappings'] > 0
