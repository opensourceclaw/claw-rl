#!/usr/bin/env python3
"""Collect user feedback for learning"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Collect feedback for claw-rl")
    parser.add_argument("feedback", help="User feedback text")
    parser.add_argument("--action", "-a", default="general", help="Action that triggered feedback")
    parser.add_argument("--negative", "-n", action="store_true", help="Mark as negative feedback")
    parser.add_argument("--workspace", "-w", default="~/.openclaw/workspace", help="Workspace path")
    args = parser.parse_args()
    
    try:
        from claw_rl import BinaryRLJudge, OPDHintExtractor
        from claw_rl.core import LearningLoop
    except ImportError:
        print("❌ claw-rl not installed. Run: pip install claw-rl")
        sys.exit(1)
    
    # Evaluate feedback
    judge = BinaryRLJudge()
    signal = "negative" if args.negative else "positive"
    result = judge.judge(args.feedback, signal)
    
    # Extract hint if negative
    if args.negative:
        extractor = OPDHintExtractor()
        hint = extractor.extract(args.feedback)
        if hint:
            print(f"💡 Extracted hint: {hint.content}")
    
    print(f"📊 Feedback signal: {signal}")
    print(f"📈 Confidence: {result.confidence:.2f}")
    
    # Queue for learning
    loop = LearningLoop(workspace=args.workspace)
    loop.queue_feedback(args.feedback, signal, args.action)
    print("✅ Feedback queued for learning")

if __name__ == "__main__":
    main()
