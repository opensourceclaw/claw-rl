# claw-rl v0.9.0 Release Notes

**Release Date:** 2026-03-25  
**Version:** 0.9.0  
**Type:** Minor Release (Contextual Learning)  
**License:** Apache-2.0

---

## Executive Summary

claw-rl v0.9.0 introduces contextual learning capabilities, enabling the system to learn from decision context (emotion, time, situation). This release focuses on pattern recognition based on context.

---

## ✨ New Features

### 1. Contextual Learning

**Learn from decision context:**

- Records decision context (emotion, time, situation, urgency)
- Auto-detects time of day and day of week
- Learns patterns: "当{emotion}时，您倾向于选择{option}"
- Pattern search by emotion/decision_type
- Decision history with context
- Learning statistics

**Example:**
```
记录决策：
  情绪：焦虑
  情境：家庭
  选择：组合方案
  满意度：85%

学习到的模式：
  "当焦虑时，您倾向于选择组合方案（满意度 85%）"
```

---

## 🔧 Technical Details

### New Modules

**context/**
- `context_learning.py` - Contextual learning engine
- `__init__.py` - Module exports

### Code Statistics

- **New code:** ~380 lines
- **New modules:** 1 (context)
- **Test coverage:** >90%

---

## 📊 Version Comparison

| Feature | v0.8.0 | v0.9.0 | Change |
|---------|--------|--------|--------|
| **Learning** | Value, Calibration, Strategy | + Contextual | ✅ Enhanced |
| **Pattern Recognition** | Basic | Context-based | ✅ Major upgrade |
| **Decision History** | Basic | With context | ✅ Enhanced |
| **Code base** | ~1500 lines | ~1880 lines | +380 lines |
| **Backward Compatible** | Yes | Yes | ✅ Yes |

---

## 📦 Installation

```bash
git clone https://github.com/opensourceclaw/claw-rl.git
cd claw-rl
./scripts/install.sh
```

---

## ⚠️ Breaking Changes

**None** - This release is 100% backward compatible with v0.8.0.

---

## 🙏 Acknowledgments

**Core Development:**
- Peter Cheng - Architecture Design
- Friday AI - Implementation

---

## 📝 License

Apache-2.0

---

**Full Changelog:** https://github.com/opensourceclaw/claw-rl/compare/v0.8.0...v0.9.0
