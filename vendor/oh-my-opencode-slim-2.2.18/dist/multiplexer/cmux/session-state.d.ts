import type { PaneResult } from '../types';
import type { CmuxCloseIntent } from './close-policy';
export type CmuxSpawnState = 'known' | 'spawning' | 'attached' | 'failed';
export type CmuxLifecycleState = 'active' | 'deleted' | 'orphaned';
export interface CmuxDeferredSpawn {
    deadline: number;
    generation: number;
    timer?: {
        cancel(): void;
    };
}
export interface CmuxSessionRecord {
    session: string;
    owner: string;
    /** Monotonic lifecycle owner fence used for late-pane takeover. */
    ownerGeneration?: number;
    parent: string;
    title: string;
    directory: string;
    /** Server scope that created the pane. */
    serverUrl?: string;
    paneId?: string;
    spawnState: CmuxSpawnState;
    lifecycle: CmuxLifecycleState;
    attachedAt?: number;
    lastActivityAt: number;
    activityVersion: number;
    idleConsecutive: number;
    statusMissingSince?: number;
    /** Set only by a coordinator terminal outcome, not by status absence. */
    terminalConfirmed?: boolean;
    deferredSpawn?: CmuxDeferredSpawn;
    closeIntent?: CmuxCloseIntent;
    closeTimer?: {
        cancel(): void;
    };
    closePromise?: Promise<void>;
    /** Result of a close that settled after ownership changed. */
    closeSettlement?: CmuxCloseSettlement;
    spawnPromise?: Promise<PaneResult>;
    /** A pane returned by a spawn generation that can no longer be adopted. */
    latePaneCleanup?: boolean;
}
export interface CmuxCloseSettlement {
    paneId: string;
    closed: boolean;
}
export declare class CmuxSessionStore {
    registerOwner(): number;
    consumeCloseSettlement(record: CmuxSessionRecord): CmuxCloseSettlement | undefined;
    claimCreated(record: CmuxSessionRecord): boolean;
    get(session: string): CmuxSessionRecord | undefined;
    ownedBy(owner: string): CmuxSessionRecord[];
    observeLatePaneOrphans(directory: string, serverUrl: string | (() => string | undefined), callback: (record: CmuxSessionRecord) => void, ownerGeneration?: number): () => void;
    notifyLatePaneOrphan(record: CmuxSessionRecord): void;
    claimOrphans(owner: string, directory: string, serverUrl?: string | (() => string | undefined), ownerGeneration?: number): CmuxSessionRecord[];
    claimLatePaneOrphans(owner: string, directory: string, serverUrl: string, ownerGeneration?: number, expectedRecord?: CmuxSessionRecord): CmuxSessionRecord[];
    markAttached(session: string, paneId: string, now: number): void;
    markActivity(session: string, now: number): void;
    markDeleted(session: string): void;
    markOrphaned(session: string): void;
    removeAfterConfirmedClose(session: string): boolean;
    removeWithoutPane(session: string): boolean;
    resetForTests(): void;
}
