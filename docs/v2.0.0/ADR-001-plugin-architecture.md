# ADR-001: claw-rl v2.0.0 OpenClaw Plugin Architecture

**Status:** Accepted  
**Date:** 2026-03-31  
**Decision Makers:** Peter Cheng, Friday (AI)  
**Scope:** claw-rl v2.0.0 Plugin Migration

---

## Context

claw-rl v1.0.0 is currently implemented as:
- Python package (`claw_rl`)
- OpenClaw Skill (`src/SKILL.md`)
- Manual activation via environment variable

**Limitations of current approach:**
- Not integrated with OpenClaw Plugin system
- Manual activation required
- Limited lifecycle management
- No automatic memory injection

**Opportunities:**
- claw-mem v2.0.0 successfully migrated to Plugin architecture
- OpenClaw v2026.3.28+ supports enhanced Plugin API
- Performance improvements from Local-First design

---

## Decision

Migrate claw-rl to OpenClaw Plugin architecture following the same pattern as claw-mem v2.0.0:

### Architecture

```
OpenClaw Plugin (TypeScript)
├── src/claw_rl_plugin/
│   ├── index.ts           # Plugin entry point
│   ├── binary_rl.ts       # Binary RL handler
│   ├── opd_hint.ts        # OPD handler
│   └── learning_loop.ts   # Background training
├── openclaw.plugin.json   # Plugin manifest
├── package.json
└── dist/                  # Compiled output
        ↓ stdio JSON-RPC
Python Bridge
├── src/claw_rl/
│   ├── bridge.py          # JSON-RPC server
│   ├── binary_rl.py       # (existing)
│   ├── opd_hint.py        # (existing)
│   └── ...                # (existing modules)
```

### Key Design Decisions

1. **Local-First Communication**: stdio JSON-RPC (same as claw-mem)
2. **Plugin Kind**: `context-engine` (learning/injection)
3. **Lifecycle Hooks**:
   - `session_start`: Inject learned rules
   - `message_received`: Collect feedback signals
   - `session_end`: Process learning signals
4. **Background Training**: Separate process managed by Plugin

---

## Non-Negotiables

### Security
- Data isolation: Learning data must be workspace-scoped
- No external API calls without user consent
- Audit logs for all learning operations

### Performance
- Memory injection latency: < 10ms
- Learning signal processing: < 100ms
- Background training: Non-blocking

### Compatibility
- Python 3.8+
- Node.js 18+
- OpenClaw v2026.3.28+

---

## Consequences

### Positive
- ✅ Automatic activation (no manual setup)
- ✅ Better lifecycle management
- ✅ Unified integration with OpenClaw
- ✅ Performance improvements (Local-First)
- ✅ Consistent with claw-mem architecture

### Negative
- ⚠️ Increased complexity (TypeScript + Python)
- ⚠️ Additional dependencies (stdio bridge)
- ⚠️ Migration effort (2-3 weeks)

### Risks
- Background training process management
- Learning data persistence across sessions
- OpenClaw Plugin API stability

---

## Alternatives Considered

### Alternative 1: Keep as Skill
- **Pros:** No migration effort, existing code works
- **Cons:** No automatic activation, limited integration
- **Decision:** Rejected (doesn't align with v2.0.0 goals)

### Alternative 2: Pure TypeScript Rewrite
- **Pros:** Simpler architecture, no Python dependency
- **Cons:** Massive rewrite effort, loss of existing Python code
- **Decision:** Rejected (too much effort, high risk)

### Alternative 3: HTTP API
- **Pros:** Language-agnostic, easier debugging
- **Cons:** Network overhead, slower performance
- **Decision:** Rejected (Local-First is better)

---

## Implementation Plan

### Phase 1: Foundation (3 days)
- [ ] Create Plugin directory structure
- [ ] Implement TypeScript Plugin skeleton
- [ ] Implement Python Bridge skeleton
- [ ] Basic stdio JSON-RPC communication

### Phase 2: Core Migration (5 days)
- [ ] Migrate Binary RL module
- [ ] Migrate OPD Hint module
- [ ] Migrate Learning Loop
- [ ] Integrate with OpenClaw hooks

### Phase 3: Testing & Polish (3 days)
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] Documentation

### Phase 4: Release (1 day)
- [ ] v2.0.0-beta release
- [ ] GitHub Release
- [ ] Documentation update

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Memory Injection Latency | < 10ms |
| Learning Signal Processing | < 100ms |
| Test Coverage | > 80% |
| Documentation | Complete |
| Performance vs v1.0.0 | Same or better |

---

## References

- [claw-mem v2.0.0 Plugin Architecture](../claw-mem/docs/v2.0.0/LOCAL_FIRST_PLUGIN_ARCHITECTURE.md)
- [OpenClaw Plugin API](https://docs.openclaw.ai/plugins)
- [Hybrid SDLC Framework](../neoclaw/docs/v2.0.0/BASELINE.md)

---

**Approved by:** Peter Cheng  
**Date:** 2026-03-31
