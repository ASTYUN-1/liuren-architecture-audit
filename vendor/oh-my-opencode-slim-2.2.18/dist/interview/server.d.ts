import { type Server } from 'node:http';
import type { InterviewAnswer, InterviewFileItem, InterviewListItem, InterviewState } from './types';
export declare function createInterviewServer(deps: {
    getState: (interviewId: string) => Promise<InterviewState>;
    listInterviewFiles: () => Promise<InterviewFileItem[]>;
    listInterviews: () => InterviewListItem[];
    submitAnswers: (interviewId: string, answers: InterviewAnswer[]) => Promise<void>;
    submitBlockComment: (interviewId: string, section: string, comment: string) => Promise<void>;
    submitChat: (interviewId: string, message: string) => Promise<void>;
    handleNudgeAction: (interviewId: string, action: 'more-questions' | 'confirm-complete') => Promise<void>;
    outputFolder: string;
    port: number;
    /** Already-listening server to adopt instead of binding `port`. */
    server?: Server;
}): {
    ensureStarted: () => Promise<string>;
    close: () => void;
};
