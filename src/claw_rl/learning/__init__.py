"""
claw-rl Learning Module

Calibration, Strategy, Value learning, Optimization, A/B Testing, and Evaluation.
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
]
