export interface TuiSnapshot {
    version: 1;
    updatedAt: number;
    agentModels: Record<string, string>;
    agentVariants: Record<string, string>;
    activeSessions: Record<string, string>;
}
export declare function getTuiStatePath(projectDir: string): string;
export declare function readTuiSnapshot(projectDir: string): TuiSnapshot;
export declare function readTuiSnapshotAsync(projectDir: string): Promise<TuiSnapshot>;
export declare function recordTuiAgentModels(input: {
    agentModels: Record<string, string>;
    agentVariants?: Record<string, string>;
}, projectDir: string): void;
export declare function recordTuiAgentModel(input: {
    agentName: string;
    model: string;
    variant?: string | null;
}, projectDir: string): void;
export declare function recordTuiAgentActivity(input: {
    sessionID: string;
    agentName: string;
    active: true;
} | {
    sessionID: string;
    active: false;
}, projectDir: string): void;
export declare function clearTuiAgentActivities(projectDir: string): void;
