import { ClawRLBridge } from '../bridge.js';

export interface SessionEndContext {
  duration: number;
  messageCount: number;
  feedbackCount?: number;
}

export interface SessionEndResult {
  processed: boolean;
  rulesCount?: number;
}

/**
 * SessionEndHook: Log session summary
 * 
 * This hook runs at the end of a Claude Code session.
 * It logs session statistics for learning.
 */
export async function SessionEndHook(
  context: SessionEndContext
): Promise<SessionEndResult> {
  const bridge = new ClawRLBridge();

  // Get current status
  const status = await bridge.getStatus();

  // Log summary
  const duration = Math.round(context.duration / 60000); // minutes
  console.log(`📊 Session ended:`);
  console.log(`   Duration: ${duration} minutes`);
  console.log(`   Messages: ${context.messageCount}`);
  console.log(`   Learned rules: ${status.rulesCount}`);

  return {
    processed: true,
    rulesCount: status.rulesCount
  };
}
