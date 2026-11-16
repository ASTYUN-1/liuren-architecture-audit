import { type PluginInput, type ToolDefinition } from '@opencode-ai/plugin';
import type { BackgroundJobStore } from '../utils/background-job-store';
interface TaskResultToolOptions {
    input: PluginInput;
    backgroundJobBoard: BackgroundJobStore;
}
export declare function createTaskResultTool(options: TaskResultToolOptions): Record<string, ToolDefinition>;
export {};
