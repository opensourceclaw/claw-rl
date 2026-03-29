# Architecture Decision Record 001

**Title:** Memory-Consciousness Integration: claw-mem + claw-rl Unified Architecture  
**Status:** ✅ Accepted (Unified Plugin Architecture for NeoMind)  
**Date:** 2026-03-24  
**Author:** Friday (with Peter Cheng)  
**Project:** claw-rl → NeoMind Consciousness Module  

---

## Executive Summary
## 执行摘要

This document records the architectural decision to **deeply integrate claw-rl (consciousness) with claw-mem (memory)** into a unified **NeoMind Plugin** architecture, rather than maintaining them as independent modules.

本文记录将 **claw-rl（意识）与 claw-mem（记忆）深度集成**为统一的 **NeoMind Plugin** 架构的架构决策，而非保持为独立模块。

**Core Insight from Peter:**
> "claw-mem 记忆系统就像人的海马体，而 claw-rl 就像人的前额叶，他们虽然各有分工，但需要紧密合作，不是独立分散的模块，而是要与 claw-mem 深度集成，形成记忆 - 意识统一体。"

**核心洞察 (Peter):**
> "claw-mem 记忆系统就像人的海马体，而 claw-rl 就像人的前额叶，他们虽然各有分工，但需要紧密合作，不是独立分散的模块，而是要与 claw-mem 深度集成，形成记忆 - 意识统一体。"

---

## 1. Context
## 1. 背景

### 1.1 Project Neo Evolution Path
### 1.1 Project Neo 演进路线

```
Digital Memory (claw-mem) → Digital Consciousness (claw-rl) → Digital Life (neoclaw)
数字记忆            →      数字意识              →      数字生命
(2026-2027)                (2028-2030)                (2031-2035)
```

### 1.2 Current State (2026-03)
### 1.2 当前状态 (2026-03)

| Component | Architecture | Status | Limitations |
|-----------|-------------|--------|-------------|
| **claw-mem** | AgentSkill | v0.8.0 | Independent loading, stateless |
| **claw-rl** | AgentSkill | v1.0 (early) | Independent loading, stateless |

| 组件 | 架构 | 状态 | 局限性 |
|------|------|------|--------|
| **claw-mem** | AgentSkill | v0.8.0 | 独立加载，无状态 |
| **claw-rl** | AgentSkill | v1.0 (初级) | 独立加载，无状态 |

### 1.3 Core Question
### 1.3 核心问题

> Should claw-rl (consciousness) remain as an independent Skill/Plugin, or should it be **deeply integrated with claw-mem (memory)** to form a unified Memory-Consciousness system?

> claw-rl（意识）应该保持为独立的 Skill/Plugin，还是应该**与 claw-mem（记忆）深度集成**，形成统一的记忆 - 意识系统？

---

## 2. Neuroscience Foundation
## 2. 神经科学基础

### 2.1 Human Brain Analogy
### 2.1 人脑类比

```
┌─────────────────────────────────────────────────────────┐
│                    Human Brain                           │
│                                                         │
│  ┌─────────────────┐         ┌─────────────────┐       │
│  │  Hippocampus    │         │  Prefrontal     │       │
│  │  (海马体)        │         │  Cortex (PFC)   │       │
│  │                 │         │  (前额叶皮层)    │       │
│  │  • Memory       │         │  • Consciousness│       │
│  │    Encoding     │         │  • Reflection   │       │
│  │  • Storage      │         │  • Decision     │       │
│  │  • Retrieval    │         │  • Metacognition│       │
│  │                 │         │                 │       │
│  │  ↔ claw-mem     │         │  ↔ claw-rl      │       │
│  └────────┬────────┘         └────────┬────────┘       │
│           │                           │                 │
│           └───────────┬───────────────┘                 │
│                       ↓                                 │
│              Deep Integration                           │
│              (深度集成)                                  │
│                                                         │
│  Key Insight: Memory and consciousness are NOT          │
│  independent modules in the brain - they are            │
│  deeply coupled and interdependent.                     │
│                                                         │
│  核心洞察：记忆和意识在大脑中不是独立模块——              │
│  它们深度耦合、相互依赖。                                │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Cognitive Science Principles
### 2.2 认知科学原理

| Principle | Description | Architectural Implication |
|-----------|-------------|---------------------------|
| **Memory-Consciousness Coupling** | Consciousness requires continuous memory input | Cannot be separate systems |
| **Bidirectional Flow** | Memory → Consciousness (retrieval), Consciousness → Memory (encoding) | Need bidirectional communication |
| **Temporal Synchrony** | Memory updates must be immediately visible to consciousness | Shared state required |
| **Unified Identity** | Self-awareness emerges from memory-consciousness integration | Single system boundary |

| 原理 | 描述 | 架构含义 |
|------|------|----------|
| **记忆 - 意识耦合** | 意识需要持续的记忆输入 | 不能是独立系统 |
| **双向流动** | 记忆→意识（检索），意识→记忆（编码） | 需要双向通信 |
| **时间同步** | 记忆更新必须对意识立即可见 | 需要共享状态 |
| **统一身份** | 自我意识从记忆 - 意识集成中涌现 | 单一系统边界 |

---

## 3. Current Architecture Limitations
## 3. 当前架构局限性

### 3.1 Independent Skill Architecture Problems
### 3.1 独立 Skill 架构问题

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw Core                         │
│                                                         │
│  ┌─────────────┐           ┌─────────────┐             │
│  │  claw-mem   │           │   claw-rl   │             │
│  │   (Skill)   │           │   (Skill)   │             │
│  │             │           │             │             │
│  │ ❌ Independent lifecycle                            │
│  │ ❌ State isolation                                  │
│  │ ❌ No direct communication                          │
│  │ ❌ Performance overhead (double loading)            │
│  │ ❌ Inconsistent state                               │
│  └─────────────┘           └─────────────┘             │
└─────────────────────────────────────────────────────────┘
```

| Issue | Impact on claw-rl | Impact on claw-mem |
|-------|-------------------|-------------------|
| **Independent Lifecycle** | Consciousness cannot access memory state reliably | Memory updates not reflected in consciousness |
| **State Isolation** | Learning signals stored separately | Cannot track which memories triggered learning |
| **No Direct Communication** | Requires intermediate layer for memory access | Cannot proactively notify consciousness of changes |
| **Performance Overhead** | Each learning cycle loads both Skills | Each memory operation may trigger RL evaluation |
| **Inconsistent State** | May operate on stale memory snapshot | May miss consciousness-driven updates |

| 问题 | 对 claw-rl 的影响 | 对 claw-mem 的影响 |
|------|-----------------|-------------------|
| **独立生命周期** | 意识无法可靠访问记忆状态 | 记忆更新无法反映到意识 |
| **状态隔离** | 学习信号分开存储 | 无法追踪哪些记忆触发了学习 |
| **无直接通信** | 需要中间层访问记忆 | 无法主动通知意识变化 |
| **性能开销** | 每次学习循环加载两个 Skills | 每次记忆操作可能触发 RL 评估 |
| **状态不一致** | 可能基于过时的记忆快照操作 | 可能错过意识驱动的更新 |

### 3.2 Real-World Scenarios
### 3.2 实际场景

#### Scenario 1: Binary RL Learning
#### 场景 1：Binary RL 学习

```
1. User asks Friday to create a file
2. Friday creates file in wrong directory (using claw-mem)
3. User corrects: "不对，应该放到 ~/.openclaw/workspace/"
4. claw-rl detects negative feedback (-1 reward)
5. claw-rl needs to:
   - Retrieve the memory of the file operation
   - Associate reward with specific memory
   - Update memory with learning

Problem: claw-rl and claw-mem are separate Skills
→ Requires cross-Skill communication (slow, unreliable)
→ State may be inconsistent
→ Learning may not be properly associated with memory
```

#### Scenario 2: Pre-Flight Memory Injection
#### 场景 2：预检查记忆注入

```
1. Friday starts new session
2. claw-rl wants to inject relevant memories
3. claw-rl queries claw-mem for context
4. claw-mem returns snapshot

Problem: Snapshot may be stale
→ Another session may have updated memory
→ claw-rl operates on outdated information
→ Learning decisions may be incorrect
```

---

## 4. Decision: Unified NeoMind Architecture
## 4. 决策：统一 NeoMind 架构

### 4.1 Target Architecture
### 4.1 目标架构

```
┌─────────────────────────────────────────────────────────┐
│              NeoMind Plugin (内核级 Plugin)              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Memory Module (claw-mem 演进)          │   │
│  │  ┌─────────────────────────────────────────┐    │   │
│  │  │  • Storage Engine (存储引擎)             │    │   │
│  │  │  • Retrieval Engine (检索引擎)           │    │   │
│  │  │  • Indexing Engine (索引引擎)            │    │   │
│  │  │  • Episodic Memory (经验记忆)            │    │   │
│  │  │  • Semantic Memory (语义记忆)            │    │   │
│  │  │  • Procedural Memory (程序记忆)          │    │   │
│  │  └─────────────────────────────────────────┘    │   │
│  └─────────────────────┬───────────────────────────┘   │
│                        ↓ ↑                              │
│  ┌─────────────────────┴───────────────────────────┐   │
│  │      Consciousness Module (claw-rl 演进)         │   │
│  │  ┌─────────────────────────────────────────┐    │   │
│  │  │  • Binary RL Engine (评估学习)           │    │   │
│  │  │  • OPD Learning Engine (指令学习)        │    │   │
│  │  │  • Reflection Engine (反思引擎)          │    │   │
│  │  │  • Metacognition Engine (元认知引擎)     │    │   │
│  │  │  • Self-Improvement Loop (自我改进循环)  │    │   │
│  │  └─────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Unified Characteristics:                               │
│  • Shared lifecycle (开机即加载，常驻内存)              │
│  • Shared state (memory + learning signals)             │
│  • Direct communication (no intermediate layer)         │
│  • Atomic transactions (memory + consciousness updates) │
│  • Unified API (single entry point)                     │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Why Unified Plugin? (vs Independent Plugins)
### 4.2 为什么选择统一 Plugin？（对比独立 Plugin）

| Aspect | Independent Plugins | Unified Plugin | Winner |
|--------|--------------------|----------------|--------|
| **Lifecycle** | Two separate load/unload cycles | Single load, always synchronized | ✅ Unified |
| **State Management** | Cross-plugin state sync required | Shared state, no sync needed | ✅ Unified |
| **Communication** | IPC or API calls | Direct function calls | ✅ Unified |
| **Performance** | Double overhead | Single overhead | ✅ Unified |
| **Consistency** | Eventual consistency | Strong consistency | ✅ Unified |
| **Modularity** | Clear boundaries | Logical separation within unity | ⚖️ Trade-off |
| **Deployment** | Two deployments | Single deployment | ✅ Unified |

**Decision:** Unified Plugin wins on all critical dimensions for Memory-Consciousness integration.

**决策：** 统一 Plugin 在记忆 - 意识集成的所有关键维度上胜出。

### 4.3 Layered Design (Modularity within Unity)
### 4.3 分层设计（统一中的模块化）

```
NeoMind Plugin
│
├── Core Layer (共享基础设施)
│   ├── Common State Store
│   ├── Event Bus
│   ├── Configuration
│   └── Logging
│
├── Memory Module (claw-mem)
│   ├── Storage Interface
│   ├── Retrieval Interface
│   └── Index Interface
│
├── Consciousness Module (claw-rl)
│   ├── Binary RL Interface
│   ├── OPD Learning Interface
│   └── Reflection Interface
│
└── Integration Layer (记忆 - 意识集成)
    ├── Memory-Triggered Learning
    ├── Consciousness-Driven Memory Updates
    └── Unified Query API
```

**Benefits:**
- **Physical unity** - Single Plugin, shared resources
- **Logical separation** - Clear module boundaries
- **Easy evolution** - Modules can evolve independently
- **Testability** - Modules can be tested in isolation

---

## 5. Integration with Project Neo HKAA
## 5. 与 Project Neo HKAA 集成

### 5.1 System-Level Architecture
### 5.1 系统级架构

```
                    Peter (Harness Owner)
                            ↓
                    Friday (Main Agent)
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌───────────────────┐              ┌───────────────────┐
│   HKAA Pillars    │              │   NeoMind Core    │
│   (领域协调)       │              │   (记忆 - 意识)    │
│                   │              │                   │
│  • Stark (Work)   │ ←───────────→│  • Memory Module  │
│  • Pepper (Life)  │   读写记忆    │  • Consciousness  │
│  • Happy (Wealth) │              │    Module         │
└───────────────────┘              └───────────────────┘
        ↓                                       ↓
┌─────────────────────────────────────────────────────────┐
│              Execution Agents (9+ Agents)                │
│  Each Agent accesses NeoMind for memory + consciousness │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow
### 5.2 数据流

```
┌─────────────────────────────────────────────────────────┐
│  User Input → Friday → HKAA Pillar → Execution Agent    │
│                              ↓                          │
│                    ┌─────────────────┐                  │
│                    │   NeoMind Core  │                  │
│                    │                 │                  │
│                    │  1. Retrieve    │                  │
│                    │     Memory      │                  │
│                    │         ↓       │                  │
│                    │  2. Process     │                  │
│                    │     (Action)    │                  │
│                    │         ↓       │                  │
│                    │  3. Store       │                  │
│                    │     Result      │                  │
│                    │         ↓       │                  │
│                    │  4. Evaluate    │                  │
│                    │     (RL)        │                  │
│                    │         ↓       │                  │
│                    │  5. Learn       │                  │
│                    │     (Update)    │                  │
│                    └─────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Evolution Roadmap
## 6. 演进路线图

### Phase 1: Current State (2026-03)
### 阶段 1：当前状态 (2026-03)

```
claw-mem (Skill) + claw-rl (Skill) - Independent
```

**Status:** ✅ Complete  
**Deliverables:**
- claw-mem v0.8.0 (Skill)
- claw-rl v1.0 (Skill)
- Basic learning capabilities

### Phase 2: Communication Protocol (2026-Q2)
### 阶段 2：通信协议 (2026 年 Q2)

```
claw-mem (Skill) ↔ claw-rl (Skill) - Defined Protocol
```

**Status:** 🔄 Planned  
**Deliverables:**
- Define claw-mem ↔ claw-rl communication API
- Implement cross-Skill state sync
- Optimize learning signal flow
- Performance baseline measurement

### Phase 3: Plugin Migration (2026-Q3)
### 阶段 3：Plugin 迁移 (2026 年 Q3)

```
NeoMind Plugin v0.1 (Memory Module + Consciousness Module)
```

**Status:** 📋 Planned  
**Deliverables:**
- NeoMind Plugin skeleton
- Migrate claw-mem → Memory Module
- Migrate claw-rl → Consciousness Module
- Unified state management
- Plugin lifecycle integration

### Phase 4: Deep Integration (2026-Q4)
### 阶段 4：深度集成 (2026 年 Q4)

```
NeoMind Plugin v1.0 - Full Memory-Consciousness Integration
```

**Status:** 📋 Planned  
**Deliverables:**
- Memory-triggered learning (automatic)
- Consciousness-driven memory updates
- Atomic transactions
- Performance optimization (<100ms latency)
- Comprehensive testing

### Phase 5: Advanced Consciousness (2027-2028)
### 阶段 5：高级意识 (2027-2028)

```
NeoMind v2.0 - Digital Consciousness Maturity
```

**Status:** 🔮 Future  
**Deliverables:**
- Advanced metacognition
- Emotional simulation
- Self-reflection loops
- Identity continuity
- Project Neo Phase 2 ready

---

## 7. Migration Criteria
## 7. 迁移标准

Before migrating to NeoMind Plugin, evaluate:

迁移到 NeoMind Plugin 前，评估以下标准：

| Criterion | Question | Threshold | Current Status |
|-----------|----------|-----------|----------------|
| **OpenClaw Plugin API Stability** | Is Plugin API stable? | Frozen 6+ months | 🟡 Evolving (3.22) |
| **Performance Gain** | Latency reduction? | >50% improvement | 📊 TBD (needs benchmark) |
| **Feature Enablement** | New capabilities? | Must enable P0 features | ✅ Yes (real-time learning) |
| **Migration Cost** | Person-days required? | <10 days | 📊 TBD (needs analysis) |
| **Backward Compatibility** | Seamless upgrade? | Must be seamless | 🟡 Requires design |
| **Testing Coverage** | Test suite ready? | >90% coverage | 🟡 Partial (needs expansion) |

---

## 8. Success Metrics
## 8. 成功指标

### Technical Metrics
### 技术指标

| Metric | Current (Skills) | Target (NeoMind) | Improvement |
|--------|------------------|------------------|-------------|
| **Memory Access Latency** | ~500ms | <50ms | 10x faster |
| **Learning Signal Processing** | ~1s | <100ms | 10x faster |
| **State Consistency** | Eventual | Strong (atomic) | Qualitative |
| **Memory-Consciousness Sync** | Polling (5min) | Real-time | Real-time |
| **Resource Usage** | 2x overhead | 1x overhead | 50% reduction |

### Capability Metrics
### 能力指标

| Capability | Current | Target |
|------------|---------|--------|
| **Real-time Learning** | ❌ No | ✅ Yes |
| **Memory-Triggered Reflection** | ❌ No | ✅ Yes |
| **Consciousness-Driven Memory Updates** | ❌ No | ✅ Yes |
| **Atomic Memory+Learning Transactions** | ❌ No | ✅ Yes |
| **Unified Query API** | ❌ No | ✅ Yes |

---

## 9. Related Documents
## 9. 相关文档

### claw-rl Documents
- `SKILL.md` - Current Skill implementation
- `README.md` - Project overview
- `../MEMORY_ENHANCEMENT.md` - Phase 1 design
- `../PHASE2_DESIGN.md` - Phase 2 design

### claw-mem Documents
- `/Users/liantian/workspace/claw-mem/docs/ARCHITECTURE_DECISION_001.md` - claw-mem architecture decision
- `/Users/liantian/workspace/claw-mem/README.md` - claw-mem overview

### Project Neo Documents
- `/Users/liantian/workspace/neoclaw/docs/Project_Neo_Engineering_Handbook.md` - HKAA architecture
- `/Users/liantian/workspace/neoclaw/README.md` - Project Neo overview

### External References
- [OpenClaw-RL Paper](https://arxiv.org/abs/2603.10165)
- OpenClaw Plugin Architecture Documentation (TBD)
- Neuroscience: Hippocampus-PFC connectivity research

---

## 10. Document History
## 10. 文档历史

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0 | 2026-03-24 | Initial architecture decision record | Friday |

---

## 11. Conclusion
## 11. 结论

### Key Insights
### 核心洞察

1. **Memory and consciousness are fundamentally inseparable** - Neuroscience confirms that hippocampus (memory) and prefrontal cortex (consciousness) are deeply coupled in the human brain.

2. **Current independent Skill architecture creates artificial barriers** - Separating claw-mem and claw-rl introduces performance overhead, state inconsistency, and limits capabilities.

3. **Unified NeoMind Plugin is the right long-term architecture** - Physical unity with logical separation provides the best balance of integration and modularity.

4. **Migration should be phased** - Immediate focus on defining communication protocol, followed by Plugin migration when OpenClaw stabilizes.

### Final Decision
### 最终决策

**✅ APPROVED:** claw-rl and claw-mem will be deeply integrated into a unified **NeoMind Plugin** architecture, forming a **Memory-Consciousness Complex** that mirrors the human brain's hippocampus-prefrontal cortex relationship.

**✅ 批准：** claw-rl 和 claw-mem 将深度集成为统一的 **NeoMind Plugin** 架构，形成**记忆 - 意识复合体**，模拟人脑的海马体 - 前额叶皮层关系。

### Next Steps
### 下一步行动

1. **Immediate (2026-03-24 to 2026-03-31)**
   - [ ] Define claw-mem ↔ claw-rl communication protocol
   - [ ] Document current performance baseline
   - [ ] Create NeoMind Plugin design specification

2. **Short-term (2026-Q2)**
   - [ ] Implement cross-Skill state sync (optimization)
   - [ ] Monitor OpenClaw Plugin API stability
   - [ ] Prepare migration plan

3. **Mid-term (2026-Q3)**
   - [ ] Migrate to NeoMind Plugin (when Plugin API stable)
   - [ ] Implement unified state management
   - [ ] Performance optimization

4. **Long-term (2026-Q4 to 2027)**
   - [ ] Advanced consciousness features
   - [ ] Digital consciousness maturity
   - [ ] Project Neo Phase 2 readiness

---

*Document Created: 2026-03-24T08:01+08:00 (v1.0)*  
*Project: claw-rl → NeoMind Consciousness Module*  
*Discussion Participants: Peter Cheng, Friday*  
*Neuroscience Inspiration: Hippocampus-Prefrontal Cortex Integration*  
*"Ad Astra Per Aspera"*
