/**
 * Event router for task session manager.
 *
 * Routes lifecycle events (session.created, server.instance.disposed,
 * session.idle, session.error, session.status, session.deleted) to
 * the appropriate subsystems.
 */
import type { BackgroundJobExecution } from '../../utils/background-job-board';
import type { BackgroundJobStore } from '../../utils/background-job-store';
import type { BackgroundJobSupervisor } from '../../utils/background-job-supervisor';
import type { InjectedTerminalJobs, RetainedBoardSnapshotState } from './board-injection';
import type { PendingTaskCall } from './pending-call-tracker';
import type { RevivedRunTracker } from './revived-run-tracker';
export declare function handleEvent(input: {
    event: {
        type: string;
        properties?: {
            info?: {
                id?: string;
                parentID?: string;
                agent?: string;
                generation?: number;
                activityAt?: number;
                timestamp?: number;
                time?: {
                    updated?: number;
                };
            };
            id?: string;
            requestID?: string;
            sessionID?: string;
            generation?: number;
            activityAt?: number;
            timestamp?: number;
            time?: {
                updated?: number;
            };
            status?: {
                type?: string;
            };
            error?: {
                name?: string;
            };
            part?: unknown;
        };
    };
}, deps: {
    inputWaits: {
        trackInputWait(event: {
            type: string;
            properties?: {
                id?: string;
                requestID?: string;
                sessionID?: string;
            };
        }): void;
        clearInputWaits(sessionID: string): void;
        waitsByParent: Map<string, Set<string | symbol>>;
    };
    idleSessionTokens: {
        clearSession(sessionID: string): void;
        invalidate(sessionID: string): void;
        /** Drop local idle-token bookkeeping; keep process-global wait_for_user. */
        disposeLocalState(): void;
        sessionTokens: Map<string, symbol>;
    };
    options: {
        shouldManageSession: (sessionID: string) => boolean;
        registerSessionAsOrchestrator?: (sessionID: string) => void;
        isFallbackInProgress?: (sessionID: string) => boolean;
        /** True when foreground fallback could still recover the session. */
        willAttemptFallback?: (sessionID: string) => boolean;
        /** Test seam; production uses event-arrival wall-clock time. */
        now?: () => number;
    };
    idleReconciler: {
        scheduleIdleReconciliation(sessionID: string): void;
        scheduleChildIdleReconciliation(sessionID: string, idleObservedAt: number, observedGeneration: number): void;
        scheduleErrorTerminalize(sessionID: string, idleObservedAt: number, observedGeneration: number): void;
        clearIdleTimers(sessionID: string): void;
        clearAllTimers(): string[];
    };
    /** Sessions with a deferred inline 401/410 awaiting fallback outcome. */
    deferredInlineErrors: Set<string>;
    backgroundJobBoard: BackgroundJobStore;
    pendingCallTracker: {
        peekByParentAndAgent(parentSessionID: string, agentHint?: string): PendingTaskCall | undefined;
        clearSession(sessionID: string): void;
        clearAll?(): void;
    };
    taskContextTracker: {
        pendingManagedTaskIds: Set<string>;
        clearSession(sessionID: string): void;
        prune(board: {
            taskIDs(): Set<string>;
        }): void;
    };
    terminalJobsInjectedByParent: Map<string, InjectedTerminalJobs>;
    pendingInjectedTerminalJobsByParent: Map<string, Map<string, BackgroundJobExecution>>;
    retainedBoardSnapshots: Map<string, RetainedBoardSnapshotState>;
    backgroundJobSupervisor?: BackgroundJobSupervisor;
    bindConcurrencyTicket?: (taskID: string, pending: PendingTaskCall) => void;
    releaseConcurrencyTask?: (taskID: string) => void;
    observeSyntheticTerminalPart?: (part: unknown) => void;
    revivedRunTracker?: RevivedRunTracker;
}): Promise<void>;
