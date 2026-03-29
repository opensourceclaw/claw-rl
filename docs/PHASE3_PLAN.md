# claw-rl Phase 3: Integration & Activation Plan

**Version:** 1.1.0  
**Created:** 2026-03-29  
**Updated:** 2026-03-29  
**Status:** 📋 Planning  
**Target:** v1.0.0 Stable Release

---

## 🎯 Strategic Alignment

Phase 3 aims to deliver **claw-rl v1.0.0** in sync with:

| Project | Version | Role | Status |
|---------|---------|------|--------|
| **neoclaw** | v1.0.0 | Agent Framework | 🔄 In Development |
| **claw-mem** | v1.0.8 | Memory System | ✅ Released |
| **claw-rl** | v1.0.0 | Self-Improvement | 🎯 Phase 3 Target |

**Goal:** Three systems work together seamlessly:
```
┌─────────────────────────────────────────────────────────┐
│                    Project Neo Ecosystem                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│  │ neoclaw  │ ←→ │ claw-rl  │ ←→ │ claw-mem │        │
│  │ v1.0.0   │    │ v1.0.0   │    │ v1.0.8   │        │
│  │          │    │          │    │          │        │
│  │ Agents   │    │ Learning │    │ Memory   │        │
│  └──────────┘    └──────────┘    └──────────┘        │
│       ↑              ↑              ↑                 │
│       └──────────────┴──────────────┘                 │
│                   Friday (Main Agent)                  │
│                                                         │
└─────────────────────────────────────────────────────────┘

neoclaw ──决策──→ claw-rl ──学习──→ claw-mem
   ↑                                      │
   └──────────── 记忆注入 ←───────────────┘
```

---

## Phase 3 Objectives

| Objective | Description | Priority |
|-----------|-------------|----------|
| **Auto-Activation** | Zero-config learning enablement | 🔴 P0 |
| **Friday Integration** | Session lifecycle hooks | 🔴 P0 |
| **claw-mem Integration** | Learning → Memory → Injection | 🔴 P0 |
| **neoclaw Integration** | Agent decision learning | 🟡 P1 |
| **LLM-based PRM** | Accurate reward evaluation | 🟡 P1 |

---

## Task Breakdown

### P0: Core Integration (v1.0.0 Required)

#### T0.1: Environment Variable Auto-Activation

**Goal:** Detect `CLAWRL_ENABLED=1` and auto-activate learning

**Tasks:**
- [ ] Create `src/claw_rl/auto_activate.py`
- [ ] Check `CLAWRL_ENABLED` environment variable on import
- [ ] Auto-create data directories if missing
- [ ] Initialize learning state on activation
- [ ] Add activation logging

**Files:**
```
src/claw_rl/auto_activate.py
tests/test_auto_activate.py
```

**Implementation:**
```python
# src/claw_rl/auto_activate.py
import os
from pathlib import Path

class AutoActivator:
    """Auto-activate claw-rl when CLAWRL_ENABLED=1"""
    
    def __init__(self):
        self.enabled = os.getenv('CLAWRL_ENABLED', '0') == '1'
        self.data_dir = Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
        
        if self.enabled:
            self._activate()
    
    def _activate(self):
        """Initialize claw-rl on activation"""
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / 'rewards').mkdir(exist_ok=True)
        (self.data_dir / 'hints').mkdir(exist_ok=True)
        (self.data_dir / 'learnings').mkdir(exist_ok=True)
        
        print("✅ claw-rl auto-activated")
        print(f"   Data directory: {self.data_dir}")
    
    def is_active(self) -> bool:
        return self.enabled

# Auto-activate on import
_activator = AutoActivator()
```

**Usage:**
```bash
# In ~/.zshrc or ~/.bashrc
export CLAWRL_ENABLED=1

# claw-rl activates automatically on import
from claw_rl import auto_activate
```

**Acceptance Criteria:**
- [ ] `CLAWRL_ENABLED=1` enables claw-rl
- [ ] Data directories auto-created
- [ ] No manual `activate.sh` required
- [ ] Activation logged

**Estimated Time:** 3 hours

---

#### T0.2: Session Lifecycle Hooks

**Goal:** Integrate with OpenClaw session lifecycle for automatic learning

**Tasks:**
- [ ] Create `src/claw_rl/hooks/pre_session.py` - Memory injection
- [ ] Create `src/claw_rl/hooks/post_session.py` - Reward collection
- [ ] Define hook interface and data format
- [ ] Integrate with OpenClaw Gateway config
- [ ] Add session tracking

**Files:**
```
src/claw_rl/hooks/
├── __init__.py
├── pre_session.py
├── post_session.py
└── types.py
tests/test_hooks.py
```

**Hook Interface:**
```python
# src/claw_rl/hooks/pre_session.py
from dataclasses import dataclass
from typing import Optional, List
import json
from pathlib import Path

@dataclass
class PreSessionInput:
    session_id: str
    user_id: str
    timestamp: str

@dataclass
class PreSessionOutput:
    injected_memory: str
    hints: List[str]
    patterns: List[str]
    active: bool

class PreSessionHook:
    """Inject learned hints before session starts"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
    
    def execute(self, input: PreSessionInput) -> PreSessionOutput:
        """Execute pre-session hook"""
        # Load hints from last 7 days
        hints = self._load_recent_hints(days=7)
        
        # Load patterns from claw-mem
        patterns = self._load_patterns()
        
        # Build injected memory
        injected = self._build_memory(hints, patterns)
        
        return PreSessionOutput(
            injected_memory=injected,
            hints=hints,
            patterns=patterns,
            active=True
        )
    
    def _load_recent_hints(self, days: int) -> List[str]:
        """Load hints from recent sessions"""
        # Implementation...
        pass
    
    def _load_patterns(self) -> List[str]:
        """Load learned patterns from claw-mem"""
        # Implementation...
        pass
    
    def _build_memory(self, hints: List[str], patterns: List[str]) -> str:
        """Build memory section for injection"""
        sections = []
        
        if hints:
            sections.append("## 🧠 Learned Hints (claw-rl)\n")
            for hint in hints[:5]:  # Top 5 hints
                sections.append(f"- {hint}\n")
        
        if patterns:
            sections.append("\n## 📊 Learned Patterns (claw-rl)\n")
            for pattern in patterns[:3]:  # Top 3 patterns
                sections.append(f"- {pattern}\n")
        
        return "".join(sections)
```

```python
# src/claw_rl/hooks/post_session.py
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class Turn:
    turn_id: int
    action: str
    next_state: str  # User response
    reward: Optional[int] = None

@dataclass
class PostSessionInput:
    session_id: str
    user_id: str
    turns: List[Turn]

@dataclass
class PostSessionOutput:
    rewards_recorded: int
    hints_extracted: int
    learning_triggered: bool
    summary: str

class PostSessionHook:
    """Collect rewards and hints after session ends"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
    
    def execute(self, input: PostSessionInput) -> PostSessionOutput:
        """Execute post-session hook"""
        rewards_recorded = 0
        hints_extracted = 0
        
        for turn in input.turns:
            # Judge reward
            reward = self._judge_reward(turn.action, turn.next_state)
            turn.reward = reward
            
            # Record reward
            if reward != 0:
                self._record_reward(input.session_id, turn)
                rewards_recorded += 1
            
            # Extract hint if correction
            if reward == -1:
                hint = self._extract_hint(turn.next_state)
                if hint:
                    self._record_hint(input.session_id, hint)
                    hints_extracted += 1
        
        # Check if learning should be triggered
        learning_triggered = self._check_learning_trigger(input.session_id)
        
        return PostSessionOutput(
            rewards_recorded=rewards_recorded,
            hints_extracted=hints_extracted,
            learning_triggered=learning_triggered,
            summary=f"Recorded {rewards_recorded} rewards, extracted {hints_extracted} hints"
        )
    
    def _judge_reward(self, action: str, response: str) -> int:
        """Judge reward from user response"""
        # Use rule-based or LLM-based judge
        from claw_rl.binary_rl import BinaryRL
        judge = BinaryRL(data_dir=self.data_dir)
        return judge.judge(response, action)
    
    def _extract_hint(self, correction: str) -> Optional[str]:
        """Extract hint from user correction"""
        from claw_rl.opd_hint import OPDHintExtractor
        extractor = OPDHintExtractor(data_dir=self.data_dir)
        return extractor.extract(correction)
    
    def _record_reward(self, session_id: str, turn: Turn):
        """Record reward to file"""
        # Implementation...
        pass
    
    def _record_hint(self, session_id: str, hint: str):
        """Record hint to file"""
        # Implementation...
        pass
    
    def _check_learning_trigger(self, session_id: str) -> bool:
        """Check if learning should be triggered"""
        # Implementation...
        pass
```

**OpenClaw Gateway Config:**
```yaml
# ~/.openclaw/config.yaml
hooks:
  preSession:
    - command: "python -m claw_rl.hooks.pre_session"
      enabled: true
  postSession:
    - command: "python -m claw_rl.hooks.post_session"
      enabled: true
```

**Acceptance Criteria:**
- [ ] Pre-session hook injects learned hints
- [ ] Post-session hook collects rewards
- [ ] Hooks integrate with OpenClaw Gateway
- [ ] Session tracking works correctly

**Estimated Time:** 6 hours

---

#### T0.3: claw-mem Integration

**Goal:** Write learned patterns to claw-mem for persistence

**Tasks:**
- [ ] Create `src/claw_rl/memory_bridge.py`
- [ ] Define claw-mem write format
- [ ] Implement pattern writing to claw-mem
- [ ] Implement pattern reading from claw-mem
- [ ] Test: Learning → claw-mem → Injection

**Files:**
```
src/claw_rl/memory_bridge.py
tests/test_memory_bridge.py
```

**Implementation:**
```python
# src/claw_rl/memory_bridge.py
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import json

class ClawMemBridge:
    """Bridge between claw-rl and claw-mem"""
    
    def __init__(self, claw_mem_dir: Optional[Path] = None):
        self.claw_mem_dir = claw_mem_dir or Path.home() / '.openclaw' / 'workspace' / 'memory'
        self.learnings_file = self.claw_mem_dir / 'claw-rl-learnings.md'
    
    def write_pattern(self, pattern: str, confidence: float, source: str, session_id: str):
        """Write a learned pattern to claw-mem"""
        timestamp = datetime.now().isoformat()
        
        entry = f"""<!-- tags: claw-rl, learned-pattern; id: {session_id[:8]} -->
[{timestamp}] {pattern}
- **Confidence:** {confidence:.0%}
- **Source:** {source}

"""
        
        # Append to learnings file
        with open(self.learnings_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        # Also append to MEMORY.md
        memory_file = self.claw_mem_dir / 'MEMORY.md'
        with open(memory_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{entry}")
    
    def read_patterns(self, limit: int = 10) -> List[dict]:
        """Read recent patterns from claw-mem"""
        if not self.learnings_file.exists():
            return []
        
        patterns = []
        with open(self.learnings_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('['):
                    # Parse pattern entry
                    # Implementation...
                    pass
        
        return patterns[:limit]
    
    def read_hints(self, days: int = 7, limit: int = 10) -> List[str]:
        """Read recent hints from claw-mem"""
        # Read from hints data
        hints_dir = Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data' / 'hints'
        
        hints = []
        # Implementation...
        
        return hints[:limit]
```

**claw-mem Format:**
```markdown
<!-- tags: claw-rl, learned-pattern; id: abc12345 -->
[2026-03-29T09:00:00] 操作前先检查目标文件是否存在
- **Confidence:** 85%
- **Source:** User correction

<!-- tags: claw-rl, learned-pattern; id: def67890 -->
[2026-03-29T10:00:00] 当用户说"不对"时，先确认理解了需求
- **Confidence:** 90%
- **Source:** Negative reward accumulation
```

**Acceptance Criteria:**
- [ ] Patterns written to `memory/claw-rl-learnings.md`
- [ ] Patterns appended to `MEMORY.md`
- [ ] Patterns readable by claw-mem
- [ ] Format compatible with claw-mem

**Estimated Time:** 4 hours

---

#### T0.4: Background Learning Daemon

**Goal:** Run learning loop automatically in background

**Tasks:**
- [ ] Port `training_loop.sh` to Python
- [ ] Implement daemon with configurable interval
- [ ] Add PID file and health check
- [ ] Add graceful shutdown
- [ ] Integrate with OpenClaw startup

**Files:**
```
src/claw_rl/learning_daemon.py
scripts/start_daemon.py
scripts/stop_daemon.py
tests/test_learning_daemon.py
```

**Implementation:**
```python
# src/claw_rl/learning_daemon.py
import os
import signal
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

class LearningDaemon:
    """Background learning loop"""
    
    def __init__(self, interval_seconds: int = 300, data_dir: Optional[Path] = None):
        self.interval = interval_seconds
        self.data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
        self.pid_file = self.data_dir / 'daemon.pid'
        self.log_file = self.data_dir / 'daemon.log'
        self.running = False
    
    def start(self):
        """Start the daemon"""
        self._write_pid()
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)
        
        self._log("Learning daemon started")
        
        while self.running:
            try:
                self._run_learning_cycle()
            except Exception as e:
                self._log(f"Error: {e}")
            
            time.sleep(self.interval)
    
    def stop(self):
        """Stop the daemon"""
        self.running = False
        self._log("Learning daemon stopped")
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def _run_learning_cycle(self):
        """Run one learning cycle"""
        self._log("Running learning cycle...")
        
        # 1. Check rewards
        rewards = self._check_rewards()
        
        # 2. Check hints
        hints = self._check_hints()
        
        # 3. Trigger learning if needed
        if self._should_learn(rewards):
            self._trigger_learning(rewards, hints)
        
        self._log(f"Cycle complete: {len(rewards)} rewards, {len(hints)} hints")
    
    def _write_pid(self):
        """Write PID file"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    
    def _log(self, message: str):
        """Log message"""
        timestamp = datetime.now().isoformat()
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def _shutdown(self, signum, frame):
        """Graceful shutdown"""
        self.stop()
    
    def _check_rewards(self):
        """Check recent rewards"""
        # Implementation...
        pass
    
    def _check_hints(self):
        """Check recent hints"""
        # Implementation...
        pass
    
    def _should_learn(self, rewards):
        """Check if learning should trigger"""
        # Implementation...
        pass
    
    def _trigger_learning(self, rewards, hints):
        """Trigger learning update"""
        # Implementation...
        pass

if __name__ == '__main__':
    daemon = LearningDaemon(interval_seconds=300)
    daemon.start()
```

**Scripts:**
```python
# scripts/start_daemon.py
from claw_rl.learning_daemon import LearningDaemon
import sys

interval = int(sys.argv[1]) if len(sys.argv) > 1 else 300
daemon = LearningDaemon(interval_seconds=interval)
daemon.start()
```

```python
# scripts/stop_daemon.py
from pathlib import Path
import os
import signal

pid_file = Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data' / 'daemon.pid'

if pid_file.exists():
    with open(pid_file, 'r') as f:
        pid = int(f.read().strip())
    os.kill(pid, signal.SIGTERM)
    print(f"Stopped learning daemon (PID: {pid})")
else:
    print("Learning daemon not running")
```

**Acceptance Criteria:**
- [ ] Daemon runs with configurable interval
- [ ] PID file tracks running instance
- [ ] Graceful shutdown on SIGTERM
- [ ] Logs written to `daemon.log`
- [ ] Can start/stop via scripts

**Estimated Time:** 5 hours

---

### P1: Enhanced Learning (v1.0.0 Nice-to-Have)

#### T1.1: neoclaw Agent Integration

**Goal:** Enable learning from neoclaw agent decisions

**Tasks:**
- [ ] Define agent signal format
- [ ] Create `agent_signal_collector.py`
- [ ] Create adapters for Stark/Pepper/Happy
- [ ] Integrate with neoclaw v1.0.0
- [ ] Test: Agent decisions generate learning signals

**Files:**
```
src/claw_rl/agents/
├── __init__.py
├── signal_collector.py
├── stark_adapter.py
├── pepper_adapter.py
└── happy_adapter.py
tests/test_agent_integration.py
```

**Signal Format:**
```python
@dataclass
class AgentSignal:
    agent_id: str  # e.g., "stark_tech"
    pillar: str    # work, life, wealth
    decision_type: str  # code_generation, advice, analysis
    action: str
    outcome: str   # user_accepted, user_rejected, partial
    satisfaction: float  # 0.0 - 1.0
    context: dict
    timestamp: str
```

**Integration Point:**
```python
# In neoclaw agents
from claw_rl.agents.signal_collector import AgentSignalCollector

class StarkTechAgent:
    def __init__(self):
        self.signal_collector = AgentSignalCollector()
    
    def after_decision(self, decision, outcome, satisfaction):
        """Called after each decision"""
        self.signal_collector.record(
            agent_id="stark_tech",
            pillar="work",
            decision_type=decision.type,
            action=decision.action,
            outcome=outcome,
            satisfaction=satisfaction
        )
```

**Estimated Time:** 8 hours

---

#### T1.2: LLM-based PRM Judge

**Goal:** Replace rule-based PRM with LLM evaluation

**Tasks:**
- [ ] Create `llm_prm_judge.py`
- [ ] Design evaluation prompt
- [ ] Add caching for repeated patterns
- [ ] Fallback to rule-based on error
- [ ] Test: Accuracy > 85%

**Files:**
```
src/claw_rl/llm_prm_judge.py
tests/test_llm_prm_judge.py
```

**Prompt Template:**
```
Evaluate the user's response to an AI assistant action.

Action: {action}
User Response: {response}

Determine satisfaction:
- +1: User is satisfied (thanked, praised, continued)
- -1: User is dissatisfied (corrected, complained, repeated)
- 0: Neutral (no clear signal)

Respond with ONLY: SCORE | REASON

Examples:
"谢谢，很好！" → +1 | User expressed gratitude
"不对，应该这样" → -1 | User corrected
"然后呢？" → +1 | User wants to continue
```

**Estimated Time:** 6 hours

---

## Timeline

### Week 1: P0 Core Integration (18 hours)

| Day | Task | Hours |
|-----|------|-------|
| Mon | T0.1 Auto-Activation | 3h |
| Tue | T0.2 Session Hooks (Part 1) | 3h |
| Wed | T0.2 Session Hooks (Part 2) | 3h |
| Thu | T0.3 claw-mem Integration | 4h |
| Fri | T0.4 Learning Daemon | 5h |

### Week 2: P1 Enhanced Learning (14 hours) - Optional

| Day | Task | Hours |
|-----|------|-------|
| Mon | T1.1 neoclaw Integration (Part 1) | 4h |
| Tue | T1.1 neoclaw Integration (Part 2) | 4h |
| Wed | T1.2 LLM-based PRM (Part 1) | 3h |
| Thu | T1.2 LLM-based PRM (Part 2) | 3h |

---

## Success Criteria

### v1.0.0 Release Criteria (P0 Complete)

- [ ] `CLAWRL_ENABLED=1` enables learning automatically
- [ ] Pre-session hook injects learned hints from claw-mem
- [ ] Post-session hook collects rewards and hints
- [ ] Learned patterns written to claw-mem
- [ ] Background learning daemon runs automatically
- [ ] Integration with neoclaw v1.0.0 framework
- [ ] All tests passing (80%+ coverage)

### v1.1.0 Release Criteria (P1 Complete)

- [ ] neoclaw agents generate learning signals
- [ ] LLM-based PRM accuracy > 85%
- [ ] Multi-agent learning working

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     claw-rl v1.0.0                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐     ┌─────────────────┐              │
│  │  Pre-Session    │     │  Post-Session   │              │
│  │  Hook           │     │  Hook           │              │
│  │                 │     │                 │              │
│  │  - Load hints   │     │  - Judge reward │              │
│  │  - Load patterns│     │  - Extract hint │              │
│  │  - Inject memory│     │  - Record data  │              │
│  └────────┬────────┘     └────────┬────────┘              │
│           │                       │                        │
│           ▼                       ▼                        │
│  ┌─────────────────────────────────────────────┐          │
│  │              claw-mem Bridge                │          │
│  │                                             │          │
│  │  - Write patterns to MEMORY.md             │          │
│  │  - Read hints/patterns for injection       │          │
│  └─────────────────────────────────────────────┘          │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────┐          │
│  │           Learning Daemon                   │          │
│  │                                             │          │
│  │  - Check rewards (every 5 min)             │          │
│  │  - Trigger learning on accumulation        │          │
│  │  - Update patterns                         │          │
│  └─────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘

External Integrations:
- neoclaw v1.0.0: Agent signal collection (P1)
- OpenClaw Gateway: Session lifecycle hooks
- claw-mem v1.0.8: Pattern storage
```

---

## Dependencies

| Dependency | Version | Purpose | Status |
|------------|---------|---------|--------|
| OpenClaw Gateway | v2.0+ | Session hooks | ✅ Available |
| neoclaw | v1.0.0 | Agent integration | 🔄 In Development |
| claw-mem | v1.0.8 | Memory storage | ✅ Available |
| Python | 3.10+ | Runtime | ✅ Available |

---

## Version Milestone

### v1.0.0 - Core Integration

**Target:** Sync with neoclaw v1.0.0 release

**Deliverables:**
- ✅ Phase 2 complete (Binary RL, OPD, Context Learning)
- 🔄 P0: Auto-activation
- 🔄 P0: Session hooks
- 🔄 P0: claw-mem integration
- 🔄 P0: Learning daemon

**Release Date:** TBD (aligned with neoclaw v1.0.0)

---

### v1.1.0 - Enhanced Learning

**Target:** Post neoclaw v1.0.0

**Deliverables:**
- ⏳ P1: neoclaw agent integration
- ⏳ P1: LLM-based PRM

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| neoclaw v1.0.0 delay | High | Medium | P0 can release independently |
| OpenClaw hook API changes | High | Low | Use stable API, add version checks |
| LLM API latency | Medium | Medium | Add caching, timeout handling |
| Memory overhead | Low | Low | Implement data rotation |

---

## Testing Strategy

### Unit Tests

```bash
# Run all tests
./venv/bin/pytest tests/ -v --cov=claw_rl --cov-report=html

# Run specific module tests
./venv/bin/pytest tests/test_hooks.py -v
./venv/bin/pytest tests/test_memory_bridge.py -v
./venv/bin/pytest tests/test_learning_daemon.py -v
```

### Integration Tests

```bash
# Test full pipeline
python -c "
from claw_rl.hooks.pre_session import PreSessionHook
from claw_rl.hooks.post_session import PostSessionHook

# Pre-session
pre = PreSessionHook()
result = pre.execute(PreSessionInput(
    session_id='test_001',
    user_id='peter',
    timestamp='2026-03-29T09:00:00'
))
print(f'Injected: {len(result.hints)} hints')

# Post-session
post = PostSessionHook()
result = post.execute(PostSessionInput(
    session_id='test_001',
    user_id='peter',
    turns=[...]
))
print(f'Recorded: {result.rewards_recorded} rewards')
"
```

### End-to-End Test

```bash
# Set environment
export CLAWRL_ENABLED=1

# Start daemon
python scripts/start_daemon.py 300 &

# Run OpenClaw session
# ... session happens ...

# Check learning
cat ~/.openclaw/workspace/memory/claw-rl-learnings.md
```

---

## Next Steps

1. **Review this plan** with Peter
2. **Confirm alignment** with neoclaw v1.0.0 timeline
3. **Start with T0.1** (Auto-Activation)
4. **Weekly sync** with neoclaw development

---

## References

- [ROADMAP.md](../ROADMAP.md) - Product roadmap
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [PHASE2_DESIGN.md](PHASE2_DESIGN.md) - Phase 2 design
- [neoclaw v1.0.0](https://github.com/opensourceclaw/neoclaw) - neoclaw repository
- [claw-mem v1.0.8](https://github.com/opensourceclaw/claw-mem) - claw-mem repository

---

**Document Created:** 2026-03-29  
**Last Updated:** 2026-03-29  
**Author:** Friday AI  
**Status:** 📋 Pending Review  
**Version Target:** v1.0.0 (aligned with neoclaw v1.0.0)
