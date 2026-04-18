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
claw-rl LLM-Enhanced PRM Judge (v2.1.0)

Enhanced LLM-based Process Reward Model Judge with:
- Multi-LLM backend support (OpenAI, Claude, Local)
- Confidence-aware fallback
- Optimized caching
- Structured output parsing
"""

from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import json
import hashlib
import time
import os
from abc import ABC, abstractmethod


class LLMBackend(Enum):
    """Supported LLM backends"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AUTO = "auto"  # Auto-detect available


@dataclass
class JudgeResult:
    """Enhanced judge result with full context"""
    reward: int  # -1, 0, or +1
    confidence: float  # 0.0 to 1.0
    reason: str
    source: str  # 'llm', 'rule', 'cache'
    backend: Optional[str] = None  # Which LLM backend was used
    latency_ms: float = 0.0
    pattern_matched: Optional[str] = None
    
    def to_tuple(self) -> Tuple[int, str]:
        """Convert to simple tuple for backward compatibility"""
        return (self.reward, self.reason)


class LLMClient(ABC):
    """Abstract LLM client interface"""
    
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available"""
        pass


class OpenAIClient(LLMClient):
    """OpenAI client implementation"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI()
            except ImportError as e:
                logger.warning(f"OpenAI package not installed: {e}. Install with: pip install openai")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                return None
        return self._client
    
    def is_available(self) -> bool:
        return self._get_client() is not None
    
    async def complete(self, prompt: str, **kwargs) -> str:
        client = self._get_client()
        if not client:
            raise RuntimeError("OpenAI client not available")
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 100),
            temperature=kwargs.get("temperature", 0),
        )
        return response.choices[0].message.content.strip()


class AnthropicClient(LLMClient):
    """Anthropic Claude client implementation"""
    
    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.model = model
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic()
            except ImportError as e:
                logger.warning(f"Anthropic package not installed: {e}. Install with: pip install anthropic")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                return None
        return self._client
    
    def is_available(self) -> bool:
        return self._get_client() is not None
    
    async def complete(self, prompt: str, **kwargs) -> str:
        client = self._get_client()
        if not client:
            raise RuntimeError("Anthropic client not available")
        
        response = client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 100),
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()


class LocalLLMClient(LLMClient):
    """Local LLM client (Ollama, etc.)"""
    
    def __init__(self, endpoint: str = "http://localhost:11434"):
        self.endpoint = endpoint
    
    def is_available(self) -> bool:
        try:
            import requests
            response = requests.get(f"{self.endpoint}/api/tags", timeout=1)
            return response.status_code == 200
        except:
            return False
    
    async def complete(self, prompt: str, **kwargs) -> str:
        import requests
        
        response = requests.post(
            f"{self.endpoint}/api/generate",
            json={
                "model": kwargs.get("model", "llama3.2"),
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": kwargs.get("max_tokens", 100),
                    "temperature": kwargs.get("temperature", 0),
                }
            },
            timeout=30
        )
        return response.json().get("response", "").strip()


class LLMEnhancedPRMJudge:
    """
    LLM-Enhanced PRM Judge (v2.1.0)
    
    Features:
    - Multi-LLM backend support
    - Confidence-aware fallback to rules
    - Intelligent caching
    - Structured output parsing
    - Performance metrics
    
    Usage:
        judge = LLMEnhancedPRMJudge()
        
        result = judge.judge(
            action="Created file /workspace/test.md",
            response="谢谢，很好！"
        )
        # result.reward = 1, result.confidence = 0.95
    """
    
    # Enhanced prompt template with English examples for broader LLM compatibility
    PROMPT_TEMPLATE = """You are a reward evaluation model for an AI assistant.

Task: Evaluate the user's response to determine their satisfaction with the AI's action.

Context:
- Agent Action: {action}
- User Response: {response}

Scoring Guidelines:
+1 (Satisfied): User expresses gratitude, approval, or wants to continue
  Examples: "thanks", "great", "good", "perfect", "continue", "what's next"
  
-1 (Dissatisfied): User corrects, complains, or indicates error
  Examples: "wrong", "incorrect", "should be", "not working", "redo", "fix this"
  
0 (Neutral): No clear satisfaction signal
  Examples: "ok", "hmm", normal questions without correction

Important Nuances:
- "should" usually indicates correction → -1
- "what's next" implies satisfaction → +1  
- "ok" alone is acknowledgment → +1
- Questions without correction are often neutral → 0

Note: The response may be in any language. Apply the same scoring logic to translated meanings.

Respond in JSON format:
{{
  "score": <1, 0, or -1>,
  "confidence": <0.0 to 1.0>,
  "reason": "<brief explanation>"
}}

JSON Response:"""
    
    # Configuration
    DEFAULT_CONFIG = {
        'confidence_threshold': 0.7,  # Below this, use rule fallback
        'cache_enabled': True,
        'cache_size': 1000,
        'cache_ttl': 3600,  # 1 hour
        'timeout_ms': 2000,
        'fallback_to_rules': True,
        'backend': LLMBackend.AUTO,
        'openai_model': 'gpt-4o-mini',
        'anthropic_model': 'claude-3-haiku-20240307',
        'local_endpoint': 'http://localhost:11434',
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize LLM-Enhanced PRM Judge
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        
        # Initialize cache
        self._cache: Dict[str, Tuple[JudgeResult, float]] = {}
        
        # Initialize LLM clients
        self._clients: Dict[LLMBackend, LLMClient] = {}
        self._init_clients()
        
        # Initialize rule-based judge for fallback
        from claw_rl.feedback.binary_rl import BinaryRLJudge
        self._rule_judge = BinaryRLJudge()
        
        # Metrics
        self._metrics = {
            'total_calls': 0,
            'llm_calls': 0,
            'rule_fallbacks': 0,
            'cache_hits': 0,
            'errors': 0,
        }
    
    def _init_clients(self):
        """Initialize LLM clients"""
        # Try to initialize each backend
        backends_to_try = [LLMBackend.OPENAI, LLMBackend.ANTHROPIC, LLMBackend.LOCAL]
        
        for backend in backends_to_try:
            try:
                if backend == LLMBackend.OPENAI:
                    client = OpenAIClient(model=self.config['openai_model'])
                    if client.is_available():
                        self._clients[backend] = client
                        
                elif backend == LLMBackend.ANTHROPIC:
                    client = AnthropicClient(model=self.config['anthropic_model'])
                    if client.is_available():
                        self._clients[backend] = client
                        
                elif backend == LLMBackend.LOCAL:
                    client = LocalLLMClient(endpoint=self.config['local_endpoint'])
                    if client.is_available():
                        self._clients[backend] = client
            except Exception:
                pass
    
    def _select_backend(self) -> Optional[LLMBackend]:
        """Select best available backend"""
        backend_pref = self.config['backend']
        
        if backend_pref != LLMBackend.AUTO:
            if backend_pref in self._clients and self._clients[backend_pref].is_available():
                return backend_pref
        
        # Auto-select: prefer OpenAI > Anthropic > Local
        for backend in [LLMBackend.OPENAI, LLMBackend.ANTHROPIC, LLMBackend.LOCAL]:
            if backend in self._clients and self._clients[backend].is_available():
                return backend
        
        return None
    
    def judge(
        self,
        action: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        use_llm: bool = True
    ) -> JudgeResult:
        """
        Judge user satisfaction from response
        
        Args:
            action: Agent action description
            response: User response text
            context: Optional additional context
            use_llm: Whether to use LLM (default True)
            
        Returns:
            JudgeResult with reward, confidence, and metadata
        """
        start_time = time.time()
        self._metrics['total_calls'] += 1
        
        # Initialize cache_key
        cache_key = None
        if self.config['cache_enabled']:
            cache_key = self._get_cache_key(action, response)
            cached = self._get_cached(cache_key)
            if cached:
                self._metrics['cache_hits'] += 1
                return cached
        
        # 2. Try rule-based quick check (high confidence patterns)
        rule_result = self._rule_judge.judge_with_reason(response, action)
        if rule_result.confidence >= 0.95:
            # High confidence rule match, skip LLM
            result = JudgeResult(
                reward=rule_result.reward,
                confidence=rule_result.confidence,
                reason=self._get_rule_reason(rule_result.reward, response),
                source='rule',
                latency_ms=(time.time() - start_time) * 1000,
                pattern_matched=rule_result.pattern_matched
            )
            self._cache_result(cache_key, result)
            return result
        
        # 3. Try LLM evaluation
        if use_llm:
            backend = self._select_backend()
            if backend:
                try:
                    llm_result = self._judge_with_llm(action, response, context, backend)
                    if llm_result and llm_result.confidence >= self.config['confidence_threshold']:
                        llm_result.latency_ms = (time.time() - start_time) * 1000
                        self._cache_result(cache_key, llm_result)
                        self._metrics['llm_calls'] += 1
                        return llm_result
                except Exception as e:
                    self._metrics['errors'] += 1
        
        # 4. Fallback to rule-based
        if self.config['fallback_to_rules']:
            result = JudgeResult(
                reward=rule_result.reward,
                confidence=rule_result.confidence,
                reason=self._get_rule_reason(rule_result.reward, response),
                source='rule',
                latency_ms=(time.time() - start_time) * 1000,
                pattern_matched=rule_result.pattern_matched
            )
            self._metrics['rule_fallbacks'] += 1
            self._cache_result(cache_key, result)
            return result
        
        # 5. Unable to determine
        result = JudgeResult(
            reward=0,
            confidence=0.0,
            reason="Unable to determine satisfaction",
            source='unknown',
            latency_ms=(time.time() - start_time) * 1000
        )
        return result
    
    def _judge_with_llm(
        self,
        action: str,
        response: str,
        context: Optional[Dict[str, Any]],
        backend: LLMBackend
    ) -> Optional[JudgeResult]:
        """Judge using LLM"""
        client = self._clients.get(backend)
        if not client:
            return None
        
        prompt = self.PROMPT_TEMPLATE.format(
            action=action,
            response=response
        )
        
        try:
            # Safe async handling for both sync and async contexts
            import asyncio
            
            async def _call_llm():
                return await client.complete(prompt, max_tokens=100, temperature=0)
            
            # Try to get running loop first
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, need to run in executor or use asyncio.run
                # For safety, create new thread with new event loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _call_llm())
                    result_text = future.result(timeout=self.config.get('timeout_ms', 2000) / 1000)
            except RuntimeError:
                # No running loop, we can safely use asyncio.run
                result_text = asyncio.run(_call_llm())
            
            parsed = self._parse_llm_response(result_text)
            if parsed:
                return JudgeResult(
                    reward=parsed['score'],
                    confidence=parsed['confidence'],
                    reason=parsed['reason'],
                    source='llm',
                    backend=backend.value
                )
        except Exception:
            pass
        
        return None
    
    def _parse_llm_response(self, text: str) -> Optional[Dict]:
        """Parse LLM JSON response"""
        try:
            # Try to extract JSON from response
            # LLM might add extra text before/after JSON
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end]
                data = json.loads(json_str)
                
                score = int(data.get('score', 0))
                confidence = float(data.get('confidence', 0.5))
                reason = str(data.get('reason', 'No reason provided'))
                
                # Validate score
                if score not in [-1, 0, 1]:
                    return None
                
                # Validate confidence
                confidence = max(0.0, min(1.0, confidence))
                
                return {
                    'score': score,
                    'confidence': confidence,
                    'reason': reason
                }
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
        
        return None
    
    def _get_rule_reason(self, reward: int, response: str) -> str:
        """Get human-readable reason from rule-based judge"""
        if reward == 1:
            if '谢谢' in response or '感谢' in response:
                return "User expressed gratitude"
            elif '好的' in response or '很好' in response or '不错' in response:
                return "User expressed approval"
            else:
                return "User seems satisfied"
        elif reward == -1:
            if '不对' in response or '错了' in response or '错误' in response:
                return "User indicated error"
            elif '应该' in response:
                return "User provided correction"
            else:
                return "User seems dissatisfied"
        else:
            return "No clear satisfaction signal detected"
    
    def _get_cache_key(self, action: str, response: str) -> str:
        """Generate cache key"""
        combined = f"{action}|{response}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cached(self, key: str) -> Optional[JudgeResult]:
        """Get cached result if not expired"""
        if key not in self._cache:
            return None
        
        result, timestamp = self._cache[key]
        ttl = self.config['cache_ttl']
        
        if time.time() - timestamp > ttl:
            del self._cache[key]
            return None
        
        return result
    
    def _cache_result(self, key: str, result: JudgeResult) -> None:
        """Cache result with timestamp"""
        if not self.config['cache_enabled']:
            return
        
        # Limit cache size (LRU eviction)
        if len(self._cache) >= self.config['cache_size']:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = (result, time.time())
    
    def clear_cache(self) -> None:
        """Clear cache"""
        self._cache.clear()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        total = self._metrics['total_calls']
        return {
            **self._metrics,
            'cache_hit_rate': self._metrics['cache_hits'] / total if total > 0 else 0,
            'llm_usage_rate': self._metrics['llm_calls'] / total if total > 0 else 0,
            'rule_fallback_rate': self._metrics['rule_fallbacks'] / total if total > 0 else 0,
            'error_rate': self._metrics['errors'] / total if total > 0 else 0,
            'cache_size': len(self._cache),
            'available_backends': [b.value for b in self._clients.keys()],
        }
    
    def get_available_backends(self) -> List[str]:
        """Get list of available LLM backends"""
        return [b.value for b in self._clients.keys()]
    
    # Backward compatibility
    def judge_tuple(self, action: str, response: str) -> Tuple[int, str]:
        """Simple tuple return for backward compatibility"""
        result = self.judge(action, response)
        return result.to_tuple()
