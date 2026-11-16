import type { Server } from 'node:http';
import type { PluginInput } from '@opencode-ai/plugin';
import type { PluginConfig } from '../config';
export declare function createInterviewManager(ctx: PluginInput, config: PluginConfig, options?: {
    /** Already-listening server for the dashboard role to adopt. */
    server?: Server;
}): {
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
    dispose: () => Promise<void> | void;
};
