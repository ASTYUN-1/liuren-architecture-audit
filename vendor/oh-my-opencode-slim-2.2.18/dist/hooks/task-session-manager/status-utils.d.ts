import type { BackgroundJobRecord, BackgroundJobStore, ContextFile } from '../../utils';
export declare function extractTaskSummary(output: string): string | undefined;
export declare function isActiveStatus(status: Record<string, unknown>, sessionID: string): boolean;
export declare function isLateCancelledTaskError(job: BackgroundJobRecord | undefined, state: string): boolean;
export declare function formatCancelledTaskStatusOutput(taskID: string, summary?: string): string;
export declare function updateBackgroundJobFromOutput(output: unknown, backgroundJobBoard: BackgroundJobStore, taskContextTracker: {
    pendingManagedTaskIds: Set<string>;
    contextFilesForPrompt(taskId: string): ContextFile[];
    prune(board: {
        taskIDs(): Set<string>;
    }): void;
}): BackgroundJobRecord | undefined;
export declare function normalizeLateCancelledTaskOutput(output: {
    output: unknown;
    metadata?: unknown;
}, backgroundJobBoard: BackgroundJobStore): void;
