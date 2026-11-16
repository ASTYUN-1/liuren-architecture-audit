import { type Server } from 'node:http';
import type { PluginInput } from '@opencode-ai/plugin';
import type { InterviewStateEntry } from './types';
export declare function readDashboardAuthFile(port: number): Promise<{
    token: string;
    pid: number;
    startedAt: number;
} | null>;
interface RegisteredSession {
    sessionID: string;
    directory: string;
    pid: number;
    registeredAt: number;
}
type PendingKind = 'answers' | 'nudge' | 'block-comment' | 'chat';
export declare const DEFAULT_DASHBOARD_PORT = 43211;
export interface DashboardConfig {
    port: number;
    outputFolder: string;
    sessionClient?: Pick<PluginInput['client']['session'], 'list'>;
    /** Already-listening server to adopt instead of binding `port`. */
    server?: Server;
}
export declare function createDashboardServer(config: DashboardConfig): {
    start: () => Promise<string>;
    close: () => void;
    registerSession: (info: RegisteredSession) => void;
    removeSession: (sessionID: string) => void;
    pushState: (entry: InterviewStateEntry) => void;
    getState: (interviewId: string) => InterviewStateEntry | undefined;
    storeAnswers: (interviewId: string, answers: Array<{
        questionId: string;
        answer: string;
    }>) => void;
    getPendingAnswers: (interviewId: string) => Array<{
        questionId: string;
        answer: string;
    }> | null;
    claimPendingAnswers: (interviewId: string) => {
        claimId: string;
        answers: Array<{
            questionId: string;
            answer: string;
        }>;
    } | null;
    claimNudgeAction: (interviewId: string) => {
        claimId: string;
        action: 'more-questions' | 'confirm-complete';
    } | null;
    claimBlockComment: (interviewId: string) => {
        claimId: string;
        comment: {
            section: string;
            comment: string;
        };
    } | null;
    claimChatMessage: (interviewId: string) => {
        claimId: string;
        message: string;
    } | null;
    acknowledgePending: (interviewId: string, kind: PendingKind, claimId: string) => boolean;
    rollbackPending: (interviewId: string, kind: PendingKind, claimId: string) => boolean;
    consumePendingAnswers: (interviewId: string) => Array<{
        questionId: string;
        answer: string;
    }> | null;
    consumeNudgeAction: (interviewId: string) => 'more-questions' | 'confirm-complete' | null;
    consumeBlockComment: (interviewId: string) => {
        section: string;
        comment: string;
    } | null;
    consumeChatMessage: (interviewId: string) => string | null;
    authToken: string;
    discoverSessionDirectories: () => Promise<void>;
    addManualFolder: (dir: string) => void;
    removeManualFolder: (dir: string) => void;
    getManualFolders: () => string[];
    setScanDays: (days: number) => void;
    getScanDays: () => number;
    refreshFiles: () => Promise<void>;
};
export declare function probeDashboard(port: number): Promise<{
    alive: boolean;
    timestamp: number;
}>;
export declare function tryBecomeDashboard(config: DashboardConfig, maxAttempts?: number): Promise<ReturnType<typeof createDashboardServer> | null>;
export {};
