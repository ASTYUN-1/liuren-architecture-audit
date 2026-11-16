import type { PluginInput } from '@opencode-ai/plugin';
import type { BackgroundJobStore, ContextFile } from '../../utils';
export declare const RUNTIME_STATUS_RECONCILE_DELAY_MS = 5000;
export declare function createRuntimeStatusReconciler(options: {
    input: PluginInput;
    backgroundJobBoard: BackgroundJobStore;
    delayMs?: number;
    statusTimeoutMs?: number;
    stopConfirmationGraceMs?: number;
    taskContextTracker: {
        pendingManagedTaskIds: Set<string>;
        contextFilesForPrompt(taskId: string): ContextFile[];
        prune(board: {
            taskIDs(): Set<string>;
        }): void;
    };
}): {
    schedule: () => void;
    reconcile: () => Promise<void>;
    dispose: () => void;
};
