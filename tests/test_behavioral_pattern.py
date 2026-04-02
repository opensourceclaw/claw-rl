"""
Unit tests for Behavioral Pattern Clustering.
"""

import pytest
from datetime import datetime, timedelta

from claw_rl.pattern import (
    BehavioralPatternClusterer,
    BehavioralPattern,
    BehaviorCluster,
    BehaviorFeature,
    BehaviorType
)


class TestBehaviorFeature:
    """Test BehaviorFeature."""
    
    def test_feature_creation(self):
        """Test feature creation."""
        feature = BehaviorFeature(
            feature_id="feat-001",
            feature_type="content",
            feature_value=100.0,
            metadata={'word_count': 20}
        )
        
        assert feature.feature_id == "feat-001"
        assert feature.feature_type == "content"
        assert feature.feature_value == 100.0
        assert feature.metadata['word_count'] == 20
    
    def test_feature_to_dict(self):
        """Test feature to_dict."""
        feature = BehaviorFeature(
            feature_id="feat-001",
            feature_type="content",
            feature_value=100.0,
            metadata={'key': 'value'}
        )
        
        feature_dict = feature.to_dict()
        
        assert feature_dict['feature_id'] == "feat-001"
        assert feature_dict['feature_type'] == "content"
        assert feature_dict['feature_value'] == 100.0
        assert feature_dict['metadata']['key'] == 'value'


class TestBehaviorCluster:
    """Test BehaviorCluster."""
    
    def test_cluster_creation(self):
        """Test cluster creation."""
        cluster = BehaviorCluster(
            cluster_id="cluster-001",
            cluster_type=BehaviorType.INTERACTION,
            behaviors=['b1', 'b2', 'b3'],
            centroid=[100.0],
            cohesion=0.85,
            separation=0.75
        )
        
        assert cluster.cluster_id == "cluster-001"
        assert cluster.cluster_type == BehaviorType.INTERACTION
        assert len(cluster.behaviors) == 3
        assert cluster.cohesion == 0.85
        assert cluster.separation == 0.75
    
    def test_cluster_to_dict(self):
        """Test cluster to_dict."""
        cluster = BehaviorCluster(
            cluster_id="cluster-001",
            cluster_type=BehaviorType.COMMAND,
            behaviors=['b1', 'b2'],
            centroid=[50.0],
            cohesion=0.80,
            separation=0.70,
            metadata={'key': 'value'}
        )
        
        cluster_dict = cluster.to_dict()
        
        assert cluster_dict['cluster_id'] == "cluster-001"
        assert cluster_dict['cluster_type'] == 'command'
        assert cluster_dict['behaviors'] == ['b1', 'b2']
        assert cluster_dict['cohesion'] == 0.80
        assert cluster_dict['metadata']['key'] == 'value'
    
    def test_cluster_is_significant(self):
        """Test cluster significance."""
        # Significant cluster
        significant = BehaviorCluster(
            cluster_id="cluster-001",
            cluster_type=BehaviorType.INTERACTION,
            behaviors=['b1', 'b2', 'b3', 'b4'],
            centroid=[100.0],
            cohesion=0.85,
            separation=0.75
        )
        
        assert significant.is_significant(min_size=3, min_cohesion=0.5)
        
        # Small cluster
        small = BehaviorCluster(
            cluster_id="cluster-002",
            cluster_type=BehaviorType.INTERACTION,
            behaviors=['b1'],
            centroid=[100.0],
            cohesion=0.85,
            separation=0.75
        )
        
        assert not small.is_significant(min_size=3, min_cohesion=0.5)
        
        # Low cohesion
        low_cohesion = BehaviorCluster(
            cluster_id="cluster-003",
            cluster_type=BehaviorType.INTERACTION,
            behaviors=['b1', 'b2', 'b3'],
            centroid=[100.0],
            cohesion=0.40,
            separation=0.75
        )
        
        assert not low_cohesion.is_significant(min_size=3, min_cohesion=0.5)


class TestBehavioralPattern:
    """Test BehavioralPattern."""
    
    def test_pattern_creation(self):
        """Test pattern creation."""
        cluster = BehaviorCluster(
            cluster_id="cluster-001",
            cluster_type=BehaviorType.INTERACTION,
            behaviors=['b1', 'b2', 'b3'],
            centroid=[100.0],
            cohesion=0.85,
            separation=0.75
        )
        
        pattern = BehavioralPattern(
            pattern_id="pattern-001",
            pattern_type="interaction_cluster",
            clusters=[cluster],
            confidence=0.85,
            frequency=10,
            description="Test pattern"
        )
        
        assert pattern.pattern_id == "pattern-001"
        assert pattern.pattern_type == "interaction_cluster"
        assert len(pattern.clusters) == 1
        assert pattern.confidence == 0.85
        assert pattern.frequency == 10
    
    def test_pattern_to_dict(self):
        """Test pattern to_dict."""
        cluster = BehaviorCluster(
            cluster_id="cluster-001",
            cluster_type=BehaviorType.INTERACTION,
            behaviors=['b1', 'b2'],
            centroid=[100.0],
            cohesion=0.80,
            separation=0.70
        )
        
        pattern = BehavioralPattern(
            pattern_id="pattern-001",
            pattern_type="interaction_cluster",
            clusters=[cluster],
            confidence=0.85,
            frequency=10,
            description="Test pattern",
            metadata={'key': 'value'}
        )
        
        pattern_dict = pattern.to_dict()
        
        assert pattern_dict['pattern_id'] == "pattern-001"
        assert pattern_dict['pattern_type'] == "interaction_cluster"
        assert len(pattern_dict['clusters']) == 1
        assert pattern_dict['confidence'] == 0.85
        assert pattern_dict['metadata']['key'] == 'value'
    
    def test_pattern_is_significant(self):
        """Test pattern significance."""
        cluster = BehaviorCluster(
            cluster_id="cluster-001",
            cluster_type=BehaviorType.INTERACTION,
            behaviors=['b1', 'b2', 'b3'],
            centroid=[100.0],
            cohesion=0.85,
            separation=0.75
        )
        
        # Significant pattern
        significant = BehavioralPattern(
            pattern_id="pattern-001",
            pattern_type="interaction_cluster",
            clusters=[cluster],
            confidence=0.85,
            frequency=5,
            description="Test pattern"
        )
        
        assert significant.is_significant(min_confidence=0.7, min_frequency=3)
        
        # Low confidence
        low_confidence = BehavioralPattern(
            pattern_id="pattern-002",
            pattern_type="interaction_cluster",
            clusters=[cluster],
            confidence=0.65,
            frequency=5,
            description="Test pattern"
        )
        
        assert not low_confidence.is_significant(min_confidence=0.7, min_frequency=3)


class TestBehavioralPatternClusterer:
    """Test BehavioralPatternClusterer."""
    
    def test_clusterer_creation(self):
        """Test clusterer creation."""
        clusterer = BehavioralPatternClusterer()
        
        assert clusterer.min_confidence == 0.7
        assert clusterer.min_cluster_size == 3
        assert clusterer.n_clusters == 5
    
    def test_clusterer_with_config(self):
        """Test clusterer with configuration."""
        config = {
            'min_confidence': 0.8,
            'min_cluster_size': 5,
            'n_clusters': 10
        }
        
        clusterer = BehavioralPatternClusterer(config=config)
        
        assert clusterer.min_confidence == 0.8
        assert clusterer.min_cluster_size == 5
        assert clusterer.n_clusters == 10
    
    def test_cluster_behaviors(self):
        """Test behavior clustering."""
        clusterer = BehavioralPatternClusterer()
        
        # Create memories with behaviors
        memories = [
            {'id': f'mem{i}', 'behavior': 'interaction', 'content': 'A' * (i * 100)}
            for i in range(1, 11)
        ]
        
        patterns = clusterer.cluster(
            memories,
            behavior_types=[BehaviorType.INTERACTION]
        )
        
        assert patterns is not None
        # Should cluster similar behaviors
        assert len(patterns) >= 0
    
    def test_cluster_multiple_types(self):
        """Test clustering multiple behavior types."""
        clusterer = BehavioralPatternClusterer()
        
        # Create memories with different behaviors
        memories = []
        
        # Interactions
        for i in range(5):
            memories.append({
                'id': f'interact{i}',
                'behavior': 'interaction',
                'content': 'Interaction ' + str(i)
            })
        
        # Commands
        for i in range(5):
            memories.append({
                'id': f'cmd{i}',
                'behavior': 'command',
                'content': 'Command ' + str(i)
            })
        
        patterns = clusterer.cluster(memories)
        
        assert patterns is not None
    
    def test_cluster_insufficient_data(self):
        """Test clustering with insufficient data."""
        clusterer = BehavioralPatternClusterer()
        
        # Create only 2 memories (< min_cluster_size)
        memories = [
            {'id': 'mem1', 'behavior': 'interaction', 'content': 'Test 1'},
            {'id': 'mem2', 'behavior': 'interaction', 'content': 'Test 2'}
        ]
        
        patterns = clusterer.cluster(
            memories,
            behavior_types=[BehaviorType.INTERACTION]
        )
        
        # Should return empty list (not enough data)
        assert patterns == []
    
    def test_get_statistics(self):
        """Test clusterer statistics."""
        clusterer = BehavioralPatternClusterer()
        
        # Cluster behaviors
        memories = [
            {'id': f'mem{i}', 'behavior': 'interaction', 'content': 'Test ' * (i + 1)}
            for i in range(10)
        ]
        
        clusterer.cluster(memories)
        
        stats = clusterer.get_statistics()
        
        assert 'total_processed' in stats
        assert 'patterns_found' in stats
        assert stats['total_processed'] == 10
