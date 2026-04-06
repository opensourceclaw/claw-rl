"""
Tests for Knowledge Base
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import json

from claw_rl.learning.knowledge_base import (
    KnowledgeBase,
    LearningRule,
    RuleStatus,
    RulePriority,
    RuleConflictStrategy,
)


class TestLearningRule:
    """Tests for LearningRule."""
    
    def test_create_rule(self):
        """Test creating a learning rule."""
        rule = LearningRule(
            rule_id="rule_001",
            name="Test Rule",
            description="A test rule",
        )
        
        assert rule.rule_id == "rule_001"
        assert rule.name == "Test Rule"
        assert rule.status == RuleStatus.ACTIVE
        assert rule.priority == RulePriority.MEDIUM
    
    def test_rule_to_dict(self):
        """Test converting rule to dict."""
        rule = LearningRule(
            rule_id="rule_002",
            name="Dict Rule",
            condition={"context": "chat"},
            action={"style": "concise"},
            tags=["test", "chat"],
        )
        
        result = rule.to_dict()
        
        assert result["rule_id"] == "rule_002"
        assert result["name"] == "Dict Rule"
        assert result["condition"] == {"context": "chat"}
        assert result["tags"] == ["test", "chat"]
    
    def test_rule_from_dict(self):
        """Test creating rule from dict."""
        data = {
            "rule_id": "rule_003",
            "name": "From Dict",
            "priority": 1,
            "status": "deprecated",
            "confidence": 0.8,
            "usage_count": 10,
            "success_count": 8,
        }
        
        rule = LearningRule.from_dict(data)
        
        assert rule.rule_id == "rule_003"
        assert rule.name == "From Dict"
        assert rule.priority == RulePriority.CRITICAL
        assert rule.status == RuleStatus.DEPRECATED
        assert rule.confidence == 0.8
    
    def test_success_rate(self):
        """Test success rate calculation."""
        rule = LearningRule(
            rule_id="rule_004",
            name="Rate Test",
            usage_count=10,
            success_count=7,
        )
        
        assert rule.success_rate == 0.7
    
    def test_success_rate_zero_usage(self):
        """Test success rate with zero usage."""
        rule = LearningRule(
            rule_id="rule_005",
            name="No Usage",
        )
        
        assert rule.success_rate == 0.0
    
    def test_is_expired(self):
        """Test expiration check."""
        # Not expired
        rule1 = LearningRule(
            rule_id="rule_006",
            name="Not Expired",
        )
        assert not rule1.is_expired
        
        # Expired
        past_time = (datetime.now() - timedelta(days=1)).isoformat()
        rule2 = LearningRule(
            rule_id="rule_007",
            name="Expired",
            expires_at=past_time,
        )
        assert rule2.is_expired
        
        # Future expiration
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        rule3 = LearningRule(
            rule_id="rule_008",
            name="Future Expiration",
            expires_at=future_time,
        )
        assert not rule3.is_expired
    
    def test_update_usage(self):
        """Test updating usage statistics."""
        rule = LearningRule(
            rule_id="rule_009",
            name="Usage Test",
            usage_count=5,
            success_count=3,
        )
        
        rule.update_usage(success=True)
        
        assert rule.usage_count == 6
        assert rule.success_count == 4


class TestKnowledgeBase:
    """Tests for KnowledgeBase."""
    
    @pytest.fixture
    def kb(self):
        """Create a knowledge base with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield KnowledgeBase(data_dir=Path(tmpdir))
    
    def test_create_kb(self):
        """Test creating a knowledge base."""
        with tempfile.TemporaryDirectory() as tmpdir:
            kb = KnowledgeBase(data_dir=Path(tmpdir))
            assert len(kb) == 0
    
    def test_add_rule(self, kb):
        """Test adding a rule."""
        rule = LearningRule(
            rule_id="rule_001",
            name="Test Rule",
            tags=["test"],
        )
        
        result = kb.add_rule(rule)
        
        assert result is True
        assert len(kb) == 1
        assert kb.get_rule("rule_001") == rule
    
    def test_add_duplicate_rule(self, kb):
        """Test adding a duplicate rule."""
        rule = LearningRule(rule_id="rule_001", name="Test")
        
        kb.add_rule(rule)
        result = kb.add_rule(rule)
        
        assert result is False
        assert len(kb) == 1
    
    def test_update_rule(self, kb):
        """Test updating a rule."""
        rule = LearningRule(
            rule_id="rule_001",
            name="Original",
        )
        kb.add_rule(rule)
        
        rule.name = "Updated"
        result = kb.update_rule(rule)
        
        assert result is True
        assert kb.get_rule("rule_001").name == "Updated"
    
    def test_update_nonexistent_rule(self, kb):
        """Test updating a non-existent rule."""
        rule = LearningRule(rule_id="rule_999", name="Ghost")
        result = kb.update_rule(rule)
        
        assert result is False
    
    def test_delete_rule(self, kb):
        """Test deleting a rule."""
        rule = LearningRule(rule_id="rule_001", name="Test")
        kb.add_rule(rule)
        
        result = kb.delete_rule("rule_001")
        
        assert result is True
        assert len(kb) == 0
        assert kb.get_rule("rule_001") is None
    
    def test_delete_nonexistent_rule(self, kb):
        """Test deleting a non-existent rule."""
        result = kb.delete_rule("rule_999")
        assert result is False
    
    def test_find_rules_by_status(self, kb):
        """Test finding rules by status."""
        kb.add_rule(LearningRule(rule_id="rule_001", name="Active", status=RuleStatus.ACTIVE))
        kb.add_rule(LearningRule(rule_id="rule_002", name="Deprecated", status=RuleStatus.DEPRECATED))
        kb.add_rule(LearningRule(rule_id="rule_003", name="Active2", status=RuleStatus.ACTIVE))
        
        results = kb.find_rules(status=RuleStatus.ACTIVE)
        
        assert len(results) == 2
        assert all(r.status == RuleStatus.ACTIVE for r in results)
    
    def test_find_rules_by_tags(self, kb):
        """Test finding rules by tags."""
        kb.add_rule(LearningRule(rule_id="rule_001", name="Test1", tags=["chat", "general"]))
        kb.add_rule(LearningRule(rule_id="rule_002", name="Test2", tags=["code", "python"]))
        kb.add_rule(LearningRule(rule_id="rule_003", name="Test3", tags=["chat", "special"]))
        
        results = kb.find_rules(tags=["chat"])
        
        assert len(results) == 2
    
    def test_find_rules_by_condition(self, kb):
        """Test finding rules by condition."""
        kb.add_rule(LearningRule(
            rule_id="rule_001",
            name="Chat Rule",
            condition={"context": "chat", "mode": "casual"},
        ))
        kb.add_rule(LearningRule(
            rule_id="rule_002",
            name="Code Rule",
            condition={"context": "code", "language": "python"},
        ))
        
        results = kb.find_rules(condition={"context": "chat"})
        
        assert len(results) == 1
        assert results[0].rule_id == "rule_001"
    
    def test_find_rules_min_confidence(self, kb):
        """Test finding rules with minimum confidence."""
        kb.add_rule(LearningRule(rule_id="rule_001", name="High", confidence=0.9))
        kb.add_rule(LearningRule(rule_id="rule_002", name="Medium", confidence=0.6))
        kb.add_rule(LearningRule(rule_id="rule_003", name="Low", confidence=0.3))
        
        results = kb.find_rules(min_confidence=0.5)
        
        assert len(results) == 2
        assert all(r.confidence >= 0.5 for r in results)
    
    def test_find_rules_limit(self, kb):
        """Test finding rules with limit."""
        for i in range(10):
            kb.add_rule(LearningRule(rule_id=f"rule_{i:03d}", name=f"Rule {i}"))
        
        results = kb.find_rules(limit=5)
        
        assert len(results) == 5
    
    def test_resolve_conflicts_highest_priority(self, kb):
        """Test resolving conflicts with highest priority strategy."""
        kb.conflict_strategy = RuleConflictStrategy.HIGHEST_PRIORITY
        
        rules = [
            LearningRule(rule_id="rule_001", name="Low", priority=RulePriority.LOW),
            LearningRule(rule_id="rule_002", name="Critical", priority=RulePriority.CRITICAL),
            LearningRule(rule_id="rule_003", name="High", priority=RulePriority.HIGH),
        ]
        
        winner = kb.resolve_conflicts(rules)
        
        assert winner.rule_id == "rule_002"
        assert winner.priority == RulePriority.CRITICAL
    
    def test_resolve_conflicts_newest_wins(self, kb):
        """Test resolving conflicts with newest wins strategy."""
        kb.conflict_strategy = RuleConflictStrategy.NEWEST_WINS
        
        now = datetime.now()
        rules = [
            LearningRule(rule_id="rule_001", name="Old", updated_at=(now - timedelta(days=2)).isoformat()),
            LearningRule(rule_id="rule_002", name="New", updated_at=(now - timedelta(hours=1)).isoformat()),
            LearningRule(rule_id="rule_003", name="Middle", updated_at=(now - timedelta(days=1)).isoformat()),
        ]
        
        winner = kb.resolve_conflicts(rules)
        
        assert winner.rule_id == "rule_002"
    
    def test_resolve_conflicts_single_rule(self, kb):
        """Test resolving conflicts with single rule."""
        rule = LearningRule(rule_id="rule_001", name="Solo")
        winner = kb.resolve_conflicts([rule])
        assert winner == rule
    
    def test_get_statistics(self, kb):
        """Test getting statistics."""
        kb.add_rule(LearningRule(
            rule_id="rule_001",
            name="Active",
            status=RuleStatus.ACTIVE,
            usage_count=10,
            success_count=8,
            confidence=0.9,
        ))
        kb.add_rule(LearningRule(
            rule_id="rule_002",
            name="Deprecated",
            status=RuleStatus.DEPRECATED,
            usage_count=5,
            success_count=2,
            confidence=0.5,
        ))
        
        stats = kb.get_statistics()
        
        assert stats["total_rules"] == 2
        assert stats["active_rules"] == 1
        assert stats["deprecated_rules"] == 1
        assert stats["total_usage"] == 15
        assert stats["total_success"] == 10
        assert 0.66 < stats["overall_success_rate"] < 0.67
    
    def test_prune_expired_rules(self, kb):
        """Test pruning expired rules."""
        past = (datetime.now() - timedelta(days=1)).isoformat()
        future = (datetime.now() + timedelta(days=1)).isoformat()
        
        kb.add_rule(LearningRule(rule_id="rule_001", name="Expired", expires_at=past))
        kb.add_rule(LearningRule(rule_id="rule_002", name="Active", expires_at=future))
        kb.add_rule(LearningRule(rule_id="rule_003", name="No Expiry"))
        
        removed = kb.prune_expired_rules()
        
        assert removed == 1
        assert len(kb) == 2
        assert kb.get_rule("rule_001") is None
    
    def test_deprecate_low_performing_rules(self, kb):
        """Test deprecating low performing rules."""
        kb.add_rule(LearningRule(
            rule_id="rule_001",
            name="Low Performance",
            usage_count=15,
            success_count=3,  # 20% success rate
        ))
        kb.add_rule(LearningRule(
            rule_id="rule_002",
            name="High Performance",
            usage_count=20,
            success_count=16,  # 80% success rate
        ))
        kb.add_rule(LearningRule(
            rule_id="rule_003",
            name="Low Usage",
            usage_count=5,
            success_count=1,
        ))
        
        deprecated = kb.deprecate_low_performing_rules(
            min_usage=10,
            min_success_rate=0.3,
        )
        
        assert deprecated == 1
        assert kb.get_rule("rule_001").status == RuleStatus.DEPRECATED
        assert kb.get_rule("rule_002").status == RuleStatus.ACTIVE
    
    def test_persistence(self):
        """Test rule persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            
            # Create and save rule
            kb1 = KnowledgeBase(data_dir=data_dir)
            kb1.add_rule(LearningRule(
                rule_id="rule_001",
                name="Persistent",
                tags=["test"],
            ))
            
            # Load in new instance
            kb2 = KnowledgeBase(data_dir=data_dir)
            
            assert len(kb2) == 1
            assert kb2.get_rule("rule_001").name == "Persistent"
    
    def test_max_rules_limit(self):
        """Test max rules limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            kb = KnowledgeBase(data_dir=Path(tmpdir), max_rules=3)
            
            for i in range(5):
                rule = LearningRule(rule_id=f"rule_{i:03d}", name=f"Rule {i}")
                kb.add_rule(rule)
            
            # Should have at most 3 rules
            assert len(kb) <= 3
    
    def test_contains(self, kb):
        """Test __contains__ method."""
        kb.add_rule(LearningRule(rule_id="rule_001", name="Test"))
        
        assert "rule_001" in kb
        assert "rule_999" not in kb
    
    def test_repr(self, kb):
        """Test string representation."""
        kb.add_rule(LearningRule(rule_id="rule_001", name="Test", tags=["chat"]))
        
        result = repr(kb)
        
        assert "KnowledgeBase" in result
        assert "rules=1" in result
