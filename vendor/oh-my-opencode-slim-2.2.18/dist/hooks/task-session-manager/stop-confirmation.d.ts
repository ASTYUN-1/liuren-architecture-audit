import type { BackgroundJobRecord, BackgroundJobStore, ContextFile } from '../../utils';
export declare const STOP_CONFIRMATION_GRACE_MS = 5000;
export declare const STOPPED_WITHOUT_TERMINAL_RESULT = "Background session stopped before a terminal task result was received.";
export type StopConfirmationTracker = {
    pendingManagedTaskIds: Set<string>;
    contextFilesForPrompt(taskId: string): ContextFile[];
    prune(board: {
        taskIDs(): Set<string>;
    }): void;
};
export declare function applyConfirmedStop(options: {
    backgroundJobBoard: BackgroundJobStore;
    taskID: string;
    observedAt: number;
    generation: number;
    taskContextTracker: StopConfirmationTracker;
}): BackgroundJobRecord | undefined;
/**
 * Idle/absent/non-busy is only a stop candidate. The first observation
 * starts a grace clock; a later observation after the grace confirms
 * the stop. Live busy after the observation wins and leaves the job running.
 */
export declare function observeNonBusyRuntime(options: {
    backgroundJobBoard: BackgroundJobStore;
    taskID: string;
    observedAt: number;
    generation: number;
    graceMs: number;
    lastStatusError: string;
    taskContextTracker: StopConfirmationTracker;
}): BackgroundJobRecord | undefined;
