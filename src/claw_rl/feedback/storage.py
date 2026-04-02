"""
Feedback Storage - Persistent storage for feedback data

This module provides storage interfaces for feedback data,
supporting both in-memory and file-based persistence.
"""

import json
from typing import Optional, List, Dict, Any
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .collector import Feedback, FeedbackType, FeedbackSource


class FeedbackStorage:
    """
    Persistent storage for feedback data.
    
    Supports:
    - JSON file storage
    - Query by type, source, signal, date range
    - Statistics and aggregation
    
    Example:
        >>> storage = FeedbackStorage("~/.claw-rl/feedback.json")
        >>> 
        >>> # Store feedback
        >>> fb = Feedback(...)
        >>> storage.store(fb)
        >>> 
        >>> # Query feedback
        >>> recent = storage.query(days=7, signal="positive")
        >>> 
        >>> # Get statistics
        >>> stats = storage.get_statistics()
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize FeedbackStorage.
        
        Args:
            storage_path: Path to JSON storage file. If None, uses default.
        """
        if storage_path is None:
            storage_path = str(Path.home() / ".claw-rl" / "feedback.json")
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._feedbacks: List[Feedback] = []
        self._load()
    
    def _load(self) -> None:
        """Load feedback from storage file."""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._feedbacks = [Feedback.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError) as e:
            # Corrupted file, start fresh
            print(f"Warning: Could not load feedback storage: {e}")
            self._feedbacks = []
    
    def _save(self) -> None:
        """Save feedback to storage file."""
        data = [fb.to_dict() for fb in self._feedbacks]
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def store(self, feedback: Feedback) -> str:
        """
        Store a feedback.
        
        Args:
            feedback: Feedback to store
        
        Returns:
            Feedback ID (timestamp-based)
        """
        # Generate ID if not present
        if not feedback.metadata.get("id"):
            feedback.metadata["id"] = f"fb_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        self._feedbacks.append(feedback)
        self._save()
        
        return feedback.metadata["id"]
    
    def store_batch(self, feedbacks: List[Feedback]) -> List[str]:
        """
        Store multiple feedbacks.
        
        Args:
            feedbacks: List of feedbacks to store
        
        Returns:
            List of feedback IDs
        """
        ids = []
        for fb in feedbacks:
            ids.append(self.store(fb))
        return ids
    
    def get(self, feedback_id: str) -> Optional[Feedback]:
        """
        Get a feedback by ID.
        
        Args:
            feedback_id: Feedback ID
        
        Returns:
            Feedback if found, None otherwise
        """
        for fb in self._feedbacks:
            if fb.metadata.get("id") == feedback_id:
                return fb
        return None
    
    def query(
        self,
        feedback_type: Optional[str] = None,
        source: Optional[str] = None,
        signal: Optional[str] = None,
        session_id: Optional[str] = None,
        days: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Feedback]:
        """
        Query feedback with filters.
        
        Args:
            feedback_type: Filter by feedback type
            source: Filter by source
            signal: Filter by signal ("positive", "negative", "neutral")
            session_id: Filter by session ID
            days: Filter to last N days
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            limit: Maximum number of results
        
        Returns:
            List of matching feedbacks
        """
        results = []
        
        for fb in self._feedbacks:
            # Filter by type
            if feedback_type and fb.feedback_type != feedback_type:
                continue
            
            # Filter by source
            if source and fb.source != source:
                continue
            
            # Filter by signal
            if signal and fb.signal != signal:
                continue
            
            # Filter by session ID
            if session_id and fb.session_id != session_id:
                continue
            
            # Filter by date range
            if days or start_date or end_date:
                fb_date = datetime.fromisoformat(fb.timestamp)
                
                if days:
                    cutoff = datetime.now() - __import__("datetime").timedelta(days=days)
                    if fb_date < cutoff:
                        continue
                
                if start_date:
                    start = datetime.fromisoformat(start_date)
                    if fb_date < start:
                        continue
                
                if end_date:
                    end = datetime.fromisoformat(end_date)
                    if fb_date > end:
                        continue
            
            results.append(fb)
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        return results
    
    def count(
        self,
        feedback_type: Optional[str] = None,
        source: Optional[str] = None,
        signal: Optional[str] = None,
        session_id: Optional[str] = None,
        days: Optional[int] = None,
    ) -> int:
        """
        Count feedback matching filters.
        
        Args:
            feedback_type: Filter by feedback type
            source: Filter by source
            signal: Filter by signal
            session_id: Filter by session ID
            days: Filter to last N days
        
        Returns:
            Count of matching feedbacks
        """
        return len(self.query(
            feedback_type=feedback_type,
            source=source,
            signal=signal,
            session_id=session_id,
            days=days,
        ))
    
    def delete(self, feedback_id: str) -> bool:
        """
        Delete a feedback by ID.
        
        Args:
            feedback_id: Feedback ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        for i, fb in enumerate(self._feedbacks):
            if fb.metadata.get("id") == feedback_id:
                self._feedbacks.pop(i)
                self._save()
                return True
        return False
    
    def clear(self) -> int:
        """
        Clear all feedback.
        
        Returns:
            Number of feedbacks cleared
        """
        count = len(self._feedbacks)
        self._feedbacks.clear()
        self._save()
        return count
    
    def get_statistics(
        self,
        days: Optional[int] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get statistics about stored feedback.
        
        Args:
            days: Limit to last N days
            source: Filter by source
        
        Returns:
            Dictionary with statistics
        """
        feedbacks = self.query(days=days, source=source)
        
        if not feedbacks:
            return {
                "total": 0,
                "by_type": {},
                "by_signal": {},
                "by_source": {},
                "positive_rate": 0.0,
                "negative_rate": 0.0,
                "average_confidence": 0.0,
            }
        
        by_type: Dict[str, int] = {}
        by_signal: Dict[str, int] = {}
        by_source: Dict[str, int] = {}
        total_confidence = 0.0
        
        for fb in feedbacks:
            by_type[fb.feedback_type] = by_type.get(fb.feedback_type, 0) + 1
            by_signal[fb.signal] = by_signal.get(fb.signal, 0) + 1
            by_source[fb.source] = by_source.get(fb.source, 0) + 1
            total_confidence += fb.confidence
        
        total = len(feedbacks)
        
        return {
            "total": total,
            "by_type": by_type,
            "by_signal": by_signal,
            "by_source": by_source,
            "positive_rate": by_signal.get("positive", 0) / total,
            "negative_rate": by_signal.get("negative", 0) / total,
            "average_confidence": total_confidence / total,
        }
    
    def get_trends(
        self,
        days: int = 30,
        granularity: str = "day",
    ) -> Dict[str, Any]:
        """
        Get feedback trends over time.
        
        Args:
            days: Number of days to analyze
            granularity: "day" or "week"
        
        Returns:
            Dictionary with trend data
        """
        feedbacks = self.query(days=days)
        
        if not feedbacks:
            return {
                "period": f"{days} days",
                "granularity": granularity,
                "data_points": [],
            }
        
        # Group by period
        from datetime import timedelta
        from collections import defaultdict
        
        cutoff = datetime.now() - timedelta(days=days)
        grouped: Dict[str, Dict[str, int]] = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
        
        for fb in feedbacks:
            fb_date = datetime.fromisoformat(fb.timestamp)
            if fb_date < cutoff:
                continue
            
            if granularity == "week":
                # Group by week
                week_start = fb_date - timedelta(days=fb_date.weekday())
                key = week_start.strftime("%Y-%m-%d")
            else:
                # Group by day
                key = fb_date.strftime("%Y-%m-%d")
            
            grouped[key][fb.signal] += 1
        
        # Convert to list
        data_points = []
        for key in sorted(grouped.keys()):
            counts = grouped[key]
            total = counts["positive"] + counts["negative"] + counts["neutral"]
            data_points.append({
                "date": key,
                "positive": counts["positive"],
                "negative": counts["negative"],
                "neutral": counts["neutral"],
                "total": total,
                "positive_rate": counts["positive"] / total if total > 0 else 0,
            })
        
        return {
            "period": f"{days} days",
            "granularity": granularity,
            "data_points": data_points,
        }
    
    def export(self, format: str = "json") -> str:
        """
        Export all feedback.
        
        Args:
            format: Export format ("json" only for now)
        
        Returns:
            Exported data as string
        """
        if format == "json":
            data = [fb.to_dict() for fb in self._feedbacks]
            return json.dumps(data, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_data(self, data: str, format: str = "json") -> int:
        """
        Import feedback data.
        
        Args:
            data: Data to import
            format: Import format ("json" only for now)
        
        Returns:
            Number of feedbacks imported
        """
        if format == "json":
            items = json.loads(data)
            count = 0
            for item in items:
                fb = Feedback.from_dict(item)
                self._feedbacks.append(fb)
                count += 1
            self._save()
            return count
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def __len__(self) -> int:
        """Return number of stored feedbacks."""
        return len(self._feedbacks)
    
    def __repr__(self) -> str:
        return f"FeedbackStorage(path={self.storage_path}, count={len(self._feedbacks)})"
