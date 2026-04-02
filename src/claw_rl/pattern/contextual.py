"""
Contextual Association Analysis - Find relationships between context and behavior.

This module provides contextual association analysis capabilities:
- Association rule mining
- Context embedding
- Causal inference
- Knowledge graph construction

Reference: ADR-007: Pattern Recognition Engine
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Set
from enum import Enum
import time
from collections import defaultdict


class AssociationType(Enum):
    """Types of associations."""
    CAUSAL = "causal"              # A causes B
    CORRELATIONAL = "correlational"  # A correlates with B
    TEMPORAL = "temporal"          # A happens before B
    CONTEXTUAL = "contextual"      # A and B share context
    SEQUENTIAL = "sequential"      # A leads to B


class ContextType(Enum):
    """Types of context."""
    TIME = "time"                  # Time-based context
    LOCATION = "location"          # Location-based context
    USER = "user"                  # User-based context
    TOPIC = "topic"                # Topic-based context
    EMOTION = "emotion"            # Emotion-based context
    TASK = "task"                  # Task-based context


@dataclass
class Context:
    """Represents a context."""
    context_id: str
    context_type: ContextType
    context_value: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'context_id': self.context_id,
            'context_type': self.context_type.value,
            'context_value': self.context_value,
            'confidence': self.confidence,
            'metadata': self.metadata
        }
    
    def matches(self, other: 'Context', threshold: float = 0.8) -> bool:
        """Check if contexts match."""
        if self.context_type != other.context_type:
            return False
        return self.context_value == other.context_value and self.confidence >= threshold


@dataclass
class AssociationRule:
    """Represents an association rule."""
    rule_id: str
    association_type: AssociationType
    antecedent: List[str]  # Left-hand side (A)
    consequent: List[str]  # Right-hand side (B)
    support: float  # Frequency of A∪B (0-1)
    confidence: float  # P(B|A) (0-1)
    lift: float  # P(B|A) / P(B) (>1 means positive association)
    contexts: List[Context] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'rule_id': self.rule_id,
            'association_type': self.association_type.value,
            'antecedent': self.antecedent,
            'consequent': self.consequent,
            'support': self.support,
            'confidence': self.confidence,
            'lift': self.lift,
            'contexts': [c.to_dict() for c in self.contexts],
            'metadata': self.metadata
        }
    
    def is_significant(self, min_support: float = 0.1, min_confidence: float = 0.7, min_lift: float = 1.0) -> bool:
        """Check if rule is significant."""
        return (
            self.support >= min_support and
            self.confidence >= min_confidence and
            self.lift >= min_lift
        )


@dataclass
class ContextualPattern:
    """Represents a contextual pattern."""
    pattern_id: str
    contexts: List[Context]
    associations: List[AssociationRule]
    confidence: float
    frequency: int
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'pattern_id': self.pattern_id,
            'contexts': [c.to_dict() for c in self.contexts],
            'associations': [a.to_dict() for a in self.associations],
            'confidence': self.confidence,
            'frequency': self.frequency,
            'description': self.description,
            'metadata': self.metadata
        }
    
    def is_significant(self, min_confidence: float = 0.7, min_frequency: int = 3) -> bool:
        """Check if pattern is significant."""
        return self.confidence >= min_confidence and self.frequency >= min_frequency


class ContextualAssociationAnalyzer:
    """
    Contextual Association Analyzer.
    
    Analyzes relationships between context and behavior:
    - Association rule mining (Apriori algorithm)
    - Context embedding (simplified)
    - Causal inference (simplified)
    - Knowledge graph construction
    
    Example:
        >>> analyzer = ContextualAssociationAnalyzer()
        >>> memories = [
        ...     {'id': 'm1', 'context': {'time': 'morning'}, 'behavior': 'work'},
        ...     {'id': 'm2', 'context': {'time': 'morning'}, 'behavior': 'work'},
        ... ]
        >>> patterns = analyzer.analyze(memories)
        >>> for pattern in patterns:
        ...     print(f"{pattern.description}: {pattern.confidence:.2f}")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Contextual Association Analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Configuration
        self.min_support = self.config.get('min_support', 0.1)
        self.min_confidence = self.config.get('min_confidence', 0.7)
        self.min_lift = self.config.get('min_lift', 1.0)
        self.min_frequency = self.config.get('min_frequency', 3)
        
        # Statistics
        self._total_processed = 0
        self._patterns_found = 0
    
    def analyze(
        self,
        memories: List[Dict[str, Any]],
        context_types: Optional[List[ContextType]] = None
    ) -> List[ContextualPattern]:
        """
        Analyze memories for contextual associations.
        
        Args:
            memories: List of memories with context and behavior
            context_types: Types of contexts to analyze (default: all)
            
        Returns:
            List of contextual patterns
        """
        start_time = time.time()
        
        # Default to all context types
        if context_types is None:
            context_types = [
                ContextType.TIME,
                ContextType.LOCATION,
                ContextType.USER,
                ContextType.TOPIC,
                ContextType.EMOTION,
                ContextType.TASK
            ]
        
        patterns = []
        
        # Extract contexts from memories
        contexts = self._extract_contexts(memories, context_types)
        
        # Mine association rules
        associations = self._mine_associations(memories, contexts)
        
        # Create patterns from associations
        if associations:
            pattern = ContextualPattern(
                pattern_id="contextual_0",
                contexts=contexts[:10],  # Top 10 contexts
                associations=associations,
                confidence=sum(a.confidence for a in associations) / len(associations),
                frequency=len(memories),
                description=f"Found {len(associations)} associations in {len(memories)} memories"
            )
            patterns.append(pattern)
        
        # Update statistics
        self._total_processed += len(memories)
        self._patterns_found += len(patterns)
        
        return patterns
    
    def _extract_contexts(
        self,
        memories: List[Dict[str, Any]],
        context_types: List[ContextType]
    ) -> List[Context]:
        """Extract contexts from memories."""
        contexts = []
        
        for i, memory in enumerate(memories):
            memory_contexts = memory.get('context', {})
            
            for context_type in context_types:
                context_key = context_type.value
                if context_key in memory_contexts:
                    context_value = str(memory_contexts[context_key])
                    
                    contexts.append(Context(
                        context_id=f"context_{i}_{context_key}",
                        context_type=context_type,
                        context_value=context_value,
                        confidence=1.0,
                        metadata={'memory_id': memory.get('id', 'unknown')}
                    ))
        
        return contexts
    
    def _mine_associations(
        self,
        memories: List[Dict[str, Any]],
        contexts: List[Context]
    ) -> List[AssociationRule]:
        """Mine association rules using Apriori-like algorithm."""
        associations = []
        
        if len(memories) < self.min_frequency:
            return associations
        
        # Group memories by context
        context_groups = defaultdict(list)
        for context in contexts:
            context_groups[(context.context_type.value, context.context_value)].append(context)
        
        # Find frequent context-behavior pairs
        behavior_groups = defaultdict(list)
        for memory in memories:
            behavior = memory.get('behavior', 'unknown')
            memory_contexts = memory.get('context', {})
            
            for key, value in memory_contexts.items():
                behavior_groups[(key, str(value), behavior)].append(memory)
        
        # Create association rules
        total_memories = len(memories)
        rule_id = 0
        
        for (context_type, context_value, behavior), group in behavior_groups.items():
            if len(group) >= self.min_frequency:
                support = len(group) / total_memories
                
                # Calculate confidence (P(behavior|context))
                context_count = len(context_groups.get((context_type, context_value), []))
                confidence = len(group) / max(context_count, 1)
                
                # Calculate lift (P(behavior|context) / P(behavior))
                behavior_count = sum(1 for m in memories if m.get('behavior') == behavior)
                behavior_prob = behavior_count / total_memories
                lift = confidence / max(behavior_prob, 0.001)
                
                rule = AssociationRule(
                    rule_id=f"rule_{rule_id}",
                    association_type=AssociationType.CONTEXTUAL,
                    antecedent=[f"{context_type}={context_value}"],
                    consequent=[behavior],
                    support=support,
                    confidence=confidence,
                    lift=lift,
                    metadata={
                        'context_type': context_type,
                        'context_value': context_value,
                        'behavior': behavior
                    }
                )
                
                if rule.is_significant(self.min_support, self.min_confidence, self.min_lift):
                    associations.append(rule)
                    rule_id += 1
        
        return associations
    
    def find_causal_relationships(
        self,
        memories: List[Dict[str, Any]]
    ) -> List[AssociationRule]:
        """
        Find potential causal relationships.
        
        Uses simplified causal inference based on temporal ordering.
        
        Args:
            memories: List of memories with temporal data
            
        Returns:
            List of potential causal relationships
        """
        causal_rules = []
        
        if len(memories) < self.min_frequency:
            return causal_rules
        
        # Sort memories by timestamp
        sorted_memories = sorted(memories, key=lambda m: m.get('timestamp', 0))
        
        # Find sequential patterns (A before B)
        sequence_pairs = defaultdict(int)
        
        for i in range(len(sorted_memories) - 1):
            current_behavior = sorted_memories[i].get('behavior', 'unknown')
            next_behavior = sorted_memories[i + 1].get('behavior', 'unknown')
            
            if current_behavior != next_behavior:
                pair = (current_behavior, next_behavior)
                sequence_pairs[pair] += 1
        
        # Create causal rules
        total_pairs = sum(sequence_pairs.values())
        rule_id = 0
        
        for (cause, effect), count in sequence_pairs.items():
            if count >= self.min_frequency:
                support = count / total_pairs
                confidence = count / max(total_pairs, 1)
                lift = confidence  # Simplified
                
                rule = AssociationRule(
                    rule_id=f"causal_{rule_id}",
                    association_type=AssociationType.CAUSAL,
                    antecedent=[cause],
                    consequent=[effect],
                    support=support,
                    confidence=confidence,
                    lift=lift,
                    metadata={
                        'cause': cause,
                        'effect': effect,
                        'count': count
                    }
                )
                
                causal_rules.append(rule)
                rule_id += 1
        
        return causal_rules
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analyzer statistics."""
        return {
            'total_processed': self._total_processed,
            'patterns_found': self._patterns_found
        }
