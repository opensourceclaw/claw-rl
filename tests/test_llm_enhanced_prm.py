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
Tests for claw-rl LLM-Enhanced PRM Judge (v2.1.0)
"""

import pytest
import time

from claw_rl.feedback.llm_enhanced_prm import (
    LLMEnhancedPRMJudge,
    JudgeResult,
    LLMBackend,
    OpenAIClient,
    AnthropicClient,
    LocalLLMClient,
)


class TestJudgeResult:
    """Tests for JudgeResult dataclass"""
    
    def test_to_tuple(self):
        """Test conversion to tuple"""
        result = JudgeResult(
            reward=1,
            confidence=0.95,
            reason="User expressed gratitude",
            source="llm",
            backend="openai"
        )
        
        assert result.to_tuple() == (1, "User expressed gratitude")
    
    def test_defaults(self):
        """Test default values"""
        result = JudgeResult(
            reward=0,
            confidence=0.5,
            reason="Test",
            source="rule"
        )
        
        assert result.backend is None
        assert result.latency_ms == 0.0
        assert result.pattern_matched is None


class TestLLMEnhancedPRMJudge:
    """Tests for LLMEnhancedPRMJudge"""
    
    def test_init_default(self):
        """Test default initialization"""
        judge = LLMEnhancedPRMJudge()
        
        assert judge.config['cache_enabled'] is True
        assert judge.config['fallback_to_rules'] is True
        assert judge.config['confidence_threshold'] == 0.7
    
    def test_init_with_config(self):
        """Test initialization with custom config"""
        judge = LLMEnhancedPRMJudge(config={
            'cache_enabled': False,
            'confidence_threshold': 0.8,
        })
        
        assert judge.config['cache_enabled'] is False
        assert judge.config['confidence_threshold'] == 0.8
    
    def test_judge_positive_gratitude(self):
        """Test judging positive gratitude"""
        judge = LLMEnhancedPRMJudge()
        
        result = judge.judge("Created file", "谢谢！")
        
        assert result.reward == 1
        assert result.confidence >= 0.9
        assert "gratitude" in result.reason.lower()
    
    def test_judge_positive_approval(self):
        """Test judging positive approval"""
        judge = LLMEnhancedPRMJudge()
        
        result = judge.judge("Edited file", "很好！")
        
        assert result.reward == 1
        assert result.confidence >= 0.9
        assert "approval" in result.reason.lower()
    
    def test_judge_negative_correction(self):
        """Test judging negative correction"""
        judge = LLMEnhancedPRMJudge()
        
        result = judge.judge("Created file", "不对，应该放这里")
        
        assert result.reward == -1
        assert result.confidence >= 0.9
        assert "error" in result.reason.lower() or "correction" in result.reason.lower()
    
    def test_judge_negative_should(self):
        """Test judging negative with 'should'"""
        judge = LLMEnhancedPRMJudge()
        
        result = judge.judge("Edited config", "应该先检查文件")
        
        assert result.reward == -1
        assert "correction" in result.reason.lower()
    
    def test_judge_neutral(self):
        """Test judging neutral response"""
        judge = LLMEnhancedPRMJudge()
        
        result = judge.judge("Some action", "这是一段普通的回复")
        
        assert result.reward == 0
        assert "no clear" in result.reason.lower()
    
    def test_judge_with_cache(self):
        """Test caching works"""
        judge = LLMEnhancedPRMJudge()
        
        # First call
        result1 = judge.judge("action", "谢谢")
        
        # Second call (should hit cache)
        result2 = judge.judge("action", "谢谢")
        
        assert result1.reward == result2.reward
        assert result1.reason == result2.reason
        
        # Check metrics
        metrics = judge.get_metrics()
        assert metrics['cache_hits'] >= 1
    
    def test_cache_disabled(self):
        """Test with cache disabled"""
        judge = LLMEnhancedPRMJudge(config={'cache_enabled': False})
        
        result1 = judge.judge("action", "谢谢")
        result2 = judge.judge("action", "谢谢")
        
        # Should still work, just no caching
        assert result1.reward == result2.reward
    
    def test_cache_clear(self):
        """Test cache clear"""
        judge = LLMEnhancedPRMJudge()
        
        judge.judge("action", "谢谢")
        assert len(judge._cache) > 0
        
        judge.clear_cache()
        assert len(judge._cache) == 0
    
    def test_cache_ttl(self):
        """Test cache TTL expiration"""
        judge = LLMEnhancedPRMJudge(config={'cache_ttl': 0.1})  # 0.1 second
        
        result1 = judge.judge("action", "谢谢")
        
        # Wait for TTL
        time.sleep(0.15)
        
        # Should not hit cache
        result2 = judge.judge("action", "谢谢")
        
        metrics = judge.get_metrics()
        # Cache should have been expired
        assert metrics['cache_hits'] == 0
    
    def test_cache_size_limit(self):
        """Test cache size limit"""
        judge = LLMEnhancedPRMJudge(config={'cache_size': 3})
        
        # Add more than cache size
        for i in range(5):
            judge.judge(f"action{i}", f"谢谢{i}")
        
        # Cache should be limited
        assert len(judge._cache) <= 3
    
    def test_no_fallback(self):
        """Test no fallback when disabled"""
        judge = LLMEnhancedPRMJudge(config={
            'fallback_to_rules': False,
            'cache_enabled': False
        })
        
        # With use_llm=False, high-confidence rule still works
        # (rule-based quick check happens before LLM)
        result = judge.judge("action", "谢谢", use_llm=False)
        
        # High confidence rule match should still work
        assert result.reward == 1
        assert result.source == 'rule'
        
        # Test with a neutral response (no high-confidence rule match)
        result2 = judge.judge("action", "这是一段普通的回复", use_llm=False)
        assert result2.reward == 0
        assert "Unable to determine" in result2.reason
    
    def test_metrics(self):
        """Test metrics collection"""
        judge = LLMEnhancedPRMJudge()
        
        # Make some calls
        judge.judge("action1", "谢谢")
        judge.judge("action2", "不对")
        judge.judge("action1", "谢谢")  # Cache hit
        
        metrics = judge.get_metrics()
        
        assert metrics['total_calls'] == 3
        assert metrics['cache_hits'] >= 1
        assert 'cache_hit_rate' in metrics
        assert 'available_backends' in metrics
    
    def test_get_available_backends(self):
        """Test getting available backends"""
        judge = LLMEnhancedPRMJudge()
        
        backends = judge.get_available_backends()
        
        # Should return a list (may be empty if no LLM available)
        assert isinstance(backends, list)
    
    def test_backward_compatibility(self):
        """Test backward compatibility with tuple return"""
        judge = LLMEnhancedPRMJudge()
        
        reward, reason = judge.judge_tuple("action", "谢谢")
        
        assert reward == 1
        assert isinstance(reason, str)
    
    def test_context_parameter(self):
        """Test context parameter (for future use)"""
        judge = LLMEnhancedPRMJudge()
        
        result = judge.judge(
            "action",
            "谢谢",
            context={'user': 'test', 'session': '123'}
        )
        
        assert result.reward == 1
    
    def test_high_confidence_rule_skip_llm(self):
        """Test that high confidence rule matches skip LLM"""
        judge = LLMEnhancedPRMJudge()
        
        # Very clear positive signal
        result = judge.judge("action", "谢谢，非常好！")
        
        # Should use rule-based (source='rule') due to high confidence
        assert result.source == 'rule'
        assert result.confidence >= 0.9


class TestLLMClients:
    """Tests for LLM client implementations"""
    
    def test_openai_client_unavailable(self):
        """Test OpenAI client when not available"""
        client = OpenAIClient()
        # Will be unavailable if no API key
        # Just test it doesn't crash
        assert client.model == "gpt-4o-mini"
    
    def test_anthropic_client_unavailable(self):
        """Test Anthropic client when not available"""
        client = AnthropicClient()
        # Will be unavailable if no API key
        assert client.model == "claude-3-haiku-20240307"
    
    def test_local_client_unavailable(self):
        """Test local LLM client when not available"""
        client = LocalLLMClient()
        # Will be unavailable if Ollama not running
        assert client.endpoint == "http://localhost:11434"


class TestParseLLMResponse:
    """Tests for LLM response parsing"""
    
    def test_parse_valid_json(self):
        """Test parsing valid JSON response"""
        judge = LLMEnhancedPRMJudge()
        
        response = '{"score": 1, "confidence": 0.95, "reason": "User satisfied"}'
        result = judge._parse_llm_response(response)
        
        assert result is not None
        assert result['score'] == 1
        assert result['confidence'] == 0.95
        assert result['reason'] == "User satisfied"
    
    def test_parse_json_with_extra_text(self):
        """Test parsing JSON with extra text"""
        judge = LLMEnhancedPRMJudge()
        
        response = '''Here is my evaluation:
        {"score": -1, "confidence": 0.9, "reason": "User corrected"}
        That's my assessment.'''
        
        result = judge._parse_llm_response(response)
        
        assert result is not None
        assert result['score'] == -1
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON"""
        judge = LLMEnhancedPRMJudge()
        
        result = judge._parse_llm_response("not json")
        assert result is None
    
    def test_parse_invalid_score(self):
        """Test parsing with invalid score"""
        judge = LLMEnhancedPRMJudge()
        
        response = '{"score": 5, "confidence": 0.9, "reason": "test"}'
        result = judge._parse_llm_response(response)
        
        assert result is None
    
    def test_parse_confidence_clamping(self):
        """Test confidence value clamping"""
        judge = LLMEnhancedPRMJudge()
        
        # Over 1.0
        response = '{"score": 1, "confidence": 1.5, "reason": "test"}'
        result = judge._parse_llm_response(response)
        assert result['confidence'] == 1.0
        
        # Under 0.0
        response = '{"score": 1, "confidence": -0.5, "reason": "test"}'
        result = judge._parse_llm_response(response)
        assert result['confidence'] == 0.0


class TestEdgeCases:
    """Tests for edge cases"""
    
    def test_empty_response(self):
        """Test empty response"""
        judge = LLMEnhancedPRMJudge()
        
        result = judge.judge("action", "")
        
        assert result.reward == 0
    
    def test_whitespace_response(self):
        """Test whitespace-only response"""
        judge = LLMEnhancedPRMJudge()
        
        result = judge.judge("action", "   ")
        
        assert result.reward == 0
    
    def test_very_long_response(self):
        """Test very long response"""
        judge = LLMEnhancedPRMJudge()
        
        long_response = "这是一段很长的回复，" * 100 + "谢谢"
        result = judge.judge("action", long_response)
        
        # Should still detect "谢谢"
        assert result.reward == 1
    
    def test_special_characters(self):
        """Test response with special characters"""
        judge = LLMEnhancedPRMJudge()
        
        result = judge.judge("action", "谢谢！👍✅")
        
        assert result.reward == 1
    
    def test_mixed_signals(self):
        """Test response with mixed signals"""
        judge = LLMEnhancedPRMJudge()
        
        # "不对" appears first, should be negative
        result = judge.judge("action", "不对，应该这样，谢谢")
        
        assert result.reward == -1
