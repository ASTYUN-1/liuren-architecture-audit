export declare class SessionLifecycle {
    #private;
    constructor(log: (msg: string, meta?: Record<string, unknown>) => void);
    onSessionDeleted(callback: (sessionId: string) => void): void;
    dispatchSessionDeleted(sessionId: string): void;
    markPending(sessionId: string): void;
    /** Atomic — only one caller gets true per markPending call. */
    consumePending(sessionId: string): boolean;
    clearSession(sessionId: string): void;
}
