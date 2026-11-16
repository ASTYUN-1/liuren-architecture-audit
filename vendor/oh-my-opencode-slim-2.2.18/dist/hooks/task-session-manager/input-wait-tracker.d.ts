export declare function createInputWaitTracker(options: {
    shouldManageSession: (sessionID: string) => boolean;
    /** Cancel delayed idle work when an input wait arms. */
    invalidateIdle: (sessionID: string) => void;
}): {
    beginUserWait: (sessionID: string) => void;
    trackInputWait: (event: {
        type: string;
        properties?: {
            id?: string;
            requestID?: string;
            sessionID?: string;
        };
    }) => void;
    hasInputWait: (sessionID: string) => boolean;
    clearInputWaits: (sessionID: string) => void;
    waitsByParent: Map<string, Set<string | symbol>>;
};
