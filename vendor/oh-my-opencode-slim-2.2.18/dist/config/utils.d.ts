import type { AgentOverrideConfig, PluginConfig } from './schema';
/**
 * Get agent override config by name, supporting backward-compatible aliases.
 * Checks both the current name and any legacy alias names.
 *
 * @param config - The plugin configuration
 * @param name - The current agent name
 * @returns The agent-specific override configuration if found
 */
export declare function getAgentOverride(config: PluginConfig | undefined, name: string): AgentOverrideConfig | undefined;
/**
 * Get custom agent names declared in config.agents.
 *
 * Custom agents are unknown keys that are neither built-in agent names nor
 * legacy aliases.
 */
export declare function getCustomAgentNames(config: PluginConfig | undefined): string[];
export declare function getAcpAgentNames(config: PluginConfig | undefined): string[];
