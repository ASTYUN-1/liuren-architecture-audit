import type { PluginInput } from '@opencode-ai/plugin';
import type { MultiplexerConfig } from '../config/schema';
import { type SessionReadinessOptions } from '../multiplexer';
import type { BackgroundJobStore } from '../utils/background-job-store';
import { type CmuxSessionLifecycleOptions } from './cmux/session-lifecycle';
type BackgroundJobReader = Pick<BackgroundJobStore, 'getState' | 'deferIfRunning' | 'clearDeferredClose'>;
interface SessionEvent {
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
export declare function resetMultiplexerSessionManagerState(): void;
export type MultiplexerSessionManagerOptions = CmuxSessionLifecycleOptions & SessionReadinessOptions;
/**
 * Tracks child sessions and spawns/closes multiplexer panes for them.
 *
 * Uses session.status events for completion detection instead of polling,
 * with polling kept as a fallback for reliability.
 */
export declare class MultiplexerSessionManager {
    private readonly backgroundJobBoard?;
    private instanceId;
    private readonly resolveServerUrl;
    private directory;
    private multiplexer;
    private sessions;
    private knownSessions;
    private spawningSessions;
    private closingSessions;
    private permanentlyClosedSessions;
    private pollInterval?;
    private enabled;
    private cmuxLifecycle?;
    private readonly readiness;
    private readonly now;
    private readonly closeRetryMs;
    private readonly closeRetryMaxAttempts;
    private readonly shutdownTimeoutMs;
    private readinessAbort?;
    private cleanupInProgress;
    /**
     * Sessions that signaled `busy` while a spawn/readiness pass was in flight
     * (the busy handler defers to the pending pass). Consumed after the pass:
     * if the pass failed to attach a pane, the session is retried immediately
     * instead of being silently orphaned.
     */
    private readonly busyDuringSpawn;
    constructor(ctx: PluginInput, config: MultiplexerConfig, backgroundJobBoard?: BackgroundJobReader | undefined, options?: MultiplexerSessionManagerOptions);
    /** Fresh options for a readiness wait; the manager owns the abort signal. */
    private readinessOptions;
    /** Abort an in-flight readiness wait during cleanup or disposal. */
    private abortInFlightReadiness;
    onSessionCreated(event: SessionEvent): Promise<void>;
    onSessionStatus(event: SessionEvent): Promise<void>;
    onSessionDeleted(event: SessionEvent): Promise<void>;
    private startPolling;
    private stopPolling;
    private pollSessions;
    private retryDueCloses;
    private fetchSessionStatuses;
    private trackAndCloseStalePane;
    private closeSession;
    private performClose;
    private getOrCreateCloseState;
    private cancelFailedIdleClose;
    private respawnIfKnown;
    private isTrackedOrSpawning;
    private updatePolling;
    private isPollableSession;
    private getSessionId;
    private backgroundJobState;
    private shouldCloseNow;
    closeSessionFromCoordinator(sessionId: string): Promise<void>;
    /** Permanently close a wall-clock timed-out pane and block late busy respawn. */
    closeSessionPermanentlyFromCoordinator(sessionId: string): Promise<void>;
    cleanup(): Promise<void>;
    private waitForSettlements;
    cleanupOnInstanceDisposed(): Promise<void>;
}
/**
 * @deprecated Use MultiplexerSessionManager instead
 */
export declare const TmuxSessionManager: typeof MultiplexerSessionManager;
export {};
