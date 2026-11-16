import { type PluginInput, type ToolDefinition } from '@opencode-ai/plugin';
import type { BackgroundJobStore } from '../utils/background-job-store';
export interface TaskControlToolOptions {
    input: PluginInput;
    backgroundJobBoard: BackgroundJobStore;
    shouldManageSession: (sessionID: string) => boolean;
    abortTimeoutMs?: number;
    verifyAbortMs?: number;
    abortRetryIntervalMs?: number;
    stableStoppedMs?: number;
}
interface CapturedExecution {
    taskID: string;
    generation: number;
}
export declare class SessionStillRunningError extends Error {
}
export declare function createCancelTaskTool(options: TaskControlToolOptions): Record<'task_cancel', ToolDefinition>;
/**
 * Abort one captured generation and prove that its retained host session is
 * quiescent. This is shared by task_cancel and task_revive; neither operation
 * ever deletes the session.
 */
export declare function cancelTrackedExecution(options: TaskControlToolOptions, execution: CapturedExecution, reason?: string): Promise<void>;
export {};
