export interface BackgroundTaskConcurrencyConfig {
    defaultConcurrency: number;
    providerConcurrency: Readonly<Record<string, number>>;
    modelConcurrency: Readonly<Record<string, number>>;
}
export interface BackgroundTaskConcurrencyRequest {
    model?: string;
}
export interface BackgroundTaskConcurrencyTicket {
    readonly ready: Promise<void>;
    bind(taskID: string): void;
    release(): void;
    releaseIfUnbound(): void;
}
export declare class BackgroundTaskConcurrencyQueueCancelledError extends Error {
    constructor();
}
/**
 * Process-local admission scheduler for native background task launches.
 *
 * Limits follow the reference implementation's override semantics: a model
 * cap for the task's model wins over a provider cap for its provider, which
 * wins over the default cap — only the most specific configured cap applies.
 * A configured value of `0` means unlimited for that key. Queued requests are
 * admitted in order, but entries whose resolved tier is saturated are skipped
 * in favor of admittable later entries (FIFO with skip). A ticket owns
 * capacity from the moment its `ready` promise resolves until the bound task
 * reaches a terminal state. The job board still owns task lifecycle; this
 * scheduler only controls admission.
 *
 * State is scoped to the scheduler instance. Plugin generations share this
 * scheduler through the per-directory lease in `src/admission-runtime.ts`.
 * `restoreTask` covers the one case the shared instance cannot: a genuine
 * process restart that resumes a still-running task from persisted history.
 */
export declare class BackgroundTaskConcurrency {
    private config;
    private readonly waiting;
    private readonly active;
    private readonly activeByKey;
    private readonly activeByTaskID;
    private activeDefault;
    private nextID;
    private disposed;
    constructor(config: BackgroundTaskConcurrencyConfig);
    /**
     * Apply a new configuration to this instance (used when the plugin factory
     * re-runs with changed config). Both running slots and queued tickets are
     * re-resolved against the new config: active entries move their accounting
     * to the tier their model now resolves to (so a newly lowered cap starts
     * counting tasks that were admitted under an unlimited/looser config), and
     * the queue re-pumps. Existing tasks are never terminated by a config
     * change — a running task that now exceeds a tightened cap keeps running
     * and blocks new admissions until it finishes.
     */
    updateConfig(config: BackgroundTaskConcurrencyConfig): void;
    isDisposed(): boolean;
    acquire(request: BackgroundTaskConcurrencyRequest): BackgroundTaskConcurrencyTicket;
    releaseTask(taskID: string): void;
    /**
     * Claim a slot for a task that is already running. Used to restore the
     * admission state after a plugin re-init (or a process restart that resumes
     * a live run), where the fresh scheduler cannot know about tasks that were
     * admitted by a previous generation. Idempotent: a task that already holds
     * a slot is left untouched. Restores bypass the resolved caps because the
     * task is already in flight — we are reconstructing reality, not admitting
     * new work.
     */
    restoreTask(taskID: string, model?: string): void;
    /**
     * Atomically move a running task's accounting from its admission
     * model/provider to a new model. Keeps provider/model caps correct when a
     * child session switches models mid-flight (foreground fallback, runtime
     * model switch). No-op when the task is unknown or already on that model.
     */
    migrateTask(taskID: string, model: string | undefined): void;
    dispose(): void;
    /** Test/diagnostic seam. */
    snapshot(): {
        active: number;
        queued: number;
    };
    private bind;
    private pump;
    private canStart;
    private track;
    private untrack;
    private release;
}
export { getBackgroundTaskConcurrency, resetBackgroundTaskConcurrencyForTests, } from '../admission-runtime';
