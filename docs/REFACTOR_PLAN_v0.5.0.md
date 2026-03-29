# P0-3: claw-rl v0.5.0 Refactor Plan (Progressive Python Migration)
# P0-3: claw-rl v0.5.0 重构计划（渐进式 Python 迁移）

**Created:** 2026-03-24T10:50+08:00  
**Updated:** 2026-03-24T11:05+08:00 (Added Python migration decision)  
**Status:** 📋 Planning  
**Owner:** Friday (with Peter Cheng)  
**Timeline:** 2026-04-08 to 2026-04-30 (3 weeks)  
**Location:** `/Users/liantian/workspace/osprojects/claw-rl/`  
**Documentation:** `/Users/liantian/workspace/osprojects/claw-rl/docs/`  

---

## Executive Summary
## 执行摘要

**Objective:** Refactor claw-rl to v0.5.0, continuing with Skill architecture (not Plugin), **starting progressive Python migration** (Shell → Python), enhancing Binary RL + OPD capabilities, and testing real-world collaboration with claw-mem v1.0.1.

**目标:** 重构 claw-rl 为 v0.5.0，继续使用 Skill 架构（非 Plugin），**开始渐进式 Python 迁移**（Shell → Python），增强 Binary RL + OPD 能力，并与 claw-mem v1.0.1 进行实际协同测试。

**Key Principle:** Stability first, proven patterns, no rushed Plugin migration. **Learn from claw-mem's successful Python architecture.**

**核心原则:** 稳定优先，验证模式，不急于 Plugin 迁移。**学习 claw-mem 成功的 Python 架构。**

---

## 🎯 Architecture Decision: Progressive Python Migration
## 🎯 架构决策：渐进式 Python 迁移

**Peter's Decision (2026-03-24 11:03):**
> "好，参考你的建议，渐进式 Python 迁移（v0.5.0 开始）"

**Migration Roadmap:**
**迁移路线图:**

| Version | Architecture | Timeline | Status |
|---------|-------------|----------|--------|
| **v0.4.x** | Pure Shell Scripts | Current | ✅ Stable |
| **v0.5.0** | Shell entry + Python core (NeoMind) | 2026-04-08 to 04-30 | 📋 P0-3 (This plan) |
| **v0.6.0** | Full Python + Shell compatibility layer | 2026-05-01 to 05-31 | 🔮 Future |
| **v1.0.0** | Python Plugin (if migration) | After P0-4 | 🔮 Future |

**v0.5.0 Target Architecture:**
**v0.5.0 目标架构:**

```
/Users/liantian/workspace/osprojects/claw-rl/
├── scripts/                   # Shell entry (keep compatibility)
│   ├── prm_judge.sh          # → calls src/neomind/binary_rl.py
│   ├── hint_extractor.sh     # → calls src/neomind/opd_hint.py
│   └── training_loop.sh      # → calls src/neomind/learning_loop.py
│
├── src/neomind/              # ← Python core (NEW) - NeoMind brand
│   ├── __init__.py
│   ├── binary_rl.py          # Binary RL logic
│   ├── opd_hint.py           # OPD Hint extraction
│   ├── learning_loop.py      # Learning loop
│   └── utils.py              # Utilities
│
├── tests/                    # ← Python tests (NEW)
│   ├── test_binary_rl.py
│   ├── test_opd_hint.py
│   └── ...
│
├── pyproject.toml            # ← Python project config (NEW)
├── requirements.txt          # ← Python dependencies (NEW)
└── SKILL.md                  # Update call method
```

**Key Benefits:**
**关键优势:**

| Benefit | Description |
|---------|-------------|
| ✅ **Backward Compatible** | Scripts unchanged, Skill works as before |
| ✅ **Performance** | Python core is faster than pure shell |
| ✅ **Testability** | pytest automation, better coverage |
| ✅ **Extensibility** | Can add ML pattern recognition later |
| ✅ **Learn from claw-mem** | Same successful Python package structure |

---

## 1. Current State Assessment
## 1. 当前状态评估

### 1.1 claw-rl Current Version
### 1.1 claw-rl 当前版本

| Attribute | Current State |
|-----------|---------------|
| **Version** | v1.0 (early production) |
| **Architecture** | AgentSkill |
| **Location** | `~/.openclaw/workspace/skills/claw-rl/` |
| **Project Root** | `/Users/liantian/workspace/osprojects/claw-rl/` |
| **Core Features** | Binary RL, OPD, Memory Injection, Pre-flight Checks |
| **Stability** | Early production, needs hardening |

### 1.2 Known Issues & Improvement Areas
### 1.2 已知问题与改进方向

| Issue | Impact | Priority |
|-------|--------|----------|
| **Learning Loop Latency** | ~1s end-to-end | P0 |
| **Binary RL Accuracy** | ~90% feedback detection | P0 |
| **OPD Hint Extraction** | Basic pattern matching | P1 |
| **Error Handling** | Edge cases not covered | P1 |
| **Documentation** | SKILL.md needs update | P1 |
| **Code Organization** | Scripts can be better organized | P2 |
| **Performance Baseline** | Not documented | P0 |

---

## 2. v0.5.0 Refactor Goals
## 2. v0.5.0 重构目标

### 2.1 Primary Goals (P0)
### 2.1 主要目标（P0）

| Goal | Success Metric | Timeline |
|------|----------------|----------|
| **Stability Hardening** | Zero critical bugs for 2+ weeks | Week 1-2 |
| **Binary RL Accuracy** | >95% feedback detection | Week 1 |
| **Learning Loop Latency** | End-to-end <500ms | Week 2 |
| **Performance Baseline** | Documented metrics | Week 3 |
| **claw-mem Collaboration** | Successful real-world testing | Week 3 |

### 2.2 Secondary Goals (P1)
### 2.2 次要目标（P1）

| Goal | Success Metric | Timeline |
|------|----------------|----------|
| **OPD Hint Enhancement** | Support complex correction patterns | Week 2-3 |
| **Error Handling** | Cover 95%+ edge cases | Week 2 |
| **Documentation Update** | Complete SKILL.md + README | Week 3 |
| **Code Organization** | Cleaner scripts structure | Week 1-2 |

### 2.3 Out of Scope (Future Versions)
### 2.3 不在范围内（未来版本）

| Feature | Reason | Future Version |
|---------|--------|----------------|
| **Plugin Migration** | Keep Skill until stable | v1.0+ (after P0-4) |
| **Custom Communication Protocol** | Use OpenClaw built-ins | Not needed |
| **Major Architecture Changes** | Stability first | After collaboration proven |

---

## 3. Detailed Task Breakdown
## 3. 详细任务分解

### Week 1: Python Foundation & Project Setup (Apr 8-14)
### 第一周：Python 基础与项目设置（4 月 8-14 日）

#### Task 1.1: Python Project Structure Setup
#### 任务 1.1：Python 项目结构设置

**Owner:** Friday  
**Due:** 2026-04-09  
**Location:** `/Users/liantian/workspace/osprojects/claw-rl/`

**Actions:**
- [ ] Create `src/neorl/` directory structure
- [ ] Create `tests/` directory
- [ ] Create `pyproject.toml` (reference claw-mem)
- [ ] Create `requirements.txt` (minimal dependencies)
- [ ] Create `requirements-dev.txt` (pytest, pytest-cov)
- [ ] Add `.gitignore` for Python artifacts
- [ ] Create refactor branch: `v0.5.0-python-migration`

**Reference (claw-mem):**
```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "neorl"
version = "0.5.0"
description = "NeoMind RL System for OpenClaw"
requires-python = ">=3.9"
dependencies = []  # Start minimal

[project.optional-dependencies]
dev = ["pytest>=7.0.0", "pytest-cov>=3.0.0"]
```

**Deliverable:** 
- Python project structure created
- `pyproject.toml` configured
- `docs/PYTHON_SETUP_v0.5.0.md`

---

#### Task 1.2: Binary RL Python Implementation
#### 任务 1.2：Binary RL Python 实现

**Owner:** Friday  
**Due:** 2026-04-11  
**Location:** `src/neorl/binary_rl.py`

**Current Shell (scripts/prm_judge.sh):**
```bash
if [[ "$feedback" =~ ^(谢谢 | 很好 | 不错) ]]; then
  reward=+1
elif [[ "$feedback" =~ ^(不对 | 错了 | 应该) ]]; then
  reward=-1
fi
```

**Python Implementation:**
```python
# src/neorl/binary_rl.py
import re
from typing import Tuple, Optional

class BinaryRLJudge:
    """Binary RL reward judge with pattern matching."""
    
    POSITIVE_PATTERNS = [
        r'^(谢谢 | 感谢 | 太好了 | 很好 | 不错 | 正确 | 对了)',
        r'(满意 | 喜欢 | 赞同 | 支持)$',
        # Add 20+ patterns
    ]
    
    NEGATIVE_PATTERNS = [
        r'^(不对 | 错了 | 错误 | 应该 | 不正确)',
        r'(不满意 | 不喜欢 | 反对 | 失望)$',
        # Add 20+ patterns
    ]
    
    def judge(self, feedback: str, action: str) -> Tuple[int, float]:
        """
        Judge reward from user feedback.
        
        Returns:
            (reward, confidence): reward in {-1, 0, +1}, confidence in [0, 1]
        """
        # Check positive patterns
        for pattern in self.POSITIVE_PATTERNS:
            if re.search(pattern, feedback):
                return (+1, 0.9)
        
        # Check negative patterns
        for pattern in self.NEGATIVE_PATTERNS:
            if re.search(pattern, feedback):
                return (-1, 0.9)
        
        # Neutral
        return (0, 0.5)
```

**Actions:**
- [ ] Implement `BinaryRLJudge` class
- [ ] Add 20+ positive patterns
- [ ] Add 20+ negative patterns
- [ ] Add confidence scoring
- [ ] Write unit tests (50+ test cases)
- [ ] Update `scripts/prm_judge.sh` to call Python

**Target:** >95% accuracy on test dataset

**Deliverable:** 
- `src/neorl/binary_rl.py`
- `tests/test_binary_rl.py`
- `docs/BINARY_RL_PYTHON_v0.5.0.md`

---

#### Task 1.2: Binary RL Accuracy Improvement
#### 任务 1.2：Binary RL 准确性改进

**Owner:** Friday  
**Due:** 2026-04-10  
**Location:** `scripts/prm_judge.sh`

**Current State:**
```bash
# Current pattern matching
if [[ "$feedback" =~ ^(谢谢 | 很好 | 不错) ]]; then
  reward=+1
elif [[ "$feedback" =~ ^(不对 | 错了 | 应该) ]]; then
  reward=-1
fi
```

**Improvements:**
- [ ] Expand positive feedback patterns (>20 patterns)
- [ ] Expand negative feedback patterns (>20 patterns)
- [ ] Add context-aware detection (conversation history)
- [ ] Implement confidence scoring
- [ ] Add test coverage for edge cases

**Target:** >95% accuracy on test dataset

**Deliverable:** 
- Enhanced `scripts/prm_judge.sh`
- Test dataset → `data/binary_rl_test_cases.md`
- Accuracy report → `docs/BINARY_RL_ACCURACY_v0.5.0.md`

---

#### Task 1.3: Error Handling Hardening
#### 任务 1.3：错误处理加固

**Owner:** Friday  
**Due:** 2026-04-12  
**Location:** All scripts

**Actions:**
- [ ] Add comprehensive error handling to all scripts
- [ ] Implement graceful degradation
- [ ] Add logging for debugging
- [ ] Create error code documentation
- [ ] Test edge cases (missing files, invalid input, etc.)

**Deliverable:** 
- Hardened scripts
- Error handling guide → `docs/ERROR_HANDLING.md`

---

### Week 2: OPD & Learning Loop Python Migration (Apr 15-21)
### 第二周：OPD 与学习循环 Python 迁移（4 月 15-21 日）

#### Task 2.1: OPD Hint Python Implementation
#### 任务 2.1：OPD Hint Python 实现

**Owner:** Friday  
**Due:** 2026-04-17  
**Location:** `src/neorl/opd_hint.py`

**Current Shell (scripts/hint_extractor.sh):**
```bash
if [[ "$feedback" =~ 应该 (.+) ]]; then
  hint="操作前 ${BASH_REMATCH[1]}"
fi
```

**Python Implementation:**
```python
# src/neorl/opd_hint.py
import re
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class OPDHint:
    """OPD hint structure."""
    hint_type: str  # 'should', 'should_not', 'sequence', 'conditional'
    content: str
    priority: int   # 1-5, higher = more important
    confidence: float  # 0-1

class OPDHintExtractor:
    """Extract OPD hints from user corrections."""
    
    def extract(self, feedback: str) -> Optional[OPDHint]:
        """Extract hint from user feedback."""
        
        # Pattern 1: "应该 X" → "操作前 X"
        match = re.search(r'应该 (.+)', feedback)
        if match:
            return OPDHint(
                hint_type='should',
                content=f"操作前{match.group(1)}",
                priority=3,
                confidence=0.9
            )
        
        # Pattern 2: "不要 X" → "避免 X"
        match = re.search(r'不要 (.+)', feedback)
        if match:
            return OPDHint(
                hint_type='should_not',
                content=f"避免{match.group(1)}",
                priority=4,
                confidence=0.9
            )
        
        # Pattern 3: "先 X 再 Y" → "顺序：先 X 再 Y"
        match = re.search(r'先 (.+?) 再 (.+)', feedback)
        if match:
            return OPDHint(
                hint_type='sequence',
                content=f"顺序：先{match.group(1)}再{match.group(2)}",
                priority=5,
                confidence=0.95
            )
        
        return None
```

**Actions:**
- [ ] Implement `OPDHintExtractor` class
- [ ] Support 4+ pattern types (should, should_not, sequence, conditional)
- [ ] Add hint prioritization
- [ ] Add hint deduplication
- [ ] Write unit tests (30+ test cases)
- [ ] Update `scripts/hint_extractor.sh` to call Python

**Deliverable:** 
- `src/neorl/opd_hint.py`
- `tests/test_opd_hint.py`
- `docs/OPD_PATTERNS_v0.5.0.md`

---

#### Task 2.2: Learning Loop Python Implementation
#### 任务 2.2：学习循环 Python 实现

**Owner:** Friday + Dev Agent  
**Due:** 2026-04-19  
**Location:** `src/neorl/learning_loop.py`

**Current Performance:** ~1s end-to-end (shell)

**Target:** <300ms end-to-end (Python)

**Python Implementation:**
```python
# src/neorl/learning_loop.py
import json
from pathlib import Path
from typing import List, Dict
from .binary_rl import BinaryRLJudge
from .opd_hint import OPDHintExtractor

class LearningLoop:
    """Main learning loop orchestrator."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.judge = BinaryRLJudge()
        self.hint_extractor = OPDHintExtractor()
        self.rewards_dir = data_dir / ".rewards"
        self.hints_dir = data_dir / ".hints"
        
    def process_feedback(self, feedback: str, action: str, context: str) -> Dict:
        """
        Process user feedback and trigger learning.
        
        Returns:
            Learning result with reward, hints, and status
        """
        # Step 1: Judge reward
        reward, confidence = self.judge.judge(feedback, action)
        
        # Step 2: Extract hints (if negative)
        hints = []
        if reward < 0:
            hint = self.hint_extractor.extract(feedback)
            if hint:
                hints.append(hint)
        
        # Step 3: Record learning
        result = {
            'feedback': feedback,
            'action': action,
            'context': context,
            'reward': reward,
            'confidence': confidence,
            'hints': [h.__dict__ for h in hints],
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 4: Save to disk (optimized I/O)
        self._save_result(result)
        
        return result
    
    def _save_result(self, result: Dict):
        """Save learning result with optimized I/O."""
        # Implement atomic writes, batching, etc.
        pass
```

**Optimization Strategies:**
- [ ] Use Python's `json` for faster parsing (vs shell text processing)
- [ ] Implement in-memory caching (reduce disk I/O)
- [ ] Batch writes (reduce disk operations)
- [ ] Use `pathlib` for efficient file operations
- [ ] Profile and optimize hot paths

**Measurement:**
```bash
# Python version
$ time python -m neorl.learning_loop run
# Target: <300ms (vs ~1s shell)
```

**Deliverable:** 
- `src/neorl/learning_loop.py`
- `tests/test_learning_loop.py`
- Performance comparison → `docs/PERFORMANCE_OPTIMIZATION_v0.5.0.md`

---

#### Task 2.2: OPD Hint Extraction Enhancement
#### 任务 2.2：OPD Hint 提取增强

**Owner:** Friday  
**Due:** 2026-04-19  
**Location:** `scripts/hint_extractor.sh`

**Current State:**
```bash
# Basic pattern matching
if [[ "$feedback" =~ 应该 (.+) ]]; then
  hint="操作前 ${BASH_REMATCH[1]}"
fi
```

**Enhancements:**
- [ ] Support multi-step corrections ("先 X 再 Y")
- [ ] Support negative patterns ("不要 Y")
- [ ] Support conditional hints ("如果 X，则 Y")
- [ ] Add hint prioritization
- [ ] Implement hint deduplication

**Examples:**
| User Feedback | Extracted Hint |
|---------------|----------------|
| "应该先检查文件" | "操作前检查文件" |
| "不要放到 workspace" | "避免放到 workspace" |
| "先确认目录，再创建文件" | "顺序：先确认目录，再创建文件" |
| "如果是配置文档，放~/.openclaw" | "条件：配置文档 → 放~/.openclaw" |

**Deliverable:** 
- Enhanced `scripts/hint_extractor.sh`
- OPD patterns documentation → `docs/OPD_PATTERNS_v0.5.0.md`

---

#### Task 2.3: Code Organization
#### 任务 2.3：代码组织优化

**Owner:** Friday  
**Due:** 2026-04-20  
**Location:** `scripts/`

**Actions:**
- [ ] Organize scripts into logical subdirectories
- [ ] Create shared utility functions
- [ ] Document script dependencies
- [ ] Add script versioning
- [ ] Create script execution flow diagram

**Proposed Structure:**
```
scripts/
├── core/
│   ├── memory_retrieval.sh
│   ├── prm_judge.sh
│   ├── hint_extractor.sh
│   └── training_loop.sh
├── utils/
│   ├── logging.sh
│   ├── error_handling.sh
│   └── config.sh
├── tests/
│   ├── test_binary_rl.sh
│   ├── test_opd.sh
│   └── test_integration.sh
└── README.md
```

**Deliverable:** 
- Reorganized scripts
- Script organization guide → `docs/SCRIPT_ORGANIZATION.md`

---

### Week 3: Python Integration & Release (Apr 22-28)
### 第三周：Python 集成与发布（4 月 22-28 日）

#### Task 3.1: Shell-Python Integration Testing
#### 任务 3.1：Shell-Python 集成测试

**Owner:** Friday  
**Due:** 2026-04-24  
**Location:** `scripts/`, `src/neorl/`

**Integration Tests:**
```bash
# Test 1: Shell script calls Python correctly
$ ./scripts/prm_judge.sh "谢谢，很好" "created file"
# Expected: reward=+1 from Python

# Test 2: End-to-end learning loop
$ ./scripts/training_loop.sh run
# Expected: <300ms, Python backend

# Test 3: Error handling
$ ./scripts/hint_extractor.sh "invalid input"
# Expected: Graceful error, fallback to shell
```

**Test Coverage:**
- [ ] Binary RL: 50+ test cases
- [ ] OPD Hint: 30+ test cases
- [ ] Learning Loop: 20+ test cases
- [ ] Integration: 10+ end-to-end tests
- [ ] Edge cases: invalid input, missing files, etc.

**Target:** >90% code coverage (pytest-cov)

**Deliverable:** 
- Integration test report → `docs/INTEGRATION_TEST_v0.5.0.md`
- Coverage report → `htmlcov/` (pytest-cov)

---

#### Task 3.2: claw-mem v1.0.1 Collaboration Testing
#### 任务 3.2：claw-mem v1.0.1 协同测试

**Owner:** Friday + Peter  
**Due:** 2026-04-26  
**Location:** Real-world usage

**Test Scenarios:**
1. **Memory-Triggered Learning**
   - User asks → claw-mem retrieves → Friday responds → User corrects → claw-rl (Python) learns
   - Measure: End-to-end latency (target <500ms with Python)

2. **Pre-flight Memory Injection**
   - Session starts → claw-rl injects memories from claw-mem → Friday uses context
   - Measure: Injection time (target <200ms)

3. **Compaction Learning**
   - Auto-compaction → claw-rl (Python) learns from event
   - Measure: Event detection + learning time

**Test Plan:**
- [ ] Define test scenarios (5+ real-world cases)
- [ ] Execute tests with Peter
- [ ] Record Python vs Shell performance
- [ ] Document pain points
- [ ] Identify improvement areas

**Deliverable:** 
- Test report → `docs/COLLABORATION_TEST_REPORT_v0.5.0.md`
- Performance baseline → `docs/PERFORMANCE_BASELINE_v0.5.0.md`

---

#### Task 3.3: Documentation Update
#### 任务 3.3：文档更新

**Owner:** Friday  
**Due:** 2026-04-27  
**Location:** `docs/`, `README.md`, `SKILL.md`

**Documents to Update:**
- [ ] `README.md` - Add Python installation instructions
- [ ] `SKILL.md` - Update to reference Python backend
- [ ] `docs/ARCHITECTURE_DECISION_001.md` - Already done ✅
- [ ] `docs/REFACTOR_PLAN_v0.5.0.md` - This document
- [ ] `docs/PYTHON_MIGRATION_v0.5.0.md` - Migration guide
- [ ] `docs/PERFORMANCE_BASELINE_v0.5.0.md` - Python vs Shell comparison
- [ ] `docs/COLLABORATION_TEST_REPORT_v0.5.0.md` - From Task 3.2

**SKILL.md Update Example:**
```markdown
## Installation

```bash
git clone ... ~/.openclaw/workspace/skills/claw-rl
cd ~/.openclaw/workspace/skills/claw-rl
pip install -e .  # NEW: Install Python dependencies
```

## Architecture

claw-rl v0.5.0 uses **hybrid architecture**:
- Shell scripts for OpenClaw integration (backward compatible)
- Python core for performance and extensibility
```

**Deliverable:** Complete, up-to-date documentation

---

#### Task 3.2: Performance Baseline Documentation
#### 任务 3.2：性能基线文档化

**Owner:** Friday  
**Due:** 2026-04-26  
**Location:** `docs/PERFORMANCE_BASELINE_v0.5.0.md`

**Metrics to Document:**

| Metric | Measurement | Target | Actual |
|--------|-------------|--------|--------|
| **Binary RL Accuracy** | Test dataset (100 cases) | >95% | TBD |
| **Learning Loop Latency** | End-to-end time | <500ms | TBD |
| **OPD Hint Extraction** | Pattern match time | <100ms | TBD |
| **Memory Injection** | Pre-flight time | <200ms | TBD |
| **Error Rate** | Failed operations / total | <1% | TBD |
| **Resource Usage** | CPU, memory during learning | Minimal | TBD |

**Deliverable:** Complete performance baseline document

---

#### Task 3.3: Documentation Update
#### 任务 3.3：文档更新

**Owner:** Friday  
**Due:** 2026-04-27  
**Location:** `docs/`, `README.md`, `SKILL.md`

**Documents to Update:**
- [ ] `README.md` - Project overview, quick start
- [ ] `SKILL.md` - Skill capabilities, usage examples
- [ ] `docs/ARCHITECTURE_DECISION_001.md` - Already done ✅
- [ ] `docs/REFACTOR_PLAN_v0.5.0.md` - This document
- [ ] `docs/PERFORMANCE_BASELINE_v0.5.0.md` - From Task 3.2
- [ ] `docs/COLLABORATION_TEST_REPORT_v0.5.0.md` - From Task 3.1

**Deliverable:** Complete, up-to-date documentation

---

#### Task 3.4: Version Bump & Release
#### 任务 3.4：版本升级与发布

**Owner:** Friday  
**Due:** 2026-04-28  
**Location:** `package.json`, git tags

**Actions:**
- [ ] Update `package.json` version to `0.5.0`
- [ ] Update `SKILL.md` version metadata
- [ ] Create git tag: `v0.5.0`
- [ ] Write release notes
- [ ] Test installation from fresh OpenClaw

**Release Notes Template:**
```markdown
## claw-rl v0.5.0 (2026-04-28)

### Enhancements
- Binary RL accuracy improved to >95%
- Learning loop latency reduced to <500ms
- OPD hint extraction enhanced with multi-pattern support
- Error handling hardened across all scripts

### Testing
- Real-world collaboration with claw-mem v1.0.1 validated
- Performance baseline established
- 100+ test cases covered

### Documentation
- Complete SKILL.md update
- Architecture decision records
- Performance baseline documented

### Known Issues
- [List any remaining issues]

### Next Steps
- Continue stability monitoring
- Prepare for Plugin migration (future, after P0-4)
```

**Deliverable:** 
- Released v0.5.0
- Release notes → `docs/RELEASE_NOTES_v0.5.0.md`

---

## 4. Success Criteria
## 4. 成功标准

### Must Have (P0) - Python Migration
### 必须有（P0）- Python 迁移

- [ ] ✅ Python project structure created (`src/neorl/`, `pyproject.toml`)
- [ ] ✅ Binary RL Python implementation (>95% accuracy)
- [ ] ✅ OPD Hint Python implementation (4+ pattern types)
- [ ] ✅ Learning Loop Python implementation (<300ms latency)
- [ ] ✅ Shell-Python integration working (backward compatible)
- [ ] ✅ Test coverage >90% (pytest-cov)
- [ ] ✅ Zero critical bugs for 2+ weeks
- [ ] ✅ Successful collaboration with claw-mem v1.0.1 demonstrated
- [ ] ✅ Performance baseline documented (Python vs Shell comparison)

### Should Have (P1)
### 应该有（P1）

- [ ] ✅ OPD hint extraction supports complex patterns
- [ ] ✅ Error handling covers 95%+ edge cases
- [ ] ✅ Complete documentation updated
- [ ] ✅ Code organization improved

### Nice to Have (P2)
### 最好有（P2）

- [ ] Scripts organized into subdirectories
- [ ] Shared utility library created
- [ ] Automated test suite expanded

---

## 5. Risk Management
## 5. 风险管理

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Binary RL accuracy doesn't improve** | High | Low | Fallback to current patterns, iterate |
| **Performance optimization fails** | Medium | Low | Document current baseline, defer to v0.6.0 |
| **claw-mem collaboration issues** | High | Medium | Test incrementally, document pain points |
| **Documentation incomplete** | Low | Medium | Prioritize core docs, defer nice-to-haves |
| **Timeline slippage** | Medium | Medium | Focus on P0, defer P1/P2 if needed |

---

## 6. Document Organization
## 6. 文档组织

**Critical Rule:** All claw-rl documents stay in claw-rl's docs directory!

**关键规则：** 所有 claw-rl 文档保留在 claw-rl 的 docs 目录中！

| Document | Location | Status |
|----------|----------|--------|
| `ARCHITECTURE_DECISION_001.md` | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | ✅ Done |
| `REFACTOR_PLAN_v0.5.0.md` | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | 📋 This doc |
| `BINARY_RL_ACCURACY_v0.5.0.md` | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | 📋 TODO |
| `PERFORMANCE_OPTIMIZATION_v0.5.0.md` | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | 📋 TODO |
| `OPD_PATTERNS_v0.5.0.md` | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | 📋 TODO |
| `COLLABORATION_TEST_REPORT_v0.5.0.md` | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | 📋 TODO |
| `PERFORMANCE_BASELINE_v0.5.0.md` | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | 📋 TODO |
| `RELEASE_NOTES_v0.5.0.md` | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | 📋 TODO |

**❌ DO NOT:**
- Put claw-rl docs in `/Users/liantian/workspace/neoclaw/docs/`
- Put claw-rl docs in `/Users/liantian/workspace/claw-mem/docs/`

---

## 7. Communication Plan
## 7. 沟通计划

### Weekly Check-ins
### 每周检查

| When | What | With Whom |
|------|------|-----------|
| **Mon 10:00** | Week plan review | Peter + Friday |
| **Wed 10:00** | Mid-week progress | Friday report |
| **Fri 16:00** | Week completion review | Peter + Friday |

### Key Decision Points
### 关键决策点

| Decision | When | Who |
|----------|------|-----|
| **Binary RL patterns approval** | Week 1 | Peter + Friday |
| **Performance optimization approach** | Week 2 | Peter + Friday |
| **Collaboration test results** | Week 3 | Peter + Friday |
| **v0.5.0 release approval** | Week 3 end | Peter |

---

## 8. Next Steps
## 8. 下一步

### Immediate (Today - Apr 8)
### 立即（今天 - 4 月 8 日）

- [ ] **Peter reviews this plan** → Approval/adjustments
- [ ] **Create v0.5.0-refactor branch**
- [ ] **Setup project tracking** (TBD: GitHub Projects or simple checklist)

### Week 1 Start (Apr 8)
### 第一周开始（4 月 8 日）

- [ ] **Task 1.1:** Project structure review
- [ ] **Task 1.2:** Binary RL accuracy improvement kickoff
- [ ] **Daily progress updates** to Peter

---

## 9. Related Documents
## 9. 相关文档

### claw-rl Documents
### claw-rl 文档

| Document | Location | Project |
|----------|----------|---------|
| ARCHITECTURE_DECISION_001.md | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | claw-rl |
| REFACTOR_PLAN_v0.5.0.md | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | claw-rl |
| PYTHON_MIGRATION_v0.5.0.md | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | claw-rl (TODO) |
| PERFORMANCE_BASELINE_v0.5.0.md | `/Users/liantian/workspace/osprojects/claw-rl/docs/` | claw-rl (TODO) |

### Reference Documents (claw-mem)
### 参考文档（claw-mem）

| Document | Location | Purpose |
|----------|----------|---------|
| claw-mem pyproject.toml | `/Users/liantian/workspace/osprojects/claw-mem/pyproject.toml` | Python config reference |
| claw-mem src/ | `/Users/liantian/workspace/osprojects/claw-mem/src/claw_mem/` | Python code structure reference |
| claw-mem tests/ | `/Users/liantian/workspace/osprojects/claw-mem/tests/` | pytest test reference |

### neoclaw Documents
### neoclaw 文档

| Document | Location | Project |
|----------|----------|---------|
| P0_PRIORITY_UPDATE.md | `/Users/liantian/workspace/neoclaw/docs/` | neoclaw |
| OPENCLAW_PLUGIN_RESEARCH.md | `/Users/liantian/workspace/neoclaw/docs/` | neoclaw |
| INTEGRATED_EVOLUTION_PLAN.md | `/Users/liantian/workspace/neoclaw/docs/` | neoclaw |

---

## 10. Document History
## 10. 文档历史

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0 | 2026-03-24T10:50+08:00 | Initial refactor plan (Shell-only) | Friday |
| 1.1 | 2026-03-24T11:05+08:00 | **Added Python migration decision** (Progressive migration starting v0.5.0) | Friday |

---

## 11. Python Migration Checklist
## 11. Python 迁移检查清单

### Phase 1: Project Setup (Week 1)
### 阶段 1：项目设置（第 1 周）

- [ ] Create `src/neorl/` directory
- [ ] Create `tests/` directory
- [ ] Create `pyproject.toml`
- [ ] Create `requirements.txt` (minimal)
- [ ] Create `requirements-dev.txt` (pytest, pytest-cov)
- [ ] Update `.gitignore` for Python artifacts
- [ ] Test `pip install -e .` works

### Phase 2: Core Implementation (Week 1-2)
### 阶段 2：核心实现（第 1-2 周）

- [ ] Implement `src/neorl/binary_rl.py`
- [ ] Implement `src/neorl/opd_hint.py`
- [ ] Implement `src/neorl/learning_loop.py`
- [ ] Implement `src/neorl/utils.py`
- [ ] Write unit tests (>90% coverage)
- [ ] Update shell scripts to call Python

### Phase 3: Integration & Testing (Week 3)
### 阶段 3：集成与测试（第 3 周）

- [ ] Shell-Python integration tests
- [ ] claw-mem collaboration tests
- [ ] Performance benchmark (Python vs Shell)
- [ ] Documentation update
- [ ] v0.5.0 release

---

*Document Created: 2026-03-24T10:50+08:00*  
*Updated: 2026-03-24T11:05+08:00 (v1.1 - Python migration decision)*  
*Project: claw-rl (NeoMind)*  
*Discussion Participants: Peter Cheng, Friday*  
*Timeline: 2026-04-08 to 2026-04-30*  
*Architecture: Progressive Python Migration (Shell → Python)*  
*"Ad Astra Per Aspera"*

**⚠️ Critical Reminders:**
> 1. All claw-rl documents stay in `/Users/liantian/workspace/osprojects/claw-rl/docs/`. Never mix with neoclaw or claw-mem docs!
> 2. Keep backward compatibility - shell scripts must continue working during Python migration
> 3. Learn from claw-mem's successful Python architecture

**⚠️ 关键提醒:**
> 1. 所有 claw-rl 文档保留在 `/Users/liantian/workspace/osprojects/claw-rl/docs/`。绝不与 neoclaw 或 claw-mem 文档混淆！
> 2. 保持向后兼容 - Shell 脚本在 Python 迁移期间必须继续工作
> 3. 学习 claw-mem 成功的 Python 架构

---

*Document Created: 2026-03-24T10:50+08:00*  
*Project: claw-rl (NeoMind)*  
*Discussion Participants: Peter Cheng, Friday*  
*Timeline: 2026-04-08 to 2026-04-30*  
*"Ad Astra Per Aspera"*

**⚠️ Critical Reminder:**
> All claw-rl documents stay in `/Users/liantian/workspace/osprojects/claw-rl/docs/`. Never mix with neoclaw or claw-mem docs!

**⚠️ 关键提醒:**
> 所有 claw-rl 文档保留在 `/Users/liantian/workspace/osprojects/claw-rl/docs/`。绝不与 neoclaw 或 claw-mem 文档混淆！
