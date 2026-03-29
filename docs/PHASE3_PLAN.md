# claw-rl Phase 3: Integration & Activation Plan

**Version:** 1.0.0  
**Created:** 2026-03-29  
**Status:** 📋 Planning  
**Target:** v1.1.0 Release

---

## Overview

Phase 3 focuses on **integrating claw-rl with OpenClaw ecosystem** and **enabling automatic activation**, transforming claw-rl from a standalone library into a production-ready self-improvement system.

**Goal:** Zero-configuration learning from user conversations.

---

## Phase 3 Objectives

| Objective | Description | Priority |
|-----------|-------------|----------|
| **Auto-Activation** | No manual `activate.sh` required | 🔴 P0 |
| **Friday Integration** | Automatic memory injection & reward collection | 🔴 P0 |
| **neoclaw Integration** | Multi-agent learning signals | 🟡 P1 |
| **LLM-based PRM** | Accurate reward judgment | 🟡 P1 |
| **Learning Dashboard** | Visualization & analytics | 🟢 P2 |

---

## Task Breakdown

### P0: Auto-Activation & Friday Integration

#### T0.1: Environment Variable Auto-Detection

**Goal:** Detect `CLAWRL_ENABLED=1` and auto-activate

**Tasks:**
- [ ] Create `src/claw_rl/auto_activate.py`
- [ ] Check `CLAWRL_ENABLED` environment variable
- [ ] Auto-create data directories if missing
- [ ] Initialize learning loop on startup
- [ ] Test: `CLAWRL_ENABLED=1` enables learning automatically

**Files:**
```
src/claw_rl/auto_activate.py
scripts/auto_activate.sh
tests/test_auto_activate.py
```

**Acceptance Criteria:**
- [ ] `CLAWRL_ENABLED=1` in `.zshrc` enables claw-rl
- [ ] No manual `./scripts/activate.sh` required
- [ ] Data directories auto-created on first run

**Estimated Time:** 4 hours

---

#### T0.2: Session Lifecycle Hooks

**Goal:** Integrate with OpenClaw session lifecycle

**Tasks:**
- [ ] Create `pre_session_hook.py` - Memory injection before session
- [ ] Create `post_session_hook.py` - Reward collection after session
- [ ] Define hook interface (input/output format)
- [ ] Integrate with OpenClaw Gateway hooks
- [ ] Test: Hooks fire automatically on session start/end

**Files:**
```
src/claw_rl/hooks/
├── __init__.py
├── pre_session.py
├── post_session.py
└── hook_interface.py
tests/test_hooks.py
```

**Hook Interface:**
```python
# pre_session_hook input
{
    "session_id": "session_12345",
    "user_id": "peter",
    "timestamp": "2026-03-29T09:00:00+08:00"
}

# pre_session_hook output
{
    "injected_memory": "## Learned Hints\n- 操作前先检查文件\n...",
    "hints": ["hint1", "hint2"],
    "patterns": ["pattern1"]
}

# post_session_hook input
{
    "session_id": "session_12345",
    "turns": [
        {"action": "...", "next_state": "...", "reward": +1},
        ...
    ]
}

# post_session_hook output
{
    "rewards_recorded": 5,
    "hints_extracted": 2,
    "learning_triggered": false
}
```

**Acceptance Criteria:**
- [ ] Pre-session hook injects learned hints
- [ ] Post-session hook collects rewards
- [ ] Hooks integrate with OpenClaw Gateway
- [ ] No manual intervention required

**Estimated Time:** 8 hours

---

#### T0.3: MEMORY.md Auto-Update

**Goal:** Automatically update `MEMORY.md` with learned patterns

**Tasks:**
- [ ] Create `memory_updater.py` module
- [ ] Define MEMORY.md section format for learned patterns
- [ ] Implement append-only updates (no overwrites)
- [ ] Add timestamp and session_id to entries
- [ ] Test: Learning entries appear in MEMORY.md

**Files:**
```
src/claw_rl/memory_updater.py
tests/test_memory_updater.py
```

**MEMORY.md Format:**
```markdown
<!-- claw-rl: learned-patterns (auto-generated) -->
<!-- Last updated: 2026-03-29T09:00:00+08:00 -->

## 🧠 Learned Patterns

### 2026-03-29 Session session_12345
- **Pattern:** 当用户说"不对"时，先检查是否理解了需求
- **Confidence:** 85%
- **Source:** User correction

### 2026-03-28 Session session_12344
- **Pattern:** 文件操作前先确认目录
- **Confidence:** 90%
- **Source:** Negative reward accumulation
```

**Acceptance Criteria:**
- [ ] Learned patterns auto-appended to MEMORY.md
- [ ] No overwrites of existing content
- [ ] Timestamps and session IDs included
- [ ] Human-readable format

**Estimated Time:** 4 hours

---

#### T0.4: Background Learning Loop Integration

**Goal:** Run learning loop as OpenClaw background process

**Tasks:**
- [ ] Port `training_loop.sh` to Python (`learning_daemon.py`)
- [ ] Integrate with OpenClaw cron or background process
- [ ] Add health check endpoint
- [ ] Add graceful shutdown
- [ ] Test: Learning runs automatically in background

**Files:**
```
src/claw_rl/learning_daemon.py
scripts/start_daemon.sh
scripts/stop_daemon.sh
tests/test_learning_daemon.py
```

**Acceptance Criteria:**
- [ ] Learning loop runs every 5 minutes
- [ ] Health check at `~/.openclaw/workspace/claw-rl/data/daemon.pid`
- [ ] Graceful shutdown on SIGTERM
- [ ] Logs to `~/.openclaw/workspace/claw-rl/data/daemon.log`

**Estimated Time:** 6 hours

---

### P1: neoclaw Integration & LLM-based PRM

#### T1.1: neoclaw Agent Integration

**Goal:** Enable learning from neoclaw agent interactions

**Tasks:**
- [ ] Define agent learning signal format
- [ ] Create `agent_signal_collector.py`
- [ ] Integrate with Stark/Pepper/Happy agents
- [ ] Map agent outcomes to rewards
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

**Agent Signal Format:**
```json
{
    "agent_id": "stark_tech",
    "decision_type": "code_generation",
    "action": "Generated REST API endpoint",
    "outcome": "user_accepted",
    "satisfaction": 0.9,
    "context": {
        "task": "Create API for user management",
        "complexity": "medium"
    }
}
```

**Acceptance Criteria:**
- [ ] Stark agent decisions generate signals
- [ ] Pepper agent decisions generate signals
- [ ] Happy agent decisions generate signals
- [ ] Signals flow to Binary RL module

**Estimated Time:** 10 hours

---

#### T1.2: LLM-based PRM Judge

**Goal:** Replace rule-based PRM with LLM-based evaluation

**Tasks:**
- [ ] Create `llm_prm_judge.py` module
- [ ] Design prompt for reward evaluation
- [ ] Implement fallback to rule-based judge
- [ ] Add caching for repeated patterns
- [ ] Test: LLM judge produces accurate rewards

**Files:**
```
src/claw_rl/llm_prm_judge.py
tests/test_llm_prm_judge.py
```

**LLM Prompt Template:**
```
You are a reward evaluation model for an AI assistant.

Task: Evaluate the user's response to determine satisfaction.

User Response: "{user_response}"
Agent Action: "{agent_action}"

Scoring:
- +1: User is satisfied (thanked, praised, continued conversation)
- -1: User is dissatisfied (corrected, complained, repeated question)
- 0: Neutral (no clear signal)

Respond with ONLY the score (+1, -1, or 0) and a brief reason.

Format: SCORE | REASON

Examples:
Input: "谢谢，很好！" → Output: +1 | User expressed gratitude and praise
Input: "不对，应该放这里" → Output: -1 | User corrected the action
Input: "然后呢？" → Output: +1 | User wants to continue (satisfied)
```

**Acceptance Criteria:**
- [ ] LLM judge accuracy > 85% on test set
- [ ] Fallback to rule-based on LLM failure
- [ ] Response time < 2 seconds
- [ ] Cache hit rate > 50% for repeated patterns

**Estimated Time:** 8 hours

---

#### T1.3: Hint Quality Filter

**Goal:** Filter low-quality hints before injection

**Tasks:**
- [ ] Create `hint_quality_filter.py`
- [ ] Implement quality scoring (specificity, actionability, clarity)
- [ ] Set minimum quality threshold (0.7)
- [ ] Add hint deduplication
- [ ] Test: Only high-quality hints injected

**Files:**
```
src/claw_rl/hint_quality_filter.py
tests/test_hint_quality_filter.py
```

**Quality Scoring:**
```python
def score_hint(hint: str) -> float:
    """
    Score hint quality (0.0 - 1.0)
    
    Criteria:
    - Specificity: Is it specific? (0.0 - 0.3)
    - Actionability: Can it be acted upon? (0.0 - 0.4)
    - Clarity: Is it clear? (0.0 - 0.3)
    """
    specificity = score_specificity(hint)  # e.g., "操作前先检查文件" = 0.25
    actionability = score_actionability(hint)  # e.g., has action verb = 0.35
    clarity = score_clarity(hint)  # e.g., no ambiguity = 0.28
    
    return specificity + actionability + clarity  # 0.88
```

**Acceptance Criteria:**
- [ ] Quality score calculated for each hint
- [ ] Hints with score < 0.7 filtered out
- [ ] Duplicate hints removed
- [ ] Filter statistics logged

**Estimated Time:** 6 hours

---

### P2: Learning Dashboard

#### T2.1: Learning Analytics API

**Goal:** Expose learning data via REST API

**Tasks:**
- [ ] Create `analytics_api.py` (FastAPI or Flask)
- [ ] Define endpoints for learning data
- [ ] Add authentication (API key or OpenClaw token)
- [ ] Test: API returns correct data

**Files:**
```
src/claw_rl/analytics/
├── __init__.py
├── api.py
├── models.py
└── routes.py
tests/test_analytics_api.py
```

**API Endpoints:**
```
GET /api/v1/rewards?date=2026-03-29
GET /api/v1/hints?limit=10
GET /api/v1/patterns?emotion=happy
GET /api/v1/statistics
GET /api/v1/health
```

**Estimated Time:** 6 hours

---

#### T2.2: Web Dashboard

**Goal:** Visualize learning progress

**Tasks:**
- [ ] Create simple HTML dashboard
- [ ] Display reward trends (chart)
- [ ] Display hint patterns (list)
- [ ] Display learning statistics (cards)
- [ ] Test: Dashboard loads and updates

**Files:**
```
src/claw_rl/dashboard/
├── index.html
├── style.css
├── app.js
└── charts.js
```

**Dashboard Components:**
- Reward trend chart (7-day rolling)
- Hint pattern list (top 10)
- Learning statistics cards (total rewards, avg satisfaction, patterns learned)
- Agent decision breakdown (pie chart)

**Estimated Time:** 8 hours

---

## Timeline

### Week 1: P0 Tasks (22 hours)

| Day | Tasks | Hours |
|-----|-------|-------|
| Mon | T0.1 Auto-Activation | 4h |
| Tue | T0.2 Session Hooks (Part 1) | 4h |
| Wed | T0.2 Session Hooks (Part 2) | 4h |
| Thu | T0.3 MEMORY.md Auto-Update | 4h |
| Fri | T0.4 Learning Daemon | 6h |

### Week 2: P1 Tasks (24 hours)

| Day | Tasks | Hours |
|-----|-------|-------|
| Mon | T1.1 neoclaw Integration (Part 1) | 5h |
| Tue | T1.1 neoclaw Integration (Part 2) | 5h |
| Wed | T1.2 LLM-based PRM (Part 1) | 4h |
| Thu | T1.2 LLM-based PRM (Part 2) | 4h |
| Fri | T1.3 Hint Quality Filter | 6h |

### Week 3: P2 Tasks (14 hours)

| Day | Tasks | Hours |
|-----|-------|-------|
| Mon | T2.1 Analytics API | 6h |
| Tue-Wed | T2.2 Web Dashboard | 8h |

---

## Success Criteria

### P0 Success Criteria (Must Have)

- [ ] `CLAWRL_ENABLED=1` enables learning automatically
- [ ] Pre-session hook injects learned hints
- [ ] Post-session hook collects rewards
- [ ] MEMORY.md auto-updates with learned patterns
- [ ] Learning daemon runs in background
- [ ] All tests passing (target: 80%+ coverage)

### P1 Success Criteria (Should Have)

- [ ] neoclaw agents generate learning signals
- [ ] LLM-based PRM accuracy > 85%
- [ ] Hint quality filter removes low-quality hints
- [ ] Fallback mechanisms working

### P2 Success Criteria (Nice to Have)

- [ ] Analytics API responding correctly
- [ ] Dashboard visualizing learning data
- [ ] Charts updating in real-time

---

## Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| OpenClaw Gateway | Session hooks | ✅ Available |
| neoclaw | Agent integration | ⏳ In development |
| LLM API | PRM evaluation | ✅ Available |
| FastAPI/Flask | Analytics API | ✅ Available |
| Chart.js | Dashboard charts | ✅ Available |

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenClaw hook API changes | High | Use stable API, add version checks |
| LLM API latency | Medium | Add caching, timeout handling |
| neoclaw integration complexity | Medium | Start with simple signals, iterate |
| Memory overhead | Low | Implement data rotation, cleanup old entries |

---

## Version Target

**Phase 3 Completion → v1.1.0**

Version numbering:
- v1.0.0: Phase 2 complete (current)
- v1.1.0: Phase 3 P0 complete
- v1.2.0: Phase 3 P1 complete
- v1.3.0: Phase 3 P2 complete

---

## Next Steps

1. **Review this plan** with Peter
2. **Prioritize tasks** based on Project Neo timeline
3. **Start with T0.1** (Auto-Activation)
4. **Weekly check-ins** to track progress

---

## References

- [PHASE2_DESIGN.md](PHASE2_DESIGN.md) - Phase 2 design details
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [ROADMAP.md](../ROADMAP.md) - Product roadmap
- [CLAW_RL_CURRENT_STATUS.md](CLAW_RL_CURRENT_STATUS.md) - Current status assessment

---

**Document Created:** 2026-03-29  
**Author:** Friday AI  
**Status:** 📋 Pending Review
