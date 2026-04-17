---
name: claw-rl
description: "Self-Improvement System for AI agents. Use when: (1) collecting user feedback (thumbs up/down, corrections), (2) extracting improvement hints from user messages, (3) learning from mistakes and preferences, (4) injecting learned rules into sessions. Features Binary RL evaluation, OPD hint extraction, Multi-Armed Bandit strategy selection, and continuous background learning."
homepage: https://github.com/opensourceclaw/claw-rl
metadata: {"clawdbot":{"emoji":"🔄","requires":{"bins":["python3"],"packages":["claw-rl"]}}}
---

# claw-rl: Self-Improvement System for AI agents

Self-improvement system for AI agents with reinforcement learning and continuous learning.

## Prerequisites

```bash
pip install claw-rl
```

## Quick Start

### Collect Feedback

```bash
python3 {baseDir}/scripts/collect_feedback.py "Great job!" --action file_created
python3 {baseDir}/scripts/collect_feedback.py "Wrong, use Chinese instead" --action response --negative
```

### Get Learned Rules

```bash
python3 {baseDir}/scripts/get_rules.py --top-k 10
python3 {baseDir}/scripts/get_rules.py --context "user preference"
```

### Check Learning Status

```bash
python3 {baseDir}/scripts/status.py
```

### Start Learning Daemon

```bash
python3 {baseDir}/scripts/daemon.py start
python3 {baseDir}/scripts/daemon.py stop
python3 {baseDir}/scripts/daemon.py status
```

## Core Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **Binary RL Judge** | Evaluate satisfaction from feedback | 👍 → positive, 👎 → negative |
| **OPD Extractor** | Extract improvement hints | "Use Chinese" → rule hint |
| **Learning Loop** | Continuous background learning | Process feedback queue |
| **MAB Strategy** | Strategy selection via bandits | Thompson Sampling, ε-greedy |

## Learning Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `calibration` | Calibration learning | User satisfaction calibration |
| `strategy` | Strategy learning | Action selection optimization |
| `value` | Value preference learning | User preference learning |
| `context` | Context-aware learning | Situational rules |

## Configuration

OpenClaw config (`openclaw.config.json`):
```json
{
  "plugins": {
    "slots": {
      "context-engine": "claw-rl"
    },
    "claw-rl": {
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

## Performance

| Operation | Latency |
|-----------|---------|
| Initialize | ~2ms |
| Collect feedback | ~0.03ms |
| Extract hint | ~1ms |
| Get rules | ~0.7ms |
| Process learning | ~0.5ms |

## Advanced

See references for detailed documentation:
- [Architecture](references/architecture.md) - System design
- [Learning](references/learning.md) - Learning algorithms
- [MAB](references/mab.md) - Multi-Armed Bandit strategies
