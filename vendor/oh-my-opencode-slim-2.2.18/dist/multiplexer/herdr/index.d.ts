/**
 * Herdr multiplexer implementation
 *
 * Splits panes for sub-agent sessions in Herdr.
 *
 * Herdr is an agent-aware terminal multiplexer (workspaces → tabs → panes).
 * Pane IDs use the format `w<workspace>:p<pane>`. The CLI outputs
 * newline-delimited JSON; `pane split` returns a `pane_info` result whose
 * `pane.pane_id` field is the new pane's ID.
 *
 * Environment detection: Herdr injects `HERDR_ENV=1` and `HERDR_PANE_ID`
 * into every pane it manages.
 */
import type { MultiplexerLayout } from '../../config/schema';
import type { Multiplexer, PaneResult } from '../types';
export declare class HerdrMultiplexer implements Multiplexer {
    readonly type: 'herdr';
    private binaryPath;
    private hasChecked;
    private readonly parentPaneId;
    private layout;
    private paneDirection;
    private agentAreaPaneId;
    private spawnMutex;
    constructor(layout?: MultiplexerLayout, mainPaneSize?: number);
    isAvailable(): Promise<boolean>;
    isInsideSession(): boolean;
    spawnPane(sessionId: string, description: string, serverUrl: string, directory: string): Promise<PaneResult>;
    private doSpawn;
    closePane(paneId: string): Promise<boolean>;
    applyLayout(layout: MultiplexerLayout, _mainPaneSize: number): Promise<void>;
    private runSplit;
    private targetPaneArg;
    private getBinary;
}
