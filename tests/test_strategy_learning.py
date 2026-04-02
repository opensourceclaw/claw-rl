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
Tests for claw-rl Conflict Resolution Strategy Learning
"""

import pytest
import tempfile
import shutil
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from claw_rl.learning.strategy import StrategyLearner, StrategyRecord


class TestStrategyLearner:
    """Test Strategy Learner"""
    
    @pytest.fixture
    def temp_learner(self):
        """Create temporary learner"""
        temp_dir = tempfile.mkdtemp()
        learner = StrategyLearner(data_dir=temp_dir)
        yield learner
        shutil.rmtree(temp_dir)
    
    def test_initialization(self, temp_learner):
        """Test initialization"""
        assert len(temp_learner.strategies) == 5  # 5 conflict types
        assert "value_based" in temp_learner.strategies
    
    def test_record_strategy(self, temp_learner):
        """Test recording strategy"""
        record = StrategyRecord(
            id="test_001",
            conflict_type="value_based",
            strategy_used="priority_based",
            success=True,
            satisfaction=0.9
        )
        temp_learner.record_strategy(record)
        
        # Check effectiveness was updated
        eff = temp_learner.strategies["value_based"]["priority_based"]
        assert eff.total_uses == 1
        assert eff.successful_uses == 1
    
    def test_strategy_ranking(self, temp_learner):
        """Test strategy ranking"""
        # Record some successful uses
        for i in range(10):
            record = StrategyRecord(
                id=f"test_{i}",
                conflict_type="value_based",
                strategy_used="priority_based",
                success=True,
                satisfaction=0.85
            )
            temp_learner.record_strategy(record)
        
        ranking = temp_learner.get_strategy_ranking("value_based")
        assert isinstance(ranking, list)
        assert len(ranking) > 0
        # Check priority_based is ranked high
        top_strategy = ranking[0][0]
        assert top_strategy == "priority_based"
    
    def test_recommended_strategy(self, temp_learner):
        """Test recommended strategy"""
        # Record enough successful uses
        for i in range(10):
            record = StrategyRecord(
                id=f"test_{i}",
                conflict_type="value_based",
                strategy_used="priority_based",
                success=True,
                satisfaction=0.9
            )
            temp_learner.record_strategy(record)
        
        recommended = temp_learner.get_recommended_strategy("value_based")
        assert recommended == "priority_based"
    
    def test_effectiveness_calculation(self, temp_learner):
        """Test effectiveness calculation"""
        record = StrategyRecord(
            id="test_001",
            conflict_type="value_based",
            strategy_used="compromise",
            success=True,
            satisfaction=0.7
        )
        temp_learner.record_strategy(record)
        
        eff = temp_learner.strategies["value_based"]["compromise"]
        assert 0.0 <= eff.effectiveness_score <= 1.0
    
    def test_learning_statistics(self, temp_learner):
        """Test learning statistics"""
        stats = temp_learner.get_learning_statistics()
        assert "total_conflict_types" in stats
        assert "total_strategies" in stats
        assert "recommended_strategies" in stats
        assert "avg_effectiveness" in stats
        assert "total_records" in stats
