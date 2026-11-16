import type { Server } from 'node:http';
import type { InterviewConfig } from '../config';
import type { InterviewSessionRuntime } from '../interview/runtime';
import { createInterviewService } from '../interview/service';
import type { InterviewMessage } from '../interview/types';
import type { V2CommandDraft, V2Context, V2SessionContextEvent } from './types';
export declare const INTERVIEW_COMMAND_MARKER = "<omos-interview-command>$ARGUMENTS</omos-interview-command>";
/** Render the `/interview` command marker with the given arguments. */
export declare function markerText(args: string): string;
export interface V2InterviewBridge {
    readonly service: ReturnType<typeof createInterviewService>;
    readonly runtime: InterviewSessionRuntime;
    registerCommand(draft: V2CommandDraft): void;
    handleContext(event: V2SessionContextEvent): Promise<void>;
    handleEvent(event: Record<string, unknown>): Promise<void>;
    getTranscript(sessionID: string): InterviewMessage[];
    dispose(): void;
}
/** Mutate the trailing command message from hook-produced parts. When the
 * hook produced nothing, strip the marker and leave the raw args text.
 * Only the trailing message is mutated; earlier messages are left
 * byte-for-byte untouched so provider prompt prefixes remain cacheable. */
export declare function applyInterviewCommandParts(trailing: {
    role: string;
    content: Array<Record<string, unknown>>;
}, text: string, parts: Array<Record<string, unknown>>): void;
export declare function createV2InterviewBridge(ctx: V2Context, config?: InterviewConfig, options?: {
    /** Already-listening server for the dashboard role to adopt. */
    server?: Server;
}): V2InterviewBridge;
