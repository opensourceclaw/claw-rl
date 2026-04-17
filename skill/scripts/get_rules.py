#!/usr/bin/env python3
"""Get learned rules for injection"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Get learned rules from claw-rl")
    parser.add_argument("--top-k", "-k", type=int, default=10, help="Max rules to return")
    parser.add_argument("--context", "-c", default=None, help="Context filter")
    parser.add_argument("--workspace", "-w", default="~/.openclaw/workspace", help="Workspace path")
    args = parser.parse_args()
    
    try:
        from claw_rl.core import LearningLoop
    except ImportError:
        print("❌ claw-rl not installed. Run: pip install claw-rl")
        sys.exit(1)
    
    loop = LearningLoop(workspace=args.workspace)
    rules = loop.get_rules(top_k=args.top_k, context=args.context)
    
    if not rules:
        print("No learned rules found")
        return
    
    print(f"📚 Learned Rules ({len(rules)}):\n")
    for i, rule in enumerate(rules, 1):
        priority = rule.get('priority', 'normal')
        content = rule.get('content', '')
        source = rule.get('source', 'unknown')
        print(f"{i}. [{priority}] {content}")
        print(f"   Source: {source}")
        print()

if __name__ == "__main__":
    main()
