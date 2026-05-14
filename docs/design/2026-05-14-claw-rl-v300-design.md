# claw-rl v3.0.0 — Skill Library + Triad Architecture

**版本**: v1.0
**日期**: 2026-05-14
**作者**: Jarvis
**状态**: 设计完成

---

## 1. 模块总览

```
claw-rl v3.0.0:
├── SkillLibrary        — 技能存储/检索/改进
├── ProcessRewardModel  — 步骤级过程奖励
├── TriadArchitecture   — Proposer → Solver → Judge
└── SelfPlayRL          — 零数据 Self-Play
```

## 2. SkillLibrary

```python
class SkillLibrary:
    def __init__(self): skills: Dict, state_index: Dict
    def add_skill(name, state_pattern, action, reward)
    def find_skills(state, top_k=5) -> List[Skill]
    def improve_skill(name, reward_delta)
    def get_stats() -> Dict
```

## 3. ProcessRewardModel

```python
class ProcessRewardModel:
    def __init__(self): weights
    def evaluate_step(step_description, outcome) -> float
    def evaluate_sequence(steps) -> ProcessRewardResult
    def get_weighted_score(scores) -> float
```

## 4. TriadArchitecture

```python
class Proposer:
    def generate_task(level, previous_skills) -> Task

class Solver:
    def solve(task, skills) -> Solution

class Judge:
    def evaluate(solution, expected) -> Judgement

class TriadArchitecture:
    proposer: Proposer; solver: Solver; judge: Judge
    def run_cycle(level) -> TriadResult
    def run_self_play(n_cycles)
```

## 5. 文件结构

```
src/claw_rl/
├── skill_library.py
├── process_reward.py
├── triad.py
└── self_play.py
```

## 6. 测试: 20+ tests

- SkillLibrary: 5 tests
- ProcessRewardModel: 4 tests
- TriadArchitecture: 6 tests
- SelfPlayRL: 5 tests
