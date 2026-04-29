---
name: claw-rl
description: OpenClaw-RL 自我改进核心系统.从用户对话中自动提取学习信号,实现 Binary RL 评估学习和 OPD 指令学习,支持会话前记忆注入和预检查清单.

metadata: {"clawdbot":{"emoji":"🧠","requires":{"bins":["bash"]},"primaryEnv":"CLAWRL_ENABLED"}}
---

# claw-rl - OpenClaw 自我改进核心系统

基于 OpenClaw-RL 论文实现的自我改进能力,让 Friday 从每次对话中学习.

---

## 🚀 快速开始

### 启用 claw-rl

```bash
# 设置环境变量启用
export CLAWRL_ENABLED=1

# 或在 OpenClaw 配置中添加
clawrl.enabled: true
```

---

## 🔧 核心功能

### 1. 会话前记忆注入

每次会话前自动注入相关记忆:
- 📜 Friday 宪法核心原则
- 📁 工作目录配置
- 📚 相关学习条目

```bash
# 手动触发记忆注入
node {baseDir}/scripts/memory_retrieval.sh auto file
```

### 2. 预检查清单

特定操作前强制执行预检查:
- 文件操作 → 检查目录分工
- 技能使用 → 检查技能是否存在
- 外部操作 → 检查授权

```bash
# 文件操作预检查
node {baseDir}/scripts/pre_flight_check.sh file_write <路径>
```

### 3. Binary RL(评估信号学习)

从用户反馈中自动判断满意度:
- 满意 (+1): "谢谢","很好",继续追问
- 不满意 (-1): "不对","错了","应该"
- 中性 (0): 无明显信号

```bash
# 评估用户反馈
node {baseDir}/scripts/prm_judge.sh rule "谢谢,很好" "创建了文件"
```

### 4. OPD(指令信号学习)

从用户纠正中提取改进方向:
- "应该 X" → "操作前 X"
- "不要 Y" → "避免 Y"
- "先 X 再 Y" → "顺序:先 X 再 Y"

```bash
# 提取 Hint
node {baseDir}/scripts/hint_extractor.sh extract "应该先检查文件"
```

### 5. 后台训练循环

定期处理学习信号,更新记忆:
- 检查新奖励记录
- 检查新 Hint 记录
- 负面奖励累积触发学习

```bash
# 后台监控(每 5 分钟)
node {baseDir}/scripts/training_loop.sh daemon 300
```

---

## 📋 使用示例

### 示例 1: 文件操作场景

```
用户:帮我创建一个文件

[系统自动注入]
📜 Friday 宪法 - 核心原则
  ### 2️⃣ 文件操作
  - /Users/liantian/workspace/ → 日常项目
  - ~/.openclaw/workspace/ → 系统配置

Friday:好的,这是什么类型的文件?
- 如果是日常项目文档 → /Users/liantian/workspace/
- 如果是 OpenClaw 配置 → ~/.openclaw/workspace/
```

### 示例 2: 用户纠正后的学习

```
1. Friday 创建文件到错误目录
2. 用户:不对,应该放到 ~/.openclaw/workspace/

3. 自动触发学习:
   - PRM Judge: 奖励 = -1
   - OPD Hint: "操作前确认目录为~/.openclaw/workspace/"
   - 记录到奖励文件
   - 累积负面奖励触发学习条目生成

4. 下次会话前:
   - 自动注入相关学习条目
   - 预防重复错误
```

---

## 📊 工作流程

```
用户输入 → Friday 生成回复 → 用户回复 (next-state)
                                    ↓
                    ┌───────────────┴───────────┐
                    ↓                           ↓
           ┌──────────────┐           ┌──────────────┐
           │  Binary RL   │           │     OPD      │
           │  (评估信号)  │           │  (指令信号)  │
           │              │           │              │
           │ PRM Judge    │           │ Hint Extract │
           │ → r∈{+1,-1,0}│           │ → 文本提示   │
           └──────┬───────┘           └──────┬───────┘
                  ↓                          ↓
           ┌──────────────┐          ┌──────────────┐
           │ 奖励记录     │          │ 增强上下文   │
           │ .rewards/    │          │ .hints/      │
           └──────┬───────┘          └──────┬───────┘
                  ↓                          ↓
                  └───────────┬─────────────┘
                              ↓
                     ┌──────────────┐
                     │  记忆更新    │
                     │ .learnings/  │
                     └──────────────┘
```

---

## 🛠️ 脚本说明

| 脚本 | 功能 | 用法 |
|------|------|------|
| `memory_retrieval.sh` | 记忆检索注入 | `auto <场景>` |
| `pre_flight_check.sh` | 预检查清单 | `file_write <路径>` |
| `prm_judge.sh` | PRM 奖励判断 | `rule <回复> <动作>` |
| `reward_collector.sh` | 奖励收集 | `summary / check` |
| `hint_extractor.sh` | Hint 提取 | `extract <反馈>` |
| `training_loop.sh` | 训练循环 | `run / daemon` |

---

## 📝 配置选项

| 配置项 | 默认值 | 说明 |
|--------|-------|------|
| `clawrl.enabled` | false | 是否启用 claw-rl |
| `clawrl.memory_inject` | true | 会话前记忆注入 |
| `clawrl.pre_flight_check` | true | 预检查清单 |
| `clawrl.binary_rl` | true | Binary RL 学习 |
| `clawrl.opd` | true | OPD 指令学习 |
| `clawrl.training_interval` | 300 | 训练循环间隔 (秒) |

---

## 📈 效果对比

| 场景 | 无 claw-rl | 启用 claw-rl |
|------|-----------|-------------|
| 文件目录错误 | 可能重复犯 | 自动注入规则 + 学习更新 |
| 忘记已有技能 | 无法追踪 | 技能列表强制注入 |
| 用户纠正 | 事后记录 | 自动提取 Hint+ 奖励更新 |
| 隐性反馈 | 无法识别 | PRM 自动判断满意/不满意 |

---

## 🔍 调试命令

```bash
# 查看今日奖励统计
node {baseDir}/scripts/reward_collector.sh summary

# 检查学习触发条件
node {baseDir}/scripts/reward_collector.sh check

# 注入 Hint 到上下文
node {baseDir}/scripts/hint_extractor.sh inject

# 生成训练报告
node {baseDir}/scripts/training_loop.sh report

# 运行综合测试
node {baseDir}/scripts/test_all.sh
```

---

## 📚 相关文档

- [Phase 1 设计文档](MEMORY_ENHANCEMENT.md)
- [Phase 2 设计文档](PHASE2_DESIGN.md)
- [Friday 宪法](FRIDAY_CONSTITUTION.md)
- [OpenClaw-RL 论文](https://arxiv.org/abs/2603.10165)

---

**版本:** 1.0  
**创建时间:** 2026-03-17  
**作者:** Friday + Peter
