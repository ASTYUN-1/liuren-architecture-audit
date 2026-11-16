/**
 * Parse Task tool output to recover a session/task ID for resumption.
 */
export type TaskOutputState = 'running' | 'completed' | 'error' | 'cancelled';
export interface TaskLaunchOutput {
    taskID: string;
    state: 'running';
    result?: string;
}
export interface TaskStatusOutput {
    taskID: string;
    state: TaskOutputState;
    timedOut: boolean;
    result?: string;
}
/**
 * Static, deterministic placeholder for a still-running background task tool
 * result. Keyed only on the task ID so re-rendering across consecutive
 * requests produces byte-identical output regardless of any live progress the
 * runtime may stream into the tool part's `state.output`. Keeping running
 * results byte-stable prevents provider prompt-cache invalidation mid-history
 * while a background lane is active.
 */
export declare function renderRunningTaskPlaceholder(taskID: string): string;
export declare function parseTaskIdFromTaskOutput(output: string): string | undefined;
export declare function parseTaskLaunchOutput(output: string): TaskLaunchOutput | undefined;
export declare function parseTaskStatusOutput(output: string): TaskStatusOutput | undefined;
export declare function parseTaskStateFromOutput(output: string): TaskOutputState | undefined;
/** Diagnostic applied when a terminal `completed` report carries no text. */
export declare const COMPLETED_WITHOUT_TEXT_DIAGNOSTIC = "Task ended without a public text result; completion is not confirmed";
export interface GuardedTaskStatus {
    state: TaskOutputState;
    resultSummary?: string;
    lastStatusError?: string;
}
export declare function guardCompletedStatusText(state: TaskOutputState, result: string | undefined, existingResultSummary: string | undefined): GuardedTaskStatus;
export declare function parseTaskResultFromOutput(output: string): string | undefined;
