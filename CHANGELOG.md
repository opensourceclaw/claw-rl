# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-31

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
