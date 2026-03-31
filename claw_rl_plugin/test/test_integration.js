/**
 * Integration test for claw-rl Plugin
 * 
 * Tests the complete workflow: feedback collection → hint extraction → learning → rule injection
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
      
      const venvPython = path.resolve(__dirname, '..', '..', 'venv', 'bin', 'python3');
      const actualPython = fs.existsSync(venvPython) ? venvPython : pythonPath;
      
      const env = {
        ...process.env,
        PYTHONPATH: path.resolve(__dirname, '..', '..', 'src'),
        CLAW_RL_SILENT: '1'
      };
      
      console.log(`[test] Using Python: ${actualPython}`);
      
      this.process = spawn(actualPython, ['-m', bridgeModule], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.resolve(__dirname, '..', '..'),
        env: env,
      });
      
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
            // Ignore non-JSON output
          }
        }
      });
      
      this.process.stderr.on('data', (data) => {
        const msg = data.toString().trim();
        if (msg && !msg.includes('Starting v2.0.0') && !msg.includes('Python version')) {
          console.log(`[python] ${msg}`);
        }
      });
      
      this.process.on('exit', (code) => {
        this.process = null;
      });
      
      this.process.on('error', (err) => {
        reject(err);
      });
      
      // Initialize
      this.call('initialize', { workspace: path.resolve(__dirname, '..', '..') })
        .then((result) => {
          console.log(`[test] ✅ Bridge initialized (${result.latency_ms?.toFixed(3)}ms)\n`);
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
      const request = { jsonrpc: '2.0', method, params, id };
      
      this.pendingRequests.set(id, { resolve, reject });
      this.process.stdin.write(JSON.stringify(request) + '\n');
      
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error(`Timeout: ${method}`));
        }
      }, 30000);
    });
  }
  
  async stop() {
    if (this.process) {
      try {
        await this.call('shutdown');
      } catch (e) {}
      this.process.kill();
      this.process = null;
    }
  }
}

// Integration Tests
async function runIntegrationTests() {
  const client = new ClawRLBridgeClient();
  
  console.log('========================================');
  console.log('claw-rl Plugin Integration Tests');
  console.log('========================================\n');
  
  const testResults = [];
  
  try {
    // Initialize
    await client.start();
    
    // Test 1: Binary RL - Positive Feedback
    console.log('[Test 1] Binary RL - Positive Feedback');
    const posResult = await client.call('collect_feedback', {
      feedback: '很好，谢谢！',
      action: 'created_file'
    });
    console.log(`  Reward: ${posResult.reward}, Confidence: ${posResult.confidence}`);
    testResults.push({ name: 'Positive Feedback', pass: posResult.reward > 0 });
    
    // Test 2: Binary RL - Negative Feedback
    console.log('[Test 2] Binary RL - Negative Feedback');
    const negResult = await client.call('collect_feedback', {
      feedback: '不对，应该这样...',
      action: 'created_file'
    });
    console.log(`  Reward: ${negResult.reward}, Confidence: ${negResult.confidence}`);
    testResults.push({ name: 'Negative Feedback', pass: negResult.reward < 0 });
    
    // Test 3: OPD Hint Extraction
    console.log('[Test 3] OPD Hint - Extract from feedback');
    const hintResult = await client.call('extract_hint', {
      feedback: '不要用 var，应该用 const 或 let'
    });
    console.log(`  Hint extracted: ${hintResult.hint ? 'Yes' : 'No'}`);
    testResults.push({ name: 'Hint Extraction', pass: hintResult.status === 'success' });
    
    // Test 4: Get Rules
    console.log('[Test 4] Get Learned Rules');
    const rulesResult = await client.call('get_rules', { top_k: 5 });
    console.log(`  Rules count: ${rulesResult.count}`);
    testResults.push({ name: 'Get Rules', pass: rulesResult.status === 'success' });
    
    // Test 5: Process Learning
    console.log('[Test 5] Process Learning Signals');
    const learnResult = await client.call('process_learning', {});
    console.log(`  Status: ${learnResult.status}`);
    testResults.push({ name: 'Process Learning', pass: learnResult.status === 'success' });
    
    // Test 6: Status Check
    console.log('[Test 6] Status Check');
    const statusResult = await client.call('status', {});
    console.log(`  Components: BinaryRL=${statusResult.components?.binary_rl}, OPD=${statusResult.components?.opd_hint}, LearningLoop=${statusResult.components?.learning_loop}`);
    testResults.push({ name: 'Status Check', pass: statusResult.initialized });
    
    // Summary
    console.log('\n========================================');
    console.log('Test Results Summary');
    console.log('========================================');
    
    const passed = testResults.filter(r => r.pass).length;
    const total = testResults.length;
    
    testResults.forEach(r => {
      console.log(`  ${r.pass ? '✅' : '❌'} ${r.name}`);
    });
    
    console.log(`\nTotal: ${passed}/${total} passed`);
    
    if (passed === total) {
      console.log('\n🎉 All integration tests passed!\n');
    } else {
      console.log('\n⚠️ Some tests failed\n');
    }
    
    // Shutdown
    await client.stop();
    
  } catch (error) {
    console.error('❌ Test error:', error);
    await client.stop();
    process.exit(1);
  }
}

runIntegrationTests().catch(console.error);
