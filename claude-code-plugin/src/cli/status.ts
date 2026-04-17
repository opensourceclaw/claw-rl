#!/usr/bin/env node

import { ClawRLBridge } from '../bridge.js';

async function main() {
  const bridge = new ClawRLBridge();
  
  // Check installation
  const check = await bridge.checkInstallation();
  if (!check.installed) {
    console.error(`Error: ${check.error}`);
    process.exit(1);
  }
  
  // Get status
  const status = await bridge.getStatus();
  
  console.log('📊 claw-rl Learning Status\n');
  console.log(`  Rules learned: ${status.rulesCount}`);
  console.log(`  Pending feedback: ${status.pendingFeedback}`);
  console.log(`  Daemon running: ${status.daemonRunning ? 'Yes' : 'No'}`);
  console.log(`  Version: ${check.version}`);
}

main().catch(console.error);
