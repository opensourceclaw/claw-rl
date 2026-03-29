# claw-rl Phase 2: OpenClaw-RL 核心实现

**状态：** ✅ 完成  
**创建时间：** 2026-03-17

---

## 📦 新增文件

| 文件 | 功能 |
|------|------|
| `PHASE2_DESIGN.md` | Phase 2 设计文档 |
| `scripts/prm_judge.sh` | PRM 奖励判断 |
| `scripts/reward_collector.sh` | 奖励信号收集 |
| `scripts/hint_extractor.sh` | OPD Hint 提取 |
| `scripts/training_loop.sh` | 后台训练循环 |
| `scripts/test_all.sh` | 综合测试脚本 |
| `.rewards/` | 奖励记录目录 |
| `.hints/` | Hint 记录目录 |

---

## 🚀 使用方法

### 1. PRM Judge - 评估用户反馈

```bash
# 评估用户回复
./scripts/prm_judge.sh rule <用户回复> <动作描述>

# 示例：满意反馈
./scripts/prm_judge.sh rule "谢谢，很好" "创建了文件"
# 输出：奖励：+1

# 示例：不满意反馈
./scripts/prm_judge.sh rule "不对，应该放这里" "创建了文件"
# 输出：奖励：-1
```

### 2. OPD Hint Extractor - 提取指令信号

```bash
# 从用户纠正中提取 Hint
./scripts/hint_extractor.sh extract <用户反馈> [动作描述]

# 示例
./scripts/hint_extractor.sh extract "应该先检查文件再编辑"
# 输出：Hint: 操作前先检查文件再编辑

# 注入 Hint 到上下文
./scripts/hint_extractor.sh inject
```

### 3. Reward Collector - 收集奖励信号

```bash
# 记录奖励
./scripts/reward_collector.sh record <reward> <reason> <action> <reply>

# 查看今日统计
./scripts/reward_collector.sh summary

# 检查学习触发条件
./scripts/reward_collector.sh check
```

### 4. Training Loop - 后台训练

```bash
# 单次训练循环
./scripts/training_loop.sh run

# 生成训练报告
./scripts/training_loop.sh report

# 后台监控模式（每 5 分钟检查一次）
./scripts/training_loop.sh daemon 300
```

### 5. 综合测试

```bash
# 运行所有组件测试
./scripts/test_all.sh
```

---

## 📊 工作流程示例

### 场景 1: 用户满意

```
1. Friday 创建文件 → 用户回复："谢谢，很好"
2. PRM Judge 评估：
   ./scripts/prm_judge.sh rule "谢谢，很好" "创建了文件"
   → 奖励：+1
3. 记录奖励：
   ./scripts/reward_collector.sh record 1 "满意反馈" "创建文件" "谢谢，很好"
4. Training Loop 后台处理（无负面信号，不触发学习）
```

### 场景 2: 用户纠正

```
1. Friday 创建文件 → 用户回复："不对，应该先检查文件"
2. PRM Judge 评估：
   ./scripts/prm_judge.sh rule "不对，应该先检查文件" "创建了文件"
   → 奖励：-1
3. OPD Hint 提取：
   ./scripts/hint_extractor.sh extract "应该先检查文件"
   → Hint: 操作前先检查文件
4. 记录奖励和 Hint：
   ./scripts/reward_collector.sh record -1 "纠正" "创建文件" "不对..."
   ./scripts/hint_extractor.sh record "操作前先检查文件" "创建文件"
5. Training Loop 检测到负面奖励累积 → 触发学习更新
```

---

## 🎯 核心机制

### Binary RL（评估信号）

```
用户回复 → PRM Judge → r ∈ {+1, -1, 0} → 记录到 .rewards/
                                          ↓
                              累积负面奖励 >= 3 → 触发学习
```

### OPD（指令信号）

```
用户纠正 → Hint Extractor → 文本提示 → 记录到 .hints/
                                        ↓
                                注入到会话上下文
```

### 训练循环

```
后台定期执行：
1. 检查新奖励记录
2. 检查新 Hint 记录
3. 负面奖励累积 >= 3 → 生成学习条目
4. 更新记忆文件
```

---

## 📈 预期效果

| 功能 | Phase 1 | Phase 2 |
|------|---------|-------|
| 用户反馈处理 | 手动记录 | 自动 PRM 判断 |
| 隐性信号识别 | ❌ 无法识别 | ✅ 满意/不满意自动判断 |
| 指令提取 | ❌ 无 | ✅ Hint 自动提取 |
| 学习触发 | 手动 | 自动（累积负面奖励） |
| 训练方式 | 无 | 后台异步循环 |

---

## 🔧 技术细节

### PRM Judge 判断规则

| 关键词 | 奖励 | 说明 |
|--------|------|------|
| 谢谢/好的/很好 | +1 | 满意 |
| 不对/错了/应该 | -1 | 纠正 |
| 那/然后/接下来 | +1 | 继续对话（隐含满意） |
| 还是/仍然 | -1 | 重复问题（不满意） |
| 其他 | 0 | 中性 |

### Hint 提取规则

| 用户反馈模式 | 提取的 Hint |
|------------|-----------|
| "应该 X" | "操作前 X" |
| "先 X 再 Y" | "顺序：先 X 再 Y" |
| "不要 X" | "避免 X" |
| "用 X 方法" | "优先使用 X" |

### 学习触发条件

- 单日负面奖励 >= 3 次
- 或同一场景连续负面奖励 >= 2 次

---

## 📝 下一步

### Phase 3: 集成与优化

- [ ] 与 OpenClaw 会话流程集成
- [ ] 自动化奖励记录（无需手动调用）
- [ ] LLM-based PRM Judge（更准确）
- [ ] Hint 质量评估和过滤
- [ ] 长期奖励趋势分析

---

**最后更新：** 2026-03-17
