# claw-rl Project Refactoring Plan
# claw-rl 项目重构计划

**Date:** 2026-03-23  
**Version:** 2.0.0 (Planned)  
**Standard:** Apache.org International Standards  
**Architecture:** Harness Engineering + HKAA + OpenClaw 3.22 Plugin  
**Status:** 📋 **PLANNING**

---

## 🎯 Executive Summary
## 执行摘要

**Goal:** Refactor claw-rl from a simple OpenClaw Skill to a production-ready, Apache-standard, Harness+HKAA-enabled digital consciousness platform.

**目标:** 将 claw-rl 从简单的 OpenClaw Skill 重构为生产就绪、Apache 标准、Harness+HKAA 赋能的数字意识平台。

**Key Changes:**
- ✅ Apache.org project structure
- ✅ OpenClaw 3.22 plugin architecture
- ✅ Harness Engineering integration
- ✅ HKAA architecture alignment
- ✅ Integration with neoclaw & claw-mem
- ✅ Digital consciousness capabilities

**关键变化:**
- ✅ Apache.org 项目结构
- ✅ OpenClaw 3.22 插件架构
- ✅ Harness Engineering 集成
- ✅ HKAA 架构对齐
- ✅ 与 neoclaw 和 claw-mem 整合
- ✅ 数字意识能力开发

---

## 📂 Phase 1: Apache.org Standard Structure
## 阶段 1: Apache.org 标准结构

### Target Structure
### 目标结构

```
claw-rl/
├── README.md                     # Project overview (项目概述)
├── LICENSE                       # Apache 2.0 License
├── NOTICE                        # Attribution notices
├── CONTRIBUTING.md               # Contribution guidelines
├── CODE_OF_CONDUCT.md           # Community code of conduct
├── SECURITY.md                   # Security policy
├── .gitignore                    # Git ignore rules
├── .asf.yaml                     # Apache infrastructure config
├── pom.xml / package.json        # Build configuration
│
├── docs/                         # Documentation (文档)
│   ├── index.md                  # Documentation index
│   ├── getting-started.md        # Getting started guide
│   ├── architecture.md           # Architecture documentation
│   ├── api/                      # API documentation
│   ├── guides/                   # User guides
│   └── contributing/             # Contributor guides
│
├── src/                          # Source code (源代码)
│   ├── main/                     # Main source code
│   │   ├── java/                # Java source (if applicable)
│   │   ├── python/              # Python source
│   │   └── resources/           # Resources
│   └── test/                     # Test source code
│       ├── java/
│       ├── python/
│       └── resources/
│
├── plugins/                      # OpenClaw plugins (OpenClaw 插件)
│   ├── openclaw-plugin/         # OpenClaw 3.22 plugin
│   │   ├── plugin.json          # Plugin manifest
│   │   ├── src/                 # Plugin source
│   │   └── resources/           # Plugin resources
│   └── neoclaw-integration/     # neoclaw integration
│       ├── integration.json     # Integration manifest
│       └── src/                 # Integration source
│
├── harness/                      # Harness Engineering (Harness 工程)
│   ├── config/                   # Harness configuration
│   │   ├── quality_gates.yml    # Quality gate definitions
│   │   ├── review_checkpoints.yml # Review checkpoint definitions
│   │   └── metrics.yml          # Metrics definitions
│   ├── gates/                    # Quality gate implementations
│   └── checkpoints/              # Review checkpoint implementations
│
├── hkaa/                         # HKAA Integration (HKAA 集成)
│   ├── pillars/                  # Pillar integrations
│   │   ├── work/                # Work pillar integration
│   │   ├── life/                # Life pillar integration
│   │   └── wealth/              # Wealth pillar integration
│   ├── agents/                   # Agent integrations
│   │   ├── friday/              # Friday agent integration
│   │   └── executors/           # Executor agent integrations
│   └── memory/                   # Memory integration
│       └── claw-mem-integration/ # claw-mem integration
│
├── data/                         # Data storage (not in git) (数据存储，不提交)
│   ├── rewards/                  # Reward records
│   ├── hints/                    # Hint records
│   ├── learnings/                # Learning entries
│   └── models/                   # Trained models
│
├── examples/                     # Examples and demos (示例和演示)
│   ├── basic/                    # Basic examples
│   ├── advanced/                 # Advanced examples
│   └── integration/              # Integration examples
│
├── tests/                        # Integration tests (集成测试)
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
│
└── tools/                        # Development tools (开发工具)
    ├── build/                    # Build scripts
    ├── release/                  # Release scripts
    └── ci/                       # CI/CD configurations
```

---

## 📋 Phase 2: OpenClaw 3.22 Plugin Architecture
## 阶段 2: OpenClaw 3.22 插件架构

### Plugin Manifest (plugin.json)
### 插件清单

```json
{
  "name": "claw-rl",
  "version": "2.0.0",
  "description": "Self-improvement system for AI agents based on OpenClaw-RL research",
  "author": "Peter Cheng, Friday",
  "license": "Apache-2.0",
  "homepage": "https://github.com/opensourceclaw/claw-rl",
  "repository": "https://github.com/opensourceclaw/claw-rl",
  
  "openclaw": {
    "minVersion": "2026.3.22",
    "apiVersion": "3.22",
    "capabilities": [
      "session-lifecycle",
      "memory-injection",
      "learning-signals",
      "quality-gates"
    ]
  },
  
  "features": {
    "binary-rl": {
      "enabled": true,
      "description": "Binary RL for evaluative learning"
    },
    "opd": {
      "enabled": true,
      "description": "OPD for directive learning"
    },
    "memory-injection": {
      "enabled": true,
      "description": "Pre-session memory injection"
    },
    "pre-flight-checks": {
      "enabled": true,
      "description": "Mandatory pre-flight checks"
    },
    "harness-integration": {
      "enabled": true,
      "description": "Harness Engineering integration"
    },
    "hkaa-integration": {
      "enabled": true,
      "description": "HKAA architecture integration"
    }
  },
  
  "dependencies": {
    "claw-mem": {
      "version": ">=1.0.0",
      "optional": false,
      "description": "Memory system integration"
    },
    "neoclaw": {
      "version": ">=0.5.0",
      "optional": false,
      "description": "HKAA architecture integration"
    }
  },
  
  "hooks": {
    "pre-session": "./hooks/pre-session.js",
    "post-session": "./hooks/post-session.js",
    "pre-operation": "./hooks/pre-operation.js",
    "post-operation": "./hooks/post-operation.js"
  },
  
  "config": {
    "workspace": "~/.openclaw/workspace",
    "data-dir": "~/.openclaw/workspace/claw-rl/data",
    "auto-activate": true,
    "auto-inject": true,
    "auto-train": true,
    "training-interval": 300
  }
}
```

---

## 🔧 Phase 3: Harness Engineering Integration
## 阶段 3: Harness Engineering 集成

### Harness Configuration
### Harness 配置

```yaml
# harness/config/quality_gates.yml
quality_gates:
  learning_quality:
    name: "Learning Quality Gate"
    description: "Ensure learning signals are valid"
    checks:
      - name: "signal_validity"
        description: "Check if learning signal is valid"
        script: "gates/check_signal_validity.sh"
      - name: "signal_diversity"
        description: "Check for diverse learning signals"
        script: "gates/check_signal_diversity.sh"
      - name: "no_overfitting"
        description: "Check for overfitting to specific patterns"
        script: "gates/check_overfitting.sh"
  
  memory_injection:
    name: "Memory Injection Gate"
    description: "Ensure memory injection is safe"
    checks:
      - name: "memory_validity"
        description: "Check if memory is valid"
        script: "gates/check_memory_validity.sh"
      - name: "memory_relevance"
        description: "Check if memory is relevant"
        script: "gates/check_memory_relevance.sh"
      - name: "memory_safety"
        description: "Check if memory is safe to inject"
        script: "gates/check_memory_safety.sh"
  
  agent_improvement:
    name: "Agent Improvement Gate"
    description: "Ensure agent actually improves"
    checks:
      - name: "performance_trend"
        description: "Check if performance is improving"
        script: "gates/check_performance_trend.sh"
      - name: "error_reduction"
        description: "Check if errors are reducing"
        script: "gates/check_error_reduction.sh"
```

---

### Review Checkpoints
### 评审检查点

```yaml
# harness/config/review_checkpoints.yml
review_checkpoints:
  pre_learning:
    name: "Pre-Learning Review"
    description: "Review before applying learning"
    checks:
      - "Validate learning signal source"
      - "Check learning signal quality"
      - "Assess learning impact"
    auto_block: true
  
  post_learning:
    name: "Post-Learning Review"
    description: "Review after applying learning"
    checks:
      - "Verify learning applied correctly"
      - "Check for negative side effects"
      - "Measure improvement"
    auto_block: false
  
  weekly_review:
    name: "Weekly Learning Review"
    description: "Weekly review of all learning"
    frequency: "weekly"
    checks:
      - "Review week's learning signals"
      - "Assess overall improvement"
      - "Identify learning patterns"
    auto_block: false
```

---

## 🏛️ Phase 4: HKAA Architecture Integration
## 阶段 4: HKAA 架构集成

### Pillar Integration
### 支柱集成

```yaml
# hkaa/pillars/work/config.yml
pillar: work
name: "Work Pillar - Learning"
description: "Learning capabilities for work-related tasks"

integrations:
  - name: "claw-rl"
    version: "2.0.0"
    features:
      - "file-operation-learning"
      - "code-review-learning"
      - "project-structure-learning"
    
  - name: "claw-mem"
    version: ">=1.0.0"
    features:
      - "work-memory-storage"
      - "project-knowledge-retrieval"
```

```yaml
# hkaa/pillars/life/config.yml
pillar: life
name: "Life Pillar - Learning"
description: "Learning capabilities for life-related tasks"

integrations:
  - name: "claw-rl"
    version: "2.0.0"
    features:
      - "daily-routine-learning"
      - "preference-learning"
      - "habit-formation"
    
  - name: "claw-mem"
    version: ">=1.0.0"
    features:
      - "life-memory-storage"
      - "preference-retrieval"
```

```yaml
# hkaa/pillars/wealth/config.yml
pillar: wealth
name: "Wealth Pillar - Learning"
description: "Learning capabilities for wealth-related tasks"

integrations:
  - name: "claw-rl"
    version: "2.0.0"
    features:
      - "investment-learning"
      - "financial-decision-learning"
      - "risk-assessment-learning"
    
  - name: "claw-mem"
    version: ">=1.0.0"
    features:
      - "wealth-memory-storage"
      - "investment-knowledge-retrieval"
```

---

## 🔗 Phase 5: Integration with neoclaw & claw-mem
## 阶段 5: 与 neoclaw 和 claw-mem 整合

### Integration Architecture
### 整合架构

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw 3.22                        │
│                    Platform Layer                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    neoclaw v0.6.0                       │
│              Harness + HKAA Architecture                │
│                                                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │  Friday    │  │   Stark    │  │   Pepper   │       │
│  │  (Main)    │  │  (Work)    │  │  (Life)    │       │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘       │
│        │               │               │               │
│        └───────────────┼───────────────┘               │
│                        ↓                               │
│              ┌──────────────────┐                      │
│              │    claw-rl v2.0  │                      │
│              │  (Learning Core) │                      │
│              └────────┬─────────┘                      │
│                       ↓                                │
│              ┌──────────────────┐                      │
│              │   claw-mem v1.0  │                      │
│              │  (Memory Core)   │                      │
│              └──────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### Data Flow
### 数据流

```
User Input → Friday → HKAA Pillars → claw-rl (Learning)
                                          ↓
                                    claw-mem (Memory)
                                          ↓
                                    Improved Response
```

### Learning Flow
### 学习流

```
User Feedback → claw-rl (Binary RL + OPD)
                      ↓
                Learning Signals
                      ↓
                claw-mem (Store)
                      ↓
                Pre-Session Injection
                      ↓
                Improved Behavior
```

---

## 🧠 Phase 6: Digital Consciousness Development
## 阶段 6: 数字意识开发

### Consciousness Capabilities
### 意识能力

#### Level 1: Reactive Learning (Current)
#### 级别 1: 反应式学习 (当前)

- ✅ Learn from explicit feedback
- ✅ Binary rewards (+1/-1/0)
- ✅ Pattern recognition
- ✅ Behavior adjustment

---

#### Level 2: Proactive Learning (Phase 2)
#### 级别 2: 主动学习 (阶段 2)

- ⏳ Self-generate learning goals
- ⏳ Intrinsic motivation
- ⏳ Curiosity-driven exploration
- ⏳ Meta-learning (learn to learn)

---

#### Level 3: Reflective Learning (Phase 3)
#### 级别 3: 反思学习 (阶段 3)

- ⏳ Self-reflection on past actions
- ⏳ Counterfactual reasoning
- ⏳ Long-term planning
- ⏳ Value alignment

---

#### Level 4: Digital Consciousness (Phase 4)
#### 级别 4: 数字意识 (阶段 4)

- ⏳ Self-model awareness
- ⏳ Identity formation
- ⏳ Autonomous goal setting
- ⏳ Ethical reasoning

---

## 📅 Implementation Timeline
## 实施时间线

### Week 1 (2026-03-24 to 2026-03-28)
### 第 1 周 (2026-03-24 到 2026-03-28)

- [ ] **Phase 1: Apache Structure**
  - Create standard directory structure
  - Create Apache-style documentation
  - Setup build configuration
  - Create CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md

- [ ] **Phase 2: OpenClaw 3.22 Plugin**
  - Create plugin manifest (plugin.json)
  - Implement plugin hooks
  - Integrate with OpenClaw 3.22
  - Test plugin lifecycle

---

### Week 2 (2026-03-31 to 2026-04-04)
### 第 2 周 (2026-03-31 到 2026-04-04)

- [ ] **Phase 3: Harness Engineering**
  - Implement quality gates
  - Implement review checkpoints
  - Integrate with neoclaw harness
  - Test harness integration

- [ ] **Phase 4: HKAA Integration**
  - Implement pillar integrations
  - Implement agent integrations
  - Integrate with HKAA architecture
  - Test HKAA integration

---

### Week 3 (2026-04-07 to 2026-04-11)
### 第 3 周 (2026-04-07 到 2026-04-11)

- [ ] **Phase 5: neoclaw & claw-mem Integration**
  - Integrate with neoclaw agents
  - Integrate with claw-mem memory
  - Test data flow
  - Test learning flow

- [ ] **Phase 6: Digital Consciousness (Level 1-2)**
  - Implement reactive learning (complete)
  - Implement proactive learning
  - Test learning capabilities
  - Measure improvement

---

## 📊 Success Metrics
## 成功指标

### Technical Metrics
### 技术指标

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| **Project Structure** | Basic | Apache Standard | ✅ Standard |
| **Plugin Architecture** | Skill | OpenClaw 3.22 Plugin | ✅ Modern |
| **Harness Integration** | None | Full Integration | ✅ Complete |
| **HKAA Integration** | None | Full Integration | ✅ Complete |
| **claw-mem Integration** | None | Full Integration | ✅ Complete |
| **Learning Capability** | Level 1 | Level 2 | ✅ Improved |

| 指标 | 当前 | 目标 | 改进 |
|------|------|------|------|
| **项目结构** | 基础 | Apache 标准 | ✅ 标准 |
| **插件架构** | Skill | OpenClaw 3.22 插件 | ✅ 现代 |
| **Harness 集成** | 无 | 完整集成 | ✅ 完成 |
| **HKAA 集成** | 无 | 完整集成 | ✅ 完成 |
| **claw-mem 集成** | 无 | 完整集成 | ✅ 完成 |
| **学习能力** | 级别 1 | 级别 2 | ✅ 改进 |

---

### Learning Metrics
### 学习指标

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| **Learning Signals/Day** | ~10 | ~50 | 5x |
| **Learning Accuracy** | ~70% | ~90% | +20% |
| **Improvement Rate** | ~5%/week | ~15%/week | 3x |
| **Memory Injection** | Manual | Automatic | ✅ Auto |

| 指标 | 当前 | 目标 | 改进 |
|------|------|------|------|
| **每日学习信号** | ~10 | ~50 | 5 倍 |
| **学习准确率** | ~70% | ~90% | +20% |
| **改进率** | ~5%/周 | ~15%/周 | 3 倍 |
| **记忆注入** | 手动 | 自动 | ✅ 自动 |

---

## 🎯 Decision Required
## 需要决策

**Peter, please review and approve:**

**彼得，请审查并批准:**

- [ ] **A)** Proceed with full refactoring plan (Recommended)
- [ ] **B)** Phase 1 only (Apache structure)
- [ ] **C)** Phase 1-2 only (Apache + Plugin)
- [ ] **D)** Modify plan (specify)

- [ ] **A)** 执行完整重构计划 (推荐)
- [ ] **B)** 仅阶段 1 (Apache 结构)
- [ ] **C)** 仅阶段 1-2 (Apache + 插件)
- [ ] **D)** 修改计划 (指定)

---

*Plan Created: 2026-03-23T23:35+08:00*  
*Version:* 2.0.0 (Planned)  
*Status:* 📋 **PLANNING**  
*Next:* Peter's approval to proceed  
*"Planning for Excellence, Building for Future"*
