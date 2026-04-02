# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
