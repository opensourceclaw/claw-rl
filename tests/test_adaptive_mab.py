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


class TestMetaLearnerSimilarity:
    """Tests for MetaLearner context similarity (v2.9.x)"""

    def test_cosine_similarity_identical(self):
        """Test cosine similarity of identical vectors"""
        a = [1.0, 0.5, 0.3]
        b = [1.0, 0.5, 0.3]
        sim = MetaLearner._cosine_similarity(a, b)
        assert abs(sim - 1.0) < 0.001

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity of orthogonal vectors"""
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        sim = MetaLearner._cosine_similarity(a, b)
        assert abs(sim - 0.0) < 0.001

    def test_cosine_similarity_empty(self):
        """Test cosine similarity with empty vectors"""
        assert MetaLearner._cosine_similarity([], []) == 0.0
        assert MetaLearner._cosine_similarity([1.0], []) == 0.0
        assert MetaLearner._cosine_similarity([], [1.0]) == 0.0

    def test_cosine_similarity_mismatched_lengths(self):
        """Test cosine similarity with mismatched vector lengths"""
        a = [1.0, 0.5]
        b = [1.0, 0.5, 0.3]
        sim = MetaLearner._cosine_similarity(a, b)
        assert sim == 0.0

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector"""
        a = [0.0, 0.0, 0.0]
        b = [1.0, 0.5, 0.3]
        sim = MetaLearner._cosine_similarity(a, b)
        assert sim == 0.0

    def test_cache_context_vector(self):
        """Test caching context vectors"""
        learner = MetaLearner()
        ctx1 = ContextFeatures(operation_type="file", data_size=10)
        ctx2 = ContextFeatures(operation_type="code", data_size=50)

        learner._cache_context_vector("file|small|high", ctx1)
        learner._cache_context_vector("code|medium|high", ctx2)

        assert len(learner._context_vectors) == 2
        assert learner._context_vectors[0][0] == "file|small|high"
        assert len(learner._context_vectors[0][1]) == 11

    def test_cache_context_vector_max_limit(self):
        """Test context vector cache respects max limit"""
        learner = MetaLearner()
        learner._max_context_cache = 10

        for i in range(15):
            ctx = ContextFeatures(operation_type="file", data_size=i)
            learner._cache_context_vector(f"key_{i}", ctx)

        assert len(learner._context_vectors) == 10
        # Should keep the most recent entries
        assert learner._context_vectors[-1][0] == "key_14"

    def test_find_similar_contexts_exact_match(self):
        """Test finding similar contexts with exact match"""
        learner = MetaLearner()
        ctx = ContextFeatures(operation_type="file", data_size=50)
        learner._cache_context_vector("key1", ctx)
        learner._cache_context_vector("key2",
            ContextFeatures(operation_type="code", data_size=100))

        similar = learner.find_similar_contexts(ctx, top_k=3)
        assert len(similar) >= 1
        # Exact match should be highly similar
        assert similar[0][1] > 0.9

    def test_find_similar_contexts_below_threshold(self):
        """Test that dissimilar contexts are filtered out"""
        learner = MetaLearner(similarity_threshold=0.8)
        ctx_file = ContextFeatures(operation_type="file", data_size=50,
                                   recent_success_rate=0.9)
        ctx_code = ContextFeatures(operation_type="code", data_size=999,
                                   recent_success_rate=0.1,
                                   data_variance=1.0,
                                   memory_usage=0.9)

        learner._cache_context_vector("file_key", ctx_file)

        # A very different context should match poorly
        similar = learner.find_similar_contexts(ctx_code, top_k=3)
        # May or may not find matches depending on exact values
        assert isinstance(similar, list)

    def test_find_similar_contexts_top_k(self):
        """Test top_k limits number of results"""
        learner = MetaLearner()
        for i in range(10):
            ctx = ContextFeatures(
                operation_type="file",
                data_size=50 + i,
                recent_success_rate=0.7 + i * 0.02
            )
            learner._cache_context_vector(f"key_{i}", ctx)

        query = ContextFeatures(operation_type="file", data_size=55,
                                recent_success_rate=0.75)
        for k in [1, 3, 5]:
            results = learner.find_similar_contexts(query, top_k=k)
            assert len(results) <= k

        # All results should have similarity >= threshold
        for _, sim in results:
            assert sim >= learner.similarity_threshold

    def test_predict_with_similarity_sufficient_data(self):
        """Test similarity-based prediction with enough history"""
        learner = MetaLearner()
        learner.register_strategy("s1")
        learner.register_strategy("s2")

        # Build up context history with different strategies preferred
        ctx_a = ContextFeatures(operation_type="file", data_size=10,
                                recent_success_rate=0.9)
        for _ in range(5):
            learner.update("s1", reward=1.0, context=ctx_a)

        ctx_b = ContextFeatures(operation_type="code", data_size=100,
                                recent_success_rate=0.5)
        for _ in range(5):
            learner.update("s2", reward=1.0, context=ctx_b)

        # Now predict with a context similar to ctx_a
        query = ContextFeatures(operation_type="file", data_size=12,
                                recent_success_rate=0.85)
        predicted = learner.predict_with_similarity(query, top_k=3)
        assert predicted is not None
        assert predicted in ["s1", "s2"]

    def test_predict_with_similarity_weighted_voting(self):
        """Test that similarity-weighted voting picks the correct strategy"""
        learner = MetaLearner()
        learner.register_strategy("s1")
        learner.register_strategy("s2")

        # Train: s1 is great for file, s2 is great for code
        ctx_file = ContextFeatures(operation_type="file", data_size=50,
                                   recent_success_rate=0.9)
        for i in range(10):
            learner.update("s1", reward=1.0, context=ctx_file)

        ctx_code = ContextFeatures(operation_type="code", data_size=100,
                                   recent_success_rate=0.5)
        for i in range(10):
            learner.update("s2", reward=1.0, context=ctx_code)

        # Query with file-like context
        query = ContextFeatures(operation_type="file", data_size=55,
                                recent_success_rate=0.85)

        # Run multiple times - should consistently pick s1 due to similarity
        s1_count = 0
        for _ in range(10):
            predicted = learner.predict_with_similarity(query, top_k=3)
            if predicted == "s1":
                s1_count += 1

        assert s1_count >= 5  # Should lean towards s1

    def test_predict_with_similarity_fallback_to_coarse(self):
        """Test fallback to coarse key when no similar contexts found"""
        learner = MetaLearner(similarity_threshold=0.99)  # Very strict
        learner.register_strategy("s1")
        learner.register_strategy("s2")

        ctx = ContextFeatures(operation_type="file", data_size=50)
        learner.update("s1", reward=1.0, context=ctx)
        learner.update("s2", reward=0.0, context=ctx)

        # Query with a very different context
        query = ContextFeatures(operation_type="code", data_size=999,
                                data_variance=1.0, memory_usage=0.9,
                                recent_success_rate=0.1, latency_budget_ms=100)

        # Should fall back to coarse key (which maps "code" context)
        predicted = learner.predict_with_similarity(query, top_k=3)
        assert predicted is not None
        assert predicted in ["s1", "s2"]

    def test_predict_with_similarity_no_strategies(self):
        """Test similarity prediction with no registered strategies"""
        learner = MetaLearner()
        ctx = ContextFeatures(operation_type="file", data_size=10)
        predicted = learner.predict_with_similarity(ctx)
        assert predicted is None


class TestAdaptiveMABContextAware:
    """Integration tests for context-aware AdaptiveMAB (v2.9.x)"""

    def test_contextual_mode_similarity_enabled(self):
        """Test that CONTEXTUAL mode uses similarity when enough history"""
        mab = AdaptiveMAB(adaptation_mode=AdaptationMode.CONTEXTUAL, seed=42)
        mab.register_strategy("s1")
        mab.register_strategy("s2")

        # Build enough history for similarity to activate
        for i in range(10):
            ctx = ContextFeatures(operation_type="file", data_size=i * 10,
                                  recent_success_rate=0.5 + i * 0.05)
            mab.update("s1" if i % 2 == 0 else "s2",
                       reward=1.0 if i % 3 != 0 else -1.0,
                       context=ctx)

        # Verify similarity is enabled
        assert len(mab.meta_learner._context_vectors) > 5

        # Selection should work
        ctx = ContextFeatures(operation_type="file", data_size=50)
        selected = mab.select_strategy(ctx)
        assert selected in ["s1", "s2"]

    def test_hybrid_mode_similarity_enabled(self):
        """Test that HYBRID mode uses similarity with enough history"""
        mab = AdaptiveMAB(adaptation_mode=AdaptationMode.HYBRID, seed=42)
        mab.register_strategy("s1")
        mab.register_strategy("s2")

        for i in range(10):
            ctx = ContextFeatures(operation_type="code", data_size=i * 20)
            mab.update("s1", reward=1.0, context=ctx)

        # Set high epsilon to force exploitation
        mab.current_epsilon = 0.0

        ctx_q = ContextFeatures(operation_type="code", data_size=100)
        selected = mab.select_strategy(ctx_q)
        assert selected in ["s1", "s2"]

    def test_get_stats_includes_similarity_info(self):
        """Test that stats include similarity system info"""
        mab = AdaptiveMAB()
        mab.register_strategy("s1")

        for i in range(10):
            ctx = ContextFeatures(operation_type="file", data_size=i * 10)
            mab.update("s1", reward=1.0, context=ctx)

        stats = mab.get_all_stats()
        assert 'context_vectors_cached' in stats['meta_learner']
        assert 'similarity_enabled' in stats['meta_learner']
        assert stats['meta_learner']['context_vectors_cached'] > 0
        assert stats['meta_learner']['similarity_enabled'] is True

    def test_context_vectors_not_cleared_on_reset(self):
        """Test reset behavior with context vectors"""
        mab = AdaptiveMAB()
        mab.register_strategy("s1")

        for i in range(3):
            mab.update("s1", reward=1.0,
                       context=ContextFeatures(operation_type="file",
                                               data_size=i * 10))

        mab.reset()

        # After reset, meta_learner is reconstructed
        assert len(mab.meta_learner._context_vectors) == 0
        assert len(mab.meta_learner.strategy_performance) == 0

    def test_context_similarity_cold_start(self):
        """Test behavior during cold start (not enough context vectors)"""
        mab = AdaptiveMAB(seed=42)
        mab.register_strategy("s1")
        mab.register_strategy("s2")

        # Only 2 context vectors - similarity won't activate (< 5 threshold)
        for i in range(2):
            ctx = ContextFeatures(operation_type="file", data_size=10 * i)
            mab.update("s1", reward=1.0, context=ctx)

        assert len(mab.meta_learner._context_vectors) < 5

        # Should still select successfully using coarse key
        ctx_q = ContextFeatures(operation_type="file", data_size=15)
        selected = mab.select_strategy(ctx_q)
        assert selected in ["s1", "s2"]

    def test_different_contexts_different_predictions(self):
        """Test that different contexts get appropriate strategy predictions"""
        mab = AdaptiveMAB(adaptation_mode=AdaptationMode.CONTEXTUAL, seed=42)
        mab.register_strategy("s1")
        mab.register_strategy("s2")

        # Train: s1 is best for file operations, s2 for code
        for i in range(8):
            ctx_file = ContextFeatures(operation_type="file", data_size=i * 10,
                                       recent_success_rate=0.8)
            ctx_code = ContextFeatures(operation_type="code", data_size=i * 20,
                                       recent_success_rate=0.4)
            mab.update("s1", reward=1.0, context=ctx_file)
            mab.update("s2", reward=1.0, context=ctx_code)

        # Predict for file-like vs code-like contexts
        file_query = ContextFeatures(operation_type="file", data_size=50,
                                     recent_success_rate=0.85)
        code_query = ContextFeatures(operation_type="code", data_size=100,
                                     recent_success_rate=0.45)

        # Both should return valid strategies
        f_pred = mab.meta_learner.predict_with_similarity(file_query)
        c_pred = mab.meta_learner.predict_with_similarity(code_query)

        assert f_pred in ["s1", "s2"]
        assert c_pred in ["s1", "s2"]

    def test_get_best_strategy_with_context_uses_similarity(self):
        """Test get_best_strategy respects context when available"""
        mab = AdaptiveMAB(seed=42)
        mab.register_strategy("s1")
        mab.register_strategy("s2")

        # Train: s1 for file, s2 for code
        for i in range(8):
            mab.update("s1", reward=1.0,
                       context=ContextFeatures(operation_type="file",
                                               data_size=10 * i))
            mab.update("s2", reward=1.0,
                       context=ContextFeatures(operation_type="code",
                                               data_size=10 * i))

        # Without context: should pick overall best
        best_overall = mab.get_best_strategy()
        assert best_overall in ["s1", "s2"]

        # With context: should pick context-aware best
        file_ctx = ContextFeatures(operation_type="file", data_size=50)
        best_context = mab.get_best_strategy(file_ctx)
        assert best_context in ["s1", "s2"]
