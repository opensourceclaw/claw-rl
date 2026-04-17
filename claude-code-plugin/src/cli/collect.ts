#!/usr/bin/env node

import { ClawRLBridge } from '../bridge.js';

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('Usage: claw-rl-collect <feedback> [--action <action>]');
    process.exit(1);
  }
  
  // Parse arguments
  let feedback = '';
  let action = '';
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--action' && args[i + 1]) {
      action = args[i + 1];
      i++;
    } else if (!args[i].startsWith('--')) {
      feedback = feedback ? `${feedback} ${args[i]}` : args[i];
    }
  }
  
  if (!feedback) {
    console.error('Error: No feedback provided');
    process.exit(1);
  }
  
  const bridge = new ClawRLBridge();
  
  // Check installation
  const check = await bridge.checkInstallation();
  if (!check.installed) {
    console.error(`Error: ${check.error}`);
    process.exit(1);
  }
  
  // Collect feedback
  const result = await bridge.collectFeedback({
    type: feedback.toLowerCase().includes('not') || feedback.toLowerCase().includes('wrong') 
      ? 'negative' 
      : 'positive',
    content: feedback,
    action
  });
  
  console.log(`✅ Feedback collected`);
  console.log(`   Reward: ${result.reward.toFixed(2)}`);
  console.log(`   Confidence: ${(result.confidence * 100).toFixed(0)}%`);
  
  // Extract hint if negative
  if (feedback.toLowerCase().includes('not') || feedback.toLowerCase().includes('wrong')) {
    const hint = await bridge.extractHint(feedback);
    if (hint) {
      console.log(`💡 Learned: ${hint}`);
    }
  }
}

main().catch(console.error);
