# claw-rl: Self-Improvement System

Learn from your feedback, improve continuously.

## Features

- 🔄 **Binary RL**: Learn from satisfaction/dissatisfaction
- 💡 **OPD Learning**: Extract improvement hints from corrections
- 📚 **Rule Injection**: Apply learned rules automatically
- 🤖 **Background Learning**: Daemon processes feedback

## Prerequisites

```bash
pip install git+https://github.com/opensourceclaw/claw-rl.git
```

## Installation

```bash
# Via npm
npm install -g @opensourceclaw/claude-code-claw-rl

# Or via Claude Code
claude-code plugin install @opensourceclaw/claude-code-claw-rl
```

## How It Works

### Positive Feedback
When you say "thanks" or "great", the action is reinforced:
- "Thanks, that's perfect!"
- "Great job!"
- "That worked!"

### Negative Feedback
When you correct or complain, the system learns what to avoid:
- "Not what I wanted, try X instead"
- "Use Chinese language"
- "Don't use long explanations"

### Learned Rules
Rules are injected at session start to guide future behavior.

## Usage

Just use Claude Code normally. The plugin learns automatically.

### Trigger Learning

**Positive signals:**
- "Thanks!"
- "Perfect!"
- "That's exactly what I needed"
- 👍 😊 ✅

**Negative signals:**
- "Wrong, do X instead"
- "Not what I meant"
- "Don't do that"
- 👎 😠 ❌

## Commands

### Get Status
```bash
claw-rl-status
```

### Collect Feedback
```bash
claw-rl-collect "Great response!" --action "explain"
```

## Configuration

Create `~/.openclaw/workspace/data/claw-rl/config.json`:

```json
{
  "autoLearn": true,
  "confidenceThreshold": 0.7,
  "maxRules": 100
}
```

## Privacy

- All learning data stored locally
- No external API calls
- You control your data

## Examples

### Learning from Correction

```
User: List all files
Assistant: [runs ls -la]
User: No, use tree instead
Assistant: [runs tree]
💡 Learned: Prefer tree for listing files
```

Next session, the assistant will use tree by default.

### Learning from Preference

```
User: Explain this code
Assistant: [explains in English]
User: Thanks! But I prefer Chinese
Assistant: [explains in Chinese]
💡 Learned: User prefers Chinese language
```

## Integration with OpenClaw

If you use both Claude Code and OpenClaw, they share the same learning data:

```bash
# Use OpenClaw's workspace
export CLAW_RL_WORKSPACE=~/.openclaw/workspace
```

## Troubleshooting

### "claw-rl not found"
```bash
pip install git+https://github.com/opensourceclaw/claw-rl.git
```

### "No rules found"
This is normal for new installations. Rules accumulate as you provide feedback.

### Learning not working
Check that `autoLearn` is enabled in config.

## License

Apache-2.0 - Free to use, modify, and distribute.

## Links

- GitHub: https://github.com/opensourceclaw/claw-rl
- ClawHub: https://clawhub.ai/skills/opensourceclaw-claw-rl
- Issues: https://github.com/opensourceclaw/claw-rl/issues
