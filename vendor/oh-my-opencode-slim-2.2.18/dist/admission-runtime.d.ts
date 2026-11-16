import { type PendingCallTracker } from './hooks/task-session-manager/pending-call-tracker';
import { BackgroundTaskConcurrency, type BackgroundTaskConcurrencyConfig } from './utils/background-task-concurrency';
export interface AdmissionRuntime {
    readonly backgroundTaskConcurrency: BackgroundTaskConcurrency;
    readonly pendingCallTracker: PendingCallTracker;
}
export interface AdmissionRuntimeLease extends AdmissionRuntime {
    release(): void;
}
/**
 * Acquire the per-directory admission runtime.
 *
 * Plugin generations share this runtime while they overlap. Releasing the
 * last generation is intentionally delayed by one macrotask: OpenCode
 * disposes and recreates a plugin during config updates, and the new factory
 * must be able to reclaim the scheduler and pending calls before teardown.
 */
export declare function acquireAdmissionRuntime(directory: string, config: BackgroundTaskConcurrencyConfig): AdmissionRuntimeLease;
/** Test seam: synchronously dispose every directory runtime. */
export declare function resetAdmissionRuntimeForTests(): void;
/**
 * Legacy test helper. Production code must acquire and release a lease so a
 * plugin generation cannot keep a directory runtime alive accidentally.
 */
export declare function getBackgroundTaskConcurrency(directory: string, config: BackgroundTaskConcurrencyConfig): BackgroundTaskConcurrency;
/** Legacy test helper paired with getBackgroundTaskConcurrency. */
export declare function resetBackgroundTaskConcurrencyForTests(): void;
