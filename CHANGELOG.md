# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2026-04-15

### 🎉 Official Release

claw-rl v2.0.1 正式版发布。

### Added

- **Decision Path (RL-004)**: 完整的决策路径追踪功能
  - DecisionNode - OODA 循环各阶段节点
  - DecisionPath - 完整决策路径管理
  - DecisionPathTracker - 路径生命周期管理

- **Multi-Armed Bandit (RL-003)**: MAB 算法优化
- **OPD Hint Extractor (RL-002)**: OPD 提示提取器
- **Binary RL Judge (RL-001)**: 二元强化学习判断器

### Changed

- 版本号更新到 2.0.1
- 测试覆盖率提升
- 文档更新

### Dependencies

- 无外部依赖

---

## [2.0.0-rc.3] - 2026-04-08

**Status:** Release Candidate 1 - Decision Path Feature.

### Added

**Decision Path (RL-004):**
- **DecisionNode** - Single node in a decision path (OODA loop stages)
  - Node types: OBSERVE, ORIENT, DECIDE, ACT, LEARN
  - Input/output state, decision content, feedback tracking
  - Rule and strategy association, parent/child node relationships

- **DecisionPath** - Complete decision path from start to finish
  - Path status tracking (ACTIVE, COMPLETED, FAILED)
  - Node sequence, context, and metadata
  - Duration calculation, node type statistics

- **DecisionPathTracker** - Path lifecycle management
  - Start new paths with context and metadata
  - Add nodes with rule/strategy/feedback association
  - Complete paths with success/failure status
  - Path persistence to storage

- **DecisionPathVisualizer** - Export paths in multiple formats
  - JSON export with optional feedback/state inclusion
  - Graph export (dict format)
  - Mermaid diagram export (TD/LR directions)
  - DOT (Graphviz) format
  - Path summary generation

- **DecisionPathAnalyzer** - Analyze paths for patterns and anomalies
  - Pattern analysis (node sequences, rule usage)
  - Statistics calculation (counts, durations, success rate)
  - Similar path detection using multi-factor similarity
  - Anomaly detection (unusually long, premature failure, no action)
  - 44 tests, 86% coverage

### Fixed
- N/A

### Changed
- N/A

## [2.0.0-rc.2] - 2026-04-06

**Status:** Release Candidate 2 - Sprint 3 Complete.

### Added

**Act Layer (Week 8):**
- **Parameter Applier** - Apply optimized parameters with validation and rollback
  - Parameter registration with type validation and custom validators
  - Atomic apply with automatic rollback on failure
  - Snapshot management for manual rollback
  - State persistence (save/load)
  - 39 tests

- **Configuration Manager** - Version-controlled configuration with hot-reload
  - Version control for all configuration changes
  - Configuration validation with custom validators
  - Hot-reload with file change detection
  - Rollback to any version
  - Diff between versions
  - Audit logging for all operations
  - 43 tests

- **Action Executor** - Safe execution environment with retry and timeout
  - Multiple action types: FUNCTION, SHELL, HTTP, CUSTOM
  - Timeout limits for all actions
  - Retry with exponential backoff
  - Execution status tracking
  - Thread-safe concurrent execution
  - Cancellation support
  - 35 tests

**Learn Layer (Week 9):**
- **Knowledge Base** - Learning rules storage and management
  - Rule storage with indexing for fast retrieval
  - Rule lifecycle management (active, deprecated, archived, draft)
  - Conflict resolution strategies
  - Persistence support
  - 29 tests

- **Experience Replay** - Buffer for storing and sampling experiences
  - Multiple sampling strategies (uniform, prioritized, recent, balanced)
  - Prioritized experience replay with importance sampling
  - Experience deduplication
  - Persistence support
  - 27 tests

- **Self-Improvement** - Automatic rule extraction and deployment
  - Rule extraction with 4 strategies (frequency, success_rate, reward, hybrid)
  - Rule validation (confidence, support, conflict detection)
  - Automatic rule deployment
  - Effect monitoring
  - Complete improvement cycle
  - 25 tests, 96% coverage

**Protocol Layer (Week 10):**
- **ObserverProtocol** - Abstract interface for observation collection
- **DecisionMakerProtocol** - Abstract interface for learning decisions
- **ExecutorProtocol** - Abstract interface for decision execution
- **SignalAdapterProtocol** - Abstract interface for signal adaptation
- Data classes: Observation, Decision, ExecutionResult, AdaptedSignal
- 24 tests

**Adapter Layer (Week 10):**
- **BaseObserverAdapter** - Base implementation for observers
- **BaseDecisionMakerAdapter** - Base implementation for decision makers
- **BaseExecutorAdapter** - Base implementation for executors
- **BaseSignalAdapter** - Base implementation for signal adapters
- **OpenClawObserverAdapter** - OpenClaw Gateway event observer
- **OpenClawSignalAdapter** - OpenClaw Gateway signal adapter
- 46 tests

**C-P-A Loop (Week 10):**
- **CPALoop** - Continuous Planning and Autonomous learning loop
  - Five phases: Observe, Orient, Decide, Act, Learn
  - Configurable iteration and delay
  - State management (idle, running, paused, stopped)
  - Statistics tracking
  - 21 tests

**Independence Tests (Week 10):**
- Framework independence verification
- No external framework dependencies in core modules
- Protocols are pure abstractions
- Adapters in separate directory
- 20 tests

### Changed

- Version updated to 2.0.0-rc.2
- `__init__.py` updated with all Sprint 2/3 exports
- `learning/__init__.py` updated with KnowledgeBase, ExperienceReplay, SelfImprovement
- ADR-008: Framework Independence Guarantee adopted

### Architecture

**ADR-008: Framework Independence Guarantee**
- Three-layer architecture: adapters → protocols → core
- Core modules: Zero external dependencies
- Protocol layer: Pure abstractions using Python Protocol
- Adapter layer: Optional, framework-specific implementations
- Independence tests verify compliance

### Testing

- **308 tests** passing
- Week 8: 116 tests (Act Layer)
- Week 9: 81 tests (Learn Layer)
- Week 10: 111 tests (Protocol, Adapter, C-P-A, Independence)

### Quality

- All ADR-008 independence tests passing
- Framework-agnostic design verified
- Zero neoclaw dependencies in core modules

## [2.0.0-rc.1] - 2026-04-03

- All components follow established patterns
- Comprehensive docstrings and examples
- Thread-safe implementations

## [2.0.0-rc.1] - 2026-04-03

**Status:** Release Candidate 1 - Sprint 2 Complete.

### Added

**Feedback Loop System:**
- **Explicit Feedback Collection** - 6 feedback types with sentiment analysis
  - FeedbackCollector: thumbs_up, thumbs_down, rating, text, correction, rejection
  - FeedbackStorage: JSON persistence with multi-dimensional queries
- **Implicit Feedback Inference** - User behavior analysis
  - ImplicitFeedbackInference: 5 signal types (response_time, retry_action, continuation, abandonment, rephrase)
- **Signal Fusion** - Explicit + Implicit fusion with time decay
  - SignalFusion: Confidence-weighted fusion
- **Strategy Optimizer** - Feedback-driven learning
  - StrategyOptimizer: Parameter adjustment
  - ABTestingFramework: Experiment management with statistical analysis
  - LearningEvaluation: ROI metrics and trend analysis

**Documentation:**
- ADR-007: Versioning Strategy
- Sprint 2 Dual AI Audit Checklist
- Sprint 3 Plan

### Fixed

**From Friday Self-Review:**
- Weight normalization division by zero in signal_fusion.py
- Time decay boundary issues (hours_ago >= 0, time_weight <= 1.0)
- Feedback clearing data loss (added clear_feedback parameter)
- History record unbounded growth (MAX_HISTORY_SIZE=100)
- State loading validation (parameter bounds check)

**From JARVIS Independent Review:**
- Input validation: confidence [0,1] range check
- Input validation: signal value validation
- Type annotations: relaxed for extensibility

### Security

- Added input validation for confidence values
- Added input validation for signal values
- Added parameter bounds validation

### Testing

- **391 tests** passing
- **75% code coverage**
- JARVIS independent code review passed

### Quality

- Dual AI Auditing: Friday (Builder) + JARVIS (Adversary)
- All Major issues resolved
- Code quality score: 80/100

## [2.0.0-beta.2] - 2026-03-31

**Status:** Beta release - Simplified architecture using Hooks instead of Context Engine.

### Changed

- **MAJOR: Removed Context Engine** - Simplified architecture by removing `registerContextEngine`
  - Context Engine was over-engineered for claw-rl's needs
  - Hooks (`session_start`, `agent_end`) are sufficient and simpler
  - Reduces complexity and maintenance burden
  - Consistent with claw-mem's architecture

- **Architecture Simplification** - Hooks-only approach
  - Removed Context Engine implementation (assemble, ingest, afterTurn)
  - Removed `registerContextEngine` from OpenClawPluginApi interface
  - Kept Hooks: `session_start`, `session_end`, `message_received`
  - Kept Tools: `learning_status`, `collect_feedback`, `get_learned_rules`

### Fixed

- Consistent architecture with claw-mem (both use Hooks, not Context Engine)

### Performance

- Initialize: ~2.89ms
- Collect Feedback: ~0.036ms
- Get Rules: ~9.09ms

### Testing

- All integration tests passing (6/6)

### Design Rationale

**Why remove Context Engine?**

1. **KISS Principle** - Hooks are simpler and sufficient for claw-rl's needs
2. **Risk Reduction** - Context Engine API is complex and error-prone
3. **Consistency** - claw-mem uses Hooks, claw-rl should too
4. **Maintainability** - Hooks are easier to debug and maintain
5. **Lower Coupling** - Less dependent on OpenClaw internal APIs

**What we lose:**

- Context Engine's `assemble` hook (can be replaced with session_start + manual injection)
- Context Engine's `ingest` hook (not needed for claw-rl)
- Context Engine's `afterTurn` hook (replaced with agent_end hook)

**What we gain:**

- Simpler architecture
- Lower risk
- Easier maintenance
- Consistency with claw-mem

## [2.0.0-beta.1] - 2026-03-31

**Status:** Beta release with critical bug fixes for Context Engine registration.

### Fixed

- **Context Engine Registration API**: Corrected `registerContextEngine` signature
  - Changed from object parameter to `(id, factory)` signature
  - Factory returns `ContextEngine` object with `info`, `assemble`, `ingest`, `afterTurn`
- **Hook Event Name**: Fixed incorrect event name
  - Changed `before_session_start` to `session_start`
  - Removed unsupported `inject` return from session_start hook
- **ContextEngine Interface**: Complete interface implementation
  - Added required `info` property
  - Fixed `assemble` method signature to match OpenClaw Plugin SDK
  - Added required `ingest` method
  - Fixed `afterTurn` method signature

### Changed

- **OpenClawPluginApi Interface**: Updated `registerContextEngine` type definition
  - Changed from object parameter to `(id: string, factory: () => any | Promise<any>): void`

### Testing

- Added comprehensive test script (`test/test_plugin.sh`)
- Added deployment guide (`test/DEPLOYMENT_GUIDE.md`)
- All integration tests passing (6/6)

### Performance

- Initialize: ~2.89ms
- Collect Feedback: ~0.036ms
- Get Rules: ~9.09ms

## [2.0.0-beta.0] - 2026-03-31

**Status:** Beta release for pilot testing with claw-mem v2.0.0-beta and neoclaw v2.0.0-beta.

### Added

- **OpenClaw Plugin Architecture**: Complete TypeScript Plugin implementation
- **Local-First Design**: stdio JSON-RPC communication, zero network overhead
- **Python Bridge**: `claw_rl.bridge` module for JSON-RPC server
- **TypeScript Plugin**: `@opensourceclaw/openclaw-claw-rl` NPM package
- **Auto-Inject Hook**: Automatically inject learned rules at session start
- **Auto-Learn Hook**: Automatically collect feedback from user messages
- **Learning Tools**: `learning_status`, `collect_feedback`, `get_learned_rules`
- **PYTHONPATH Support**: Automatic Python module path configuration
- **Debug Mode**: Optional debug logging for troubleshooting

### Performance

- **Average Latency**: ~0.4ms (excellent for production)
- **Initialize**: ~2ms
- **Collect Feedback**: ~0.03ms
- **Extract Hint**: ~1ms
- **Get Rules**: ~0.7ms
- **Process Learning**: ~0.5ms

### Changed

- Migrated from OpenClaw Skill to OpenClaw Plugin
- Improved architecture with stdio JSON-RPC bridge
- Enhanced test coverage to 78% (207 tests)

### Fixed

- Module path resolution for Python Bridge
- PYTHONPATH configuration for OpenClaw integration
- JSON-RPC communication stability
- Type definitions for OpenClaw Plugin API

### Documentation

- Added [ADR-001: Plugin Architecture](docs/v2.0.0/ADR-001-plugin-architecture.md)
- Added [User Stories](docs/v2.0.0/USER_STORIES.md)
- Added [Migration Plan](docs/v2.0.0/MIGRATION_PLAN.md)
- Updated README with Plugin installation instructions

## [1.0.0] - 2026-03-29

### Added

- Binary RL (Reinforcement Learning) module
- OPD (One-Prompt Directive) hint extraction
- Learning Loop for continuous improvement
- Context-aware learning
- Calibration learning
- Strategy learning
- Value preference learning
- Auto-activation hooks
- Memory integration
- LLM PRM judge
- Agent signal collector

### Performance

- 207 tests passing
- 86% code coverage (core modules)
- Validated through Phase 2 testing

### Documentation

- Complete API documentation
- Usage examples
- Integration guides

---

## Version History

- **v2.0.0** (2026-03-31): OpenClaw Plugin Architecture
- **v1.0.0** (2026-03-29): Production Ready Release
- **v0.9.0** (2026-03-29): Phase 2 Validation
- **v0.8.0** (2026-03-26): Contextual Learning
- **v0.7.0** (2026-03-25): Learning Loop Enhancement
- **v0.6.0** (2026-03-25): Shell-Python Integration
- **v0.5.0** (2026-03-24): Python Migration
