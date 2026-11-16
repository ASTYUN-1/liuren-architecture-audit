import type { PluginInput } from '@opencode-ai/plugin';
import type { BackgroundJobRecord, ContextFile } from '../../utils/background-job-board';
import type { BackgroundJobStore } from '../../utils/background-job-store';
import type { BackgroundJobSupervisor } from '../../utils/background-job-supervisor';
export interface RevivedRunTracker {
    captureBaseline(taskID: string): Promise<string | undefined>;
    register(input: {
        taskID: string;
        generation: number;
        parentSessionID: string;
        baselineMessageID?: string;
        description: string;
    }): void;
    isTracked(taskID: string, generation: number): boolean;
    probe(taskID: string, generation: number): Promise<boolean>;
    onTerminal(record: BackgroundJobRecord): void;
    dispose(): void;
}
export declare function createRevivedRunTracker(options: {
    input: PluginInput;
    backgroundJobBoard: BackgroundJobStore;
    backgroundJobSupervisor?: BackgroundJobSupervisor;
    maxNotificationRetries?: number;
    notificationRetryDelayMs?: number;
    maxStabilizationProbes?: number;
    stabilizationProbeDelayMs?: number;
    onRegister?: (taskID: string) => void;
    onSettled?: (taskID: string) => void;
    contextFilesForPrompt?: (taskID: string) => ContextFile[];
    pruneContext?: () => void;
}): RevivedRunTracker;
