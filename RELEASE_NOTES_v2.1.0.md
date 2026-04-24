# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-04-18

### 🎯 Major Release: "From Learning to Continuous Intelligent Learning"

The core goal of v2.1.0 is to upgrade claw-rl from a passive learning system to an active intelligent learning system.

### Added

#### Phase 1: LLM-Enhanced PRM Judge
- **LLMEnhancedPRMJudge** (~500 lines): Multi-LLM backend support
  - OpenAI, Anthropic, Local/Ollama backends
  - Smart TTL caching
  - Confidence-aware rule fallback
  - Performance metrics tracking
- New file: `src/claw_rl/feedback/llm_enhanced_prm.py`
- Tests: 33 tests, 80% coverage

#### Phase 2: Deep claw-mem Integration
- **MemoryConsciousnessSync** (~550 lines): Bidirectional sync system
  - Learning ↔ Memory bidirectional flow
  - Atomic transactions (all-or-nothing)
  - Real-time event propagation
  - Unified state storage (SQLite)
- New file: `src/claw_rl/core/memory_consciousness_sync.py`
- Tests: 24 tests, 77% coverage

#### Phase 3: Adaptive MAB Strategies
- **AdaptiveMAB** (~580 lines): Context-aware strategy selection
  - Four adaptive modes (STATIC, CONTEXTUAL, REACTIVE, HYBRID)
  - Meta-Learner for automatic strategy selection
  - Dynamic parameter adjustment (epsilon decay + performance-aware)
  - Complete metrics tracking
- **ContextFeatures**: 11-dimensional context feature vector
- New file: `src/claw_rl/mab/adaptive.py`
- Tests: 35 tests, 90% coverage

#### Phase 4: Learning Observability
- **LearningMetricsExporter** (~380 lines): Multi-format metrics export
  - Prometheus format (Grafana compatible)
  - JSON/Markdown formats
  - Global Collector singleton
- **RuleEvolutionTracker** (~400 lines): Rule evolution tracking
  - Rule change history
  - Evolution timeline
  - Diff comparison
- New directory: `src/claw_rl/observability/`
- Tests: 31 tests, 93%/79% coverage

#### Phase 5: Rule Portability 2.0
- **RulePortabilityV2** (~320 lines): Enhanced export functionality
  - Multi-format export (JSON/YAML/Markdown)
  - Rule validation
  - Format migration (v1.0 → v2.1)
  - Rule diff comparison
- New file: `src/claw_rl/rule_portability_v2.py`
- Tests: 12 tests, 88% coverage

### Changed

- Updated `src/claw_rl/__init__.py` to export all new modules
- Updated `src/claw_rl/mab/__init__.py` to export AdaptiveMAB
- Updated `src/claw_rl/core/__init__.py` to export MemoryConsciousnessSync
- Fixed negative pattern check order in `binary_rl.py`

### Fixed

- Fixed async/sync mismatch in LLMEnhancedPRMJudge
- Fixed prompt language inconsistency (now English-only)
- Fixed missing import failure logging

### Statistics

| Metric | Value |
|--------|-------|
| Total Tests | 144 passed |
| Avg Coverage | 85% |
| New Code | ~2,730 lines |
| New Tests | ~1,860 lines |
| Phases Complete | 5/5 |

### Compatibility

- Python: >= 3.9
- OpenClaw: >= 2026.4.18
- claw-mem: >= 2.0.0 (optional)

### Review

- Jarvis Review: 8.3/10 (Approved)
- Vision Review: Ready for Release

---

## [2.0.2] - 2026-04-17

### Added

- **Claude Code Plugin**: Full Claude Code integration
  - `claude-code-plugin/` directory with TypeScript implementation
  - SessionStartHook: Inject learned rules at session start
  - PostToolUseHook: Collect feedback from user messages
  - SessionEndHook: Log session summary
  - CLI tools: `claw-rl-status`, `claw-rl-collect`
  - npm package: `@opensourceclaw/claude-code-claw-rl`

- **skill/SKILL.md**: ClawHub skill definition

### Changed

- Updated README with correct installation methods
- Version bump to 2.0.2

### npm Package

- `@opensourceclaw/claude-code-claw-rl@2.0.0`

### Compatibility

- Python: >= 3.8
- Claude Code: >= 1.0.0
- OpenClaw: >= 2026.3.28
