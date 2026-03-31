# claw-rl v2.0.0-beta.2 - Architecture Simplification

**Release Date:** 2026-03-31  
**Status:** Beta (Architecture Simplification Release)

> ⚠️ **Important:** This release removes Context Engine in favor of a simpler Hooks-based architecture.

## 🔄 Architecture Change

### Removed: Context Engine

**Why remove it?**

| Factor | Context Engine | Hooks | Decision |
|--------|---------------|-------|----------|
| **Complexity** | High | Low | Hooks ✅ |
| **Risk** | High (API signature errors) | Low (stable event names) | Hooks ✅ |
| **Functionality** | More powerful | Sufficient | Hooks ✅ |
| **Maintenance** | High | Low | Hooks ✅ |
| **Consistency with claw-mem** | Inconsistent | Consistent | Hooks ✅ |

### Added: Hooks-only Approach

claw-rl now uses only Hooks:

```typescript
// Auto-inject learned rules at session start
api.on('session_start', async (event, ctx) => {
  const rules = await bridge.call('get_rules', { top_k: config.topK });
  // Rules will be available via get_learned_rules tool
});

// Auto-collect feedback
api.on('message_received', async (event, ctx) => {
  const feedback = extractFeedbackFromEvent(event);
  if (feedback) {
    await bridge.call('collect_feedback', feedback);
  }
});

// Process learning at session end
api.on('session_end', async (event, ctx) => {
  await bridge.call('process_learning');
});
```

## ✅ What's Preserved

All Tools functionality remains:

- `learning_status` - Get learning system status
- `collect_feedback` - Collect user feedback
- `get_learned_rules` - Get learned rules for injection

## 📊 Performance

| Operation | Latency | Status |
|-----------|---------|--------|
| Initialize | ~2.89ms | ✅ |
| Collect Feedback | ~0.036ms | ✅ |
| Get Rules | ~9.09ms | ✅ |

## 🧪 Testing

- **Unit Tests:** 207/207 passing
- **Integration Tests:** 6/6 passing
- **Test Coverage:** 78%

## 📦 Installation

### Python Package

```bash
pip install claw-rl==2.0.0b2
```

### OpenClaw Plugin

```bash
cd your-openclaw-project
npm install /path/to/claw-rl/claw_rl_plugin
```

## 🔧 Configuration

```json
{
  "plugins": {
    "slots": {},
    "entries": {
      "claw-rl": {
        "enabled": true,
        "config": {
          "pythonPath": "/path/to/claw-rl/venv/bin/python3",
          "workspaceDir": "~/.openclaw/workspace",
          "autoInject": true,
          "autoLearn": true,
          "topK": 10,
          "debug": false
        }
      }
    }
  }
}
```

## 🤝 Contributors

- Peter Cheng (@peterchengcn)
- Friday (AI Assistant)

## 📄 License

Apache License 2.0

---

**Full Changelog**: [CHANGELOG.md](CHANGELOG.md)
