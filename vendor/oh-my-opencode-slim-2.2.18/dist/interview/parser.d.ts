import type { InterviewAssistantState, InterviewMessage } from './types';
export declare function flattenMessage(message: InterviewMessage): string;
export declare function buildFallbackState(messages: InterviewMessage[]): InterviewAssistantState;
export declare function parseAssistantState(text: string, maxQuestions?: number): {
    state: InterviewAssistantState | null;
    error?: string;
};
export declare function findLatestAssistantState(messages: InterviewMessage[], maxQuestions?: number): {
    state: InterviewAssistantState | null;
    latestAssistantError?: string;
};
