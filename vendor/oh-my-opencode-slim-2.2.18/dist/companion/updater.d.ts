import type { CompanionConfig } from '../config/schema';
export interface CompanionManifest {
    version: string;
    tag: string;
    repo: string;
    checksums?: Record<string, string>;
}
export type CompanionUpdateResult = {
    status: 'installed';
    binaryPath: string;
    version: string;
} | {
    status: 'current';
    binaryPath: string;
    version: string;
} | {
    status: 'skipped';
    reason: string;
    binaryPath?: string;
} | {
    status: 'failed';
    error: string;
    binaryPath: string;
};
export declare const COMPANION_MANIFEST: CompanionManifest;
export declare function getCompanionTarget(): string | null;
export declare function getCompanionBinaryPath(): string;
export declare function loadCompanionManifestFromPackageRoot(packageRoot: string): CompanionManifest | null;
export declare function ensureCompanionVersion(options: {
    config?: CompanionConfig;
    manifest?: CompanionManifest;
    dryRun?: boolean;
    downloadTimeoutMs?: number;
    lockTimeoutMs?: number;
    lockStaleMs?: number;
}): Promise<CompanionUpdateResult>;
