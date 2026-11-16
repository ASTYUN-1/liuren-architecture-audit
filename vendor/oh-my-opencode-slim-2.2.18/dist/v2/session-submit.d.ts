/**
 * Shared v2 session submit + text helpers.
 *
 * One implementation of "submit text as a user prompt on a v2 session" so the
 * generic command bridge (setup.ts) and the interview bridge stay identical;
 * avoids a setup↔interview-bridge import cycle.
 */
import type { V2Context } from './types';
/** Function that submits `text` as a user prompt on a v2 session. */
export type V2CommandSubmit = (sessionID: string, text: string) => Promise<void>;
/** Submit marker text as a user prompt via `ctx.session.prompt`. Never
 * throws — the session methods reject on transport errors and command
 * `execute` must not leak that out to the host. */
export declare function createSessionSubmit(ctx: V2Context): V2CommandSubmit;
/** Join the text parts of a v2 message content array. */
export declare function textFromContent(content: Array<Record<string, unknown>>): string;
