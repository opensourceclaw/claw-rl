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
Decision Path Module

Provides decision path tracking, visualization, and analysis capabilities
for AI agent decision-making processes.

This module enables:
- Tracking decision paths with full context
- Visualizing paths in multiple formats (JSON, Graph, Mermaid)
- Analyzing patterns, statistics, and anomalies in decision paths
"""

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Node types in a decision path (OODA loop stages)."""
    OBSERVE = "observe"     # Observation stage
    ORIENT = "orient"       # Analysis stage
    DECIDE = "decide"       # Decision stage
    ACT = "act"             # Action stage
    LEARN = "learn"         # Learning stage


class PathStatus(Enum):
    """Status of a decision path."""
    ACTIVE = "active"       # Path is in progress
    COMPLETED = "completed" # Path completed successfully
    FAILED = "failed"       # Path failed


@dataclass
class FeedbackInfo:
    """Feedback information for a decision node."""
    feedback_type: str           # "positive", "negative", "correction"
    score: float                 # Score from -1.0 to 1.0
    hint: Optional[str] = None   # OPD hint for improvement
    source: str = "unknown"      # Source of feedback
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "feedback_type": self.feedback_type,
            "score": self.score,
            "source": self.source,
        }
        if self.hint:
            result["hint"] = self.hint
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackInfo":
        return cls(
            feedback_type=data["feedback_type"],
            score=data["score"],
            hint=data.get("hint"),
            source=data.get("source", "unknown"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
        )


@dataclass
class DecisionNode:
    """
    A single node in a decision path.

    Represents one step in the OODA (Observe-Orient-Decide-Act) loop
    or other decision-making process.

    Attributes:
        node_id: Unique identifier for this node
        timestamp: When this node was created
        node_type: Type of node (OODA loop stage)
        input_state: State before making the decision
        decision: The actual decision made
        output_state: State after making the decision
        feedback: Optional feedback received for this decision
        rule_id: Optional rule that was triggered
        strategy_id: Optional strategy that was used
        parent_node: ID of parent node (for branching)
        child_nodes: IDs of child nodes (for branching)
    """
    node_id: str
    timestamp: datetime
    node_type: NodeType

    # Decision information
    input_state: Dict[str, Any]
    decision: str
    output_state: Dict[str, Any]

    # Feedback
    feedback: Optional[FeedbackInfo] = None

    # Relationships
    rule_id: Optional[str] = None
    strategy_id: Optional[str] = None
    parent_node: Optional[str] = None
    child_nodes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = {
            "node_id": self.node_id,
            "timestamp": self.timestamp.isoformat(),
            "node_type": self.node_type.value,
            "input_state": self.input_state,
            "decision": self.decision,
            "output_state": self.output_state,
            "rule_id": self.rule_id,
            "strategy_id": self.strategy_id,
            "parent_node": self.parent_node,
            "child_nodes": self.child_nodes,
        }
        if self.feedback:
            data["feedback"] = self.feedback.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionNode":
        """Create from dictionary representation."""
        return cls(
            node_id=data["node_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            node_type=NodeType(data["node_type"]),
            input_state=data["input_state"],
            decision=data["decision"],
            output_state=data["output_state"],
            feedback=FeedbackInfo.from_dict(data["feedback"]) if data.get("feedback") else None,
            rule_id=data.get("rule_id"),
            strategy_id=data.get("strategy_id"),
            parent_node=data.get("parent_node"),
            child_nodes=data.get("child_nodes", []),
        )


@dataclass
class DecisionPath:
    """
    A complete decision path from start to finish.

    Represents a sequence of decisions made by an AI agent,
    including all context, feedback, and metadata.

    Attributes:
        path_id: Unique identifier for this path
        start_time: When the path started
        end_time: When the path ended (None if still active)
        status: Current status of the path
        nodes: Sequence of decision nodes
        context: Context information for the path
        metadata: Additional metadata
    """
    path_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: PathStatus = PathStatus.ACTIVE

    # Path nodes
    nodes: List[DecisionNode] = field(default_factory=list)

    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = {
            "path_id": self.path_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "nodes": [node.to_dict() for node in self.nodes],
            "context": self.context,
            "metadata": self.metadata,
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionPath":
        """Create from dictionary representation."""
        return cls(
            path_id=data["path_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            status=PathStatus(data["status"]),
            nodes=[DecisionNode.from_dict(n) for n in data.get("nodes", [])],
            context=data.get("context", {}),
            metadata=data.get("metadata", {}),
        )

    def get_node_count(self) -> int:
        """Get total number of nodes in this path."""
        return len(self.nodes)

    def get_duration(self) -> Optional[float]:
        """Get duration of the path in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def get_node_types(self) -> Dict[str, int]:
        """Get count of each node type."""
        counts: Dict[str, int] = {}
        for node in self.nodes:
            node_type = node.node_type.value
            counts[node_type] = counts.get(node_type, 0) + 1
        return counts


class DecisionPathTracker:
    """
    Tracks decision paths for AI agent decision-making.

    This class manages the lifecycle of decision paths, including:
    - Starting new paths
    - Adding nodes to paths
    - Completing paths
    - Querying path history

    Attributes:
        storage_path: Base path for storing path data
        active_paths: Currently active paths
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        auto_save: bool = True
    ):
        """
        Initialize the path tracker.

        Args:
            storage_path: Base directory for storing path data
            auto_save: Whether to automatically save paths
        """
        self._storage_path = storage_path
        self._auto_save = auto_save
        self._active_paths: Dict[str, DecisionPath] = {}

        if storage_path and auto_save:
            self._ensure_storage_dirs()

    def _ensure_storage_dirs(self) -> None:
        """Create storage directories if they don't exist."""
        if self._storage_path:
            (self._storage_path / "active").mkdir(parents=True, exist_ok=True)
            (self._storage_path / "completed").mkdir(parents=True, exist_ok=True)
            (self._storage_path / "failed").mkdir(parents=True, exist_ok=True)

    def start_path(
        self,
        context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        path_id: Optional[str] = None
    ) -> str:
        """
        Start a new decision path.

        Args:
            context: Initial context for the path
            metadata: Optional metadata for the path
            path_id: Optional custom path ID (generated if not provided)

        Returns:
            The path ID of the new path
        """
        path_id = path_id or str(uuid.uuid4())
        now = datetime.now()

        path = DecisionPath(
            path_id=path_id,
            start_time=now,
            status=PathStatus.ACTIVE,
            context=context,
            metadata=metadata or {},
        )

        self._active_paths[path_id] = path

        if self._storage_path and self._auto_save:
            self._save_path(path, "active")

        logger.info(f"Started decision path: {path_id}")
        return path_id

    def add_node(
        self,
        path_id: str,
        node_type: NodeType,
        input_state: Dict[str, Any],
        decision: str,
        output_state: Dict[str, Any],
        rule_id: Optional[str] = None,
        strategy_id: Optional[str] = None,
        feedback: Optional[FeedbackInfo] = None,
        parent_node_id: Optional[str] = None
    ) -> str:
        """
        Add a node to an existing path.

        Args:
            path_id: ID of the path to add the node to
            node_type: Type of the node
            input_state: State before the decision
            decision: The decision made
            output_state: State after the decision
            rule_id: Optional rule that was triggered
            strategy_id: Optional strategy that was used
            feedback: Optional feedback for this decision
            parent_node_id: Optional parent node ID

        Returns:
            The node ID of the added node

        Raises:
            KeyError: If path_id is not found
        """
        if path_id not in self._active_paths:
            raise KeyError(f"Path not found: {path_id}")

        path = self._active_paths[path_id]

        # Get the last node as implicit parent if not specified
        if parent_node_id is None and path.nodes:
            parent_node_id = path.nodes[-1].node_id

        node_id = str(uuid.uuid4())
        node = DecisionNode(
            node_id=node_id,
            timestamp=datetime.now(),
            node_type=node_type,
            input_state=input_state,
            decision=decision,
            output_state=output_state,
            rule_id=rule_id,
            strategy_id=strategy_id,
            feedback=feedback,
            parent_node=parent_node_id,
            child_nodes=[],
        )

        # Update parent's child_nodes
        if parent_node_id:
            for n in path.nodes:
                if n.node_id == parent_node_id:
                    n.child_nodes.append(node_id)
                    break

        path.nodes.append(node)

        if self._storage_path and self._auto_save:
            self._save_path(path, "active")

        logger.debug(f"Added node {node_id} to path {path_id}")
        return node_id

    def complete_path(
        self,
        path_id: str,
        success: bool = True
    ) -> DecisionPath:
        """
        Complete a decision path.

        Args:
            path_id: ID of the path to complete
            success: Whether the path was successful

        Returns:
            The completed path

        Raises:
            KeyError: If path_id is not found
        """
        if path_id not in self._active_paths:
            raise KeyError(f"Path not found: {path_id}")

        path = self._active_paths[path_id]
        path.end_time = datetime.now()
        path.status = PathStatus.COMPLETED if success else PathStatus.FAILED

        # Move to appropriate directory
        if self._storage_path and self._auto_save:
            status_dir = "completed" if success else "failed"
            self._save_path(path, status_dir)

        logger.info(f"Completed decision path: {path_id} (success={success})")
        return path

    def get_path(self, path_id: str) -> Optional[DecisionPath]:
        """
        Get a path by ID.

        Args:
            path_id: ID of the path to retrieve

        Returns:
            The path if found, None otherwise
        """
        return self._active_paths.get(path_id)

    def get_active_paths(self) -> List[DecisionPath]:
        """
        Get all active paths.

        Returns:
            List of active paths
        """
        return list(self._active_paths.values())

    def get_completed_paths(
        self,
        since: Optional[datetime] = None
    ) -> List[DecisionPath]:
        """
        Get completed paths from storage.

        Args:
            since: Only return paths completed after this time

        Returns:
            List of completed paths
        """
        paths = []
        if not self._storage_path:
            return paths

        completed_dir = self._storage_path / "completed"
        if not completed_dir.exists():
            return paths

        for date_dir in completed_dir.iterdir():
            if date_dir.is_dir():
                for path_file in date_dir.glob("*.json"):
                    try:
                        with open(path_file) as f:
                            data = json.load(f)
                        path = DecisionPath.from_dict(data)
                        if since is None or (path.end_time and path.end_time > since):
                            paths.append(path)
                    except Exception as e:
                        logger.warning(f"Failed to load path from {path_file}: {e}")

        return paths

    def _save_path(self, path: DecisionPath, status: str) -> None:
        """Save a path to storage."""
        if not self._storage_path:
            return

        status_dir = self._storage_path / status
        if status == "active":
            path_file = status_dir / f"{path.path_id}.json"
        else:
            # Save in date-based directory for completed/failed
            date_dir = status_dir / path.start_time.strftime("%Y-%m-%d")
            date_dir.mkdir(parents=True, exist_ok=True)
            path_file = date_dir / f"{path.path_id}.json"

        with open(path_file, "w") as f:
            json.dump(path.to_dict(), f, indent=2)


@dataclass
class PathSummary:
    """Summary information for a decision path."""
    path_id: str
    node_count: int
    duration_seconds: Optional[float]
    status: str
    node_types: Dict[str, int]
    has_feedback: bool
    rules_used: List[str]
    strategies_used: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DecisionPathVisualizer:
    """
    Visualizes decision paths in various formats.

    Supports exporting paths to:
    - JSON: Full data representation
    - Graph: Node-edge structure for visualization libraries
    - Mermaid: Markdown-based diagram syntax
    """

    def to_json(
        self,
        path: DecisionPath,
        include_feedback: bool = True,
        include_state: bool = False
    ) -> str:
        """
        Export path to JSON format.

        Args:
            path: The path to export
            include_feedback: Include feedback information
            include_state: Include full state information

        Returns:
            JSON string representation
        """
        data = path.to_dict()

        if not include_feedback:
            for node in data.get("nodes", []):
                node.pop("feedback", None)

        if not include_state:
            for node in data.get("nodes", []):
                node.pop("input_state", None)
                node.pop("output_state", None)

        return json.dumps(data, indent=2)

    def to_graph(
        self,
        path: DecisionPath,
        format: str = "dict"
    ) -> Union[Dict, str]:
        """
        Export path as graph structure.

        Args:
            path: The path to export
            format: Output format ("dict", "mermaid", "dot")

        Returns:
            Graph representation in requested format
        """
        if format == "dict":
            return self._to_dict_graph(path)
        elif format == "mermaid":
            return self.to_mermaid(path)
        elif format == "dot":
            return self._to_dot(path)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _to_dict_graph(self, path: DecisionPath) -> Dict[str, Any]:
        """Convert path to dictionary graph representation."""
        nodes = []
        edges = []

        for node in path.nodes:
            node_data = {
                "id": node.node_id,
                "type": node.node_type.value,
                "decision": node.decision,
                "timestamp": node.timestamp.isoformat(),
            }
            if node.rule_id:
                node_data["rule_id"] = node.rule_id
            if node.strategy_id:
                node_data["strategy_id"] = node.strategy_id
            nodes.append(node_data)

            # Add edges
            for child_id in node.child_nodes:
                edges.append({
                    "from": node.node_id,
                    "to": child_id,
                })

        return {
            "path_id": path.path_id,
            "nodes": nodes,
            "edges": edges,
            "metadata": path.metadata,
        }

    def _to_dot(self, path: DecisionPath) -> str:
        """Export path as DOT (Graphviz) format."""
        lines = [
            f'digraph {path.path_id} {{',
            '  rankdir=TB;',
            '  node [shape=box];',
        ]

        # Add nodes
        for node in path.nodes:
            label = f"{node.node_type.value}\\n{node.decision[:30]}..."
            lines.append(f'  {node.node_id} [label="{label}"];')

        # Add edges
        for node in path.nodes:
            for child_id in node.child_nodes:
                lines.append(f"  {node.node_id} -> {child_id};")

        lines.append("}")
        return "\n".join(lines)

    def to_mermaid(
        self,
        path: DecisionPath,
        direction: str = "TD"
    ) -> str:
        """
        Export path as Mermaid diagram.

        Args:
            path: The path to export
            direction: Graph direction ("TD" top-down, "LR" left-right)

        Returns:
            Mermaid diagram string
        """
        valid_directions = {"TD", "LR", "BT", "RL"}
        if direction not in valid_directions:
            direction = "TD"

        lines = [
            f"flowchart {direction}",
        ]

        # Add nodes
        for node in path.nodes:
            # Escape special characters in decision text
            decision_text = node.decision.replace('"', "'").replace('\n', ' ')
            if len(decision_text) > 50:
                decision_text = decision_text[:50] + "..."

            # Use different shapes for different node types
            shape = {
                NodeType.OBSERVE: f'("{decision_text}")',
                NodeType.ORIENT: f'["{decision_text}"]',
                NodeType.DECIDE: f'[("{decision_text}")]',
                NodeType.ACT: f'{{"{decision_text}"}}',
                NodeType.LEARN: f'[""{decision_text}""]',
            }.get(node.node_type, f'["{decision_text}"]')

            lines.append(f"    {node.node_id} {shape}")

        # Add edges
        for node in path.nodes:
            for child_id in node.child_nodes:
                lines.append(f"    {node.node_id} --> {child_id}")

        return "\n".join(lines)

    def summarize(self, path: DecisionPath) -> PathSummary:
        """
        Generate a summary of a path.

        Args:
            path: The path to summarize

        Returns:
            Path summary
        """
        rules_used = []
        strategies_used = []
        has_feedback = False

        for node in path.nodes:
            if node.rule_id and node.rule_id not in rules_used:
                rules_used.append(node.rule_id)
            if node.strategy_id and node.strategy_id not in strategies_used:
                strategies_used.append(node.strategy_id)
            if node.feedback:
                has_feedback = True

        return PathSummary(
            path_id=path.path_id,
            node_count=path.get_node_count(),
            duration_seconds=path.get_duration(),
            status=path.status.value,
            node_types=path.get_node_types(),
            has_feedback=has_feedback,
            rules_used=rules_used,
            strategies_used=strategies_used,
        )


@dataclass
class PathPattern:
    """A pattern found in decision paths."""
    pattern_id: str
    pattern_type: str
    frequency: float
    nodes: List[str]
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PathStatistics:
    """Statistics for a collection of decision paths."""
    total_paths: int
    completed_paths: int
    failed_paths: int
    active_paths: int

    avg_node_count: float
    avg_duration_seconds: Optional[float]

    node_type_counts: Dict[str, int]
    success_rate: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SimilarPath:
    """A path that is similar to a target path."""
    path: DecisionPath
    similarity_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path_id": self.path.path_id,
            "similarity_score": self.similarity_score,
            "node_count": self.path.get_node_count(),
        }


@dataclass
class AnomalousPath:
    """A path detected as anomalous."""
    path: DecisionPath
    anomaly_type: str
    severity: float
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path_id": self.path.path_id,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "description": self.description,
        }


class DecisionPathAnalyzer:
    """
    Analyzes decision paths for patterns, statistics, and anomalies.

    Provides capabilities to:
    - Identify common decision patterns
    - Calculate statistics across multiple paths
    - Find similar paths to a given path
    - Detect anomalous behavior
    """

    def analyze_patterns(
        self,
        paths: List[DecisionPath]
    ) -> List[PathPattern]:
        """
        Analyze paths to find common patterns.

        Args:
            paths: List of paths to analyze

        Returns:
            List of identified patterns
        """
        patterns = []

        if not paths:
            return patterns

        # Analyze node type sequences
        type_sequences: Dict[str, int] = {}
        for path in paths:
            sequence = "-".join(n.node_type.value for n in path.nodes)
            type_sequences[sequence] = type_sequences.get(sequence, 0) + 1

        # Find common sequences
        for sequence, count in type_sequences.items():
            if count >= 2:
                node_list = sequence.split("-")
                patterns.append(PathPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="node_sequence",
                    frequency=count / len(paths),
                    nodes=node_list,
                    description=f"Sequence {sequence} appears in {count} paths",
                ))

        # Analyze rule usage patterns
        rule_usage: Dict[str, int] = {}
        for path in paths:
            for node in path.nodes:
                if node.rule_id:
                    rule_usage[node.rule_id] = rule_usage.get(node.rule_id, 0) + 1

        for rule_id, count in rule_usage.items():
            if count >= 2:
                patterns.append(PathPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="rule_usage",
                    frequency=count / len(paths),
                    nodes=[rule_id],
                    description=f"Rule {rule_id} used in {count} paths",
                ))

        return patterns

    def calculate_statistics(
        self,
        paths: List[DecisionPath]
    ) -> PathStatistics:
        """
        Calculate statistics for a collection of paths.

        Args:
            paths: List of paths to analyze

        Returns:
            Statistics object
        """
        if not paths:
            return PathStatistics(
                total_paths=0,
                completed_paths=0,
                failed_paths=0,
                active_paths=0,
                avg_node_count=0.0,
                avg_duration_seconds=None,
                node_type_counts={},
                success_rate=0.0,
            )

        completed = sum(1 for p in paths if p.status == PathStatus.COMPLETED)
        failed = sum(1 for p in paths if p.status == PathStatus.FAILED)
        active = sum(1 for p in paths if p.status == PathStatus.ACTIVE)

        node_counts = [p.get_node_count() for p in paths]
        avg_node_count = sum(node_counts) / len(node_counts)

        durations = [p.get_duration() for p in paths if p.get_duration() is not None]
        avg_duration = sum(durations) / len(durations) if durations else None

        # Count node types
        node_type_counts: Dict[str, int] = {}
        for path in paths:
            for node_type, count in path.get_node_types().items():
                node_type_counts[node_type] = node_type_counts.get(node_type, 0) + count

        success_rate = completed / (completed + failed) if (completed + failed) > 0 else 0.0

        return PathStatistics(
            total_paths=len(paths),
            completed_paths=completed,
            failed_paths=failed,
            active_paths=active,
            avg_node_count=avg_node_count,
            avg_duration_seconds=avg_duration,
            node_type_counts=node_type_counts,
            success_rate=success_rate,
        )

    def find_similar_paths(
        self,
        target_path: DecisionPath,
        all_paths: List[DecisionPath],
        threshold: float = 0.8
    ) -> List[SimilarPath]:
        """
        Find paths similar to a target path.

        Args:
            target_path: The path to find similar paths to
            all_paths: List of all available paths
            threshold: Minimum similarity score (0.0 - 1.0)

        Returns:
            List of similar paths with similarity scores
        """
        similar_paths = []

        for path in all_paths:
            if path.path_id == target_path.path_id:
                continue

            similarity = self._calculate_similarity(target_path, path)

            if similarity >= threshold:
                similar_paths.append(SimilarPath(
                    path=path,
                    similarity_score=similarity,
                ))

        # Sort by similarity descending
        similar_paths.sort(key=lambda x: x.similarity_score, reverse=True)

        return similar_paths

    def _calculate_similarity(
        self,
        path1: DecisionPath,
        path2: DecisionPath
    ) -> float:
        """
        Calculate similarity between two paths.

        Uses multiple factors:
        - Node type sequence similarity
        - Rule usage overlap
        - Strategy usage overlap
        - Node count similarity
        """
        scores = []

        # Node type sequence similarity (Jaccard)
        types1 = set(n.node_type.value for n in path1.nodes)
        types2 = set(n.node_type.value for n in path2.nodes)
        if types1 or types2:
            jaccard = len(types1 & types2) / len(types1 | types2)
            scores.append(jaccard)

        # Rule usage similarity
        rules1 = set(n.rule_id for n in path1.nodes if n.rule_id)
        rules2 = set(n.rule_id for n in path2.nodes if n.rule_id)
        if rules1 or rules2:
            rule_sim = len(rules1 & rules2) / len(rules1 | rules2) if rules1 | rules2 else 0
            scores.append(rule_sim)

        # Strategy usage similarity
        strategies1 = set(n.strategy_id for n in path1.nodes if n.strategy_id)
        strategies2 = set(n.strategy_id for n in path2.nodes if n.strategy_id)
        if strategies1 or strategies2:
            strat_sim = len(strategies1 & strategies2) / len(strategies1 | strategies2) if strategies1 | strategies2 else 0
            scores.append(strat_sim)

        # Node count similarity (inverse of relative difference)
        count1 = len(path1.nodes)
        count2 = len(path2.nodes)
        if count1 > 0 and count2 > 0:
            count_sim = 1.0 - abs(count1 - count2) / max(count1, count2)
            scores.append(count_sim)

        return sum(scores) / len(scores) if scores else 0.0

    def detect_anomalies(
        self,
        paths: List[DecisionPath]
    ) -> List[AnomalousPath]:
        """
        Detect anomalous paths in a collection.

        Args:
            paths: List of paths to analyze

        Returns:
            List of detected anomalies
        """
        anomalies = []

        if len(paths) < 3:
            return anomalies

        stats = self.calculate_statistics(paths)

        for path in paths:
            # Check for unusually long paths
            if stats.avg_node_count > 0:
                node_ratio = path.get_node_count() / stats.avg_node_count
                if node_ratio > 3.0:
                    anomalies.append(AnomalousPath(
                        path=path,
                        anomaly_type="unusually_long",
                        severity=min(1.0, (node_ratio - 3.0) / 3.0),
                        description=f"Path has {path.get_node_count()} nodes, "
                                   f"average is {stats.avg_node_count:.1f}",
                    ))

            # Check for failed paths in otherwise successful contexts
            if path.status == PathStatus.FAILED and stats.success_rate > 0.8:
                # Check if this was likely to succeed
                if path.get_node_count() < stats.avg_node_count * 0.5:
                    anomalies.append(AnomalousPath(
                        path=path,
                        anomaly_type="premature_failure",
                        severity=0.7,
                        description="Path failed earlier than expected",
                    ))

            # Check for paths with no decisions (only observe/orient)
            node_types = path.get_node_types()
            if node_types.get("decide", 0) == 0 and node_types.get("act", 0) == 0:
                if path.get_node_count() > 3:
                    anomalies.append(AnomalousPath(
                        path=path,
                        anomaly_type="no_action",
                        severity=0.5,
                        description="Path has no decide or act nodes",
                    ))

        # Sort by severity descending
        anomalies.sort(key=lambda x: x.severity, reverse=True)

        return anomalies
