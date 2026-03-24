"""
Tests for Binary RL Judge

Run with: pytest tests/test_binary_rl.py -v
"""

import pytest
from claw_rl.binary_rl import BinaryRLJudge, RewardResult


class TestBinaryRLJudge:
    """Test suite for BinaryRLJudge."""
    
    @pytest.fixture
    def judge(self):
        """Create a BinaryRLJudge instance for testing."""
        return BinaryRLJudge()
    
    # Positive feedback tests
    def test_positive_gratitude(self, judge):
        """Test positive feedback with gratitude."""
        reward, confidence = judge.judge("谢谢")
        assert reward == 1
        assert confidence >= 0.9
    
    def test_positive_approval(self, judge):
        """Test positive feedback with approval."""
        reward, confidence = judge.judge("很好")
        assert reward == 1
        assert confidence >= 0.9
    
    def test_positive_continuation(self, judge):
        """Test positive feedback with continuation."""
        reward, confidence = judge.judge("继续")
        assert reward == 1
    
    def test_positive_emoji(self, judge):
        """Test positive feedback with emoji."""
        reward, confidence = judge.judge("👍")
        assert reward == 1
    
    # Negative feedback tests
    def test_negative_incorrect(self, judge):
        """Test negative feedback indicating incorrect."""
        reward, confidence = judge.judge("不对")
        assert reward == -1
        assert confidence >= 0.9
    
    def test_negative_correction(self, judge):
        """Test negative feedback with correction."""
        reward, confidence = judge.judge("应该放到这里")
        assert reward == -1
        assert confidence >= 0.9
    
    def test_negative_rejection(self, judge):
        """Test negative feedback with rejection."""
        reward, confidence = judge.judge("不要这样")
        assert reward == -1
    
    # Neutral feedback tests
    def test_neutral_acknowledgment(self, judge):
        """Test neutral feedback."""
        reward, confidence = judge.judge("嗯")
        assert reward == 0
        assert confidence == 0.5
    
    def test_neutral_empty(self, judge):
        """Test empty feedback."""
        reward, confidence = judge.judge("")
        assert reward == 0
        assert confidence == 0.0
    
    def test_neutral_whitespace(self, judge):
        """Test whitespace-only feedback."""
        reward, confidence = judge.judge("   ")
        assert reward == 0
        assert confidence == 0.0
    
    # Detailed result tests
    def test_judge_with_reason_positive(self, judge):
        """Test judge_with_reason for positive feedback."""
        result = judge.judge_with_reason("谢谢，很好！")
        assert isinstance(result, RewardResult)
        assert result.reward == 1
        assert result.pattern_matched is not None
    
    def test_judge_with_reason_negative(self, judge):
        """Test judge_with_reason for negative feedback."""
        result = judge.judge_with_reason("应该这样")
        assert isinstance(result, RewardResult)
        assert result.reward == -1
        assert result.pattern_matched == '应该'
    
    def test_judge_with_reason_neutral(self, judge):
        """Test judge_with_reason for neutral feedback."""
        result = judge.judge_with_reason("嗯")
        assert isinstance(result, RewardResult)
        assert result.reward == 0
        assert result.pattern_matched is None
    
    # Statistics test
    def test_get_statistics(self, judge):
        """Test getting statistics."""
        stats = judge.get_statistics()
        assert 'positive_patterns' in stats
        assert 'negative_patterns' in stats
        assert 'total_patterns' in stats
        assert stats['total_patterns'] == stats['positive_patterns'] + stats['negative_patterns']
        assert stats['positive_patterns'] >= 20  # We defined 20+ patterns
        assert stats['negative_patterns'] >= 20
    
    # Edge cases
    def test_mixed_feedback_positive_dominant(self, judge):
        """Test mixed feedback where positive dominates."""
        reward, confidence = judge.judge("谢谢，但是有点问题")
        # Should match "谢谢" first
        assert reward == 1
    
    def test_mixed_feedback_negative_dominant(self, judge):
        """Test mixed feedback where negative dominates."""
        reward, confidence = judge.judge("很好，但是应该那样")
        # Should match "应该" 
        assert reward == -1
    
    def test_case_insensitive(self, judge):
        """Test that matching is case-insensitive."""
        reward1, _ = judge.judge("谢谢")
        reward2, _ = judge.judge("谢谢")  # Full-width characters
        assert reward1 == reward2
    
    def test_partial_match(self, judge):
        """Test partial pattern matching."""
        result = judge.judge_with_reason("太感谢了！")
        assert result.reward == 1
        assert result.pattern_matched and '感谢' in result.pattern_matched
    
    # Comprehensive test cases
    @pytest.mark.parametrize("feedback,expected_reward", [
        ("谢谢", 1),
        ("感谢", 1),
        ("很好", 1),
        ("太好了", 1),
        ("不错", 1),
        ("正确", 1),
        ("对了", 1),
        ("满意", 1),
        ("👍", 1),
        ("不对", -1),
        ("错了", -1),
        ("错误", -1),
        ("应该", -1),
        ("不要", -1),
        ("不满意", -1),
        ("嗯", 0),
        ("哦", 0),
        ("", 0),
    ])
    def test_comprehensive_patterns(self, judge, feedback, expected_reward):
        """Test comprehensive pattern coverage."""
        reward, _ = judge.judge(feedback)
        assert reward == expected_reward
