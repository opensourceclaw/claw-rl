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
Tests for Observability Module (v2.1.0)
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile

from claw_rl.observability.metrics import (
    LearningMetricsCollector,
    LearningMetricsExporter,
    get_collector,
    get_exporter,
)
from claw_rl.observability.rule_evolution import (
    RuleEvolutionTracker,
    RuleChangeEvent,
    RuleSnapshot,
    RuleChangeType,
)


class TestLearningMetricsCollector:
    """Tests for LearningMetricsCollector"""
    
    def test_init(self):
        """Test initialization"""
        collector = LearningMetricsCollector()
        
        assert collector.total_rewards == 0.0
        assert collector.positive_rewards == 0
        assert collector.total_hints == 0
    
    def test_record_reward(self):
        """Test recording rewards"""
        collector = LearningMetricsCollector()
        
        collector.record_reward(1.0)
        collector.record_reward(0.0)
        collector.record_reward(-1.0)
        collector.record_reward(1.0)
        
        assert collector.total_rewards == 1.0
        assert collector.positive_rewards == 2
        assert collector.negative_rewards == 1
        assert collector.neutral_rewards == 1
        assert collector.binary_rl_evaluations == 4
    
    def test_record_hint(self):
        """Test recording hints"""
        collector = LearningMetricsCollector()
        
        collector.record_hint("opd")
        collector.record_hint("opd")
        collector.record_hint("other")
        
        assert collector.total_hints == 3
        assert collector.opd_hints == 2
    
    def test_record_rule_change(self):
        """Test recording rule changes"""
        collector = LearningMetricsCollector()
        
        collector.record_rule_change("add")
        collector.record_rule_change("add")
        collector.record_rule_change("merge")
        collector.record_rule_change("evolve")
        
        assert collector.rules_added == 2
        assert collector.rules_merged == 1
        assert collector.rules_evolved == 1
        assert collector.active_rules == 2
    
    def test_record_llm_call(self):
        """Test recording LLM calls"""
        collector = LearningMetricsCollector()
        
        collector.record_llm_call()
        collector.record_llm_call(cache_hit=True)
        collector.record_llm_call(fallback=True)
        
        assert collector.llm_calls == 3
        assert collector.llm_cache_hits == 1
        assert collector.llm_fallbacks == 1
    
    def test_record_latency(self):
        """Test recording latency"""
        collector = LearningMetricsCollector()
        
        collector.record_latency(10.0)
        collector.record_latency(20.0)
        collector.record_latency(30.0)
        
        # Should be exponential moving average
        assert collector.avg_latency_ms > 0
        assert collector.avg_latency_ms < 30.0
    
    def test_record_mab_selection(self):
        """Test recording MAB selections"""
        collector = LearningMetricsCollector()
        
        collector.record_mab_selection()
        collector.record_mab_selection(strategy_switch=True)
        collector.record_mab_selection()
        
        assert collector.strategy_selections == 3
        assert collector.strategy_switches == 1
    
    def test_get_all_metrics(self):
        """Test getting all metrics"""
        collector = LearningMetricsCollector()
        collector.record_reward(1.0)
        collector.record_hint("opd")
        
        metrics = collector.get_all_metrics()
        
        assert 'rewards' in metrics
        assert 'hints' in metrics
        assert 'rules' in metrics
        assert 'performance' in metrics
        assert 'mab' in metrics
        assert 'timestamp' in metrics
        
        assert metrics['rewards']['positive'] == 1
        assert metrics['hints']['total'] == 1


class TestLearningMetricsExporter:
    """Tests for LearningMetricsExporter"""
    
    def test_init(self):
        """Test initialization"""
        exporter = LearningMetricsExporter()
        
        assert exporter.collector is not None
    
    def test_export_prometheus(self):
        """Test Prometheus export"""
        collector = LearningMetricsCollector()
        collector.record_reward(1.0)
        collector.record_reward(-1.0)
        collector.record_hint("opd")
        collector.record_rule_change("add")
        
        exporter = LearningMetricsExporter(collector)
        prometheus = exporter.export_prometheus()
        
        assert "# HELP clawrl_rewards_total" in prometheus
        assert "# TYPE clawrl_rewards_total counter" in prometheus
        assert "clawrl_rewards_total{type=\"positive\"} 1" in prometheus
        assert "clawrl_hints_total 1" in prometheus
        assert "clawrl_rules_active 1" in prometheus
    
    def test_export_json(self):
        """Test JSON export"""
        collector = LearningMetricsCollector()
        collector.record_reward(1.0)
        
        exporter = LearningMetricsExporter(collector)
        json_str = exporter.export_json()
        
        assert '"rewards"' in json_str
        assert '"positive": 1' in json_str
    
    def test_export_markdown(self):
        """Test Markdown export"""
        collector = LearningMetricsCollector()
        collector.record_reward(1.0)
        collector.record_hint("opd")
        
        exporter = LearningMetricsExporter(collector)
        markdown = exporter.export_markdown()
        
        assert "# Learning Metrics Report" in markdown
        assert "## 📊 Rewards" in markdown
        assert "## 💡 Hints" in markdown
    
    def test_export_to_file(self):
        """Test file export"""
        collector = LearningMetricsCollector()
        collector.record_reward(1.0)
        
        exporter = LearningMetricsExporter(collector)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "metrics.json"
            exporter.export_to_file(path, format="json")
            
            assert path.exists()
            content = path.read_text()
            assert '"rewards"' in content


class TestRuleSnapshot:
    """Tests for RuleSnapshot"""
    
    def test_init(self):
        """Test initialization"""
        snapshot = RuleSnapshot(
            rule_id="rule-001",
            pattern="操作前检查路径",
            confidence=0.85,
            source="user_feedback",
            timestamp=datetime.now()
        )
        
        assert snapshot.rule_id == "rule-001"
        assert snapshot.confidence == 0.85
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        snapshot = RuleSnapshot(
            rule_id="rule-001",
            pattern="test pattern",
            confidence=0.8,
            source="test",
            timestamp=datetime.now()
        )
        
        d = snapshot.to_dict()
        
        assert d['rule_id'] == "rule-001"
        assert d['pattern'] == "test pattern"
        assert d['confidence'] == 0.8
    
    def test_from_dict(self):
        """Test creation from dictionary"""
        d = {
            'rule_id': 'rule-001',
            'pattern': 'test',
            'confidence': 0.9,
            'source': 'test',
            'timestamp': datetime.now().isoformat(),
            'feedback_count': 5,
        }
        
        snapshot = RuleSnapshot.from_dict(d)
        
        assert snapshot.rule_id == "rule-001"
        assert snapshot.feedback_count == 5


class TestRuleChangeEvent:
    """Tests for RuleChangeEvent"""
    
    def test_init(self):
        """Test initialization"""
        event = RuleChangeEvent(
            event_id="event-001",
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            before=None,
            after=RuleSnapshot(
                rule_id="rule-001",
                pattern="test",
                confidence=0.8,
                source="test",
                timestamp=datetime.now()
            ),
            timestamp=datetime.now(),
            reason="Test event"
        )
        
        assert event.event_id == "event-001"
        assert event.change_type == RuleChangeType.CREATED
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        event = RuleChangeEvent(
            event_id="event-001",
            rule_id="rule-001",
            change_type=RuleChangeType.UPDATED,
            before=None,
            after=None,
            timestamp=datetime.now(),
            reason="Test"
        )
        
        d = event.to_dict()
        
        assert d['event_id'] == "event-001"
        assert d['change_type'] == "updated"


class TestRuleEvolutionTracker:
    """Tests for RuleEvolutionTracker"""
    
    def test_init(self):
        """Test initialization"""
        tracker = RuleEvolutionTracker()
        
        assert len(tracker.events) == 0
        assert len(tracker.rule_snapshots) == 0
    
    def test_record_change(self):
        """Test recording a change"""
        tracker = RuleEvolutionTracker()
        
        snapshot = RuleSnapshot(
            rule_id="rule-001",
            pattern="操作前检查路径",
            confidence=0.65,
            source="user_feedback",
            timestamp=datetime.now()
        )
        
        event = tracker.record_change(
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            after=snapshot,
            reason="New rule from feedback"
        )
        
        assert len(tracker.events) == 1
        assert event.rule_id == "rule-001"
        assert event.change_type == RuleChangeType.CREATED
        assert "rule-001" in tracker.rule_snapshots
    
    def test_record_feedback(self):
        """Test recording feedback"""
        tracker = RuleEvolutionTracker()
        
        # First create a rule
        tracker.record_change(
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-001",
                pattern="test pattern",
                confidence=0.65,
                source="user",
                timestamp=datetime.now()
            )
        )
        
        # Record positive feedback
        event = tracker.record_feedback("rule-001", is_positive=True, new_confidence=0.75)
        
        assert event is not None
        assert event.change_type == RuleChangeType.UPDATED
        assert event.after.confidence == 0.75
        assert event.after.positive_count == 1
    
    def test_record_merge(self):
        """Test recording merge"""
        tracker = RuleEvolutionTracker()
        
        event = tracker.record_merge(
            source_rules=["rule-001", "rule-002"],
            target_rule_id="rule-003",
            target_pattern="merged pattern",
            confidence=0.8
        )
        
        assert event.change_type == RuleChangeType.MERGED
        assert event.rule_id == "rule-003"
        assert len(event.related_rules) == 2
    
    def test_get_timeline(self):
        """Test getting timeline"""
        tracker = RuleEvolutionTracker()
        
        tracker.record_change(
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-001",
                pattern="test",
                confidence=0.5,
                source="test",
                timestamp=datetime.now()
            )
        )
        
        tracker.record_change(
            rule_id="rule-002",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-002",
                pattern="test2",
                confidence=0.6,
                source="test",
                timestamp=datetime.now()
            )
        )
        
        timeline = tracker.get_timeline()
        
        assert len(timeline) == 2
    
    def test_get_timeline_filtered(self):
        """Test getting filtered timeline"""
        tracker = RuleEvolutionTracker()
        
        tracker.record_change(
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-001",
                pattern="test",
                confidence=0.5,
                source="test",
                timestamp=datetime.now()
            )
        )
        
        tracker.record_change(
            rule_id="rule-002",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-002",
                pattern="test2",
                confidence=0.6,
                source="test",
                timestamp=datetime.now()
            )
        )
        
        timeline = tracker.get_timeline(rule_id="rule-001")
        
        assert len(timeline) == 1
        assert timeline[0]['rule_id'] == "rule-001"
    
    def test_get_rule_history(self):
        """Test getting rule history"""
        tracker = RuleEvolutionTracker()
        
        tracker.record_change(
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-001",
                pattern="test",
                confidence=0.5,
                source="test",
                timestamp=datetime.now()
            )
        )
        
        history = tracker.get_rule_history("rule-001")
        
        assert len(history) == 1
        assert history[0]['confidence'] == 0.5
    
    def test_get_evolution_summary(self):
        """Test getting evolution summary"""
        tracker = RuleEvolutionTracker()
        
        tracker.record_change(
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-001",
                pattern="test",
                confidence=0.5,
                source="test",
                timestamp=datetime.now()
            )
        )
        
        summary = tracker.get_evolution_summary()
        
        assert summary['total_events'] == 1
        assert summary['total_rules'] == 1
        assert summary['change_counts']['created'] == 1
    
    def test_export_markdown_timeline(self):
        """Test exporting Markdown timeline"""
        tracker = RuleEvolutionTracker()
        
        tracker.record_change(
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-001",
                pattern="test pattern",
                confidence=0.65,
                source="user",
                timestamp=datetime.now()
            ),
            reason="New rule"
        )
        
        markdown = tracker.export_markdown_timeline()
        
        assert "# Rule Evolution Timeline" in markdown
        assert "rule-001" in markdown
        assert "created" in markdown
    
    def test_export_to_file(self):
        """Test exporting to file"""
        tracker = RuleEvolutionTracker()
        
        tracker.record_change(
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-001",
                pattern="test",
                confidence=0.5,
                source="test",
                timestamp=datetime.now()
            )
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "evolution.json"
            tracker.export_to_file(path)
            
            assert path.exists()
            content = path.read_text()
            assert '"events"' in content
    
    def test_clear(self):
        """Test clearing history"""
        tracker = RuleEvolutionTracker()
        
        tracker.record_change(
            rule_id="rule-001",
            change_type=RuleChangeType.CREATED,
            after=RuleSnapshot(
                rule_id="rule-001",
                pattern="test",
                confidence=0.5,
                source="test",
                timestamp=datetime.now()
            )
        )
        
        tracker.clear()
        
        assert len(tracker.events) == 0
        assert len(tracker.rule_snapshots) == 0


class TestGlobalFunctions:
    """Tests for global functions"""
    
    def test_get_collector(self):
        """Test getting global collector"""
        collector1 = get_collector()
        collector2 = get_collector()
        
        assert collector1 is collector2
    
    def test_get_exporter(self):
        """Test getting global exporter"""
        exporter1 = get_exporter()
        exporter2 = get_exporter()
        
        assert exporter1.collector is exporter2.collector
