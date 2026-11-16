import type { CompanionConfig } from '../config/schema';
export declare function stateFilePath(): string;
export declare function resolveCompanionBinaryPath(config?: CompanionConfig): string | null;
/**
 * Tracks live agent activity per session and mirrors it to the companion
 * state file. Source of truth is OpenCode's session.status events: every
 * spawned specialist (foreground or background) runs in its own session,
 * which reports busy/idle independently. Tool-call lifecycles are NOT used
 * because background Task launches return immediately while the agent keeps
 * running in its child session.
 */
export declare class CompanionManager {
    private readonly id;
    private readonly cwd;
    private status;
    /** sessionId → agent name, for sessions currently busy. */
    private readonly busyAgentSessions;
    private readonly config?;
    private companionProcess;
    private wasSpawner;
    private spawnedCompanionPid;
    constructor(sessionId: string, cwd: string, config?: CompanionConfig);
    onLoad(): void;
    /**
     * Register this manager behind a single process `exit` listener. Re-inits for
     * the same OpenCode session dispose the superseded manager immediately so its
     * detached child does not survive until process exit.
     */
    private registerActiveManager;
    private static disposeActiveManagers;
    /**
     * Feed every session.status event here, with the agent name resolved
     * from sessionAgentMap. Orchestrator sessions drive overall status;
     * specialist sessions drive the per-agent GIF grid.
     */
    onSessionStatus(input: {
        sessionId?: string;
        agent?: string;
        status?: string;
    }): void;
    onSessionDeleted(sessionId: string | undefined): void;
    onWaitingInput(): void;
    onInputResolved(): void;
    onExit(): void;
    private removeOwnedPidFileIfNoSessionsRemain;
    /** One entry per running agent instance (two fixers → two cells). */
    private activeAgents;
    private flush;
    private spawnIfAvailable;
}
