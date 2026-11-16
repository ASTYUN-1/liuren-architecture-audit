import { type AgentName } from './constants';
import type { RuntimeConfig } from './runtime';
/** Default MCPs per agent - "*" means all MCPs, "!item" excludes specific MCPs */
export declare const DEFAULT_AGENT_MCPS: Record<AgentName, string[]>;
/**
 * Parse a list with wildcard and exclusion syntax.
 */
export declare function parseList(items: string[], allAvailable: string[]): string[];
/**
 * Get the MCP list for an agent (from config or defaults).
 * Reads the merged (preset-aware) plugin-layer agents via RuntimeConfig.
 */
export declare function getAgentMcpList(agentName: string, runtime: RuntimeConfig): string[];
