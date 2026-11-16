/**
 * Shape adapters: convert v1 plugin objects into v2 registration shapes.
 *
 * - `parseModelRef`: "provider/model" string → v2 Model.Ref.
 * - `adaptPermissions`: v1 permission map → v2 Rule[] (with v2 permissive base +
 *   `task`→`subagent`, `bash`→`execute` mapping).
 * - `rewritePromptForV2`: rewrite v1 delegation syntax in agent/system prompts.
 * - `adaptTool`: v1 ToolDefinition ({description,args,execute}) → v2 Tool.Info.
 * - `applyAgentToDraft`: mutate a v2 agent draft entry from a v1 agent config.
 */
import type { ModelRef, V2AgentDraft } from './types';
/** Parse a v1 "provider/model" string into a v2 Model.Ref. */
export declare function parseModelRef(model: unknown): ModelRef | undefined;
/** Convert a v1 permission map (or shorthand string) into v2 permission rules. */
export declare function adaptPermissions(perm: unknown): Array<{
    action: string;
    resource: string;
    effect: string;
}>;
/** Rewrite v1 delegation syntax to v2. v2 renamed `task` → `subagent` and
 * `subagent_type` → `agent`. Applied to agent prompts at registration and to
 * the runtime system prompt so the orchestrator emits valid v2 tool calls. */
export declare function rewritePromptForV2(text: unknown): unknown;
/** Adapt a v1 tool definition ({description, args, execute}) to a v2 tool. */
export declare function adaptTool(name: string, v1Tool: Record<string, unknown>, directory: string, inputSchema: unknown): Record<string, unknown>;
/** Mutate a v2 agent draft entry from a v1 agent config. */
export declare function applyAgentToDraft(draft: V2AgentDraft, name: string, v1: Record<string, unknown>): void;
