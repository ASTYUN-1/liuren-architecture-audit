import type { InterviewQuestion } from './types';
export declare function buildKickoffPrompt(idea: string, maxQuestions: number): string;
export declare function buildResumePrompt(document: string, maxQuestions: number): string;
export declare function buildAnswerPrompt(answers: Array<{
    questionId: string;
    answer: string;
}>, questions: InterviewQuestion[], maxQuestions: number): string;
