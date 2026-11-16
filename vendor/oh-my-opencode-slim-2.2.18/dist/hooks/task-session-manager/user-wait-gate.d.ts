/**
 * Process-local gate for explicit wait_for_user HITL latches.
 *
 * Scoped via globalThis + Symbol.for so independently created hook instances
 * in the same JS process share wait state. Does not claim cross-process or
 * restart durability.
 */
/**
 * Block automatic orchestrator wakes for a text-only HITL boundary until a
 * distinct real external user message opens the next epoch.
 */
export declare function beginUserWait(sessionID: string): void;
export declare function hasUserWait(sessionID: string): boolean;
/**
 * Clear wait_for_user for a real external user message.
 * Idempotent per (sessionID, identity). Returns true when this call cleared
 * wait state.
 */
export declare function clearUserWaitForMessage(sessionID: string, identity: string | object): boolean;
/**
 * Full session cleanup (genuine deletion). Clears wait state and rearm
 * identity so a later session id reuse is not pinned to a prior message.
 */
export declare function clearUserWait(sessionID: string): void;
/** Test seam: wipe process-local gate state between cases. */
export declare function resetUserWaitGateForTests(): void;
