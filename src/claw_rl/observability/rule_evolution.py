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
Rule Evolution Tracker (v2.1.0)

Tracks the evolution of learning rules over time:
- Records rule changes (add, merge, evolve, delete)
- Generates evolution timeline
- Supports diff comparison
- Exports to various formats
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class RuleChangeType(Enum):
    """Types of rule changes"""
    CREATED = "created"
    UPDATED = "updated"
    MERGED = "merged"
    EVOLVED = "evolved"
    DEPRECATED = "deprecated"
    DELETED = "deleted"


@dataclass
class RuleSnapshot:
    """Snapshot of a rule at a point in time"""
    rule_id: str
    pattern: str
    confidence: float
    source: str
    timestamp: datetime
    feedback_count: int = 0
    positive_count: int = 0
    negative_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'rule_id': self.rule_id,
            'pattern': self.pattern,
            'confidence': self.confidence,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'feedback_count': self.feedback_count,
            'positive_count': self.positive_count,
            'negative_count': self.negative_count,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "RuleSnapshot":
        """Create from dictionary"""
        return cls(
            rule_id=data['rule_id'],
            pattern=data['pattern'],
            confidence=data['confidence'],
            source=data['source'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            feedback_count=data.get('feedback_count', 0),
            positive_count=data.get('positive_count', 0),
            negative_count=data.get('negative_count', 0),
            metadata=data.get('metadata', {}),
        )


@dataclass
class RuleChangeEvent:
    """A rule change event"""
    event_id: str
    rule_id: str
    change_type: RuleChangeType
    before: Optional[RuleSnapshot]
    after: Optional[RuleSnapshot]
    timestamp: datetime
    reason: str = ""
    related_rules: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'rule_id': self.rule_id,
            'change_type': self.change_type.value,
            'before': self.before.to_dict() if self.before else None,
            'after': self.after.to_dict() if self.after else None,
            'timestamp': self.timestamp.isoformat(),
            'reason': self.reason,
            'related_rules': self.related_rules,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "RuleChangeEvent":
        """Create from dictionary"""
        return cls(
            event_id=data['event_id'],
            rule_id=data['rule_id'],
            change_type=RuleChangeType(data['change_type']),
            before=RuleSnapshot.from_dict(data['before']) if data.get('before') else None,
            after=RuleSnapshot.from_dict(data['after']) if data.get('after') else None,
            timestamp=datetime.fromisoformat(data['timestamp']),
            reason=data.get('reason', ''),
            related_rules=data.get('related_rules', []),
        )


class RuleEvolutionTracker:
    """
    Tracks rule evolution over time.
    
    Usage:
        tracker = RuleEvolutionTracker()
        
        # Record rule creation
        tracker.record_change(
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-001",
                pattern="操作前检查目标路径",
                confidence=0.65,
                source="user_feedback",
                timestamp=datetime.now()
            ),
            reason="New rule from user feedback"
        )
        
        # Get timeline
        timeline = tracker.get_timeline()
        
        # Export
        tracker.export_to_file(Path("rule_evolution.json"))
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize tracker.
        
        Args:
            storage_path: Path to store evolution history
        """
        self.storage_path = storage_path
        self.events: List[RuleChangeEvent] = []
        self.rule_snapshots: Dict[str, List[RuleSnapshot]] = {}
        self._event_counter = 0
        
        if storage_path and storage_path.exists():
            self._load_from_storage()
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        self._event_counter += 1
        return f"event-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._event_counter:04d}"
    
    def record_change(
        self,
        rule_id: str,
        change_type: RuleChangeType,
        before: Optional[RuleSnapshot] = None,
        after: Optional[RuleSnapshot] = None,
        reason: str = "",
        related_rules: Optional[List[str]] = None
    ) -> RuleChangeEvent:
        """
        Record a rule change event.
        
        Args:
            rule_id: Rule identifier
            change_type: Type of change
            before: Snapshot before change
            after: Snapshot after change
            reason: Reason for change
            related_rules: Related rule IDs (for merges)
            
        Returns:
            Created event
        """
        event = RuleChangeEvent(
            event_id=self._generate_event_id(),
            rule_id=rule_id,
            change_type=change_type,
            before=before,
            after=after,
            timestamp=datetime.now(),
            reason=reason,
            related_rules=related_rules or [],
        )
        
        self.events.append(event)
        
        # Track snapshots per rule
        if rule_id not in self.rule_snapshots:
            self.rule_snapshots[rule_id] = []
        
        if after:
            self.rule_snapshots[rule_id].append(after)
        
        # Auto-save
        if self.storage_path:
            self._save_to_storage()
        
        logger.debug(f"Recorded {change_type.value} for rule {rule_id}")
        
        return event
    
    def record_feedback(
        self,
        rule_id: str,
        is_positive: bool,
        new_confidence: float
    ) -> Optional[RuleChangeEvent]:
        """
        Record feedback on a rule.
        
        Args:
            rule_id: Rule identifier
            is_positive: Whether feedback is positive
            new_confidence: Updated confidence
            
        Returns:
            Event if rule exists
        """
        # Get latest snapshot
        if rule_id not in self.rule_snapshots or not self.rule_snapshots[rule_id]:
            return None
        
        before = self.rule_snapshots[rule_id][-1]
        
        after = RuleSnapshot(
            rule_id=rule_id,
            pattern=before.pattern,
            confidence=new_confidence,
            source=before.source,
            timestamp=datetime.now(),
            feedback_count=before.feedback_count + 1,
            positive_count=before.positive_count + (1 if is_positive else 0),
            negative_count=before.negative_count + (0 if is_positive else 1),
            metadata=before.metadata,
        )
        
        return self.record_change(
            rule_id=rule_id,
            change_type=RuleChangeType.UPDATED,
            before=before,
            after=after,
            reason=f"{'Positive' if is_positive else 'Negative'} feedback received"
        )
    
    def record_merge(
        self,
        source_rules: List[str],
        target_rule_id: str,
        target_pattern: str,
        confidence: float
    ) -> RuleChangeEvent:
        """
        Record rule merge.
        
        Args:
            source_rules: Source rule IDs being merged
            target_rule_id: New merged rule ID
            target_pattern: Merged pattern
            confidence: Merged confidence
            
        Returns:
            Merge event
        """
        after = RuleSnapshot(
            rule_id=target_rule_id,
            pattern=target_pattern,
            confidence=confidence,
            source="merge",
            timestamp=datetime.now(),
            metadata={'merged_from': source_rules},
        )
        
        return self.record_change(
            rule_id=target_rule_id,
            change_type=RuleChangeType.MERGED,
            after=after,
            reason=f"Merged from {len(source_rules)} rules",
            related_rules=source_rules,
        )
    
    def get_timeline(self, rule_id: Optional[str] = None) -> List[Dict]:
        """
        Get evolution timeline.
        
        Args:
            rule_id: Filter by rule (optional)
            
        Returns:
            List of events in chronological order
        """
        events = self.events
        if rule_id:
            events = [e for e in events if e.rule_id == rule_id]
        
        return [e.to_dict() for e in sorted(events, key=lambda x: x.timestamp)]
    
    def get_rule_history(self, rule_id: str) -> List[Dict]:
        """
        Get history of a specific rule.
        
        Args:
            rule_id: Rule identifier
            
        Returns:
            List of snapshots
        """
        if rule_id not in self.rule_snapshots:
            return []
        
        return [s.to_dict() for s in self.rule_snapshots[rule_id]]
    
    def get_evolution_summary(self) -> Dict:
        """
        Get summary of rule evolution.
        
        Returns:
            Summary statistics
        """
        change_counts = {ct.value: 0 for ct in RuleChangeType}
        for event in self.events:
            change_counts[event.change_type.value] += 1
        
        return {
            'total_events': len(self.events),
            'total_rules': len(self.rule_snapshots),
            'change_counts': change_counts,
            'oldest_event': self.events[0].timestamp.isoformat() if self.events else None,
            'newest_event': self.events[-1].timestamp.isoformat() if self.events else None,
        }
    
    def export_markdown_timeline(self, title: str = "Rule Evolution Timeline") -> str:
        """
        Export timeline as Markdown.
        
        Args:
            title: Timeline title
            
        Returns:
            Markdown-formatted timeline
        """
        lines = [
            f"# {title}",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
        ]
        
        summary = self.get_evolution_summary()
        lines.extend([
            "## Summary",
            "",
            f"- Total Events: {summary['total_events']}",
            f"- Total Rules: {summary['total_rules']}",
            "",
        ])
        
        lines.extend([
            "## Timeline",
            "",
        ])
        
        for event in sorted(self.events, key=lambda x: x.timestamp):
            emoji = {
                RuleChangeType.CREATED: "🆕",
                RuleChangeType.UPDATED: "📝",
                RuleChangeType.MERGED: "🔗",
                RuleChangeType.EVOLVED: "📈",
                RuleChangeType.DEPRECATED: "⚠️",
                RuleChangeType.DELETED: "🗑️",
            }.get(event.change_type, "📌")
            
            lines.append(f"### {emoji} {event.timestamp.strftime('%Y-%m-%d %H:%M')} - {event.change_type.value}")
            lines.append("")
            lines.append(f"**Rule:** `{event.rule_id}`")
            
            if event.after:
                lines.append(f"**Pattern:** {event.after.pattern}")
                lines.append(f"**Confidence:** {event.after.confidence:.2f}")
            
            if event.reason:
                lines.append(f"**Reason:** {event.reason}")
            
            if event.related_rules:
                lines.append(f"**Related:** {', '.join(event.related_rules)}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def export_to_file(self, path: Path):
        """
        Export evolution history to file.
        
        Args:
            path: Output file path
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'events': [e.to_dict() for e in self.events],
            'snapshots': {
                rid: [s.to_dict() for s in snapshots]
                for rid, snapshots in self.rule_snapshots.items()
            },
            'summary': self.get_evolution_summary(),
        }
        
        path.write_text(json.dumps(data, indent=2))
        logger.info(f"Exported rule evolution to {path}")
    
    def _save_to_storage(self):
        """Save to storage path"""
        if self.storage_path:
            self.export_to_file(self.storage_path)
    
    def _load_from_storage(self):
        """Load from storage path"""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            data = json.loads(self.storage_path.read_text())
            
            self.events = [RuleChangeEvent.from_dict(e) for e in data.get('events', [])]
            
            for rid, snapshots in data.get('snapshots', {}).items():
                self.rule_snapshots[rid] = [RuleSnapshot.from_dict(s) for s in snapshots]
            
            logger.info(f"Loaded {len(self.events)} events from {self.storage_path}")
        except Exception as e:
            logger.warning(f"Failed to load from storage: {e}")
    
    def clear(self):
        """Clear all history"""
        self.events.clear()
        self.rule_snapshots.clear()
        self._event_counter = 0
