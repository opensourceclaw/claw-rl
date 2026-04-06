# ADR-008: Framework Independence Guarantee

## Status

Proposed

## Context

claw-rl 作为 OpenClaw 生态中的自我学习模块，需要保持框架无关性，以支持多种使用场景。

### 问题

1. **耦合风险**：Sprint 3 计划中存在 "neoclaw 框架对接" 的表述，可能导致强耦合
2. **复用性**：其他项目（非 neoclaw）可能需要使用 claw-rl 的学习功能
3. **演进独立**：claw-rl 应该能够独立演进，不依赖特定框架版本
4. **生态定位**：OpenClaw 生态需要可复用的独立模块

### 当前状态

| 方面 | 状态 | 风险 |
|------|------|------|
| 硬依赖 | ✅ 无 | pyproject.toml dependencies = [] |
| 代码导入 | ✅ 无 | 无 `from neoclaw` 或 `import neoclaw` |
| 文档注释 | ⚠️ 有 | agents/signal_collector.py 注释提及 neoclaw |
| Sprint 3 计划 | ⚠️ 风险 | "neoclaw 框架对接" 可能引入耦合 |

## Decision

采用 **适配器模式 (Adapter Pattern)** 保持框架独立性：

### 架构分层

```
┌─────────────────────────────────────────────────────────────┐
│                   OpenClaw 生态                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │    neoclaw      │  │   other-app     │  │  future-app │ │
│  │  (C-P-A Model)  │  │  (自定义框架)    │  │  (新框架)   │ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘ │
│           │                    │                  │        │
│           ▼                    ▼                  ▼        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              claw-rl (独立模块)                       │   │
│  │                                                      │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │    adapters/  (适配器层 - 可选依赖)             │  │   │
│  │  │  - neoclaw_adapter.py                         │  │   │
│  │  │  - openclaw_adapter.py                        │  │   │
│  │  │  - base_adapter.py                            │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  │                       │                             │   │
│  │                       ▼                             │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │    protocols/  (协议层 - 抽象接口)              │  │   │
│  │  │  - observer.py                                │  │   │
│  │  │  - decision_maker.py                          │  │   │
│  │  │  - executor.py                                │  │   │
│  │  │  - signal_adapter.py                          │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  │                       │                             │   │
│  │                       ▼                             │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │    core/  (核心层 - 框架无关)                   │  │   │
│  │  │  - feedback/                                  │  │   │
│  │  │  - learning/                                  │  │   │
│  │  │  - pattern/                                   │  │   │
│  │  │  - cpa_loop.py                                │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 核心协议定义

```python
# claw_rl/protocols/observer.py
from typing import Protocol, Dict, Any

class ObserverProtocol(Protocol):
    """观察者协议 - 收集系统状态和反馈信号"""
    
    def observe(self) -> Dict[str, Any]:
        """
        收集观察数据
        
        Returns:
            Dict containing:
            - metrics: 性能指标
            - feedback: 反馈信号
            - context: 上下文信息
        """
        ...

# claw_rl/protocols/decision_maker.py
class DecisionMakerProtocol(Protocol):
    """决策者协议 - 基于观察做出学习决策"""
    
    def decide(self, observations: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于观察做出决策
        
        Args:
            observations: 来自 Observer 的观察数据
            
        Returns:
            Dict containing:
            - action: 要执行的动作
            - parameters: 动作参数
            - confidence: 决策置信度
        """
        ...

# claw_rl/protocols/executor.py
class ExecutorProtocol(Protocol):
    """执行者协议 - 执行决策并返回结果"""
    
    def execute(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行决策
        
        Args:
            decision: 来自 DecisionMaker 的决策
            
        Returns:
            Dict containing:
            - success: 是否成功
            - result: 执行结果
            - metrics: 执行指标
        """
        ...

# claw_rl/protocols/signal_adapter.py
class SignalAdapterProtocol(Protocol):
    """信号适配器协议 - 将框架特定信号转换为通用格式"""
    
    def adapt(self, raw_signal: Any) -> Dict[str, Any]:
        """
        适配信号格式
        
        Args:
            raw_signal: 框架特定的原始信号
            
        Returns:
            Dict containing:
            - type: 信号类型
            - source: 信号来源
            - payload: 标准化负载
            - timestamp: 时间戳
        """
        ...
```

### 目录结构

```
src/claw_rl/
├── protocols/              # 新增：协议层
│   ├── __init__.py
│   ├── observer.py
│   ├── decision_maker.py
│   ├── executor.py
│   └── signal_adapter.py
│
├── adapters/               # 新增：适配器层
│   ├── __init__.py
│   ├── base_adapter.py     # 基础适配器
│   ├── neoclaw_adapter.py  # NeoClaw 适配器
│   └── openclaw_adapter.py # OpenClaw Gateway 适配器
│
├── core/                   # 核心（现有模块重组）
│   ├── feedback/           # Sprint 2
│   ├── learning/           # Sprint 2, 3
│   ├── pattern/            # Sprint 1
│   └── cpa_loop.py         # Sprint 3: 通用 C-P-A 循环
│
├── agents/                 # 保留但重构
│   └── signal_collector.py # 移除 neoclaw 特定字段
│
└── __init__.py
```

### 可选依赖

```toml
# pyproject.toml

[project]
dependencies = []  # 核心零依赖

[project.optional-dependencies]
neoclaw = [
    "neoclaw>=2.0.0",
]
openclaw = [
    "openclaw-gateway>=1.0.0",
]
all = [
    "claw-rl[neoclaw,openclaw]",
]
```

## Consequences

### 正面影响

1. **独立性**：claw-rl 可独立使用，无需任何框架依赖
2. **可扩展**：新框架只需实现适配器接口即可接入
3. **可维护**：核心代码变更不影响适配器，反之亦然
4. **可测试**：核心逻辑可独立测试，适配器可模拟测试

### 负面影响

1. **复杂度增加**：多了一层抽象
2. **代码量增加**：需要维护协议和适配器
3. **集成成本**：新框架需要实现适配器

### 风险缓解

| 风险 | 缓解措施 |
|------|----------|
| 适配器维护负担 | 提供基类和测试工具简化适配器开发 |
| 协议变更影响 | 协议版本化，保持向后兼容 |
| 文档复杂度 | 提供清晰的集成指南和示例 |

## Implementation Plan

### Sprint 3 调整

**原计划：**
```
Week 10: C-P-A Integration
- neoclaw 框架对接
```

**调整后：**
```
Week 10: C-P-A Integration
- 定义核心协议 (protocols/)
- 实现通用 C-P-A 循环 (core/cpa_loop.py)
- 实现 neoclaw 适配器 (adapters/neoclaw_adapter.py)
- 实现基础适配器 (adapters/base_adapter.py)
- 集成测试验证独立性
```

### 迁移步骤

1. **Week 8-9**：Act/Learn 层实现（保持框架无关）
2. **Week 10 Day 1-2**：定义协议层 (`protocols/`)
3. **Week 10 Day 3**：实现通用 C-P-A 循环 (`core/cpa_loop.py`)
4. **Week 10 Day 4**：实现适配器层 (`adapters/`)
5. **Week 10 Day 5**：集成测试 + JARVIS 审查

## Decision Makers

- **Proposer**: Friday (Main Agent)
- **Reviewer**: JARVIS (Adversary Agent)
- **Approver**: Peter (Captain America)

## References

- [ADR-007: Versioning Strategy](./ADR-007-versioning-strategy.md)
- [Hybrid SDLC Guide](/Users/liantian/workspace/osprojects/neoclaw/docs/v2.0.0/architecture/HYBRID_SDLC_GUIDE.md)
- [Sprint 3 Plan](./SPRINT3_PLAN.md)

---

**Created**: 2026-04-06
**Last Updated**: 2026-04-06
