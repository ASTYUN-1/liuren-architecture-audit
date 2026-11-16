import type { ChildProcess } from 'node:child_process';
export interface CrossSpawnResult {
    proc: ChildProcess;
    /** Collects all stdout into a string */
    stdout: () => Promise<string>;
    /** Collects all stderr into a string */
    stderr: () => Promise<string>;
    /** Resolves when process exits with exit code */
    exited: Promise<number>;
    /** Kill the process */
    kill: (signal?: NodeJS.Signals | number) => boolean;
    /** Current exit code or null if running */
    get exitCode(): number | null;
}
export interface ResolvedWindowsCommand {
    /** Absolute path of the executable (or shim) that was found. */
    file: string;
    /**
     * True when `file` is a `.cmd`/`.bat` shim that only cmd.exe can
     * interpret; the caller must spawn it through cmd.exe with a quoted
     * command line instead of passing it to spawn() directly.
     */
    viaCmdShell: boolean;
}
/**
 * Resolve a bare command name against PATH and PATHEXT the way cmd.exe
 * does, so spawn() can launch it on Windows.
 *
 * child_process.spawn only starts real executables; it cannot run the
 * extensionless sh and `.cmd` shims that npm-style installs leave on PATH
 * (for example `bun` installed via `npm install -g bun` exposes only
 * `bun.cmd` next to the real `bun.exe` buried in node_modules). A raw
 * spawn('bun') then fails with ENOENT even though bun runs fine in a
 * shell, which silently breaks bun-based flows such as the auto-updater.
 *
 * Walks PATH entries in order; within each entry, tries PATHEXT
 * extensions in declared order. PATH entries are split the way cmd.exe
 * reads them (quoted entries may contain `;`, empty entries mean the
 * current directory — see splitWindowsPath). The first directory
 * containing any match wins, and the matched extension decides whether
 * the file is directly spawnable (`.exe`/`.com`) or must run through
 * cmd.exe (`.cmd`/`.bat`).
 */
export declare function resolveWindowsCommand(command: string, pathEnv?: string, pathExtEnv?: string): ResolvedWindowsCommand | undefined;
/**
 * Builds the full command line handed to `cmd.exe /d /s /c`. The whole
 * line is wrapped in one outer pair of quotes because cmd's /s
 * processing strips the first and the last quote of the /c payload:
 * without the outer pair, a spaced path like `"C:\Program
 * Files\...\bun.cmd"` loses its quotes and the spawn fails (verified on
 * Windows). Exported for unit tests only.
 */
export declare function buildWindowsCommandLine(file: string, args: string[]): string;
/**
 * Cross-runtime spawn that works in both Bun and Node.js.
 * API mimics Bun.spawn but uses node:child_process internally.
 *
 * On Windows, bare command names are resolved against PATH/PATHEXT first
 * (see resolveWindowsCommand) so npm-installed CLIs that only expose
 * `.cmd` shims still run. Non-Windows platforms and explicit paths are
 * passed through unchanged.
 */
export declare function crossSpawn(command: string[], options?: {
    stdout?: 'pipe' | 'inherit' | 'ignore';
    stderr?: 'pipe' | 'inherit' | 'ignore';
    stdin?: 'pipe' | 'inherit' | 'ignore';
    cwd?: string;
    env?: Record<string, string | undefined>;
}): CrossSpawnResult;
/**
 * Cross-runtime file write that works in both Bun and Node.js.
 *
 * Order matters: Buffer is checked before treating the remainder as
 * ArrayBuffer so Buffer slices are written as-is (no parent-buffer copy).
 * Remaining union member is treated as ArrayBuffer without `instanceof`,
 * which fails for cross-realm ArrayBuffers.
 */
export declare function crossWrite(path: string, data: ArrayBuffer | Buffer | string): Promise<void>;
