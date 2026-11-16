/**
 * Activity event shapes the tracker consumes. `info.id` is the session id
 * for session-scoped events (session.*) but the message/step id for
 * message-scoped events (message.updated, step-finish); the session id for
 * those lives in `info.sessionID`.
 */
export interface ActivityEvent {
    type: string;
    properties?: {
        info?: {
            id?: string;
            sessionID?: string;
        };
        sessionID?: string;
        status?: {
            type?: string;
        };
    };
}
/**
 * Resolves the session id from an event, keying message/step-scoped events
 * by `info.sessionID` (never the message id) and session-scoped events by
 * `info.id`. Returns undefined when no session id is present.
 */
export declare function resolveEventSessionID(event: ActivityEvent): string | undefined;
/** True when the event is observable child activity that refreshes the stuck timer. */
export declare function shouldRecordActivity(event: ActivityEvent): boolean;
/** True when the session is gone and its activity bookkeeping can be dropped. */
export declare function shouldForgetActivity(event: ActivityEvent): boolean;
export declare class TaskActivityTracker {
    private readonly activity;
    touch(sessionID: string, now?: number): void;
    lastActivityAt(sessionID: string): number | undefined;
    forget(sessionID: string): void;
}
/**
 * Applies an event to the tracker: records activity for live child signals
 * keyed by session id, forgets sessions on deletion. This mirrors the wiring
 * in src/index.ts so the event policy is testable in isolation.
 */
export declare function applyActivityEvent(tracker: TaskActivityTracker, event: ActivityEvent, now?: number): void;
