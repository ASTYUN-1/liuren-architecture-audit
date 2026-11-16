import type { Multiplexer } from '../types';
export interface CmuxSessionEvent {
    type: string;
    properties?: {
        info?: {
            id?: string;
            parentID?: string;
            title?: string;
            directory?: string;
            sessionID?: string;
        };
        part?: {
            sessionID?: string;
        };
        sessionID?: string;
        status?: {
            type: string;
        };
    };
}
interface BackgroundJobs {
    deferIfRunning(session: string): boolean;
    clearDeferredClose(session: string): void;
}
export interface CmuxSessionLifecycleOptions {
    now?: () => number;
    delay?: (milliseconds: number) => Promise<void>;
    deferredRetryMs?: number;
    deferredTtlMs?: number;
    /** @deprecated Missing status never establishes deletion. */
    missingGraceMs?: number;
    closeRetryMs?: number;
    closeRetryTtlMs?: number;
    closeRetryMaxAttempts?: number;
    orphanCooldownMs?: number;
    shutdownTimeoutMs?: number;
    isServerRunning?: (url: string) => Promise<boolean>;
    fetchStatuses?: () => Promise<Record<string, {
        type: string;
    }>>;
    permanentlyClosedSessions?: Set<string>;
}
export declare class CmuxSessionLifecycle {
    private readonly owner;
    private readonly multiplexer;
    private readonly resolveServerUrl;
    private readonly defaultDirectory;
    private readonly backgroundJobs?;
    private readonly store;
    private readonly policy;
    private readonly now;
    private readonly delay;
    private readonly injectedDelay;
    private readonly deferredRetryMs;
    private readonly deferredTtlMs;
    private readonly closeRetryMs;
    private readonly shutdownTimeoutMs;
    private readonly serverCheck;
    private readonly fetchStatuses;
    private pollTimer?;
    private polling;
    private cleanupPromise?;
    private disposed;
    private spawnGeneration;
    private readonly ownerGeneration;
    private readonly permanentlyClosedSessions?;
    private readonly serverScope;
    private readonly removeLatePaneObserver;
    private initialOrphansRecovered;
    constructor(owner: string, multiplexer: Multiplexer, resolveServerUrl: () => string | null, defaultDirectory: string, backgroundJobs?: BackgroundJobs | undefined, options?: CmuxSessionLifecycleOptions);
    onSessionCreated(event: CmuxSessionEvent): Promise<void>;
    onSessionStatus(event: CmuxSessionEvent): Promise<void>;
    onSessionDeleted(event: CmuxSessionEvent): Promise<void>;
    closeSessionFromCoordinator(session: string): Promise<void>;
    closeSessionPermanentlyFromCoordinator(session: string): Promise<void>;
    cleanup(): Promise<void>;
    /** Runs one status pass; exposed for deterministic lifecycle tests. */
    pollOnce(): Promise<void>;
    private spawn;
    private spawnOperation;
    private deferSpawn;
    private cancelDeferred;
    private reactivateOrphan;
    private activity;
    private requestClose;
    private attemptClose;
    private performClose;
    private settleClosedPane;
    private scheduleCooldown;
    private poll;
    private resumeTransferredClose;
    private applyCloseSettlement;
    private startPolling;
    private updatePolling;
    private waitForSettlements;
    private runCleanup;
    private cleanupRecordUntil;
    private scheduleRetryAfterCleanupTimeout;
    private attemptCloseWithoutTimer;
    private performCloseWithoutTimer;
    private adoptAndClose;
    private closeLatePane;
    private claimLatePaneOrphans;
    private recoverInitialOrphans;
    private recoverOrphans;
    private eventSession;
    private timer;
    private loadStatuses;
}
export {};
