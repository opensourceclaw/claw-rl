# claw-rl v2.0.0-beta.1 - Critical Bug Fixes

**Release Date:** 2026-03-31  
**Status:** Beta (Bug Fix Release)

> ⚠️ **Note:** This is a critical bug fix release for v2.0.0-beta.0. All users should upgrade to this version.

## 🐛 Bug Fixes

### Context Engine Registration API

**Problem:** Incorrect `registerContextEngine` API signature caused "Context engine not registered" error.

**Fix:** Corrected API signature to match OpenClaw Plugin SDK:

```typescript
// Before (incorrect)
api.registerContextEngine({
  id: 'claw-rl',
  assemble: async (ctx) => { ... }
});

// After (correct)
api.registerContextEngine('claw-rl', () => {
  return {
    info: { id: 'claw-rl', ... },
    assemble: async (params) => { ... },
    ingest: async (params) => { ... },
    afterTurn: async (params) => { ... },
  };
});
```

### Hook Event Name

**Problem:** Used non-existent event name `before_session_start`.

**Fix:** Changed to correct event name `session_start`.

### ContextEngine Interface

**Problem:** Incomplete interface implementation.

**Fix:** Added required methods:
- `info` property (required)
- `ingest` method (required)
- Fixed method signatures to match OpenClaw Plugin SDK

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
pip install claw-rl==2.0.0b1
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

## 📝 Documentation

- [Deployment Guide](claw_rl_plugin/test/DEPLOYMENT_GUIDE.md)
- [Test Script](claw_rl_plugin/test/test_plugin.sh)

## 🤝 Contributors

- Peter Cheng (@peterchengcn)
- Friday (AI Assistant)

## 📄 License

Apache License 2.0

---

**Full Changelog**: [CHANGELOG.md](CHANGELOG.md)
