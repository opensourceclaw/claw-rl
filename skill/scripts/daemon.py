#!/usr/bin/env python3
"""Manage learning daemon"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Manage claw-rl daemon")
    parser.add_argument("action", choices=["start", "stop", "status", "restart"], help="Daemon action")
    parser.add_argument("--workspace", "-w", default="~/.openclaw/workspace", help="Workspace path")
    args = parser.parse_args()
    
    try:
        from claw_rl.core import LearningDaemon
    except ImportError:
        print("❌ claw-rl not installed. Run: pip install claw-rl")
        sys.exit(1)
    
    daemon = LearningDaemon(workspace=args.workspace)
    
    if args.action == "start":
        daemon.start()
        print("✅ Learning daemon started")
    elif args.action == "stop":
        daemon.stop()
        print("✅ Learning daemon stopped")
    elif args.action == "status":
        status = daemon.status()
        print(f"📊 Daemon status: {status}")
    elif args.action == "restart":
        daemon.stop()
        daemon.start()
        print("✅ Learning daemon restarted")

if __name__ == "__main__":
    main()
