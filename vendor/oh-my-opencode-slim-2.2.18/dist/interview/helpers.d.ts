import type { IncomingMessage, ServerResponse } from 'node:http';
export declare function sendJson(response: ServerResponse, status: number, value: unknown): void;
export declare function sendHtml(response: ServerResponse, html: string): void;
export declare function isValidId(id: string): boolean;
export declare function extractResumeSlug(interviewId: string): string;
/**
 * Read and parse JSON body from an HTTP request with size limit.
 * Destroys the request if the body exceeds MAX_BODY_SIZE.
 */
export declare function readJsonBody(request: IncomingMessage): Promise<unknown>;
