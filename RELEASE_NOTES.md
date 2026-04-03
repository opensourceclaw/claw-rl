# Release Notes - v2.0.0-rc.1

**Release Date:** 2026-04-03  
**Status:** Release Candidate 1  
**Previous Version:** v2.0.0-beta.3

---

## Summary

Sprint 2 complete! This release introduces the Feedback Loop system, enabling AI agents to learn from user feedback.

---

## New Features

### Feedback Loop System

**Explicit Feedback Collection** (Week 5)
- 6 feedback types: thumbs_up, thumbs_down, rating, text, correction, rejection
- Text sentiment analysis (positive/negative/neutral)
- OPD hint extraction (should, should_not, sequence, conditional)
- JSON persistence storage

**Implicit Feedback Inference** (Week 6)
- 5 implicit signal types: response_time, retry_action, continuation, abandonment, rephrase
- User behavior tracking
- Session context analysis

**Signal Fusion** (Week 6)
- Explicit + Implicit signal fusion
- Time decay weighting
- Confidence calculation

**Strategy Optimizer** (Week 7)
- Feedback-driven parameter adjustment
- A/B Testing framework
- Learning effect evaluation with ROI metrics

---

## Code Quality

### Testing
- **391 tests** passing
- **75% code coverage**

### Dual AI Auditing
- ✅ JARVIS independent review passed
- ✅ All Major issues fixed
- ✅ Input validation added
- ✅ Type annotations improved

---

## Bug Fixes

### Critical
- None

### Major
- Fixed weight normalization division by zero
- Fixed time decay boundary issues
- Fixed feedback clearing data loss
- Fixed history record unbounded growth
- Fixed state loading validation

### Minor
- Added confidence range validation [0,1]
- Added signal value validation
- Relaxed type annotations for extensibility

---

## Performance

- Initialize: < 1ms
- Collect Feedback: < 0.1ms
- Signal Fusion: < 0.5ms
- Strategy Optimization: < 1ms

---

## Documentation

- ADR-007: Versioning Strategy
- Sprint 2 Dual AI Audit Checklist
- Sprint 2 Audit Report
- Sprint 3 Plan (C-P-A Model Integration)

---

## Breaking Changes

None. API backward compatible with v2.0.0-beta.x.

---

## Migration Guide

No migration needed. Upgrade from v2.0.0-beta.3:

```bash
pip install claw-rl==2.0.0rc1
```

---

## Known Issues

- Test coverage at 75% (below 80% target, acceptable for RC)
- Some advanced evaluation features need production testing

---

## Contributors

- Friday (Main Agent) - Development
- JARVIS (Adversary Agent) - Code Review

---

## Next Steps

- Production testing
- User feedback collection
- Sprint 3: C-P-A Model Integration

---

**Full Changelog:** [CHANGELOG.md](CHANGELOG.md)
