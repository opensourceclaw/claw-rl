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
Tests for Learning Audit Module
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from claw_rl.learning_audit import (
    LearningAudit,
    LearningEvent,
    LearningEventType,
    AuditLevel,
    RuleExplanation,
)


class TestLearningEvent:
    """Tests for LearningEvent"""
    
    def test_create_event(self):
        """Test creating an event"""
        event = LearningEvent(
            event_id="evt_00000001",
            event_type=LearningEventType.RULE_CREATED,
            timestamp=datetime.now(),
            level=AuditLevel.INFO,
            message="Rule created from feedback",
        )
        
        assert event.event_id == "evt_00000001"
        assert event.event_type == LearningEventType.RULE_CREATED
        assert event.message == "Rule created from feedback"
    
    def test_event_to_dict(self):
        """Test event serialization"""
        event = LearningEvent(
            event_id="evt_00000002",
            event_type=LearningEventType.FEEDBACK_POSITIVE,
            timestamp=datetime(2026, 4, 8, 0, 15, 0),
            level=AuditLevel.INFO,
            message="Positive feedback received",
            source="user",
            rule_id="rule_001",
        )
        
        data = event.to_dict()
        
        assert data["event_id"] == "evt_00000002"
        assert data["event_type"] == "feedback_positive"
        assert data["rule_id"] == "rule_001"
    
    def test_event_from_dict(self):
        """Test event deserialization"""
        data = {
            "event_id": "evt_00000003",
            "event_type": "strategy_selected",
            "timestamp": "2026-04-08T00:15:00",
            "level": "info",
            "message": "Strategy selected",
            "source": "mab",
            "context": {"strategy": "thompson_sampling"},
        }
        
        event = LearningEvent.from_dict(data)
        
        assert event.event_id == "evt_00000003"
        assert event.event_type == LearningEventType.STRATEGY_SELECTED
        assert event.context["strategy"] == "thompson_sampling"


class TestRuleExplanation:
    """Tests for RuleExplanation"""
    
    def test_create_explanation(self):
        """Test creating an explanation"""
        explanation = RuleExplanation(
            rule_id="rule_001",
            explanation="This rule was created from positive feedback",
            feedback_count=5,
        )
        
        assert explanation.rule_id == "rule_001"
        assert explanation.feedback_count == 5
    
    def test_explanation_to_dict(self):
        """Test explanation serialization"""
        explanation = RuleExplanation(
            rule_id="rule_002",
            explanation="Rule from OPD extraction",
            source_events=["evt_001", "evt_002"],
            feedback_count=3,
            confidence_history=[0.5, 0.6, 0.7],
        )
        
        data = explanation.to_dict()
        
        assert data["rule_id"] == "rule_002"
        assert len(data["source_events"]) == 2
        assert len(data["confidence_history"]) == 3
    
    def test_explanation_from_dict(self):
        """Test explanation deserialization"""
        data = {
            "rule_id": "rule_003",
            "explanation": "Test explanation",
            "source_events": ["evt_003"],
            "feedback_count": 2,
            "confidence_history": [0.8],
            "created_at": "2026-04-08T00:15:00",
            "last_updated": "2026-04-08T00:20:00",
        }
        
        explanation = RuleExplanation.from_dict(data)
        
        assert explanation.rule_id == "rule_003"
        assert explanation.feedback_count == 2


class TestLearningAudit:
    """Tests for LearningAudit"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def audit(self, temp_workspace):
        """Create LearningAudit instance"""
        return LearningAudit(temp_workspace)
    
    def test_log_event(self, audit):
        """Test logging an event"""
        event = audit.log_event(
            event_type=LearningEventType.RULE_CREATED,
            message="Test rule created",
            level=AuditLevel.INFO,
        )
        
        assert event.event_id.startswith("evt_")
        assert event.message == "Test rule created"
        assert len(audit.events) == 1
    
    def test_log_event_with_context(self, audit):
        """Test logging event with context"""
        event = audit.log_event(
            event_type=LearningEventType.FEEDBACK_POSITIVE,
            message="Positive feedback",
            source="user",
            rule_id="rule_001",
            feedback_id="fb_001",
            context={"score": 0.9},
        )
        
        assert event.source == "user"
        assert event.rule_id == "rule_001"
        assert event.feedback_id == "fb_001"
        assert event.context["score"] == 0.9
    
    def test_get_events_by_type(self, audit):
        """Test getting events by type"""
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 1")
        audit.log_event(LearningEventType.RULE_UPDATED, "Rule 2")
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 3")
        
        events = audit.get_events(event_type=LearningEventType.RULE_CREATED)
        
        assert len(events) == 2
    
    def test_get_events_by_source(self, audit):
        """Test getting events by source"""
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 1", source="feedback")
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 2", source="opd")
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 3", source="feedback")
        
        events = audit.get_events(source="feedback")
        
        assert len(events) == 2
    
    def test_get_events_by_rule_id(self, audit):
        """Test getting events by rule ID"""
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 1", rule_id="rule_001")
        audit.log_event(LearningEventType.RULE_UPDATED, "Rule 1 updated", rule_id="rule_001")
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 2", rule_id="rule_002")
        
        events = audit.get_rule_history("rule_001")
        
        assert len(events) == 2
    
    def test_create_explanation(self, audit):
        """Test creating an explanation"""
        explanation = audit.create_explanation(
            rule_id="rule_001",
            explanation="This rule was created from user feedback",
            source_events=["evt_001", "evt_002"],
            feedback_count=3,
        )
        
        assert explanation.rule_id == "rule_001"
        assert explanation.feedback_count == 3
        assert "rule_001" in audit.explanations
    
    def test_get_explanation(self, audit):
        """Test getting an explanation"""
        audit.create_explanation(
            rule_id="rule_002",
            explanation="Test explanation",
        )
        
        explanation = audit.explain_rule("rule_002")
        
        assert explanation is not None
        assert explanation.explanation == "Test explanation"
    
    def test_update_explanation(self, audit):
        """Test updating an explanation"""
        audit.create_explanation(
            rule_id="rule_003",
            explanation="Initial explanation",
            feedback_count=1,
        )
        
        updated = audit.update_explanation(
            rule_id="rule_003",
            explanation="Updated explanation",
            feedback_count=5,
        )
        
        assert updated is not None
        assert updated.explanation == "Updated explanation"
        assert updated.feedback_count == 5
    
    def test_get_feedback_sources(self, audit):
        """Test getting feedback sources"""
        audit.log_event(
            LearningEventType.FEEDBACK_POSITIVE,
            "Feedback 1",
            rule_id="rule_001",
            feedback_id="fb_001",
        )
        audit.log_event(
            LearningEventType.FEEDBACK_NEGATIVE,
            "Feedback 2",
            rule_id="rule_001",
            feedback_id="fb_002",
        )
        
        sources = audit.get_feedback_sources("rule_001")
        
        assert len(sources) == 2
        assert "fb_001" in sources
        assert "fb_002" in sources
    
    def test_get_statistics(self, audit):
        """Test getting statistics"""
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 1", source="feedback")
        audit.log_event(LearningEventType.RULE_UPDATED, "Rule 1", source="feedback")
        audit.log_event(LearningEventType.STRATEGY_SELECTED, "Strategy 1", source="mab")
        
        stats = audit.get_statistics()
        
        assert stats["total_events"] == 3
        assert "rule_created" in stats["event_counts"]
        assert "feedback" in stats["source_counts"]
    
    def test_persistence(self, temp_workspace):
        """Test audit log persistence"""
        # Create audit and log events
        audit1 = LearningAudit(temp_workspace)
        audit1.log_event(LearningEventType.RULE_CREATED, "Rule 1")
        audit1.log_event(LearningEventType.RULE_UPDATED, "Rule 1 updated")
        audit1.create_explanation("rule_001", "Test explanation")
        
        # Create new audit instance (should load from disk)
        audit2 = LearningAudit(temp_workspace)
        
        assert len(audit2.events) == 2
        assert "rule_001" in audit2.explanations
    
    def test_clear_old_events(self, audit):
        """Test clearing old events"""
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 1")
        audit.log_event(LearningEventType.RULE_UPDATED, "Rule 1 updated")
        
        cleared = audit.clear_old_events(days=0)  # Clear all
        
        assert cleared == 2
        assert len(audit.events) == 0
    
    def test_export_audit_log(self, audit, temp_workspace):
        """Test exporting audit log"""
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 1")
        audit.log_event(LearningEventType.RULE_UPDATED, "Rule 1 updated")
        
        output_path = str(temp_workspace / "audit_export.json")
        count = audit.export_audit_log(output_path)
        
        assert count == 2
        assert Path(output_path).exists()
    
    def test_event_levels(self, audit):
        """Test different event levels"""
        audit.log_event(LearningEventType.INFO, "Info", level=AuditLevel.INFO)
        audit.log_event(LearningEventType.WARNING, "Warning", level=AuditLevel.WARNING)
        audit.log_event(LearningEventType.ERROR, "Error", level=AuditLevel.ERROR)
        
        events = audit.get_events(limit=10)
        
        assert len(events) == 3
        levels = [e.level for e in events]
        assert AuditLevel.INFO in levels
        assert AuditLevel.WARNING in levels
        assert AuditLevel.ERROR in levels
    
    def test_time_filter(self, audit):
        """Test time-based filtering"""
        now = datetime.now()
        
        audit.log_event(LearningEventType.RULE_CREATED, "Rule 1")
        audit.log_event(LearningEventType.RULE_UPDATED, "Rule 2")
        
        # Get events from last hour
        events = audit.get_events(
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
        )
        
        assert len(events) == 2


class TestLearningEventType:
    """Tests for LearningEventType"""
    
    def test_event_types(self):
        """Test all event types exist"""
        assert LearningEventType.FEEDBACK_RECEIVED.value == "feedback_received"
        assert LearningEventType.RULE_CREATED.value == "rule_created"
        assert LearningEventType.STRATEGY_SELECTED.value == "strategy_selected"
        assert LearningEventType.OPD_EXTRACTED.value == "opd_extracted"
        assert LearningEventType.ERROR.value == "error"


class TestAuditLevel:
    """Tests for AuditLevel"""
    
    def test_audit_levels(self):
        """Test all audit levels exist"""
        assert AuditLevel.DEBUG.value == "debug"
        assert AuditLevel.INFO.value == "info"
        assert AuditLevel.WARNING.value == "warning"
        assert AuditLevel.ERROR.value == "error"
        assert AuditLevel.CRITICAL.value == "critical"
