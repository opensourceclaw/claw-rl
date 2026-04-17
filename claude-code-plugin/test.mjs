#!/usr/bin/env node

import { ClawRLBridge } from './dist/bridge.js';

async function main() {
  console.log('🧪 Testing claw-rl Claude Code Plugin\n');
  
  const bridge = new ClawRLBridge();
  
  // Test 1: Check installation
  console.log('Test 1: Check installation');
  const check = await bridge.checkInstallation();
  console.log(`  Installed: ${check.installed}`);
  if (check.version) console.log(`  Version: ${check.version}`);
  console.log();
  
  // Test 2: Collect positive feedback
  console.log('Test 2: Collect positive feedback');
  const posResult = await bridge.collectFeedback({
    type: 'positive',
    content: 'Thanks, that was helpful!',
    action: 'explain'
  });
  console.log(`  Reward: ${posResult.reward.toFixed(2)}`);
  console.log(`  Confidence: ${(posResult.confidence * 100).toFixed(0)}%`);
  console.log();
  
  // Test 3: Collect negative feedback
  console.log('Test 3: Collect negative feedback');
  const negResult = await bridge.collectFeedback({
    type: 'negative',
    content: 'Not what I wanted, use Chinese instead',
    action: 'explain'
  });
  console.log(`  Reward: ${negResult.reward.toFixed(2)}`);
  console.log(`  Confidence: ${(negResult.confidence * 100).toFixed(0)}%`);
  console.log();
  
  // Test 4: Extract hint
  console.log('Test 4: Extract hint');
  const hint = await bridge.extractHint('Not what I wanted, use Chinese instead');
  console.log(`  Hint: ${hint || 'None'}`);
  console.log();
  
  // Test 5: Get status
  console.log('Test 5: Get status');
  const status = await bridge.getStatus();
  console.log(`  Rules count: ${status.rulesCount}`);
  console.log();
  
  console.log('✅ Tests completed');
}

main().catch(console.error);
