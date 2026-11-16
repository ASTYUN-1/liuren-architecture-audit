import { type ToolDefinition } from '@opencode-ai/plugin';
interface WaitForUserToolOptions {
    shouldManageSession: (sessionID: string) => boolean;
    resolveAgentName?: (agent: string) => string;
    registerSessionAsOrchestrator?: (sessionID: string) => void;
    beginUserWait: (sessionID: string) => void;
    hasOutstandingBackgroundTasks?: (sessionID: string) => boolean;
    waitForUserGuardEnabled?: boolean;
}
export declare function createWaitForUserTool(options: WaitForUserToolOptions): Record<'wait_for_user', ToolDefinition>;
export {};
