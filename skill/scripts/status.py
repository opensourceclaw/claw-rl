#!/usr/bin/env python3
"""Check learning system status"""

import argparse

def main():
    parser = argparse.ArgumentParser(description="Check claw-rl status")
    parser.add_argument("--workspace", "-w", default="~/.openclaw/workspace", help="Workspace path")
    args = parser.parse_args()
    
    try:
        from claw_rl.core import LearningLoop, LearningDaemon
        from claw_rl.auto_activate import is_active
    except ImportError:
        print("❌ claw-rl not installed. Run: pip install claw-rl")
        return
    
    print("🔄 claw-rl Status\n")
    print(f"Active: {'✅ Yes' if is_active() else '❌ No'}")
    
    loop = LearningLoop(workspace=args.workspace)
    stats = loop.get_stats()
    
    print(f"\n📊 Statistics:")
    print(f"  Total feedback: {stats.get('total_feedback', 0)}")
    print(f"  Positive: {stats.get('positive_count', 0)}")
    print(f"  Negative: {stats.get('negative_count', 0)}")
    print(f"  Rules learned: {stats.get('rules_count', 0)}")
    print(f"  Pending queue: {stats.get('pending_count', 0)}")
    
    daemon = LearningDaemon(workspace=args.workspace)
    daemon_status = daemon.status()
    print(f"\n daemon: {daemon_status}")

if __name__ == "__main__":
    main()
