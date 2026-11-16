/**
 * Periodic orchestrator wake scheduler.
 *
 * After continuous parent-idle time, capability-gated host session APIs may
 * receive a static internal wake prompt when incomplete todos remain. Active
 * children suppress periodic wakes. Host responses are authoritative; the local
 * job board is never consulted. Progress/reservation state is process-global
 * so independently created hook instances share one-flight and the two-wake
 * no-progress cap.
 */
import type { PluginInput } from '@opencode-ai/plugin';
import type { SessionLifecycle } from '../session-lifecycle';
export declare const ORCHESTRATOR_WAKE_TEXT = "<system-reminder>\nFinish any incomplete TODOs. Await running agents; if one appears stuck, assess it and cancel/respawn only when justified. Do not respond to this reminder.\n</system-reminder>";
export declare const ORCHESTRATOR_STOPPED_JOB_WAKE_TEXT = "<system-reminder>\nA background job stopped without a terminal result. Consult the Background Job Board, recover or reroute the work as needed, and do not wait for that job as if it were still running. Do not respond to this reminder.\n</system-reminder>";
/** After this many successful wakes with an unchanged fingerprint, stop. */
export declare const ORCHESTRATOR_WAKE_UNCHANGED_CAP = 2;
type LocalSessionState = {
    /** Invalidates local timers/async work for this hook instance. */
    generation: symbol;
    timer: ReturnType<typeof setTimeout> | undefined;
    continuousIdle: boolean;
};
export type OrchestratorWakeConfig = {
    enabled: boolean;
    intervalMs: number;
};
export type OrchestratorWakeOptions = {
    config: OrchestratorWakeConfig;
    shouldManageSession: (sessionID: string) => boolean;
    hasInputWait: (sessionID: string) => boolean;
    isFallbackInProgress?: (sessionID: string) => boolean;
    coordinator?: SessionLifecycle;
    /** Test seam: override interval without changing config validation. */
    intervalMs?: number;
};
export declare function buildOrchestratorWakeFingerprint(todos: Array<Record<string, unknown>>, children: Array<Record<string, unknown>>, status: Record<string, unknown>): string;
export declare function createOrchestratorWakeScheduler(ctx: PluginInput, options: OrchestratorWakeOptions): {
    event: (input: {
        event: {
            type: string;
            properties?: {
                info?: {
                    id?: string;
                };
                sessionID?: string;
                status?: {
                    type?: string;
                };
            };
        };
    }) => Promise<void>;
    observeChatMessage: (input: unknown, output: unknown) => void;
    triggerStoppedJobRecovery: (sessionID: string) => void;
    /** Clear timers when wait_for_user or fallback begins. */
    suppress: (sessionID: string) => void;
    /** Test seam */
    _test: {
        localSessions: Map<string, LocalSessionState>;
        intervalMs: number;
        enabled: boolean;
        hasRequiredSessionApis: () => boolean;
    };
};
export type OrchestratorWakeScheduler = ReturnType<typeof createOrchestratorWakeScheduler>;
export {};
