import type { BackgroundJobExecution, BackgroundJobInjectedCompletionFence, BackgroundJobLifecycleLedger, BackgroundJobRecord, BackgroundJobStore, BackgroundJobSyntheticTerminalOccurrence, BackgroundJobSyntheticTerminalOccurrencePhase, ContextFile } from '../../utils';
import type { MessagePart, MessageWithParts } from '../types';
export declare const BACKGROUND_JOB_BOARD_METADATA_KEY = "oh-my-opencode-slim.backgroundJobBoard";
type RetainedBoardSnapshot = {
    anchorKey: string;
    id: string;
    text: string;
    terminalUnreconciledTaskIDs: BackgroundJobExecution[];
};
export type RetainedBoardSnapshotState = {
    snapshots: RetainedBoardSnapshot[];
    nextSnapshotSequence: number;
    realMessageCount: number;
    firstRealMessageAnchorKey?: string;
};
/**
 * A board the `latest` strategy has already placed (and therefore already sent
 * to the provider) on a specific anchor message. Replayed byte-identically on
 * every later request once that anchor is no longer the tail, so a board that
 * was sent on a message the provider has cached never disappears.
 *
 * Only ONE placement is ever retained: a board that rode as a trailing PART on
 * a USER anchor (`anchorRole: 'user'`). That is the only shape that can be
 * reproduced later without inserting a message mid-array (A1) or grafting board
 * text onto a non-user message (A3). `anchorRole` stays a plain string so
 * legacy in-memory entries recorded by an earlier build (notably `'assistant'`,
 * which was replayed by splicing a synthetic message directly after the anchor
 * and could orphan a tool call from its result) are recognized and dropped
 * instead of replayed.
 */
type RetainedTailBoard = {
    anchorId: string;
    anchorRole: string;
    text: string;
};
export type InjectedTerminalJobs = {
    executions: Map<string, BackgroundJobExecution>;
    /** Prompt shape when these executions were last surfaced to the model. */
    promptShapeKey: string;
};
export type InjectedCompletionFence = BackgroundJobInjectedCompletionFence;
export type SyntheticTerminalOccurrencePhase = BackgroundJobSyntheticTerminalOccurrencePhase;
export type SyntheticTerminalOccurrenceOrigin = BackgroundJobSyntheticTerminalOccurrence;
type SyntheticTerminalProvenanceKind = 'explicit' | 'host-message' | 'legacy';
export interface InjectionState {
    backgroundJobBoard: BackgroundJobStore;
    lifecycleLedger: BackgroundJobLifecycleLedger;
    maxRetainedSnapshots: number;
    strategy: 'latest' | 'checkpoint-compatible';
    processedInjectedCompletions: Set<string>;
    processedInjectedCompletionOrder: string[];
    /**
     * Completion occurrences persist with the board so a recreated hook cannot
     * replay an old synthetic result into a newer task generation.
     */
    injectedCompletionFences?: Map<string, InjectedCompletionFence>;
    /**
     * Synthetic terminal parts observed by the runtime event stream. This is
     * separate from processed fences because an event may arrive before the
     * message transform that consumes the part.
     */
    syntheticTerminalOccurrences?: Map<string, SyntheticTerminalOccurrenceOrigin>;
    syntheticTerminalOccurrenceOrder?: string[];
    getLifecycleEpoch?: () => number;
    getDeletionEpoch?: (taskID: string) => number | undefined;
    terminalJobsInjectedByParent: Map<string, InjectedTerminalJobs>;
    pendingInjectedTerminalJobsByParent: Map<string, Map<string, BackgroundJobExecution>>;
    metadataKey: string;
    shouldManageSession: (sessionID: string) => boolean;
    taskContextTracker: {
        pendingManagedTaskIds: Set<string>;
        contextFilesForPrompt(taskId: string): ContextFile[];
        prune(board: {
            taskIDs(): Set<string>;
        }): void;
    };
    retainedBoardSnapshots: Map<string, RetainedBoardSnapshotState>;
    /**
     * Per-session log of boards the `latest` strategy has placed on real anchor
     * messages, keyed by anchor message id. Once an anchor is no longer the tail
     * its board is replayed byte-identically every later request, so a board sent
     * on a now-mid-history message is never stripped (which would rewrite already
     * cached bytes and bust the provider prompt-cache prefix from that message
     * onward - the field bust in dumps 000086->000087).
     */
    retainedTailBoards: Map<string, Map<string, RetainedTailBoard>>;
}
/**
 * Record a terminal synthetic task part at the runtime event boundary. The
 * part can be transformed later, after deletion and a same-ID relaunch, so
 * payload fields alone are not sufficient to recover its original generation.
 */
export declare function observeSyntheticTerminalPart(state: InjectionState, value: unknown): void;
/**
 * Normalize the `output` of every still-running `task` tool result to a
 * static, deterministic placeholder keyed only on the task ID.
 *
 * OpenCode core stores a fixed running placeholder in `state.output` when a
 * background task launches and materializes the terminal result separately as
 * a synthetic completion message. However, the runtime is free to stream live
 * child progress into a running task part's `state.output` (foreground
 * promotion, future core versions). Any such mid-history mutation invalidates
 * the provider prompt cache from that byte onward, re-writing the entire tail
 * every request while a background lane runs (write-never-read loop).
 *
 * This makes running task parts byte-stable at the plugin layer: it only ever
 * touches parts whose parsed state is `running`, so terminal
 * (completed/error/cancelled) results — which must reach the orchestrator
 * intact and mutate exactly once on completion — are never altered. It is a
 * pure normalization: re-running it on an already-stabilized part is a no-op.
 * Foreground (`wait:true`) tasks block and return a terminal state, so their
 * parts are never running here and keep their real output.
 */
export declare function stabilizeRunningTaskParts(messages: unknown[]): void;
export declare function updateFromInjectedCompletion(state: InjectionState, part: MessagePart, message: MessageWithParts, _messageIndex: number, partIndex: number): BackgroundJobRecord | undefined;
export declare function rememberProcessedInjectedCompletion(state: InjectionState, taskID: string, occurrenceId: string, provenanceKind: SyntheticTerminalProvenanceKind, fence?: InjectedCompletionFence): void;
export declare function isMissingRememberedSessionError(output: string): boolean;
export declare function rememberInjectedTerminalJobs(state: InjectionState, parentSessionID: string, executions: readonly BackgroundJobExecution[], promptShapeKey: string): void;
export declare function reconcileInjectedTerminalJobs(state: InjectionState, parentSessionID: string): void;
export declare function injectBackgroundJobBoard(state: InjectionState, _input: Record<string, never>, output: {
    messages?: unknown;
}): Promise<void>;
export {};
