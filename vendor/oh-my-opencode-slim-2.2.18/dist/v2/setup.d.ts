/**
 * v2 setup orchestration.
 *
 * Returns the `setup(ctx)` function v2 calls via `default.setup`. The setup
 * wraps the existing v1 factory (reusing ALL build logic) and translates the
 * returned v1 `Hooks` into v2 registrations: agent/tool/command transforms,
 * a single session context hook (system/messages transforms, chat.message
 * tracking, and interview + generic command marker dispatch), tool execute
 * hooks, and the event stream. Each bridge is independently try/catch-guarded.
 */
import type { McpConfig } from '../mcp/types';
import { type V2CommandSubmit } from './session-submit';
import type { V2Cleanup, V2CommandDraft, V2Context, V2SessionContextEvent } from './types';
/** v1 `command.execute.before` hook shape (see src/index.ts wiring). */
export type V1CommandBeforeHook = (input: {
    command: string;
    sessionID: string;
    arguments: string;
}, output: {
    parts: Array<{
        type: string;
        text?: string;
        synthetic?: boolean;
        metadata?: Record<string, unknown>;
    }>;
}) => Promise<void>;
/** Wrap slash-command arguments in the generic v2 command marker. v2 command
 * drafts are add-only (no `template`), so `execute` submits this marker as a
 * plain user prompt and the session context hook recovers it below. */
export declare function wrapCommandMarker(name: string, args: string): string;
export interface ParsedCommandMarker {
    name: string;
    args: string;
}
/** Parse the generic command marker from a message text, if present. */
export declare function parseCommandMarker(text: string): ParsedCommandMarker | undefined;
/** Strip the marker tags from marker-only `text`, leaving the raw args. */
export declare function stripCommandMarker(text: string): string;
/** Register one v1 synth command on a v2 command draft. Uses `add` when
 * present; callers wrap per-command in try/catch so a throwing `draft.add`
 * only skips that command. */
export declare function createCommandRegistration(draft: V2CommandDraft, name: string, cmd: {
    description?: string;
}, submit: V2CommandSubmit): void;
/** Register the v1 synth commands on a v2 command draft. `interview` is
 * owned by the interview bridge's own registration (whose context hook owns
 * the interview marker), so it is skipped here — a duplicate `draft.add`
 * would break `/interview` on host builds that are first-wins or throw on
 * duplicates. */
export declare function registerSynthCommands(draft: V2CommandDraft, entries: Array<[string, {
    description?: string;
}]>, submit: V2CommandSubmit): void;
/** Dispatch a generic command marker found in the trailing user message to
 * the v1 `command.execute.before` hook, then replace that message's content
 * with the hook-produced parts. Mirrors the interview bridge mutation
 * semantics: only the trailing message is touched so earlier messages stay
 * byte-for-byte identical (provider prompt-cache prefix reuse). */
export declare function applyCommandMarkerToContext(event: V2SessionContextEvent, commandBefore: V1CommandBeforeHook): Promise<void>;
/** Deps injected into the single session context hook. */
export interface V2SessionContextHandlerDeps {
    /** Interview bridge handleContext (transcript projection + /interview
     * marker dispatch). */
    interviewHandleContext: (event: V2SessionContextEvent) => Promise<void>;
    /** v1 `command.execute.before` hook (generic command marker dispatch). */
    commandBefore?: V1CommandBeforeHook;
    /** v1 `chat.message` hook (agent tracking). */
    chatMessage?: (input: {
        sessionID: string;
        agent?: string;
        messageID?: string;
    }, output: unknown) => Promise<void>;
    /** v1 `experimental.chat.system.transform` hook. */
    systemTransform?: (input: unknown, output: {
        system: string[];
    }) => Promise<void>;
    /** v1 `experimental.chat.messages.transform` hook. */
    messagesTransform?: (input: unknown, output: {
        messages: Array<{
            info: {
                role: string;
            };
            parts: unknown[];
        }>;
    }) => Promise<void>;
}
/** Build the single `ctx.session.hook("context")` handler: interview marker
 * bridge, generic command marker dispatch, chat.message agent tracking, and
 * the v1 system/messages transforms — each independently try/catch-guarded. */
export declare function createSessionContextHandler(deps: V2SessionContextHandlerDeps): (event: V2SessionContextEvent) => Promise<void>;
/** The v2→v1 tool.execute bridge pair produced by
 * `createToolExecuteBridges`. */
export interface V2ToolBridgeEvents {
    beforeBridge: (event: Record<string, unknown> & {
        input: unknown;
    }) => Promise<void>;
    afterBridge: (event: Record<string, unknown> & {
        result?: unknown;
    }) => Promise<void>;
}
/** Build the tool.execute.before/after v2→v1 bridges, including the
 * `subagent`→`task` delegation normalization. Exported for tests. */
export declare function createToolExecuteBridges(before: ((i: {
    tool: string;
    sessionID: string;
    callID: string;
}, o: {
    args: unknown;
}) => Promise<void>) | undefined, after: ((i: unknown, o: unknown) => Promise<void>) | undefined): V2ToolBridgeEvents;
/** v1 McpConfig → v2 Mcp.ServerConfig（字段几乎同构；仅剔除 undefined）。 */
export declare function adaptMcpServer(v1: McpConfig): Record<string, unknown>;
export declare function createV2Setup(): (ctx: V2Context) => Promise<V2Cleanup>;
