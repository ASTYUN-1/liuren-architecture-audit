import type { ContextFile } from '../../utils';
export declare function createTaskContextTracker(): {
    pendingManagedTaskIds: Set<string>;
    addContext(taskId: string, files: ContextFile[]): void;
    prune(backgroundJobBoard: {
        taskIDs(): Set<string>;
    }): void;
    clearSession(sessionId: string): void;
    contextFilesForPrompt(taskId: string): ContextFile[];
};
export declare function extractReadFiles(root: string, output: {
    output: unknown;
    metadata?: unknown;
}): ContextFile[];
