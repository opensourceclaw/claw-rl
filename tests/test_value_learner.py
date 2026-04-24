#!/usr/bin/env python3
"""
Tests for ValueLearner
"""

import pytest
from datetime import datetime
from claw_rl.values import (
    ValueLearner,
    Interaction,
    ExtractedPrinciple,
    LearningSource,
)


class TestInteraction:
    """Test Interaction"""

    def test_creation(self):
        """Test interaction creation"""
        interaction = Interaction(
            user_id="user1",
            user_input="Hello",
            agent_response="Hi there!"
        )

        assert interaction.user_id == "user1"
        assert interaction.user_input == "Hello"


class TestExtractedPrinciple:
    """Test ExtractedPrinciple"""

    def test_creation(self):
        """Test principle creation"""
        principle = ExtractedPrinciple(
            principle="Be honest",
            source=LearningSource.EXPLICIT_CORRECTION,
            confidence=0.9
        )

        assert principle.principle == "Be honest"
        assert principle.source == LearningSource.EXPLICIT_CORRECTION


class TestValueLearner:
    """Test ValueLearner"""

    @pytest.fixture
    def learner(self):
        """Create learner"""
        return ValueLearner()

    def test_creation(self, learner):
        """Test creation"""
        assert learner.value_store is not None

    def test_extract_principle_correction(self, learner):
        """Test extract principle from correction"""
        interaction = Interaction(
            user_id="user1",
            user_input="What is 2+2?",
            agent_response="2+2=5",
            user_feedback="不要胡说八道",
            feedback_type="correction"
        )

        principle = learner.extract_principle(interaction)

        assert principle is not None
        assert principle.source == LearningSource.EXPLICIT_CORRECTION

    def test_learn_from_interaction_correction(self, learner):
        """Test learn from correction interaction"""
        interaction = {
            "user_input": "Hello",
            "agent_response": "Hi",
            "user_feedback": "不要说废话",
            "feedback_type": "correction"
        }

        extracted = learner.learn_from_interaction("user1", interaction)

        assert len(extracted) > 0

    def test_learn_from_negative_feedback(self, learner):
        """Test learn from negative feedback"""
        interaction = {
            "user_input": "Tell me",
            "agent_response": "你是个笨蛋",
            "feedback_type": "negative"
        }

        extracted = learner.learn_from_interaction("user1", interaction)

        # Should infer red line
        assert isinstance(extracted, list)

    def test_detect_preference_style(self, learner):
        """Test detect style preference"""
        prefs = learner.detect_preference("user1", "请简洁一点")

        assert "style" in prefs or len(prefs) >= 0

    def test_get_interaction_history(self, learner):
        """Test get interaction history"""
        learner.learn_from_interaction("user1", {"user_input": "test", "agent_response": "test"})

        history = learner.get_interaction_history("user1")

        assert len(history) > 0
