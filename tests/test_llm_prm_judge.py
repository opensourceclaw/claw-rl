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
Tests for claw-rl LLM-based PRM Judge
"""

import pytest

from claw_rl.llm_prm_judge import LLMPRMJudge


class TestLLMPRMJudge:
    """Tests for LLMPRMJudge"""
    
    def test_init(self):
        """Test initialization"""
        judge = LLMPRMJudge()
        
        assert judge.cache_enabled is True
        assert judge.fallback_to_rules is True
    
    def test_init_with_options(self):
        """Test initialization with options"""
        judge = LLMPRMJudge(
            cache_enabled=False,
            fallback_to_rules=False
        )
        
        assert judge.cache_enabled is False
        assert judge.fallback_to_rules is False
    
    def test_judge_with_cache_hit(self):
        """Test cache hit returns cached result"""
        judge = LLMPRMJudge()
        
        # First call (will fall back to rules)
        result1 = judge.judge("action", "谢谢")
        
        # Second call (should hit cache)
        result2 = judge.judge("action", "谢谢")
        
        assert result1 == result2
        assert result1[0] == 1  # Positive reward
    
    def test_judge_fallback_to_rules_positive(self):
        """Test fallback to rule-based judge for positive"""
        judge = LLMPRMJudge()
        
        result = judge.judge("action", "谢谢,很好", use_llm=False)
        assert result[0] == 1  # reward
    
    def test_judge_fallback_to_rules_negative(self):
        """Test fallback to rule-based judge for negative"""
        judge = LLMPRMJudge()
        
        result = judge.judge("action", "不对,应该这样", use_llm=False)
        assert result[0] == -1  # reward
    
    def test_judge_fallback_to_rules_neutral(self):
        """Test fallback to rule-based judge for neutral"""
        judge = LLMPRMJudge()
        
        result = judge.judge("action", "这是一段普通回复", use_llm=False)
        assert result[0] == 0  # reward
    
    def test_judge_positive_gratitude(self):
        """Test judging positive gratitude"""
        judge = LLMPRMJudge()
        
        reward, reason = judge.judge("Created file", "谢谢!", use_llm=False)
        
        assert reward == 1
        assert "gratitude" in reason.lower()
    
    def test_judge_positive_approval(self):
        """Test judging positive approval"""
        judge = LLMPRMJudge()
        
        reward, reason = judge.judge("Edited file", "很好!", use_llm=False)
        
        assert reward == 1
        assert "approval" in reason.lower()
    
    def test_judge_negative_correction(self):
        """Test judging negative correction"""
        judge = LLMPRMJudge()
        
        reward, reason = judge.judge("Created file", "不对,应该放这里", use_llm=False)
        
        assert reward == -1
        assert "error" in reason.lower() or "correction" in reason.lower()
    
    def test_judge_negative_should(self):
        """Test judging negative with should"""
        judge = LLMPRMJudge()
        
        reward, reason = judge.judge("Edited config", "应该先检查文件", use_llm=False)
        
        assert reward == -1
        assert "correction" in reason.lower()
    
    def test_judge_neutral(self):
        """Test judging neutral response"""
        judge = LLMPRMJudge()
        
        reward, reason = judge.judge("Some action", "这是一段普通的回复", use_llm=False)
        
        assert reward == 0
        assert "no clear" in reason.lower() or "neutral" in reason.lower()
    
    def test_cache_clear(self):
        """Test cache clear"""
        judge = LLMPRMJudge()
        
        # Make some calls
        judge.judge("action1", "谢谢", use_llm=False)
        judge.judge("action2", "不好", use_llm=False)
        
        # Check cache has entries
        assert len(judge._cache) > 0
        
        # Clear cache
        judge.clear_cache()
        
        assert len(judge._cache) == 0
    
    def test_cache_stats(self):
        """Test cache statistics"""
        judge = LLMPRMJudge(cache_size=100)
        
        stats = judge.get_cache_stats()
        
        assert stats['cache_enabled'] is True
        assert stats['max_cache_size'] == 100
        assert stats['cache_size'] == 0
    
    def test_cache_size_limit(self):
        """Test cache size limit"""
        judge = LLMPRMJudge(cache_size=5)
        
        # Add more than cache size
        for i in range(10):
            judge.judge(f"action{i}", f"response{i}", use_llm=False)
        
        # Cache should be limited
        assert len(judge._cache) <= 5
    
    def test_parse_llm_response_positive(self):
        """Test parsing LLM positive response"""
        judge = LLMPRMJudge()
        
        result = judge._parse_llm_response("+1 | User expressed satisfaction")
        
        assert result is not None
        assert result[0] == 1
        assert result[1] == "User expressed satisfaction"
    
    def test_parse_llm_response_negative(self):
        """Test parsing LLM negative response"""
        judge = LLMPRMJudge()
        
        result = judge._parse_llm_response("-1 | User indicated error")
        
        assert result is not None
        assert result[0] == -1
        assert result[1] == "User indicated error"
    
    def test_parse_llm_response_neutral(self):
        """Test parsing LLM neutral response"""
        judge = LLMPRMJudge()
        
        result = judge._parse_llm_response("0 | No clear signal")
        
        assert result is not None
        assert result[0] == 0
        assert result[1] == "No clear signal"
    
    def test_parse_llm_response_invalid(self):
        """Test parsing invalid LLM response"""
        judge = LLMPRMJudge()
        
        # Missing separator
        result = judge._parse_llm_response("1 User satisfied")
        assert result is None
        
        # Invalid score
        result = judge._parse_llm_response("invalid | Some reason")
        assert result is None
    
    def test_no_fallback(self):
        """Test no fallback when disabled"""
        judge = LLMPRMJudge(fallback_to_rules=False, cache_enabled=False)
        
        # Should return neutral when LLM fails and no fallback
        reward, reason = judge.judge("action", "谢谢", use_llm=False)
        
        assert reward == 0
        assert "Unable to determine" in reason
    
    def test_get_cache_key(self):
        """Test cache key generation"""
        judge = LLMPRMJudge()
        
        key1 = judge._get_cache_key("action1", "response1")
        key2 = judge._get_cache_key("action1", "response1")
        key3 = judge._get_cache_key("action2", "response2")
        
        # Same input should produce same key
        assert key1 == key2
        
        # Different input should produce different key
        assert key1 != key3
        
        # Key should be MD5 hash (32 chars hex)
        assert len(key1) == 32
