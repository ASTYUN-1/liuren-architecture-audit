import { z } from 'zod';
export interface InterviewQuestion {
    id: string;
    question: string;
    options: string[];
    suggested?: string;
}
export interface InterviewAnswer {
    questionId: string;
    answer: string;
}
export interface InterviewAssistantState {
    summary: string;
    title?: string;
    questions: InterviewQuestion[];
}
/** Raw question object from LLM output - loose, everything optional. */
export declare const RawQuestionSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    question: z.ZodOptional<z.ZodString>;
    options: z.ZodOptional<z.ZodArray<z.ZodUnknown>>;
    suggested: z.ZodOptional<z.ZodUnknown>;
}, z.core.$strip>;
/** Raw interview_state block from LLM output. */
export declare const RawInterviewStateSchema: z.ZodObject<{
    summary: z.ZodOptional<z.ZodUnknown>;
    title: z.ZodOptional<z.ZodUnknown>;
    questions: z.ZodOptional<z.ZodArray<z.ZodUnknown>>;
}, z.core.$strip>;
export interface InterviewRecord {
    id: string;
    sessionID: string;
    idea: string;
    markdownPath: string;
    createdAt: string;
    abandonedAt?: string;
    abandonedOrder?: number;
    status: 'active' | 'abandoned';
    baseMessageCount: number;
}
export interface InterviewMessagePart {
    type?: string;
    text?: string;
}
export interface InterviewMessage {
    info?: {
        role?: string;
        [key: string]: unknown;
    };
    parts?: InterviewMessagePart[];
}
export interface InterviewListItem {
    id: string;
    idea: string;
    status: InterviewRecord['status'];
    createdAt: string;
}
export interface InterviewFileItem {
    fileName: string;
    resumeCommand: string;
    title: string;
    summary: string;
    sessionID?: string;
    directory?: string;
}
export interface SpecBlock {
    id: string;
    title: string;
    content: string;
}
export interface InterviewState {
    interview: InterviewRecord;
    url: string;
    markdownPath: string;
    mode: 'awaiting-agent' | 'awaiting-user' | 'abandoned' | 'completed' | 'error' | 'session-disconnected';
    lastParseError?: string;
    isBusy: boolean;
    summary: string;
    questions: InterviewQuestion[];
    document: string;
    blocks: SpecBlock[];
}
/** Wire format for dashboard state cache entries. */
export interface InterviewStateEntry {
    interviewId: string;
    sessionID: string;
    idea: string;
    mode: 'awaiting-agent' | 'awaiting-user' | 'abandoned' | 'completed' | 'error' | 'session-disconnected';
    summary: string;
    title: string;
    questions: Array<{
        id: string;
        question: string;
        options?: string[];
        suggested?: string;
    }>;
    pendingAnswers: Array<{
        questionId: string;
        answer: string;
    }> | null;
    lastUpdatedAt: number;
    filePath: string;
    nudgeAction: 'more-questions' | 'confirm-complete' | null;
    pendingBlockComment?: {
        section: string;
        comment: string;
    } | null;
    pendingChatMessage?: string | null;
    document?: string;
    blocks?: SpecBlock[];
}
