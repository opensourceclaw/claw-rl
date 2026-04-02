"""
Pattern Recognition Engine - Recognize patterns from historical memory.

This module implements Phase 2: Self-Learning - Pattern Recognition.
It provides four core capabilities:
1. Temporal Pattern Recognition - Identify patterns in time-series data
2. Behavioral Pattern Clustering - Group similar user behaviors
3. Contextual Association Analysis - Find relationships between context and behavior
4. Anomaly Detection - Identify unusual patterns

Reference: ADR-007: Pattern Recognition Engine
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from enum import Enum
from datetime import datetime
import time

# Import sub-components
from .temporal import TemporalPatternRecognizer, TemporalPatternType
from .behavioral import BehavioralPatternClusterer, BehaviorType
from .contextual import ContextualAssociationAnalyzer, ContextType
from .anomaly import AnomalyDetector, AnomalySeverity


class PatternType(Enum):
    """Types of patterns that can be recognized."""
    TEMPORAL = "temporal"          # Time-based patterns
    BEHAVIORAL = "behavioral"      # User behavior patterns
    CONTEXTUAL = "contextual"      # Context-behavior associations
    ANOMALY = "anomaly"            # Anomalous patterns


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""
    STATISTICAL = "statistical"    # Statistical outliers
    BEHAVIORAL = "behavioral"      # Unusual behavior
    TEMPORAL = "temporal"          # Time-based anomalies
    CONTEXTUAL = "contextual"      # Context mismatch


@dataclass
class Pattern:
    """Represents a recognized pattern."""
    pattern_id: str
    pattern_type: PatternType
    confidence: float  # 0.0 to 1.0
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type.value,
            'confidence': self.confidence,
            'occurrences': self.occurrences,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'context': self.context,
            'examples': self.examples,
            'metadata': self.metadata
        }
    
    def is_significant(self, min_confidence: float = 0.7, min_occurrences: int = 3) -> bool:
        """Check if pattern is significant."""
        return self.confidence >= min_confidence and self.occurrences >= min_occurrences


@dataclass
class Anomaly:
    """Represents an anomaly."""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: float  # 0.0 to 1.0
    detected_at: datetime
    memory_id: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'anomaly_id': self.anomaly_id,
            'anomaly_type': self.anomaly_type.value,
            'severity': self.severity,
            'detected_at': self.detected_at.isoformat(),
            'memory_id': self.memory_id,
            'description': self.description,
            'context': self.context,
            'metadata': self.metadata
        }
    
    def is_critical(self, threshold: float = 0.8) -> bool:
        """Check if anomaly is critical."""
        return self.severity >= threshold


@dataclass
class PatternRecognitionResult:
    """Result of pattern recognition operation."""
    patterns: List[Pattern]
    anomalies: List[Anomaly]
    processing_time: float
    memories_processed: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'patterns': [p.to_dict() for p in self.patterns],
            'anomalies': [a.to_dict() for a in self.anomalies],
            'processing_time': self.processing_time,
            'memories_processed': self.memories_processed,
            'metadata': self.metadata
        }
    
    def significant_patterns(self, min_confidence: float = 0.7, min_occurrences: int = 3) -> List[Pattern]:
        """Get significant patterns."""
        return [p for p in self.patterns if p.is_significant(min_confidence, min_occurrences)]
    
    def critical_anomalies(self, threshold: float = 0.8) -> List[Anomaly]:
        """Get critical anomalies."""
        return [a for a in self.anomalies if a.is_critical(threshold)]


class PatternRecognitionEngine:
    """
    Main pattern recognition engine.
    
    This component provides:
    1. Temporal pattern recognition
    2. Behavioral pattern clustering
    3. Contextual association analysis
    4. Anomaly detection
    
    Reference: ADR-007: Pattern Recognition Engine
    
    Example:
        >>> from claw_mem import MemoryStore
        >>> from claw_rl.pattern import PatternRecognitionEngine
        >>> 
        >>> memory_store = MemoryStore()
        >>> engine = PatternRecognitionEngine(memory_store)
        >>> 
        >>> # Recognize patterns
        >>> result = engine.recognize_patterns(
        ...     memory_ids=["mem1", "mem2", "mem3"],
        ...     pattern_types=[PatternType.TEMPORAL, PatternType.BEHAVIORAL]
        ... )
        >>> 
        >>> # Get significant patterns
        >>> significant = result.significant_patterns()
        >>> print(f"Found {len(significant)} significant patterns")
    """
    
    def __init__(
        self,
        memory_store: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Pattern Recognition Engine.
        
        Args:
            memory_store: Memory store for retrieving memories
            config: Configuration dictionary
        """
        self.memory_store = memory_store
        self.config = config or {}
        
        # Configuration
        self.min_confidence = self.config.get('min_confidence', 0.7)
        self.min_occurrences = self.config.get('min_occurrences', 3)
        self.anomaly_threshold = self.config.get('anomaly_threshold', 0.8)
        
        # Initialize sub-components
        self.temporal_recognizer = TemporalPatternRecognizer(config=self.config.get('temporal', {}))
        self.behavioral_clusterer = BehavioralPatternClusterer(config=self.config.get('behavioral', {}))
        self.contextual_analyzer = ContextualAssociationAnalyzer(config=self.config.get('contextual', {}))
        self.anomaly_detector = AnomalyDetector(config=self.config.get('anomaly', {}))
        
        # Pattern storage
        self._patterns: Dict[str, Pattern] = {}
        self._pattern_counter = 0
        
        # Statistics
        self._total_processed = 0
        self._total_patterns_found = 0
        self._total_anomalies_detected = 0
    
    def recognize_patterns(
        self,
        memory_ids: List[str],
        pattern_types: Optional[List[PatternType]] = None
    ) -> PatternRecognitionResult:
        """
        Recognize patterns from memories.
        
        Args:
            memory_ids: List of memory IDs to analyze
            pattern_types: Types of patterns to recognize (default: all)
            
        Returns:
            PatternRecognitionResult with patterns and anomalies
        """
        start_time = time.time()
        
        # Default to all pattern types
        if pattern_types is None:
            pattern_types = [
                PatternType.TEMPORAL,
                PatternType.BEHAVIORAL,
                PatternType.CONTEXTUAL
            ]
        
        patterns = []
        anomalies = []
        
        # Retrieve memories
        memories = self._retrieve_memories(memory_ids)
        
        # Recognize each pattern type
        for pattern_type in pattern_types:
            if pattern_type == PatternType.TEMPORAL:
                type_patterns = self._recognize_temporal_patterns(memories)
                patterns.extend(type_patterns)
            
            elif pattern_type == PatternType.BEHAVIORAL:
                type_patterns = self._recognize_behavioral_patterns(memories)
                patterns.extend(type_patterns)
            
            elif pattern_type == PatternType.CONTEXTUAL:
                type_patterns = self._recognize_contextual_patterns(memories)
                patterns.extend(type_patterns)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(memories)
        
        # Update statistics
        processing_time = time.time() - start_time
        self._total_processed += len(memory_ids)
        self._total_patterns_found += len(patterns)
        self._total_anomalies_detected += len(anomalies)
        
        return PatternRecognitionResult(
            patterns=patterns,
            anomalies=anomalies,
            processing_time=processing_time,
            memories_processed=len(memories),
            metadata={
                'pattern_types': [pt.value for pt in pattern_types],
                'min_confidence': self.min_confidence,
                'min_occurrences': self.min_occurrences
            }
        )
    
    def detect_anomalies(
        self,
        memory_ids: List[str]
    ) -> List[Anomaly]:
        """
        Detect anomalies in memories.
        
        Args:
            memory_ids: List of memory IDs to analyze
            
        Returns:
            List of detected anomalies
        """
        memories = self._retrieve_memories(memory_ids)
        return self._detect_anomalies(memories)
    
    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """
        Get a pattern by ID.
        
        Args:
            pattern_id: Pattern ID
            
        Returns:
            Pattern if found, None otherwise
        """
        return self._patterns.get(pattern_id)
    
    def get_all_patterns(self) -> List[Pattern]:
        """
        Get all patterns.
        
        Returns:
            List of all patterns
        """
        return list(self._patterns.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get engine statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'total_processed': self._total_processed,
            'total_patterns_found': self._total_patterns_found,
            'total_anomalies_detected': self._total_anomalies_detected,
            'patterns_stored': len(self._patterns)
        }
    
    def _retrieve_memories(self, memory_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve memories from memory store.
        
        Args:
            memory_ids: List of memory IDs
            
        Returns:
            List of memory dictionaries
        """
        # TODO: Integrate with claw-mem
        # For now, return placeholder
        memories = []
        for mem_id in memory_ids:
            memories.append({
                'id': mem_id,
                'content': f"Memory {mem_id}",
                'timestamp': datetime.now(),
                'metadata': {}
            })
        return memories
    
    def _recognize_temporal_patterns(self, memories: List[Dict[str, Any]]) -> List[Pattern]:
        """
        Recognize temporal patterns in memories.
        
        Args:
            memories: List of memories
            
        Returns:
            List of temporal patterns
        """
        # Use TemporalPatternRecognizer
        temporal_patterns = self.temporal_recognizer.recognize(memories)
        
        # Convert to Pattern objects
        patterns = []
        for tp in temporal_patterns:
            self._pattern_counter += 1
            pattern = Pattern(
                pattern_id=f"temporal_{self._pattern_counter}",
                pattern_type=PatternType.TEMPORAL,
                confidence=tp.confidence,
                occurrences=tp.frequency,
                first_seen=tp.time_window.start,
                last_seen=tp.time_window.end,
                context={'temporal_type': tp.pattern_type.value},
                examples=[],
                metadata={'temporal_pattern': tp.to_dict()}
            )
            patterns.append(pattern)
        
        return patterns
    
    def _recognize_behavioral_patterns(self, memories: List[Dict[str, Any]]) -> List[Pattern]:
        """
        Recognize behavioral patterns in memories.
        
        Args:
            memories: List of memories
            
        Returns:
            List of behavioral patterns
        """
        # Use BehavioralPatternClusterer
        behavioral_patterns = self.behavioral_clusterer.cluster(memories)
        
        # Convert to Pattern objects
        patterns = []
        for bp in behavioral_patterns:
            self._pattern_counter += 1
            pattern = Pattern(
                pattern_id=f"behavioral_{self._pattern_counter}",
                pattern_type=PatternType.BEHAVIORAL,
                confidence=bp.confidence,
                occurrences=bp.frequency,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                context={'behavioral_type': bp.pattern_type},
                examples=[],
                metadata={'behavioral_pattern': bp.to_dict()}
            )
            patterns.append(pattern)
        
        return patterns
    
    def _recognize_contextual_patterns(self, memories: List[Dict[str, Any]]) -> List[Pattern]:
        """
        Recognize contextual patterns in memories.
        
        Args:
            memories: List of memories
            
        Returns:
            List of contextual patterns
        """
        # Use ContextualAssociationAnalyzer
        contextual_patterns = self.contextual_analyzer.analyze(memories)
        
        # Convert to Pattern objects
        patterns = []
        for cp in contextual_patterns:
            self._pattern_counter += 1
            pattern = Pattern(
                pattern_id=f"contextual_{self._pattern_counter}",
                pattern_type=PatternType.CONTEXTUAL,
                confidence=cp.confidence,
                occurrences=cp.frequency,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                context={'contextual_type': cp.pattern_type},
                examples=[],
                metadata={'contextual_pattern': cp.to_dict()}
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_anomalies(self, memories: List[Dict[str, Any]]) -> List[Anomaly]:
        """
        Detect anomalies in memories.
        
        Args:
            memories: List of memories
            
        Returns:
            List of anomalies
        """
        # Use AnomalyDetector
        alerts = self.anomaly_detector.detect(memories)
        
        # Convert to Anomaly objects
        anomalies = []
        for alert in alerts:
            anomaly = Anomaly(
                anomaly_id=alert.alert_id,
                anomaly_type=AnomalyType.STATISTICAL,  # Default
                severity=alert.anomaly_score.severity.value,
                detected_at=alert.detected_at,
                memory_id=alert.memory_id,
                description=alert.anomaly_score.explanation,
                context=alert.context,
                metadata=alert.anomaly_score.metadata
            )
            anomalies.append(anomaly)
        
        return anomalies


# Convenience function
def recognize_patterns(
    memory_ids: List[str],
    pattern_types: Optional[List[PatternType]] = None,
    memory_store: Optional[Any] = None,
    config: Optional[Dict[str, Any]] = None
) -> PatternRecognitionResult:
    """
    Convenience function to recognize patterns.
    
    Args:
        memory_ids: List of memory IDs to analyze
        pattern_types: Types of patterns to recognize
        memory_store: Memory store for retrieving memories
        config: Configuration dictionary
        
    Returns:
        PatternRecognitionResult with patterns and anomalies
        
    Example:
        >>> result = recognize_patterns(
        ...     memory_ids=["mem1", "mem2", "mem3"],
        ...     pattern_types=[PatternType.TEMPORAL]
        ... )
        >>> print(f"Found {len(result.patterns)} patterns")
    """
    engine = PatternRecognitionEngine(memory_store=memory_store, config=config)
    return engine.recognize_patterns(memory_ids, pattern_types)
