import { type ToolDefinition } from '@opencode-ai/plugin';
import type { RevivedRunTracker } from '../hooks/task-session-manager/revived-run-tracker';
import type { BackgroundJobSupervisor } from '../utils/background-job-supervisor';
import { type TaskControlToolOptions } from './cancel-task';
export interface TaskReviveToolOptions extends TaskControlToolOptions {
    backgroundJobSupervisor?: BackgroundJobSupervisor;
    revivedRunTracker: RevivedRunTracker;
}
export declare function createTaskReviveTool(options: TaskReviveToolOptions): Record<'task_revive', ToolDefinition>;
