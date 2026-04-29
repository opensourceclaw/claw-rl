# claw-rl Plugin 安全部署指南

## 测试结果

✅ 所有测试通过:
- TypeScript 编译成功
- Bridge 模块正常
- JSON-RPC 通信测试通过 (6/6)
- Plugin 元数据正常
- 编译文件存在

## 安全部署步骤

### Step 1: 备份当前配置

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%Y%m%d_%H%M%S)
```

### Step 2: 禁用 contextEngine slot

编辑 `~/.openclaw/openclaw.json`,确保:

```json
{
  "plugins": {
    "slots": {},  // 清空 slots,不替换 legacy context engine
    "entries": {
      "claw-rl": {
        "enabled": true,
        "config": { ... }
      }
    }
  }
}
```

### Step 3: 观察 OpenClaw 日志

打开一个终端,持续观察日志:

```bash
openclaw logs --follow | grep -E "claw-rl|Context engine|registerContextEngine"
```

### Step 4: 重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

### Step 5: 验证 Plugin 状态

```bash
openclaw plugins list | grep -A 3 "claw-rl"
```

期望看到:
- Status: `loaded` (不是 `disabled`)
- 没有错误日志

### Step 6: 测试 Plugin 功能

在新的 OpenClaw 会话中,尝试调用 Tools:

```
learning_status
```

期望返回:
```json
{
  "initialized": true,
  "components": {
    "binary_rl": true,
    "opd_hint": true,
    "learning_loop": true
  }
}
```

### Step 7: 启用 contextEngine slot(可选)

如果 Step 6 成功,可以尝试启用 contextEngine:

```json
{
  "plugins": {
    "slots": {
      "contextEngine": "claw-rl"
    },
    "entries": {
      "claw-rl": {
        "enabled": true,
        "config": { ... }
      }
    }
  }
}
```

然后重启 Gateway 并观察日志.

## 回滚方案

如果出现问题:

1. 恢复备份配置:
   ```bash
   cp ~/.openclaw/openclaw.json.backup.XXXXXX ~/.openclaw/openclaw.json
   ```

2. 重启 Gateway:
   ```bash
   openclaw gateway restart
   ```

3. 禁用 Plugin:
   ```bash
   openclaw plugins disable claw-rl
   ```

## 已知问题

1. **contextEngine slot 问题**:如果看到 `Context engine "claw-rl" is not registered`,说明 Context Engine 注册有问题,需要检查 API 签名.

2. **Hook 事件名称**:使用正确的事件名称(`session_start` 而不是 `before_session_start`).

3. **Bridge 启动失败**:检查 PYTHONPATH 和 Python 路径配置.
