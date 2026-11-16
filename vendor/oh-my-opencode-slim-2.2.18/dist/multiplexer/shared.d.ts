/**
 * Shared multiplexer infrastructure
 *
 * Functions used across tmux, zellij, and herdr backend adapters.
 * Extracted to eliminate copy-paste duplication and prevent drift.
 */
export declare function quoteShellArg(value: string): string;
/** Normalize Windows backslashes to / so sh -lc (MSYS2/Git Bash) doesn't treat them as escape chars. */
export declare function normalizePathForShell(directory: string): string;
export declare function buildOpencodeAttachCommand(sessionId: string, serverUrl: string, directory: string, executable?: string): string;
/**
 * Resolve the absolute path to the running OpenCode binary so child shells
 * (e.g. a kitty-launched window) don't need `opencode` on their PATH. Falls
 * back to the bare `opencode` name when no absolute path can be determined.
 */
export declare function resolveOpencodeExecutable(): string;
/**
 * Build the `[shell, ...shellArgs, command]` array for launching a command in
 * the user's interactive shell. OpenCode respects the user's shell when running
 * commands; multiplexer panes must do the same, otherwise a hardcoded `sh -c`
 * breaks under non-POSIX shells (fish, nu, powershell, ...) or misses login
 * startup files (where `opencode` may be on PATH).
 *
 * Mirrors OpenCode's own `Shell.args()` resolution:
 * - nu / fish: `<shell> -c <command>` (no login mode)
 * - zsh: login mode; zsh sources ~/.zshenv automatically, then we source
 *   .zshrc before running the command
 * - bash: login mode, sources bashrc, then runs command
 * - cmd: `cmd /c <command>`
 * - powershell: `pwsh -NoProfile -Command <command>`
 * - default (sh/dash/elvish/xonsh/...): `<shell> -c <command>`
 *
 * Note: the working directory is supplied by the launcher (e.g. kitty's
 * `--cwd`), not by a `cd` inside the shell command.
 */
export declare function buildShellLaunchArgs(command: string): string[];
export declare function resolveHostOpencodeBinary(options?: {
    override?: string;
    envOverride?: string;
    execPath?: string;
    argv0?: string;
    pathExists?: (path: string) => boolean;
}): string | null;
export declare function findBinary(binaryName: string, options?: {
    verify?: boolean;
}): Promise<string | null>;
export interface GracefulClosePaneOptions {
    /** Backend-specific Ctrl+C command args (binary prepended by caller). */
    ctrlC: string[];
    /** Backend-specific close/kill command args (binary prepended by caller). */
    close: string[];
    /** Accept exit code 1 as success (zellij/herdr treat "already closed" as 1). */
    acceptExitCode1?: boolean;
    /** Return true for empty/unknown paneId instead of false (zellij/herdr behavior). */
    emptyPaneReturnsTrue?: boolean;
    /** Env to pass to the kitten/kitty invocations (e.g. KITTY_LISTEN_ON). */
    env?: Record<string, string | undefined>;
}
export declare function gracefulClosePane(binary: string | null, paneId: string, options: GracefulClosePaneOptions): Promise<boolean>;
export interface SessionReadinessOptions {
    /** Override the per-attempt readiness probe (default: GET /session/status). */
    checkSessionReady?: (url: URL, sessionId: string, signal: AbortSignal) => Promise<boolean>;
    /** Injectable cancellation-safe delay for backoff between attempts. */
    delay?: (milliseconds: number) => Promise<void>;
    /** Per-attempt abort timeout in milliseconds (default 1000). */
    readinessAttemptTimeoutMs?: number;
    /**
     * Absolute deadline for the whole wait in milliseconds (default 2000).
     * The wait stops once `now()` passes `deadlineMs` after the first probe,
     * regardless of how many attempts remain, so a hanging probe can never
     * stretch the total beyond the deadline.
     */
    readinessDeadlineMs?: number;
    /** Injectable clock for deterministic deadline tests (default Date.now). */
    now?: () => number;
    /**
     * Abort the whole wait (e.g. manager cleanup/disposal). Resolves false;
     * in-flight probes are aborted through this signal.
     */
    signal?: AbortSignal;
}
/**
 * Poll the OpenCode `/session/status` endpoint until the child session is
 * attachable, bounded by an absolute deadline (default 2s) rather than a
 * fixed number of independently-timed attempts.
 *
 * Adapter contract: this gate is used by the generic pane adapters (tmux,
 * zellij, herdr, kitty). The cmux adapter is explicitly excluded: cmux
 * sessions are managed by CmuxSessionLifecycle, which has its own spawn
 * machinery (server health check plus deferred spawn retry with a TTL) and
 * never calls this function.
 *
 * Prevents the attach-before-ready race where `opencode attach --session
 * <id>` launches before the server has published the session and falls back
 * to the new-session picker TUI. Returns false when the session never became
 * ready within the deadline or when the caller's abort signal fires.
 */
export declare function waitForSessionReady(serverUrl: string, sessionId: string, options?: SessionReadinessOptions): Promise<boolean>;
