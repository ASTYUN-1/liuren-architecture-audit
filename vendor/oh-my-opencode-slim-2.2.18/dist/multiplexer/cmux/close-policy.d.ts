export type CmuxCloseReason = 'idle' | 'deleted' | 'cleanup';
export interface CmuxCloseIntent {
    reason: CmuxCloseReason;
    expectedActivityVersion: number;
    attempts: number;
    deadline: number;
    phase: 'pending' | 'cooldown';
    nextAttemptAt: number;
    cooldowns: number;
}
export declare class CmuxClosePolicy {
    private readonly budgetMs;
    private readonly maxAttempts;
    constructor(budgetMs?: number, maxAttempts?: number);
    request(reason: CmuxCloseReason, version: number, now: number, current?: CmuxCloseIntent): CmuxCloseIntent;
    activity(intent?: CmuxCloseIntent): CmuxCloseIntent | undefined;
    failed(intent: CmuxCloseIntent, now: number): CmuxCloseIntent;
    resume(intent: CmuxCloseIntent, now: number): CmuxCloseIntent;
    complete(): undefined;
}
