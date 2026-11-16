import { CLI_LANGUAGES } from './types';
export declare function findSgCliPathSync(): string | null;
export declare function getSgCliPath(): string;
export declare function setSgCliPath(path: string): void;
export { CLI_LANGUAGES };
export declare const DEFAULT_TIMEOUT_MS = 300000;
export declare const DEFAULT_MAX_OUTPUT_BYTES: number;
export declare const DEFAULT_MAX_MATCHES = 500;
export declare const LANG_EXTENSIONS: Record<string, string[]>;
export interface EnvironmentCheckResult {
    cli: {
        available: boolean;
        path: string;
        error?: string;
    };
}
