# claw-rl Tutorial

## Getting Started

### Installation

```bash
cd ~/workspace/osprojects/claw-rl
pip3 install -e .
```

### Step 1: Basic Feedback Collection

```python
from claw_rl import LearningLoop

loop = LearningLoop()

# Collect user feedback
loop.collect_feedback(
    feedback="satisfied",  # or "dissatisfied"
    action="code_review_completed"
)
```

### Step 2: Understanding the Learning Loop

```python
# After each session, learning happens automatically
# View learned rules
rules = loop.get_learned_rules(top_k=10)
for rule in rules:
    print(f"{rule.pattern} -> {rule.response}")
```

### Step 3: Viewing Dashboard Metrics

```bash
# Start dashboard
python -m claw_rl.dashboard.dashboard

# Visit http://localhost:5000
```

### Step 4: Exporting and Importing Rules

```python
from claw_rl.rule_portability import RuleExporter, RuleImporter

# Export rules
exporter = RuleExporter(workspace="/path/to/workspace")
exporter.export_rules(output_path="rules.json")

# Import rules
importer = RuleImporter(workspace="/path/to/workspace")
importer.import_rules("rules.json", strategy="merge")
```

## Configuration Examples

### Basic Usage (minimal.yaml)

```yaml
learning:
  enabled: true
  auto_inject: true

feedback:
  collection: auto
```

### Production (production.yaml)

```yaml
learning:
  enabled: true
  auto_inject: true
  top_k: 20

dashboard:
  port: 5000
  host: "0.0.0.0"

monitoring:
  metrics: true
  alerts: true
```

### Development (development.yaml)

```yaml
learning:
  enabled: true
  debug: true

logging:
  level: DEBUG
  verbose: true
```

## Troubleshooting

### Rules not being learned

Check feedback collection is working:
```python
print(loop.get_stats())
```

### Dashboard not loading

Verify Flask is installed:
```bash
pip3 install flask
```

### Import errors

Ensure all dependencies are installed:
```bash
pip3 install -r requirements.txt
```
