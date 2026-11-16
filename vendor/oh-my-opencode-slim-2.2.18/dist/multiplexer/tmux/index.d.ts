/**
 * Tmux multiplexer implementation
 */
import type { MultiplexerLayout } from '../../config/schema';
import type { Multiplexer, PaneResult, PaneSpawnOptions } from '../types';
export declare class TmuxMultiplexer implements Multiplexer {
    readonly type: 'tmux';
    private binaryPath;
    private hasChecked;
    private storedLayout;
    private storedMainPaneSize;
    private targetPane;
    private layoutTimers;
    private paneTargets;
    constructor(layout?: MultiplexerLayout, mainPaneSize?: number);
    isAvailable(): Promise<boolean>;
    isInsideSession(): boolean;
    spawnPane(sessionId: string, description: string, serverUrl: string, directory: string, options?: PaneSpawnOptions): Promise<PaneResult>;
    closePane(paneId: string): Promise<boolean>;
    applyLayout(layout: MultiplexerLayout, mainPaneSize: number): Promise<void>;
    private scheduleLayout;
    private applyLayoutNow;
    private runTmux;
    private getBinary;
    private splitPane;
    private targetArgs;
}
