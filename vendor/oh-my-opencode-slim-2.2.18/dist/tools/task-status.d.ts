import { type PluginInput, type ToolDefinition } from '@opencode-ai/plugin';
import type { BackgroundJobStore } from '../utils/background-job-store';
import type { TaskActivityTracker } from './task-activity';
export declare function createTaskStatusTool(options: {
    input: PluginInput;
    backgroundJobBoard: BackgroundJobStore;
    activityTracker?: TaskActivityTracker;
    now?: () => number;
    statusTimeoutMs?: number;
}): Record<'task_status', ToolDefinition>;
