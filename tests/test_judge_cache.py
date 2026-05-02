# Copyright 2026 Peter Cheng
#
# Licensed under the Apache License, Version 2.0 (the "License");
"""Tests for learning/judge_cache.py"""

import time
import pytest
from claw_rl.learning.judge_cache import (
    JudgeCacheEntry,
    JudgeResponseCache,
    get_judge_cache,
)


class TestJudgeCacheEntry:
    def test_creation(self):
        entry = JudgeCacheEntry(reward=1, reason="test", timestamp=time.time())
        assert entry.reward == 1
        assert entry.reason == "test"
        assert entry.access_count == 0

    def test_access_count_default(self):
        entry = JudgeCacheEntry(reward=0, reason="", timestamp=0.0)
        assert entry.access_count == 0

    def test_access_count_set(self):
        entry = JudgeCacheEntry(reward=-1, reason="bad", timestamp=1.0,
                                access_count=5)
        assert entry.access_count == 5


class TestJudgeResponseCache:
    def test_init_defaults(self):
        cache = JudgeResponseCache()
        assert cache.max_size == 500
        assert cache.ttl_seconds == 600.0
        assert cache._hits == 0
        assert cache._misses == 0

    def test_make_key_deterministic(self):
        cache = JudgeResponseCache()
        k1 = cache._make_key("action", "response")
        k2 = cache._make_key("action", "response")
        k3 = cache._make_key("ACTION", "RESPONSE")
        assert k1 == k2
        assert k1 == k3

    def test_make_key_different(self):
        cache = JudgeResponseCache()
        k1 = cache._make_key("a1", "r1")
        k2 = cache._make_key("a2", "r2")
        assert k1 != k2

    def test_put_and_get(self):
        cache = JudgeResponseCache()
        cache.put("action1", "response1", reward=1, reason="good job")
        result = cache.get("action1", "response1")
        assert result is not None
        assert result == (1, "good job")

    def test_get_miss(self):
        cache = JudgeResponseCache()
        result = cache.get("unknown", "unknown")
        assert result is None

    def test_get_ttl_expired(self):
        cache = JudgeResponseCache(ttl_seconds=0.001)
        cache.put("act", "resp", reward=1, reason="ok")
        time.sleep(0.01)
        result = cache.get("act", "resp")
        assert result is None

    def test_lru_eviction(self):
        cache = JudgeResponseCache(max_size=2)
        cache.put("a1", "r1", reward=1, reason="first")
        cache.put("a2", "r2", reward=1, reason="second")
        cache.put("a3", "r3", reward=1, reason="third")
        # First entry should be evicted
        assert cache.get("a1", "r1") is None
        assert cache.get("a3", "r3") is not None

    def test_lru_move_to_end(self):
        cache = JudgeResponseCache(max_size=2)
        cache.put("a1", "r1", reward=1, reason="first")
        cache.put("a2", "r2", reward=1, reason="second")
        # Access a1 to move it to end
        cache.get("a1", "r1")
        cache.put("a3", "r3", reward=1, reason="third")
        # a2 should be evicted, a1 preserved
        assert cache.get("a2", "r2") is None
        assert cache.get("a1", "r1") is not None

    def test_invalidate_all(self):
        cache = JudgeResponseCache()
        cache.put("a1", "r1", reward=1, reason="ok")
        cache.put("a2", "r2", reward=1, reason="ok")
        cache.invalidate()
        assert cache.get("a1", "r1") is None
        assert cache.get("a2", "r2") is None

    def test_invalidate_specific(self):
        cache = JudgeResponseCache()
        cache.put("a1", "r1", reward=1, reason="ok")
        cache.put("a2", "r2", reward=1, reason="ok")
        cache.invalidate(action="a1")
        # invalidate specific currently clears all
        assert cache.get("a1", "r1") is None
        assert cache.get("a2", "r2") is None

    def test_get_stats_empty(self):
        cache = JudgeResponseCache()
        stats = cache.get_stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0

    def test_get_stats_with_data(self):
        cache = JudgeResponseCache()
        cache.put("a", "r", reward=1, reason="ok")
        cache.get("a", "r")
        cache.get("unknown", "unknown")
        stats = cache.get_stats()
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0

    def test_cleanup_expired(self):
        cache = JudgeResponseCache(ttl_seconds=0.001)
        cache.put("a", "r", reward=1, reason="ok")
        time.sleep(0.01)
        cache.cleanup_expired()
        stats = cache.get_stats()
        assert stats["size"] == 0

    def test_access_count_increment(self):
        cache = JudgeResponseCache()
        cache.put("a", "r", reward=1, reason="ok")
        cache.get("a", "r")
        cache.get("a", "r")
        # The cache entry access_count should be incremented
        # Access via internal structure
        key = cache._make_key("a", "r")
        assert cache._cache[key].access_count == 3


class TestGetJudgeCache:
    def test_singleton_behavior(self):
        c1 = get_judge_cache()
        c2 = get_judge_cache()
        assert c1 is c2
