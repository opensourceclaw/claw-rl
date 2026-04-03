"""
A/B Testing Framework - Experiment design and analysis

This module provides A/B testing capabilities for comparing
different strategy configurations and measuring their effectiveness.
"""

from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import hashlib
import random


class ExperimentStatus(Enum):
    """Status of an experiment."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class ExperimentVariant:
    """A variant in an A/B test."""
    name: str
    config: Dict[str, Any]           # Strategy configuration for this variant
    description: str = ""
    
    # Statistics
    assignment_count: int = 0        # Number of users assigned
    total_events: int = 0            # Total events tracked
    positive_events: int = 0         # Positive outcome events
    negative_events: int = 0         # Negative outcome events
    
    # Metrics
    conversion_rate: float = 0.0     # Positive / total
    confidence_interval: tuple = (0.0, 0.0)  # 95% CI
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "config": self.config,
            "description": self.description,
            "assignment_count": self.assignment_count,
            "total_events": self.total_events,
            "positive_events": self.positive_events,
            "negative_events": self.negative_events,
            "conversion_rate": self.conversion_rate,
            "confidence_interval": self.confidence_interval,
        }


@dataclass
class Experiment:
    """An A/B test experiment."""
    id: str
    name: str
    description: str
    variants: List[ExperimentVariant]
    status: str = ExperimentStatus.DRAFT.value
    
    # Configuration
    traffic_allocation: float = 1.0   # Fraction of traffic to include
    variant_split: List[float] = field(default_factory=list)  # e.g., [0.5, 0.5] for 50/50
    
    # Timing
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    
    # Target metrics
    primary_metric: str = "conversion_rate"
    minimum_detectable_effect: float = 0.05  # 5% minimum detectable effect
    statistical_power: float = 0.8            # 80% power
    significance_level: float = 0.05          # 5% significance level
    
    # Results
    winner: Optional[str] = None
    conclusion: Optional[str] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "variants": [v.to_dict() for v in self.variants],
            "status": self.status,
            "traffic_allocation": self.traffic_allocation,
            "variant_split": self.variant_split,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "primary_metric": self.primary_metric,
            "minimum_detectable_effect": self.minimum_detectable_effect,
            "statistical_power": self.statistical_power,
            "significance_level": self.significance_level,
            "winner": self.winner,
            "conclusion": self.conclusion,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class ExperimentResult:
    """Result of an experiment analysis."""
    experiment_id: str
    analyzed_at: str
    
    # Variant comparison
    variants: List[Dict[str, Any]]
    
    # Statistical significance
    is_significant: bool
    p_value: float
    confidence_level: float
    
    # Recommendation
    winner: Optional[str]
    recommendation: str
    
    # Details
    sample_size: int
    effect_size: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "experiment_id": self.experiment_id,
            "analyzed_at": self.analyzed_at,
            "variants": self.variants,
            "is_significant": self.is_significant,
            "p_value": self.p_value,
            "confidence_level": self.confidence_level,
            "winner": self.winner,
            "recommendation": self.recommendation,
            "sample_size": self.sample_size,
            "effect_size": self.effect_size,
        }


class ABTestingFramework:
    """
    A/B Testing Framework for strategy experiments.
    
    Provides:
    - Experiment creation and management
    - Variant assignment (deterministic hashing)
    - Event tracking
    - Statistical analysis
    - Winner determination
    
    Example:
        >>> ab = ABTestingFramework()
        >>> 
        >>> # Create experiment
        >>> experiment = ab.create_experiment(
        ...     name="Learning Rate Test",
        ...     variants=[
        ...         {"name": "control", "config": {"learning_rate": 0.1}},
        ...         {"name": "treatment", "config": {"learning_rate": 0.2}},
        ...     ],
        ... )
        >>> 
        >>> # Assign user to variant
        >>> variant = ab.assign_variant(experiment.id, "user-123")
        >>> print(variant.name)
        'control'
        >>> 
        >>> # Track event
        >>> ab.track_event(experiment.id, "user-123", outcome="positive")
        >>> 
        >>> # Analyze results
        >>> result = ab.analyze(experiment.id)
        >>> print(result.winner)
        'treatment'
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize A/B Testing Framework.
        
        Args:
            data_dir: Directory for storing experiment data
        """
        self.data_dir = data_dir or os.path.expanduser("~/.openclaw/workspace/claw-rl/data/ab_tests")
        self.experiments: Dict[str, Experiment] = {}
        
        # Event tracking
        self._events: Dict[str, List[Dict[str, Any]]] = {}  # experiment_id -> events
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing experiments
        self._load_experiments()
    
    def _load_experiments(self) -> None:
        """Load existing experiments from disk."""
        experiments_file = os.path.join(self.data_dir, "experiments.json")
        if os.path.exists(experiments_file):
            try:
                with open(experiments_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for exp_data in data.get("experiments", []):
                        variants = [
                            ExperimentVariant(**v) for v in exp_data.get("variants", [])
                        ]
                        exp_data["variants"] = variants
                        self.experiments[exp_data["id"]] = Experiment(**exp_data)
            except (json.JSONDecodeError, KeyError):
                pass
    
    def _save_experiments(self) -> None:
        """Save experiments to disk."""
        experiments_file = os.path.join(self.data_dir, "experiments.json")
        data = {
            "experiments": [exp.to_dict() for exp in self.experiments.values()],
            "updated_at": datetime.now().isoformat(),
        }
        with open(experiments_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_experiment(
        self,
        name: str,
        variants: List[Dict[str, Any]],
        description: str = "",
        traffic_allocation: float = 1.0,
        variant_split: Optional[List[float]] = None,
    ) -> Experiment:
        """
        Create a new A/B test experiment.
        
        Args:
            name: Experiment name
            variants: List of variant configs [{"name": "control", "config": {...}}, ...]
            description: Experiment description
            traffic_allocation: Fraction of traffic to include (0.0 to 1.0)
            variant_split: Split ratio for variants (e.g., [0.5, 0.5])
        
        Returns:
            Created Experiment
        """
        # Generate experiment ID
        exp_id = hashlib.sha256(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Create variants
        exp_variants = []
        for v in variants:
            exp_variants.append(ExperimentVariant(
                name=v["name"],
                config=v.get("config", {}),
                description=v.get("description", ""),
            ))
        
        # Default variant split (equal distribution)
        if variant_split is None:
            variant_split = [1.0 / len(exp_variants)] * len(exp_variants)
        
        # Normalize variant split
        total = sum(variant_split)
        variant_split = [s / total for s in variant_split]
        
        experiment = Experiment(
            id=exp_id,
            name=name,
            description=description,
            variants=exp_variants,
            traffic_allocation=traffic_allocation,
            variant_split=variant_split,
        )
        
        self.experiments[exp_id] = experiment
        self._events[exp_id] = []
        self._save_experiments()
        
        return experiment
    
    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start an experiment.
        
        Args:
            experiment_id: Experiment ID
        
        Returns:
            True if started successfully
        """
        exp = self.experiments.get(experiment_id)
        if not exp:
            return False
        
        exp.status = ExperimentStatus.RUNNING.value
        exp.start_time = datetime.now().isoformat()
        exp.updated_at = datetime.now().isoformat()
        self._save_experiments()
        
        return True
    
    def pause_experiment(self, experiment_id: str) -> bool:
        """
        Pause an experiment.
        
        Args:
            experiment_id: Experiment ID
        
        Returns:
            True if paused successfully
        """
        exp = self.experiments.get(experiment_id)
        if not exp:
            return False
        
        exp.status = ExperimentStatus.PAUSED.value
        exp.updated_at = datetime.now().isoformat()
        self._save_experiments()
        
        return True
    
    def complete_experiment(self, experiment_id: str, winner: Optional[str] = None) -> bool:
        """
        Complete an experiment.
        
        Args:
            experiment_id: Experiment ID
            winner: Name of winning variant (optional)
        
        Returns:
            True if completed successfully
        """
        exp = self.experiments.get(experiment_id)
        if not exp:
            return False
        
        exp.status = ExperimentStatus.COMPLETED.value
        exp.end_time = datetime.now().isoformat()
        exp.winner = winner
        exp.updated_at = datetime.now().isoformat()
        self._save_experiments()
        
        return True
    
    def assign_variant(
        self,
        experiment_id: str,
        user_id: str,
    ) -> Optional[ExperimentVariant]:
        """
        Assign a user to a variant.
        
        Uses deterministic hashing for consistent assignment.
        
        Args:
            experiment_id: Experiment ID
            user_id: User identifier
        
        Returns:
            Assigned variant or None if experiment not found
        """
        exp = self.experiments.get(experiment_id)
        if not exp or exp.status != ExperimentStatus.RUNNING.value:
            return None
        
        # Check traffic allocation
        hash_val = int(hashlib.sha256(f"{experiment_id}_{user_id}".encode()).hexdigest(), 16)
        if (hash_val % 10000) / 10000 >= exp.traffic_allocation:
            return None
        
        # Determine variant using hash
        variant_hash = hash_val % 10000 / 10000
        cumulative = 0.0
        for i, split in enumerate(exp.variant_split):
            cumulative += split
            if variant_hash < cumulative:
                exp.variants[i].assignment_count += 1
                exp.updated_at = datetime.now().isoformat()
                self._save_experiments()
                return exp.variants[i]
        
        # Fallback to last variant
        return exp.variants[-1]
    
    def track_event(
        self,
        experiment_id: str,
        user_id: str,
        variant_name: Optional[str] = None,
        outcome: Literal["positive", "negative", "neutral"] = "neutral",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Track an event for an experiment.
        
        Args:
            experiment_id: Experiment ID
            user_id: User identifier
            variant_name: Variant name (auto-detected if not provided)
            outcome: Event outcome
            metadata: Additional event metadata
        
        Returns:
            True if tracked successfully
        """
        exp = self.experiments.get(experiment_id)
        if not exp:
            return False
        
        # Find variant if not provided
        if variant_name is None:
            variant = self.assign_variant(experiment_id, user_id)
            if variant:
                variant_name = variant.name
            else:
                return False
        
        # Update variant statistics
        for v in exp.variants:
            if v.name == variant_name:
                v.total_events += 1
                if outcome == "positive":
                    v.positive_events += 1
                elif outcome == "negative":
                    v.negative_events += 1
                break
        
        # Record event
        event = {
            "user_id": user_id,
            "variant": variant_name,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        if experiment_id not in self._events:
            self._events[experiment_id] = []
        self._events[experiment_id].append(event)
        
        exp.updated_at = datetime.now().isoformat()
        self._save_experiments()
        
        return True
    
    def analyze(self, experiment_id: str) -> Optional[ExperimentResult]:
        """
        Analyze experiment results.
        
        Args:
            experiment_id: Experiment ID
        
        Returns:
            ExperimentResult or None if experiment not found
        """
        exp = self.experiments.get(experiment_id)
        if not exp:
            return None
        
        # Calculate conversion rates
        for variant in exp.variants:
            if variant.total_events > 0:
                variant.conversion_rate = variant.positive_events / variant.total_events
                # Simple confidence interval (Wilson score)
                variant.confidence_interval = self._wilson_score_interval(
                    variant.positive_events,
                    variant.total_events,
                )
        
        # Find best variant
        best_variant = max(exp.variants, key=lambda v: v.conversion_rate)
        
        # Calculate statistical significance (simple z-test)
        is_significant = False
        p_value = 1.0
        
        if len(exp.variants) >= 2:
            control = exp.variants[0]  # Assume first is control
            treatment = exp.variants[1]  # Assume second is treatment
            
            if control.total_events > 0 and treatment.total_events > 0:
                p_value = self._z_test(
                    control.positive_events, control.total_events,
                    treatment.positive_events, treatment.total_events,
                )
                is_significant = p_value < exp.significance_level
        
        # Calculate effect size
        effect_size = 0.0
        if len(exp.variants) >= 2:
            control_rate = exp.variants[0].conversion_rate
            if control_rate > 0:
                effect_size = (best_variant.conversion_rate - control_rate) / control_rate
        
        # Build recommendation
        if is_significant:
            recommendation = f"Variant '{best_variant.name}' is statistically significant winner with {best_variant.conversion_rate:.1%} conversion rate."
        else:
            recommendation = f"No statistically significant difference found. Continue experiment or declare '{best_variant.name}' as practical winner with {best_variant.conversion_rate:.1%} conversion rate."
        
        return ExperimentResult(
            experiment_id=experiment_id,
            analyzed_at=datetime.now().isoformat(),
            variants=[v.to_dict() for v in exp.variants],
            is_significant=is_significant,
            p_value=p_value,
            confidence_level=1 - exp.significance_level,
            winner=best_variant.name if is_significant or best_variant.conversion_rate > 0 else None,
            recommendation=recommendation,
            sample_size=sum(v.total_events for v in exp.variants),
            effect_size=effect_size,
        )
    
    def _wilson_score_interval(
        self,
        successes: int,
        trials: int,
        confidence: float = 0.95,
    ) -> tuple:
        """
        Calculate Wilson score confidence interval.
        
        Args:
            successes: Number of successes
            trials: Total trials
            confidence: Confidence level (default 0.95)
        
        Returns:
            (lower, upper) confidence interval
        """
        if trials == 0:
            return (0.0, 0.0)
        
        import math
        
        p = successes / trials
        z = 1.96  # 95% confidence
        
        denominator = 1 + z**2 / trials
        center = (p + z**2 / (2 * trials)) / denominator
        margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * trials)) / trials) / denominator
        
        return (max(0, center - margin), min(1, center + margin))
    
    def _z_test(
        self,
        successes_a: int,
        trials_a: int,
        successes_b: int,
        trials_b: int,
    ) -> float:
        """
        Perform two-proportion z-test.
        
        Args:
            successes_a: Successes in group A
            trials_a: Trials in group A
            successes_b: Successes in group B
            trials_b: Trials in group B
        
        Returns:
            p-value
        """
        import math
        
        if trials_a == 0 or trials_b == 0:
            return 1.0
        
        p_a = successes_a / trials_a
        p_b = successes_b / trials_b
        
        # Pooled proportion
        p_pooled = (successes_a + successes_b) / (trials_a + trials_b)
        
        if p_pooled == 0 or p_pooled == 1:
            return 1.0
        
        # Standard error
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1/trials_a + 1/trials_b))
        
        if se == 0:
            return 1.0
        
        # Z-score
        z = abs(p_a - p_b) / se
        
        # P-value (two-tailed)
        # Using approximation for normal distribution
        p_value = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))
        
        return p_value
    
    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """
        Get an experiment by ID.
        
        Args:
            experiment_id: Experiment ID
        
        Returns:
            Experiment or None if not found
        """
        return self.experiments.get(experiment_id)
    
    def list_experiments(
        self,
        status: Optional[str] = None,
    ) -> List[Experiment]:
        """
        List experiments.
        
        Args:
            status: Filter by status (optional)
        
        Returns:
            List of experiments
        """
        if status:
            return [exp for exp in self.experiments.values() if exp.status == status]
        return list(self.experiments.values())
    
    def delete_experiment(self, experiment_id: str) -> bool:
        """
        Delete an experiment.
        
        Args:
            experiment_id: Experiment ID
        
        Returns:
            True if deleted successfully
        """
        if experiment_id in self.experiments:
            del self.experiments[experiment_id]
            if experiment_id in self._events:
                del self._events[experiment_id]
            self._save_experiments()
            return True
        return False
