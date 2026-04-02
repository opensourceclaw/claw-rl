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

## 📦 Installation

### Python Package

```bash
pip install claw-rl
```

### OpenClaw Plugin

```bash
npm install @opensourceclaw/openclaw-claw-rl
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Python package
pip install claw-rl

# OpenClaw Plugin
cd your-openclaw-project
npm install /path/to/claw-rl/claw_rl_plugin
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
collect_feedback(feedback="很好，谢谢！", action="created_file")
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
