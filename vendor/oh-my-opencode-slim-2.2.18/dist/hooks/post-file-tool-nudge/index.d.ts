/**
 * Post-tool nudge - queues a delegation reminder after file reads/writes.
 * Catches the "inspect/edit files → implement myself" anti-pattern.
 *
 * The reminder is ephemeral: recorded on tool execution, injected via
 * messages.transform, and consumed once. File tool output stays clean.
 */
import type { SessionLifecycle } from '../session-lifecycle';
interface PostFileToolNudgeOptions {
    shouldInject?: (sessionID: string) => boolean;
    coordinator?: SessionLifecycle;
}
export declare function createPostFileToolNudgeHook(options?: PostFileToolNudgeOptions): {
    'tool.execute.after': (input: {
        tool: string;
        sessionID?: string;
        callID?: string;
    }, _output: unknown) => Promise<void>;
    'experimental.chat.messages.transform': (_input: Record<string, never>, output: {
        messages?: unknown;
    }) => Promise<void>;
};
export {};
