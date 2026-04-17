# Learning Algorithms

## Learning Types

### Calibration Learning

Adjusts confidence thresholds based on user feedback:
- Tracks calibration accuracy over time
- Adjusts decision boundaries
- Reduces false positives/negatives

### Strategy Learning

Optimizes action selection strategies:
- Learns which actions lead to satisfaction
- Weights actions by success rate
- Context-aware strategy selection

### Value Preference Learning

Learns user preferences:
- Extracts preference patterns from feedback
- Builds preference model per user
- Adapts to changing preferences

### Context-Aware Learning

Learns situational rules:
- Identifies context patterns
- Associates rules with contexts
- Applies context-specific rules

## Learning Pipeline

```
1. Collect Feedback
   ↓
2. Classify Signal (positive/negative)
   ↓
3. Extract Hints (if negative)
   ↓
4. Update Rule Weights
   ↓
5. Decay Old Rules
   ↓
6. Merge Similar Rules
   ↓
7. Inject into Context
```

## Rule Prioritization

Rules are prioritized by:
- Recency (recent feedback weighted higher)
- Frequency (repeated patterns weighted higher)
- Confidence (high-confidence hints weighted higher)
- Context match (relevant contexts weighted higher)

## Rule Decay

Old rules decay over time:
- Exponential decay with configurable half-life
- Low-weight rules removed automatically
- Important rules protected from decay
