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

import os
import sys
import json
import asyncio
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

# Set silent mode to suppress stdout logs from modules
os.environ['CLAW_RL_SILENT'] = '1'

from claw_rl.feedback.binary_rl import BinaryRLJudge
from claw_rl.feedback.opd_hint import OPDHintExtractor
from claw_rl.core.learning_loop import LearningLoop


class ClawRLBridge:
    """JSON-RPC Bridge for claw-rl"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.binary_rl: Optional[BinaryRLJudge] = None
        self.opd_hint: Optional[OPDHintExtractor] = None
        self.learning_loop: Optional[LearningLoop] = None
        self.running = True
        self.request_count = 0
        self.total_latency = 0.0
        self.initialized = False
        self.workspace: Optional[str] = None
    
    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the bridge with config"""
        start_time = time.time()
        
        self.workspace = params.get('workspace', os.getcwd())
        
        try:
            # Initialize components
            self.binary_rl = BinaryRLJudge()
            self.opd_hint = OPDHintExtractor()
            self.learning_loop = LearningLoop(data_dir=Path(self.workspace) / 'data' / 'claw-rl')
            
            self.initialized = True
            latency = (time.time() - start_time) * 1000
            
            return {
                'status': 'success',
                'workspace': self.workspace,
                'latency_ms': latency
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def get_status(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get bridge status"""
        return {
            'initialized': self.initialized,
            'request_count': self.request_count,
            'avg_latency_ms': self.total_latency / max(1, self.request_count),
            'components': {
                'binary_rl': self.binary_rl is not None,
                'opd_hint': self.opd_hint is not None,
                'learning_loop': self.learning_loop is not None
            }
        }
    
    async def collect_feedback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Collect user feedback signal"""
        if not self.initialized:
            return {'error': 'Bridge not initialized'}
        
        start_time = time.time()
        
        try:
            feedback = params.get('feedback', '')
            action = params.get('action')
            
            # Use BinaryRLJudge.judge() method
            reward, confidence = self.binary_rl.judge(feedback=feedback, action=action)
            
            latency = (time.time() - start_time) * 1000
            self.request_count += 1
            self.total_latency += latency
            
            return {
                'status': 'success',
                'reward': reward,
                'confidence': confidence,
                'latency_ms': latency
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def extract_hint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract improvement hint from user feedback"""
        if not self.initialized:
            return {'error': 'Bridge not initialized'}
        
        start_time = time.time()
        
        try:
            feedback = params.get('feedback', '')
            
            # Use OPDHintExtractor.extract() method
            hint = self.opd_hint.extract(feedback=feedback)
            
            latency = (time.time() - start_time) * 1000
            self.request_count += 1
            self.total_latency += latency
            
            if hint:
                return {
                    'status': 'success',
                    'hint': hint.to_dict() if hasattr(hint, 'to_dict') else str(hint),
                    'latency_ms': latency
                }
            else:
                return {
                    'status': 'success',
                    'hint': None,
                    'latency_ms': latency
                }
        except Exception as e:
            return {'error': str(e)}
    
    async def get_rules(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get learned rules for injection"""
        if not self.initialized:
            return {'error': 'Bridge not initialized'}
        
        start_time = time.time()
        
        try:
            limit = params.get('top_k', 10)
            
            # Use LearningLoop.get_recent_learnings() method
            learnings = self.learning_loop.get_recent_learnings(limit=limit)
            
            # Convert to rules format
            rules = []
            if learnings:
                for learning in learnings:
                    if isinstance(learning, dict):
                        rules.append({
                            'content': learning.get('hint', str(learning)),
                            'score': learning.get('score', 1.0)
                        })
                    else:
                        rules.append({
                            'content': str(learning),
                            'score': 1.0
                        })
            
            latency = (time.time() - start_time) * 1000
            self.request_count += 1
            self.total_latency += latency
            
            return {
                'status': 'success',
                'rules': rules,
                'count': len(rules),
                'latency_ms': latency
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def process_learning(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process learning signals"""
        if not self.initialized:
            return {'error': 'Bridge not initialized'}
        
        start_time = time.time()
        
        try:
            # Get statistics as a simple process operation
            stats = self.learning_loop.get_statistics()
            
            latency = (time.time() - start_time) * 1000
            self.request_count += 1
            self.total_latency += latency
            
            return {
                'status': 'success',
                'statistics': stats,
                'latency_ms': latency
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def shutdown(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Shutdown bridge"""
        self.running = False
        
        avg_latency = self.total_latency / max(1, self.request_count)
        
        return {
            'status': 'success',
            'total_requests': self.request_count,
            'avg_latency_ms': avg_latency
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC request"""
        method = request.get('method', '')
        params = request.get('params', {})
        request_id = request.get('id')
        
        handlers = {
            'initialize': self.initialize,
            'status': self.get_status,
            'collect_feedback': self.collect_feedback,
            'extract_hint': self.extract_hint,
            'get_rules': self.get_rules,
            'process_learning': self.process_learning,
            'shutdown': self.shutdown,
        }
        
        handler = handlers.get(method)
        if not handler:
            return {
                'jsonrpc': '2.0',
                'error': {'code': -32601, 'message': f'Method not found: {method}'},
                'id': request_id
            }
        
        try:
            result = await handler(params)
            return {
                'jsonrpc': '2.0',
                'result': result,
                'id': request_id
            }
        except Exception as e:
            return {
                'jsonrpc': '2.0',
                'error': {'code': -32603, 'message': str(e)},
                'id': request_id
            }
    
    async def run(self):
        """Run the bridge (stdio JSON-RPC server)"""
        print('[claw-rl bridge] Starting v2.0.0...', file=sys.stderr)
        print(f'[claw-rl bridge] Python version: {sys.version}', file=sys.stderr)
        
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Read line from stdin
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse JSON-RPC request
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f'[claw-rl bridge] JSON parse error: {e}', file=sys.stderr)
                    continue
                
                # Handle request
                response = await self.handle_request(request)
                
                # Send response
                print(json.dumps(response), flush=True)
                
            except Exception as e:
                print(f'[claw-rl bridge] Error: {e}', file=sys.stderr)
        
        print('[claw-rl bridge] Shutting down...', file=sys.stderr)
        print(f'[claw-rl bridge] Total requests: {self.request_count}', file=sys.stderr)
        if self.request_count > 0:
            avg_latency = self.total_latency / self.request_count
            print(f'[claw-rl bridge] Average latency: {avg_latency:.3f}ms', file=sys.stderr)


def main():
    """Main entry point"""
    bridge = ClawRLBridge()
    asyncio.run(bridge.run())


if __name__ == '__main__':
    main()
