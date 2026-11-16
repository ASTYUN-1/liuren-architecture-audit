import type { Server } from 'node:http';
import type { PluginInput } from '@opencode-ai/plugin';
import type { PluginConfig } from '../config';
import { type DashboardConfig } from './dashboard';
import type { InterviewSessionRuntime } from './runtime';
import { createInterviewService } from './service';
export declare function createDashboardManager(ctx: PluginInput, config: PluginConfig, dashboardPort: number, outputFolder: string, options?: {
    runtime?: InterviewSessionRuntime;
    sessionClient?: DashboardConfig['sessionClient'];
    /** Already-listening server for the dashboard role to adopt. */
    server?: Server;
}): {
    service: ReturnType<typeof createInterviewService>;
    registerCommand: (config: Record<string, unknown>) => void;
    handleCommandExecuteBefore: (input: {
        command: string;
        sessionID: string;
        arguments: string;
    }, output: {
        parts: Array<{
            type: string;
            text?: string;
        }>;
    }) => Promise<void>;
    handleEvent: (input: {
        event: {
            type: string;
            properties?: Record<string, unknown>;
        };
    }) => Promise<void>;
    dispose: () => Promise<void>;
};
