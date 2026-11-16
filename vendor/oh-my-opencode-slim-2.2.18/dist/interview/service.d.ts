import type { PluginInput } from '@opencode-ai/plugin';
import type { InterviewConfig } from '../config';
import { type InterviewSessionRuntime } from './runtime';
import type { InterviewAnswer, InterviewFileItem, InterviewListItem, InterviewRecord, InterviewState } from './types';
/**
 * Cap on retained abandoned interview records. Abandoned interviews are kept
 * briefly so a still-open browser tab can render their final state, but
 * without a bound the `interviewsById` and `browserOpened` collections grow
 * for the life of a long-running session/dashboard process.
 */
export declare const MAX_RETAINED_ABANDONED = 50;
export declare function createInterviewService(ctx: PluginInput, config?: InterviewConfig, deps?: {
    openBrowser?: (url: string) => void;
    env?: NodeJS.ProcessEnv;
    runtime?: InterviewSessionRuntime;
}): {
    setBaseUrlResolver: (resolver: () => Promise<string>) => void;
    setStatePushCallback: (callback: (interviewId: string, state: InterviewState) => void) => void;
    setOnInterviewCreated: (callback: (interview: InterviewRecord) => void) => void;
    getActiveInterviewId: (sessionID: string) => string | null;
    registerCommand: (config: Record<string, unknown>) => void;
    handleCommandExecuteBefore: (input: {
        command: string;
        sessionID: string;
        arguments: string;
    }, output: {
        parts: Array<{
            type: string;
            text?: string;
            synthetic?: boolean;
            metadata?: Record<string, unknown>;
        }>;
    }) => Promise<void>;
    handleEvent: (input: {
        event: {
            type: string;
            properties?: Record<string, unknown>;
        };
    }) => Promise<void>;
    getInterviewState: (interviewId: string) => Promise<InterviewState>;
    listInterviewFiles: () => Promise<InterviewFileItem[]>;
    listInterviews: () => InterviewListItem[];
    submitAnswers: (interviewId: string, answers: InterviewAnswer[]) => Promise<void>;
    submitBlockComment: (interviewId: string, section: string, comment: string) => Promise<void>;
    submitChat: (interviewId: string, message: string) => Promise<void>;
    handleNudgeAction: (interviewId: string, action: 'more-questions' | 'confirm-complete') => Promise<void>;
};
