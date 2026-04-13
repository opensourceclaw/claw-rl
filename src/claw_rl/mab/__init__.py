# Copyright 2026 Peter Cheng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Multi-Armed Bandit Module

Intelligent strategy selection using Thompson Sampling and other bandit algorithms.

This is what makes claw-rl different from simple feedback collection:
it provides sophisticated exploration/exploitation balance for
optimal strategy selection.
"""

from .mab import (
    MultiArmedBandit,
    Strategy,
    StrategyPerformance,
    BanditConfig,
    StrategyType,
    BanditError,
    StrategyError,
    SelectionError,
)
from .thompson_sampling import (
    BetaDistribution,
    ThompsonSamplingStrategy,
)
from .epsilon_greedy import (
    EpsilonGreedyStrategy,
    DecayMode,
)

__all__ = [
    # Multi-Armed Bandit
    "MultiArmedBandit",
    "Strategy",
    "StrategyPerformance",
    "BanditConfig",
    "StrategyType",
    "BanditError",
    "StrategyError",
    "SelectionError",
    # Thompson Sampling
    "BetaDistribution",
    "ThompsonSamplingStrategy",
    # Epsilon Greedy
    "EpsilonGreedyStrategy",
    "DecayMode",
]
