# claw-rl v2.0.0 Migration Plan

**Version:** 2.0.0  
**Date:** 2026-03-31  
**Status:** Planning

---

## Overview

Migrate claw-rl from OpenClaw Skill to OpenClaw Plugin architecture, following the successful pattern from claw-mem v2.0.0.

---

## Current State (v1.0.0)

```
claw-rl/
├── src/
│   ├── SKILL.md              # OpenClaw Skill definition
│   └── claw_rl/              # Python package
│       ├── __init__.py
│       ├── binary_rl.py      # Binary RL module
│       ├── opd_hint.py       # OPD module
│       ├── learning_loop.py  # Background training
│       └── ...
├── scripts/                  # Shell scripts
├── tests/                    # Test suite
└── data/                     # Learning data
```

**Activation:** Manual via `CLAWRL_ENABLED=1`

---

## Target State (v2.0.0)

```
claw-rl/
├── src/
│   └── claw_rl/              # Python package (existing)
│       ├── bridge.py         # NEW: JSON-RPC bridge
│       ├── binary_rl.py
│       ├── opd_hint.py
│       ├── learning_loop.py
│       └── ...
├── claw_rl_plugin/           # NEW: TypeScript Plugin
│   ├── index.ts              # Plugin entry point
│   ├── binary_rl.ts          # Binary RL handler
│   ├── opd_hint.ts           # OPD handler
│   ├── learning_loop.ts      # Background training
│   ├── openclaw.plugin.json  # Plugin manifest
│   ├── package.json
│   ├── tsconfig.json
│   └── test/
├── tests/                    # Test suite
├── docs/
│   └── v2.0.0/               # NEW: Migration docs
│       ├── ADR-001-plugin-architecture.md
│       ├── USER_STORIES.md
│       └── MIGRATION_PLAN.md
└── data/                     # Learning data
```

**Activation:** Automatic via OpenClaw Plugin system

---

## Migration Strategy

### Approach: Incremental Migration

1. **Keep existing Python code** - No rewrite, just add Bridge
2. **Add TypeScript Plugin** - New layer for OpenClaw integration
3. **Maintain backward compatibility** - v1.0.0 API still works

### Communication Pattern

```
OpenClaw Plugin (TypeScript)
        ↓ spawn + stdio JSON-RPC (< 10ms)
Python Bridge (bridge.py)
        ↓ Python Function Call (< 1ms)
claw-rl Core (existing modules)
```

---

## Phase 1: Foundation (3 days)

### Day 1: Setup

**Tasks:**
- [ ] Create `claw_rl_plugin/` directory structure
- [ ] Create `package.json`, `tsconfig.json`
- [ ] Create `openclaw.plugin.json`
- [ ] Setup build scripts

**Deliverables:**
- Plugin directory structure
- Build configuration
- Empty Plugin skeleton

### Day 2: Python Bridge

**Tasks:**
- [ ] Create `src/claw_rl/bridge.py`
- [ ] Implement JSON-RPC server (stdio)
- [ ] Implement basic methods:
  - `initialize`
  - `shutdown`
  - `status`

**Deliverables:**
- Working Python Bridge
- Basic JSON-RPC communication

### Day 3: TypeScript Plugin

**Tasks:**
- [ ] Create `claw_rl_plugin/index.ts`
- [ ] Implement ClawRLBridge class
- [ ] Implement Plugin registration:
  - Tools: `learning_status`, `inject_rules`
  - Hooks: `session_start`, `session_end`
- [ ] Test basic communication

**Deliverables:**
- Working TypeScript Plugin
- End-to-end communication

---

## Phase 2: Core Migration (5 days)

### Day 4-5: Binary RL Migration

**Tasks:**
- [ ] Migrate Binary RL Python module interface
- [ ] Implement TypeScript handler
- [ ] Add `message_received` hook for feedback collection
- [ ] Test Binary RL flow

**Deliverables:**
- Binary RL working via Plugin
- Feedback collection functional

### Day 6-7: OPD Hint Migration

**Tasks:**
- [ ] Migrate OPD Hint Python module interface
- [ ] Implement TypeScript handler
- [ ] Add hint extraction logic
- [ ] Test OPD flow

**Deliverables:**
- OPD Hint working via Plugin
- Hint extraction functional

### Day 8: Learning Loop

**Tasks:**
- [ ] Migrate Learning Loop Python module interface
- [ ] Implement background process management
- [ ] Add `session_end` hook for learning processing
- [ ] Test background training

**Deliverables:**
- Learning Loop working via Plugin
- Background training functional

---

## Phase 3: Testing & Polish (3 days)

### Day 9: Unit Tests

**Tasks:**
- [ ] Write Python Bridge unit tests
- [ ] Write TypeScript Plugin unit tests
- [ ] Achieve 80%+ coverage

**Deliverables:**
- Complete test suite
- Coverage report

### Day 10: Integration Tests

**Tasks:**
- [ ] Write end-to-end tests
- [ ] Test with OpenClaw
- [ ] Performance benchmarks

**Deliverables:**
- Integration test suite
- Performance report

### Day 11: Documentation

**Tasks:**
- [ ] Update README.md
- [ ] Update CHANGELOG.md
- [ ] Write migration guide
- [ ] Update API documentation

**Deliverables:**
- Complete documentation
- Migration guide

---

## Phase 4: Release (1 day)

### Day 12: Release

**Tasks:**
- [ ] Final testing
- [ ] Create v2.0.0-beta tag
- [ ] Create GitHub Release
- [ ] Update documentation

**Deliverables:**
- v2.0.0-beta release
- GitHub Release notes
- Updated documentation

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Bridge communication issues | Medium | High | Thorough testing, fallback to v1.0.0 |
| Performance regression | Low | High | Benchmark against v1.0.0 |
| Background process management | Medium | Medium | Use proven patterns from claw-mem |
| OpenClaw API changes | Low | High | Target stable v2026.3.28+ |

---

## Success Criteria

| Metric | v1.0.0 | v2.0.0 Target |
|--------|--------|---------------|
| Activation | Manual | Automatic |
| Memory Injection | N/A | < 10ms |
| Learning Processing | N/A | < 100ms |
| Test Coverage | 86% | > 80% |
| Documentation | Complete | Complete |

---

## Dependencies

- OpenClaw v2026.3.28+
- Python 3.8+
- Node.js 18+
- claw-mem v2.0.0+ (for memory injection)

---

## Timeline (AI Speed)

**Total Duration:** 4 days

- Phase 1: 1 day (Foundation)
- Phase 2: 1 day (Core Migration)
- Phase 3: 0.5 day (Testing & Documentation)
- Phase 4: 0.5 day (Release)
- Buffer: 1 day

**Based on:** claw-mem v2.0.0 actual development experience

---

**Created:** 2026-03-31  
**Author:** Friday (AI Assistant)  
**Approved by:** Peter Cheng  
**Approval Date:** 2026-03-31  
**Status:** Ready for Implementation
