# claw-rl Phase 1: 记忆系统增强

**状态：** ✅ 完成  
**创建时间：** 2026-03-17

---

## 📦 已创建文件

| 文件 | 用途 |
|------|------|
| `FRIDAY_CONSTITUTION.md` | Friday 宪法 - 行为原则清单 |
| `MEMORY_ENHANCEMENT.md` | 记忆系统增强方案文档 |
| `scripts/pre_flight_check.sh` | 预检查脚本 |
| `scripts/memory_retrieval.sh` | 记忆检索脚本 |

---

## 🚀 使用方法

### 1. 记忆检索（会话前注入）

```bash
# 自动根据场景检索
./scripts/memory_retrieval.sh auto <场景关键词>

# 示例：文件操作场景
./scripts/memory_retrieval.sh file

# 示例：技能使用场景
./scripts/memory_retrieval.sh skill

# 完整注入（所有记忆）
./scripts/memory_retrieval.sh full
```

### 2. 预检查（操作前验证）

```bash
# 文件写操作检查
./scripts/pre_flight_check.sh file_write <目标路径>

# 技能使用检查
./scripts/pre_flight_check.sh skill_use <技能名>

# 学习条目检索
./scripts/pre_flight_check.sh learning_check <关键词>
```

---

## 📋 增强的核心机制

### 机制 1: 会话前强制记忆注入

**解决问题：** 记忆文件存在，但我可以选择性忽略

**实现方式：**
```
用户输入 → 记忆检索 → 注入相关记忆 → Friday 处理 → 输出
```

**示例输出：**
```
════════════════════════════════════════
📜 Friday 宪法 - 核心原则
════════════════════════════════════════
  ### 1️⃣ 助理边界
  ### 2️⃣ 文件操作
  ...

════════════════════════════════════════
📁 工作目录配置 (TOOLS.md)
════════════════════════════════════════
日常工作主目录：/Users/liantian/workspace/
  → 日常项目、文档、MBA 论文等

OpenClaw 系统配置目录：~/.openclaw/workspace/
  → AI 配置、记忆文件、技能模块
```

---

### 机制 2: 预检查清单

**解决问题：** 没有在执行前强制检查相关规则

**检查类型：**
| 操作类型 | 必须检查的内容 |
|---------|--------------|
| 文件创建/写入 | TOOLS.md 目录分工 |
| 技能使用 | 技能是否存在 |
| 外部操作 | 是否获得授权 |

---

### 机制 3: 学习条目自动检索

**解决问题：** 学习条目不会被主动检索

**场景映射：**
| 场景 | 检索关键词 |
|------|----------|
| 文件操作 | 目录 workspace 文件 |
| 技能使用 | 技能 skill |
| 权限/执行 | 请示 授权 边界 |

---

## ✅ 预期效果

| 场景 | 现有系统 | 增强后 |
|------|---------|-------|
| 文件创建 | 可能放错目录 | 自动注入目录规则，强制检查 |
| 技能使用 | 可能忘记已有技能 | 自动注入技能列表 |
| 重复错误 | 可能再犯 | 自动注入相关学习条目 |
| 越权执行 | 事后纠正 | 预检查阻止 |

---

## 📝 下一步

### Phase 2: OpenClaw-RL 核心实现

- [ ] PRM Judge 模型配置
- [ ] Binary RL 训练循环
- [ ] OPD Hint 提取机制
- [ ] 异步训练架构

---

## 🔧 技术细节

### 脚本依赖
- bash 3.2+ (macOS 默认版本兼容)
- grep, sed (系统自带)

### 文件位置
```
/Users/liantian/.openclaw/workspace/claw-rl/
├── FRIDAY_CONSTITUTION.md      # Friday 宪法
├── MEMORY_ENHANCEMENT.md       # 增强方案文档
├── README.md                   # 本文件
├── discussion.md               # 项目讨论记录
└── scripts/
    ├── pre_flight_check.sh     # 预检查脚本
    └── memory_retrieval.sh     # 记忆检索脚本
```

---

**最后更新：** 2026-03-17
