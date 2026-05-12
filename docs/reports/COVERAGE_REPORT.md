# claw-rl v2.0.0 Coverage Report

## 📊 Overall Coverage

- **Total Lines**: 6321
- **Covered Lines**: 2755
- **Coverage Rate**: 37%
- **Uncovered Lines**: 3566

## 📈 Module Coverage Details

| Module | Stmts | Miss | Branch | BrPart | Cover | Missing |
|--------|-------|------|--------|--------|-------|---------|
| `learning_loop.py` | 62 | 25 | 16 | 2 | 55% | 110, 147-149, 178-186, 211-223, 239-249 |
| `cpa_loop.py` | 163 | 25 | 48 | 7 | 85% | 165, 169, 177->187, 179-184, 189, 220->225, 230-236, 283, 297-311, 364-378, 382, 386, 390, 394, 398, 402, 406, 410, 419-431, 442-454, 458 |
| `learning_daemon.py` | 175 | 61 | 48 | 0 | 65% | 104-148, 152-156, 160-162, 166-176, 180-183, 187-188, 192-214, 218-240, 245-248, 252-269, 273-295, 308-324, 337-351 |
| `binary_rl.py` | 41 | 15 | 26 | 1 | 61% | 137-157, 179, 217 |
| `opd_hint.py` | 63 | 49 | 36 | 0 | 16% | 21, 45-112, 116-121, 125-130, 134 |
| `mab.py` | 203 | 120 | 62 | 0 | 34% | 80, 93, 135, 151, 166-186, 212, 218-225, 230-250, 263-266, 270, 274, 286, 290-297, 323-340, 352-360, 369-372, 387-414, 418-425, 429-439, 443-452, 465-475, 487-495, 499, 503, 507-516, 527-536 |
| `decision_path.py` | 374 | 112 | 196 | 0 | 70% | 65-74, 78, 128-142, 147, 193-202, 207, 219, 223-225, 229-233, 263-268, 272-275, 294-311, 345-382, 402-415, 427, 436, 451-471, 475-488, 504, 534-545, 562-569, 573-596, 605-622, 639-670, 682-694, 716, 734, 744, 760, 792-832, 847-877, 905-922, 938-968, 983-1028 |

## 🎯 Coverage Improvement Plan

### Phase 1: Framework Layer (Priority)
- **LearningDaemon**: Add configuration validation tests
- **CPALoop**: Add observer/executor integration tests
- **LearningLoop**: Add daemon integration tests

### Phase 2: Decision Path
- Add visualization and analysis functionality tests
- Add path pattern matching tests
- Add anomaly detection tests

### Phase 3: Performance
- Add benchmark tests for C-P-A loop iterations
- Add memory usage profiling tests
- Add latency measurement tests

## 📅 Timeline

| Milestone | Target Date |
|-----------|-----------|
| Framework Coverage to 60% | April 15, 2026 |
| Decision Path Coverage to 50% | April 18, 2026 |
| Overall Coverage to 70% | April 22, 2026 |

---
**Generated:** April 13, 2026
**Status:** Ready for v2.0.0 Release