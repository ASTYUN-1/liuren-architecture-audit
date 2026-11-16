import type { BackgroundJobBoard, BackgroundJobLaunchInput, BackgroundJobLease, BackgroundJobPromptMetadata, BackgroundJobRecord, BackgroundJobStatusInput, ContextFile, WallClockTimeoutClaimInput, WallClockTimeoutFinalizeInput } from './background-job-board';
import type { BackgroundJobStore } from './background-job-store';
type TerminalStateListener = (taskID: string) => void;
type TerminalOutcomeListener = (record: BackgroundJobRecord) => void;
/**
 * BackgroundJobCoordinator owns the lifecycle policy for background jobs.
 * It sits between the board and its consumers, providing:
 * - Subscription interface for terminal state notifications (replaces fire-and-forget)
 * - Lifecycle policy: determines when jobs are terminal, when closes should be deferred
 * - Single-writer contract: coordinator is the sole writer to the board
 *
 * The board's guards prevent silent overwrites. The coordinator adds:
 * - Centralized notification with guaranteed delivery
 * - Re-checks board state before notifying (handles races)
 */
export declare class BackgroundJobCoordinator implements BackgroundJobStore {
    private readonly board;
    private terminalStateListeners;
    private terminalOutcomeListeners;
    private readonly deferredIdleCloses;
    constructor(board: BackgroundJobBoard);
    addTerminalStateListener(listener: TerminalStateListener): void;
    removeTerminalStateListener(listener: TerminalStateListener): void;
    /**
     * Handle terminal state from board. Re-checks board state to handle races.
     * This is the centralized lifecycle policy.
     */
    private handleTerminalState;
    /** Observe every canonical terminal publication, including non-idle jobs. */
    addTerminalOutcomeListener(listener: TerminalOutcomeListener): void;
    removeTerminalOutcomeListener(listener: TerminalOutcomeListener): void;
    /**
     * Evaluate close policy. Returns true if session should close now.
     * Mutates deferred state: adds to deferred set if running, removes if not.
     */
    deferIfRunning(sessionId: string): boolean;
    /**
     * Retry closing a deferred session. Called when a background job completes.
     * Returns true if the session should now close.
     */
    retryDeferredClose(sessionId: string): boolean;
    /**
     * Clear deferred close state for a session being deleted.
     */
    clearDeferredClose(sessionId: string): void;
    registerLaunch(input: BackgroundJobLaunchInput): BackgroundJobRecord;
    acquireCancellationLease(taskID: string, generation: number): BackgroundJobLease | undefined;
    acquireRelaunchLease(taskID: string, generation: number): BackgroundJobLease | undefined;
    acquireMessageLease(taskID: string, generation: number): BackgroundJobLease | undefined;
    acquireTerminalNotificationLease(taskID: string, generation: number): BackgroundJobLease | undefined;
    validateLease(lease: BackgroundJobLease): boolean;
    releaseLease(lease: BackgroundJobLease): boolean;
    updateStatus(input: BackgroundJobStatusInput): BackgroundJobRecord | undefined;
    updateFromStatusOutput(output: string): BackgroundJobRecord | undefined;
    claimWallClockDeadline(input: WallClockTimeoutClaimInput): BackgroundJobRecord | undefined;
    finalizeWallClockTimeout(input: WallClockTimeoutFinalizeInput): BackgroundJobRecord | undefined;
    markRunningFromLiveSession(taskID: string, now?: number, expectedGeneration?: number): BackgroundJobRecord | undefined;
    markStopped(taskID: string, resultSummary: string, observedAt?: number, expectedGeneration?: number, now?: number): BackgroundJobRecord | undefined;
    noteStopConfirmation(taskID: string, startedAt: number, expectedGeneration?: number): BackgroundJobRecord | undefined;
    markStatusUncertain(taskID: string, lastStatusError: string, expectedGeneration?: number, now?: number): BackgroundJobRecord | undefined;
    markReconciled(taskID: string, now?: number): BackgroundJobRecord | undefined;
    markCancelled(taskID: string, reason?: string, now?: number, options?: {
        force?: boolean;
        expectedGeneration?: number;
        cancellationLease?: BackgroundJobLease;
    }): BackgroundJobRecord | undefined;
    get(taskID: string): BackgroundJobRecord | undefined;
    field<K extends keyof BackgroundJobRecord>(taskID: string, key: K): BackgroundJobRecord[K] | undefined;
    isRunning(taskID: string): boolean;
    isTerminalUnreconciled(taskID: string): boolean;
    getResultSummary(taskID: string): string | undefined;
    getLastLiveBusyAt(taskID: string): number | undefined;
    getParentSessionID(taskID: string): string | undefined;
    getState(taskID: string): BackgroundJobRecord['state'] | undefined;
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
    formatForPrompt(parentSessionID: string, now?: number): string | undefined;
    formatForPromptWithMetadata(parentSessionID: string, now?: number): BackgroundJobPromptMetadata | undefined;
    clearParent(parentSessionID: string): void;
    drop(taskID: string): void;
}
export {};
