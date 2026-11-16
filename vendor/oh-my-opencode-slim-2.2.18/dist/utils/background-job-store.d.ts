import type { BackgroundJobLaunchInput, BackgroundJobLease, BackgroundJobPromptMetadata, BackgroundJobRecord, BackgroundJobStatusInput, ContextFile, WallClockTimeoutClaimInput, WallClockTimeoutFinalizeInput } from './background-job-board';
export type BackgroundJobSyntheticTerminalOccurrencePhase = 'observed' | 'processed' | 'ambiguous';
export interface BackgroundJobSyntheticTerminalOccurrence {
    taskID: string;
    occurrenceID: string;
    generationAtObservation?: number;
    lifecycleEpochAtObservation: number;
    phase: BackgroundJobSyntheticTerminalOccurrencePhase;
}
export interface BackgroundJobInjectedCompletionFence {
    taskID: string;
    generation: number;
    lifecycleEpoch: number;
}
/**
 * Process-local lifecycle memory shared by every hook using one job store.
 *
 * These sets/maps intentionally have no count cap. Evicting an old identity
 * would turn a replay of valid history into a false negative for the current
 * generation. The ledger is process-local by design; it is not persistence.
 */
export interface BackgroundJobLifecycleLedger {
    tombstones: Set<string>;
    deletionEpochs: Map<string, number>;
    injectedCompletionFences: Map<string, BackgroundJobInjectedCompletionFence>;
    syntheticTerminalOccurrences: Map<string, BackgroundJobSyntheticTerminalOccurrence>;
    syntheticTerminalOccurrenceOrder: string[];
    processedInjectedCompletions: Set<string>;
    processedInjectedCompletionOrder: string[];
    nextEpoch: number;
}
export declare function getBackgroundJobLifecycleLedger(store: BackgroundJobStore): BackgroundJobLifecycleLedger;
/** Record a task drop/eviction as a rehydrate and late-output tombstone. */
export declare function recordBackgroundJobSuppression(store: BackgroundJobStore, taskID: string): void;
/** Clear only the active rehydrate tombstone for a proven new launch. */
export declare function clearBackgroundJobSuppression(store: BackgroundJobStore, taskID: string): void;
/**
 * Unified interface for background job operations.
 * Both BackgroundJobBoard and BackgroundJobCoordinator satisfy this.
 *
 * ponytail: single interface, both board and coordinator implement it.
 */
export interface BackgroundJobStore {
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
    /**
     * Acknowledge the terminal notification delivered to the parent session.
     * This is a prompt-lifecycle acknowledgement, not filesystem reconciliation.
     */
    markReconciled(taskID: string, now?: number): BackgroundJobRecord | undefined;
    markCancelled(taskID: string, reason?: string, now?: number, options?: {
        force?: boolean;
        expectedGeneration?: number;
        cancellationLease?: BackgroundJobLease;
    }): BackgroundJobRecord | undefined;
    clearParent(parentSessionID: string): void;
    drop(taskID: string): void;
    addContext(taskID: string, files: ContextFile[]): void;
    markUsed(parentSessionID: string, key: string, now?: number): void;
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
    taskIDs(): Set<string>;
    list(parentSessionID?: string): BackgroundJobRecord[];
    hasRunning(parentSessionID: string): boolean;
    hasTerminalUnreconciled(parentSessionID: string): boolean;
    hasConvergenceSignals(taskID: string, threshold?: number): boolean;
    formatForPrompt(parentSessionID: string, now?: number): string | undefined;
    formatForPromptWithMetadata(parentSessionID: string, now?: number): BackgroundJobPromptMetadata | undefined;
    /** Evaluate close policy. Returns true if session should close now.
     *  Mutates deferred state: adds to deferred set if running, removes if not. */
    deferIfRunning(sessionId: string): boolean;
    /** Retry closing a deferred session. Returns true if session should now close. */
    retryDeferredClose(sessionId: string): boolean;
    /** Clear deferred close state for a session being deleted. */
    clearDeferredClose(sessionId: string): void;
}
