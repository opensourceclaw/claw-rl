import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface LearnedRule {
  id: string;
  content: string;
  category: string;
  confidence: number;
  createdAt: string;
}

export interface FeedbackSignal {
  type: 'positive' | 'negative' | 'neutral';
  content: string;
  action?: string;
}

export interface FeedbackResult {
  reward: number;
  confidence: number;
}

export interface LearningStatus {
  rulesCount: number;
  pendingFeedback: number;
  lastLearningTime: string;
  daemonRunning: boolean;
}

export class ClawRLBridge {
  private pythonPath: string;
  private workspaceDir: string;

  constructor(options?: { pythonPath?: string; workspaceDir?: string }) {
    this.pythonPath = options?.pythonPath || process.env.CLAW_RL_PYTHON || 'python3';
    this.workspaceDir = options?.workspaceDir || process.env.CLAW_RL_WORKSPACE || '~/.openclaw/workspace';
  }

  /**
   * Get learned rules for injection
   */
  async getRules(options?: { topK?: number; context?: string }): Promise<LearnedRule[]> {
    const { topK = 10 } = options || {};
    
    try {
      const { stdout } = await execAsync(
        `${this.pythonPath} -c "
import sys
import os
import json
os.environ['CLAW_RL_SILENT'] = '1'

from pathlib import Path
from claw_rl.core.learning_loop import LearningLoop

workspace = Path('${this.workspaceDir}').expanduser()
loop = LearningLoop(data_dir=workspace / 'data' / 'claw-rl')
rules = loop.get_rules(limit=${topK})
output = [{'id': r.get('id', ''), 'content': r.get('content', ''), 'category': r.get('category', 'general'), 'confidence': r.get('confidence', 0.5), 'createdAt': r.get('created_at', '')} for r in rules]
print(json.dumps(output))
"`,
        { maxBuffer: 1024 * 1024, timeout: 30000 }
      );
      return JSON.parse(stdout);
    } catch (error: any) {
      console.error('Get rules failed:', error.message);
      return [];
    }
  }

  /**
   * Collect feedback for learning
   */
  async collectFeedback(signal: FeedbackSignal): Promise<FeedbackResult> {
    try {
      const { stdout } = await execAsync(
        `${this.pythonPath} -c "
import sys
import os
import json
os.environ['CLAW_RL_SILENT'] = '1'

from claw_rl.feedback.binary_rl import BinaryRLJudge

judge = BinaryRLJudge()
reward, confidence = judge.judge(feedback='${signal.content.replace(/'/g, "\\'")}', action='${signal.action || ''}')
print(json.dumps({'reward': reward, 'confidence': confidence}))
"`,
        { timeout: 10000 }
      );
      return JSON.parse(stdout);
    } catch (error: any) {
      console.error('Collect feedback failed:', error.message);
      return { reward: 0, confidence: 0 };
    }
  }

  /**
   * Extract improvement hint from correction
   */
  async extractHint(correction: string): Promise<string | null> {
    try {
      const { stdout } = await execAsync(
        `${this.pythonPath} -c "
import sys
import os
import json
os.environ['CLAW_RL_SILENT'] = '1'

from claw_rl.feedback.opd_hint import OPDHintExtractor

extractor = OPDHintExtractor()
hint = extractor.extract(feedback='${correction.replace(/'/g, "\\'")}')
if hint:
    result = hint.to_dict() if hasattr(hint, 'to_dict') else str(hint)
    print(json.dumps(result))
else:
    print(json.dumps(None))
"`,
        { timeout: 10000 }
      );
      const result = JSON.parse(stdout);
      return result ? (typeof result === 'string' ? result : result.content || result.hint || JSON.stringify(result)) : null;
    } catch (error: any) {
      console.error('Extract hint failed:', error.message);
      return null;
    }
  }

  /**
   * Get learning status
   */
  async getStatus(): Promise<LearningStatus> {
    try {
      const { stdout } = await execAsync(
        `${this.pythonPath} -c "
import sys
import os
import json
os.environ['CLAW_RL_SILENT'] = '1'

from pathlib import Path
from claw_rl.core.learning_loop import LearningLoop

workspace = Path('${this.workspaceDir}').expanduser()
loop = LearningLoop(data_dir=workspace / 'data' / 'claw-rl')
rules = loop.get_rules(limit=1000)
print(json.dumps({'rulesCount': len(rules), 'pendingFeedback': 0, 'lastLearningTime': '', 'daemonRunning': False}))
"`,
        { timeout: 10000 }
      );
      return JSON.parse(stdout);
    } catch (error) {
      return { rulesCount: 0, pendingFeedback: 0, lastLearningTime: '', daemonRunning: false };
    }
  }

  /**
   * Check installation
   */
  async checkInstallation(): Promise<{ installed: boolean; version?: string; error?: string }> {
    try {
      const { stdout } = await execAsync(
        `${this.pythonPath} -c "import claw_rl; print(getattr(claw_rl, '__version__', 'unknown'))"`,
        { timeout: 5000 }
      );
      return { installed: true, version: stdout.trim() };
    } catch (error: any) {
      return {
        installed: false,
        error: 'claw-rl Python package not found. Run: pip install git+https://github.com/opensourceclaw/claw-rl.git'
      };
    }
  }
}
