import type { PluginInput } from '@opencode-ai/plugin';
import type { InterviewMessage } from './types';
export interface InterviewSessionRuntime {
    messages(sessionID: string): Promise<InterviewMessage[]>;
    notify(sessionID: string, text: string): Promise<void>;
    continue(sessionID: string, text: string, model?: {
        providerID: string;
        modelID: string;
    }): Promise<void>;
    rename(sessionID: string, title: string): Promise<void>;
}
/** The v1 implementation deliberately stays inside the interview boundary. */
export declare function createV1InterviewSessionRuntime(ctx: PluginInput): InterviewSessionRuntime;
export declare const createInterviewSessionRuntime: typeof createV1InterviewSessionRuntime;
