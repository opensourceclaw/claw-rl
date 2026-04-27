# claw-rl

<div align="center">

**Self-Improvement System for OpenClaw**

*Learn from User Feedback, Improve Continuously*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-2.4.0-blue.svg)](https://github.com/opensourceclaw/claw-rl)

</div>

---

## 🎯 Overview

claw-rl is a **self-improvement system** for AI agents, featuring:

- **Binary RL (Reinforcement Learning)**: Learn from user satisfaction/dissatisfaction
- **OPD (One-Prompt Directive)**: Extract improvement hints from user corrections
- **Learning Loop**: Continuous background learning
- **Adaptive Learning**: Context-aware strategy selection (v2.4.0+)
- **Distributed Learning Sync**: Multi-instance learning synchronization (v2.4.0+)
- **Rule Visualization**: Visual learning analytics (v2.4.0+)
- **OpenClaw Plugin**: Seamless integration with v2.0.0+ architecture

## 📦 Installation

### Prerequisites

- **Python**: 3.10 or higher (tested with Python 3.14.3)
- **pip**: Latest version recommended

```bash
# Check Python version
python3 --version
```

### Option 1: Via pip (Recommended)

```bash
# Install latest version from GitHub
pip3 install git+https://github.com/opensourceclaw/claw-rl.git

# Or install specific version
pip3 install git+https://github.com/opensourceclaw/claw-rl.git@v2.4.0
```

### Option 2: From Source

```bash
# Clone repository
git clone https://github.com/opensourceclaw/claw-rl.git
cd claw-rl

# Install in editable mode (recommended for development)
pip3 install -e .

# Or install with all dependencies
pip3 install -e ".[all]"
```

### Option 3: Via ClawHub

```bash
# Install ClawHub if not already installed
npm install -g clawhub

# Install claw-rl skill
npx clawhub@latest install opensourceclaw-claw-rl
```

## 🚀 Quick Start

### Basic Usage

```python
from claw_rl import BinaryRLJudge, OPDHintExtractor, LearningLoop

# Initialize components
judge = BinaryRLJudge()
extractor = OPDHintExtractor()
learning = LearningLoop()

# Collect and process feedback
feedback = judge.collect("Great, thanks!", action="created_file")
if feedback.is_positive:
    learning.record_success(action="created_file", context={})

# Extract improvement hints
hint = extractor.extract("应该用英文而不是中文写注释", original_action="write_comment")
if hint:
    learning.apply_hint(hint)

# Get learned rules for injection
rules = learning.get_rules(top_k=10, context="code style")
```

### v2.4.0 New Features

```python
# Adaptive Learning (v2.4.0+)
from claw_rl.mab import AdaptiveMAB, ContextFeatures

mab = AdaptiveMAB()
strategy = mab.select_strategy(ContextFeatures(
    operation_type="file",
    user_satisfaction=0.8,
    recent_success_rate=0.9
))
print(f"Selected strategy: {strategy}")

# Distributed Learning Sync (v2.4.0+)
from claw_rl.distributed import LearningSync

sync = LearningSync(
    node_id="worker-1",
    peers=["worker-2", "worker-3"]
)
sync.sync_rules()  # Synchronize learned rules across instances

# Rule Visualization (v2.4.0+)
from claw_rl.visualization import RuleVisualizer

viz = RuleVisualizer()
viz.generate_dashboard()  # Creates HTML dashboard
viz.export_rules_graph()  # Exports rule relationships as JSON
```

## 📊 Performance

| Operation | Latency | Evaluation |
|-----------|---------|------------|
| Initialize | ~2ms | ✅ Excellent |
| Collect feedback | ~0.03ms | ✅ Excellent |
| Extract hint | ~1ms | ✅ Excellent |
| Get rules | ~0.7ms | ✅ Excellent |
| Process learning | ~0.5ms | ✅ Excellent |
| Adaptive Strategy | ~0.1ms | ✅ Excellent |
| Learning Sync | ~5ms | ✅ Good |

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   OpenClaw Plugin (TypeScript)      │
│   @opensourceclaw/openclaw-claw-rl  │
│   - Tool Registration               │
│   - Hook Handlers                   │
└──────────────┬──────────────────────┘
               │ spawn + stdio JSON-RPC
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
│   - AdaptiveMAB (v2.4.0+)           │
│   - LearningSync (v2.4.0+)          │
│   - RuleVisualizer (v2.4.0+)        │
└─────────────────────────────────────┘
```

### Local-First Design

- ✅ **Zero network overhead**: stdio JSON-RPC
- ✅ **Minimal latency**: ~0.4ms average
- ✅ **Completely local**: No cloud dependencies
- ✅ **Simple deployment**: Just Python environment

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

## 🧪 Testing

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/feedback/ -v
pytest tests/mab/ -v
pytest tests/distributed/ -v
pytest tests/visualization/ -v

# With coverage
pytest tests/ --cov=src/claw_rl --cov-report=html
```

**Test Requirements:**

```bash
# Install test dependencies
pip3 install -e ".[test]"

# Or manually
pip3 install pytest pytest-cov
```

## 📝 Changelog

### v2.4.0 (2026-04-27)

- ✅ **Adaptive Learning**
  - `AdaptiveMAB` class for context-aware strategy selection
  - `ContextFeatures` for operation type, satisfaction, success rate
  - Dynamic parameter adjustment
  - Exploration vs exploitation balance

- ✅ **Distributed Learning Sync**
  - `LearningSync` class for multi-instance synchronization
  - Peer-to-peer rule sharing
  - Conflict resolution
  - Version vector for consistency

- ✅ **Rule Visualization**
  - `RuleVisualizer` class for learning analytics
  - HTML dashboard generation
  - Rule relationship graph export
  - Performance metrics visualization

### v2.3.0 (2026-04-26)

- ✅ Value Alignment Layer
- ✅ FeedbackHandler improvements
- ✅ UserValueStore enhancements

### v2.2.0 (2026-04-20)

- ✅ Enhanced PRM Judge
- ✅ Memory-Consciousness Sync

### v2.1.0 (2026-04-18)

- ✅ LLM-Enhanced PRM Judge
- ✅ Adaptive MAB Strategies
- ✅ Learning Observability
- ✅ Rule Portability 2.0

### v2.0.0 (2026-03-31)

- ✅ OpenClaw Plugin architecture
- ✅ Local-First design (stdio JSON-RPC)
- ✅ TypeScript Plugin implementation
- ✅ Python Bridge implementation
- ✅ Auto-Inject and Auto-Learn hooks
- ✅ 207 tests, 78% coverage

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