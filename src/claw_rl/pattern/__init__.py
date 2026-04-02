"""
Pattern Recognition Module.

This module provides pattern recognition capabilities for Phase 2: Self-Learning.

Components:
- PatternRecognitionEngine: Main pattern recognition engine
- TemporalPatternRecognizer: Time-based pattern recognition
- BehavioralPatternClusterer: Behavior clustering
- ContextualAssociationAnalyzer: Context-behavior associations
- AnomalyDetector: Anomaly detection
- Pattern: Represents a recognized pattern
- Anomaly: Represents an anomaly
- PatternType: Types of patterns
- AnomalyType: Types of anomalies

Reference: ADR-007: Pattern Recognition Engine
"""

from .engine import (
    PatternRecognitionEngine,
    Pattern,
    Anomaly,
    PatternType,
    AnomalyType,
    PatternRecognitionResult,
    recognize_patterns
)

from .temporal import (
    TemporalPatternRecognizer,
    TemporalPattern,
    TemporalPatternType,
    TimeWindow
)

from .behavioral import (
    BehavioralPatternClusterer,
    BehavioralPattern,
    BehaviorCluster,
    BehaviorFeature,
    BehaviorType
)

from .contextual import (
    ContextualAssociationAnalyzer,
    ContextualPattern,
    AssociationRule,
    Context,
    AssociationType,
    ContextType
)

from .anomaly import (
    AnomalyDetector,
    AnomalyAlert,
    AnomalyScore,
    AnomalySeverity,
    AnomalyCategory
)

__all__ = [
    # Engine
    'PatternRecognitionEngine',
    'Pattern',
    'Anomaly',
    'PatternType',
    'AnomalyType',
    'PatternRecognitionResult',
    'recognize_patterns',
    
    # Temporal
    'TemporalPatternRecognizer',
    'TemporalPattern',
    'TemporalPatternType',
    'TimeWindow',
    
    # Behavioral
    'BehavioralPatternClusterer',
    'BehavioralPattern',
    'BehaviorCluster',
    'BehaviorFeature',
    'BehaviorType',
    
    # Contextual
    'ContextualAssociationAnalyzer',
    'ContextualPattern',
    'AssociationRule',
    'Context',
    'AssociationType',
    'ContextType',
    
    # Anomaly
    'AnomalyDetector',
    'AnomalyAlert',
    'AnomalyScore',
    'AnomalySeverity',
    'AnomalyCategory'
]
