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
Judge Response Cache for claw-rl v2.5.0
LRU cache with TTL for judge responses
"""

import time
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from collections import OrderedDict
from dataclasses import dataclass
import threading


@dataclass
class JudgeCacheEntry:
    """Cache entry for judge response"""
    reward: int
    reason: str
    timestamp: float
    access_count: int = 0


class JudgeResponseCache:
    """LRU Cache with TTL for judge responses

    Features:
    - LRU eviction
    - TTL expiration
    - Access frequency tracking
    - Thread-safe operations
    - Content-based hashing
    """

    def __init__(
        self,
        max_size: int = 500,
        ttl_seconds: float = 600.0,
        min_access_count: int = 2
    ):
        """Initialize cache

        Args:
            max_size: Maximum number of entries
            ttl_seconds: Time-to-live in seconds (default: 10 min)
            min_access_count: Minimum accesses before frequency boost
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.min_access_count = min_access_count

        self._cache: OrderedDict[str, JudgeCacheEntry] = OrderedDict()
        self._lock = threading.RLock()

        # Stats
        self._hits = 0
        self._misses = 0

    def _make_key(self, action: str, response: str) -> str:
        """Generate cache key from action and response"""
        # Normalize and hash for consistent keys
        key_data = f"{action.strip().lower()}:{response.strip().lower()}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def get(self, action: str, response: str) -> Optional[Tuple[int, str]]:
        """Get cached judge response

        Args:
            action: Action taken
            response: User response

        Returns:
            (reward, reason) or None
        """
        key = self._make_key(action, response)

        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]

            # Check TTL
            if time.time() - entry.timestamp > self.ttl_seconds:
                del self._cache[key]
                self._misses += 1
                return None

            # Update access order (move to end)
            self._cache.move_to_end(key)
            entry.access_count += 1

            self._hits += 1
            return (entry.reward, entry.reason)

    def put(self, action: str, response: str, reward: int, reason: str):
        """Cache judge response

        Args:
            action: Action taken
            response: User response
            reward: Judge reward (-1, 0, +1)
            reason: Judge reasoning
        """
        key = self._make_key(action, response)

        with self._lock:
            # Evict if needed
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)

            # Store
            self._cache[key] = JudgeCacheEntry(
                reward=reward,
                reason=reason,
                timestamp=time.time(),
                access_count=1
            )

    def invalidate(self, action: Optional[str] = None):
        """Invalidate cache

        Args:
            action: Specific action to invalidate, or None for all
        """
        with self._lock:
            if action is None:
                self._cache.clear()
            else:
                # Remove entries matching action
                keys_to_remove = []
                for key, entry in self._cache.items():
                    # This is approximate - we'd need to store action separately for exact match
                    keys_to_remove.append(key)
                for key in keys_to_remove:
                    self._cache.pop(key, None)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics

        Returns:
            Statistics dictionary
        """
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "ttl_seconds": self.ttl_seconds
            }

    def cleanup_expired(self):
        """Remove expired entries"""
        with self._lock:
            now = time.time()
            expired = [
                key for key, entry in self._cache.items()
                if now - entry.timestamp > self.ttl_seconds
            ]
            for key in expired:
                del self._cache[key]


# Global cache instance
_judge_cache: Optional[JudgeResponseCache] = None


def get_judge_cache(
    max_size: int = 500,
    ttl_seconds: float = 600.0
) -> JudgeResponseCache:
    """Get global judge cache instance"""
    global _judge_cache

    if _judge_cache is None:
        _judge_cache = JudgeResponseCache(
            max_size=max_size,
            ttl_seconds=ttl_seconds
        )

    return _judge_cache
