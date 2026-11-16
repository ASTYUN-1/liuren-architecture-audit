export declare const LOOP_GUARD_WARNING = "\n[REPEATED TOOL CALLS - STOP]\n\nYou have issued the exact same tool call with identical arguments 3 times in a row and received identical results. This is an infinite loop and you are making no progress.\n\nSTOP repeating this call. Instead:\n1. Reconsider what you are looking for; the result above already contains what this call can tell you.\n2. If you need different information, make a DIFFERENT call (different path, pattern, or tool).\n3. If the task is actually done, produce your final answer now instead of calling more tools.\n";
export interface ToolLoopGuardHook {
    'tool.execute.before': (input: {
        tool: string;
        sessionID?: string;
        callID?: string;
    }, output: {
        args?: unknown;
    }) => Promise<void>;
    'tool.execute.after': (input: {
        tool: string;
        sessionID?: string;
        callID?: string;
    }, output: {
        output: unknown;
        metadata?: unknown;
    }) => Promise<void>;
    observeNewUserMessage(sessionID: string, messageID: string): void;
    resetTurn(sessionID: string): void;
    resetSession(sessionID: string): void;
    resetForTests(): void;
}
export declare function createToolLoopGuardHook(): ToolLoopGuardHook;
