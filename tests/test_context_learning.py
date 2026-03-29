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
Tests for claw-rl Contextual Learning
"""

import pytest
import tempfile
import os
import json
from datetime import datetime

from claw_rl.context.context_learning import (
    DecisionContext,
    ContextualDecision,
    ContextLearner
)


class TestDecisionContext:
    """Tests for DecisionContext"""
    
    def test_create_default_context(self):
        """Test creating a default context"""
        context = DecisionContext()
        
        assert context.timestamp is not None
        assert context.time_of_day == ""
        assert context.day_of_week == ""
        assert context.emotion == ""
        assert context.situation == ""
        assert context.urgency == "normal"
        assert context.metadata == {}
    
    def test_create_context_with_values(self):
        """Test creating context with custom values"""
        context = DecisionContext(
            time_of_day="morning",
            day_of_week="Monday",
            emotion="happy",
            situation="work",
            urgency="high",
            metadata={"key": "value"}
        )
        
        assert context.time_of_day == "morning"
        assert context.day_of_week == "Monday"
        assert context.emotion == "happy"
        assert context.situation == "work"
        assert context.urgency == "high"
        assert context.metadata == {"key": "value"}
    
    def test_context_to_dict(self):
        """Test converting context to dict"""
        context = DecisionContext(
            time_of_day="afternoon",
            day_of_week="Friday",
            emotion="calm",
            situation="health"
        )
        
        result = context.to_dict()
        
        assert result["time_of_day"] == "afternoon"
        assert result["day_of_week"] == "Friday"
        assert result["emotion"] == "calm"
        assert result["situation"] == "health"
        assert result["urgency"] == "normal"
        assert "timestamp" in result
    
    def test_context_from_dict(self):
        """Test creating context from dict"""
        data = {
            "timestamp": "2026-03-29T10:00:00",
            "time_of_day": "evening",
            "day_of_week": "Sunday",
            "emotion": "anxious",
            "situation": "family",
            "urgency": "low",
            "metadata": {"test": 123}
        }
        
        context = DecisionContext.from_dict(data)
        
        assert context.timestamp == "2026-03-29T10:00:00"
        assert context.time_of_day == "evening"
        assert context.day_of_week == "Sunday"
        assert context.emotion == "anxious"
        assert context.situation == "family"
        assert context.urgency == "low"
        assert context.metadata == {"test": 123}


class TestContextualDecision:
    """Tests for ContextualDecision"""
    
    def test_create_decision(self):
        """Test creating a decision"""
        context = DecisionContext(emotion="happy", situation="work")
        decision = ContextualDecision(
            decision_id="test-001",
            context=context,
            decision_type="investment",
            options=["A", "B", "C"],
            chosen_option="B",
            outcome="success",
            satisfaction=0.9
        )
        
        assert decision.decision_id == "test-001"
        assert decision.decision_type == "investment"
        assert decision.options == ["A", "B", "C"]
        assert decision.chosen_option == "B"
        assert decision.outcome == "success"
        assert decision.satisfaction == 0.9
        assert decision.learned_pattern is None
    
    def test_decision_to_dict(self):
        """Test converting decision to dict"""
        context = DecisionContext(emotion="calm")
        decision = ContextualDecision(
            decision_id="test-002",
            context=context,
            decision_type="career",
            options=["stay", "move"],
            chosen_option="move",
            outcome="partial",
            satisfaction=0.6,
            learned_pattern="test pattern"
        )
        
        result = decision.to_dict()
        
        assert result["decision_id"] == "test-002"
        assert result["decision_type"] == "career"
        assert result["chosen_option"] == "move"
        assert result["outcome"] == "partial"
        assert result["satisfaction"] == 0.6
        assert result["learned_pattern"] == "test pattern"
        assert "context" in result


class TestContextLearner:
    """Tests for ContextLearner"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_init_empty(self, temp_data_dir):
        """Test initializing learner with empty data"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        assert learner.data_dir == temp_data_dir
        assert learner.decisions == []
        assert learner.patterns == {}
    
    def test_record_decision(self, temp_data_dir):
        """Test recording a decision"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        decision = learner.record_decision(
            decision_id="test-001",
            decision_type="investment",
            options=["stocks", "bonds", "cash"],
            chosen_option="stocks",
            outcome="success",
            satisfaction=0.85,
            context_data={"emotion": "confident", "situation": "work"}
        )
        
        assert len(learner.decisions) == 1
        assert decision.decision_id == "test-001"
        assert decision.decision_type == "investment"
        assert decision.chosen_option == "stocks"
        assert decision.context.emotion == "confident"
    
    def test_record_multiple_decisions(self, temp_data_dir):
        """Test recording multiple decisions"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        learner.record_decision(
            decision_id="test-001",
            decision_type="investment",
            options=["A", "B"],
            chosen_option="A",
            outcome="success",
            satisfaction=0.9,
            context_data={"emotion": "happy"}
        )
        
        learner.record_decision(
            decision_id="test-002",
            decision_type="career",
            options=["stay", "move"],
            chosen_option="move",
            outcome="partial",
            satisfaction=0.7,
            context_data={"emotion": "anxious"}
        )
        
        assert len(learner.decisions) == 2
        assert learner.decisions[0].decision_type == "investment"
        assert learner.decisions[1].decision_type == "career"
    
    def test_auto_detect_time_of_day(self, temp_data_dir):
        """Test auto-detection of time of day"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        # Test without explicit time_of_day
        decision = learner.record_decision(
            decision_id="test-auto-time",
            decision_type="test",
            options=["A"],
            chosen_option="A",
            outcome="success",
            satisfaction=0.8
        )
        
        # Should have auto-detected time_of_day
        assert decision.context.time_of_day in ["morning", "afternoon", "evening", "night"]
    
    def test_auto_detect_day_of_week(self, temp_data_dir):
        """Test auto-detection of day of week"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        decision = learner.record_decision(
            decision_id="test-auto-day",
            decision_type="test",
            options=["A"],
            chosen_option="A",
            outcome="success",
            satisfaction=0.8
        )
        
        # Should have auto-detected day_of_week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                "Friday", "Saturday", "Sunday"]
        assert decision.context.day_of_week in days
    
    def test_pattern_learning_high_satisfaction(self, temp_data_dir):
        """Test pattern learning with high satisfaction"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        decision = learner.record_decision(
            decision_id="test-pattern",
            decision_type="investment",
            options=["conservative", "aggressive"],
            chosen_option="aggressive",
            outcome="success",
            satisfaction=0.9,  # High satisfaction
            context_data={"emotion": "confident"}
        )
        
        # Should learn a pattern
        assert decision.learned_pattern is not None
        assert "confident" in decision.learned_pattern
        assert "aggressive" in decision.learned_pattern
    
    def test_pattern_learning_low_satisfaction(self, temp_data_dir):
        """Test pattern learning with low satisfaction"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        decision = learner.record_decision(
            decision_id="test-low-sat",
            decision_type="investment",
            options=["A", "B"],
            chosen_option="B",
            outcome="failure",
            satisfaction=0.3,  # Low satisfaction
            context_data={"emotion": "anxious"}
        )
        
        # Should not learn a pattern for low satisfaction
        assert decision.learned_pattern is None
    
    def test_get_patterns_for_context(self, temp_data_dir):
        """Test getting patterns for a context"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        # Record multiple decisions
        learner.record_decision(
            decision_id="test-001",
            decision_type="investment",
            options=["A", "B"],
            chosen_option="A",
            outcome="success",
            satisfaction=0.9,
            context_data={"emotion": "happy"}
        )
        
        learner.record_decision(
            decision_id="test-002",
            decision_type="investment",
            options=["C", "D"],
            chosen_option="C",
            outcome="success",
            satisfaction=0.85,
            context_data={"emotion": "happy"}
        )
        
        # Get patterns for happy emotion
        patterns = learner.get_patterns_for_context(emotion="happy")
        
        assert len(patterns) >= 2
    
    def test_get_decision_history(self, temp_data_dir):
        """Test getting decision history"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        # Record multiple decisions
        for i in range(5):
            learner.record_decision(
                decision_id=f"test-{i:03d}",
                decision_type="investment" if i % 2 == 0 else "career",
                options=["A", "B"],
                chosen_option="A",
                outcome="success",
                satisfaction=0.8
            )
        
        # Get all history
        history = learner.get_decision_history()
        assert len(history) == 5
        
        # Get filtered history
        investment_history = learner.get_decision_history(decision_type="investment")
        assert len(investment_history) == 3  # 0, 2, 4
        
        # Get limited history
        limited_history = learner.get_decision_history(limit=2)
        assert len(limited_history) == 2
    
    def test_get_statistics(self, temp_data_dir):
        """Test getting learning statistics"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        # Record decisions
        learner.record_decision(
            decision_id="test-001",
            decision_type="investment",
            options=["A", "B"],
            chosen_option="A",
            outcome="success",
            satisfaction=0.9,
            context_data={"emotion": "confident"}
        )
        
        learner.record_decision(
            decision_id="test-002",
            decision_type="career",
            options=["stay", "move"],
            chosen_option="move",
            outcome="partial",
            satisfaction=0.6,
            context_data={"emotion": "anxious"}
        )
        
        stats = learner.get_statistics()
        
        assert stats["total_decisions"] == 2
        assert "investment" in stats["by_decision_type"]
        assert "career" in stats["by_decision_type"]
        assert 0.7 <= stats["avg_satisfaction"] <= 0.8
        assert stats["total_patterns"] >= 1
    
    def test_persistence(self, temp_data_dir):
        """Test data persistence"""
        # Record decision with first learner
        learner1 = ContextLearner(data_dir=temp_data_dir)
        learner1.record_decision(
            decision_id="test-persist",
            decision_type="investment",
            options=["A", "B"],
            chosen_option="A",
            outcome="success",
            satisfaction=0.85,
            context_data={"emotion": "happy"}
        )
        
        # Create new learner - should load existing data
        learner2 = ContextLearner(data_dir=temp_data_dir)
        
        assert len(learner2.decisions) >= 1
        assert any(d.decision_id == "test-persist" for d in learner2.decisions)
    
    def test_context_with_metadata(self, temp_data_dir):
        """Test context with custom metadata"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        decision = learner.record_decision(
            decision_id="test-meta",
            decision_type="test",
            options=["A"],
            chosen_option="A",
            outcome="success",
            satisfaction=0.8,
            context_data={
                "emotion": "happy",
                "metadata": {
                    "source": "api",
                    "version": "1.0",
                    "tags": ["test", "demo"]
                }
            }
        )
        
        assert decision.context.metadata["source"] == "api"
        assert decision.context.metadata["version"] == "1.0"
        assert "test" in decision.context.metadata["tags"]
    
    def test_urgency_levels(self, temp_data_dir):
        """Test different urgency levels"""
        learner = ContextLearner(data_dir=temp_data_dir)
        
        # Test all urgency levels
        for urgency in ["low", "normal", "high"]:
            decision = learner.record_decision(
                decision_id=f"test-urgency-{urgency}",
                decision_type="test",
                options=["A"],
                chosen_option="A",
                outcome="success",
                satisfaction=0.8,
                context_data={"urgency": urgency}
            )
            assert decision.context.urgency == urgency
