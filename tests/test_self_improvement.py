"""
Tests for Self-Improvement
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import json

from claw_rl.learning.self_improvement import (
    SelfImprovement,
    RuleExtractor,
    RuleValidator,
    ExtractedRule,
    RuleExtractionStrategy,
    RuleValidationStatus,
    DeploymentResult,
)
from claw_rl.learning.knowledge_base import KnowledgeBase, LearningRule, RuleStatus


class TestExtractedRule:
    """Tests for ExtractedRule."""
    
    def test_create_extracted_rule(self):
        """Test creating an extracted rule."""
        rule = ExtractedRule(
            name="Test Rule",
            description="A test rule",
            condition={"context": "chat"},
            action={"style": "concise"},
            confidence=0.8,
            support=10,
        )
        
        assert rule.name == "Test Rule"
        assert rule.confidence == 0.8
        assert rule.support == 10
    
    def test_to_learning_rule(self):
        """Test converting to LearningRule."""
        extracted = ExtractedRule(
            name="Test",
            description="Test",
            condition={"x": 1},
            action={"y": 2},
            confidence=0.9,
            support=5,
            source_experiences=["exp_001", "exp_002"],
        )
        
        learning_rule = extracted.to_learning_rule("rule_001")
        
        assert learning_rule.rule_id == "rule_001"
        assert learning_rule.name == "Test"
        assert learning_rule.condition == {"x": 1}
        assert learning_rule.action == {"y": 2}
        assert learning_rule.confidence == 0.9
        assert learning_rule.status == RuleStatus.DRAFT
        assert learning_rule.metadata["support"] == 5


class TestRuleExtractor:
    """Tests for RuleExtractor."""
    
    @pytest.fixture
    def experiences(self):
        """Create sample experiences."""
        experiences = []
        for i in range(20):
            exp = {
                "experience_id": f"exp_{i:03d}",
                "state": {"context": "chat" if i < 15 else "code"},
                "action": {"style": "concise" if i < 15 else "detailed"},
                "reward": 1.0 if i < 15 else -0.5,
            }
            experiences.append(exp)
        return experiences
    
    def test_extract_frequency(self, experiences):
        """Test frequency-based extraction."""
        extractor = RuleExtractor(
            strategy=RuleExtractionStrategy.FREQUENCY,
            min_support=5,
            min_confidence=0.6,
        )
        
        rules = extractor.extract(experiences)
        
        # Should extract at least one rule
        assert len(rules) >= 1
        # All rules should have minimum support
        for rule in rules:
            assert rule.support >= 5
    
    def test_extract_success_rate(self, experiences):
        """Test success rate-based extraction."""
        extractor = RuleExtractor(
            strategy=RuleExtractionStrategy.SUCCESS_RATE,
            min_support=5,
            min_confidence=0.6,
        )
        
        rules = extractor.extract(experiences)
        
        assert len(rules) >= 1
        for rule in rules:
            assert rule.confidence >= 0.6
    
    def test_extract_reward(self, experiences):
        """Test reward-based extraction."""
        extractor = RuleExtractor(
            strategy=RuleExtractionStrategy.REWARD_BASED,
            min_support=5,
            min_confidence=0.3,
        )
        
        rules = extractor.extract(experiences)
        
        assert len(rules) >= 1
        for rule in rules:
            assert rule.support >= 5
    
    def test_extract_hybrid(self, experiences):
        """Test hybrid extraction."""
        extractor = RuleExtractor(
            strategy=RuleExtractionStrategy.HYBRID,
            min_support=5,
            min_confidence=0.5,
        )
        
        rules = extractor.extract(experiences)
        
        assert len(rules) >= 1
    
    def test_extract_insufficient_experiences(self):
        """Test extraction with insufficient experiences."""
        extractor = RuleExtractor(min_support=10)
        
        experiences = [
            {"experience_id": "exp_001", "state": {}, "action": {}, "reward": 1.0},
            {"experience_id": "exp_002", "state": {}, "action": {}, "reward": 1.0},
        ]
        
        rules = extractor.extract(experiences)
        
        assert len(rules) == 0
    
    def test_extract_low_confidence(self, experiences):
        """Test extraction with low confidence threshold."""
        extractor = RuleExtractor(
            min_support=5,
            min_confidence=0.99,  # Very high threshold
        )
        
        rules = extractor.extract(experiences)
        
        # Should have fewer rules due to high threshold
        # May be 0 if no pattern meets threshold
        assert isinstance(rules, list)


class TestRuleValidator:
    """Tests for RuleValidator."""
    
    def test_validate_high_quality_rule(self):
        """Test validating a high quality rule."""
        validator = RuleValidator()
        
        rule = ExtractedRule(
            name="High Quality",
            description="A high quality rule",
            condition={"context": "chat"},
            action={"style": "concise"},
            confidence=0.9,
            support=10,
        )
        
        result = validator.validate(rule)
        
        assert result.is_valid()
        assert result.status == RuleValidationStatus.VALID
    
    def test_validate_low_confidence(self):
        """Test validating low confidence rule."""
        validator = RuleValidator()
        
        rule = ExtractedRule(
            name="Low Confidence",
            description="Low confidence",
            condition={"x": 1},
            action={"y": 2},
            confidence=0.3,
            support=10,
        )
        
        result = validator.validate(rule)
        
        assert not result.is_valid()
        assert any("confidence" in issue.lower() for issue in result.issues)
    
    def test_validate_low_support(self):
        """Test validating low support rule."""
        validator = RuleValidator()
        
        rule = ExtractedRule(
            name="Low Support",
            description="Low support",
            condition={"x": 1},
            action={"y": 2},
            confidence=0.9,
            support=2,
        )
        
        result = validator.validate(rule)
        
        assert any("support" in issue.lower() for issue in result.issues)
    
    def test_validate_empty_condition(self):
        """Test validating rule with empty condition."""
        validator = RuleValidator()
        
        rule = ExtractedRule(
            name="Empty Condition",
            description="No condition",
            condition={},
            action={"y": 2},
            confidence=0.9,
            support=10,
        )
        
        result = validator.validate(rule)
        
        assert any("empty condition" in issue.lower() for issue in result.issues)
    
    def test_validate_with_knowledge_base(self):
        """Test validation with knowledge base conflict detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            kb = KnowledgeBase(data_dir=Path(tmpdir))
            
            # Add existing rule
            existing = LearningRule(
                rule_id="rule_001",
                name="Existing",
                condition={"context": "chat"},
                action={"style": "detailed"},
            )
            kb.add_rule(existing)
            
            validator = RuleValidator(knowledge_base=kb)
            
            # Create conflicting rule
            rule = ExtractedRule(
                name="Conflicting",
                description="Conflicts with existing",
                condition={"context": "chat"},
                action={"style": "concise"},  # Different action
                confidence=0.9,
                support=10,
            )
            
            result = validator.validate(rule)
            
            # Should detect conflict
            assert any("conflict" in issue.lower() for issue in result.issues)


class TestSelfImprovement:
    """Tests for SelfImprovement."""
    
    @pytest.fixture
    def kb(self):
        """Create a knowledge base."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield KnowledgeBase(data_dir=Path(tmpdir))
    
    @pytest.fixture
    def experiences(self):
        """Create sample experiences."""
        experiences = []
        for i in range(30):
            exp = {
                "experience_id": f"exp_{i:03d}",
                "state": {"context": "chat" if i < 20 else "code"},
                "action": {"style": "concise" if i < 20 else "detailed"},
                "reward": 1.0 if i < 20 else -0.5,
            }
            experiences.append(exp)
        return experiences
    
    def test_create_self_improvement(self, kb):
        """Test creating self-improvement."""
        si = SelfImprovement(knowledge_base=kb)
        
        assert si.knowledge_base == kb
        assert len(si._extraction_history) == 0
        assert len(si._deployment_history) == 0
    
    def test_extract_rules(self, kb, experiences):
        """Test extracting rules."""
        si = SelfImprovement(knowledge_base=kb, min_support=5)
        
        rules = si.extract_rules(experiences)
        
        assert len(rules) >= 1
        assert len(si._extraction_history) == 1
        assert si._extraction_history[0]["experience_count"] == 30
    
    def test_validate_rule(self, kb):
        """Test validating a rule."""
        si = SelfImprovement(knowledge_base=kb)
        
        rule = ExtractedRule(
            name="Test",
            description="Test",
            condition={"x": 1},
            action={"y": 2},
            confidence=0.9,
            support=10,
        )
        
        result = si.validate_rule(rule)
        
        assert result.is_valid()
    
    def test_deploy_rule(self, kb):
        """Test deploying a rule."""
        si = SelfImprovement(knowledge_base=kb)
        
        rule = ExtractedRule(
            name="Deploy Test",
            description="Test deployment",
            condition={"context": "chat"},
            action={"style": "concise"},
            confidence=0.9,
            support=10,
        )
        
        result = si.deploy_rule(rule)
        
        assert result.success
        assert result.rule_id.startswith("rule_")
        assert len(kb) == 1
    
    def test_deploy_invalid_rule(self, kb):
        """Test deploying an invalid rule."""
        si = SelfImprovement(knowledge_base=kb)
        
        rule = ExtractedRule(
            name="Invalid",
            description="Invalid rule",
            condition={},
            action={},
            confidence=0.1,
            support=1,
        )
        
        result = si.deploy_rule(rule, validate=True)
        
        assert not result.success
        assert len(kb) == 0
    
    def test_deploy_auto(self, kb, experiences):
        """Test auto deployment."""
        si = SelfImprovement(
            knowledge_base=kb,
            auto_deploy=True,
            min_support=5,
        )
        
        rules = si.extract_rules(experiences)
        
        # Deploy all rules
        for rule in rules:
            result = si.deploy_rule(rule, validate=True)
            # Should deploy despite validation issues if auto_deploy is True
        
    def test_monitor_effect(self, kb, experiences):
        """Test monitoring rule effect."""
        si = SelfImprovement(knowledge_base=kb)
        
        # Deploy a rule first
        rule = ExtractedRule(
            name="Monitor Test",
            description="Test monitoring",
            condition={"context": "chat"},
            action={"style": "concise"},
            confidence=0.9,
            support=10,
        )
        
        result = si.deploy_rule(rule)
        
        # Monitor effect
        metrics = si.monitor_effect(result.rule_id, experiences)
        
        assert "rule_id" in metrics
        assert "matching_experiences" in metrics
        assert metrics["matching_experiences"] > 0
    
    def test_monitor_nonexistent_rule(self, kb, experiences):
        """Test monitoring non-existent rule."""
        si = SelfImprovement(knowledge_base=kb)
        
        metrics = si.monitor_effect("nonexistent_rule", experiences)
        
        assert "error" in metrics
    
    def test_run_improvement_cycle(self, kb, experiences):
        """Test running complete improvement cycle."""
        si = SelfImprovement(
            knowledge_base=kb,
            min_support=5,
            min_confidence=0.5,
        )
        
        result = si.run_improvement_cycle(experiences)
        
        assert "experiences_processed" in result
        assert "rules_extracted" in result
        assert "rules_deployed" in result
        assert result["experiences_processed"] == 30
    
    def test_get_statistics(self, kb, experiences):
        """Test getting statistics."""
        si = SelfImprovement(knowledge_base=kb, min_support=5)
        
        # Run some operations
        si.extract_rules(experiences)
        rule = ExtractedRule(
            name="Stats Test",
            description="Test",
            condition={"x": 1},
            action={"y": 2},
            confidence=0.9,
            support=10,
        )
        si.deploy_rule(rule)
        
        stats = si.get_statistics()
        
        assert stats["extractions"] == 1
        assert stats["deployments"] == 1
        assert stats["successful_deployments"] == 1
    
    def test_persistence(self):
        """Test persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "improvement"
            kb_data_dir = Path(tmpdir) / "kb"
            
            kb = KnowledgeBase(data_dir=kb_data_dir)
            
            # Create and deploy
            si = SelfImprovement(knowledge_base=kb, data_dir=data_dir)
            
            rule = ExtractedRule(
                name="Persist Test",
                description="Test persistence",
                condition={"x": 1},
                action={"y": 2},
                confidence=0.9,
                support=10,
            )
            
            result = si.deploy_rule(rule)
            
            # Check deployment file exists
            deployment_file = data_dir / f"deployment_{result.rule_id}.json"
            assert deployment_file.exists()
    
    def test_repr(self, kb):
        """Test string representation."""
        si = SelfImprovement(knowledge_base=kb)
        
        result = repr(si)
        
        assert "SelfImprovement" in result
        assert "extractions=" in result
        assert "deployments=" in result
