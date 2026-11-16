/** v2↔v1 delegation tool normalization. The v2 host's built-in `subagent`
 * tool corresponds to v1's `task`: the v2 setup tool-execute bridge
 * translates names/args so the whole v1 pipeline (task-session-manager,
 * job board, task_* tools) is reused with zero changes. */
export declare const DELEGATION_TOOL_V2 = "subagent";
export declare const DELEGATION_TOOL_V1 = "task";
/** v2 `subagent` tool name → the `task` name the v1 pipeline expects;
 * every other name is returned unchanged. */
export declare function toolNameToV1(tool: string): string;
/** v2 subagent args → v1 task args view (shallow copy):
 * agent→subagent_type, sessionID→task_id, rest unchanged. */
export declare function subagentArgsToV1(input: unknown): Record<string, unknown>;
/** v1 task args → v2 subagent args (shallow copy, reverse mapping).
 * A hook deleting task_id → result has no sessionID; a hook writing
 * task_id → sessionID stays in sync. */
export declare function v1ArgsToSubagent(args: Record<string, unknown>): Record<string, unknown>;
