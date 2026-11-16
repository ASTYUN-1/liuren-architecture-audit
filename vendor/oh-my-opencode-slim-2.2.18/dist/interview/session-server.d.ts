import type { PluginInput } from '@opencode-ai/plugin';
import type { InterviewConfig } from '../config';
export declare function createPerSessionInterviewServer(ctx: PluginInput, interviewConfig: InterviewConfig | undefined, outputFolder: string): {
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
    dispose: () => void;
};
