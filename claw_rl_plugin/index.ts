/**
 * claw-rl Plugin for OpenClaw
 * 
 * Architecture: Local-First
 * - TypeScript Plugin spawns Python Bridge process
 * - Communication via stdio JSON-RPC
 * - Zero network overhead
 * - Minimal latency (<10ms)
 * 
 * @packageDocumentation
 */

import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Plugin configuration
 */
interface ClawRLConfig {
  pythonPath?: string;
  bridgePath?: string;
  workspaceDir?: string;
  autoInject?: boolean;
  autoLearn?: boolean;
  topK?: number;
  debug?: boolean;
}

/**
 * JSON-RPC Request
 */
interface JSONRPCRequest {
  jsonrpc: '2.0';
  method: string;
  params?: any;
  id?: number | string;
}

/**
 * JSON-RPC Response
 */
interface JSONRPCResponse {
  jsonrpc: '2.0';
  result?: any;
  error?: { code: number; message: string; data?: any };
  id?: number | string;
}

/**
 * OpenClaw Plugin API (minimal interface)
 */
interface OpenClawPluginApi {
  id: string;
  name: string;
  version?: string;
  description?: string;
  source: string;
  rootDir?: string;
  config: any;
  pluginConfig?: Record<string, unknown>;
  logger: {
    info: (...args: any[]) => void;
    error: (...args: any[]) => void;
    warn: (...args: any[]) => void;
    debug: (...args: any[]) => void;
  };
  
  registerTool(tool: any, handler: (params: any) => Promise<any>): void;
  on(eventName: string, handler: (event: any, ctx: any) => Promise<any | void>): void;
  registerService(service: { id: string; start: () => Promise<void>; stop: () => Promise<void> }): void;
  registerContextEngine(id: string, factory: () => any | Promise<any>): void;
}

/**
 * Plugin Definition
 */
interface PluginDefinition {
  id?: string;
  name?: string;
  description?: string;
  version?: string;
  kind?: 'context-engine';
  configSchema?: any;
  register?: (api: OpenClawPluginApi) => void | Promise<void>;
}

// ============================================================================
// ClawRLBridge - Python Bridge Client
// ============================================================================

/**
 * Bridge client for communicating with Python Bridge
 */
class ClawRLBridge {
  private process: ChildProcess | null = null;
  private requestId = 0;
  private pendingRequests = new Map<number | string, {
    resolve: (value: any) => void;
    reject: (error: Error) => void;
  }>();
  private ready = false;
  private starting = false;
  private logger: OpenClawPluginApi['logger'];
  
  constructor(
    private config: ClawRLConfig,
    logger: OpenClawPluginApi['logger']
  ) {
    this.logger = logger;
  }
  
  /**
   * Check if bridge is ready
   */
  isReady(): boolean {
    return this.ready;
  }
  
  /**
   * Start the bridge
   */
  async start(): Promise<void> {
    if (this.process || this.starting) {
      return;
    }
    
    this.starting = true;
    
    return new Promise((resolve, reject) => {
      const pythonPath = this.config.pythonPath || 'python3';
      const bridgeModule = 'claw_rl.bridge';  // Module name, not path
      
      if (this.config.debug) {
        this.logger.info(`[claw-rl bridge] Starting with ${pythonPath} -m ${bridgeModule}`);
      }
      
      // Set PYTHONPATH to include src directory
      const workspaceDir = this.config.workspaceDir || process.cwd();
      const srcDir = path.join(workspaceDir, 'src');
      
      // Spawn Python Bridge process with separate arguments
      this.process = spawn(pythonPath, ['-m', bridgeModule], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: workspaceDir,
        env: {
          ...process.env,
          PYTHONPATH: srcDir,
          CLAW_RL_SILENT: '1',
        },
      });
      
      // Handle stdout (responses)
      this.process.stdout?.on('data', (data: Buffer) => {
        const lines = data.toString().split('\n').filter(line => line.trim());
        
        for (const line of lines) {
          try {
            const response: JSONRPCResponse = JSON.parse(line);
            const pending = this.pendingRequests.get(response.id!);
            
            if (pending) {
              this.pendingRequests.delete(response.id!);
              
              if (response.error) {
                pending.reject(new Error(response.error.message));
              } else {
                pending.resolve(response.result);
              }
            }
          } catch (e) {
            this.logger.error('[claw-rl bridge] Failed to parse response:', e);
          }
        }
      });
      
      // Handle stderr (logs)
      this.process.stderr?.on('data', (data: Buffer) => {
        const msg = data.toString().trim();
        if (msg) {
          this.logger.info(`[claw-rl bridge] ${msg}`);
        }
      });
      
      // Handle process exit
      this.process.on('exit', (code) => {
        this.logger.info(`[claw-rl bridge] exited with code ${code}`);
        this.process = null;
        this.ready = false;
        this.starting = false;
      });
      
      // Handle process error
      this.process.on('error', (err) => {
        this.logger.error('[claw-rl bridge] Process error:', err);
        this.process = null;
        this.ready = false;
        this.starting = false;
        reject(err);
      });
      
      // Initialize bridge
      this.call('initialize', { workspace: workspaceDir })
        .then(() => {
          this.ready = true;
          this.starting = false;
          this.logger.info('[claw-rl bridge] Started successfully');
          resolve();
        })
        .catch((err) => {
          this.logger.error('[claw-rl bridge] Failed to initialize:', err);
          this.starting = false;
          reject(err);
        });
    });
  }
  
  /**
   * Call a method on the bridge
   */
  async call(method: string, params?: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.process || !this.process.stdin) {
        reject(new Error('Bridge not started'));
        return;
      }
      
      const id = ++this.requestId;
      const request: JSONRPCRequest = {
        jsonrpc: '2.0',
        method,
        params,
        id,
      };
      
      this.pendingRequests.set(id, { resolve, reject });
      
      // Send request
      const requestStr = JSON.stringify(request) + '\n';
      this.process.stdin.write(requestStr);
      
      if (this.config.debug) {
        this.logger.debug(`[claw-rl bridge] → ${requestStr.trim()}`);
      }
      
      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error(`Timeout waiting for response to ${method}`));
        }
      }, 30000);
    });
  }
  
  /**
   * Stop the bridge
   */
  async stop(): Promise<void> {
    if (this.process) {
      try {
        await this.call('shutdown');
      } catch (e) {
        // Ignore shutdown errors
      }
      
      this.process.kill();
      this.process = null;
      this.ready = false;
    }
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Extract feedback from event
 */
function extractFeedbackFromEvent(event: any): { feedback: string; context: any } | null {
  // Extract from message content
  if (event?.message?.content) {
    const content = event.message.content.toLowerCase();
    
    // Explicit feedback
    if (content.includes('👍') || content.includes('good') || content.includes('thanks')) {
      return { feedback: 'positive', context: event };
    }
    if (content.includes('👎') || content.includes('bad') || content.includes('wrong')) {
      return { feedback: 'negative', context: event };
    }
    
    // Implicit feedback (correction)
    if (content.includes('no,') || content.includes('actually,') || content.includes('instead,')) {
      return { feedback: 'correction', context: event };
    }
  }
  
  return null;
}

/**
 * Format rules for injection
 */
function formatRulesForInjection(rules: any[]): string {
  if (!rules || rules.length === 0) {
    return '';
  }
  
  const lines = ['Learned rules from previous sessions:'];
  for (const rule of rules) {
    if (rule.content) {
      lines.push(`- ${rule.content}`);
    }
  }
  return lines.join('\n');
}

// ============================================================================
// Plugin Definition
// ============================================================================

const plugin: PluginDefinition = {
  id: 'claw-rl',
  name: 'claw-rl Self-Improvement System',
  description: 'Reinforcement learning system for OpenClaw agents (Local-First)',
  version: '2.0.0',
  kind: 'context-engine',
  
  configSchema: {
    type: 'object',
    properties: {
      pythonPath: { type: 'string' },
      bridgePath: { type: 'string' },
      workspaceDir: { type: 'string' },
      autoInject: { type: 'boolean', default: true },
      autoLearn: { type: 'boolean', default: true },
      topK: { type: 'number', default: 10 },
      debug: { type: 'boolean', default: false },
    },
  },
  
  register(api: OpenClawPluginApi) {
    const config: ClawRLConfig = {
      pythonPath: api.pluginConfig?.pythonPath as string | undefined,
      bridgePath: api.pluginConfig?.bridgePath as string | undefined,
      workspaceDir: (api.pluginConfig?.workspaceDir as string | undefined) || api.config?.workspaceDir,
      autoInject: (api.pluginConfig?.autoInject as boolean | undefined) ?? true,
      autoLearn: (api.pluginConfig?.autoLearn as boolean | undefined) ?? true,
      topK: (api.pluginConfig?.topK as number | undefined) ?? 10,
      debug: (api.pluginConfig?.debug as boolean | undefined) ?? false,
    };
    
    const bridge = new ClawRLBridge(config, api.logger);
    let currentSessionId: string | undefined;
    
    // ========================================================================
    // Register Tools
    // ========================================================================
    
    api.registerTool(
      {
        name: 'learning_status',
        label: 'Learning Status',
        description: 'Get the current status of the learning system.',
        parameters: {
          type: 'object',
          properties: {},
        },
      },
      async (params: any) => {
        if (!bridge.isReady()) {
          return { error: 'Bridge not initialized' };
        }
        
        try {
          const result = await bridge.call('status');
          return result;
        } catch (error) {
          api.logger.error('[claw-rl] Status error:', error);
          return { error: (error as Error).message };
        }
      }
    );
    
    api.registerTool(
      {
        name: 'collect_feedback',
        label: 'Collect Feedback',
        description: 'Collect user feedback signal for learning.',
        parameters: {
          type: 'object',
          properties: {
            feedback: { type: 'string', description: 'Feedback type: positive, negative, or correction' },
            context: { type: 'object', description: 'Context of the feedback' },
          },
          required: ['feedback'],
        },
      },
      async (params: any) => {
        if (!bridge.isReady()) {
          return { error: 'Bridge not initialized' };
        }
        
        try {
          const result = await bridge.call('collect_feedback', params);
          return result;
        } catch (error) {
          api.logger.error('[claw-rl] Collect feedback error:', error);
          return { error: (error as Error).message };
        }
      }
    );
    
    api.registerTool(
      {
        name: 'get_learned_rules',
        label: 'Get Learned Rules',
        description: 'Get learned rules for injection into context.',
        parameters: {
          type: 'object',
          properties: {
            top_k: { type: 'number', description: 'Max rules to return', default: config.topK },
            context: { type: 'string', description: 'Context for rule selection' },
          },
        },
      },
      async (params: any) => {
        if (!bridge.isReady()) {
          return { error: 'Bridge not initialized' };
        }
        
        try {
          const result = await bridge.call('get_rules', params);
          return result;
        } catch (error) {
          api.logger.error('[claw-rl] Get rules error:', error);
          return { error: (error as Error).message };
        }
      }
    );
    
    // ========================================================================
    // Register Hooks
    // ========================================================================
    
    // Auto-inject: inject learned rules before session starts
    if (config.autoInject) {
      api.on('session_start', async (event: any, ctx: any) => {
        currentSessionId = ctx.sessionKey;

        try {
          // Get learned rules
          const result = await bridge.call('get_rules', {
            top_k: config.topK,
            context: event?.message?.content || '',
          });

          // Note: session_start hook does not support injection
          // Rules will be injected via Context Engine assemble()
          if (result.rules && result.rules.length > 0) {
            api.logger.info(`[claw-rl] Loaded ${result.rules.length} rules for session`);
          }
        } catch (error) {
          api.logger.error('[claw-rl] Auto-inject error:', error);
        }
      });
    }
    
    // Auto-learn: collect feedback after messages
    if (config.autoLearn) {
      api.on('message_received', async (event: any, ctx: any) => {
        // Extract feedback from event
        const feedbackData = extractFeedbackFromEvent(event);
        
        if (feedbackData) {
          try {
            await bridge.call('collect_feedback', feedbackData);
          } catch (error) {
            api.logger.error('[claw-rl] Auto-learn error:', error);
          }
        }
      });
      
      // Process learning at session end
      api.on('session_end', async (event: any, ctx: any) => {
        try {
          await bridge.call('process_learning');
        } catch (error) {
          api.logger.error('[claw-rl] Process learning error:', error);
        }
      });
    }
    
    // ========================================================================
    // Lifecycle
    // ========================================================================
    
    // Start bridge
    bridge.start().catch((err) => {
      api.logger.error('[claw-rl] Failed to start bridge:', err);
    });
    
    // Register service for lifecycle
    api.registerService({
      id: 'claw-rl',
      start: async () => {
        api.logger.info('[claw-rl] Service started (local-first mode)');
      },
      stop: async () => {
        await bridge.stop();
        api.logger.info('[claw-rl] Service stopped');
      },
    });

    // ========================================================================
    // Context Engine Registration
    // ========================================================================

    // Register Context Engine factory
    api.registerContextEngine('claw-rl', () => {
      // Return ContextEngine object
      return {
        // Engine info
        info: {
          id: 'claw-rl',
          name: 'claw-rl Self-Improvement Engine',
          version: '2.0.0-beta.0',
          ownsCompaction: false,
        },

        // Assemble context before each turn - inject learned rules
        async assemble(params: {
          sessionId: string;
          sessionKey?: string;
          messages: any[];
          tokenBudget?: number;
          model?: string;
          prompt?: string;
        }) {
          try {
            if (!bridge.isReady()) {
              return {
                messages: params.messages,
                estimatedTokens: 0,
              };
            }

            // Get learned rules
            const result = await bridge.call('get_rules', {
              top_k: config.topK || 10,
              context: params.prompt || '',
            });

            // Format rules as system prompt addition
            if (result.rules && result.rules.length > 0) {
              const rulesText = result.rules
                .map((r: any) => r.content || r)
                .join('\n');

              return {
                messages: params.messages,
                estimatedTokens: 0,
                systemPromptAddition: `[Learned Rules]\n${rulesText}`,
              };
            }

            return {
              messages: params.messages,
              estimatedTokens: 0,
            };
          } catch (error) {
            api.logger.error('[claw-rl] Assemble error:', error);
            return {
              messages: params.messages,
              estimatedTokens: 0,
            };
          }
        },

        // Ingest messages - required method
        async ingest(params: {
          sessionId: string;
          sessionKey?: string;
          message: any;
          isHeartbeat?: boolean;
        }) {
          // We don't store messages, just return success
          return { ingested: true };
        },

        // After turn - learn from interaction
        async afterTurn(params: {
          sessionId: string;
          sessionKey?: string;
          sessionFile: string;
          messages: any[];
          prePromptMessageCount: number;
          autoCompactionSummary?: string;
          isHeartbeat?: boolean;
          tokenBudget?: number;
          runtimeContext?: any;
        }) {
          try {
            if (config.autoLearn && bridge.isReady() && params.messages.length > 0) {
              // Extract feedback from the last turn
              const lastMessages = params.messages.slice(params.prePromptMessageCount);

              for (const msg of lastMessages) {
                if (msg.role === 'user') {
                  await bridge.call('collect_feedback', {
                    feedback: msg.content,
                    context: { sessionId: params.sessionId },
                  });
                }
              }
            }
          } catch (error) {
            api.logger.error('[claw-rl] AfterTurn error:', error);
          }
        },
      };
    });
  },
};

export default plugin;
