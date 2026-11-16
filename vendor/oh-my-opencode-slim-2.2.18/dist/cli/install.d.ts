import type { InstallArgs, InstallConfig } from './types';
export declare function configureBackgroundSubagents(config: InstallConfig): Promise<{
    enabledNow: boolean;
    configuredTarget?: string;
}>;
export declare function shouldInstallCompanion(config: InstallConfig): Promise<boolean>;
export declare function install(args: InstallArgs): Promise<number>;
