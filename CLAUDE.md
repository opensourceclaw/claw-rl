# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

claw-rl is a **Self-Improvement System** for AI agents. It learns from user feedback and continuously improves through Binary RL and OPD (One-Prompt Directive).

## Key Commands

```bash
# Python tests with coverage
pytest tests/ -v --cov=src/claw_rl

# Plugin integration tests
cd claw_rl_plugin
node test/test_integration.js
```

## Architecture

```
OpenClaw Plugin (TypeScript)
        ↓ spawn + stdio JSON-RPC
claw-rl Python Bridge
        ↓ Python Function Call
claw-rl Core (BinaryRLJudge, OPDHintExtractor, LearningLoop)
```

## Core Concepts

- **Binary RL**: Learns from user satisfaction/dissatisfaction signals
- **OPD**: Extracts improvement hints from user corrections
- **Learning Loop**: Continuous background learning

## Configuration

Key settings in OpenClaw:
- `autoInject`: Inject learned rules at session start
- `autoLearn`: Process learning at session end
- `topK`: Max rules to retrieve (default: 10)

## Tools

- `learning_status()`: Get current learning system status
- `collect_feedback(feedback, action)`: Collect user feedback signal
- `get_learned_rules(top_k, context)`: Get rules for injection

## Performance

- Initialize: ~2ms
- Collect feedback: ~0.03ms
- Extract hint: ~1ms
- Get rules: ~0.7ms
- Process learning: ~0.5ms

## Important Notes

- Zero network overhead: stdio JSON-RPC
- Average latency: ~0.4ms
- 207 tests, 78% coverage
- Framework-independent: Can be integrated with any framework via adapters
