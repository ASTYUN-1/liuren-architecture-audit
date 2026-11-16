/**
 * Zellij multiplexer implementation
 *
 * Creates panes for sub-agent sessions in Zellij.
 *
 * Requires Zellij >= 0.44.1: `isAvailable()` parses `zellij --version` and
 * rejects older releases whose CLI lacks the stable pane-id targeting used
 * here (`rename-pane <name> -p <paneId>`, `write-chars <chars> -p <paneId>`,
 * `list-panes --json --tab --all` with stable `tab_id`, and
 * `new-pane --tab-id` for cross-tab targeting; `--tab-id` only exists in
 * 0.44.1+). No `focus-pane` or `current-tab-info` calls are made — the former
 * is invalid CLI syntax and the latter is client-bound and fails from pane
 * child processes.
 *
 * The default mode creates a dedicated "opencode-agents" tab:
 * - First sub-agent uses the default pane from new-tab
 * - Subsequent sub-agents create new panes
 * - User stays in their original tab (resolved from the parent pane's
 *   ZELLIJ_PANE_ID via list-panes)
 *
 * The optional "current-tab" mode creates panes in the tab containing the
 * parent OpenCode pane instead.
 */
import type { MultiplexerLayout, ZellijPaneMode } from '../../config/schema';
import type { Multiplexer, PaneResult } from '../types';
export declare class ZellijMultiplexer implements Multiplexer {
    private readonly paneMode;
    readonly type: 'zellij';
    private binaryPath;
    private availabilityPromise;
    private agentTabId;
    private firstPaneId;
    private firstPaneUsed;
    private parentTabId;
    private parentTabResolved;
    private readonly parentPaneId;
    private readonly paneDirection;
    /**
     * Serializes pane-creation sequences that may switch Zellij tabs or move
     * client focus (new-tab, go-to-tab-by-id, new-pane). Concurrent spawns are
     * chained so a cross-tab create cannot race another create's focus restore.
     * Read-only queries (list-panes/list-tabs) never go through this queue.
     */
    private paneOpsChain;
    constructor(layout?: MultiplexerLayout, mainPaneSize?: number, paneMode?: ZellijPaneMode);
    isAvailable(): Promise<boolean>;
    /**
     * Resolve the zellij binary and gate on its version. Runs at most once per
     * adapter instance (the promise is cached by isAvailable).
     */
    private probeAvailability;
    /**
     * Parse and gate on the installed Zellij version. The adapter relies on
     * stable pane-id targeting that only exists in Zellij >= 0.44.1; older
     * releases (or unparsable version output) make the backend unavailable.
     */
    private hasSupportedVersion;
    private readVersion;
    isInsideSession(): boolean;
    spawnPane(sessionId: string, description: string, serverUrl: string, directory: string): Promise<PaneResult>;
    private spawnPaneUnlocked;
    private createPaneInCurrentTab;
    /**
     * Run `new-pane`, retrying once without the direction hint on failure.
     *
     * Zellij silently drops a `--direction` split once a tab is crowded (exit
     * code 0 but no `terminal_*` id on stdout), so a failed directed create is
     * retried without `--direction`, which lets Zellij place the pane in the
     * largest free space. The retry keeps `--name`, `--close-on-exit`, and the
     * command part — only the direction hint is dropped. Two failures (or one
     * failure with no direction configured) report `{ success: false }`.
     */
    private runNewPaneWithFallback;
    private createPaneInAgentTab;
    private runInPane;
    private ensureAgentTab;
    private listPanesJson;
    private getFirstPaneInTab;
    private findTabByName;
    private findTabByNameText;
    closePane(paneId: string): Promise<boolean>;
    applyLayout(_layout: MultiplexerLayout, _mainPaneSize: number): Promise<void>;
    private directionArgs;
    private tabIdArgs;
    private getParentTabId;
    private findTabIdForPane;
    private getBinary;
}
