/**
 * Per-instance session tokens used to invalidate delayed idle-reconciliation
 * timers when the parent becomes busy, errors, waits, or is deleted.
 */
export declare function createIdleSessionTokens(options?: {
    onInvalidate?: (sessionID: string) => void;
}): {
    getSessionToken: (sessionID: string) => symbol;
    isCurrentSessionToken: (sessionID: string, sessionToken: symbol) => boolean;
    invalidate: (sessionID: string) => void;
    onExternalUserMessage: (sessionID: string, messageIdentity: string | object) => void;
    clearSession: (sessionID: string) => void;
    disposeLocalState: () => void;
    sessionTokens: Map<string, symbol>;
};
