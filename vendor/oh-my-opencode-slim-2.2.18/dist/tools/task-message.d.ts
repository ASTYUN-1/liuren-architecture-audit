import { type PluginInput, type ToolDefinition } from '@opencode-ai/plugin';
import type { BackgroundJobStore } from '../utils/background-job-store';
export declare function createTaskMessageTool(options: {
    input: PluginInput;
    backgroundJobBoard: BackgroundJobStore;
    messageTimeoutMs?: number;
}): Record<'task_message', ToolDefinition>;
