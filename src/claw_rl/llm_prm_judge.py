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
claw-rl LLM-based PRM Judge

Uses LLM for more accurate reward evaluation.
Falls back to rule-based judge on error.
"""

from typing import Optional, Tuple, Dict
from pathlib import Path
import json
import hashlib


class LLMPRMJudge:
    """
    LLM-based PRM Judge for reward evaluation
    
    Uses LLM to evaluate user satisfaction from responses.
    Falls back to rule-based judge on error.
    
    Usage:
        judge = LLMPRMJudge()
        
        reward, reason = judge.judge(
            action="Created file /workspace/test.md",
            response="thanks,great!"
        )
        # Returns: (+1, "User expressed gratitude and praise")
    """
    
    # Cache for repeated patterns
    _cache: Dict[str, Tuple[int, str]] = {}
    
    # Prompt template
    PROMPT_TEMPLATE = """You are a reward evaluation model for an AI assistant.

Task: Evaluate the user's response to determine satisfaction.

Agent Action: {action}
User Response: {response}

Scoring:
- +1: User is satisfied (thanked, praised, continued conversation)
- -1: User is dissatisfied (corrected, complained, repeated question)
- 0: Neutral (no clear signal)

Respond with ONLY the score and a brief reason in this format:
SCORE | REASON

Examples:
Action: "Created file test.md" | Response: "thanks,great!" → +1 | User expressed gratitude and praise
Action: "Edited config.yaml" | Response: "incorrect,shouldput here" → -1 | User corrected the action
Action: "Generated code" | Response: "then?" → +1 | User wants to continue (satisfied)
Action: "Fixed bug" | Response: "still not working" → -1 | User indicates problem persists
Action: "Added feature" | Response: "okay" → +1 | User acknowledged and accepted
Action: "Created report" | Response: "redo" → -1 | User requested redo (dissatisfied)

Now evaluate:"""
    
    def __init__(
        self,
        cache_enabled: bool = True,
        cache_size: int = 1000,
        fallback_to_rules: bool = True
    ):
        """
        Initialize LLM PRM Judge
        
        Args:
            cache_enabled: Enable caching for repeated patterns
            cache_size: Maximum cache size
            fallback_to_rules: Fall back to rule-based judge on error
        """
        self.cache_enabled = cache_enabled
        self.cache_size = cache_size
        self.fallback_to_rules = fallback_to_rules
        
        # Import rule-based judge for fallback
        from claw_rl.feedback.binary_rl import BinaryRLJudge
        self.rule_judge = BinaryRLJudge()
    
    def judge(
        self,
        action: str,
        response: str,
        use_llm: bool = True
    ) -> Tuple[int, str]:
        """
        Judge user satisfaction from response
        
        Args:
            action: Agent action
            response: User response
            use_llm: Whether to use LLM (default True)
            
        Returns:
            Tuple[int, str]: (reward, reason)
        """
        # Check cache first
        if self.cache_enabled:
            cache_key = self._get_cache_key(action, response)
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        # Try LLM evaluation
        if use_llm:
            try:
                result = self._judge_with_llm(action, response)
                if result:
                    # Cache result
                    if self.cache_enabled:
                        self._cache_result(cache_key if self.cache_enabled else None, result)
                    return result
            except Exception as e:
                # Log error and fall back
                pass
        
        # Fallback to rule-based
        if self.fallback_to_rules:
            reward, confidence = self.rule_judge.judge(response, action)
            reason = self._get_rule_reason(reward, response)
            result = (reward, reason)
            
            # Cache result
            if self.cache_enabled:
                self._cache_result(cache_key if self.cache_enabled else None, result)
            
            return result
        
        # Default neutral
        return (0, "Unable to determine satisfaction")
    
    def _judge_with_llm(self, action: str, response: str) -> Optional[Tuple[int, str]]:
        """
        Judge using LLM
        
        Args:
            action: Agent action
            response: User response
            
        Returns:
            Optional[Tuple[int, str]]: (reward, reason) or None
        """
        # Try to use OpenClaw's LLM if available
        try:
            # Import OpenClaw LLM client
            import openai
            
            prompt = self.PROMPT_TEMPLATE.format(
                action=action,
                response=response
            )
            
            # Call LLM
            client = openai.OpenAI()
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Fast and cheap
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0
            )
            
            # Parse response
            result_text = completion.choices[0].message.content.strip()
            return self._parse_llm_response(result_text)
            
        except ImportError:
            # OpenAI not available, return None
            return None
        except Exception:
            # Any error, return None
            return None
    
    def _parse_llm_response(self, text: str) -> Optional[Tuple[int, str]]:
        """
        Parse LLM response
        
        Args:
            text: LLM response text
            
        Returns:
            Optional[Tuple[int, str]]: (reward, reason) or None
        """
        # Parse format: "SCORE | REASON"
        if '|' not in text:
            return None
        
        parts = text.split('|', 1)
        if len(parts) != 2:
            return None
        
        score_str = parts[0].strip()
        reason = parts[1].strip()
        
        # Parse score
        try:
            # Check for explicit +1 or -1
            if '+1' in score_str:
                score = 1
            elif '-1' in score_str:
                score = -1
            elif '1' in score_str and '-' not in score_str:
                # Just "1" means +1
                score = 1
            elif '0' in score_str:
                score = 0
            else:
                return None
        except:
            return None
        
        return (score, reason)
    
    def _get_rule_reason(self, reward: int, response: str) -> str:
        """Get reason from rule-based judge"""
        if reward == 1:
            if 'thanks' in response or 'thank you' in response:
                return "User expressed gratitude"
            elif 'okay' in response or 'great' in response:
                return "User expressed approval"
            else:
                return "User seems satisfied"
        elif reward == -1:
            if 'incorrect' in response or 'wrong' in response:
                return "User indicated error"
            elif 'should' in response:
                return "User provided correction"
            else:
                return "User seems dissatisfied"
        else:
            return "No clear satisfaction signal"
    
    def _get_cache_key(self, action: str, response: str) -> str:
        """Generate cache key from action and response"""
        combined = f"{action}|{response}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _cache_result(self, key: Optional[str], result: Tuple[int, str]) -> None:
        """Cache result"""
        if not key:
            return
        
        # Limit cache size
        if len(self._cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = result
    
    def clear_cache(self) -> None:
        """Clear cache"""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cache_size': len(self._cache),
            'cache_enabled': self.cache_enabled,
            'max_cache_size': self.cache_size
        }
