import { ClawRLBridge, FeedbackSignal } from '../bridge.js';

export interface ToolUseResult {
  tool: string;
  input: Record<string, any>;
  output: any;
  success: boolean;
}

export interface PostToolUseResult {
  collected: boolean;
  hint?: string;
  reward?: number;
}

/**
 * PostToolUseHook: Collect feedback and extract hints
 * 
 * This hook looks for user feedback signals in the conversation
 * and collects them for learning.
 */
export async function PostToolUseHook(
  result: ToolUseResult,
  userMessage?: string
): Promise<PostToolUseResult> {
  const bridge = new ClawRLBridge();

  // If user message provided, check for feedback
  if (!userMessage) {
    return { collected: false };
  }

  // Classify feedback
  const signal = classifyFeedback(userMessage);
  
  if (signal.type === 'neutral') {
    return { collected: false };
  }

  // Collect feedback
  const feedbackResult = await bridge.collectFeedback({
    ...signal,
    action: result.tool
  });

  // If negative, extract improvement hint
  if (signal.type === 'negative') {
    const hint = await bridge.extractHint(userMessage);
    
    if (hint) {
      console.log(`💡 Learned: ${hint}`);
    }
    
    return {
      collected: true,
      hint: hint || undefined,
      reward: feedbackResult.reward
    };
  }

  return { 
    collected: true,
    reward: feedbackResult.reward
  };
}

/**
 * Classify user message as feedback signal
 */
function classifyFeedback(message: string): FeedbackSignal {
  const lowerMessage = message.toLowerCase();
  
  // Positive signals
  const positivePatterns = [
    /thank(s| you)/,
    /great|good|excellent|perfect/,
    /👍|😊|✅/,
    /that'?s (exactly )?what i (needed|wanted)/,
    /worked perfectly/,
    /nice|awesome|amazing/
  ];
  
  // Negative signals
  const negativePatterns = [
    /wrong|incorrect|error|mistake/,
    /not what i (wanted|needed|meant)/,
    /try again|do it (differently|again)/,
    /👎|😠|❌/,
    /don'?t|do not/,
    /instead|rather|should be/,
    /no,? (use|try|make)/
  ];

  for (const pattern of positivePatterns) {
    if (pattern.test(lowerMessage)) {
      return { type: 'positive', content: message };
    }
  }

  for (const pattern of negativePatterns) {
    if (pattern.test(lowerMessage)) {
      return { type: 'negative', content: message };
    }
  }

  return { type: 'neutral', content: message };
}
