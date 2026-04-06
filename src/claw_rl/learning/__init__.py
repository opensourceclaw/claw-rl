"""
claw-rl Learning Module

Calibration, Strategy, Value learning, Optimization, A/B Testing, Evaluation,
Parameter Applier, Configuration Manager, Action Executor, Knowledge Base,
Experience Replay, and Self-Improvement.
"""

from .calibration import CalibrationLearner
from .strategy import StrategyLearner
from .value import ValuePreferenceLearner
from .optimizer import (
    OptimizationStrategy,
    AdjustmentDirection,
    StrategyParameter,
    OptimizationResult,
    StrategyOptimizer,
)
from .ab_testing import (
    ExperimentStatus,
    ExperimentVariant,
    Experiment,
    ExperimentResult,
    ABTestingFramework,
)
from .evaluation import (
    MetricType,
    MetricDataPoint,
    MetricSummary,
    EvaluationResult,
    LearningEvaluation,
)
from .applier import (
    ApplyStatus,
    ApplyResult,
    ParameterSnapshot,
    ParameterApplier,
)
from .config_manager import (
    ConfigStatus,
    ConfigVersion,
    ConfigAuditEntry,
    ConfigManager,
)
from .executor import (
    ActionStatus,
    ActionType,
    Action,
    ActionResult,
    ExecutorStats,
    ActionExecutor,
)
from .knowledge_base import (
    RuleStatus,
    RulePriority,
    RuleConflictStrategy,
    LearningRule,
    KnowledgeBase,
)
from .experience_replay import (
    SamplingStrategy,
    Experience,
    ExperienceReplay,
)
from .self_improvement import (
    RuleExtractionStrategy,
    RuleValidationStatus,
    ExtractedRule,
    ValidationResult,
    DeploymentResult,
    RuleExtractor,
    RuleValidator,
    SelfImprovement,
)

__all__ = [
    # Original
    'CalibrationLearner',
    'StrategyLearner',
    'ValuePreferenceLearner',
    # Optimizer
    'OptimizationStrategy',
    'AdjustmentDirection',
    'StrategyParameter',
    'OptimizationResult',
    'StrategyOptimizer',
    # A/B Testing
    'ExperimentStatus',
    'ExperimentVariant',
    'Experiment',
    'ExperimentResult',
    'ABTestingFramework',
    # Evaluation
    'MetricType',
    'MetricDataPoint',
    'MetricSummary',
    'EvaluationResult',
    'LearningEvaluation',
    # Parameter Applier (Week 8)
    'ApplyStatus',
    'ApplyResult',
    'ParameterSnapshot',
    'ParameterApplier',
    # Configuration Manager (Week 8)
    'ConfigStatus',
    'ConfigVersion',
    'ConfigAuditEntry',
    'ConfigManager',
    # Action Executor (Week 8)
    'ActionStatus',
    'ActionType',
    'Action',
    'ActionResult',
    'ExecutorStats',
    'ActionExecutor',
    # Knowledge Base (Week 9)
    'RuleStatus',
    'RulePriority',
    'RuleConflictStrategy',
    'LearningRule',
    'KnowledgeBase',
    # Experience Replay (Week 9)
    'SamplingStrategy',
    'Experience',
    'ExperienceReplay',
    # Self-Improvement (Week 9)
    'RuleExtractionStrategy',
    'RuleValidationStatus',
    'ExtractedRule',
    'ValidationResult',
    'DeploymentResult',
    'RuleExtractor',
    'RuleValidator',
    'SelfImprovement',
]
