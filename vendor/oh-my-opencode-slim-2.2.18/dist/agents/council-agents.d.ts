import type { RuntimeConfig } from '../config/runtime';
import type { AgentDefinition } from './orchestrator';
/**
 * Build dynamic councillor agents from council config presets.
 * Each councillor gets its own agent (name + model) so the orchestrator
 * can task() them with native panes at depth 1 using per-councillor models.
 * Agent names are prefixed with `councillor-` because raw councillor names
 * (e.g. "alpha") can collide with OpenCode-reserved agent type names.
 */
export declare function buildCouncillorAgents(runtime: RuntimeConfig, disabled: Set<string>): AgentDefinition[];
/**
 * Return the user-facing councillor seat name for a prefixed agent name.
 * Inverse of the prefix applied in `buildCouncillorAgents`.
 */
export declare function getCouncillorSeatName(agentName: string): string;
