import type { BackgroundJobRecord } from '../utils/background-job-board';
import { type RuntimeSessionStatus, type RuntimeSessionStatusSnapshot } from '../utils/session-runtime-status';
/** A live child is reported possibly stuck after this much time without activity. */
export declare const STUCK_IDLE_THRESHOLD_MS = 120000;
/**
 * Bounded, explicit observation of a tracked child's live session status.
 *
 * `ok` is true only when the host status map was read successfully (within
 * the bounded timeout). An absent session in a valid map is unknown;
 * a malformed entry is also `status: undefined` but carries `error`; a
 * failed or timed-out read is `ok: false` with `error`.
 */
export interface LiveStatusObservation {
    ok: boolean;
    status?: RuntimeSessionStatus;
    error?: string;
}
export interface TaskStatusReport {
    /** Effective state: the live-confirmed host status, or the board state. */
    state: string;
    /** Where `state` came from: 'live' host read or 'board' record. */
    source: 'live' | 'board';
    /** True when the live status could not be confirmed. */
    uncertain: boolean;
    lastStatusError?: string;
    idleSeconds: number;
    possiblyStuck: boolean;
}
/**
 * Converts a bounded snapshot into a single-session observation. A failed
 * read becomes `ok: false`; a malformed entry becomes `ok: true` with
 * `status: undefined` and an error; a valid map reports the entry's status.
 * A valid map without the requested session is an unknown/quiescent
 * observation, not an idle or terminal observation.
 */
export declare function observationFromSnapshot(snapshot: RuntimeSessionStatusSnapshot, taskID: string): LiveStatusObservation;
/**
 * Shared status/activity policy used by task_status. The board state is only
 * reported with explicit uncertainty when the live read is unavailable, so a
 * stale board record is never presented as a confident live status.
 */
export declare function summarizeTaskStatus(job: BackgroundJobRecord, observation: LiveStatusObservation, lastActivityAt: number | undefined, now: number): TaskStatusReport;
