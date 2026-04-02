"""
Behavioral Pattern Clustering - Group similar user behaviors.

This module provides behavioral pattern clustering capabilities:
- Feature extraction from interactions
- K-Means clustering
- DBSCAN density-based clustering
- Behavior sequence analysis

Reference: ADR-007: Pattern Recognition Engine
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import time
from collections import defaultdict
import hashlib


class BehaviorType(Enum):
    """Types of behaviors."""
    INTERACTION = "interaction"      # User interactions (clicks, views)
    COMMAND = "command"              # Commands issued
    QUERY = "query"                  # Search queries
    FEEDBACK = "feedback"            # User feedback
    NAVIGATION = "navigation"        # Navigation patterns


@dataclass
class BehaviorFeature:
    """Represents a behavior feature for clustering."""
    feature_id: str
    feature_type: str
    feature_value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'feature_id': self.feature_id,
            'feature_type': self.feature_type,
            'feature_value': self.feature_value,
            'metadata': self.metadata
        }


@dataclass
class BehaviorCluster:
    """Represents a cluster of similar behaviors."""
    cluster_id: str
    cluster_type: BehaviorType
    behaviors: List[str]  # Behavior IDs
    centroid: List[float]  # Cluster centroid
    cohesion: float  # How cohesive the cluster is (0-1)
    separation: float  # How separated from other clusters (0-1)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'cluster_id': self.cluster_id,
            'cluster_type': self.cluster_type.value,
            'behaviors': self.behaviors,
            'centroid': self.centroid,
            'cohesion': self.cohesion,
            'separation': self.separation,
            'metadata': self.metadata
        }
    
    def is_significant(self, min_size: int = 3, min_cohesion: float = 0.5) -> bool:
        """Check if cluster is significant."""
        return len(self.behaviors) >= min_size and self.cohesion >= min_cohesion


@dataclass
class BehavioralPattern:
    """Represents a behavioral pattern."""
    pattern_id: str
    pattern_type: str
    clusters: List[BehaviorCluster]
    confidence: float
    frequency: int
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type,
            'clusters': [c.to_dict() for c in self.clusters],
            'confidence': self.confidence,
            'frequency': self.frequency,
            'description': self.description,
            'metadata': self.metadata
        }
    
    def is_significant(self, min_confidence: float = 0.7, min_frequency: int = 3) -> bool:
        """Check if pattern is significant."""
        return self.confidence >= min_confidence and self.frequency >= min_frequency


class BehavioralPatternClusterer:
    """
    Behavioral Pattern Clusterer.
    
    Clusters similar user behaviors:
    - Extracts features from interactions
    - Uses K-Means for centroid-based clustering
    - Uses DBSCAN for density-based clustering
    - Analyzes behavior sequences
    
    Example:
        >>> clusterer = BehavioralPatternClusterer()
        >>> memories = [
        ...     {'id': 'm1', 'behavior': 'click', 'content': '...'},
        ...     {'id': 'm2', 'behavior': 'view', 'content': '...'},
        ... ]
        >>> patterns = clusterer.cluster(memories)
        >>> for pattern in patterns:
        ...     print(f"{pattern.pattern_type}: {pattern.confidence:.2f}")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Behavioral Pattern Clusterer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Configuration
        self.min_confidence = self.config.get('min_confidence', 0.7)
        self.min_cluster_size = self.config.get('min_cluster_size', 3)
        self.n_clusters = self.config.get('n_clusters', 5)
        self.eps = self.config.get('eps', 0.5)  # DBSCAN epsilon
        self.min_samples = self.config.get('min_samples', 3)  # DBSCAN min samples
        
        # Statistics
        self._total_processed = 0
        self._patterns_found = 0
    
    def cluster(
        self,
        memories: List[Dict[str, Any]],
        behavior_types: Optional[List[BehaviorType]] = None
    ) -> List[BehavioralPattern]:
        """
        Cluster memories by behavior.
        
        Args:
            memories: List of memories with behavior data
            behavior_types: Types of behaviors to cluster (default: all)
            
        Returns:
            List of behavioral patterns
        """
        start_time = time.time()
        
        # Default to all behavior types
        if behavior_types is None:
            behavior_types = [
                BehaviorType.INTERACTION,
                BehaviorType.COMMAND,
                BehaviorType.QUERY,
                BehaviorType.FEEDBACK,
                BehaviorType.NAVIGATION
            ]
        
        patterns = []
        
        # Group memories by behavior type
        behavior_groups = self._group_by_behavior(memories)
        
        # Cluster each behavior type
        for behavior_type in behavior_types:
            if behavior_type.value in behavior_groups:
                type_patterns = self._cluster_behavior_type(
                    behavior_type,
                    behavior_groups[behavior_type.value]
                )
                patterns.extend(type_patterns)
        
        # Update statistics
        self._total_processed += len(memories)
        self._patterns_found += len(patterns)
        
        return patterns
    
    def _group_by_behavior(self, memories: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group memories by behavior type."""
        groups = defaultdict(list)
        
        for memory in memories:
            behavior = memory.get('behavior', 'unknown')
            groups[behavior].append(memory)
        
        return groups
    
    def _cluster_behavior_type(
        self,
        behavior_type: BehaviorType,
        memories: List[Dict[str, Any]]
    ) -> List[BehavioralPattern]:
        """Cluster memories of a specific behavior type."""
        patterns = []
        
        if len(memories) < self.min_cluster_size:
            return patterns
        
        # Extract features
        features = self._extract_features(memories)
        
        if not features:
            return patterns
        
        # K-Means clustering (simplified)
        clusters = self._kmeans_clustering(features, memories)
        
        # Create pattern from clusters
        if clusters:
            # Calculate confidence based on cluster quality
            avg_cohesion = sum(c.cohesion for c in clusters) / len(clusters)
            
            pattern = BehavioralPattern(
                pattern_id=f"behavior_{behavior_type.value}_{len(patterns)}",
                pattern_type=f"{behavior_type.value}_cluster",
                clusters=clusters,
                confidence=avg_cohesion,
                frequency=len(memories),
                description=f"Clustered {len(memories)} {behavior_type.value} behaviors into {len(clusters)} groups",
                metadata={'behavior_type': behavior_type.value}
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def _extract_features(self, memories: List[Dict[str, Any]]) -> List[BehaviorFeature]:
        """Extract features from memories."""
        features = []
        
        for memory in memories:
            # Extract simple features
            feature_id = memory.get('id', 'unknown')
            
            # Content-based features
            content = memory.get('content', '')
            content_length = len(content)
            word_count = len(content.split())
            
            features.append(BehaviorFeature(
                feature_id=feature_id,
                feature_type='content',
                feature_value=content_length,
                metadata={'word_count': word_count}
            ))
        
        return features
    
    def _kmeans_clustering(
        self,
        features: List[BehaviorFeature],
        memories: List[Dict[str, Any]]
    ) -> List[BehaviorCluster]:
        """
        K-Means clustering (simplified implementation).
        
        In production, use scikit-learn's KMeans.
        """
        clusters = []
        
        if len(features) < self.min_cluster_size:
            return clusters
        
        # Simplified: group by feature value ranges
        # In production, use actual K-Means algorithm
        value_groups = defaultdict(list)
        
        for feature, memory in zip(features, memories):
            # Create bucket based on feature value
            bucket = int(feature.feature_value / 100)  # Groups of 100
            value_groups[bucket].append((feature, memory))
        
        # Create clusters from groups
        for bucket, items in value_groups.items():
            if len(items) >= self.min_cluster_size:
                behaviors = [m.get('id', 'unknown') for _, m in items]
                
                # Calculate centroid (average feature value)
                avg_value = sum(f.feature_value for f, _ in items) / len(items)
                centroid = [avg_value]
                
                # Calculate cohesion (how close items are to centroid)
                distances = [abs(f.feature_value - avg_value) for f, _ in items]
                avg_distance = sum(distances) / len(distances)
                cohesion = 1.0 / (1.0 + avg_distance / 100)  # Normalized cohesion
                
                cluster = BehaviorCluster(
                    cluster_id=f"cluster_{bucket}",
                    cluster_type=BehaviorType.INTERACTION,
                    behaviors=behaviors,
                    centroid=centroid,
                    cohesion=min(1.0, cohesion),
                    separation=0.5,  # Simplified
                    metadata={'bucket': bucket, 'avg_value': avg_value}
                )
                
                clusters.append(cluster)
        
        return clusters
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get clusterer statistics."""
        return {
            'total_processed': self._total_processed,
            'patterns_found': self._patterns_found
        }
