import { ClawRLBridge, LearnedRule } from '../bridge.js';

export interface SessionStartResult {
  type: 'context_injection';
  content: string;
  rules?: LearnedRule[];
}

/**
 * SessionStartHook: Inject learned rules at session start
 * 
 * This hook runs when Claude Code starts a new session.
 * It retrieves learned rules and injects them as context.
 */
export async function SessionStartHook(): Promise<SessionStartResult> {
  const bridge = new ClawRLBridge();
  
  // Check installation
  const installCheck = await bridge.checkInstallation();
  if (!installCheck.installed) {
    console.error(`⚠️  ${installCheck.error}`);
    return {
      type: 'context_injection',
      content: ''
    };
  }

  // Get learned rules
  const rules = await bridge.getRules({ topK: 10 });

  if (rules.length === 0) {
    return {
      type: 'context_injection',
      content: ''
    };
  }

  // Format rules for injection
  const formattedRules = formatRules(rules);

  return {
    type: 'context_injection',
    content: formattedRules,
    rules
  };
}

/**
 * Format rules for Claude context
 */
function formatRules(rules: LearnedRule[]): string {
  const lines: string[] = [
    '# 📚 Learned Rules',
    '',
    'Based on past interactions, follow these guidelines:',
    ''
  ];

  // Group by category
  const byCategory: Record<string, LearnedRule[]> = {};
  rules.forEach(rule => {
    if (!byCategory[rule.category]) {
      byCategory[rule.category] = [];
    }
    byCategory[rule.category].push(rule);
  });

  // Format each category
  Object.entries(byCategory).forEach(([category, categoryRules]) => {
    const categoryTitle = category.charAt(0).toUpperCase() + category.slice(1);
    lines.push(`## ${categoryTitle}`);
    categoryRules.forEach(rule => {
      lines.push(`- ${rule.content}`);
    });
    lines.push('');
  });

  lines.push('---');
  lines.push('*These rules were learned from user feedback. They may be overridden by explicit instructions.*');

  return lines.join('\n');
}
