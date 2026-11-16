import type { BackgroundJobLease } from '../../utils/background-job-board';
import type { BackgroundJobStore } from '../../utils/background-job-store';
import type { BackgroundJobSupervisor } from '../../utils/background-job-supervisor';
import type { BackgroundTaskConcurrencyTicket } from '../../utils/background-task-concurrency';
export interface EarlyTaskRegistration {
    taskID: string;
    generation: number;
    backgroundJobBoard: BackgroundJobStore;
    backgroundJobSupervisor?: BackgroundJobSupervisor;
}
export interface PendingTaskCall {
    callId: string;
    parentSessionId: string;
    agentType: string;
    label: string;
    /** Untruncated objective text the label was derived from; board comparison
     *  uses this so long exact duplicates are not missed. */
    fullObjective?: string;
    background: boolean;
    /** Deletion epoch observed when this native task call started. */
    lifecycleEpoch: number;
    resumedTaskId?: string;
    relaunchLease?: BackgroundJobLease;
    /** Board generation that owns the relaunch lease. */
    releaseLease?: (lease: BackgroundJobLease) => boolean;
    concurrencyTicket?: BackgroundTaskConcurrencyTicket;
    earlyRegisteredTaskID?: string;
    earlyRegistration?: EarlyTaskRegistration;
    earlyRegistrationRejected?: boolean;
}
export interface PendingCallTracker {
    add(call: PendingTaskCall): void;
    take(callId?: string, parentSessionId?: string, ownerBoard?: BackgroundJobStore): PendingTaskCall | undefined;
    release(call: PendingTaskCall): void;
    peekByParent(parentSessionId: string): PendingTaskCall | undefined;
    peekByParentAndAgent(parentSessionId: string, agentHint?: string): PendingTaskCall | undefined;
    adoptEarlyRegistrations(backgroundJobBoard: BackgroundJobStore, backgroundJobSupervisor?: BackgroundJobSupervisor): void;
    clearSession(sessionId: string): void;
    clearAll(): void;
    pendingCallId(sessionID?: string, callID?: string): string;
}
export declare function createPendingCallTracker(options?: {
    releaseLease?: (lease: BackgroundJobLease) => boolean;
}): PendingCallTracker;
