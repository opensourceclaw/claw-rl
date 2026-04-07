"""
claw-rl: Self-Learning Module for AI Agents

This package provides self-learning capabilities for AI agents:
- Pattern Recognition: Recognize patterns from historical memory
- Feedback Loop: Optimize policies based on feedback
- Core: Learning loop, daemon, and memory bridge
- Learning: Calibration, strategy, and value learning
- Context: Context-aware learning
- Hooks: Pre/post session hooks
- Protocols: Framework-agnostic interfaces
- Adapters: Framework-specific implementations
- Multi-Armed Bandit: Intelligent strategy selection
- Rule Portability: Export and import learned rules

Version: 2.0.0-rc.2
"""

__version__ = "2.0.1-rc.1"
__author__ = "OpenClaw Team"

# Pattern Recognition (Sprint 1)
from .pattern import (
    PatternRecognitionEngine,
    Pattern,
    Anomaly,
    PatternType,
    AnomalyType,
    PatternRecognitionResult,
    recognize_patterns
)

# Feedback Loop (v2.0.0b2 migrated)
from .feedback import (
    BinaryRLJudge,
    RewardResult,
    OPDHint,
    OPDHintExtractor,
)

# Core
from .core import (
    LearningLoop,
    ClawRLBridge,
    ClawMemBridge,
    LearningDaemon,
    CPALoop,
    CPALoopConfig,
)

# Learning (Sprint 1-3)
from .learning import (
    CalibrationLearner,
    StrategyLearner,
    ValuePreferenceLearner,
    # Sprint 2
    KnowledgeBase,
    ExperienceReplay,
    SelfImprovement,
)

# Context
from .context import (
    ContextLearner,
)

# Hooks
from .hooks import (
    PreSessionHook,
    PostSessionHook,
)

# Protocols (Sprint 3)
from .protocols import (
    ObserverProtocol,
    DecisionMakerProtocol,
    ExecutorProtocol,
    SignalAdapterProtocol,
)

# Adapters (Sprint 3)
from .adapters import (
    BaseObserverAdapter,
    BaseDecisionMakerAdapter,
    BaseExecutorAdapter,
    BaseSignalAdapter,
    OpenClawObserverAdapter,
    OpenClawSignalAdapter,
)

# Auto-activate
from .auto_activate import (
    AutoActivator,
    get_activator,
    is_active,
)

# Multi-Armed Bandit (Week 1)
from .mab import (
    MultiArmedBandit,
    Strategy,
    StrategyPerformance,
    BanditConfig,
    StrategyType,
    BanditError,
    StrategyError,
    SelectionError,
    BetaDistribution,
    ThompsonSamplingStrategy,
    EpsilonGreedyStrategy,
    DecayMode,
)

# Rule Portability (Week 1)
from .rule_portability import (
    RulePortability,
    ExportedRule,
    RuleVersion,
    RuleLineage,
    RuleMergeStrategy,
    RuleExportResult,
    RuleImportResult,
)

# Learning Audit (Week 1)
from .learning_audit import (
    LearningAudit,
    LearningEvent,
    LearningEventType,
    AuditLevel,
    RuleExplanation,
)

# Decision Path (RL-004)
from .decision_path import (
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

__all__ = [
    # Version
    '__version__',
    '__author__',
    
    # Pattern Recognition
    'PatternRecognitionEngine',
    'Pattern',
    'Anomaly',
    'PatternType',
    'AnomalyType',
    'PatternRecognitionResult',
    'recognize_patterns',
    
    # Feedback
    'BinaryRLJudge',
    'RewardResult',
    'OPDHint',
    'OPDHintExtractor',
    
    # Core
    'LearningLoop',
    'ClawRLBridge',
    'ClawMemBridge',
    'LearningDaemon',
    'CPALoop',
    'CPALoopConfig',
    
    # Learning
    'CalibrationLearner',
    'StrategyLearner',
    'ValuePreferenceLearner',
    'KnowledgeBase',
    'ExperienceReplay',
    'SelfImprovement',
    
    # Context
    'ContextLearner',
    
    # Hooks
    'PreSessionHook',
    'PostSessionHook',
    
    # Protocols
    'ObserverProtocol',
    'DecisionMakerProtocol',
    'ExecutorProtocol',
    'SignalAdapterProtocol',
    
    # Adapters
    'BaseObserverAdapter',
    'BaseDecisionMakerAdapter',
    'BaseExecutorAdapter',
    'BaseSignalAdapter',
    'OpenClawObserverAdapter',
    'OpenClawSignalAdapter',
    
    # Auto-activate
    'AutoActivator',
    'get_activator',
    'is_active',
    
    # Multi-Armed Bandit
    'MultiArmedBandit',
    'Strategy',
    'StrategyPerformance',
    'BanditConfig',
    'StrategyType',
    'BanditError',
    'StrategyError',
    'SelectionError',
    'BetaDistribution',
    'ThompsonSamplingStrategy',
    'EpsilonGreedyStrategy',
    'DecayMode',
    
    # Rule Portability
    'RulePortability',
    'ExportedRule',
    'RuleVersion',
    'RuleLineage',
    'RuleMergeStrategy',
    'RuleExportResult',
    'RuleImportResult',
    
    # Learning Audit
    'LearningAudit',
    'LearningEvent',
    'LearningEventType',
    'AuditLevel',
    'RuleExplanation',

    # Decision Path (RL-004)
    'NodeType',
    'PathStatus',
    'FeedbackInfo',
    'DecisionNode',
    'DecisionPath',
    'DecisionPathTracker',
    'PathSummary',
    'DecisionPathVisualizer',
    'PathPattern',
    'PathStatistics',
    'SimilarPath',
    'AnomalousPath',
    'DecisionPathAnalyzer',
]
