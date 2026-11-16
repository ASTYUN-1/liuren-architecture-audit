export declare const TMUX_PANE_REGISTRATION_TTL_MS = 30000;
export declare function getTmuxPaneRegistrationPath(sessionId: string): string;
export declare function recordTmuxPane(sessionId: string, paneId: string, ownerPid?: number): boolean;
export declare function readTmuxPane(sessionId: string, now?: number): string | undefined;
export declare function removeTmuxPane(sessionId: string, paneId: string, ownerPid?: number): void;
