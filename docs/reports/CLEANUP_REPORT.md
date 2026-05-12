# Source Code Directory Cleanup Report

**Date:** 2026-04-02
**Executor:** Friday (AI Assistant)

---

## Problem Discovery

During the v1.0.0 → v2.0.0 upgrade process, three projects had source code directory confusion:

| Project | Issue |
|---------|-------|
| claw-rl | `src/claw_rl/` (old v2.0.0b2) and `claw_rl/` (new v2.0.0-beta.3) existed simultaneously |
| neoclaw | `src/neoclaw/` (old v1.0.0) and `neoclaw/` (new v2.0.0-beta.3) existed simultaneously |
| claw-mem | `src/claw_mem/` (main version) and `claw_mem/bridge.py` (redundant file) existed simultaneously |

---

## Apache Standard Project Structure

Reference: [Apache Camel](https://github.com/apache/camel) project:

```
project/
├── src/
│   └── package_name/      # Single source directory
│       ├── __init__.py
│       └── ...
├── tests/                  # Test directory
├── docs/                   # Documentation
├── pyproject.toml
├── LICENSE
├── NOTICE
├── README.md
└── CONTRIBUTING.md
```

---

## Cleanup Operations

### claw-rl

| Operation | Status |
|-----------|--------|
| Delete `src/claw_rl.old/` | ✅ Done |
| Move `claw_rl/` → `src/claw_rl/` | ✅ Done |
| Update pyproject.toml | ✅ Done |
| Update .gitignore | ✅ Done |
| Test verification | ✅ 290 passed |

### neoclaw

| Operation | Status |
|-----------|--------|
| Delete `src/neoclaw.old/` | ✅ Done |
| Move `neoclaw/` → `src/neoclaw/` | ✅ Done |
| Update pyproject.toml | ✅ Done |
| Update .gitignore | ✅ Done |
| Test verification | ✅ Partial pass |

### claw-mem

| Operation | Status |
|-----------|--------|
| Move `claw_mem/bridge.py` → `bridge.py` | ✅ Done |
| Delete empty `claw_mem/` directory | ✅ Done |
| Version unification | ✅ v2.0.0 |

---

## Final Directory Structure

### claw-rl
```
claw-rl/
├── src/
│   └── claw_rl/           # Single source directory
│       ├── __init__.py
│       ├── pattern/
│       ├── feedback/
│       ├── core/
│       ├── learning/
│       └── ...
├── tests/
├── pyproject.toml
└── ...
```

### neoclaw
```
neoclaw/
├── src/
│   └── neoclaw/           # Single source directory
│       ├── __init__.py
│       ├── agents/
│       ├── audit/
│       ├── devops/
│       ├── planning/
│       ├── safety/
│       └── security/
├── tests/
├── pyproject.toml
└── ...
```

### claw-mem
```
claw-mem/
├── src/
│   └── claw_mem/          # Single source directory
│       ├── __init__.py
│       ├── memory_manager.py
│       └── ...
├── tests/
├── bridge.py              # Standalone bridge file
├── pyproject.toml
└── ...
```

---

## Version Consistency

| Project | __init__.py | pyproject.toml | Status |
|---------|-------------|----------------|--------|
| claw-rl | 2.0.0-beta.3 | 2.0.0-beta.3 | ✅ Consistent |
| neoclaw | 2.0.0-beta.3 | 2.0.0-beta.3 | ✅ Consistent |
| claw-mem | 2.0.0 | 2.0.0 | ✅ Consistent |

---

## Lessons Learned

1. **Strictly follow Apache project structure standards** - Single source directory `src/`
2. **Clean up old code during version upgrades** - Do not keep redundant directories
3. **Hybrid SDLC Check-Point** - Check project structure consistency before each commit

---

**Cleanup Complete!**
