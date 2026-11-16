/**
 * Tool execute hooks for task session manager.
 *
 * Handles `tool.execute.before` (task tool: pending call creation,
 * reusable/recoverable task_id resolution) and `tool.execute.after`
 * (read context tracking, task launch registration/update from output).
 */
import type { BackgroundJobStore, BackgroundJobSupervisor, BackgroundTaskConcurrency, ContextFile } from '../../utils';
import type { PendingTaskCall } from './pending-call-tracker';
export declare function handleToolExecuteBefore(input: {
    tool: string;
    sessionID?: string;
    callID?: string;
}, output: {
    args?: unknown;
}, deps: {
    shouldManageSession: (sessionID: string) => boolean;
    registerSessionAsOrchestrator?: (sessionID: string) => void;
    backgroundJobBoard: BackgroundJobStore;
    pendingCallTracker: {
        add(call: PendingTaskCall): void;
        take(callID?: string, sessionID?: string): PendingTaskCall | undefined;
        release?(call: PendingTaskCall): void;
        pendingCallId(sessionID?: string, callID?: string): string;
    };
    taskContextTracker: {
        pendingManagedTaskIds: Set<string>;
    };
    backgroundJobSupervisor?: BackgroundJobSupervisor;
    backgroundTaskConcurrency?: BackgroundTaskConcurrency;
    getModelForAgent?: (agentType: string, parentSessionID?: string) => string | undefined;
    getLifecycleEpoch?: () => number;
}): Promise<void>;
export declare function handleToolExecuteAfter(input: {
    tool: string;
    sessionID?: string;
    callID?: string;
}, output: {
    output: unknown;
    metadata?: unknown;
}, deps: {
    directory: string;
    backgroundJobBoard: BackgroundJobStore;
    pendingCallTracker: {
        take(callID?: string, sessionID?: string, ownerBoard?: BackgroundJobStore): PendingTaskCall | undefined;
        release?(call: PendingTaskCall): void;
    };
    taskContextTracker: {
        pendingManagedTaskIds: Set<string>;
        addContext(taskId: string, files: ContextFile[]): void;
        contextFilesForPrompt(taskId: string): ContextFile[];
        prune(board: {
            taskIDs(): Set<string>;
        }): void;
    };
    backgroundJobSupervisor?: BackgroundJobSupervisor;
    bindConcurrencyTicket?: (taskID: string, pending: PendingTaskCall) => void;
    releaseConcurrencyTask?: (taskID: string) => void;
    /** Record direct task cleanup even when the store is a thin facade. */
    recordLifecycleSuppression?: (taskID: string) => void;
    /** Clear a deletion guard when a new native task output proves a run exists. */
    clearRehydrateTombstone?: (taskID: string) => void;
    isStaleDeletedTaskOutput?: (taskID: string, lifecycleEpoch: number) => boolean;
}): Promise<void>;
