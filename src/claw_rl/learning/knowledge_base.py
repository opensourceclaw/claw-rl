"""
Knowledge Base - Learning Rules Storage and Management

This module provides a knowledge base for storing, indexing, and managing
learning rules extracted from the learning process.
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import hashlib
import threading


class RuleStatus(Enum):
    """Status of a learning rule."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DRAFT = "draft"


class RulePriority(Enum):
    """Priority of a learning rule."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class RuleConflictStrategy(Enum):
    """Strategy for resolving rule conflicts."""
    HIGHEST_PRIORITY = "highest_priority"
    NEWEST_WINS = "newest_wins"
    MOST_SPECIFIC = "most_specific"
    MANUAL = "manual"


@dataclass
class LearningRule:
    """
    A learning rule extracted from the learning process.
    
    Attributes:
        rule_id: Unique identifier for the rule
        name: Human-readable name
        description: Detailed description
        condition: Condition when the rule applies
        action: Action to take when condition is met
        priority: Rule priority
        status: Current status
        confidence: Confidence score (0.0 - 1.0)
        usage_count: Number of times the rule has been applied
        success_count: Number of successful applications
        created_at: Creation timestamp
        updated_at: Last update timestamp
        expires_at: Optional expiration timestamp
        tags: Tags for categorization
        metadata: Additional metadata
    """
    rule_id: str
    name: str
    description: str = ""
    condition: Dict[str, Any] = field(default_factory=dict)
    action: Dict[str, Any] = field(default_factory=dict)
    priority: RulePriority = RulePriority.MEDIUM
    status: RuleStatus = RuleStatus.ACTIVE
    confidence: float = 0.5
    usage_count: int = 0
    success_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "condition": self.condition,
            "action": self.action,
            "priority": self.priority.value,
            "status": self.status.value,
            "confidence": self.confidence,
            "usage_count": self.usage_count,
            "success_count": self.success_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "tags": self.tags,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningRule':
        """Create from dictionary."""
        return cls(
            rule_id=data["rule_id"],
            name=data["name"],
            description=data.get("description", ""),
            condition=data.get("condition", {}),
            action=data.get("action", {}),
            priority=RulePriority(data.get("priority", 3)),
            status=RuleStatus(data.get("status", "active")),
            confidence=data.get("confidence", 0.5),
            usage_count=data.get("usage_count", 0),
            success_count=data.get("success_count", 0),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            expires_at=data.get("expires_at"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count
    
    @property
    def is_expired(self) -> bool:
        """Check if the rule is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > datetime.fromisoformat(self.expires_at)
    
    def update_usage(self, success: bool) -> None:
        """Update usage statistics."""
        self.usage_count += 1
        if success:
            self.success_count += 1
        self.updated_at = datetime.now().isoformat()


class KnowledgeBase:
    """
    Knowledge base for storing and managing learning rules.
    
    Features:
    - Rule storage and retrieval
    - Indexing for fast search
    - Rule lifecycle management
    - Conflict resolution
    - Persistence support
    
    Example:
        >>> kb = KnowledgeBase()
        >>> 
        >>> # Create a rule
        >>> rule = LearningRule(
        ...     rule_id="rule_001",
        ...     name="Prefer concise responses",
        ...     condition={"context": "chat", "query_length": "short"},
        ...     action={"response_style": "concise"},
        ...     priority=RulePriority.HIGH,
        ... )
        >>> kb.add_rule(rule)
        >>> 
        >>> # Find applicable rules
        >>> rules = kb.find_rules({"context": "chat"})
    """
    
    def __init__(
        self,
        data_dir: Optional[Path] = None,
        conflict_strategy: RuleConflictStrategy = RuleConflictStrategy.HIGHEST_PRIORITY,
        max_rules: int = 10000,
    ):
        """
        Initialize Knowledge Base.
        
        Args:
            data_dir: Optional directory for persistence
            conflict_strategy: Strategy for resolving conflicts
            max_rules: Maximum number of rules to store
        """
        self.data_dir = data_dir or Path.home() / ".openclaw" / "workspace" / "claw-rl" / "knowledge"
        self.conflict_strategy = conflict_strategy
        self.max_rules = max_rules
        
        self._rules: Dict[str, LearningRule] = {}
        self._index: Dict[str, List[str]] = {}  # tag -> rule_ids
        self._condition_index: Dict[str, List[str]] = {}  # condition_key -> rule_ids
        self._lock = threading.RLock()
        
        # Create data directory
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing rules
        self._load()
    
    def add_rule(self, rule: LearningRule) -> bool:
        """
        Add a rule to the knowledge base.
        
        Args:
            rule: Rule to add
            
        Returns:
            True if added successfully, False otherwise
        """
        with self._lock:
            # Check if rule already exists
            if rule.rule_id in self._rules:
                return False
            
            # Check max rules limit
            if len(self._rules) >= self.max_rules:
                # Remove lowest priority rule
                self._remove_lowest_priority_rule()
            
            # Add rule
            self._rules[rule.rule_id] = rule
            
            # Update indexes
            self._index_rule(rule)
            
            # Persist
            self._save_rule(rule)
            
            return True
    
    def update_rule(self, rule: LearningRule) -> bool:
        """
        Update an existing rule.
        
        Args:
            rule: Rule with updated data
            
        Returns:
            True if updated successfully, False if rule not found
        """
        with self._lock:
            if rule.rule_id not in self._rules:
                return False
            
            # Remove old indexes
            old_rule = self._rules[rule.rule_id]
            self._remove_rule_indexes(old_rule)
            
            # Update rule
            rule.updated_at = datetime.now().isoformat()
            self._rules[rule.rule_id] = rule
            
            # Add new indexes
            self._index_rule(rule)
            
            # Persist
            self._save_rule(rule)
            
            return True
    
    def delete_rule(self, rule_id: str) -> bool:
        """
        Delete a rule from the knowledge base.
        
        Args:
            rule_id: ID of rule to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if rule_id not in self._rules:
                return False
            
            rule = self._rules[rule_id]
            
            # Remove indexes
            self._remove_rule_indexes(rule)
            
            # Remove rule
            del self._rules[rule_id]
            
            # Delete from disk
            rule_file = self.data_dir / f"{rule_id}.json"
            if rule_file.exists():
                rule_file.unlink()
            
            return True
    
    def get_rule(self, rule_id: str) -> Optional[LearningRule]:
        """
        Get a rule by ID.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Rule if found, None otherwise
        """
        return self._rules.get(rule_id)
    
    def find_rules(
        self,
        condition: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[RuleStatus] = None,
        min_confidence: float = 0.0,
        limit: int = 100,
    ) -> List[LearningRule]:
        """
        Find rules matching criteria.
        
        Args:
            condition: Condition to match
            tags: Tags to match (any match)
            status: Status to filter
            min_confidence: Minimum confidence
            limit: Maximum rules to return
            
        Returns:
            List of matching rules
        """
        with self._lock:
            results = []
            
            for rule in self._rules.values():
                # Check status
                if status and rule.status != status:
                    continue
                
                # Check confidence
                if rule.confidence < min_confidence:
                    continue
                
                # Check expiration
                if rule.is_expired:
                    continue
                
                # Check tags
                if tags and not any(tag in rule.tags for tag in tags):
                    continue
                
                # Check condition
                if condition and not self._match_condition(rule, condition):
                    continue
                
                results.append(rule)
                
                if len(results) >= limit:
                    break
            
            # Sort by priority (highest first)
            results.sort(key=lambda r: r.priority.value)
            
            return results
    
    def resolve_conflicts(
        self,
        rules: List[LearningRule],
    ) -> LearningRule:
        """
        Resolve conflicts between multiple matching rules.
        
        Args:
            rules: List of conflicting rules
            
        Returns:
            The winning rule based on conflict strategy
            
        Raises:
            ValueError: If no rules provided or manual resolution required
        """
        if not rules:
            raise ValueError("No rules to resolve")
        
        if len(rules) == 1:
            return rules[0]
        
        if self.conflict_strategy == RuleConflictStrategy.HIGHEST_PRIORITY:
            return min(rules, key=lambda r: r.priority.value)
        
        elif self.conflict_strategy == RuleConflictStrategy.NEWEST_WINS:
            return max(rules, key=lambda r: r.updated_at)
        
        elif self.conflict_strategy == RuleConflictStrategy.MOST_SPECIFIC:
            return max(rules, key=lambda r: len(r.condition))
        
        else:  # MANUAL
            raise ValueError(
                f"Manual conflict resolution required for {len(rules)} rules"
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total_rules = len(self._rules)
            active_rules = sum(1 for r in self._rules.values() if r.status == RuleStatus.ACTIVE)
            total_usage = sum(r.usage_count for r in self._rules.values())
            total_success = sum(r.success_count for r in self._rules.values())
            
            return {
                "total_rules": total_rules,
                "active_rules": active_rules,
                "deprecated_rules": sum(1 for r in self._rules.values() if r.status == RuleStatus.DEPRECATED),
                "archived_rules": sum(1 for r in self._rules.values() if r.status == RuleStatus.ARCHIVED),
                "draft_rules": sum(1 for r in self._rules.values() if r.status == RuleStatus.DRAFT),
                "total_usage": total_usage,
                "total_success": total_success,
                "overall_success_rate": total_success / total_usage if total_usage > 0 else 0.0,
                "avg_confidence": sum(r.confidence for r in self._rules.values()) / total_rules if total_rules > 0 else 0.0,
                "tag_count": len(self._index),
            }
    
    def prune_expired_rules(self) -> int:
        """
        Remove expired rules from the knowledge base.
        
        Returns:
            Number of rules removed
        """
        with self._lock:
            expired_ids = [
                rule_id for rule_id, rule in self._rules.items()
                if rule.is_expired
            ]
            
            for rule_id in expired_ids:
                self.delete_rule(rule_id)
            
            return len(expired_ids)
    
    def deprecate_low_performing_rules(
        self,
        min_usage: int = 10,
        min_success_rate: float = 0.3,
    ) -> int:
        """
        Deprecate rules with low performance.
        
        Args:
            min_usage: Minimum usage count to consider
            min_success_rate: Minimum success rate threshold
            
        Returns:
            Number of rules deprecated
        """
        with self._lock:
            deprecated_count = 0
            
            for rule in self._rules.values():
                if rule.usage_count >= min_usage and rule.success_rate < min_success_rate:
                    rule.status = RuleStatus.DEPRECATED
                    rule.updated_at = datetime.now().isoformat()
                    self._save_rule(rule)
                    deprecated_count += 1
            
            return deprecated_count
    
    def _index_rule(self, rule: LearningRule) -> None:
        """Index a rule for fast retrieval."""
        # Index by tags
        for tag in rule.tags:
            if tag not in self._index:
                self._index[tag] = []
            self._index[tag].append(rule.rule_id)
        
        # Index by condition keys
        for key in rule.condition.keys():
            condition_key = f"condition:{key}"
            if condition_key not in self._condition_index:
                self._condition_index[condition_key] = []
            self._condition_index[condition_key].append(rule.rule_id)
    
    def _remove_rule_indexes(self, rule: LearningRule) -> None:
        """Remove rule from indexes."""
        # Remove from tag index
        for tag in rule.tags:
            if tag in self._index and rule.rule_id in self._index[tag]:
                self._index[tag].remove(rule.rule_id)
                if not self._index[tag]:
                    del self._index[tag]
        
        # Remove from condition index
        for key in rule.condition.keys():
            condition_key = f"condition:{key}"
            if condition_key in self._condition_index and rule.rule_id in self._condition_index[condition_key]:
                self._condition_index[condition_key].remove(rule.rule_id)
                if not self._condition_index[condition_key]:
                    del self._condition_index[condition_key]
    
    def _remove_lowest_priority_rule(self) -> None:
        """Remove the lowest priority rule."""
        if not self._rules:
            return
        
        # Find lowest priority rule (excluding critical)
        lowest_rule = max(
            (r for r in self._rules.values() if r.priority != RulePriority.CRITICAL),
            key=lambda r: r.priority.value,
            default=None,
        )
        
        if lowest_rule:
            self.delete_rule(lowest_rule.rule_id)
    
    def _match_condition(self, rule: LearningRule, condition: Dict[str, Any]) -> bool:
        """Check if a condition matches a rule's condition."""
        for key, value in condition.items():
            if key not in rule.condition:
                return False
            if rule.condition[key] != value:
                return False
        return True
    
    def _save_rule(self, rule: LearningRule) -> None:
        """Save a rule to disk."""
        rule_file = self.data_dir / f"{rule.rule_id}.json"
        with open(rule_file, "w", encoding="utf-8") as f:
            json.dump(rule.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _load(self) -> None:
        """Load rules from disk."""
        for rule_file in self.data_dir.glob("*.json"):
            try:
                with open(rule_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                rule = LearningRule.from_dict(data)
                self._rules[rule.rule_id] = rule
                self._index_rule(rule)
            except (json.JSONDecodeError, KeyError):
                continue
    
    def __len__(self) -> int:
        """Return number of rules."""
        return len(self._rules)
    
    def __contains__(self, rule_id: str) -> bool:
        """Check if rule exists."""
        return rule_id in self._rules
    
    def __repr__(self) -> str:
        """String representation."""
        return f"KnowledgeBase(rules={len(self._rules)}, tags={len(self._index)})"
