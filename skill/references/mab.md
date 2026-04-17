# Multi-Armed Bandit Strategies

## Overview

Multi-Armed Bandit (MAB) provides intelligent strategy selection:
- Balances exploration vs exploitation
- Adapts to changing environments
- Optimizes for long-term reward

## Available Strategies

### Thompson Sampling

Bayesian approach with beta distributions:
- Models uncertainty in strategy performance
- Samples from posterior distribution
- Naturally balances exploration/exploitation

```python
from claw_rl.mab import ThompsonSamplingStrategy

strategy = ThompsonSamplingStrategy(
    alpha=1.0,  # Prior success count
    beta=1.0    # Prior failure count
)
```

### ε-Greedy

Simple but effective strategy:
- Explores with probability ε
- Exploits best strategy with probability 1-ε
- Configurable decay for ε

```python
from claw_rl.mab import EpsilonGreedyStrategy

strategy = EpsilonGreedyStrategy(
    epsilon=0.1,     # Exploration rate
    decay=0.99,      # Decay per round
    min_epsilon=0.01 # Minimum ε
)
```

### Decay Modes

- `none` - No decay
- `linear` - Linear decay per round
- `exponential` - Exponential decay per round
- `step` - Step decay at intervals

## Strategy Performance Tracking

Each strategy tracks:
- Total selections
- Success count
- Failure count
- Average reward
- Last selection timestamp

## Selection Process

```
1. Get all available strategies
2. Calculate selection probability
3. Sample strategy based on algorithm
4. Execute selected strategy
5. Update performance metrics
6. Repeat
```

## Best Practices

- Start with Thompson Sampling for uncertain environments
- Use ε-Greedy for simpler scenarios
- Monitor strategy performance over time
- Adjust decay parameters based on feedback frequency
