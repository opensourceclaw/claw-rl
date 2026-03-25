# claw-rl v0.8.0 Release Notes

**Release Date:** 2026-03-25  
**Version:** 0.8.0  
**Type:** Minor Release (Learning Capabilities Enhancement)  
**License:** Apache-2.0

---

## Executive Summary

claw-rl v0.8.0 introduces three major learning capabilities that enable the system to learn from user interactions and improve over time. This release focuses on value preference learning, confidence calibration, and conflict resolution strategy optimization.

---

## ✨ New Features

### 1. Value Preference Learning

**Learn user value preferences from decision outcomes:**

- Records decision history with satisfaction ratings
- Analyzes value alignment for each decision
- Reinforces values from positive outcomes
- Adjusts values from negative outcomes
- Persistent storage of value priorities
- Ranked value recommendations

**Example:**
```python
from claw_rl.value_learning import ValuePreferenceLearner

learner = ValuePreferenceLearner()
learner.record_decision(decision_record)
priorities = learner.get_priorities()  # {"家庭": 8.4, "财富": 7.2, ...}
```

**Benefits:**
- Personalized decision support
- Adapts to user's evolving values
- Improves recommendation relevance

---

### 2. Calibration Error Learning

**Learn confidence calibration from predictions vs outcomes:**

- Records predicted confidence vs actual outcomes
- Detects overconfidence and underconfidence
- Calculates calibration error per capability
- Provides calibrated confidence scores
- Quality assessment (excellent/good/fair/poor)
- Suggests confidence adjustments

**Example:**
```python
from claw_rl.calibration_learning import CalibrationLearner

learner = CalibrationLearner()
learner.record_calibration(record)
calibrated = learner.get_calibrated_confidence("intent_understanding", 0.9)
# Returns adjusted confidence based on historical accuracy
```

**Benefits:**
- More accurate confidence estimates
- Identifies capability limitations
- Improves meta-cognitive accuracy

---

### 3. Conflict Resolution Strategy Learning

**Learn effective conflict resolution strategies:**

- Records strategy usage and outcomes
- Calculates effectiveness per strategy
- Ranks strategies by effectiveness score
- Recommends best strategies per conflict type
- Tracks success rates and satisfaction

**Example:**
```python
from claw_rl.strategy_learning import StrategyLearner

learner = StrategyLearner()
learner.record_strategy(strategy_record)
recommended = learner.get_recommended_strategy("value_based")
# Returns "priority_based" if most effective
```

**Benefits:**
- Improves conflict resolution over time
- Data-driven strategy selection
- Higher success rates

---

## 🔧 Technical Details

### New Modules

**value_learning.py** (~330 lines)
- `ValuePreferenceLearner` class
- `ValuePreference` dataclass
- `DecisionRecord` dataclass
- Persistent storage (JSON)

**calibration_learning.py** (~410 lines)
- `CalibrationLearner` class
- `CalibrationRecord` dataclass
- `CapabilityCalibration` dataclass
- Running averages for efficiency

**strategy_learning.py** (~380 lines)
- `StrategyLearner` class
- `StrategyRecord` dataclass
- `StrategyEffectiveness` dataclass
- Effectiveness scoring algorithm

### Code Statistics

- **New code:** ~1120 lines
- **New modules:** 3
- **New tests:** 19
- **Total tests:** 101 (all passing)
- **Test coverage:** >85%

---

## 📊 Version Comparison

| Feature | v0.7.0 | v0.8.0 | Change |
|---------|--------|--------|--------|
| **Learning Capabilities** | Basic (Binary RL, OPD) | Advanced (Value, Calibration, Strategy) | ✅ Major upgrade |
| **Code base** | ~20 lines (scripts) | ~1140 lines (+Python modules) | +5600% |
| **Test coverage** | Basic | >85% | ✅ Improved |
| **Backward Compatible** | Yes | Yes | ✅ Yes |

---

## 🧪 Testing

### Test Results

```
============================= 101 passed in 0.71s ==============================
```

**New Test Modules:**
- `test_value_learning.py` (6 tests)
- `test_calibration_learning.py` (7 tests)
- `test_strategy_learning.py` (6 tests)

**Run Tests:**
```bash
cd claw-rl
./venv/bin/python -m pytest tests/ -v
```

---

## 📦 Installation

### From GitHub

```bash
git clone https://github.com/opensourceclaw/claw-rl.git
cd claw-rl
./scripts/install.sh
```

### Upgrade

```bash
cd claw-rl
git pull origin v0.5.0-python-migration
./scripts/install.sh
```

---

## ⚠️ Breaking Changes

**None** - This release is 100% backward compatible with v0.7.0.

**Migration:**
- No migration needed
- Existing scripts continue to work
- New Python modules are additive

---

## 🐛 Bug Fixes

- N/A (This is a feature release)

---

## 🙏 Acknowledgments

**Core Development:**
- Peter Cheng - Architecture Design
- Friday AI - Implementation

**Testing:**
- 101 test cases (all passing)

---

## 📝 License

Copyright 2026 Peter Cheng

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

## 🔗 References

- **GitHub Release:** https://github.com/opensourceclaw/claw-rl/releases/tag/v0.8.0
- **Full Changelog:** https://github.com/opensourceclaw/claw-rl/compare/v0.7.0...v0.8.0
- **Documentation:** `/Users/liantian/workspace/osprojects/claw-rl/docs/` (local only)

---

**Release Status:** ✅ **APPROVED**  
**QA Status:** ✅ **101 TESTS PASSED**  
**Next Release:** v0.9.0 or v1.0.0 (Phase 3 Completion)
