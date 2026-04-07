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
Learning Audit Module

Provides comprehensive audit logging for the learning process.

This is what makes claw-rl explainable - every learning decision
is tracked and can be reviewed.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class LearningEventType(Enum):
    """Types of learning events"""
    # Feedback events
    FEEDBACK_RECEIVED = "feedback_received"
    FEEDBACK_POSITIVE = "feedback_positive"
    FEEDBACK_NEGATIVE = "feedback_negative"
    
    # Rule events
    RULE_CREATED = "rule_created"
    RULE_UPDATED = "rule_updated"
    RULE_DELETED = "rule_deleted"
    RULE_ACTIVATED = "rule_activated"
    RULE_DEACTIVATED = "rule_deactivated"
    
    # Strategy events
    STRATEGY_SELECTED = "strategy_selected"
    STRATEGY_EVALUATED = "strategy_evaluated"
    STRATEGY_UPDATED = "strategy_updated"
    
    # Learning events
    LEARNING_STARTED = "learning_started"
    LEARNING_COMPLETED = "learning_completed"
    LEARNING_FAILED = "learning_failed"
    
    # Calibration events
    CALIBRATION_STARTED = "calibration_started"
    CALIBRATION_COMPLETED = "calibration_completed"
    
    # OPD events
    OPD_EXTRACTED = "opd_extracted"
    OPD_APPLIED = "opd_applied"
    
    # Other
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class AuditLevel(Enum):
    """Audit log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LearningEvent:
    """
    A learning event in the audit log.
    
    Attributes:
        event_id: Unique identifier
        event_type: Type of event
        timestamp: When it happened
        level: Audit level
        message: Human-readable message
        source: Where the event originated (feedback, opd, calibration, etc.)
        context: Additional context
        rule_id: Related rule ID (if applicable)
        strategy_id: Related strategy ID (if applicable)
        feedback_id: Related feedback ID (if applicable)
        metadata: Additional metadata
    """
    event_id: str
    event_type: LearningEventType
    timestamp: datetime
    level: AuditLevel
    message: str
    source: str = "unknown"
    context: Dict[str, Any] = field(default_factory=dict)
    rule_id: Optional[str] = None
    strategy_id: Optional[str] = None
    feedback_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "context": self.context,
            "rule_id": self.rule_id,
            "strategy_id": self.strategy_id,
            "feedback_id": self.feedback_id,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningEvent":
        """Create from dictionary"""
        return cls(
            event_id=data["event_id"],
            event_type=LearningEventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            level=AuditLevel(data["level"]),
            message=data["message"],
            source=data.get("source", "unknown"),
            context=data.get("context", {}),
            rule_id=data.get("rule_id"),
            strategy_id=data.get("strategy_id"),
            feedback_id=data.get("feedback_id"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class RuleExplanation:
    """
    Explanation for why a rule was created/modified.
    
    This is the core of explainable AI - every rule has a story.
    
    Attributes:
        rule_id: The rule ID
        explanation: Human-readable explanation
        source_events: IDs of events that led to this rule
        feedback_count: Number of feedback items that influenced this
        confidence_history: How confidence changed over time
        created_at: When the rule was created
        last_updated: When the rule was last modified
    """
    rule_id: str
    explanation: str
    source_events: List[str] = field(default_factory=list)
    feedback_count: int = 0
    confidence_history: List[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "explanation": self.explanation,
            "source_events": self.source_events,
            "feedback_count": self.feedback_count,
            "confidence_history": self.confidence_history,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuleExplanation":
        """Create from dictionary"""
        return cls(
            rule_id=data["rule_id"],
            explanation=data["explanation"],
            source_events=data.get("source_events", []),
            feedback_count=data.get("feedback_count", 0),
            confidence_history=data.get("confidence_history", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
        )


class LearningAudit:
    """
    Audit logging for the learning process.
    
    This provides complete traceability for all learning decisions,
    making claw-rl explainable and trustworthy.
    
    Features:
    - Complete event logging
    - Rule explanation tracking
    - Feedback source tracking
    - Time-based queries
    - Statistics and summaries
    """
    
    def __init__(self, workspace: Path):
        """
        Initialize LearningAudit.
        
        Args:
            workspace: Path to claw-rl workspace
        """
        self.workspace = workspace
        self.audit_dir = workspace / "audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        self.events: List[LearningEvent] = []
        self.explanations: Dict[str, RuleExplanation] = {}
        self._event_counter = 0
        
        # Load existing events
        self._load()
    
    def _load(self):
        """Load existing audit log"""
        events_file = self.audit_dir / "events.json"
        if events_file.exists():
            try:
                with open(events_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.events = [LearningEvent.from_dict(e) for e in data.get("events", [])]
                    self._event_counter = data.get("event_counter", len(self.events))
            except Exception as e:
                logger.warning(f"Failed to load audit log: {e}")
        
        explanations_file = self.audit_dir / "explanations.json"
        if explanations_file.exists():
            try:
                with open(explanations_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.explanations = {
                        k: RuleExplanation.from_dict(v)
                        for k, v in data.items()
                    }
            except Exception as e:
                logger.warning(f"Failed to load explanations: {e}")
    
    def _save(self):
        """Save audit log"""
        events_file = self.audit_dir / "events.json"
        with open(events_file, "w", encoding="utf-8") as f:
            json.dump({
                "events": [e.to_dict() for e in self.events],
                "event_counter": self._event_counter,
                "updated_at": datetime.now().isoformat(),
            }, f, indent=2, ensure_ascii=False)
        
        explanations_file = self.audit_dir / "explanations.json"
        with open(explanations_file, "w", encoding="utf-8") as f:
            json.dump({
                k: v.to_dict() for k, v in self.explanations.items()
            }, f, indent=2, ensure_ascii=False)
    
    def log_event(
        self,
        event_type: LearningEventType,
        message: str,
        level: AuditLevel = AuditLevel.INFO,
        source: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
        rule_id: Optional[str] = None,
        strategy_id: Optional[str] = None,
        feedback_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LearningEvent:
        """
        Log a learning event.
        
        Args:
            event_type: Type of event
            message: Human-readable message
            level: Audit level
            source: Where the event originated
            context: Additional context
            rule_id: Related rule ID
            strategy_id: Related strategy ID
            feedback_id: Related feedback ID
            metadata: Additional metadata
            
        Returns:
            The created LearningEvent
        """
        self._event_counter += 1
        event_id = f"evt_{self._event_counter:08d}"
        
        event = LearningEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now(),
            level=level,
            message=message,
            source=source,
            context=context or {},
            rule_id=rule_id,
            strategy_id=strategy_id,
            feedback_id=feedback_id,
            metadata=metadata or {},
        )
        
        self.events.append(event)
        self._save()
        
        # Log to standard logger
        log_msg = f"[{event_type.value}] {message}"
        if level == AuditLevel.DEBUG:
            logger.debug(log_msg)
        elif level == AuditLevel.INFO:
            logger.info(log_msg)
        elif level == AuditLevel.WARNING:
            logger.warning(log_msg)
        elif level == AuditLevel.ERROR:
            logger.error(log_msg)
        elif level == AuditLevel.CRITICAL:
            logger.critical(log_msg)
        
        return event
    
    def explain_rule(self, rule_id: str) -> Optional[RuleExplanation]:
        """
        Get explanation for a rule.
        
        Args:
            rule_id: The rule ID
            
        Returns:
            RuleExplanation or None
        """
        return self.explanations.get(rule_id)
    
    def create_explanation(
        self,
        rule_id: str,
        explanation: str,
        source_events: Optional[List[str]] = None,
        feedback_count: int = 0,
    ) -> RuleExplanation:
        """
        Create an explanation for a rule.
        
        Args:
            rule_id: The rule ID
            explanation: Human-readable explanation
            source_events: IDs of events that led to this rule
            feedback_count: Number of feedback items
            
        Returns:
            The created RuleExplanation
        """
        rule_explanation = RuleExplanation(
            rule_id=rule_id,
            explanation=explanation,
            source_events=source_events or [],
            feedback_count=feedback_count,
        )
        
        self.explanations[rule_id] = rule_explanation
        self._save()
        
        return rule_explanation
    
    def update_explanation(
        self,
        rule_id: str,
        explanation: Optional[str] = None,
        source_events: Optional[List[str]] = None,
        feedback_count: Optional[int] = None,
    ) -> Optional[RuleExplanation]:
        """
        Update an explanation for a rule.
        
        Args:
            rule_id: The rule ID
            explanation: New explanation (optional)
            source_events: Additional source events (optional)
            feedback_count: New feedback count (optional)
            
        Returns:
            Updated RuleExplanation or None
        """
        if rule_id not in self.explanations:
            return None
        
        rule_explanation = self.explanations[rule_id]
        
        if explanation:
            rule_explanation.explanation = explanation
        
        if source_events:
            rule_explanation.source_events.extend(source_events)
            rule_explanation.source_events = list(set(rule_explanation.source_events))
        
        if feedback_count is not None:
            rule_explanation.feedback_count = feedback_count
        
        rule_explanation.last_updated = datetime.now()
        self._save()
        
        return rule_explanation
    
    def get_events(
        self,
        event_type: Optional[LearningEventType] = None,
        source: Optional[str] = None,
        rule_id: Optional[str] = None,
        strategy_id: Optional[str] = None,
        feedback_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[LearningEvent]:
        """
        Get events with filters.
        
        Args:
            event_type: Filter by event type
            source: Filter by source
            rule_id: Filter by rule ID
            strategy_id: Filter by strategy ID
            feedback_id: Filter by feedback ID
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of results
            
        Returns:
            List of matching events
        """
        results = []
        
        for event in reversed(self.events):  # Most recent first
            # Apply filters
            if event_type and event.event_type != event_type:
                continue
            if source and event.source != source:
                continue
            if rule_id and event.rule_id != rule_id:
                continue
            if strategy_id and event.strategy_id != strategy_id:
                continue
            if feedback_id and event.feedback_id != feedback_id:
                continue
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            
            results.append(event)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_rule_history(self, rule_id: str) -> List[LearningEvent]:
        """
        Get all events related to a rule.
        
        Args:
            rule_id: The rule ID
            
        Returns:
            List of related events
        """
        return [
            event for event in self.events
            if event.rule_id == rule_id
        ]
    
    def get_feedback_sources(self, rule_id: str) -> List[str]:
        """
        Get all feedback sources that influenced a rule.
        
        Args:
            rule_id: The rule ID
            
        Returns:
            List of feedback IDs
        """
        events = self.get_rule_history(rule_id)
        feedback_ids = set()
        
        for event in events:
            if event.feedback_id:
                feedback_ids.add(event.feedback_id)
        
        return list(feedback_ids)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get audit statistics.
        
        Returns:
            Dictionary with statistics
        """
        # Event counts by type
        event_counts = {}
        for event in self.events:
            type_name = event.event_type.value
            event_counts[type_name] = event_counts.get(type_name, 0) + 1
        
        # Event counts by source
        source_counts = {}
        for event in self.events:
            source_counts[event.source] = source_counts.get(event.source, 0) + 1
        
        # Rules with explanations
        explained_rules = len(self.explanations)
        
        # Time range
        if self.events:
            first_event = min(self.events, key=lambda e: e.timestamp)
            last_event = max(self.events, key=lambda e: e.timestamp)
            time_range = {
                "first_event": first_event.timestamp.isoformat(),
                "last_event": last_event.timestamp.isoformat(),
            }
        else:
            time_range = None
        
        return {
            "total_events": len(self.events),
            "event_counts": event_counts,
            "source_counts": source_counts,
            "explained_rules": explained_rules,
            "time_range": time_range,
        }
    
    def clear_old_events(self, days: int = 30) -> int:
        """
        Clear events older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of events cleared
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        original_count = len(self.events)
        
        self.events = [e for e in self.events if e.timestamp >= cutoff]
        cleared = original_count - len(self.events)
        
        if cleared > 0:
            self._save()
            logger.info(f"Cleared {cleared} old events")
        
        return cleared
    
    def export_audit_log(self, output_path: str) -> int:
        """
        Export audit log to JSON file.
        
        Args:
            output_path: Path to output file
            
        Returns:
            Number of events exported
        """
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_events": len(self.events),
            "events": [e.to_dict() for e in self.events],
            "explanations": {
                k: v.to_dict() for k, v in self.explanations.items()
            },
            "statistics": self.get_statistics(),
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return len(self.events)
