/**
 * Process-local gate for orchestrator-wake reservation, progress cap, and
 * in-flight ownership. Shared across independently created hook instances in
 * the same JS process via globalThis + Symbol.for.
 */
import type { ContinuationModelSelection } from '../task-session-manager/continuation-model-selection';
export type WakeProgressState = {
    unchangedWakeCount: number;
    lastFingerprint: string | undefined;
    stopped: boolean;
    /** Set when a wake was reserved; next busy preserves the cap. */
    expectingWakeBusy: boolean;
    observedModel: ContinuationModelSelection | undefined;
};
export declare function getWakeProgress(sessionID: string): WakeProgressState;
/**
 * Atomically claim the single in-flight evaluation slot for a session.
 * Returns an owner token, or null if another evaluation owns the slot.
 */
export declare function tryBeginWakeEvaluation(sessionID: string): symbol | null;
/**
 * Release an in-flight evaluation only when still owned by `owner`.
 */
export declare function releaseWakeEvaluation(sessionID: string, owner: symbol): void;
/**
 * Retry an evaluation that lost the shared in-flight reservation. Registering
 * and checking the reservation happen against the same store, so an owner
 * release cannot be missed between them.
 */
export declare function retryAfterWakeEvaluation(sessionID: string, retry: () => void): () => void;
/**
 * Record a wake reservation before promptAsync. Owner-safe: only the current
 * in-flight owner may commit. Updates fingerprint accounting and marks that
 * the next busy should preserve (not rearm) the no-progress cap.
 */
export declare function commitWakeReservation(sessionID: string, owner: symbol, fingerprint: string): boolean;
/** Host fingerprint changed: reset the two-wake no-progress cap. */
export declare function noteHostProgress(sessionID: string, fingerprint: string): void;
/**
 * Whether busy belongs to a scheduler wake. The marker persists through
 * duplicate status delivery from independently-created hook instances.
 */
export declare function isExpectingWakeBusy(sessionID: string): boolean;
/** Clear the scheduler busy marker once the corresponding idle arrives. */
export declare function clearExpectingWakeBusy(sessionID: string): void;
/** External user activity or genuine lifecycle cleanup rearms the cap. */
export declare function rearmWakeProgress(sessionID: string): void;
export declare function setObservedWakeModel(sessionID: string, model: ContinuationModelSelection | undefined): void;
export declare function getObservedWakeModel(sessionID: string): ContinuationModelSelection | undefined;
/** Full session cleanup (deletion or disposal). */
export declare function clearWakeSession(sessionID: string): void;
/** Server/instance disposal: drop all process-local wake state. */
export declare function clearAllWakeSessions(): void;
/** Test seam. */
export declare function resetOrchestratorWakeGateForTests(): void;
