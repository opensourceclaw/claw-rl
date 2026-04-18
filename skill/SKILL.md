---
name: claw-rl
displayName: "claw-rl: Self-Improvement System for AI agents"
description: "Self-Improvement System for AI agents. Features: feedback collection, hint extraction, rule learning. Use for: learning from user corrections."
homepage: https://github.com/opensourceclaw/claw-rl
metadata: {"clawdbot":{"emoji":"🔄","requires":{"bins":["python3"],"packages":["claw-rl"]}}}
---

# claw-rl: Self-Improvement System for AI agents

Self-improvement system for AI agents with reinforcement learning.

## Prerequisites

```bash
pip install git+https://github.com/opensourceclaw/claw-rl.git@v2.0.2
```

## Quick Start

### Collect Feedback

```bash
python3 {baseDir}/scripts/collect_feedback.py "Great job!" --action file_created
python3 {baseDir}/scripts/collect_feedback.py "Wrong, try X instead" --action response --negative
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

### Start Learning Daemon (Optional)

```bash
python3 {baseDir}/scripts/daemon.py start
python3 {baseDir}/scripts/daemon.py stop
python3 {baseDir}/scripts/daemon.py status
```

## Core Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **Binary RL Judge** | Evaluate satisfaction | 👍 → positive, 👎 → negative |
| **OPD Extractor** | Extract improvement hints | "Use Chinese" → rule hint |
| **Learning Loop** | Background learning | Process feedback queue |
| **MAB Strategy** | Strategy selection | Thompson Sampling, ε-greedy |

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
        "topK": 10
      }
    }
  }
}
```

> **Note**: `autoInject` and `autoLearn` are disabled by default. Enable them only after reviewing learned rules.

## Performance

| Operation | Latency |
|-----------|--------|
| Initialize | ~2ms |
| Collect feedback | ~0.03ms |
| Extract hint | ~1ms |
| Get rules | ~0.7ms |

## Links

- [GitHub](https://github.com/opensourceclaw/claw-rl)
- [Documentation](https://github.com/opensourceclaw/claw-rl#readme)
