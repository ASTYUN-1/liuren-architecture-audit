import type { BackgroundJobStore, ContextFile } from '../../utils';
import type { RevivedRunTracker } from './revived-run-tracker';
export declare function createIdleReconciler(options: {
    backgroundJobBoard: BackgroundJobStore;
    reconcileInjectedTerminalJobs: (parentSessionID: string) => void;
    /** Called when a deferred inline error is terminalized at idle. */
    onErrorTerminalize?: (sessionID: string) => void;
    idleReconcileDelayMs: number;
    stopConfirmationGraceMs?: number;
    isFallbackInProgress?: (sessionID: string) => boolean;
    hasInputWait: (sessionID: string) => boolean;
    getIdleSessionToken: (sessionID: string) => symbol;
    isCurrentIdleSessionToken: (sessionID: string, sessionToken: symbol) => boolean;
    taskContextTracker: {
        pendingManagedTaskIds: Set<string>;
        contextFilesForPrompt(taskId: string): ContextFile[];
        prune(board: {
            taskIDs(): Set<string>;
        }): void;
    };
    revivedRunTracker?: RevivedRunTracker;
}): {
    scheduleIdleReconciliation: (parentSessionID: string) => void;
    scheduleChildIdleReconciliation: (sessionID: string, idleObservedAt: number, observedGeneration: number) => void;
    scheduleErrorTerminalize: (sessionID: string, idleObservedAt: number, observedGeneration: number) => void;
    clearIdleTimers: (sessionID: string) => void;
    clearAllTimers: () => string[];
    /** Callback for idle-session-tokens invalidate. */
    onInvalidateIdle: (sessionID: string) => void;
};
