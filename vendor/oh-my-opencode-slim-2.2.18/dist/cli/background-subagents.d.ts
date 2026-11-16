export type BackgroundSubagentsMode = 'ask' | 'yes' | 'no';
export type ShellKind = 'bash' | 'fish' | 'zsh';
export declare function isBackgroundSubagentsEnabled(value: string | undefined): boolean;
export declare function detectShellKind(shell: string | undefined): ShellKind | undefined;
export declare function detectBackgroundSubagentsTarget(env?: NodeJS.ProcessEnv): string | undefined;
export declare function getBackgroundSubagentsBlock(targetPath: string): string;
export declare function manualBackgroundSubagentsInstructions(options?: {
    targetPath?: string;
    shell?: ShellKind;
}): string;
export declare function expandHomePath(targetPath: string): string;
export declare function upsertBackgroundSubagentsBlock(content: string, block: string): string;
export declare function writeBackgroundSubagentsBlock(targetPath: string): void;
