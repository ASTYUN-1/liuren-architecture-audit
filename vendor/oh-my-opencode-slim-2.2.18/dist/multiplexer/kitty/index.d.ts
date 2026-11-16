/**
 * Kitty multiplexer implementation
 *
 * Uses kitty's remote-control CLI (`kitten @`) to manage windows.
 * A kitty WINDOW is the 1:1 equivalent of a tmux pane (full PTY).
 *
 * Requires `allow_remote_control` **and** `listen_on` in kitty.conf. When
 * `listen_on` is set, kitty exports `KITTY_LISTEN_ON` to its child processes
 * (including OpenCode). The plugin passes that env through to `kitten @` so
 * remote control goes via the socket instead of the controlling terminal,
 * because OpenCode spawns subagent commands in a process detached from the
 * kitty window's tty, where the tty-based remote-control path does not work.
 *
 * Layout mapping:
 * - main-vertical → tall layout (full-height main pane on left, side panes stacked on right)
 * - main-horizontal → fat layout (full-width main pane on top, side panes tiled below)
 * - tiled → grid layout (equal-sized cells)
 * - even-horizontal → horizontal layout (all panes side-by-side)
 * - even-vertical → vertical layout (all panes stacked)
 *
 * Maps each plugin layout to the closest kitty built-in layout. kitty has no
 * per-window layout API, so the chosen layout is applied as a global change to
 * the active tab (overriding whatever layout was active there).
 */
import type { MultiplexerLayout } from '../../config/schema';
import type { Multiplexer, PaneResult } from '../types';
export declare class KittyMultiplexer implements Multiplexer {
    readonly type: 'kitty';
    private binaryPath;
    private hasChecked;
    private storedLayout;
    private appliedLayout;
    constructor(layout?: MultiplexerLayout, mainPaneSize?: number);
    isAvailable(): Promise<boolean>;
    isInsideSession(): boolean;
    /**
     * The kitty multiplexer needs `listen_on` configured in kitty.conf so kitty
     * exports `KITTY_LISTEN_ON` to its children. Without it, `kitten @` cannot
     * reach kitty from OpenCode's detached subagent processes (the tty path does
     * not work). Returns true when the socket env is present.
     */
    private hasListenOn;
    spawnPane(sessionId: string, description: string, serverUrl: string, directory: string): Promise<PaneResult>;
    closePane(paneId: string): Promise<boolean>;
    applyLayout(layout: MultiplexerLayout, mainPaneSize: number): Promise<void>;
    private runKitty;
    private ensureLayout;
    private getBinary;
    /**
     * Build the env for `kitten @` invocations. When kitty's `listen_on` socket
     * is configured, kitty sets `KITTY_LISTEN_ON` in its child processes (which
     * includes OpenCode). We pass that env through so remote control goes via the
     * socket instead of the controlling terminal (required for the plugin's
     * detached subagent processes). When the var is absent we return undefined
     * and `kitten @` falls back to the tty path.
     */
    private kittyEnv;
}
