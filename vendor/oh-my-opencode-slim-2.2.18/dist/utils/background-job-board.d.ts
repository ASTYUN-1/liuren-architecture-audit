import type { BackgroundJobStore } from './background-job-store';
import { type TaskOutputState } from './task';
export interface ContextFile {
    path: string;
    lineCount: number;
    lineNumbers?: number[];
    lastReadAt: number;
}
export interface BackgroundJobExecution {
    taskID: string;
    generation: number;
}
export type BackgroundJobLeaseKind = 'cancellation' | 'relaunch' | 'message' | 'terminal-notification';
/** Process-local ownership of a remote operation or same-ID relaunch. */
export interface BackgroundJobLease {
    taskID: string;
    generation: number;
    token: string;
    kind: BackgroundJobLeaseKind;
}
export interface BackgroundJobPromptMetadata {
    text: string | undefined;
    terminalUnreconciledTaskIDs: BackgroundJobExecution[];
}
export type BackgroundJobState = TaskOutputState | 'stopped' | 'reconciled';
export interface BackgroundJobRecord {
    taskID: string;
    parentSessionID: string;
    agent: string;
    description: string;
    objective?: string;
    state: BackgroundJobState;
    /** True only when the native task call explicitly supplied background:true. */
    background: boolean;
    timedOut: boolean;
    recoverableAfterLiveBusy: boolean;
    statusUncertain: boolean;
    cancellationRequested: boolean;
    terminalUnreconciled: boolean;
    launchedAt: number;
    lastLaunchedAt: number;
    /** Monotonic run identity. Explicit relaunch/reuse increments it. */
    generation: number;
    /** Task-local run identity; unlike generation, unrelated tasks do not affect it. */
    taskGeneration: number;
    /** First launch observation for the current generation. */
    runStartedAt: number;
    /** Persistent hard wall-clock marker; distinct from external task wait timeout. */
    deadlineExceededAt?: number;
    updatedAt: number;
    lastLiveBusyAt?: number;
    /** First non-busy runtime observation for the current stop-confirmation grace. */
    stopConfirmationStartedAt?: number;
    completedAt?: number;
    resultSummary?: string;
    lastStatusError?: string;
    alias: string;
    lastUsedAt: number;
    terminalState?: TaskOutputState;
    contextFiles: ContextFile[];
    totalErrors?: number;
    timeoutCount?: number;
    lastErrorAt?: number;
}
export interface BackgroundJobBoardOptions {
    maxReusablePerAgent?: number;
    maxContextLines?: number;
    readContextMinLines?: number;
    readContextMaxFiles?: number;
}
export interface BackgroundJobLaunchInput {
    taskID: string;
    parentSessionID: string;
    agent: string;
    description?: string;
    objective?: string;
    background?: boolean;
    /** Preserve the current run when this is a duplicate lifecycle observation. */
    preserveRun?: boolean;
    /** Lease proving that this is an authorized same-ID relaunch observation. */
    relaunchLease?: BackgroundJobLease;
    /** Backwards-compatible generic spelling for the relaunch lease. */
    lease?: BackgroundJobLease;
    now?: number;
}
export interface BackgroundJobStatusInput {
    taskID: string;
    state: TaskOutputState;
    /** Ignore native output from an older run of the same task ID. */
    expectedGeneration?: number;
    timedOut?: boolean;
    statusUncertain?: boolean;
    resultSummary?: string;
    lastStatusError?: string;
    now?: number;
}
export interface WallClockTimeoutClaimInput {
    taskID: string;
    generation: number;
    now?: number;
    resultSummary?: string;
}
export interface WallClockTimeoutFinalizeInput {
    taskID: string;
    generation: number;
    now?: number;
    statusUncertain: boolean;
    resultSummary: string;
}
type TerminalStateListener = (taskID: string) => void;
export declare class BackgroundJobLaunchConflictError extends Error {
    constructor(taskID: string, message: string);
}
export declare class BackgroundJobBoard implements BackgroundJobStore {
    private readonly jobs;
    /** One live operation/relaunch owner per native session ID. */
    private readonly liveLeases;
    private readonly counters;
    private executionSequence;
    private leaseSequence;
    private terminalStateListeners;
    private readonly maxReusablePerAgent;
    private readonly maxContextLines;
    private readonly readContextMinLines;
    private readonly readContextMaxFiles;
    constructor(options?: BackgroundJobBoardOptions);
    addTerminalStateListener(listener: TerminalStateListener): void;
    removeTerminalStateListener(listener: TerminalStateListener): void;
    setTerminalStateListener(listener?: TerminalStateListener): void;
    private notifyTerminalStateListeners;
    registerLaunch(input: BackgroundJobLaunchInput): BackgroundJobRecord;
    updateStatus(input: BackgroundJobStatusInput): BackgroundJobRecord | undefined;
    updateFromStatusOutput(output: string): BackgroundJobRecord | undefined;
    markRunningFromLiveSession(taskID: string, now?: number, expectedGeneration?: number): BackgroundJobRecord | undefined;
    /**
     * The host reports that this child no longer executes, but no native task
     * result established success, cancellation, or failure. Keep that ambiguity
     * visible to the parent and never permit session reuse.
     */
    markStopped(taskID: string, resultSummary: string, observedAt?: number, expectedGeneration?: number, now?: number): BackgroundJobRecord | undefined;
    noteStopConfirmation(taskID: string, startedAt: number, expectedGeneration?: number): BackgroundJobRecord | undefined;
    markStatusUncertain(taskID: string, lastStatusError: string, expectedGeneration?: number, now?: number): BackgroundJobRecord | undefined;
    markReconciled(taskID: string, now?: number): BackgroundJobRecord | undefined;
    markCancelled(taskID: string, reason?: string, now?: number, options?: {
        force?: boolean;
        expectedGeneration?: number;
        cancellationLease?: BackgroundJobLease;
    }): BackgroundJobRecord | undefined;
    acquireCancellationLease(taskID: string, generation: number): BackgroundJobLease | undefined;
    acquireRelaunchLease(taskID: string, generation: number): BackgroundJobLease | undefined;
    acquireMessageLease(taskID: string, generation: number): BackgroundJobLease | undefined;
    acquireTerminalNotificationLease(taskID: string, generation: number): BackgroundJobLease | undefined;
    validateLease(lease: BackgroundJobLease): boolean;
    releaseLease(lease: BackgroundJobLease): boolean;
    get(taskID: string): BackgroundJobRecord | undefined;
    field<K extends keyof BackgroundJobRecord>(taskID: string, key: K): BackgroundJobRecord[K] | undefined;
    isRunning(taskID: string): boolean;
    isTerminalUnreconciled(taskID: string): boolean;
    getResultSummary(taskID: string): string | undefined;
    getLastLiveBusyAt(taskID: string): number | undefined;
    claimWallClockDeadline(input: WallClockTimeoutClaimInput): BackgroundJobRecord | undefined;
    finalizeWallClockTimeout(input: WallClockTimeoutFinalizeInput): BackgroundJobRecord | undefined;
    getParentSessionID(taskID: string): string | undefined;
    getState(taskID: string): BackgroundJobState | undefined;
    resolve(parentSessionID: string, taskIDOrAlias: string): BackgroundJobRecord | undefined;
    resolveReusable(parentSessionID: string, taskIDOrAlias: string, agent?: string): BackgroundJobRecord | undefined;
    resolveRecoverable(parentSessionID: string, taskIDOrAlias: string, agent?: string): BackgroundJobRecord | undefined;
    markUsed(parentSessionID: string, key: string, now?: number): void;
    taskIDs(): Set<string>;
    addContext(taskID: string, files: ContextFile[]): void;
    list(parentSessionID?: string): BackgroundJobRecord[];
    hasRunning(parentSessionID: string): boolean;
    hasTerminalUnreconciled(parentSessionID: string): boolean;
    hasConvergenceSignals(taskID: string, threshold?: number): boolean;
    formatForPromptWithMetadata(parentSessionID: string, _now?: number): BackgroundJobPromptMetadata | undefined;
    formatForPrompt(parentSessionID: string, now?: number): string | undefined;
    clearParent(parentSessionID: string): void;
    drop(taskID: string): void;
    deferIfRunning(_sessionId: string): boolean;
    retryDeferredClose(_sessionId: string): boolean;
    clearDeferredClose(_sessionId: string): void;
    private trimReusable;
    private formatReusableJob;
    private nextAlias;
    private nextLeaseToken;
}
export declare function deriveTaskSessionLabel(input: {
    description?: string;
    prompt?: string;
    agentType: string;
}): string;
/**
 * Full objective text before deriveTaskSessionLabel truncates it: the
 * whitespace-normalized description, else the first non-empty prompt line.
 * Board records store this untruncated so the duplicate-spawn guard can
 * match long exact duplicates without colliding on shared 48-char prefixes.
 */
export declare function deriveFullObjective(input: {
    description?: string;
    prompt?: string;
}): string | undefined;
export {};
