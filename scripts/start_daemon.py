#!/usr/bin/env python3
"""
Start Learning Daemon

Usage:
    python scripts/start_daemon.py [interval_seconds]

Example:
    python scripts/start_daemon.py 300  # Run every 5 minutes
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from claw_rl.learning_daemon import LearningDaemon


def main():
    # Get interval from argument or default to 5 minutes
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    
    # Check if already running
    if LearningDaemon.is_running():
        print("Learning daemon is already running")
        print("Use 'python scripts/stop_daemon.py' to stop it first")
        sys.exit(1)
    
    # Start daemon
    print(f"Starting learning daemon with {interval}s interval...")
    daemon = LearningDaemon(interval_seconds=interval)
    daemon.start()


if __name__ == '__main__':
    main()
