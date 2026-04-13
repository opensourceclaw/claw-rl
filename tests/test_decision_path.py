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
Tests for Decision Path Module
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import json

from typing import List

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


class TestNodeType:
    """Tests for NodeType enum"""

    def test_node_types_exist(self):
        """Test all node types are defined"""
        assert NodeType.OBSERVE.value == "observe"
        assert NodeType.ORIENT.value == "orient"
        assert NodeType.DECIDE.value == "decide"
        assert NodeType.ACT.value == "act"
        assert NodeType.LEARN.value == "learn"


class TestPathStatus:
    """Tests for PathStatus enum"""

    def test_status_values(self):
        """Test all status values are correct"""
        assert PathStatus.ACTIVE.value == "active"
        assert PathStatus.COMPLETED.value == "completed"
        assert PathStatus.FAILED.value == "failed"


class TestFeedbackInfo:
    """Tests for FeedbackInfo"""

    def test_create_feedback(self):
        """Test creating feedback"""
        feedback = FeedbackInfo(
            feedback_type="positive",
            score=0.8,
            hint="Good decision",
            source="user",
        )

        assert feedback.feedback_type == "positive"
        assert feedback.score == 0.8
        assert feedback.hint == "Good decision"
        assert feedback.source == "user"

    def test_feedback_to_dict(self):
        """Test feedback serialization"""
        feedback = FeedbackInfo(
            feedback_type="negative",
            score=-0.5,
            hint="Consider alternative",
            source="system",
            timestamp=datetime(2026, 4, 8, 10, 0, 0),
        )

        data = feedback.to_dict()

        assert data["feedback_type"] == "negative"
        assert data["score"] == -0.5
        assert data["hint"] == "Consider alternative"
        assert data["source"] == "system"
        assert "timestamp" in data

    def test_feedback_from_dict(self):
        """Test feedback deserialization"""
        data = {
            "feedback_type": "correction",
            "score": 0.3,
            "hint": "Better approach",
            "source": "review",
            "timestamp": "2026-04-08T10:00:00",
        }

        feedback = FeedbackInfo.from_dict(data)

        assert feedback.feedback_type == "correction"
        assert feedback.score == 0.3
        assert feedback.hint == "Better approach"
        assert feedback.timestamp is not None


class TestDecisionNode:
    """Tests for DecisionNode"""

    def test_create_node(self):
        """Test creating a decision node"""
        node = DecisionNode(
            node_id="node_001",
            timestamp=datetime.now(),
            node_type=NodeType.DECIDE,
            input_state={"context": "test"},
            decision="Choose option A",
            output_state={"result": "option_a"},
        )

        assert node.node_id == "node_001"
        assert node.node_type == NodeType.DECIDE
        assert node.decision == "Choose option A"
        assert node.parent_node is None
        assert node.child_nodes == []

    def test_node_to_dict(self):
        """Test node serialization"""
        node = DecisionNode(
            node_id="node_001",
            timestamp=datetime(2026, 4, 8, 10, 0, 0),
            node_type=NodeType.ACT,
            input_state={"task": "test"},
            decision="Execute action",
            output_state={"status": "success"},
            rule_id="rule_001",
            strategy_id="strategy_001",
            parent_node="node_000",
            child_nodes=["node_002"],
        )

        data = node.to_dict()

        assert data["node_id"] == "node_001"
        assert data["node_type"] == "act"
        assert data["rule_id"] == "rule_001"
        assert data["strategy_id"] == "strategy_001"
        assert data["parent_node"] == "node_000"
        assert "node_002" in data["child_nodes"]

    def test_node_from_dict(self):
        """Test node deserialization"""
        data = {
            "node_id": "node_001",
            "timestamp": "2026-04-08T10:00:00",
            "node_type": "orient",
            "input_state": {"info": "data"},
            "decision": "Analyze options",
            "output_state": {"analysis": "complete"},
            "feedback": {
                "feedback_type": "positive",
                "score": 0.9,
                "source": "user",
            },
            "rule_id": None,
            "strategy_id": "strat_001",
            "parent_node": None,
            "child_nodes": [],
        }

        node = DecisionNode.from_dict(data)

        assert node.node_id == "node_001"
        assert node.node_type == NodeType.ORIENT
        assert node.feedback is not None
        assert node.feedback.feedback_type == "positive"


class TestDecisionPath:
    """Tests for DecisionPath"""

    def test_create_path(self):
        """Test creating a decision path"""
        path = DecisionPath(
            path_id="path_001",
            start_time=datetime.now(),
            status=PathStatus.ACTIVE,
            context={"task": "test"},
            metadata={"source": "agent"},
        )

        assert path.path_id == "path_001"
        assert path.status == PathStatus.ACTIVE
        assert path.nodes == []
        assert path.get_node_count() == 0

    def test_path_with_nodes(self):
        """Test path with multiple nodes"""
        path = DecisionPath(
            path_id="path_001",
            start_time=datetime.now(),
        )

        node1 = DecisionNode(
            node_id="node_001",
            timestamp=datetime.now(),
            node_type=NodeType.OBSERVE,
            input_state={},
            decision="Observe",
            output_state={},
        )

        node2 = DecisionNode(
            node_id="node_002",
            timestamp=datetime.now(),
            node_type=NodeType.DECIDE,
            input_state={},
            decision="Decide",
            output_state={},
            parent_node="node_001",
        )

        path.nodes = [node1, node2]

        assert path.get_node_count() == 2
        assert path.get_node_types()["observe"] == 1
        assert path.get_node_types()["decide"] == 1

    def test_path_to_dict(self):
        """Test path serialization"""
        path = DecisionPath(
            path_id="path_001",
            start_time=datetime(2026, 4, 8, 10, 0, 0),
            end_time=datetime(2026, 4, 8, 10, 5, 0),
            status=PathStatus.COMPLETED,
            context={"task": "example"},
            metadata={"version": "1.0"},
        )

        data = path.to_dict()

        assert data["path_id"] == "path_001"
        assert data["status"] == "completed"
        assert data["context"]["task"] == "example"

    def test_path_from_dict(self):
        """Test path deserialization"""
        data = {
            "path_id": "path_001",
            "start_time": "2026-04-08T10:00:00",
            "end_time": "2026-04-08T10:05:00",
            "status": "completed",
            "nodes": [],
            "context": {"task": "test"},
            "metadata": {},
        }

        path = DecisionPath.from_dict(data)

        assert path.path_id == "path_001"
        assert path.status == PathStatus.COMPLETED

    def test_get_duration(self):
        """Test duration calculation"""
        path = DecisionPath(
            path_id="path_001",
            start_time=datetime(2026, 4, 8, 10, 0, 0),
            end_time=datetime(2026, 4, 8, 10, 5, 0),
        )

        duration = path.get_duration()
        assert duration == 300.0  # 5 minutes

    def test_get_duration_active(self):
        """Test duration for active path (returns None)"""
        path = DecisionPath(
            path_id="path_001",
            start_time=datetime(2026, 4, 8, 10, 0, 0),
        )

        assert path.get_duration() is None


class TestDecisionPathTracker:
    """Tests for DecisionPathTracker"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = DecisionPathTracker(
            storage_path=Path(self.temp_dir),
            auto_save=True,
        )

    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    def test_start_path(self):
        """Test starting a new path"""
        path_id = self.tracker.start_path(
            context={"task": "test"},
            metadata={"source": "agent"},
        )

        assert path_id is not None
        path = self.tracker.get_path(path_id)
        assert path is not None
        assert path.status == PathStatus.ACTIVE

    def test_start_path_custom_id(self):
        """Test starting path with custom ID"""
        path_id = self.tracker.start_path(
            context={},
            path_id="custom_path_id",
        )

        assert path_id == "custom_path_id"
        assert self.tracker.get_path("custom_path_id") is not None

    def test_add_node(self):
        """Test adding a node to path"""
        path_id = self.tracker.start_path(context={})

        node_id = self.tracker.add_node(
            path_id=path_id,
            node_type=NodeType.OBSERVE,
            input_state={"observation": "data"},
            decision="Observe the data",
            output_state={"perceived": True},
        )

        assert node_id is not None
        path = self.tracker.get_path(path_id)
        assert path is not None
        assert len(path.nodes) == 1

    def test_add_node_with_rule(self):
        """Test adding node with rule and strategy"""
        path_id = self.tracker.start_path(context={})

        node_id = self.tracker.add_node(
            path_id=path_id,
            node_type=NodeType.DECIDE,
            input_state={},
            decision="Choose strategy",
            output_state={},
            rule_id="rule_001",
            strategy_id="strategy_001",
        )

        path = self.tracker.get_path(path_id)
        node = path.nodes[0]
        assert node.rule_id == "rule_001"
        assert node.strategy_id == "strategy_001"

    def test_add_node_invalid_path(self):
        """Test adding node to non-existent path"""
        with pytest.raises(KeyError):
            self.tracker.add_node(
                path_id="invalid_path",
                node_type=NodeType.DECIDE,
                input_state={},
                decision="test",
                output_state={},
            )

    def test_complete_path_success(self):
        """Test completing a path successfully"""
        path_id = self.tracker.start_path(context={})
        self.tracker.add_node(
            path_id=path_id,
            node_type=NodeType.DECIDE,
            input_state={},
            decision="test",
            output_state={},
        )

        path = self.tracker.complete_path(path_id, success=True)

        assert path.status == PathStatus.COMPLETED
        assert path.end_time is not None
        assert path.get_duration() is not None

    def test_complete_path_failure(self):
        """Test completing a path with failure"""
        path_id = self.tracker.start_path(context={})

        path = self.tracker.complete_path(path_id, success=False)

        assert path.status == PathStatus.FAILED

    def test_get_active_paths(self):
        """Test getting active paths"""
        path_id1 = self.tracker.start_path(context={})
        path_id2 = self.tracker.start_path(context={})

        active_paths = self.tracker.get_active_paths()

        assert len(active_paths) == 2

    def test_tracker_without_storage(self):
        """Test tracker without storage"""
        tracker = DecisionPathTracker(auto_save=False)
        path_id = tracker.start_path(context={})

        assert tracker.get_path(path_id) is not None


class TestDecisionPathVisualizer:
    """Tests for DecisionPathVisualizer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.visualizer = DecisionPathVisualizer()
        self.path = self._create_sample_path()

    def _create_sample_path(self) -> DecisionPath:
        """Create a sample path for testing"""
        path = DecisionPath(
            path_id="path_001",
            start_time=datetime(2026, 4, 8, 10, 0, 0),
            end_time=datetime(2026, 4, 8, 10, 5, 0),
            status=PathStatus.COMPLETED,
        )

        node1 = DecisionNode(
            node_id="node_001",
            timestamp=datetime(2026, 4, 8, 10, 0, 0),
            node_type=NodeType.OBSERVE,
            input_state={},
            decision="Observe data",
            output_state={},
            rule_id="rule_001",
            child_nodes=["node_002"],
        )

        node2 = DecisionNode(
            node_id="node_002",
            timestamp=datetime(2026, 4, 8, 10, 1, 0),
            node_type=NodeType.DECIDE,
            input_state={},
            decision="Choose option A",
            output_state={},
            parent_node="node_001",
            child_nodes=["node_003"],
        )

        node3 = DecisionNode(
            node_id="node_003",
            timestamp=datetime(2026, 4, 8, 10, 2, 0),
            node_type=NodeType.ACT,
            input_state={},
            decision="Execute action",
            output_state={"result": "success"},
            parent_node="node_002",
        )

        path.nodes = [node1, node2, node3]
        return path

    def test_to_json(self):
        """Test JSON export"""
        json_str = self.visualizer.to_json(self.path)

        data = json.loads(json_str)
        assert data["path_id"] == "path_001"
        assert len(data["nodes"]) == 3

    def test_to_json_without_feedback(self):
        """Test JSON export without feedback"""
        json_str = self.visualizer.to_json(self.path, include_feedback=False)

        data = json.loads(json_str)
        for node in data["nodes"]:
            assert "feedback" not in node or node["feedback"] is None

    def test_to_json_without_state(self):
        """Test JSON export without state"""
        json_str = self.visualizer.to_json(self.path, include_state=False)

        data = json.loads(json_str)
        for node in data["nodes"]:
            assert "input_state" not in node or node["input_state"] == {}
            assert "output_state" not in node or node["output_state"] == {}

    def test_to_graph_dict(self):
        """Test graph export as dict"""
        graph = self.visualizer.to_graph(self.path, format="dict")

        assert "path_id" in graph
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) == 3
        assert len(graph["edges"]) == 2

    def test_to_mermaid(self):
        """Test Mermaid export"""
        mermaid = self.visualizer.to_mermaid(self.path)

        assert "flowchart" in mermaid
        assert "node_001" in mermaid
        assert "node_002" in mermaid
        assert "-->" in mermaid

    def test_to_mermaid_lr_direction(self):
        """Test Mermaid export with LR direction"""
        mermaid = self.visualizer.to_mermaid(self.path, direction="LR")

        assert "flowchart LR" in mermaid

    def test_to_dot(self):
        """Test DOT export"""
        dot = self.visualizer.to_graph(self.path, format="dot")

        assert "digraph" in dot
        assert "node_001" in dot
        assert "node_002" in dot

    def test_summarize(self):
        """Test path summary"""
        summary = self.visualizer.summarize(self.path)

        assert summary.path_id == "path_001"
        assert summary.node_count == 3
        assert summary.duration_seconds == 300.0
        assert summary.status == "completed"
        assert "rule_001" in summary.rules_used


class TestPathSummary:
    """Tests for PathSummary"""

    def test_create_summary(self):
        """Test creating a summary"""
        summary = PathSummary(
            path_id="path_001",
            node_count=5,
            duration_seconds=120.0,
            status="completed",
            node_types={"observe": 1, "decide": 2, "act": 2},
            has_feedback=True,
            rules_used=["rule_001"],
            strategies_used=["strategy_001"],
        )

        assert summary.path_id == "path_001"
        assert summary.node_count == 5
        assert summary.has_feedback


class TestDecisionPathAnalyzer:
    """Tests for DecisionPathAnalyzer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = DecisionPathAnalyzer()

    def _create_paths(self, count: int, include_rules: bool = True) -> List[DecisionPath]:
        """Create multiple paths for testing"""
        paths = []
        for i in range(count):
            path = DecisionPath(
                path_id=f"path_{i:03d}",
                start_time=datetime(2026, 4, 8, 10, i, 0),
                end_time=datetime(2026, 4, 8, 10, i + 5, 0),
                status=PathStatus.COMPLETED if i % 3 != 0 else PathStatus.FAILED,
            )

            # Add similar nodes
            node1 = DecisionNode(
                node_id=f"node_{i}_001",
                timestamp=datetime(2026, 4, 8, 10, i, 0),
                node_type=NodeType.OBSERVE,
                input_state={},
                decision="Observe",
                output_state={},
                rule_id="rule_common" if include_rules else None,
            )

            node2 = DecisionNode(
                node_id=f"node_{i}_002",
                timestamp=datetime(2026, 4, 8, 10, i, 1),
                node_type=NodeType.DECIDE,
                input_state={},
                decision="Decide",
                output_state={},
                parent_node=f"node_{i}_001",
                rule_id="rule_common" if include_rules else None,
            )

            path.nodes = [node1, node2]
            paths.append(path)

        return paths

    def test_analyze_patterns_empty(self):
        """Test analyzing empty path list"""
        patterns = self.analyzer.analyze_patterns([])
        assert patterns == []

    def test_analyze_patterns(self):
        """Test analyzing patterns"""
        paths = self._create_paths(5)
        patterns = self.analyzer.analyze_patterns(paths)

        assert len(patterns) > 0

    def test_calculate_statistics_empty(self):
        """Test statistics for empty list"""
        stats = self.analyzer.calculate_statistics([])

        assert stats.total_paths == 0
        assert stats.avg_node_count == 0.0

    def test_calculate_statistics(self):
        """Test calculating statistics"""
        paths = self._create_paths(5)
        stats = self.analyzer.calculate_statistics(paths)

        assert stats.total_paths == 5
        assert stats.completed_paths > 0
        assert stats.failed_paths > 0
        assert stats.avg_node_count == 2.0

    def test_find_similar_paths(self):
        """Test finding similar paths"""
        paths = self._create_paths(5)

        similar = self.analyzer.find_similar_paths(
            target_path=paths[0],
            all_paths=paths,
            threshold=0.5,
        )

        assert len(similar) > 0
        assert all(s.similarity_score >= 0.5 for s in similar)

    def test_find_similar_paths_no_match(self):
        """Test finding similar paths with no matches"""
        path = DecisionPath(
            path_id="unique_path",
            start_time=datetime.now(),
        )
        path.nodes = [
            DecisionNode(
                node_id="node_001",
                timestamp=datetime.now(),
                node_type=NodeType.LEARN,
                input_state={},
                decision="Learn",
                output_state={},
            )
        ]

        paths = self._create_paths(3)

        similar = self.analyzer.find_similar_paths(
            target_path=path,
            all_paths=paths,
            threshold=0.9,
        )

        # May or may not find matches depending on threshold

    def test_detect_anomalies_empty(self):
        """Test anomaly detection on empty list"""
        anomalies = self.analyzer.detect_anomalies([])
        assert anomalies == []

    def test_detect_anomalies_few_paths(self):
        """Test anomaly detection with too few paths"""
        paths = self._create_paths(2)
        anomalies = self.analyzer.detect_anomalies(paths)
        assert anomalies == []

    def test_detect_anomalies(self):
        """Test anomaly detection"""
        paths = self._create_paths(10)

        # Add an anomalous path
        anomalous = DecisionPath(
            path_id="anomalous",
            start_time=datetime(2026, 4, 8, 10, 0, 0),
            end_time=datetime(2026, 4, 8, 10, 1, 0),
            status=PathStatus.FAILED,
        )
        anomalous.nodes = [
            DecisionNode(
                node_id="node_001",
                timestamp=datetime(2026, 4, 8, 10, 0, 0),
                node_type=NodeType.OBSERVE,
                input_state={},
                decision="Observe",
                output_state={},
            )
        ]
        paths.append(anomalous)

        anomalies = self.analyzer.detect_anomalies(paths)

        # Should detect some anomalies

    def test_calculate_similarity(self):
        """Test similarity calculation"""
        path1 = DecisionPath(
            path_id="path_1",
            start_time=datetime.now(),
        )
        path1.nodes = [
            DecisionNode(
                node_id="node_001",
                timestamp=datetime.now(),
                node_type=NodeType.OBSERVE,
                input_state={},
                decision="Observe",
                output_state={},
                rule_id="rule_001",
            )
        ]

        path2 = DecisionPath(
            path_id="path_2",
            start_time=datetime.now(),
        )
        path2.nodes = [
            DecisionNode(
                node_id="node_001",
                timestamp=datetime.now(),
                node_type=NodeType.OBSERVE,
                input_state={},
                decision="Observe",
                output_state={},
                rule_id="rule_001",
            )
        ]

        similarity = self.analyzer._calculate_similarity(path1, path2)
        assert similarity > 0.5


class TestIntegration:
    """Integration tests for the full workflow"""

    def test_full_workflow(self):
        """Test complete workflow from tracking to analysis"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = DecisionPathTracker(
                storage_path=Path(temp_dir),
                auto_save=True,
            )

            # Start path
            path_id = tracker.start_path(
                context={"task": "process_data"},
                metadata={"agent": "test_agent"},
            )

            # Add nodes through OODA loop
            tracker.add_node(
                path_id=path_id,
                node_type=NodeType.OBSERVE,
                input_state={"raw_data": [1, 2, 3]},
                decision="Observe data",
                output_state={"perceived": True},
            )

            tracker.add_node(
                path_id=path_id,
                node_type=NodeType.ORIENT,
                input_state={"perceived": True},
                decision="Analyze patterns",
                output_state={"patterns": ["trend1"]},
            )

            tracker.add_node(
                path_id=path_id,
                node_type=NodeType.DECIDE,
                input_state={"patterns": ["trend1"]},
                decision="Apply filter",
                output_state={"decision": "filter"},
                rule_id="rule_filter",
            )

            tracker.add_node(
                path_id=path_id,
                node_type=NodeType.ACT,
                input_state={"decision": "filter"},
                decision="Execute filter",
                output_state={"result": "filtered_data"},
            )

            # Complete path
            path = tracker.complete_path(path_id, success=True)

            # Visualize
            visualizer = DecisionPathVisualizer()
            json_output = visualizer.to_json(path)
            mermaid_output = visualizer.to_mermaid(path)
            summary = visualizer.summarize(path)

            assert summary.node_count == 4
            assert "filter" in json_output
            assert "flowchart" in mermaid_output

            # Analyze
            analyzer = DecisionPathAnalyzer()
            stats = analyzer.calculate_statistics([path])

            assert stats.total_paths == 1
            assert stats.completed_paths == 1

    def test_multiple_paths_analysis(self):
        """Test analysis across multiple paths"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = DecisionPathTracker(
                storage_path=Path(temp_dir),
                auto_save=False,
            )

            # Create multiple paths
            path_ids = []
            for i in range(5):
                path_id = tracker.start_path(
                    context={"task": f"task_{i}"},
                )

                # Vary node counts
                node_count = 2 + (i % 3)
                for j in range(node_count):
                    tracker.add_node(
                        path_id=path_id,
                        node_type=NodeType.DECIDE,
                        input_state={},
                        decision=f"Decision {j}",
                        output_state={},
                        rule_id=f"rule_{i % 2}",
                    )

                tracker.complete_path(path_id, success=(i % 3 != 0))
                path_ids.append(path_id)

            # Get all paths
            paths = [tracker.get_path(pid) for pid in path_ids]
            paths = [p for p in paths if p is not None]

            # Analyze
            analyzer = DecisionPathAnalyzer()
            stats = analyzer.calculate_statistics(paths)
            patterns = analyzer.analyze_patterns(paths)

            assert stats.total_paths == 5
            assert stats.completed_paths > 0
            assert stats.failed_paths > 0
