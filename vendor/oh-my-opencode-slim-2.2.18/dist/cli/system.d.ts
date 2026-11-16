export declare function resolveOpenCodePath(environment?: NodeJS.ProcessEnv): string;
export declare function isOpenCodeInstalled(environment?: NodeJS.ProcessEnv): Promise<boolean>;
export declare function isTmuxInstalled(): Promise<boolean>;
export declare function getOpenCodeVersion(): Promise<string | null>;
export declare function getOpenCodePath(): string | null;
export declare function fetchLatestVersion(packageName: string): Promise<string | null>;
