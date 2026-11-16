import { getCompanionBinaryPath, getCompanionTarget } from '../companion/updater';
import type { ConfigMergeResult, InstallConfig } from './types';
export { getCompanionBinaryPath, getCompanionTarget };
export declare function installCompanion(config: InstallConfig): Promise<ConfigMergeResult>;
