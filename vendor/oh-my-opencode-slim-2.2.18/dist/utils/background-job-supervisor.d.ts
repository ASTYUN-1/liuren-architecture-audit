import type { BackgroundJobRecord } from './background-job-board';
import type { BackgroundJobStore } from './background-job-store';
type TimerHandle = ReturnType<typeof setTimeout>;
export interface BackgroundJobSupervisorOptions {
    backgroundJobStore: BackgroundJobStore;
    wallClockTimeoutMs: number;
    abortGraceMs: number;
    abort: (taskID: string) => Promise<unknown>;
    now?: () => number;
    setTimeout?: (callback: () => void, delay: number) => TimerHandle;
    clearTimeout?: (timer: TimerHandle) => void;
}
/**
 * One-shot wall-clock supervision for native background task sessions.
 *
 * This class owns only timer/generation/abort mechanics. The board/coordinator
 * remains the atomic state and terminal-publication boundary.
 */
export declare class BackgroundJobSupervisor {
    private readonly options;
    private readonly now;
    private readonly setTimer;
    private readonly clearTimer;
    private readonly runs;
    private disposed;
    constructor(options: BackgroundJobSupervisorOptions);
    /** Register the first observation of a launch or an explicit new run. */
    onLaunch(record: BackgroundJobRecord): void;
    /** Clear one-shot timers after any canonical terminal publication. */
    onTerminal(record: BackgroundJobRecord): void;
    /**
     * Handle a child deletion before the normal board drop callback. A deletion
     * during grace confirms the timed-out terminal; an ordinary deletion simply
     * invalidates the run without inventing a terminal result.
     */
    onSessionDeleted(taskID: string): boolean;
    drop(taskID: string): void;
    clearParent(parentSessionID: string): void;
    /** Idempotent local cleanup. It never aborts or writes terminal state. */
    dispose(): void;
    private onDeadline;
    private onGraceExpired;
    private clear;
}
export {};
