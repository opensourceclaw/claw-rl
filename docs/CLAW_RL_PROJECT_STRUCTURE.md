# claw-rl Project Structure & Activation Analysis
# claw-rl 项目结构与激活机制分析

**Date:** 2026-03-23  
**Version:** 1.0.0  
**Type:** OpenClaw Skill

---

## 🎯 Executive Summary
## 执行摘要

**claw-rl** is currently implemented as an **OpenClaw Skill** (not a plugin), requiring manual activation via `activate.sh`.

**claw-rl** 目前实现为 **OpenClaw Skill** (非插件)，需要通过 `activate.sh` 手动激活。

**Key Findings:**
- ✅ **Project Type:** OpenClaw Skill (bash scripts)
- ✅ **Location:** `~/.openclaw/workspace/skills/claw-rl/`
- ✅ **Source Code:** Bash scripts in `scripts/` directory
- ⚠️ **Activation:** Manual (requires running `./scripts/activate.sh`)
- ⚠️ **Reason:** Designed as optional skill, not core feature

**关键发现:**
- ✅ **项目类型:** OpenClaw Skill (bash 脚本)
- ✅ **位置:** `~/.openclaw/workspace/skills/claw-rl/`
- ✅ **源代码:** `scripts/` 目录中的 bash 脚本
- ⚠️ **激活:** 手动 (需要运行 `./scripts/activate.sh`)
- ⚠️ **原因:** 设计为可选技能，非核心功能

---

## 📂 Project Directory Structure
## 项目目录结构

### Full Structure
### 完整结构

```
~/.openclaw/workspace/skills/claw-rl/
├── SKILL.md                      # OpenClaw skill definition (技能定义)
├── package.json                  # Package configuration (包配置)
├── README.md                     # User documentation (用户文档)
├── scripts/                      # Core scripts (核心脚本)
│   ├── activate.sh              # ⚠️ Manual activation script (手动激活脚本)
│   ├── session_hook.sh          # Session lifecycle hook (会话生命周期钩子)
│   ├── memory_retrieval.sh      # Memory retrieval & injection (记忆检索注入)
│   ├── pre_flight_check.sh      # Pre-flight checks (预检查)
│   ├── prm_judge.sh             # PRM reward judgment (PRM 奖励判断)
│   ├── reward_collector.sh      # Reward collection (奖励收集)
│   ├── hint_extractor.sh        # Hint extraction from feedback (反馈提示提取)
│   ├── training_loop.sh         # Background training loop (后台训练循环)
│   ├── test_all.sh              # Comprehensive testing (综合测试)
│   ├── install.sh               # Installation script (安装脚本)
│   ├── .hints/                  # Hint storage directory (提示存储目录)
│   └── .rewards/                # Reward storage directory (奖励存储目录)
└── (Documentation in parent dir)
    └── ~/.openclaw/workspace/claw-rl/
        ├── FRIDAY_CONSTITUTION.md    # Friday Constitution (Friday 宪法)
        ├── MEMORY_ENHANCEMENT.md     # Phase 1 design (Phase 1 设计)
        ├── PHASE2_DESIGN.md          # Phase 2 design (Phase 2 设计)
        ├── PHASE2_README.md          # Phase 2 README (Phase 2 说明)
        ├── README.md                 # Project README (项目说明)
        └── discussion.md             # Design discussion (设计讨论)
```

---

## 📍 Location Summary
## 位置总结

| Component | Location | Type |
|-----------|----------|------|
| **Skill Package** | `~/.openclaw/workspace/skills/claw-rl/` | OpenClaw Skill |
| **Source Code** | `~/.openclaw/workspace/skills/claw-rl/scripts/` | Bash Scripts |
| **Documentation** | `~/.openclaw/workspace/claw-rl/` | Markdown Docs |
| **Data Storage** | `~/.openclaw/workspace/skills/claw-rl/scripts/.rewards/` | Reward Data |
| **Hint Storage** | `~/.openclaw/workspace/skills/claw-rl/scripts/.hints/` | Hint Data |

| 组件 | 位置 | 类型 |
|------|------|------|
| **技能包** | `~/.openclaw/workspace/skills/claw-rl/` | OpenClaw Skill |
| **源代码** | `~/.openclaw/workspace/skills/claw-rl/scripts/` | Bash 脚本 |
| **文档** | `~/.openclaw/workspace/claw-rl/` | Markdown 文档 |
| **数据存储** | `~/.openclaw/workspace/skills/claw-rl/scripts/.rewards/` | 奖励数据 |
| **提示存储** | `~/.openclaw/workspace/skills/claw-rl/scripts/.hints/` | 提示数据 |

---

## 🔧 Why Manual Activation?
## 为什么需要手动激活？

### Design Reason
### 设计原因

**claw-rl is designed as an OPTIONAL skill, not a core feature.**

**claw-rl 设计为可选技能，非核心功能。**

**Reasons:**
1. **Opt-in Learning** - Users choose whether to enable learning
2. **Privacy** - Learning from conversations is optional
3. **Performance** - Background training has resource cost
4. **Flexibility** - Can be enabled/disabled as needed

**原因:**
1. **自愿学习** - 用户选择是否启用学习
2. **隐私** - 从对话中学习是可选的
3. **性能** - 后台训练有资源成本
4. **灵活性** - 可按需启用/禁用

---

### Current Activation Mechanism
### 当前激活机制

**How it works:**
```bash
# User manually runs activation script
cd ~/.openclaw/workspace/skills/claw-rl
./scripts/activate.sh

# Script does:
# 1. Injects Friday Constitution
# 2. Checks workspace configuration
# 3. Injects today's learning hints
# 4. Shows reward statistics
# 5. Starts background training loop (if not running)
```

**工作方式:**
```bash
# 用户手动运行激活脚本
cd ~/.openclaw/workspace/skills/claw-rl
./scripts/activate.sh

# 脚本执行:
# 1. 注入 Friday 宪法
# 2. 检查工作目录配置
# 3. 注入今日学习提示
# 4. 显示奖励统计
# 5. 启动后台训练循环 (如果未运行)
```

---

### SKILL.md Configuration
### SKILL.md 配置

**Current Configuration:**
```yaml
name: claw-rl
description: OpenClaw-RL 自我改进核心系统
metadata:
  clawdbot:
    emoji: 🧠
    requires:
      bins: ["bash"]
    primaryEnv: "CLAWRL_ENABLED"
```

**Key Setting:**
- `primaryEnv: "CLAWRL_ENABLED"` - Requires environment variable to be set

**关键设置:**
- `primaryEnv: "CLAWRL_ENABLED"` - 需要设置环境变量

---

## 🔄 How to Make it Automatic?
## 如何改为自动激活？

### Option A: Set Environment Variable (Recommended)
### 选项 A: 设置环境变量 (推荐)

**Add to shell profile:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export CLAWRL_ENABLED=1
```

**Benefits:**
- ✅ Automatic activation on shell startup
- ✅ No manual script running needed
- ✅ Simple to implement

**Drawbacks:**
- ⚠️ Only affects new shell sessions
- ⚠️ Doesn't integrate with OpenClaw sessions

**添加到 shell 配置文件:**
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export CLAWRL_ENABLED=1
```

**优点:**
- ✅ Shell 启动时自动激活
- ✅ 无需手动运行脚本
- ✅ 实现简单

**缺点:**
- ⚠️ 仅影响新 shell 会话
- ⚠️ 不与 OpenClaw 会话集成

---

### Option B: Integrate with OpenClaw Session Hook
### 选项 B: 与 OpenClaw 会话钩子集成

**Modify `session_hook.sh`:**
```bash
#!/bin/bash
# ~/.openclaw/workspace/skills/claw-rl/scripts/session_hook.sh

# This hook is called before each OpenClaw session
# Automatically inject claw-rl context

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Always inject memory (no manual activation needed)
"$SCRIPT_DIR/memory_retrieval.sh" auto file

# Always start training loop (if not running)
if ! pgrep -f "training_loop.sh daemon" > /dev/null 2>&1; then
    nohup "$SCRIPT_DIR/training_loop.sh" daemon 300 > /tmp/clawrl_training.log 2>&1 &
fi
```

**Benefits:**
- ✅ Automatic for every OpenClaw session
- ✅ Integrated with OpenClaw lifecycle
- ✅ No user action needed

**Drawbacks:**
- ⚠️ Requires OpenClaw hook support
- ⚠️ May need OpenClaw configuration changes

**修改 `session_hook.sh`:**
```bash
#!/bin/bash
# ~/.openclaw/workspace/skills/claw-rl/scripts/session_hook.sh

# 此钩子在每次 OpenClaw 会话前调用
# 自动注入 claw-rl 上下文

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 总是注入记忆 (无需手动激活)
"$SCRIPT_DIR/memory_retrieval.sh" auto file

# 总是启动训练循环 (如果未运行)
if ! pgrep -f "training_loop.sh daemon" > /dev/null 2>&1; then
    nohup "$SCRIPT_DIR/training_loop.sh" daemon 300 > /tmp/clawrl_training.log 2>&1 &
fi
```

**优点:**
- ✅ 每次 OpenClaw 会话自动激活
- ✅ 与 OpenClaw 生命周期集成
- ✅ 无需用户操作

**缺点:**
- ⚠️ 需要 OpenClaw 钩子支持
- ⚠️ 可能需要 OpenClaw 配置更改

---

### Option C: Convert to Auto-Load Plugin
### 选项 C: 转换为自动加载插件

**Create auto-load configuration:**
```json
// ~/.openclaw/config.json
{
  "skills": {
    "claw-rl": {
      "enabled": true,
      "autoActivate": true,
      "config": {
        "workspace": "~/.openclaw/workspace",
        "auto_inject": true,
        "auto_train": true
      }
    }
  }
}
```

**Benefits:**
- ✅ Proper OpenClaw integration
- ✅ Configurable via config file
- ✅ Follows OpenClaw patterns

**Drawbacks:**
- ⚠️ Requires OpenClaw skill system support
- ⚠️ May need skill system enhancement

**创建自动加载配置:**
```json
// ~/.openclaw/config.json
{
  "skills": {
    "claw-rl": {
      "enabled": true,
      "autoActivate": true,
      "config": {
        "workspace": "~/.openclaw/workspace",
        "auto_inject": true,
        "auto_train": true
      }
    }
  }
}
```

**优点:**
- ✅ 正确的 OpenClaw 集成
- ✅ 通过配置文件可配置
- ✅ 遵循 OpenClaw 模式

**缺点:**
- ⚠️ 需要 OpenClaw 技能系统支持
- ⚠️ 可能需要技能系统增强

---

## 📊 Comparison: Current vs. Automatic
## 对比：当前 vs. 自动

| Aspect | Current (Manual) | Option A (Env Var) | Option B (Hook) | Option C (Plugin) |
|--------|-----------------|-------------------|-----------------|-------------------|
| **Activation** | Manual script | Auto (shell) | Auto (session) | Auto (config) |
| **Integration** | None | Low | Medium | High |
| **Complexity** | Low | Low | Medium | High |
| **Flexibility** | High | Medium | Medium | High |
| **Recommended** | ⚠️ Current | ✅ Quick fix | ⚠️ Needs hooks | ✅ Best long-term |

| 方面 | 当前 (手动) | 选项 A (环境变量) | 选项 B (钩子) | 选项 C (插件) |
|------|-----------|-----------------|-------------|-------------|
| **激活** | 手动脚本 | 自动 (shell) | 自动 (会话) | 自动 (配置) |
| **集成** | 无 | 低 | 中 | 高 |
| **复杂度** | 低 | 低 | 中 | 高 |
| **灵活性** | 高 | 中 | 中 | 高 |
| **推荐** | ⚠️ 当前 | ✅ 快速修复 | ⚠️ 需要钩子 | ✅ 最佳长期 |

---

## 🎯 Recommendation
## 建议

### Immediate (Today)
### 立即 (今天)

**Option A: Set Environment Variable**

```bash
# Add to ~/.zshrc (macOS default)
echo 'export CLAWRL_ENABLED=1' >> ~/.zshrc
source ~/.zshrc

# Or add to ~/.bashrc
echo 'export CLAWRL_ENABLED=1' >> ~/.bashrc
source ~/.bashrc
```

**Benefit:** Quick fix, no code changes

**选项 A: 设置环境变量**

```bash
# 添加到 ~/.zshrc (macOS 默认)
echo 'export CLAWRL_ENABLED=1' >> ~/.zshrc
source ~/.zshrc

# 或添加到 ~/.bashrc
echo 'export CLAWRL_ENABLED=1' >> ~/.bashrc
source ~/.bashrc
```

**收益:** 快速修复，无需代码更改

---

### Short-Term (This Week)
### 短期 (本周)

**Option B: Enhance Session Hook**

Modify `session_hook.sh` to auto-inject on every session:

**选项 B: 增强会话钩子**

修改 `session_hook.sh` 在每次会话时自动注入:

```bash
#!/bin/bash
# ~/.openclaw/workspace/skills/claw-rl/scripts/session_hook.sh

# Auto-inject memory before every session
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/memory_retrieval.sh" auto file
```

---

### Long-Term (Phase 2+)
### 长期 (Phase 2+)

**Option C: Proper OpenClaw Integration**

Work with OpenClaw to support auto-activating skills:

**选项 C: 正确的 OpenClaw 集成**

与 OpenClaw 合作支持自动激活技能:

```json
{
  "skills": {
    "claw-rl": {
      "enabled": true,
      "autoActivate": true
    }
  }
}
```

---

## 📋 Source Code Locations
## 源代码位置

### Core Scripts (Source Code)
### 核心脚本 (源代码)

| Script | Purpose | Lines |
|--------|---------|-------|
| **activate.sh** | Manual activation | ~80 lines |
| **session_hook.sh** | Session lifecycle | ~50 lines |
| **memory_retrieval.sh** | Memory injection | ~80 lines |
| **pre_flight_check.sh** | Pre-flight checks | ~150 lines |
| **prm_judge.sh** | PRM reward judgment | ~180 lines |
| **reward_collector.sh** | Reward collection | ~150 lines |
| **hint_extractor.sh** | Hint extraction | ~150 lines |
| **training_loop.sh** | Training loop | ~130 lines |
| **test_all.sh** | Testing | ~50 lines |
| **install.sh** | Installation | ~60 lines |

**Total Source Code:** ~1,080 lines of bash scripts

**总源代码:** ~1,080 行 bash 脚本

---

### Data Files
### 数据文件

| Directory | Purpose | Format |
|-----------|---------|--------|
| **`.rewards/`** | Reward records | JSONL |
| **`.hints/`** | Hint records | JSONL |
| **`.learnings/`** | Learning entries | Markdown |

**Data Storage:** `~/.openclaw/workspace/skills/claw-rl/scripts/`

**数据存储:** `~/.openclaw/workspace/skills/claw-rl/scripts/`

---

## 🔍 Why Not a Plugin?
## 为什么不是插件？

### Historical Reason
### 历史原因

**claw-rl was created as:**
1. **Research Project** - Based on OpenClaw-RL paper
2. **Proof of Concept** - Demonstrate learning capability
3. **Optional Feature** - Not all users want learning

**claw-rl 创建为:**
1. **研究项目** - 基于 OpenClaw-RL 论文
2. **概念验证** - 展示学习能力
3. **可选功能** - 不是所有用户都需要学习

---

### Technical Reason
### 技术原因

**OpenClaw Skill System:**
- Skills are optional, user-activated
- Plugins are core, auto-loaded
- claw-rl designed as skill, not plugin

**OpenClaw 技能系统:**
- 技能是可选的，用户激活
- 插件是核心的，自动加载
- claw-rl 设计为技能，非插件

---

### Design Philosophy
### 设计哲学

**Why Optional?**
- Learning from conversations is personal
- Users should choose to enable it
- Privacy-first design

**为什么可选？**
- 从对话中学习是私人的
- 用户应该选择启用
- 隐私优先设计

---

## 🎯 Decision Required
## 需要决策

**Peter, please decide:**

**彼得，请决定:**

- [ ] **A)** Keep as manual (current)
- [ ] **B)** Set environment variable (quick fix)
- [ ] **C)** Enhance session hook (auto-inject)
- [ ] **D)** Convert to auto-load plugin (long-term)
- [ ] **E)** Other (specify)

- [ ] **A)** 保持手动 (当前)
- [ ] **B)** 设置环境变量 (快速修复)
- [ ] **C)** 增强会话钩子 (自动注入)
- [ ] **D)** 转换为自动加载插件 (长期)
- [ ] **E)** 其他 (指定)

---

## 📊 Summary
## 总结

| Question | Answer |
|----------|--------|
| **Project Type** | OpenClaw Skill (not plugin) |
| **Location** | `~/.openclaw/workspace/skills/claw-rl/` |
| **Source Code** | Bash scripts in `scripts/` directory |
| **Why Manual?** | Designed as optional skill |
| **How to Auto?** | Env var, hook, or plugin conversion |
| **Recommendation** | Option B (env var) for now |

| 问题 | 答案 |
|------|------|
| **项目类型** | OpenClaw Skill (非插件) |
| **位置** | `~/.openclaw/workspace/skills/claw-rl/` |
| **源代码** | `scripts/` 目录中的 bash 脚本 |
| **为什么手动？** | 设计为可选技能 |
| **如何自动？** | 环境变量、钩子或插件转换 |
| **建议** | 选项 B (环境变量) 当前 |

---

*Analysis Created: 2026-03-23T23:15+08:00*  
*Version:* 1.0.0  
*Status:* 📋 **READY FOR REVIEW**  
*Next:* Peter's decision on activation method  
*"Understanding Structure, Enabling Automation"*
