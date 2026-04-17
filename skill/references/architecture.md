# claw-rl Architecture

## Overview

claw-rl is a self-improvement system for AI agents based on reinforcement learning:

1. **Feedback Collection** - Collect user satisfaction signals
2. **Hint Extraction** - Extract improvement hints from corrections
3. **Rule Learning** - Learn behavioral rules from feedback
4. **Rule Injection** - Inject learned rules into sessions

## Core Components

### Binary RL Judge

Evaluates user satisfaction from feedback signals:
- Positive signals: 👍, "good", "thanks", etc.
- Negative signals: 👎, "wrong", "no", corrections
- Outputs: confidence score, signal type

### OPD Hint Extractor

Extracts One-Prompt Directive hints from user corrections:
- Pattern recognition from correction text
- Rule extraction from "do X instead" patterns
- Context-aware hint prioritization

### Learning Loop

Continuous background learning:
- Process feedback queue
- Update rule weights
- Decay old rules
- Merge similar rules

### Multi-Armed Bandit

Strategy selection via bandit algorithms:
- Thompson Sampling
- ε-Greedy
- UCB (Upper Confidence Bound)
- Adaptive exploration/exploitation

## Data Flow

```
User Feedback → Binary RL Judge → Signal Classification
                      ↓
              OPD Hint Extractor (if negative)
                      ↓
              Learning Loop → Rule Storage
                      ↓
              MAB Strategy Selection
                      ↓
              Rule Injection → Session Context
```

## Storage

All learning data stored in SQLite:
- `feedback.db` - Feedback history
- `rules.db` - Learned rules
- `stats.db` - Learning statistics
