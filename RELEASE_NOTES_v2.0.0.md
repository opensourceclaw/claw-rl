# claw-rl v2.0.0 - OpenClaw Plugin Architecture

**Release Date:** 2026-03-31

## 🎉 Highlights

- **OpenClaw Plugin Architecture**: Complete TypeScript Plugin implementation
- **Local-First Design**: stdio JSON-RPC communication, zero network overhead
- **~0.4ms Average Latency**: Excellent performance for production use
- **Auto-Inject & Auto-Learn**: Automatic learning from user interactions

## 🚀 New Features

### OpenClaw Plugin

- TypeScript Plugin with full type definitions
- Auto-Inject: Inject learned rules at session start
- Auto-Learn: Collect feedback from user messages
- Tools: `learning_status`, `collect_feedback`, `get_learned_rules`

### Python Bridge

- stdio JSON-RPC server for zero network overhead
- Automatic PYTHONPATH configuration
- Graceful error handling
- Debug mode for troubleshooting

## 📊 Performance

| Operation | Latency | Evaluation |
|-----------|---------|------------|
| Initialize | ~2ms | ✅ Excellent |
| Collect feedback | ~0.03ms | ✅ Excellent |
| Extract hint | ~1ms | ✅ Excellent |
| Get rules | ~0.7ms | ✅ Excellent |
| Process learning | ~0.5ms | ✅ Excellent |
| **Average** | **~0.4ms** | **✅ Excellent** |

## 📦 Installation

### Python Package

```bash
pip install claw-rl==2.0.0
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
    "slots": {
      "context-engine": "claw-rl"
    },
    "claw-rl": {
      "enabled": true,
      "config": {
        "workspaceDir": "~/.openclaw/workspace",
        "autoInject": true,
        "autoLearn": true,
        "topK": 10
      }
    }
  }
}
```

## 🧪 Testing

- **207 tests passing**
- **78% code coverage**
- All integration tests passing (6/6)

## 🐛 Bug Fixes

- Fixed module path resolution for Python Bridge
- Fixed PYTHONPATH configuration for OpenClaw integration
- Fixed JSON-RPC communication stability
- Fixed type definitions for OpenClaw Plugin API

## 📝 Documentation

- [ADR-001: Plugin Architecture](docs/v2.0.0/ADR-001-plugin-architecture.md)
- [User Stories](docs/v2.0.0/USER_STORIES.md)
- [Migration Plan](docs/v2.0.0/MIGRATION_PLAN.md)

## 🤝 Contributors

- Peter Cheng (@peterchengcn)
- Friday (AI Assistant)

## 📄 License

Apache License 2.0

---

**Full Changelog**: [CHANGELOG.md](CHANGELOG.md)
