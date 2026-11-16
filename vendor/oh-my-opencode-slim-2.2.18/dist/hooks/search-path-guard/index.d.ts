import path from 'node:path';
import type { PluginInput } from '@opencode-ai/plugin';
interface ToolExecuteBeforeInput {
    tool: string;
}
interface ToolExecuteBeforeOutput {
    args?: {
        path?: unknown;
        [key: string]: unknown;
    };
}
type PathOperations = Pick<typeof path, 'isAbsolute' | 'join' | 'resolve'>;
/**
 * Resolve a search path the same way as the corresponding host tool.
 *
 * v1's grep uses path.join while v1's glob uses path.resolve. The v2 tool
 * adapter uses path.resolve for both tools. `pathOperations` is injectable so
 * path flavor behavior can be tested deterministically without a Windows CI
 * runner; production uses Node's native path flavor, as does the host.
 */
export declare function resolveSearchPath(tool: string, hostFlavor: string | undefined, directory: string | undefined, raw: string, pathOperations?: PathOperations): string | null;
export declare function createSearchPathGuardHook(ctx: PluginInput): {
    'tool.execute.before': (input: ToolExecuteBeforeInput, output: ToolExecuteBeforeOutput) => Promise<void>;
};
export {};
