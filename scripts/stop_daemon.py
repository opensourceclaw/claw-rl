#!/usr/bin/env python3
"""
Stop Learning Daemon

Usage:
    python scripts/stop_daemon.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from claw_rl.learning_daemon import LearningDaemon


def main():
    if LearningDaemon.stop_daemon():
        print("Learning daemon stopped")
    else:
        print("Learning daemon is not running")
        sys.exit(1)


if __name__ == '__main__':
    main()
