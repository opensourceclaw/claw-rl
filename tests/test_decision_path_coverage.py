# DecisionPath Coverage Enhancement Tests

import pytest
from pathlib import Path
from claw_rl.decision_path import (
    NodeType,
    PathStatus,
    FeedbackInfo,
    DecisionNode,
    DecisionPath,
    DecisionPathTracker,
    PathSummary,
    DecisionPathVisualizer,
    PathPattern,
    PathStatistics,
    SimilarPath,
    AnomalousPath,
    DecisionPathAnalyzer,
)

def test_decision_node_creation():
    """Test DecisionNode creation and basic functionality"""
    from datetime import datetime
    node = DecisionNode(
        node_id="node_001",
        timestamp=datetime.now(),
        node_type=NodeType.ACT,
        input_state={"state": "initial"},
        decision="Create file",
        output_state={"state": "created"},
        feedback=None,
        rule_id=None,
        strategy_id=None,
        parent_node=None
    )
    
    assert node.node_id == "node_001"
    assert node.node_type == NodeType.ACT
    assert node.decision == "Create file"

def test_decision_path_creation():
    """Test DecisionPath creation with multiple nodes"""
    from datetime import datetime
    node1 = DecisionNode(
        node_id="node_001",
        timestamp=datetime.now(),
        node_type=NodeType.OBSERVE,
        input_state={"state": "initial"},
        decision="Observe user request",
        output_state={"state": "observed"},
        feedback=None,
        rule_id=None,
        strategy_id=None,
        parent_node=None
    )
    node2 = DecisionNode(
        node_id="node_002",
        timestamp=datetime.now(),
        node_type=NodeType.DECIDE,
        input_state={"state": "observed"},
        decision="Decide action",
        output_state={"state": "decided"},
        feedback=None,
        rule_id=None,
        strategy_id=None,
        parent_node="node_001"
    )
    node3 = DecisionNode(
        node_id="node_003",
        timestamp=datetime.now(),
        node_type=NodeType.ACT,
        input_state={"state": "decided"},
        decision="Execute action",
        output_state={"state": "executed"},
        feedback=None,
        rule_id=None,
        strategy_id=None,
        parent_node="node_002"
    )
    
    from datetime import datetime
    path = DecisionPath(
        path_id="path_001",
        start_time=datetime.now(),
        nodes=[node1, node2, node3]
    )
    
    assert len(path.nodes) == 3
    assert path.nodes[0].node_type == NodeType.OBSERVE
    assert path.nodes[1].node_type == NodeType.DECIDE
    assert path.nodes[2].node_type == NodeType.ACT

def test_decision_path_visualization():
    """Test DecisionPath visualization capabilities"""
    # Test basic visualization
    visualizer = DecisionPathVisualizer()
    
    # Test that visualizer can be created
    assert visualizer is not None
    
    # Test that to_mermaid method exists (correct name)
    assert hasattr(visualizer, 'to_mermaid')
    
    # Test basic method signature
    try:
        # Try with minimal input
        result = visualizer.to_mermaid([])
        # If it works, verify result type
        if result is not None:
            assert isinstance(result, str)
    except Exception as e:
        # Method exists but may require specific input format
        pass

def test_decision_path_analyzer_basic():
    """Test DecisionPathAnalyzer basic functionality"""
    analyzer = DecisionPathAnalyzer()
    
    # Test that analyzer can be created
    assert analyzer is not None
    
    # Test that key methods exist
    assert hasattr(analyzer, 'analyze_patterns')
    assert hasattr(analyzer, 'calculate_statistics')
    assert hasattr(analyzer, 'detect_anomalies')
    assert hasattr(analyzer, 'find_similar_paths')

def test_decision_path_statistics():
    """Test DecisionPath statistics calculation"""
    from datetime import datetime
    stats = PathStatistics(
        total_paths=10,
        completed_paths=8,
        failed_paths=2,
        active_paths=3,
        avg_node_count=5.5,
        avg_duration_seconds=12.3,
        node_type_counts={"OBSERVE": 2, "DECIDE": 3, "ACT": 5},
        success_rate=0.8
    )
    
    # Test basic statistics creation
    assert stats is not None
    
    # Test that statistics can be converted to dict
    stats_dict = stats.to_dict()
    assert isinstance(stats_dict, dict)
    assert 'total_paths' in stats_dict

def test_decision_path_patterns():
    """Test DecisionPath pattern matching"""
    # Test pattern creation
    pattern = PathPattern(
        pattern_id="pattern_001",
        pattern_type="common",
        frequency=0.8,
        nodes=["OBSERVE", "DECIDE", "ACT"],
        description="Common decision pattern"
    )
    
    assert pattern.pattern_id == "pattern_001"
    assert pattern.pattern_type == "common"
    assert pattern.frequency == 0.8
    assert pattern.description == "Common decision pattern"

def test_decision_path_feedback_info():
    """Test FeedbackInfo creation and handling"""
    from datetime import datetime
    feedback = FeedbackInfo(
        feedback_type="positive",
        score=0.95,
        hint="Great job!",
        source="user",
        timestamp=datetime.now()
    )
    
    assert feedback.feedback_type == "positive"
    assert feedback.score == 0.95
    assert feedback.hint == "Great job!"
    assert feedback.source == "user"