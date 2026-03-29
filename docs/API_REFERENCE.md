# claw-rl API Reference

**Version:** v0.9.0  
**Last Updated:** 2026-03-29

---

## Overview

claw-rl provides three core modules for AI agent self-improvement:

1. **Binary RL** - Evaluative learning from user feedback
2. **OPD Hint** - Directive learning from user corrections
3. **Contextual Learning** - Context-aware pattern recognition

---

## Module: `binary_rl`

Evaluative learning module - learns from user satisfaction signals.

### Classes

#### `BinaryRL(data_dir: str = None)`

Initialize Binary RL learner.

**Parameters:**
- `data_dir` (str, optional): Directory for storing reward data. Defaults to `~/.openclaw/workspace/claw-rl/data/rewards/`

**Example:**
```python
from claw_rl.binary_rl import BinaryRL

learner = BinaryRL()
```

### Methods

#### `record_reward(session_id: str, turn_id: int, action: str, next_state: str, reward: int, reason: str = None) -> RewardRecord`

Record a reward signal from user feedback.

**Parameters:**
- `session_id` (str): Session identifier
- `turn_id` (int): Turn number in conversation
- `action` (str): Action taken by agent
- `next_state` (str): User's response/next state
- `reward` (int): Reward value (+1, -1, 0)
- `reason` (str, optional): Reason for reward

**Returns:**
- `RewardRecord`: Recorded reward entry

**Example:**
```python
learner.record_reward(
    session_id="session_001",
    turn_id=5,
    action="Created file /workspace/test.md",
    next_state="User said: 谢谢，很好！",
    reward=+1,
    reason="User satisfied"
)
```

#### `get_cumulative_reward(session_id: str = None, decision_type: str = None) -> float`

Get cumulative reward score.

**Parameters:**
- `session_id` (str, optional): Filter by session
- `decision_type` (str, optional): Filter by decision type

**Returns:**
- `float`: Cumulative reward score

#### `get_reward_history(limit: int = 10) -> List[RewardRecord]`

Get recent reward history.

**Parameters:**
- `limit` (int): Maximum records to return

**Returns:**
- `List[RewardRecord]`: List of reward records

---

## Module: `opd_hint`

Directive learning module - learns from user corrections.

### Classes

#### `OPDHintExtractor(data_dir: str = None)`

Initialize OPD hint extractor.

**Parameters:**
- `data_dir` (str, optional): Directory for storing hints. Defaults to `~/.openclaw/workspace/claw-rl/data/hints/`

### Methods

#### `extract_hint(user_correction: str) -> Optional[str]`

Extract actionable hint from user correction.

**Parameters:**
- `user_correction` (str): User's correction text

**Returns:**
- `Optional[str]`: Extracted hint or None

**Example:**
```python
from claw_rl.opd_hint import OPDHintExtractor

extractor = OPDHintExtractor()

hint = extractor.extract_hint("不对，应该先检查文件是否存在")
# Returns: "操作前先检查目标文件是否存在"
```

#### `record_hint(session_id: str, user_correction: str, extracted_hint: str, context: Dict = None) -> HintRecord`

Record an extracted hint.

**Parameters:**
- `session_id` (str): Session identifier
- `user_correction` (str): Original user correction
- `extracted_hint` (str): Extracted actionable hint
- `context` (Dict, optional): Additional context

**Returns:**
- `HintRecord`: Recorded hint entry

#### `get_hints_for_context(context: str = None, limit: int = 10) -> List[str]`

Get relevant hints for a context.

**Parameters:**
- `context` (str, optional): Context to match
- `limit` (int): Maximum hints to return

**Returns:**
- `List[str]`: List of relevant hints

---

## Module: `context.context_learning`

Contextual learning module - learns patterns from decision contexts.

### Classes

#### `DecisionContext`

Context information for a decision.

**Attributes:**
- `timestamp` (str): ISO timestamp
- `time_of_day` (str): morning, afternoon, evening, night
- `day_of_week` (str): Monday-Sunday
- `emotion` (str): User's emotional state
- `situation` (str): Decision situation (work, family, health, etc.)
- `urgency` (str): low, normal, high
- `metadata` (Dict): Additional context data

**Methods:**
- `to_dict() -> Dict`: Convert to dictionary
- `from_dict(data: Dict) -> DecisionContext`: Create from dictionary

#### `ContextualDecision`

A decision with full context.

**Attributes:**
- `decision_id` (str): Unique identifier
- `context` (DecisionContext): Decision context
- `decision_type` (str): Type (investment, career, health, etc.)
- `options` (List[str]): Available options
- `chosen_option` (str): Selected option
- `outcome` (str): Result (success, failure, partial)
- `satisfaction` (float): Satisfaction score (0.0-1.0)
- `learned_pattern` (str, optional): Pattern learned from this decision

#### `ContextLearner(data_dir: str = None)`

Initialize Context Learner.

**Parameters:**
- `data_dir` (str, optional): Directory for storing learning data. Defaults to `~/.openclaw/workspace/claw-rl/data/`

### Methods

#### `record_decision(decision_id: str, decision_type: str, options: List[str], chosen_option: str, outcome: str, satisfaction: float, context_data: Dict = None) -> ContextualDecision`

Record a decision with context.

**Parameters:**
- `decision_id` (str): Unique decision ID
- `decision_type` (str): Type of decision
- `options` (List[str]): Available options
- `chosen_option` (str): Chosen option
- `outcome` (str): Outcome (success/failure/partial)
- `satisfaction` (float): Satisfaction (0.0-1.0)
- `context_data` (Dict, optional): Context (emotion, situation, urgency, etc.)

**Returns:**
- `ContextualDecision`: Recorded decision

**Example:**
```python
from claw_rl.context.context_learning import ContextLearner

learner = ContextLearner()

decision = learner.record_decision(
    decision_id="invest_001",
    decision_type="investment",
    options=["stocks", "bonds", "cash"],
    chosen_option="stocks",
    outcome="success",
    satisfaction=0.85,
    context_data={
        "emotion": "confident",
        "situation": "work",
        "urgency": "normal"
    }
)

# High satisfaction decisions learn patterns
print(decision.learned_pattern)
# "当confident时，您倾向于选择stocks（满意度85%）"
```

#### `get_patterns_for_context(emotion: str = None, decision_type: str = None, situation: str = None) -> List[Dict]`

Get learned patterns matching a context.

**Parameters:**
- `emotion` (str, optional): Filter by emotion
- `decision_type` (str, optional): Filter by decision type
- `situation` (str, optional): Filter by situation

**Returns:**
- `List[Dict]`: Matching patterns

#### `get_decision_history(decision_type: str = None, limit: int = 10) -> List[ContextualDecision]`

Get decision history.

**Parameters:**
- `decision_type` (str, optional): Filter by type
- `limit` (int): Maximum results

**Returns:**
- `List[ContextualDecision]`: Recent decisions

#### `get_statistics() -> Dict`

Get learning statistics.

**Returns:**
- `Dict`: Statistics including total decisions, average satisfaction, pattern counts

---

## Module: `learning_loop`

Background training loop for continuous learning.

### Functions

#### `run_learning_cycle(data_dir: str = None) -> Dict`

Run one learning cycle.

**Parameters:**
- `data_dir` (str, optional): Data directory

**Returns:**
- `Dict`: Cycle results (rewards processed, hints extracted, patterns learned)

#### `start_background_learning(interval_seconds: int = 300, data_dir: str = None) -> None`

Start background learning loop.

**Parameters:**
- `interval_seconds` (int): Interval between cycles (default 5 minutes)
- `data_dir` (str, optional): Data directory

---

## Data Storage

### Directory Structure

```
~/.openclaw/workspace/claw-rl/data/
├── rewards/              # Binary RL reward records
│   └── YYYY-MM-DD.jsonl
├── hints/                # OPD hint records
│   └── YYYY-MM-DD.jsonl
├── learnings/            # Learning entries
│   └── LEARNINGS.md
├── contextual_decisions.jsonl  # Context learning decisions
└── context_patterns.json       # Learned patterns
```

### File Formats

#### Rewards (JSONL)
```json
{"timestamp": "2026-03-29T10:00:00", "session_id": "s001", "turn_id": 5, "action": "...", "reward": 1, "reason": "..."}
```

#### Hints (JSONL)
```json
{"timestamp": "2026-03-29T10:00:00", "session_id": "s001", "correction": "...", "hint": "..."}
```

#### Contextual Decisions (JSONL)
```json
{"decision_id": "d001", "context": {...}, "decision_type": "...", "chosen_option": "...", "satisfaction": 0.85}
```

---

## Integration with OpenClaw

### Memory Injection

claw-rl integrates with OpenClaw via memory injection:

1. **Pre-session**: Inject learned hints into MEMORY.md
2. **During session**: Record rewards and hints
3. **Post-session**: Run learning cycle

### Example Integration

```python
# Pre-session: Inject learned hints
from claw_rl.opd_hint import OPDHintExtractor

extractor = OPDHintExtractor()
hints = extractor.get_hints_for_context(limit=5)

# Inject into MEMORY.md
with open("~/.openclaw/workspace/MEMORY.md", "a") as f:
    f.write("\n## Learned Hints\n")
    for hint in hints:
        f.write(f"- {hint}\n")

# During session: Record feedback
from claw_rl.binary_rl import BinaryRL

learner = BinaryRL()

# After user correction
learner.record_reward(
    session_id=current_session,
    turn_id=turn,
    action=agent_action,
    next_state=user_response,
    reward=reward_value  # +1, -1, or 0
)

# Post-session: Run learning
from claw_rl.learning_loop import run_learning_cycle

results = run_learning_cycle()
```

---

## Error Handling

All modules handle errors gracefully:

- Missing data directories are auto-created
- Corrupt data files are skipped with warnings
- Invalid inputs return sensible defaults

---

## Testing

Run tests with coverage:

```bash
./venv/bin/pytest tests/ -v --cov=claw_rl --cov-report=html
```

Current coverage: **70%+** (v0.9.0)

---

## Version Compatibility

| claw-rl | Python | OpenClaw |
|---------|--------|----------|
| v0.9.x | 3.10+ | v2.0+ |
| v1.0.x | 3.10+ | v2.0+ |

---

## See Also

- [ROADMAP.md](ROADMAP.md) - Project roadmap
- [PHASE2_DESIGN.md](docs/PHASE2_DESIGN.md) - Phase 2 design details
- [WORKFLOW.md](docs/WORKFLOW.md) - Development workflow
