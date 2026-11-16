import type { RuntimeConfig } from '../config/runtime';
/**
 * Normalizes an agent name by trimming whitespace and removing the optional @ prefix.
 *
 * @param agentName - The agent name to normalize (e.g., "@oracle" or "oracle")
 * @returns The normalized agent name without @ prefix and trimmed of whitespace
 *
 * @example
 * normalizeAgentName("@oracle") // returns "oracle"
 * normalizeAgentName("  explore  ") // returns "explore"
 */
export declare function normalizeAgentName(agentName: string): string;
/**
 * Resolve a runtime-provided agent name to an internal agent name.
 *
 * Supports:
 * - internal names (e.g. "oracle")
 * - @-prefixed names (e.g. "@oracle")
 * - displayName aliases (e.g. "advisor" -> "oracle")
 */
export declare function resolveRuntimeAgentName(runtime: RuntimeConfig, agentName: string): string;
export declare function escapeRegExp(value: string): string;
export type DisplayNameMentionRewriter = (text: string) => string;
export declare function createDisplayNameMentionRewriter(runtime: RuntimeConfig): DisplayNameMentionRewriter;
