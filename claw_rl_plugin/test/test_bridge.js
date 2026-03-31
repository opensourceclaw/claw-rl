/**
 * Test script for claw-rl Plugin Bridge
 * 
 * Tests the JSON-RPC communication between TypeScript Plugin and Python Bridge
 */

import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class ClawRLBridgeClient {
  constructor() {
    this.process = null;
    this.requestId = 0;
    this.pendingRequests = new Map();
  }
  
  async start(pythonPath = 'python3', bridgeModule = 'claw_rl.bridge') {
    return new Promise((resolve, reject) => {
      console.log('[test] Starting Python Bridge...');
      
      // Use venv Python if available
      const venvPython = path.resolve(__dirname, '..', '..', 'venv', 'bin', 'python3');
      const actualPython = fs.existsSync(venvPython) ? venvPython : pythonPath;
      
      // Set PYTHONPATH to include src directory
      const env = {
        ...process.env,
        PYTHONPATH: path.resolve(__dirname, '..', '..', 'src'),
        CLAW_RL_SILENT: '1'
      };
      
      console.log(`[test] Using Python: ${actualPython}`);
      console.log(`[test] PYTHONPATH: ${env.PYTHONPATH}`);
      console.log(`[test] Bridge module: ${bridgeModule}`);
      
      // Spawn with separate arguments: python -m claw_rl.bridge
      this.process = spawn(actualPython, ['-m', bridgeModule], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.resolve(__dirname, '..', '..'),
        env: env,
      });
      
      // Handle stdout (responses)
      this.process.stdout.on('data', (data) => {
        const lines = data.toString().split('\n').filter(line => line.trim());
        for (const line of lines) {
          try {
            const response = JSON.parse(line);
            const pending = this.pendingRequests.get(response.id);
            if (pending) {
              this.pendingRequests.delete(response.id);
              if (response.error) {
                pending.reject(new Error(response.error.message));
              } else {
                pending.resolve(response.result);
              }
            }
          } catch (e) {
            console.error('[test] Parse error:', e.message);
          }
        }
      });
      
      // Handle stderr (logs)
      this.process.stderr.on('data', (data) => {
        const msg = data.toString().trim();
        if (msg) {
          console.log(`[python] ${msg}`);
        }
      });
      
      // Handle process exit
      this.process.on('exit', (code) => {
        console.log(`[test] Bridge exited with code ${code}`);
        this.process = null;
      });
      
      // Handle process error
      this.process.on('error', (err) => {
        console.error('[test] Bridge error:', err);
        reject(err);
      });
      
      // Initialize
      this.call('initialize', { workspace: path.resolve(__dirname, '..', '..') })
        .then((result) => {
          console.log(`  ✅ Bridge initialized`);
          console.log(`  Workspace: ${result.workspace}`);
          console.log(`  Latency: ${result.latency_ms?.toFixed(3)}ms\n`);
          resolve();
        })
        .catch(reject);
    });
  }
  
  async call(method, params = {}) {
    return new Promise((resolve, reject) => {
      if (!this.process || !this.process.stdin) {
        reject(new Error('Bridge not started'));
        return;
      }
      
      const id = ++this.requestId;
      const request = {
        jsonrpc: '2.0',
        method,
        params,
        id,
      };
      
      this.pendingRequests.set(id, { resolve, reject });
      
      // Send request
      this.process.stdin.write(JSON.stringify(request) + '\n');
      
      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error(`Timeout waiting for response to ${method}`));
        }
      }, 30000);
    });
  }
  
  async stop() {
    if (this.process) {
      try {
        await this.call('shutdown');
      } catch (e) {
        // Ignore shutdown errors
      }
      this.process.kill();
      this.process = null;
    }
  }
}

// Test functions
async function runTests() {
  const client = new ClawRLBridgeClient();
  
  console.log('========================================');
  console.log('claw-rl Plugin Bridge Test');
  console.log('========================================\n');
  
  try {
    // Test 1: Initialize
    console.log('[test] Initializing Bridge...');
    await client.start();
    
    // Test 2: Get Status
    console.log('[test] Getting status...');
    const status = await client.call('status');
    console.log(`  Initialized: ${status.initialized}`);
    console.log(`  Components: ${JSON.stringify(status.components)}\n`);
    
    // Test 3: Collect Feedback
    console.log('[test] Collecting feedback...');
    const feedback = await client.call('collect_feedback', {
      feedback: 'positive',
      context: { test: true }
    });
    console.log(`  Status: ${feedback.status}`);
    console.log(`  Latency: ${feedback.latency_ms?.toFixed(3)}ms\n`);
    
    // Test 4: Get Rules
    console.log('[test] Getting learned rules...');
    const rules = await client.call('get_rules', { top_k: 5 });
    console.log(`  Status: ${rules.status}`);
    console.log(`  Rules count: ${rules.count}`);
    console.log(`  Latency: ${rules.latency_ms?.toFixed(3)}ms\n`);
    
    // Test 5: Process Learning
    console.log('[test] Processing learning signals...');
    const learning = await client.call('process_learning');
    console.log(`  Status: ${learning.status}`);
    console.log(`  Latency: ${learning.latency_ms?.toFixed(3)}ms\n`);
    
    // Test 6: Shutdown
    console.log('[test] Shutting down...');
    const shutdown = await client.call('shutdown');
    console.log(`  Status: ${shutdown.status}`);
    console.log(`  Total requests: ${shutdown.total_requests}`);
    console.log(`  Average latency: ${shutdown.avg_latency_ms?.toFixed(3)}ms\n`);
    
    console.log('========================================');
    console.log('✅ All tests passed!');
    console.log('========================================\n');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    await client.stop();
    process.exit(1);
  }
  
  await client.stop();
}

// Run tests
runTests().catch(console.error);
