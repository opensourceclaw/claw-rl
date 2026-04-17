#!/usr/bin/env python3
"""
Bridge entry point - redirects to core.bridge

This module provides a short alias for claw_rl.core.bridge.main
to support OpenClaw's bridge loading mechanism.
"""

from claw_rl.core.bridge import main

__all__ = ['main']

if __name__ == '__main__':
    main()
