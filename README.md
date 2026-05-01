# claw-rl

<div align="center">

**Self-Improvement System for OpenClaw**

*Learn from User Feedback, Improve Continuously*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-2.6.0-blue.svg)](https://github.com/opensourceclaw/claw-rl)

</div>

---

## 🎯 Product Positioning

claw-rl is a **self-improvement system** for AI Agents with the following core features:

- **Binary RL (Reinforcement Learning)**: Learn from user satisfaction/dissatisfaction
- **OPD (One-Prompt Directive)**: Extract improvement hints from user corrections
- **Learning Loop**: Continuous background learning
- **Adaptive Learning**: Context-aware strategy selection (v2.4.0+)
- **Distributed Learning Sync**: Multi-instance learning synchronization (v2.4.0+)
- **Rule Visualization**: Visual learning analytics (v2.4.0+)
- **ClawMem Bridge**: Seamless memory integration (v2.6.0+)
- **OpenClaw Plugin**: Seamless integration with v2.0.0+ architecture

### Core Advantages

| Feature | Description |
|---------|-------------|
| Binary RL | Binary feedback classification (positive/negative) |
| OPD Hints | Extract actionable improvement hints from corrections |
| Adaptive Strategy | Context-aware learning strategy selection via MAB |
| Distributed Sync | Multi-instance rule synchronization |
| Local-First | Zero network dependency, ~0.4ms average latency |
| OpenClaw Integration | Native plugin architecture, auto-inject/learn hooks |

---

## 📦 Installation

### Prerequisites

- **Python**: 3.10 or higher (tested with Python 3.14.3)
- **pip**: Latest version recommended

```bash
# Check Python version
python3 --version
```

### Method 1: Via ClawHub (Recommended)

```bash
# Install ClawHub if not already installed
npm install -g clawhub

# Install claw-rl skill
npx clawhub@latest install opensourceclaw-claw-rl
```

### Method 2: From Source

```bash
# Clone repository
git clone https://github.com/opensourceclaw/claw-rl.git
cd claw-rl

# Install in editable mode (recommended for development)
pip3 install -e .

# Or install with all dependencies
pip3 install -e ".[all]"
```

### Method 3: Via ClawHub

```bash
# Install ClawHub if not already installed
npm install -g clawhub

# Install claw-rl skill
npx clawhub@latest install opensourceclaw-claw-rl
```

---

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
hint = extractor.extract("Use English instead of Chinese for comments", original_action="write_comment")
if hint:
    learning.apply_hint(hint)

# Get learned rules for injection
rules = learning.get_rules(top_k=10, context="code style")
```

### Enable Advanced Features

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

# ClawMem Bridge (v2.6.0+)
from claw_rl.bridges.claw_mem_bridge import ClawMemBridge

bridge = ClawMemBridge()
bridge.store_episodic(
    text="User corrected code comment to English",
    metadata={"action": "write_comment", "feedback": "negative"}
)
```

---

## 🛠️ Configuration Options

### BinaryRLJudge Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | str | `"default"` | LLM model for judgment |
| `threshold` | float | `0.5` | Confidence threshold |
| `cache_enabled` | bool | `True` | Enable result caching |

### OPDHintExtractor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | str | `"default"` | LLM model for extraction |
| `max_hints` | int | `5` | Maximum hints per extraction |
| `language` | str | `"en"` | Output language |

### AdaptiveMAB Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exploration_rate` | float | `0.1` | Epsilon for epsilon-greedy |
| `strategies` | list | `["epsilon", "ucb", "thompson"]` | Available strategies |

---

## 🔌 OpenClaw Plugin Installation (v2.0.0+)

claw-rl can be installed as an OpenClaw plugin for seamless integration.

### Prerequisites

- **OpenClaw**: 2026.4.0 or higher
- **Python**: 3.10+ with claw-rl installed

```bash
# Install claw-rl first (via ClawHub)
npx clawhub@latest install opensourceclaw-claw-rl

# Or from source
cd /path/to/claw-rl
pip3 install -e .
```

### Step 1: Install Plugin

```bash
# Install from npm
npm install -g @opensourceclaw/openclaw-claw-rl

# Or install from source
cd /path/to/claw-rl/claw_rl_plugin
npm install
openclaw plugins install ./dist
```

### Step 2: Configure OpenClaw

Edit `~/.openclaw/config.json`:

```json
{
  "plugins": {
    "allow": ["claw-rl", "claw-mem", "memory-core", "acpx"],
    "entries": {
      "claw-rl": {
        "enabled": true,
        "config": {
          "workspaceDir": "/path/to/claw-rl-workspace",
          "autoInject": true,
          "autoLearn": true
        },
        "hooks": {
          "allowConversationAccess": true
        }
      }
    }
  }
}
```

### Step 3: Restart Gateway

```bash
openclaw gateway restart
```

### Verification

```bash
# Check plugin loading
tail -20 ~/.openclaw/logs/gateway.log | grep claw-rl

# Or use learning_status tool
learning_status()
```

---

## 📊 Performance Metrics

### Core Performance

| Operation | Latency | Rating |
|-----------|---------|--------|
| Initialize | ~2ms | 🟢 Excellent |
| Collect feedback | ~0.03ms | 🟢 Excellent |
| Extract hint | ~1ms | 🟢 Excellent |
| Get rules | ~0.7ms | 🟢 Excellent |
| Process learning | ~0.5ms | 🟢 Excellent |
| Adaptive Strategy | ~0.1ms | 🟢 Excellent |
| Learning Sync | ~5ms | 🟢 Good |
| **Average** | **~0.4ms** | 🟢 **Excellent** |

### Feature Performance (v2.4.0+)

| Feature | Target | Actual |
|---------|--------|--------|
| Adaptive MAB | < 1ms | ~0.1ms |
| Distributed Sync | < 10ms | ~5ms |
| Visualization | < 100ms | ~50ms |

---

## 🏗️ Technical Architecture

```
┌─────────────────────────────────────────┐
│         OpenClaw Gateway                │
└──────────────────┬──────────────────────┘
                   │ Plugin Protocol
                   ▼
┌─────────────────────────────────────────┐
│   TypeScript Plugin                     │
│   claw_rl_plugin                        │
└──────────────┬──────────────────────────┘
               │ spawn + stdio JSON-RPC
               ▼
┌─────────────────────────────────────────┐
│   Python Bridge                         │
│   claw_rl.bridge                        │
└──────────────┬──────────────────────────┘
               │ Python Function Call
               ▼
┌─────────────────────────────────────────┐
│   claw-rl Core                          │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐   │
│  │    BinaryRLJudge                │   │  ← Binary Feedback
│  │  Positive/Negative/Neutral      │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │    OPDHintExtractor             │   │  ← Hint Extraction
│  │  Correction → Actionable Hint   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │    LearningLoop                 │   │  ← Continuous Learning
│  │  Record → Apply → Inject        │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │    AdaptiveMAB                  │   │  ← Strategy Selection
│  │  Context → Best Strategy        │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │    LearningSync                 │   │  ← Distributed Sync
│  │  Peer-to-Peer Rules             │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │    ClawMemBridge (v2.6.0+)      │   │  ← Memory Integration
│  │  Episodic/Semantic Storage      │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 🔧 Advanced Features

### 1. Binary RL (Binary Reinforcement Learning)

Classify user feedback into positive/negative/neutral signals.

```python
from claw_rl import BinaryRLJudge

judge = BinaryRLJudge()

# Collect feedback
result = judge.collect("Perfect! That's exactly what I needed.", action="write_code")
print(f"Is positive: {result.is_positive}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Reason: {result.reason}")

# Negative feedback
result = judge.collect("That's wrong, please redo it.", action="write_code")
print(f"Is negative: {result.is_negative}")
```

**Feedback Classification**:
- **Positive**: Thanks, Great, Perfect, Exactly, etc.
- **Negative**: Wrong, Redo, Bad, Don't, etc.
- **Neutral**: Other feedback

---

### 2. OPD (One-Prompt Directive)

Extract actionable improvement hints from user corrections.

```python
from claw_rl import OPDHintExtractor

extractor = OPDHintExtractor()

# Extract hints from correction
hint = extractor.extract(
    "Use English instead of Chinese for comments",
    original_action="write_comment"
)

if hint:
    print(f"Action: {hint.action}")
    print(f"Directive: {hint.directive}")
    print(f"Context: {hint.context}")
```

**Hint Structure**:
- `action`: Target action to improve
- `directive`: Specific instruction
- `context`: Related context
- `priority`: High/Medium/Low

---

### 3. Adaptive Learning (v2.4.0+)

Use Multi-Armed Bandit for context-aware strategy selection.

```python
from claw_rl.mab import AdaptiveMAB, ContextFeatures, StrategyType

mab = AdaptiveMAB(
    exploration_rate=0.1,
    strategies=[
        StrategyType.EPSILON_GREEDY,
        StrategyType.UCB,
        StrategyType.THOMPSON
    ]
)

# Select strategy based on context
context = ContextFeatures(
    operation_type="file",       # file, search, execute, etc.
    user_satisfaction=0.8,       # 0-1
    recent_success_rate=0.9,     # 0-1
    session_length=50            # messages count
)

strategy = mab.select_strategy(context)
print(f"Selected strategy: {strategy}")

# Update after feedback
mab.update(
    strategy=strategy,
    reward=1.0 if success else 0.0,
    context=context
)
```

---

### 4. Distributed Learning Sync (v2.4.0+)

Synchronize learned rules across multiple instances.

```python
from claw_rl.distributed import LearningSync, SyncConfig

config = SyncConfig(
    node_id="worker-1",
    peers=["worker-2", "worker-3", "worker-4"],
    sync_interval=60,  # seconds
    conflict_resolution="latest"
)

sync = LearningSync(config)

# Manual sync
sync.sync_rules()

# Or use automatic sync
sync.start_background_sync()
```

---

### 5. Rule Visualization (v2.4.0+)

Visualize learning analytics and rule relationships.

```python
from claw_rl.visualization import RuleVisualizer

viz = RuleVisualizer(
    output_dir="./visualizations"
)

# Generate HTML dashboard
dashboard_path = viz.generate_dashboard()
print(f"Dashboard: {dashboard_path}")

# Export rule graph
graph_data = viz.export_rules_graph()
print(f"Total rules: {len(graph_data['nodes'])}")

# Export metrics
metrics = viz.export_metrics()
print(f"Learning rate: {metrics['learning_rate']}")
```

---

### 6. ClawMem Bridge (v2.6.0+)

Integrate with claw-mem for persistent memory storage.

```python
from claw_rl.bridges.claw_mem_bridge import ClawMemBridge

bridge = ClawMemBridge()

# Store episodic memory
bridge.store_episodic(
    text="User corrected code comment format",
    metadata={
        "action": "write_comment",
        "feedback": "negative",
        "correction": "use English not Chinese"
    }
)

# Store semantic memory (learned rule)
bridge.store_semantic(
    text="Always write comments in English",
    metadata={
        "type": "rule",
        "category": "code_style",
        "source": "opd_hint"
    }
)

# Retrieve related memories
memories = bridge.search("comment language preference")
```

---

## 📝 Changelog

### v2.6.0 (2026-05-01)

- ✅ **ClawMem Bridge**: Seamless integration with claw-mem
  - `ClawMemBridge` class for memory storage
  - Episodic and semantic memory support
  - Bidirectional sync between rl and mem

- ✅ **JSON-RPC Enhancement**:
  - Improved message content extraction
  - Better error handling
  - Enhanced bridge stability

### v2.5.0 (2026-04-30)

- ✅ **Bridge Improvements**
- ✅ **Error Handling Enhancement**
- ✅ **Performance Optimization**

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

---

## 🔄 Integration: claw-rl + claw-mem

When both plugins are deployed together, they create a powerful self-improvement loop:

```
┌─────────────────────────────────────────────────────────┐
│                    Self-Improvement Loop                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐           │
│   │  User   │───▶│ claw-rl │───▶│ claw-   │           │
│   │Feedback │    │  Learn  │    │  mem    │           │
│   └─────────┘    └─────────┘    └─────────┘           │
│       │              │               │                 │
│       ▼              ▼               ▼                 │
│   ┌─────────────────────────────────────┐             │
│   │  Binary RL → OPD Hint → Memory     │             │
│   │  Positive/Negative → Rule → Store  │             │
│   └─────────────────────────────────────┘             │
│                      │                                 │
│                      ▼                                 │
│   ┌─────────────────────────────────────┐             │
│   │  Session Start: Inject Learned Rules│             │
│   │  Context-Aware Strategy Selection   │             │
│   └─────────────────────────────────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Combined Capabilities

| Capability | claw-rl | claw-mem | Combined |
|------------|---------|----------|----------|
| Feedback Learning | ✅ | ❌ | ✅ |
| Hint Extraction | ✅ | ❌ | ✅ |
| Memory Storage | ❌ | ✅ | ✅ |
| Semantic Search | ❌ | ✅ | ✅ |
| Concept Graph | ❌ | ✅ | ✅ |
| Rule Injection | ✅ | ❌ | ✅ |
| Adaptive Strategy | ✅ | ❌ | ✅ |

---

## 🧪 Testing

```bash
# All tests
pytest tests/ -v

# Specific modules
pytest tests/feedback/ -v
pytest tests/mab/ -v
pytest tests/distributed/ -v
pytest tests/visualization/ -v
pytest tests/bridges/ -v

# With coverage
pytest tests/ --cov=src/claw_rl --cov-report=html
```

### Install Test Dependencies

```bash
pip3 install -e ".[test]"
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) - AI Assistant Framework
- Binary RL Research
- OPD Learning Research
- [ClawMem](https://github.com/opensourceclaw/claw-mem) - Intelligent Memory System

---

<div align="center">

**Built with ❤️ by the OpenClaw Community**

</div>
