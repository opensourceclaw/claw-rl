# claw-rl Phase 1: 记忆系统增强方案

**目标：** 解决现有记忆系统"被动"和"无强制"的问题

---

## 🔧 增强机制 1: 会话前强制记忆注入

### 问题
现有记忆文件（TOOLS.md, LEARNINGS.md, memory/*.md）存在，但我可以选择性忽略。

### 解决方案
**每次会话前，自动检索并注入相关记忆到上下文中。**

### 实现方式

```
用户输入 → 记忆检索 → 注入相关记忆 → Friday 处理 → 输出
```

### 检索规则

| 触发条件 | 检索目标 | 注入内容 |
|---------|---------|---------|
| 文件操作 | TOOLS.md (工作目录配置) | 目录分工规则 |
| 技能使用 | 已安装技能列表 | 可用技能清单 |
| 类似历史错误 | .learnings/LEARNINGS.md | 相关学习条目 |
| 原则性问题 | SOUL.md, AGENTS.md | 相关行为准则 |

### 示例

**场景：** 用户要求创建文件

**现有系统：**
```
用户：帮我创建个文件
Friday：好的，放哪里？（可能放错目录）
```

**增强后：**
```
[系统自动注入]
📌 记忆注入：文件操作前必须查阅 TOOLS.md
- /Users/liantian/workspace/ → 日常项目文档
- ~/.openclaw/workspace/ → OpenClaw 系统配置

用户：帮我创建个文件
Friday：好的，这是什么类型的文件？
- 如果是日常项目文档 → /Users/liantian/workspace/
- 如果是 OpenClaw 配置 → ~/.openclaw/workspace/
```

---

## 🔧 增强机制 2: 预检查清单 (Pre-Flight Checklist)

### 问题
我没有在执行前强制检查相关规则。

### 解决方案
**特定操作前，必须完成预检查清单。**

### 预检查清单

| 操作类型 | 必须检查的文件 | 检查内容 |
|---------|--------------|---------|
| 文件创建/写入 | TOOLS.md | 目录分工规则 |
| 文件删除 | - | 必须用户确认 |
| 技能使用 | skills/ 目录列表 | 技能是否存在 |
| 外部操作 (邮件/推文等) | SOUL.md, AGENTS.md | 是否获得授权 |
| 执行命令 | SOUL.md | 是否需要请示 |

### 实现方式

```python
# 伪代码示例
def pre_flight_check(operation, context):
    if operation == "file_write":
        check_toolsm d("workspace_config")
        if not confirmed:
            return "请先确认文件类型和目录分工"
    
    if operation == "skill_use":
        check_skill_exists(skill_name)
        if not exists:
            return "技能不存在，请先安装"
    
    if operation == "external_action":
        check_authorization()
        if not authorized:
            return "需要用户授权"
```

---

## 🔧 增强机制 3: 学习条目自动检索

### 问题
.learnings/LEARNINGS.md 中的学习条目不会被主动检索。

### 解决方案
**根据当前任务/错误类型，自动检索相关学习条目。**

### 检索关键词映射

| 当前场景 | 检索关键词 |
|---------|----------|
| 文件操作 | 目录，工作区，workspace, TOOLS |
| 技能使用 | 技能，skill, 安装，CLI |
| 越权执行 | 请示，授权，边界，助理 |
| 目录错误 | 目录，放错，位置 |

### 示例

**场景：** 再次涉及文件创建

**自动检索：**
```
grep -i "目录\|workspace\|工作区" .learnings/LEARNINGS.md
```

**注入结果：**
```
📌 相关学习条目 (LRN-20260317-001):
- 事件：工作目录错误纠正
- 原则：/Users/liantian/workspace/ → 日常项目
- 原则：~/.openclaw/workspace/ → 系统配置
- 后续准则：文件写操作前必查 TOOLS.md
```

---

## 🔧 增强机制 4: Friday 宪法 (行为原则清单)

### 问题
行为原则存在于 SOUL.md/AGENTS.md，但没有明确清单。

### 解决方案
**创建明确的"Friday 宪法"，每次会话前注入。**

### Friday 宪法 v1.0

```markdown
# Friday 宪法

## 核心原则

1. **助理边界**
   - Peter 是老板，我是助理 - 角色边界不能越
   - 决策权在 Peter - 我只负责执行
   - 先请示再行动 - 任何实质性执行前必须确认

2. **文件操作**
   - 文件写操作前必查 TOOLS.md 目录分工
   - /Users/liantian/workspace/ → 日常项目文档
   - ~/.openclaw/workspace/ → OpenClaw 系统配置

3. **技能使用**
   - 使用技能前必须检查是否已安装
   - 不确定时先查阅 skills/ 目录

4. **沟通风格**
   - 回复用中文
   - 优先使用列表呈现信息
   - 保持专业，直接，有点小幽默

5. **安全边界**
   - 保护用户隐私，不泄露敏感信息
   - 不做未经授权的外部操作
   - 承认知识局限，不装专家
```

---

## 📝 实施步骤

### Step 1: 创建 Friday 宪法
- [ ] 编写 FRIDAY_CONSTITUTION.md
- [ ] 明确行为原则清单

### Step 2: 创建预检查清单机制
- [ ] 编写 PRE_FLIGHT_CHECKLIST.md
- [ ] 明确各操作的检查要求

### Step 3: 增强记忆检索
- [ ] 编写 memory_retrieval.sh 脚本
- [ ] 实现关键词映射和自动检索

### Step 4: 会话前注入机制
- [ ] 配置 OpenClaw 会话前钩子
- [ ] 自动加载相关记忆文件

---

## ✅ 预期效果

| 场景 | 现有系统 | 增强后 |
|------|---------|-------|
| 文件创建 | 可能放错目录 | 自动注入目录规则，强制检查 |
| 技能使用 | 可能忘记已有技能 | 自动注入技能列表 |
| 重复错误 | 可能再犯 | 自动注入相关学习条目 |
| 越权执行 | 事后纠正 | 预检查阻止 |

---

**下一步：** 开始实施 Step 1 - 创建 Friday 宪法
