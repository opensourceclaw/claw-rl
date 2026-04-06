"""
Self-Improvement - Automatic rule extraction and deployment

This module provides automatic rule extraction from learning experiences,
rule validation, deployment, and effect monitoring.
"""

from typing import Optional, Dict, Any, List, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import re
import math

from .knowledge_base import KnowledgeBase, LearningRule, RuleStatus, RulePriority


class RuleExtractionStrategy(Enum):
    """Strategy for extracting rules."""
    FREQUENCY = "frequency"  # Based on frequency of patterns
    SUCCESS_RATE = "success_rate"  # Based on success rate
    REWARD_BASED = "reward_based"  # Based on cumulative reward
    HYBRID = "hybrid"  # Combination of strategies


class RuleValidationStatus(Enum):
    """Status of rule validation."""
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_REVIEW = "needs_review"


@dataclass
class ExtractedRule:
    """A rule extracted from experiences."""
    name: str
    description: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    confidence: float
    support: int  # Number of experiences supporting this rule
    source_experiences: List[str] = field(default_factory=list)
    
    def to_learning_rule(self, rule_id: str) -> LearningRule:
        """Convert to LearningRule."""
        return LearningRule(
            rule_id=rule_id,
            name=self.name,
            description=self.description,
            condition=self.condition,
            action=self.action,
            confidence=self.confidence,
            status=RuleStatus.DRAFT,
            metadata={
                "support": self.support,
                "source_experiences": self.source_experiences,
            },
        )


@dataclass
class ValidationResult:
    """Result of rule validation."""
    status: RuleValidationStatus
    score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.status == RuleValidationStatus.VALID


@dataclass
class DeploymentResult:
    """Result of rule deployment."""
    success: bool
    rule_id: str
    deployed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class RuleExtractor:
    """
    Extracts rules from experiences.
    
    Features:
    - Multiple extraction strategies
    - Pattern recognition
    - Confidence calculation
    - Support counting
    """
    
    def __init__(
        self,
        strategy: RuleExtractionStrategy = RuleExtractionStrategy.HYBRID,
        min_support: int = 5,
        min_confidence: float = 0.6,
    ):
        """
        Initialize Rule Extractor.
        
        Args:
            strategy: Extraction strategy
            min_support: Minimum experiences to support a rule
            min_confidence: Minimum confidence threshold
        """
        self.strategy = strategy
        self.min_support = min_support
        self.min_confidence = min_confidence
    
    def extract(
        self,
        experiences: List[Dict[str, Any]],
    ) -> List[ExtractedRule]:
        """
        Extract rules from experiences.
        
        Args:
            experiences: List of experience dictionaries
            
        Returns:
            List of extracted rules
        """
        if len(experiences) < self.min_support:
            return []
        
        if self.strategy == RuleExtractionStrategy.FREQUENCY:
            return self._extract_by_frequency(experiences)
        elif self.strategy == RuleExtractionStrategy.SUCCESS_RATE:
            return self._extract_by_success_rate(experiences)
        elif self.strategy == RuleExtractionStrategy.REWARD_BASED:
            return self._extract_by_reward(experiences)
        else:  # HYBRID
            return self._extract_hybrid(experiences)
    
    def _extract_by_frequency(
        self,
        experiences: List[Dict[str, Any]],
    ) -> List[ExtractedRule]:
        """Extract rules based on frequency."""
        # Count state-action patterns
        patterns: Dict[str, List[Dict[str, Any]]] = {}
        
        for exp in experiences:
            state = exp.get("state", {})
            action = exp.get("action", {})
            
            # Create pattern key
            pattern_key = self._create_pattern_key(state, action)
            
            if pattern_key not in patterns:
                patterns[pattern_key] = []
            patterns[pattern_key].append(exp)
        
        # Extract rules from frequent patterns
        rules = []
        for pattern_key, pattern_exps in patterns.items():
            if len(pattern_exps) >= self.min_support:
                state, action = self._parse_pattern_key(pattern_key)
                
                # Calculate confidence based on positive outcomes
                positive_count = sum(1 for e in pattern_exps if e.get("reward", 0) > 0)
                confidence = positive_count / len(pattern_exps)
                
                if confidence >= self.min_confidence:
                    rule = ExtractedRule(
                        name=f"Rule_{len(rules) + 1:03d}",
                        description=f"Frequent pattern: {pattern_key}",
                        condition=state,
                        action=action,
                        confidence=confidence,
                        support=len(pattern_exps),
                        source_experiences=[e.get("experience_id", "") for e in pattern_exps[:10]],
                    )
                    rules.append(rule)
        
        return rules
    
    def _extract_by_success_rate(
        self,
        experiences: List[Dict[str, Any]],
    ) -> List[ExtractedRule]:
        """Extract rules based on success rate."""
        # Group by state
        state_groups: Dict[str, List[Dict[str, Any]]] = {}
        
        for exp in experiences:
            state = exp.get("state", {})
            state_key = self._hash_dict(state)
            
            if state_key not in state_groups:
                state_groups[state_key] = []
            state_groups[state_key].append(exp)
        
        # Find best actions for each state
        rules = []
        for state_key, state_exps in state_groups.items():
            if len(state_exps) < self.min_support:
                continue
            
            # Group by action within state
            action_groups: Dict[str, List[Dict[str, Any]]] = {}
            for exp in state_exps:
                action = exp.get("action", {})
                action_key = self._hash_dict(action)
                
                if action_key not in action_groups:
                    action_groups[action_key] = []
                action_groups[action_key].append(exp)
            
            # Find best action
            best_action = None
            best_success_rate = 0.0
            best_exps = []
            
            for action_key, action_exps in action_groups.items():
                success_count = sum(1 for e in action_exps if e.get("reward", 0) > 0)
                success_rate = success_count / len(action_exps)
                
                if success_rate > best_success_rate:
                    best_success_rate = success_rate
                    best_action = action_key
                    best_exps = action_exps
            
            if best_success_rate >= self.min_confidence and best_action:
                state = state_exps[0].get("state", {})
                action = best_exps[0].get("action", {})
                
                rule = ExtractedRule(
                    name=f"SuccessRule_{len(rules) + 1:03d}",
                    description=f"Best action for state with {best_success_rate:.1%} success rate",
                    condition=state,
                    action=action,
                    confidence=best_success_rate,
                    support=len(best_exps),
                    source_experiences=[e.get("experience_id", "") for e in best_exps[:10]],
                )
                rules.append(rule)
        
        return rules
    
    def _extract_by_reward(
        self,
        experiences: List[Dict[str, Any]],
    ) -> List[ExtractedRule]:
        """Extract rules based on cumulative reward."""
        # Group by state-action pairs
        patterns: Dict[str, Dict[str, Any]] = {}
        
        for exp in experiences:
            state = exp.get("state", {})
            action = exp.get("action", {})
            reward = exp.get("reward", 0)
            
            pattern_key = self._create_pattern_key(state, action)
            
            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    "state": state,
                    "action": action,
                    "total_reward": 0.0,
                    "count": 0,
                    "experiences": [],
                }
            
            patterns[pattern_key]["total_reward"] += reward
            patterns[pattern_key]["count"] += 1
            patterns[pattern_key]["experiences"].append(exp.get("experience_id", ""))
        
        # Extract high-reward patterns
        rules = []
        for pattern_key, pattern_data in patterns.items():
            if pattern_data["count"] >= self.min_support:
                avg_reward = pattern_data["total_reward"] / pattern_data["count"]
                
                if avg_reward > 0.5:  # Positive reward threshold
                    confidence = min(1.0, avg_reward)  # Normalize to 0-1
                    
                    rule = ExtractedRule(
                        name=f"RewardRule_{len(rules) + 1:03d}",
                        description=f"High reward pattern: avg reward = {avg_reward:.2f}",
                        condition=pattern_data["state"],
                        action=pattern_data["action"],
                        confidence=confidence,
                        support=pattern_data["count"],
                        source_experiences=pattern_data["experiences"][:10],
                    )
                    rules.append(rule)
        
        return rules
    
    def _extract_hybrid(
        self,
        experiences: List[Dict[str, Any]],
    ) -> List[ExtractedRule]:
        """Extract rules using hybrid strategy."""
        # Get rules from all strategies
        freq_rules = self._extract_by_frequency(experiences)
        success_rules = self._extract_by_success_rate(experiences)
        reward_rules = self._extract_by_reward(experiences)
        
        # Merge and deduplicate
        all_rules = {}
        for rule in freq_rules + success_rules + reward_rules:
            key = self._create_pattern_key(rule.condition, rule.action)
            if key not in all_rules or rule.confidence > all_rules[key].confidence:
                all_rules[key] = rule
        
        return list(all_rules.values())
    
    def _create_pattern_key(self, state: Dict, action: Dict) -> str:
        """Create a unique key for state-action pattern."""
        return f"{self._hash_dict(state)}:{self._hash_dict(action)}"
    
    def _parse_pattern_key(self, key: str) -> Tuple[Dict, Dict]:
        """Parse pattern key back to state and action."""
        # This is a simplified version - in practice you'd store original data
        return {}, {}
    
    def _hash_dict(self, d: Dict) -> str:
        """Create hash of dictionary."""
        import hashlib
        content = json.dumps(d, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:8]


class RuleValidator:
    """
    Validates extracted rules.
    
    Features:
    - Rule consistency check
    - Conflict detection
    - Quality scoring
    """
    
    def __init__(
        self,
        knowledge_base: Optional[KnowledgeBase] = None,
        consistency_threshold: float = 0.7,
    ):
        """
        Initialize Rule Validator.
        
        Args:
            knowledge_base: Optional knowledge base for conflict detection
            consistency_threshold: Minimum consistency score
        """
        self.knowledge_base = knowledge_base
        self.consistency_threshold = consistency_threshold
    
    def validate(self, rule: ExtractedRule) -> ValidationResult:
        """
        Validate an extracted rule.
        
        Args:
            rule: Rule to validate
            
        Returns:
            ValidationResult
        """
        issues = []
        suggestions = []
        score = 1.0
        
        # Check confidence
        if rule.confidence < 0.5:
            issues.append(f"Low confidence: {rule.confidence:.2f}")
            score *= 0.5
            suggestions.append("Collect more experiences to increase confidence")
        
        # Check support
        if rule.support < 3:
            issues.append(f"Low support: {rule.support} experiences")
            score *= 0.7
            suggestions.append("Need at least 5 supporting experiences")
        
        # Check condition
        if not rule.condition:
            issues.append("Empty condition")
            score *= 0.8
            suggestions.append("Add specific conditions")
        
        # Check action
        if not rule.action:
            issues.append("Empty action")
            score *= 0.8
            suggestions.append("Add specific actions")
        
        # Check for conflicts with existing rules
        if self.knowledge_base:
            conflicts = self._find_conflicts(rule)
            if conflicts:
                issues.append(f"Found {len(conflicts)} conflicting rules")
                score *= 0.6
                suggestions.append("Review conflicting rules before deployment")
        
        # Determine status
        if score >= self.consistency_threshold and not issues:
            status = RuleValidationStatus.VALID
        elif score >= 0.5:
            status = RuleValidationStatus.NEEDS_REVIEW
        else:
            status = RuleValidationStatus.INVALID
        
        return ValidationResult(
            status=status,
            score=score,
            issues=issues,
            suggestions=suggestions,
        )
    
    def _find_conflicts(self, rule: ExtractedRule) -> List[LearningRule]:
        """Find conflicting rules in knowledge base."""
        if not self.knowledge_base:
            return []
        
        conflicts = []
        existing_rules = self.knowledge_base.find_rules(
            condition=rule.condition,
            status=RuleStatus.ACTIVE,
        )
        
        for existing in existing_rules:
            # Check if actions conflict
            if existing.action != rule.action:
                conflicts.append(existing)
        
        return conflicts


class SelfImprovement:
    """
    Main self-improvement system.
    
    Features:
    - Automatic rule extraction
    - Rule validation
    - Rule deployment
    - Effect monitoring
    
    Example:
        >>> kb = KnowledgeBase()
        >>> si = SelfImprovement(knowledge_base=kb)
        >>> 
        >>> # Extract rules from experiences
        >>> experiences = [...]
        >>> rules = si.extract_rules(experiences)
        >>> 
        >>> # Validate and deploy
        >>> for rule in rules:
        ...     result = si.deploy_rule(rule)
        ...     if result.success:
        ...         print(f"Deployed: {rule.name}")
    """
    
    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        extraction_strategy: RuleExtractionStrategy = RuleExtractionStrategy.HYBRID,
        min_support: int = 5,
        min_confidence: float = 0.6,
        auto_deploy: bool = False,
        data_dir: Optional[Path] = None,
    ):
        """
        Initialize Self-Improvement.
        
        Args:
            knowledge_base: Knowledge base for rule storage
            extraction_strategy: Strategy for rule extraction
            min_support: Minimum experiences to support a rule
            min_confidence: Minimum confidence threshold
            auto_deploy: Automatically deploy valid rules
            data_dir: Optional directory for persistence
        """
        self.knowledge_base = knowledge_base
        self.auto_deploy = auto_deploy
        self.data_dir = data_dir or Path.home() / ".openclaw" / "workspace" / "claw-rl" / "improvement"
        
        self.extractor = RuleExtractor(
            strategy=extraction_strategy,
            min_support=min_support,
            min_confidence=min_confidence,
        )
        
        self.validator = RuleValidator(
            knowledge_base=knowledge_base,
        )
        
        self._extraction_history: List[Dict[str, Any]] = []
        self._deployment_history: List[DeploymentResult] = []
        
        # Create data directory
        if self.data_dir:
            self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_rules(
        self,
        experiences: List[Dict[str, Any]],
    ) -> List[ExtractedRule]:
        """
        Extract rules from experiences.
        
        Args:
            experiences: List of experience dictionaries
            
        Returns:
            List of extracted rules
        """
        rules = self.extractor.extract(experiences)
        
        # Record extraction
        self._extraction_history.append({
            "timestamp": datetime.now().isoformat(),
            "experience_count": len(experiences),
            "rules_extracted": len(rules),
            "strategy": self.extractor.strategy.value,
        })
        
        return rules
    
    def validate_rule(self, rule: ExtractedRule) -> ValidationResult:
        """
        Validate an extracted rule.
        
        Args:
            rule: Rule to validate
            
        Returns:
            ValidationResult
        """
        return self.validator.validate(rule)
    
    def deploy_rule(
        self,
        rule: ExtractedRule,
        validate: bool = True,
    ) -> DeploymentResult:
        """
        Deploy a rule to the knowledge base.
        
        Args:
            rule: Rule to deploy
            validate: Whether to validate before deployment
            
        Returns:
            DeploymentResult
        """
        # Validate if requested
        if validate:
            validation = self.validate_rule(rule)
            if not validation.is_valid():
                return DeploymentResult(
                    success=False,
                    rule_id="",
                    message=f"Validation failed: {validation.status.value}",
                    metadata={"issues": validation.issues},
                )
        
        # Generate rule ID
        rule_id = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self._deployment_history):03d}"
        
        # Convert to LearningRule
        learning_rule = rule.to_learning_rule(rule_id)
        
        # Add to knowledge base
        success = self.knowledge_base.add_rule(learning_rule)
        
        # Record deployment
        result = DeploymentResult(
            success=success,
            rule_id=rule_id,
            message="Deployed successfully" if success else "Failed to add to knowledge base",
            metadata={
                "name": rule.name,
                "confidence": rule.confidence,
                "support": rule.support,
            },
        )
        
        self._deployment_history.append(result)
        
        # Persist
        if self.data_dir:
            self._save_deployment(result)
        
        return result
    
    def monitor_effect(
        self,
        rule_id: str,
        experiences: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Monitor the effect of a deployed rule.
        
        Args:
            rule_id: ID of the rule to monitor
            experiences: Recent experiences
            
        Returns:
            Effect metrics
        """
        rule = self.knowledge_base.get_rule(rule_id)
        if not rule:
            return {"error": f"Rule {rule_id} not found"}
        
        # Find experiences matching the rule condition
        matching_experiences = []
        for exp in experiences:
            state = exp.get("state", {})
            if self._matches_condition(state, rule.condition):
                matching_experiences.append(exp)
        
        if not matching_experiences:
            return {
                "rule_id": rule_id,
                "matching_experiences": 0,
                "message": "No matching experiences found",
            }
        
        # Calculate metrics
        total_reward = sum(e.get("reward", 0) for e in matching_experiences)
        avg_reward = total_reward / len(matching_experiences)
        positive_count = sum(1 for e in matching_experiences if e.get("reward", 0) > 0)
        success_rate = positive_count / len(matching_experiences)
        
        # Update rule statistics
        rule.usage_count += len(matching_experiences)
        rule.success_count += positive_count
        rule.confidence = (rule.confidence + success_rate) / 2  # Running average
        
        self.knowledge_base.update_rule(rule)
        
        return {
            "rule_id": rule_id,
            "matching_experiences": len(matching_experiences),
            "total_reward": total_reward,
            "avg_reward": avg_reward,
            "success_rate": success_rate,
            "rule_confidence": rule.confidence,
            "rule_success_rate": rule.success_rate,
        }
    
    def run_improvement_cycle(
        self,
        experiences: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Run a complete improvement cycle.
        
        Args:
            experiences: List of experiences to learn from
            
        Returns:
            Cycle results
        """
        # Extract rules
        rules = self.extract_rules(experiences)
        
        # Validate and deploy
        deployed = []
        for rule in rules:
            validation = self.validate_rule(rule)
            
            if validation.is_valid() or self.auto_deploy:
                result = self.deploy_rule(rule, validate=False)
                if result.success:
                    deployed.append({
                        "rule_id": result.rule_id,
                        "name": rule.name,
                        "confidence": rule.confidence,
                    })
        
        return {
            "experiences_processed": len(experiences),
            "rules_extracted": len(rules),
            "rules_deployed": len(deployed),
            "deployed_rules": deployed,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get self-improvement statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "extractions": len(self._extraction_history),
            "deployments": len(self._deployment_history),
            "successful_deployments": sum(1 for d in self._deployment_history if d.success),
            "extraction_history": self._extraction_history[-10:],  # Last 10
            "deployment_history": [
                {
                    "rule_id": d.rule_id,
                    "success": d.success,
                    "timestamp": d.deployed_at,
                }
                for d in self._deployment_history[-10:]  # Last 10
            ],
        }
    
    def _matches_condition(self, state: Dict, condition: Dict) -> bool:
        """Check if state matches condition."""
        for key, value in condition.items():
            if key not in state or state[key] != value:
                return False
        return True
    
    def _save_deployment(self, result: DeploymentResult) -> None:
        """Save deployment to disk."""
        if not self.data_dir:
            return
        
        deployment_file = self.data_dir / f"deployment_{result.rule_id}.json"
        with open(deployment_file, "w", encoding="utf-8") as f:
            json.dump({
                "success": result.success,
                "rule_id": result.rule_id,
                "deployed_at": result.deployed_at,
                "message": result.message,
                "metadata": result.metadata,
            }, f, indent=2, ensure_ascii=False)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SelfImprovement("
            f"extractions={len(self._extraction_history)}, "
            f"deployments={len(self._deployment_history)}"
            f")"
        )
