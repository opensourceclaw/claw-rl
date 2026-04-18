# claw-rl

<div align="center">

**Self-Improvement System for OpenClaw**

*Learn from User Feedback, Improve Continuously*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-blue.svg)](https://www.typescriptlang.org/)

</div>

---

## 🎯 Overview

claw-rl is a **self-improvement system** for AI agents, featuring:

- **Binary RL (Reinforcement Learning)**: Learn from user satisfaction/dissatisfaction
- **OPD (One-Prompt Directive)**: Extract improvement hints from user corrections
- **Learning Loop**: Continuous background learning
- **OpenClaw Plugin**: Seamless integration with v2.0.0+ architecture

### 🆕 v2.1.0 New Features

**"从能学习到持续智能学习"** - From passive to proactive intelligent learning.

| Phase | Feature | Description |
|-------|----------|-------------|
| **Phase 1** | LLM-Enhanced PRM Judge | Multi-LLM backend, smart caching, 90%+ accuracy |
| **Phase 2** | Memory-Consciousness Sync | Bidirectional Learning↔Memory sync, atomic transactions |
| **Phase 3** | Adaptive MAB Strategies | Context-aware strategy selection, dynamic parameters |
| **Phase 4** | Learning Observability | Prometheus/JSON/Markdown export, rule evolution tracking |
| **Phase 5** | Rule Portability 2.0 | Multi-format export, validation, migration |

```python
# v2.1.0 Quick Examples

# LLM-Enhanced PRM Judge
from claw_rl.feedback import LLMEnhancedPRMJudge
judge = LLMEnhancedPRMJudge()
result = judge.judge("Created file", "谢谢，很好！")  # Uses LLM for accuracy

# Adaptive MAB
from claw_rl.mab import AdaptiveMAB, ContextFeatures
mab = AdaptiveMAB()
strategy = mab.select_strategy(ContextFeatures(operation_type="file"))

# Observability
from claw_rl.observability import get_exporter
exporter = get_exporter()
print(exporter.export_prometheus())  # Grafana-compatible metrics
```

## 📦 Installation

### Option 1: Via ClawHub (Recommended)

```bash
# Install ClawHub skill
npx clawhub@latest install opensourceclaw-claw-rl

# Install Python package
pip install git+https://github.com/opensourceclaw/claw-rl.git
```

### Option 2: From GitHub

```bash
# Clone and install
git clone https://github.com/opensourceclaw/claw-rl.git
cd claw-rl
pip install -e .
```

### Option 3: Direct pip install

```bash
pip install git+https://github.com/opensourceclaw/claw-rl.git
```

## 🚀 Quick Start

### 1. Install

```bash
# Install Python package
pip install git+https://github.com/opensourceclaw/claw-rl.git

# Or via ClawHub
npx clawhub@latest install opensourceclaw-claw-rl
```

### 2. Configure OpenClaw

Add to your `openclaw.config.json`:

```json
{
  "plugins": {
    "slots": {
      "context-engine": "claw-rl"
    },
    "claw-rl": {
      "enabled": true,
      "config": {
        "workspaceDir": "~/.openclaw/workspace",
        "autoInject": true,
        "autoLearn": true,
        "topK": 10
      }
    }
  }
}
```

### 3. Automatic Learning

The plugin automatically:

- **Injects learned rules** at session start
- **Collects feedback** from user messages (👍/👎, corrections)
- **Processes learning** at session end

## 🛠️ Tools

### learning_status

Get the current status of the learning system:

```
learning_status()
```

### collect_feedback

Collect user feedback signal:

```
collect_feedback(feedback="Great, thanks!", action="created_file")
```

### get_learned_rules

Get learned rules for injection:

```
get_learned_rules(top_k=10, context="user preference")
```

## 📊 Performance

| Operation | Latency | Evaluation |
|-----------|---------|------------|
| Initialize | ~2ms | ✅ Excellent |
| Collect feedback | ~0.03ms | ✅ Excellent |
| Extract hint | ~1ms | ✅ Excellent |
| Get rules | ~0.7ms | ✅ Excellent |
| Process learning | ~0.5ms | ✅ Excellent |

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   OpenClaw Plugin (TypeScript)      │
│   @opensourceclaw/openclaw-claw-rl  │
│   - Tool Registration               │
│   - Hook Handlers                   │
└──────────────┬──────────────────────┘
               │ spawn + stdio JSON-RPC
               │ (~0.4ms latency)
               ▼
┌─────────────────────────────────────┐
│   claw-rl Python Bridge             │
│   claw_rl.bridge                    │
│   - JSON-RPC Server                 │
│   - Method Routing                  │
└──────────────┬──────────────────────┘
               │ Python Function Call
               ▼
┌─────────────────────────────────────┐
│   claw-rl Core (Python)             │
│   - BinaryRLJudge                   │
│   - OPDHintExtractor                │
│   - LearningLoop                    │
└─────────────────────────────────────┘
```

### Local-First Design

- ✅ **Zero network overhead**: stdio JSON-RPC
- ✅ **Minimal latency**: ~0.4ms average
- ✅ **Completely local**: No cloud dependencies
- ✅ **Simple deployment**: Just Python environment

## 📖 Documentation

### v2.1.0 Documentation
- [v2.1.0 Iteration Plan](docs/v2.1.0/ITERATION_PLAN.md)
- [Phase 1 Progress](docs/v2.1.0/PHASE1_PROGRESS.md) - LLM-Enhanced PRM Judge
- [Phase 2 Progress](docs/v2.1.0/PHASE2_PROGRESS.md) - Memory-Consciousness Sync
- [Phase 3 Progress](docs/v2.1.0/PHASE3_PROGRESS.md) - Adaptive MAB Strategies
- [Phase 4 Progress](docs/v2.1.0/PHASE4_PROGRESS.md) - Learning Observability
- [Phase 5 Progress](docs/v2.1.0/PHASE5_PROGRESS.md) - Rule Portability 2.0
- [Review Report](docs/v2.1.0/REVIEW_REPORT.md)

### v2.0.0 Documentation
- [ADR-001: Plugin Architecture](docs/v2.0.0/ADR-001-plugin-architecture.md)
- [User Stories](docs/v2.0.0/USER_STORIES.md)
- [Migration Plan](docs/v2.0.0/MIGRATION_PLAN.md)

## 🧪 Testing

```bash
# Python tests
pytest tests/ -v --cov=src/claw_rl

# Plugin integration tests
cd claw_rl_plugin
node test/test_integration.js
```

**Coverage:** 78% (207 tests)

## 📝 Changelog

### v2.0.1 (2026-04-17)

- ✅ Published to ClawHub as `opensourceclaw-claw-rl`
- ✅ Updated installation documentation

### v2.0.0 (2026-03-31)

- ✅ OpenClaw Plugin architecture
- ✅ Local-First design (stdio JSON-RPC)
- ✅ TypeScript Plugin implementation
- ✅ Python Bridge implementation
- ✅ Auto-Inject and Auto-Learn hooks
- ✅ 207 tests, 78% coverage
- ✅ ~0.4ms average latency

### v1.0.0 (2026-03-29)

- Binary RL module
- OPD Hint extraction
- Learning Loop
- Context-aware learning
- Phase 2 validation

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- OpenClaw - AI Assistant Framework
- Binary RL Research
- OPD Learning Research

---

<div align="center">

**Built with ❤️ by the OpenClaw Community**

</div>
