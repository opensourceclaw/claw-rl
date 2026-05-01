# claw-rl OpenClaw Hooks 集成架构

## 定位

claw-rl 是 OpenClaw 的增强学习插件，通过 **纯 hooks** 方式集成，不占用 Plugin Slot。与 claw-mem 的区别：

| | claw-mem | claw-rl |
|---|---|---|
| 角色 | 替换内置 memory-core | 增强学习能力 |
| Plugin Slot | `slots.memory` | 无（不需要） |
| kind | `"memory"` | 无（hooks-only） |
| 注册 API | `registerMemoryCapability()` | `registerTool()` + `api.on()` |
| Hook | `before_agent_start` / `agent_end` | `before_agent_start` / `agent_end` |

## 现有问题

| 问题 | 根因 | 影响 |
|------|------|------|
| `kind: "context-engine"` | OpenClaw 无此 slot | 集成失败/阻塞 |
| `session_start` / `message_received` / `session_end` | 事件名不匹配 OpenClaw 内部 | Hook 不触发 |
| `workspaceDir` 回退到 `process.cwd()` | 未配置时用网关工作目录 | Bridge 启动失败 |
| Bridge 启动失败 | `claw_rl.bridge` 在错误目录下不可导入 | 所有工具/回调超时 |

## 集成架构

```
OpenClaw Gateway
    │
    ├─ plugins.slots.memory = "claw-mem"       ← 接管 memory slot
    │
    └─ plugins.entries.claw-rl                  ← hooks 插件
         │
         ├─ registerTool('learning_status')     → bridge.call('status')
         ├─ registerTool('collect_feedback')    → bridge.call('collect_feedback')
         ├─ registerTool('get_learned_rules')   → bridge.call('get_rules')
         │
         ├─ api.on('before_agent_start')        → get_rules → inject rules
         └─ api.on('agent_end')                 → collect feedback + process_learning
```

## 修改清单

### 1. 去掉 `kind`

```typescript
// 删除
kind: 'context-engine',
```

### 2. Hook 事件重命名 + 注入支持

```typescript
// before_agent_start: 注入学习规则到上下文
api.on('before_agent_start', async (event, ctx) => {
    if (!bridge.isReady()) return;
    const result = await bridge.call('get_rules', { top_k: config.topK });
    if (result.rules?.length > 0) {
        return {
            inject: [{ role: 'system', content: formatRules(result.rules) }],
        };
    }
});

// agent_end: 收集反馈 + 处理学习
api.on('agent_end', async (event, ctx) => {
    if (!bridge.isReady()) return;
    const feedback = extractFeedbackFromEvent(event);
    if (feedback) {
        await bridge.call('collect_feedback', feedback);
    }
    await bridge.call('process_learning');
});
```

### 3. workspaceDir 默认值

```typescript
workspaceDir: api.pluginConfig?.workspaceDir
    || '/Users/liantian/workspace/osprojects/claw-rl'
```

### 4. 保持不变的组件

- ClawRLBridge（JSON-RPC spawn + 行缓冲 + isReady 守卫）
- getTextContent() 类型安全
- registerTool() factory 模式
- registerService() 生命周期

## 最终配置

```json
{
  "plugins": {
    "allow": ["claw-mem", "claw-rl"],
    "entries": {
      "claw-rl": {
        "enabled": true,
        "config": {
          "workspaceDir": "/Users/liantian/workspace/osprojects/claw-rl",
          "autoInject": true,
          "autoLearn": true
        }
      }
    },
    "slots": {
      "memory": "claw-mem"
    }
  }
}
```
