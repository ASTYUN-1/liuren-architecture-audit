import type { PluginInput } from '@opencode-ai/plugin';
import { type BackgroundJobStore, type BackgroundJobSupervisor, type BackgroundTaskConcurrency } from '../../utils';
import type { SessionLifecycle } from '../session-lifecycle';
import { type PendingCallTracker } from './pending-call-tracker';
import type { RevivedRunTracker } from './revived-run-tracker';
export { BACKGROUND_JOB_BOARD_METADATA_KEY } from './board-injection';
export declare function createTaskSessionManagerHook(_ctx: PluginInput, options: {
    strategy?: 'latest' | 'checkpoint-compatible';
    maxSessionsPerAgent: number;
    maxRetainedSnapshots: number;
    readContextMinLines?: number;
    readContextMaxFiles?: number;
    backgroundJobBoard?: BackgroundJobStore;
    backgroundJobSupervisor?: BackgroundJobSupervisor;
    backgroundTaskConcurrency?: BackgroundTaskConcurrency;
    /** Shared by plugin generations for one admission runtime. */
    pendingCallTracker?: PendingCallTracker;
    getModelForAgent?: (agentType: string, parentSessionID?: string) => string | undefined;
    shouldManageSession: (sessionID: string) => boolean;
    /** Register a session as orchestrator when the transform hook detects
     *  an orchestrator message but the session isn't in the agent map yet. */
    registerSessionAsOrchestrator?: (sessionID: string) => void;
    /** Optional guard: when provided, idle events for a session that is
     *  currently undergoing a foreground-fallback abort/re-prompt cycle
     *  will NOT trigger idle reconciliation. prevents marking a still-
     *  active child job as completed when the session was aborted for
     *  model fallback rather than natural completion. */
    isFallbackInProgress?: (sessionID: string) => boolean;
    /** True when foreground fallback could still recover the session
     *  (enabled, chain exists, chain not exhausted). Lets the event
     *  router defer terminal bookkeeping for persistent 401/410 errors
     *  until recovery is impossible. */
    willAttemptFallback?: (sessionID: string) => boolean;
    coordinator?: SessionLifecycle;
    /** Test seam only; production always uses the reconciliation delay. */
    idleReconcileDelayMs?: number;
    /** Test seam only; production uses the runtime reconciliation delay. */
    runtimeStatusReconcileDelayMs?: number;
    revivedRunTracker?: RevivedRunTracker;
}): {
    markRevivedRunPending: (taskID: string) => void;
    clearRevivedRunPending: (taskID: string) => void;
    contextFilesForTask: (taskID: string) => import("../../utils").ContextFile[];
    pruneTaskContext: () => void;
    beginUserWait: (sessionID: string) => void;
    /**
     * Narrow exposure for the orchestrator-wake scheduler: true while a
     * question/permission is open or wait_for_user is latched.
     */
    hasInputWait: (sessionID: string) => boolean;
    observeChatMessage: (input: unknown, output: unknown) => void;
    'tool.execute.before': (input: {
        tool: string;
        sessionID?: string;
        callID?: string;
    }, output: {
        args?: unknown;
    }) => Promise<void>;
    'tool.execute.after': (input: {
        tool: string;
        sessionID?: string;
        callID?: string;
    }, output: {
        output: unknown;
        metadata?: unknown;
    }) => Promise<void>;
    'experimental.chat.messages.transform': (_input: Record<string, never>, output: {
        messages?: unknown;
    }) => Promise<void>;
    injectBackgroundJobBoard: (input: Record<string, never>, output: {
        messages?: unknown;
    }) => Promise<void>;
    event: (input: {
        event: {
            type: string;
            properties?: {
                info?: {
                    id?: string;
                    parentID?: string;
                    agent?: string;
                };
                id?: string;
                requestID?: string;
                sessionID?: string;
                status?: {
                    type?: string;
                };
                error?: {
                    name?: string;
                };
                part?: unknown;
            };
        };
    }) => Promise<void>;
};
