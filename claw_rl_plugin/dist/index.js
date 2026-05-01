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
import { spawn } from 'child_process';
import * as path from 'path';
// ============================================================================
// ClawRLBridge - Python Bridge Client
// ============================================================================
/**
 * Bridge client for communicating with Python Bridge
 */
class ClawRLBridge {
    config;
    process = null;
    requestId = 0;
    pendingRequests = new Map();
    ready = false;
    starting = false;
    logger;
    constructor(config, logger) {
        this.config = config;
        this.logger = logger;
    }
    /**
     * Check if bridge is ready
     */
    isReady() {
        return this.ready;
    }
    /**
     * Start the bridge
     */
    async start() {
        if (this.process || this.starting) {
            return;
        }
        this.starting = true;
        return new Promise((resolve, reject) => {
            const pythonPath = this.config.pythonPath || 'python3';
            const bridgeModule = 'claw_rl.bridge'; // Module name, not path
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
            this.process.stdout?.on('data', (data) => {
                const lines = data.toString().split('\n').filter(line => line.trim());
                for (const line of lines) {
                    try {
                        const response = JSON.parse(line);
                        const pending = this.pendingRequests.get(response.id);
                        if (pending) {
                            this.pendingRequests.delete(response.id);
                            if (response.error) {
                                pending.reject(new Error(response.error.message));
                            }
                            else {
                                pending.resolve(response.result);
                            }
                        }
                    }
                    catch (e) {
                        this.logger.error('[claw-rl bridge] Failed to parse response:', e);
                    }
                }
            });
            // Handle stderr (logs)
            this.process.stderr?.on('data', (data) => {
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
    async call(method, params) {
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
    async stop() {
        if (this.process) {
            try {
                await this.call('shutdown');
            }
            catch (e) {
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
 * Safely extract text content from a message content field.
 * OpenClaw content can be a plain string or array of content blocks.
 */
function getTextContent(content) {
    if (typeof content === 'string')
        return content;
    if (Array.isArray(content)) {
        return content
            .filter((block) => block?.type === 'text' && typeof block.text === 'string')
            .map((block) => block.text)
            .join(' ');
    }
    return '';
}
/**
 * Extract feedback from event
 */
function extractFeedbackFromEvent(event) {
    // Extract from message content — safely handle string or array content
    if (event?.message?.content) {
        const textContent = getTextContent(event.message.content);
        if (!textContent)
            return null;
        const content = textContent.toLowerCase();
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
function formatRulesForInjection(rules) {
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
const plugin = {
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
    register(api) {
        const config = {
            pythonPath: api.pluginConfig?.pythonPath,
            bridgePath: api.pluginConfig?.bridgePath,
            workspaceDir: api.pluginConfig?.workspaceDir || api.config?.workspaceDir,
            autoInject: api.pluginConfig?.autoInject ?? true,
            autoLearn: api.pluginConfig?.autoLearn ?? true,
            topK: api.pluginConfig?.topK ?? 10,
            debug: api.pluginConfig?.debug ?? false,
        };
        const bridge = new ClawRLBridge(config, api.logger);
        let currentSessionId;
        // ========================================================================
        // Register Tools
        // ========================================================================
        api.registerTool({
            name: 'learning_status',
            label: 'Learning Status',
            description: 'Get the current status of the learning system.',
            parameters: {
                type: 'object',
                properties: {},
            },
        }, async (params) => {
            if (!bridge.isReady()) {
                return { error: 'Bridge not initialized' };
            }
            try {
                const result = await bridge.call('status');
                return result;
            }
            catch (error) {
                api.logger.error('[claw-rl] Status error:', error);
                return { error: error.message };
            }
        });
        api.registerTool({
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
        }, async (params) => {
            if (!bridge.isReady()) {
                return { error: 'Bridge not initialized' };
            }
            try {
                const result = await bridge.call('collect_feedback', params);
                return result;
            }
            catch (error) {
                api.logger.error('[claw-rl] Collect feedback error:', error);
                return { error: error.message };
            }
        });
        api.registerTool({
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
        }, async (params) => {
            if (!bridge.isReady()) {
                return { error: 'Bridge not initialized' };
            }
            try {
                const result = await bridge.call('get_rules', params);
                return result;
            }
            catch (error) {
                api.logger.error('[claw-rl] Get rules error:', error);
                return { error: error.message };
            }
        });
        // ========================================================================
        // Register Hooks
        // ========================================================================
        // Auto-inject: inject learned rules before session starts
        if (config.autoInject) {
            api.on('session_start', async (event, ctx) => {
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
                }
                catch (error) {
                    api.logger.error('[claw-rl] Auto-inject error:', error);
                }
            });
        }
        // Auto-learn: collect feedback after messages
        if (config.autoLearn) {
            api.on('message_received', async (event, ctx) => {
                // Extract feedback from event
                const feedbackData = extractFeedbackFromEvent(event);
                if (feedbackData) {
                    try {
                        await bridge.call('collect_feedback', feedbackData);
                    }
                    catch (error) {
                        api.logger.error('[claw-rl] Auto-learn error:', error);
                    }
                }
            });
            // Process learning at session end
            api.on('session_end', async (event, ctx) => {
                try {
                    await bridge.call('process_learning');
                }
                catch (error) {
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
    },
};
export default plugin;
//# sourceMappingURL=index.js.map