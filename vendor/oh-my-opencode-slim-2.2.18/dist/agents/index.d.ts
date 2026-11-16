import type { AgentConfig as SDKAgentConfig } from '@opencode-ai/sdk/v2';
import { type PluginConfig, SUBAGENT_NAMES } from '../config';
import type { RuntimeConfig } from '../config/runtime';
import { type AgentDefinition } from './orchestrator';
export type { AgentDefinition } from './orchestrator';
export declare function resolvePrimaryModelValue(value: unknown): string | undefined;
/**
 * Resolve the model an agent's final config carries, mirroring the combined
 * effect of `createAgents` fallbacks, `applyOverrides`, and the inheritance
 * passes. Returns `undefined` exactly when the agent config ends up with NO
 * model key — i.e. `inheritModelFrom: 'session'` (or `'orchestrator'` with no
 * configured orchestrator model) — in which case OpenCode serves the agent
 * with the parent session's current model.
 *
 * This is the single resolution source for both agent definition building and
 * background-task admission, so provider/model concurrency accounting keys off
 * the model the spawned subagent actually uses. Explicit `model` wins; then
 * `inheritModelFrom`; then the historical fixer → librarian fallback; then
 * the preset primary model; then the per-agent default.
 */
export declare function resolveAgentConfigModel(runtime: RuntimeConfig, name: string): string | undefined;
/**
 * Apply model inheritance to the final host agent config after the host layer
 * has been merged. This clears stale host models for `session` inheritance,
 * which cannot be handled by the agent definition alone.
 */
export declare function applyModelInheritanceToConfig(configAgent: Record<string, unknown>, runtime: RuntimeConfig): void;
export type SubagentName = (typeof SUBAGENT_NAMES)[number];
export declare function isSubagent(name: string): name is SubagentName;
/**
 * Create all agent definitions with optional configuration overrides.
 * Instantiates the orchestrator and all subagents, applying user config and defaults.
 *
 * @param runtime - Runtime configuration interface (plugin layer, preset-aware)
 * @returns Array of agent definitions (orchestrator first, then subagents)
 */
export declare function createAgents(runtime: RuntimeConfig, options?: {
    projectDirectory?: string;
}): AgentDefinition[];
/**
 * Get agent configurations formatted for the OpenCode SDK.
 * Converts agent definitions to SDK config format and applies classification metadata.
 *
 * @param runtime - Runtime configuration interface (plugin layer, preset-aware)
 * @param options - Optional options including projectDirectory
 * @returns Record mapping agent names to their SDK configurations
 */
export declare function getAgentConfigs(runtime: RuntimeConfig, options?: {
    projectDirectory?: string;
}): Record<string, SDKAgentConfig>;
/**
 * Get the set of disabled agent names from config, applying protection rules.
 */
export declare function getDisabledAgents(config?: PluginConfig): Set<string>;
