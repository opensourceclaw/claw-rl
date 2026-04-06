# Sprint 3 Plan - C-P-A Model Integration

**项目:** claw-rl  
**开始日期:** 2026-04-07 (预计)  
**预计周期:** Week 8-10 (3 周)  
**前置条件:** Sprint 2 完成, Dual AI Audit 通过, ADR-008 采纳

---

## 目标

实现完整的 C-P-A (Continuous Planning and Autonomous) 学习循环，同时保持框架独立性。

### 设计原则 (ADR-008)

**关键约束：** claw-rl 必须保持框架无关，通过适配器模式集成外部框架。

```
┌─────────────────────────────────────────────────────────────┐
│  外部框架 (neoclaw, other-app, future-app)                   │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  adapters/  (适配器层 - 框架特定实现)                  │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        │                                    │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  protocols/  (协议层 - 抽象接口)                       │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        │                                    │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  core/  (核心层 - 框架无关)                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 背景分析

### Hybrid SDLC C-P-A Model

```
┌─────────────────────────────────────────────────────────────┐
│                    C-P-A 学习循环                            │
│                                                             │
│     ┌──────────┐                                            │
│     │ Observe  │ ← 收集反馈指标                              │
│     │  观察    │   (显式 + 隐式)                             │
│     └────┬─────┘                                            │
│          │                                                  │
│          ▼                                                  │
│     ┌──────────┐                                            │
│     │ Orient   │ ← 分析学习效果                              │
│     │  定向    │   (信号融合 + 评估)                          │
│     └────┬─────┘                                            │
│          │                                                  │
│          ▼                                                  │
│     ┌──────────┐                                            │
│     │ Decide   │ ← 策略优化决策                              │
│     │  决策    │   (A/B 测试 + 优化器)                        │
│     └────┬─────┘                                            │
│          │                                                  │
│          ▼                                                  │
│     ┌──────────┐                                            │
│     │  Act     │ ← 执行优化                                  │
│     │  行动    │   (参数调整 + 配置更新)                      │
│     └────┬─────┘                                            │
│          │                                                  │
│          ▼                                                  │
│     ┌──────────┐                                            │
│     │  Learn   │ ← 评估改进效果                              │
│     │  学习    │   (效果评估 + 知识积累)                      │
│     └──────────┘                                            │
│          │                                                  │
│          └──────────────────────────────────────→ Observe   │
└─────────────────────────────────────────────────────────────┘
```

### Sprint 2 成果回顾

| 组件 | 功能 | C-P-A 映射 | 框架相关? |
|------|------|-----------|----------|
| FeedbackCollector | 收集显式反馈 | Observe | ❌ 否 |
| ImplicitFeedbackInference | 推断隐式信号 | Observe | ❌ 否 |
| SignalFusion | 信号融合 | Orient | ❌ 否 |
| LearningEvaluation | 效果评估 | Orient | ❌ 否 |
| StrategyOptimizer | 策略优化 | Decide | ❌ 否 |
| ABTestingFramework | A/B 测试 | Decide | ❌ 否 |
| - | 参数调整 | Act | 待实现 |
| - | 知识积累 | Learn | 待实现 |

**差距分析：**
- ✅ Observe: 完成（框架无关）
- ✅ Orient: 完成（框架无关）
- ✅ Decide: 完成（框架无关）
- ⚠️ Act: 部分完成（需实现，保持框架无关）
- ❌ Learn: 未完成（需实现，保持框架无关）
- ❌ 集成: 未完成（需适配器层）

---

## 核心任务

### Week 8: Act 层实现

**目标:** 完善行动层，实现参数调整和配置更新（框架无关）

**任务:**
1. **Parameter Applier**
   - 应用优化器参数调整
   - 运行时参数注入
   - 回滚机制
   - **约束:** 无外部框架依赖

2. **Configuration Manager**
   - 版本化配置
   - 配置验证
   - 热更新支持
   - 配置审计日志
   - **约束:** 无外部框架依赖

3. **Action Executor**
   - 安全执行环境
   - 执行日志
   - 失败重试
   - 状态追踪
   - **约束:** 无外部框架依赖

**交付物:**
- `learning/applier.py` - 参数应用器
- `learning/config_manager.py` - 配置管理器
- `learning/executor.py` - 行动执行器
- `tests/test_applier.py` - 单元测试
- `tests/test_config_manager.py` - 单元测试
- `tests/test_executor.py` - 单元测试

---

### Week 9: Learn 层实现

**目标:** 实现学习层，完成知识积累（框架无关）

**任务:**
1. **Knowledge Base**
   - 学习规则存储
   - 规则索引和检索
   - 规则生命周期管理
   - 规则冲突解决
   - **约束:** 无外部框架依赖

2. **Experience Replay**
   - 经验回放缓冲区
   - 采样策略
   - 优先级队列
   - 经验去重
   - **约束:** 无外部框架依赖

3. **Self-Improvement**
   - 自动规则提取
   - 规则验证
   - 规则部署
   - 效果监控
   - **约束:** 无外部框架依赖

**交付物:**
- `learning/knowledge_base.py` - 知识库
- `learning/experience_replay.py` - 经验回放
- `learning/self_improvement.py` - 自我改进
- `tests/test_knowledge_base.py` - 单元测试
- `tests/test_experience_replay.py` - 单元测试
- `tests/test_self_improvement.py` - 单元测试

---

### Week 10: 协议层与适配器

**目标:** 定义抽象协议，实现框架适配器，保持独立性

**任务:**
1. **协议层定义 (Day 1-2)**
   - `protocols/observer.py` - 观察者协议
   - `protocols/decision_maker.py` - 决策者协议
   - `protocols/executor.py` - 执行者协议
   - `protocols/signal_adapter.py` - 信号适配器协议
   - **约束:** 纯抽象接口，无实现

2. **通用 C-P-A 循环 (Day 3)**
   - `core/cpa_loop.py` - 框架无关的 C-P-A 循环实现
   - 基于协议的通用实现
   - **约束:** 仅依赖协议层

3. **适配器实现 (Day 4)**
   - `adapters/base_adapter.py` - 基础适配器
   - `adapters/neoclaw_adapter.py` - NeoClaw 适配器（可选依赖）
   - `adapters/openclaw_adapter.py` - OpenClaw Gateway 适配器（可选依赖）
   - **约束:** 适配器放在可选模块中

4. **集成测试 (Day 5)**
   - 协议层单元测试
   - C-P-A 循环测试
   - 适配器测试（使用 mock）
   - 独立性验证测试（确保核心无框架依赖）
   - Dual AI Audit (Full)

**交付物:**
- `protocols/` - 协议层目录
- `adapters/` - 适配器目录
- `core/cpa_loop.py` - 通用 C-P-A 循环
- `tests/test_protocols.py` - 协议测试
- `tests/test_adapters.py` - 适配器测试
- `tests/test_cpa_loop.py` - C-P-A 循环测试
- `tests/test_independence.py` - 独立性验证测试

---

## 文件结构

```
src/claw_rl/
├── protocols/              # Week 10 新增：协议层
│   ├── __init__.py
│   ├── observer.py
│   ├── decision_maker.py
│   ├── executor.py
│   └── signal_adapter.py
│
├── adapters/               # Week 10 新增：适配器层
│   ├── __init__.py
│   ├── base_adapter.py
│   ├── neoclaw_adapter.py  # 可选依赖
│   └── openclaw_adapter.py # 可选依赖
│
├── core/                   # Week 10 新增：核心重组
│   ├── __init__.py
│   └── cpa_loop.py         # 通用 C-P-A 循环
│
├── feedback/               # Sprint 2 完成
│   └── ...
│
├── learning/               # Sprint 2, 3
│   ├── ... (Sprint 2 完成)
│   ├── applier.py          # Week 8 新增
│   ├── config_manager.py   # Week 8 新增
│   ├── executor.py         # Week 8 新增
│   ├── knowledge_base.py   # Week 9 新增
│   ├── experience_replay.py # Week 9 新增
│   └── self_improvement.py # Week 9 新增
│
├── agents/                 # 保留
│   └── signal_collector.py # 重构：移除框架特定字段
│
└── __init__.py
│
tests/
├── ... (Sprint 2 完成)
├── test_applier.py         # Week 8
├── test_config_manager.py  # Week 8
├── test_executor.py        # Week 8
├── test_knowledge_base.py  # Week 9
├── test_experience_replay.py # Week 9
├── test_self_improvement.py # Week 9
├── test_protocols.py       # Week 10
├── test_adapters.py        # Week 10
├── test_cpa_loop.py        # Week 10
└── test_independence.py    # Week 10 独立性验证
```

---

## 验收标准

### Week 8
- [ ] Parameter Applier 实现完成
- [ ] Configuration Manager 实现完成
- [ ] Action Executor 实现完成
- [ ] 单元测试覆盖率 > 80%
- [ ] **无外部框架依赖** (代码审查)

### Week 9
- [ ] Knowledge Base 实现完成
- [ ] Experience Replay 实现完成
- [ ] Self-Improvement 实现完成
- [ ] 单元测试覆盖率 > 80%
- [ ] **无外部框架依赖** (代码审查)

### Week 10
- [ ] 协议层定义完成（Observer, DecisionMaker, Executor, SignalAdapter）
- [ ] 通用 C-P-A 循环实现完成
- [ ] 基础适配器实现完成
- [ ] NeoClaw 适配器实现完成
- [ ] 独立性验证测试通过
- [ ] 端到端测试通过
- [ ] Dual AI Audit 通过

### 独立性验证测试

```python
# tests/test_independence.py

def test_no_neoclaw_imports():
    """验证核心模块没有导入 neoclaw"""
    import claw_rl
    # 检查所有核心模块
    core_modules = [
        'claw_rl.feedback',
        'claw_rl.learning',
        'claw_rl.pattern',
        'claw_rl.core',
    ]
    for module in core_modules:
        # 确保没有 neoclaw 导入
        assert 'neoclaw' not in dir(module)

def test_adapters_are_optional():
    """验证适配器是可选依赖"""
    import sys
    # 移除 neoclaw（如果存在）
    if 'neoclaw' in sys.modules:
        del sys.modules['neoclaw']
    
    # 核心模块应该仍然可以导入
    from claw_rl import (
        PatternRecognitionEngine,
        BinaryRLJudge,
        LearningLoop,
    )
    
    # 适配器模块应该只在显式导入时才可用
    # 且应该在导入时检查依赖
```

---

## Hybrid SDLC 流程

每个 Week:
1. **Story Clarity** - 明确验收标准
2. **C-P-A 循环** - Check-Point-Analyze
3. **Dual AI Auditing** - JARVIS 审查（重点模块）
4. **停止等待** - 收到反馈后再继续

---

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 协议设计不完整 | 中 | 高 | 参考 neoclaw C-P-A 接口，保持抽象 |
| 适配器维护负担 | 低 | 中 | 提供基类和测试工具 |
| 性能不达标 | 低 | 中 | 性能基准测试，优化算法 |
| 学习循环不稳定 | 低 | 高 | 安全限制，回滚机制 |

---

## 依赖

### 核心依赖（无）

```toml
[project]
dependencies = []  # 核心零依赖
```

### 可选依赖

```toml
[project.optional-dependencies]
neoclaw = [
    "neoclaw>=2.0.0",
]
openclaw = [
    "openclaw-gateway>=1.0.0",
]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=3.0.0",
    "pytest-benchmark",
]
```

---

## 里程碑

```
Week 8 (4/7-4/13) - Act 层
├── Day 1-2: Parameter Applier
├── Day 3-4: Configuration Manager
├── Day 5: Action Executor
└── Day 5: Dual AI Audit (Lite)

Week 9 (4/14-4/20) - Learn 层
├── Day 1-2: Knowledge Base
├── Day 3-4: Experience Replay
├── Day 5: Self-Improvement
└── Day 5: Dual AI Audit (Lite)

Week 10 (4/21-4/27) - 协议与适配器
├── Day 1-2: 协议层定义
├── Day 3: 通用 C-P-A 循环
├── Day 4: 适配器实现
└── Day 5: 集成测试 + Dual AI Audit (Full)
```

---

## ADR 参考

本计划遵循以下架构决策：

- **ADR-008: Framework Independence Guarantee** - 保持框架独立性
  - 核心模块零外部依赖
  - 通过适配器模式集成外部框架
  - 协议层定义抽象接口

---

**创建日期:** 2026-04-03  
**更新日期:** 2026-04-06  
**状态:** Draft  
**待审核:** ADR-008 + Sprint 3 调整方案
