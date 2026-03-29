# Changelog

All notable changes to claw-rl will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.9.0] - 2026-03-29

### Added
- **Contextual Learning Module** (`context/context_learning.py`)
  - `DecisionContext` class for context-aware decisions
  - `ContextualDecision` class for decision tracking
  - `ContextLearner` class with pattern learning
  - Auto-detection of time_of_day and day_of_week
  - Pattern learning for high-satisfaction decisions

- **Documentation**
  - `ROADMAP.md` - Product roadmap and milestone tracking
  - `docs/API_REFERENCE.md` - Complete API documentation
  - `docs/PHASE2_DESIGN.md` - Phase 2 design details
  - `docs/WORKFLOW.md` - Development workflow

- **Test Coverage**
  - `tests/test_context_learning.py` - 19 tests, 91% coverage
  - Total tests: 120 (101 + 19 new)

### Changed
- **Version Unification** - All version numbers unified to v0.9.0
  - `package.json`: 1.0.0 → 0.9.0
  - `pyproject.toml`: 0.9.0 (consistent)
  - `__init__.py`: 0.9.0 (consistent)

- **Coverage Configuration** - Fixed pytest coverage module name
  - `--cov=neorl` → `--cov=claw_rl`
  - Coverage now reports correctly at 70%+

### Fixed
- Coverage data collection now working correctly
- All 120 tests passing

### Phase 2 Validation
- **P0**: Emotion Dashboard v1.0.0 (Emotion ROI 9.2/10)
- **P1**: Expression Radar v1.0.0 (Score 8.68/10)
- **P2**: OpenClaw Integration (Latency < 60s)

---

## [0.8.0] - 2026-03-26

### Added
- Contextual learning capability
- Decision context tracking
- Pattern recognition from contexts

---

## [0.7.0] - 2026-03-25

### Added
- Enhanced learning loop
- Background training integration

---

## [0.6.0] - 2026-03-25

### Added
- Shell-Python integration
- Deployment automation

---

## [0.5.0] - 2026-03-24

### Added
- Python migration from Shell scripts
- `binary_rl.py` - Evaluative learning module
- `opd_hint.py` - Directive learning module
- `learning_loop.py` - Background training
- Test suite with pytest

### Changed
- Core logic migrated from Shell to Python
- Data storage in JSONL format

---

## [0.4.0] - 2026-03-23

### Added
- Initial Shell implementation
- Basic reward collection
- Hint extraction

---

## Release Notes Format

Each release includes:
- **Added**: New features
- **Changed**: Changes to existing features
- **Fixed**: Bug fixes
- **Removed**: Removed features

---

## Versioning Strategy

- **Major (X.0.0)**: Breaking changes
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, backward compatible

---

[0.9.0]: https://github.com/opensourceclaw/claw-rl/releases/tag/v0.9.0
[0.8.0]: https://github.com/opensourceclaw/claw-rl/releases/tag/v0.8.0
[0.7.0]: https://github.com/opensourceclaw/claw-rl/releases/tag/v0.7.0
[0.6.0]: https://github.com/opensourceclaw/claw-rl/releases/tag/v0.6.0
[0.5.0]: https://github.com/opensourceclaw/claw-rl/releases/tag/v0.5.0
[0.4.0]: https://github.com/opensourceclaw/claw-rl/releases/tag/v0.4.0
