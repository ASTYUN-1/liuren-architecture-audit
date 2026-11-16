import type { MultiplexerLayout } from '../../config/schema';
import { crossSpawn } from '../../utils/compat';
import type { Multiplexer, PaneResult } from '../types';
export interface CmuxReadinessOptions {
    checkSessionReady?: (url: URL, sessionId: string, signal: AbortSignal) => Promise<boolean>;
    delay?: (milliseconds: number) => Promise<void>;
    readinessAttemptTimeoutMs?: number;
    opencodeBinary?: string;
    pathExists?: (path: string) => boolean;
}
export interface CommandResult {
    exitCode: number;
    stdout: string;
    stderr: string;
}
export interface CommandRunner {
    run(argv: string[]): Promise<CommandResult>;
}
export interface CmuxIdentity {
    workspaceId: string;
    paneId: string;
    surfaceId: string;
    socketPath: string;
}
export interface CmuxClient {
    version(): Promise<string | null>;
    getVersionError?(): 'unavailable' | 'hard';
    identify(): Promise<CmuxIdentity | null>;
    getIdentifyError?(): 'unavailable' | 'hard';
    createSurface(input: {
        workspaceId: string;
        targetSurfaceId: string;
        direction: 'right' | 'down';
        focus: false;
    }, socketPath?: string): Promise<{
        paneId: string;
        surfaceId: string;
    } | null>;
    getCreateError?(): 'not_found' | 'unavailable' | 'invalid_state' | 'hard';
    respawnSurface(workspaceId: string, surfaceId: string, command: string, socketPath?: string): Promise<boolean>;
    closeSurface(workspaceId: string, surfaceId: string, socketPath?: string): Promise<'closed' | 'not_found' | 'failed'>;
    equalizeSplits(params: {
        workspace_id: string;
        orientation: 'vertical';
    }, socketPath?: string): Promise<boolean>;
}
export declare class CmuxMultiplexer implements Multiplexer {
    private readonly client;
    readonly type: 'cmux';
    private versionAvailable;
    private availabilityError;
    private readonly checkSessionReady;
    private readonly delay;
    private readonly readinessAttemptTimeoutMs;
    private readonly opencodeBinary;
    constructor(client?: CmuxClient, options?: CmuxReadinessOptions);
    isAvailable(): Promise<boolean>;
    isInsideSession(): boolean;
    spawnPane(sessionId: string, _description: string, serverUrl: string, directory: string): Promise<PaneResult>;
    closePane(paneId: string): Promise<boolean>;
    applyLayout(_layout: MultiplexerLayout, _mainPaneSize: number): Promise<void>;
    private cleanupPane;
    private waitForSession;
    private equalize;
}
export declare class SpawnCommandRunner implements CommandRunner {
    private readonly timeoutMs;
    private readonly spawn;
    constructor(timeoutMs?: number, spawn?: typeof crossSpawn);
    run(argv: string[]): Promise<CommandResult>;
}
export declare class CliCmuxClient implements CmuxClient {
    private readonly runner;
    private binary;
    private versionError;
    private identifyError;
    private lastRunThrew;
    private createError;
    constructor(runner?: CommandRunner, binary?: string);
    version(): Promise<string | null>;
    getVersionError(): 'unavailable' | 'hard';
    identify(): Promise<CmuxIdentity | null>;
    getIdentifyError(): 'unavailable' | 'hard';
    createSurface(input: {
        workspaceId: string;
        targetSurfaceId: string;
        direction: 'right' | 'down';
        focus: false;
    }, socketPath?: string): Promise<{
        paneId: string;
        surfaceId: string;
    } | null>;
    getCreateError(): 'not_found' | 'unavailable' | 'invalid_state' | 'hard';
    respawnSurface(workspaceId: string, surfaceId: string, command: string, socketPath?: string): Promise<boolean>;
    closeSurface(workspaceId: string, surfaceId: string, socketPath?: string): Promise<'closed' | 'not_found' | 'failed'>;
    equalizeSplits(params: {
        workspace_id: string;
        orientation: 'vertical';
    }, socketPath?: string): Promise<boolean>;
    private run;
}
export declare function resetCmuxStateForTests(): void;
