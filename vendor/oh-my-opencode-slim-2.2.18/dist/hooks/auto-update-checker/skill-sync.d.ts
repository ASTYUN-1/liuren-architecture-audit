export interface SkillSyncResult {
    installed: string[];
    skippedExisting: string[];
    failed: string[];
    staged: string[];
    adopted: string[];
    customized: string[];
    stagedThisSync: string[];
}
export interface SkillManifestEntry {
    status: 'managed' | 'customized' | 'deleted' | 'conflict';
    packageVersion: string;
    sourceHash: string;
    lastManagedHash: string;
    lastSeenHash: string;
    stagedPath?: string;
    updatedAt: string;
}
export interface SkillsManifest {
    schemaVersion: number;
    updatedAt: string;
    skills: Record<string, SkillManifestEntry>;
}
interface ManagedSkillSource {
    name: string;
    sourcePath: string;
}
interface SkillSyncOptions {
    skills?: ManagedSkillSource[];
    force?: boolean;
}
/**
 * Hashes of historically managed versions of skills.
 * When a release changes skill content, this table must be populated
 * from the published npm package tarballs to allow upgrading existing users.
 *
 * How to populate:
 * 1. Download previous releases of the npm package: `npm pack oh-my-opencode-slim@<version>`
 * 2. Compute directory hash for each legacy skill directory inside the unpacked tarball:
 *    `import { computeDirectoryHash } from './skill-sync';`
 *    `const hash = computeDirectoryHash('path/to/extracted/package/src/skills/<skill-name>');`
 * 3. Append the hash to the skill's string array below:
 *    ```typescript
 *    export const LEGACY_MANAGED_SKILL_HASHES: Record<string, string[]> = {
 *      'simplify': ['hash1', 'hash2'],
 *      'codemap': ['hash3']
 *    };
 *    ```
 */
export declare const LEGACY_MANAGED_SKILL_HASHES: Record<string, string[]>;
/**
 * Computes a deterministic SHA-256 hash of a directory's files.
 */
export declare function computeDirectoryHash(dirPath: string): string;
/**
 * Acquires a simple lock under .oh-my-opencode-slim.
 * Avoids stealing active locks purely by time; writes owner metadata
 * and only steals dead same-host pid if detectable.
 */
export declare function acquireLock(lockDir: string): boolean;
/**
 * Releases the lock.
 */
export declare function releaseLock(lockDir: string): void;
/**
 * Synchronizes bundled skills from the newly installed package root to OpenCode config skills directory.
 */
export declare function syncBundledSkillsFromPackage(packageRoot: string, options?: SkillSyncOptions): SkillSyncResult;
export {};
