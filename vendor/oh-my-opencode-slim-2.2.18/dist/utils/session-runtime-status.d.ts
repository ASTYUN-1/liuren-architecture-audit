import type { PluginInput } from '@opencode-ai/plugin';
export type RuntimeSessionStatus = 'busy' | 'retry' | 'idle';
export declare const DEFAULT_RUNTIME_SESSION_STATUS_TIMEOUT_MS = 5000;
export interface RuntimeSessionStatusSnapshot {
    statuses: ReadonlyMap<string, RuntimeSessionStatus>;
    malformedSessionIDs: ReadonlySet<string>;
    error?: string;
}
/**
 * Reads OpenCode's single live session-status map. An absent session in a
 * valid response is unknown: the endpoint only describes currently active
 * runners and does not prove that a background task has terminated.
 */
export declare function getRuntimeSessionStatusSnapshot(input: PluginInput, options?: {
    timeoutMs?: number;
}): Promise<RuntimeSessionStatusSnapshot>;
export declare function runtimeSessionStatus(snapshot: RuntimeSessionStatusSnapshot, sessionID: string): RuntimeSessionStatus | undefined;
