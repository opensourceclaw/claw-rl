"""
Temporal Pattern Recognition - Identify patterns in time-series data.

This module provides time-based pattern recognition capabilities:
- Sliding window analysis
- Time-based clustering
- Sequence pattern mining
- Periodic pattern detection

Reference: ADR-007: Pattern Recognition Engine
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import time
from collections import defaultdict


class TemporalPatternType(Enum):
    """Types of temporal patterns."""
    PERIODIC = "periodic"          # Recurring at fixed intervals
    SEQUENTIAL = "sequential"      # Sequence of events
    TRENDING = "trending"          # Increasing/decreasing trend
    BURST = "burst"                # Sudden spike in activity
    SEASONAL = "seasonal"          # Seasonal patterns


@dataclass
class TimeWindow:
    """Represents a time window for analysis."""
    start: datetime
    end: datetime
    
    def duration(self) -> timedelta:
        """Get window duration."""
        return self.end - self.start
    
    def contains(self, timestamp: datetime) -> bool:
        """Check if timestamp is within window."""
        return self.start <= timestamp <= self.end
    
    def to_dict(self) -> dict:
        return {
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'duration_seconds': self.duration().total_seconds()
        }


@dataclass
class TemporalPattern:
    """Represents a temporal pattern."""
    pattern_id: str
    pattern_type: TemporalPatternType
    time_window: TimeWindow
    confidence: float
    frequency: int  # How often the pattern occurs
    period: Optional[timedelta] = None  # For periodic patterns
    sequence: Optional[List[str]] = None  # For sequential patterns
    trend_direction: Optional[str] = None  # For trending patterns: 'up', 'down', 'stable'
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type.value,
            'time_window': self.time_window.to_dict(),
            'confidence': self.confidence,
            'frequency': self.frequency,
            'period': self.period.total_seconds() if self.period else None,
            'sequence': self.sequence,
            'trend_direction': self.trend_direction,
            'metadata': self.metadata
        }
    
    def is_significant(self, min_confidence: float = 0.7, min_frequency: int = 3) -> bool:
        """Check if pattern is significant."""
        return self.confidence >= min_confidence and self.frequency >= min_frequency


class TemporalPatternRecognizer:
    """
    Temporal Pattern Recognizer.
    
    Recognizes time-based patterns in memory data:
    - Periodic patterns (daily, weekly, monthly)
    - Sequential patterns (A → B → C)
    - Trending patterns (increasing/decreasing)
    - Burst patterns (sudden spikes)
    - Seasonal patterns (season-based)
    
    Example:
        >>> recognizer = TemporalPatternRecognizer()
        >>> memories = [
        ...     {'id': 'm1', 'timestamp': datetime.now(), 'content': '...'},
        ...     {'id': 'm2', 'timestamp': datetime.now() + timedelta(hours=1), 'content': '...'},
        ... ]
        >>> patterns = recognizer.recognize(memories)
        >>> for pattern in patterns:
        ...     print(f"{pattern.pattern_type.value}: {pattern.confidence:.2f}")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Temporal Pattern Recognizer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Configuration
        self.min_confidence = self.config.get('min_confidence', 0.7)
        self.min_frequency = self.config.get('min_frequency', 3)
        self.window_size = self.config.get('window_size', timedelta(hours=1))
        self.period_thresholds = self.config.get('period_thresholds', {
            'hourly': timedelta(hours=1),
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'monthly': timedelta(days=30)
        })
        
        # Statistics
        self._total_processed = 0
        self._patterns_found = 0
    
    def recognize(
        self,
        memories: List[Dict[str, Any]],
        pattern_types: Optional[List[TemporalPatternType]] = None
    ) -> List[TemporalPattern]:
        """
        Recognize temporal patterns in memories.
        
        Args:
            memories: List of memories with timestamps
            pattern_types: Types of patterns to recognize (default: all)
            
        Returns:
            List of temporal patterns
        """
        start_time = time.time()
        
        # Default to all pattern types
        if pattern_types is None:
            pattern_types = [
                TemporalPatternType.PERIODIC,
                TemporalPatternType.SEQUENTIAL,
                TemporalPatternType.TRENDING,
                TemporalPatternType.BURST
            ]
        
        patterns = []
        
        # Sort memories by timestamp
        sorted_memories = self._sort_by_timestamp(memories)
        
        # Recognize each pattern type
        for pattern_type in pattern_types:
            if pattern_type == TemporalPatternType.PERIODIC:
                type_patterns = self._recognize_periodic_patterns(sorted_memories)
                patterns.extend(type_patterns)
            
            elif pattern_type == TemporalPatternType.SEQUENTIAL:
                type_patterns = self._recognize_sequential_patterns(sorted_memories)
                patterns.extend(type_patterns)
            
            elif pattern_type == TemporalPatternType.TRENDING:
                type_patterns = self._recognize_trending_patterns(sorted_memories)
                patterns.extend(type_patterns)
            
            elif pattern_type == TemporalPatternType.BURST:
                type_patterns = self._recognize_burst_patterns(sorted_memories)
                patterns.extend(type_patterns)
        
        # Update statistics
        self._total_processed += len(memories)
        self._patterns_found += len(patterns)
        
        return patterns
    
    def _sort_by_timestamp(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort memories by timestamp."""
        return sorted(memories, key=lambda m: m.get('timestamp', datetime.now()))
    
    def _recognize_periodic_patterns(self, memories: List[Dict[str, Any]]) -> List[TemporalPattern]:
        """
        Recognize periodic patterns.
        
        Looks for patterns that repeat at regular intervals.
        """
        patterns = []
        
        if len(memories) < self.min_frequency:
            return patterns
        
        # Group memories by time intervals
        intervals = defaultdict(list)
        
        for memory in memories:
            timestamp = memory.get('timestamp', datetime.now())
            
            # Check each period threshold
            for period_name, period_delta in self.period_thresholds.items():
                # Create interval key based on period
                if period_name == 'hourly':
                    key = timestamp.strftime('%Y-%m-%d %H:00')
                elif period_name == 'daily':
                    key = timestamp.strftime('%Y-%m-%d')
                elif period_name == 'weekly':
                    key = timestamp.strftime('%Y-%W')
                else:  # monthly
                    key = timestamp.strftime('%Y-%m')
                
                intervals[(period_name, key)].append(memory)
        
        # Find recurring patterns
        for (period_name, key), group in intervals.items():
            if len(group) >= self.min_frequency:
                period_delta = self.period_thresholds[period_name]
                
                # Calculate confidence based on frequency
                confidence = min(1.0, len(group) / 10.0)
                
                pattern = TemporalPattern(
                    pattern_id=f"periodic_{period_name}_{len(patterns)}",
                    pattern_type=TemporalPatternType.PERIODIC,
                    time_window=TimeWindow(
                        start=group[0].get('timestamp', datetime.now()),
                        end=group[-1].get('timestamp', datetime.now())
                    ),
                    confidence=confidence,
                    frequency=len(group),
                    period=period_delta,
                    metadata={'period_type': period_name, 'interval_key': key}
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _recognize_sequential_patterns(self, memories: List[Dict[str, Any]]) -> List[TemporalPattern]:
        """
        Recognize sequential patterns.
        
        Looks for patterns where events follow a specific sequence.
        """
        patterns = []
        
        if len(memories) < 3:
            return patterns
        
        # Extract content sequences
        sequences = defaultdict(int)
        
        # Sliding window of size 3
        for i in range(len(memories) - 2):
            seq = tuple([
                memories[i].get('content', '')[:50],
                memories[i+1].get('content', '')[:50],
                memories[i+2].get('content', '')[:50]
            ])
            sequences[seq] += 1
        
        # Find recurring sequences
        for seq, count in sequences.items():
            if count >= self.min_frequency:
                confidence = min(1.0, count / 5.0)
                
                pattern = TemporalPattern(
                    pattern_id=f"sequential_{len(patterns)}",
                    pattern_type=TemporalPatternType.SEQUENTIAL,
                    time_window=TimeWindow(
                        start=memories[0].get('timestamp', datetime.now()),
                        end=memories[-1].get('timestamp', datetime.now())
                    ),
                    confidence=confidence,
                    frequency=count,
                    sequence=list(seq),
                    metadata={'sequence_length': 3}
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _recognize_trending_patterns(self, memories: List[Dict[str, Any]]) -> List[TemporalPattern]:
        """
        Recognize trending patterns.
        
        Looks for increasing or decreasing trends over time.
        """
        patterns = []
        
        if len(memories) < 5:
            return patterns
        
        # Divide memories into time windows
        window_size = self.window_size
        windows = defaultdict(list)
        
        for memory in memories:
            timestamp = memory.get('timestamp', datetime.now())
            window_key = int(timestamp.timestamp() / window_size.total_seconds())
            windows[window_key].append(memory)
        
        # Analyze trend
        window_counts = [len(windows[k]) for k in sorted(windows.keys())]
        
        if len(window_counts) >= 3:
            # Simple trend detection: compare first half to second half
            mid = len(window_counts) // 2
            first_half_avg = sum(window_counts[:mid]) / max(mid, 1)
            second_half_avg = sum(window_counts[mid:]) / max(len(window_counts) - mid, 1)
            
            # Determine trend direction
            if second_half_avg > first_half_avg * 1.5:
                trend_direction = 'up'
                confidence = min(1.0, (second_half_avg - first_half_avg) / first_half_avg)
            elif second_half_avg < first_half_avg * 0.5:
                trend_direction = 'down'
                confidence = min(1.0, (first_half_avg - second_half_avg) / first_half_avg)
            else:
                trend_direction = 'stable'
                confidence = 0.5
            
            pattern = TemporalPattern(
                pattern_id=f"trending_{len(patterns)}",
                pattern_type=TemporalPatternType.TRENDING,
                time_window=TimeWindow(
                    start=memories[0].get('timestamp', datetime.now()),
                    end=memories[-1].get('timestamp', datetime.now())
                ),
                confidence=confidence,
                frequency=len(memories),
                trend_direction=trend_direction,
                metadata={
                    'first_half_avg': first_half_avg,
                    'second_half_avg': second_half_avg
                }
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def _recognize_burst_patterns(self, memories: List[Dict[str, Any]]) -> List[TemporalPattern]:
        """
        Recognize burst patterns.
        
        Looks for sudden spikes in activity.
        """
        patterns = []
        
        if len(memories) < 5:
            return patterns
        
        # Group by time windows
        window_size = self.window_size
        windows = defaultdict(list)
        
        for memory in memories:
            timestamp = memory.get('timestamp', datetime.now())
            window_key = int(timestamp.timestamp() / window_size.total_seconds())
            windows[window_key].append(memory)
        
        # Calculate average and standard deviation
        window_counts = [len(windows[k]) for k in sorted(windows.keys())]
        
        if len(window_counts) >= 3:
            avg_count = sum(window_counts) / len(window_counts)
            
            # Find bursts (windows with count > 2x average)
            burst_threshold = avg_count * 2
            
            for window_key, count in zip(sorted(windows.keys()), window_counts):
                if count > burst_threshold:
                    # Calculate burst severity
                    severity = (count - avg_count) / avg_count
                    confidence = min(1.0, severity)
                    
                    # Get time window
                    window_start = datetime.fromtimestamp(window_key * window_size.total_seconds())
                    window_end = window_start + window_size
                    
                    pattern = TemporalPattern(
                        pattern_id=f"burst_{len(patterns)}",
                        pattern_type=TemporalPatternType.BURST,
                        time_window=TimeWindow(start=window_start, end=window_end),
                        confidence=confidence,
                        frequency=count,
                        metadata={
                            'avg_count': avg_count,
                            'burst_threshold': burst_threshold,
                            'severity': severity
                        }
                    )
                    
                    patterns.append(pattern)
        
        return patterns
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get recognizer statistics."""
        return {
            'total_processed': self._total_processed,
            'patterns_found': self._patterns_found
        }
