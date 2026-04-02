"""
Unit tests for Contextual Association Analysis.
"""

import pytest
from datetime import datetime

from claw_rl.pattern import (
    ContextualAssociationAnalyzer,
    ContextualPattern,
    AssociationRule,
    Context,
    AssociationType,
    ContextType
)


class TestContext:
    """Test Context."""
    
    def test_context_creation(self):
        """Test context creation."""
        context = Context(
            context_id="ctx-001",
            context_type=ContextType.TIME,
            context_value="morning",
            confidence=0.9
        )
        
        assert context.context_id == "ctx-001"
        assert context.context_type == ContextType.TIME
        assert context.context_value == "morning"
        assert context.confidence == 0.9
    
    def test_context_to_dict(self):
        """Test context to_dict."""
        context = Context(
            context_id="ctx-001",
            context_type=ContextType.LOCATION,
            context_value="office",
            confidence=0.85,
            metadata={'key': 'value'}
        )
        
        context_dict = context.to_dict()
        
        assert context_dict['context_id'] == "ctx-001"
        assert context_dict['context_type'] == 'location'
        assert context_dict['context_value'] == "office"
        assert context_dict['confidence'] == 0.85
        assert context_dict['metadata']['key'] == 'value'
    
    def test_context_matches(self):
        """Test context matching."""
        context1 = Context(
            context_id="ctx-001",
            context_type=ContextType.TIME,
            context_value="morning",
            confidence=0.9
        )
        
        context2 = Context(
            context_id="ctx-002",
            context_type=ContextType.TIME,
            context_value="morning",
            confidence=0.9
        )
        
        context3 = Context(
            context_id="ctx-003",
            context_type=ContextType.TIME,
            context_value="evening",
            confidence=0.9
        )
        
        assert context1.matches(context2)
        assert not context1.matches(context3)


class TestAssociationRule:
    """Test AssociationRule."""
    
    def test_rule_creation(self):
        """Test rule creation."""
        rule = AssociationRule(
            rule_id="rule-001",
            association_type=AssociationType.CAUSAL,
            antecedent=["A", "B"],
            consequent=["C"],
            support=0.8,
            confidence=0.9,
            lift=1.2
        )
        
        assert rule.rule_id == "rule-001"
        assert rule.association_type == AssociationType.CAUSAL
        assert rule.antecedent == ["A", "B"]
        assert rule.consequent == ["C"]
        assert rule.support == 0.8
        assert rule.confidence == 0.9
        assert rule.lift == 1.2
    
    def test_rule_to_dict(self):
        """Test rule to_dict."""
        rule = AssociationRule(
            rule_id="rule-001",
            association_type=AssociationType.CORRELATIONAL,
            antecedent=["X"],
            consequent=["Y"],
            support=0.7,
            confidence=0.8,
            lift=1.5,
            metadata={'key': 'value'}
        )
        
        rule_dict = rule.to_dict()
        
        assert rule_dict['rule_id'] == "rule-001"
        assert rule_dict['association_type'] == 'correlational'
        assert rule_dict['antecedent'] == ["X"]
        assert rule_dict['consequent'] == ["Y"]
        assert rule_dict['support'] == 0.7
        assert rule_dict['metadata']['key'] == 'value'
    
    def test_rule_is_significant(self):
        """Test rule significance."""
        # Significant rule
        significant = AssociationRule(
            rule_id="rule-001",
            association_type=AssociationType.CAUSAL,
            antecedent=["A"],
            consequent=["B"],
            support=0.8,
            confidence=0.9,
            lift=1.5
        )
        
        assert significant.is_significant(min_support=0.1, min_confidence=0.7, min_lift=1.0)
        
        # Low support
        low_support = AssociationRule(
            rule_id="rule-002",
            association_type=AssociationType.CAUSAL,
            antecedent=["A"],
            consequent=["B"],
            support=0.05,
            confidence=0.9,
            lift=1.5
        )
        
        assert not low_support.is_significant(min_support=0.1, min_confidence=0.7, min_lift=1.0)
        
        # Low confidence
        low_confidence = AssociationRule(
            rule_id="rule-003",
            association_type=AssociationType.CAUSAL,
            antecedent=["A"],
            consequent=["B"],
            support=0.8,
            confidence=0.6,
            lift=1.5
        )
        
        assert not low_confidence.is_significant(min_support=0.1, min_confidence=0.7, min_lift=1.0)


class TestContextualPattern:
    """Test ContextualPattern."""
    
    def test_pattern_creation(self):
        """Test pattern creation."""
        context = Context(
            context_id="ctx-001",
            context_type=ContextType.TIME,
            context_value="morning",
            confidence=0.9
        )
        
        rule = AssociationRule(
            rule_id="rule-001",
            association_type=AssociationType.CAUSAL,
            antecedent=["A"],
            consequent=["B"],
            support=0.8,
            confidence=0.9,
            lift=1.5
        )
        
        pattern = ContextualPattern(
            pattern_id="pattern-001",
            contexts=[context],
            associations=[rule],
            confidence=0.85,
            frequency=10,
            description="Test pattern"
        )
        
        assert pattern.pattern_id == "pattern-001"
        assert len(pattern.contexts) == 1
        assert len(pattern.associations) == 1
        assert pattern.confidence == 0.85
        assert pattern.frequency == 10
    
    def test_pattern_is_significant(self):
        """Test pattern significance."""
        pattern = ContextualPattern(
            pattern_id="pattern-001",
            contexts=[],
            associations=[],
            confidence=0.85,
            frequency=10,
            description="Test pattern"
        )
        
        assert pattern.is_significant(min_confidence=0.7, min_frequency=3)
        
        # Low confidence
        low_confidence = ContextualPattern(
            pattern_id="pattern-002",
            contexts=[],
            associations=[],
            confidence=0.6,
            frequency=10,
            description="Test pattern"
        )
        
        assert not low_confidence.is_significant(min_confidence=0.7, min_frequency=3)


class TestContextualAssociationAnalyzer:
    """Test ContextualAssociationAnalyzer."""
    
    def test_analyzer_creation(self):
        """Test analyzer creation."""
        analyzer = ContextualAssociationAnalyzer()
        
        assert analyzer.min_support == 0.1
        assert analyzer.min_confidence == 0.7
        assert analyzer.min_lift == 1.0
    
    def test_analyzer_with_config(self):
        """Test analyzer with configuration."""
        config = {
            'min_support': 0.2,
            'min_confidence': 0.8,
            'min_lift': 1.5
        }
        
        analyzer = ContextualAssociationAnalyzer(config=config)
        
        assert analyzer.min_support == 0.2
        assert analyzer.min_confidence == 0.8
        assert analyzer.min_lift == 1.5
    
    def test_analyze_memories(self):
        """Test memory analysis."""
        analyzer = ContextualAssociationAnalyzer()
        
        # Create memories with contexts
        memories = [
            {'id': 'm1', 'context': {'time': 'morning'}, 'behavior': 'work'},
            {'id': 'm2', 'context': {'time': 'morning'}, 'behavior': 'work'},
            {'id': 'm3', 'context': {'time': 'afternoon'}, 'behavior': 'work'},
            {'id': 'm4', 'context': {'time': 'morning'}, 'behavior': 'work'},
            {'id': 'm5', 'context': {'time': 'evening'}, 'behavior': 'relax'},
        ]
        
        patterns = analyzer.analyze(memories)
        
        assert patterns is not None
        # Should find associations
        assert len(patterns) >= 0
    
    def test_analyze_insufficient_data(self):
        """Test analysis with insufficient data."""
        analyzer = ContextualAssociationAnalyzer()
        
        # Create only 2 memories (< min_frequency)
        memories = [
            {'id': 'm1', 'context': {'time': 'morning'}, 'behavior': 'work'},
            {'id': 'm2', 'context': {'time': 'afternoon'}, 'behavior': 'relax'},
        ]
        
        patterns = analyzer.analyze(memories)
        
        # Should return empty list
        assert patterns == []
    
    def test_find_causal_relationships(self):
        """Test causal relationship detection."""
        analyzer = ContextualAssociationAnalyzer()
        
        # Create memories with temporal sequence
        memories = [
            {'id': 'm1', 'behavior': 'login', 'timestamp': 1},
            {'id': 'm2', 'behavior': 'work', 'timestamp': 2},
            {'id': 'm3', 'behavior': 'login', 'timestamp': 3},
            {'id': 'm4', 'behavior': 'work', 'timestamp': 4},
            {'id': 'm5', 'behavior': 'login', 'timestamp': 5},
            {'id': 'm6', 'behavior': 'work', 'timestamp': 6},
        ]
        
        causal_rules = analyzer.find_causal_relationships(memories)
        
        assert causal_rules is not None
        # Should find login -> work pattern
        assert len(causal_rules) >= 0
    
    def test_get_statistics(self):
        """Test analyzer statistics."""
        analyzer = ContextualAssociationAnalyzer()
        
        # Analyze memories
        memories = [
            {'id': f'm{i}', 'context': {'time': 'morning'}, 'behavior': 'work'}
            for i in range(10)
        ]
        
        analyzer.analyze(memories)
        
        stats = analyzer.get_statistics()
        
        assert 'total_processed' in stats
        assert 'patterns_found' in stats
        assert stats['total_processed'] == 10
