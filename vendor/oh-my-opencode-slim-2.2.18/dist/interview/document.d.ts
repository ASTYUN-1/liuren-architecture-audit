import { parseFrontmatter as sharedParseFrontmatter } from '../utils/frontmatter';
import type { InterviewAnswer, InterviewQuestion, InterviewRecord, SpecBlock } from './types';
export declare const DEFAULT_OUTPUT_FOLDER = "interview";
export declare class InterviewDocumentOwnershipError extends Error {
    readonly markdownPath: string;
    readonly ownerSessionID: string;
    constructor(markdownPath: string, ownerSessionID: string);
}
export declare function withInterviewDocumentLock<T>(markdownPath: string, operation: () => Promise<T>): Promise<T>;
export declare function claimInterviewDocument(markdownPath: string, sessionID: string, baseMessageCount: number): Promise<string>;
export declare function normalizeOutputFolder(outputFolder: string): string;
export declare function createInterviewDirectoryPath(directory: string, outputFolder: string): string;
export declare function createInterviewFilePath(directory: string, outputFolder: string, idea: string, uniqueId?: string): string;
export declare function relativeInterviewPath(directory: string, filePath: string): string;
/**
 * Resolve a user-provided value to an existing .md file path.
 * Checks absolute paths, relative paths, and output-folder-relative paths.
 * Returns null if no matching file is found.
 */
export declare function resolveExistingInterviewPath(directory: string, outputFolder: string, value: string): string | null;
export declare function slugify(value: string): string;
export declare function extractSummarySection(document: string): string;
export declare function extractTitle(document: string): string;
export declare function buildInterviewDocument(idea: string, summary: string, history: string, meta?: {
    sessionID?: string;
    baseMessageCount?: number;
    owner?: string;
    tags?: string[];
}): string;
/** Parse frontmatter from a .md file. Returns null if no frontmatter. */
export declare const parseFrontmatter: typeof sharedParseFrontmatter;
export declare function ensureInterviewFile(record: InterviewRecord): Promise<void>;
export declare function readInterviewDocument(record: InterviewRecord): Promise<string>;
export declare function rewriteInterviewDocument(record: InterviewRecord, summary: string, title?: string): Promise<string>;
/**
 * Replace only the current specification with a clean completion response.
 * The response is deliberately not passed through the interview-state parser:
 * a previous structured response must never win over the final markdown.
 */
export declare function rewriteInterviewDocumentWithFinalSpec(record: InterviewRecord, finalMarkdown: string): Promise<string>;
export declare function appendInterviewAnswers(record: InterviewRecord, questions: InterviewQuestion[], answers: InterviewAnswer[]): Promise<void>;
export declare function parseSpecBlocks(markdown: string): SpecBlock[];
