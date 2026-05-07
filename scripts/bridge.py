#!/usr/bin/env python3
"""
claw-rl Bridge - stdio JSON-RPC Server for OpenClaw Plugin

Purpose:
- Receive JSON-RPC requests from TypeScript Plugin via stdin
- Route to claw-rl Python Core
- Return responses via stdout

Protocol: JSON-RPC 2.0

Architecture:
    OpenClaw Plugin (TypeScript)
        ↓ spawn + stdio JSON-RPC
    claw-rl Bridge (Python)
        ↓ Python Function Call
    claw-rl Core (BinaryRLJudge, OPDHintExtractor, LearningLoop)
"""

import sys
import json
import asyncio
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set silent mode to suppress stdout logs from modules
import os
os.environ['CLAW_RL_SILENT'] = '1'

from claw_rl.core.bridge import ClawRLBridge

def main():
    """Main entry point"""
    bridge = ClawRLBridge()
    asyncio.run(bridge.run())

if __name__ == '__main__':
    main()
