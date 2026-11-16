interface AutoUpdateInstallContext {
    installDir: string;
    packageJsonPath: string;
}
interface PreparedPackageUpdate {
    stagingDir: string;
    targetDir: string;
}
export declare function resolveInstallContext(runtimePackageJsonPath?: string | null): AutoUpdateInstallContext | null;
/**
 * Prepares the current install root for a clean re-install of the target version.
 * Returns the install directory to run `bun install` in.
 */
export declare function preparePackageUpdate(version: string, packageName?: string, runtimePackageJsonPath?: string | null, cacheIdentity?: string): PreparedPackageUpdate | null;
export declare function discardPreparedPackageUpdate(prepared: PreparedPackageUpdate): void;
export declare function publishPackageUpdate(prepared: PreparedPackageUpdate, version: string): string | null;
export declare function verifyInstalledPackage(installDir: string, version: string, packageName?: string): boolean;
export {};
