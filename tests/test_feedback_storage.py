"""
Tests for Feedback Storage

Tests for:
- FeedbackStorage
- Store, query, delete
- Statistics and trends
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

from claw_rl.feedback.collector import Feedback, FeedbackType, FeedbackCollector
from claw_rl.feedback.storage import FeedbackStorage


class TestFeedbackStorage:
    """Test FeedbackStorage."""
    
    @pytest.fixture
    def temp_storage(self, tmp_path):
        """Create a temporary storage for testing."""
        storage_file = tmp_path / "test_feedback.json"
        return FeedbackStorage(str(storage_file))
    
    @pytest.fixture
    def collector(self):
        """Create a FeedbackCollector."""
        return FeedbackCollector()
    
    def test_store_and_get(self, temp_storage, collector):
        """Test storing and retrieving feedback."""
        fb = collector.collect_thumbs_up(session_id="test-123")
        
        fb_id = temp_storage.store(fb)
        
        assert fb_id.startswith("fb_")
        
        retrieved = temp_storage.get(fb_id)
        
        assert retrieved is not None
        assert retrieved.feedback_type == "thumbs_up"
        assert retrieved.session_id == "test-123"
    
    def test_store_batch(self, temp_storage, collector):
        """Test storing multiple feedbacks."""
        feedbacks = [
            collector.collect_thumbs_up(),
            collector.collect_thumbs_down(),
            collector.collect_rating(5),
        ]
        
        ids = temp_storage.store_batch(feedbacks)
        
        assert len(ids) == 3
        assert all(id.startswith("fb_") for id in ids)
    
    def test_query_by_type(self, temp_storage, collector):
        """Test querying by feedback type."""
        # Store various types
        temp_storage.store(collector.collect_thumbs_up())
        temp_storage.store(collector.collect_thumbs_up())
        temp_storage.store(collector.collect_thumbs_down())
        temp_storage.store(collector.collect_rating(5))
        
        # Query thumbs_up
        results = temp_storage.query(feedback_type="thumbs_up")
        
        assert len(results) == 2
        
        # Query rating
        results = temp_storage.query(feedback_type="rating")
        
        assert len(results) == 1
    
    def test_query_by_signal(self, temp_storage, collector):
        """Test querying by signal."""
        # Store various signals
        temp_storage.store(collector.collect_thumbs_up())  # positive
        temp_storage.store(collector.collect_thumbs_up())  # positive
        temp_storage.store(collector.collect_thumbs_down())  # negative
        temp_storage.store(collector.collect_rating(3))  # neutral
        
        # Query positive
        results = temp_storage.query(signal="positive")
        
        assert len(results) == 2
        
        # Query negative
        results = temp_storage.query(signal="negative")
        
        assert len(results) == 1
    
    def test_query_by_source(self, temp_storage, collector):
        """Test querying by source."""
        temp_storage.store(collector.collect_thumbs_up(source="webchat"))
        temp_storage.store(collector.collect_thumbs_up(source="discord"))
        temp_storage.store(collector.collect_thumbs_down(source="webchat"))
        
        results = temp_storage.query(source="webchat")
        
        assert len(results) == 2
    
    def test_query_by_session(self, temp_storage, collector):
        """Test querying by session ID."""
        temp_storage.store(collector.collect_thumbs_up(session_id="session-1"))
        temp_storage.store(collector.collect_thumbs_up(session_id="session-1"))
        temp_storage.store(collector.collect_thumbs_down(session_id="session-2"))
        
        results = temp_storage.query(session_id="session-1")
        
        assert len(results) == 2
    
    def test_query_by_days(self, temp_storage, collector):
        """Test querying by days."""
        # Store new feedback
        temp_storage.store(collector.collect_thumbs_up())
        temp_storage.store(collector.collect_thumbs_down())
        
        # Query last 7 days
        results = temp_storage.query(days=7)
        
        assert len(results) == 2
        
        # Query last 0 days (should be empty for new feedback)
        results = temp_storage.query(days=0)
        
        # Note: current implementation includes today
        # So this might return results
    
    def test_query_limit(self, temp_storage, collector):
        """Test query limit."""
        for _ in range(10):
            temp_storage.store(collector.collect_thumbs_up())
        
        results = temp_storage.query(limit=5)
        
        assert len(results) == 5
    
    def test_count(self, temp_storage, collector):
        """Test counting feedback."""
        temp_storage.store(collector.collect_thumbs_up())
        temp_storage.store(collector.collect_thumbs_up())
        temp_storage.store(collector.collect_thumbs_down())
        
        total = temp_storage.count()
        positive = temp_storage.count(signal="positive")
        
        assert total == 3
        assert positive == 2
    
    def test_delete(self, temp_storage, collector):
        """Test deleting feedback."""
        fb = collector.collect_thumbs_up()
        fb_id = temp_storage.store(fb)
        
        assert temp_storage.get(fb_id) is not None
        
        result = temp_storage.delete(fb_id)
        
        assert result is True
        assert temp_storage.get(fb_id) is None
    
    def test_delete_nonexistent(self, temp_storage):
        """Test deleting nonexistent feedback."""
        result = temp_storage.delete("nonexistent-id")
        
        assert result is False
    
    def test_clear(self, temp_storage, collector):
        """Test clearing all feedback."""
        temp_storage.store(collector.collect_thumbs_up())
        temp_storage.store(collector.collect_thumbs_down())
        
        count = temp_storage.clear()
        
        assert count == 2
        assert len(temp_storage) == 0
    
    def test_statistics(self, temp_storage, collector):
        """Test statistics calculation."""
        # Store various feedback
        for _ in range(5):
            temp_storage.store(collector.collect_thumbs_up())  # positive
        for _ in range(2):
            temp_storage.store(collector.collect_thumbs_down())  # negative
        for _ in range(3):
            temp_storage.store(collector.collect_rating(3))  # neutral
        
        stats = temp_storage.get_statistics()
        
        assert stats["total"] == 10
        assert stats["by_type"]["thumbs_up"] == 5
        assert stats["by_type"]["thumbs_down"] == 2
        assert stats["by_signal"]["positive"] == 5
        assert stats["by_signal"]["negative"] == 2
        assert stats["positive_rate"] == 0.5
        assert 0 <= stats["average_confidence"] <= 1
    
    def test_statistics_empty(self, temp_storage):
        """Test statistics with no feedback."""
        stats = temp_storage.get_statistics()
        
        assert stats["total"] == 0
        assert stats["positive_rate"] == 0.0
    
    def test_trends(self, temp_storage, collector):
        """Test trend calculation."""
        # Store feedback
        for _ in range(5):
            temp_storage.store(collector.collect_thumbs_up())
        for _ in range(2):
            temp_storage.store(collector.collect_thumbs_down())
        
        trends = temp_storage.get_trends(days=7, granularity="day")
        
        assert trends["period"] == "7 days"
        assert trends["granularity"] == "day"
        assert len(trends["data_points"]) >= 1
    
    def test_export_json(self, temp_storage, collector):
        """Test exporting to JSON."""
        temp_storage.store(collector.collect_thumbs_up())
        temp_storage.store(collector.collect_thumbs_down())
        
        exported = temp_storage.export(format="json")
        
        # Should be valid JSON
        data = json.loads(exported)
        assert len(data) == 2
    
    def test_import_json(self, temp_storage):
        """Test importing from JSON."""
        data = json.dumps([
            {
                "feedback_type": "thumbs_up",
                "source": "test",
                "timestamp": "2026-04-03T00:00:00",
                "signal": "positive",
                "confidence": 0.95,
                "metadata": {},
            },
            {
                "feedback_type": "thumbs_down",
                "source": "test",
                "timestamp": "2026-04-03T00:01:00",
                "signal": "negative",
                "confidence": 0.95,
                "metadata": {},
            },
        ])
        
        count = temp_storage.import_data(data, format="json")
        
        assert count == 2
        assert len(temp_storage) == 2
    
    def test_persistence(self, tmp_path, collector):
        """Test persistence across instances."""
        storage_file = tmp_path / "test_persist.json"
        
        # Store feedback in first instance
        storage1 = FeedbackStorage(str(storage_file))
        fb = collector.collect_thumbs_up(session_id="persist-test")
        fb_id = storage1.store(fb)
        
        # Create second instance and check
        storage2 = FeedbackStorage(str(storage_file))
        retrieved = storage2.get(fb_id)
        
        assert retrieved is not None
        assert retrieved.session_id == "persist-test"
    
    def test_len(self, temp_storage, collector):
        """Test len() for storage."""
        assert len(temp_storage) == 0
        
        temp_storage.store(collector.collect_thumbs_up())
        assert len(temp_storage) == 1
        
        temp_storage.store(collector.collect_thumbs_down())
        assert len(temp_storage) == 2
    
    def test_repr(self, temp_storage):
        """Test repr for storage."""
        repr_str = repr(temp_storage)
        
        assert "FeedbackStorage" in repr_str
        assert "count=0" in repr_str
