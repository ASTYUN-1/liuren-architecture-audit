/**
 * Shared session utilities for council and background managers.
 */
import type { OpencodeClient } from '@opencode-ai/sdk';
export declare const SESSION_ABORT_TIMEOUT_MS = 1000;
export declare const SESSION_ID_PATTERN: RegExp;
export declare class OperationTimeoutError extends Error {
    constructor(message: string);
}
export declare function withTimeout<T>(operation: Promise<T>, timeoutMs: number, message: string): Promise<T>;
export declare function abortSessionWithTimeout(client: OpencodeClient, sessionId: string, timeoutMs?: number): Promise<void>;
/**
 * Parse a model reference string into provider and model IDs.
 * @param model - Model string in format "provider/model"
 * @returns Object with providerID and modelID, or null if invalid
 */
export declare function parseModelReference(model: string): {
    providerID: string;
    modelID: string;
} | null;
/**
 * Send a prompt to a session with optional timeout.
 * If timeout is exceeded, the session is aborted and an error is thrown.
 * @param client - OpenCode client instance
 * @param args - Arguments for session.prompt()
 * @param timeoutMs - Timeout in milliseconds (0 = no timeout)
 * @throws Error if timeout is exceeded
 */
export declare function promptWithTimeout(client: OpencodeClient, args: Parameters<OpencodeClient['session']['prompt']>[0], timeoutMs: number, signal?: AbortSignal): Promise<void>;
/**
 * Result of extracting session content.
 * `empty` is true when the assistant produced zero text content -
 * the provider returned an empty response (e.g. rate-limited silently).
 */
export interface SessionExtractionResult {
    text: string;
    empty: boolean;
    /** True only when the last message is a completed assistant turn with no
     *  message-level error. This is terminal evidence that the session is not
     *  idle mid-work; callers must not present partial output as a final result
     *  without it. */
    terminal?: boolean;
}
/** Extract only the final assistant response to keep task retrieval bounded. */
export declare function extractFinalSessionResult(client: OpencodeClient, sessionId: string, options?: {
    directory?: string;
    includeReasoning?: boolean;
}): Promise<SessionExtractionResult>;
/**
 * Extract the result text from a session.
 * Collects all assistant messages and concatenates their text parts.
 * @param client - OpenCode client instance
 * @param sessionId - Session ID to extract from
 * @param options - Optional: `includeReasoning` (default true) controls whether
 *                  reasoning/chain-of-thought parts are included.
 * @returns Object with extracted text and an `empty` flag for zero-content detection
 */
export declare function extractSessionResult(client: OpencodeClient, sessionId: string, options?: {
    directory?: string;
    includeReasoning?: boolean;
}): Promise<SessionExtractionResult>;
