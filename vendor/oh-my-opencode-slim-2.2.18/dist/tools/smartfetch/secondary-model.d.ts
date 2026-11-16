import type { PluginInput } from '@opencode-ai/plugin';
import type { CachedFetch, SecondaryModel } from './types';
export interface SecondaryModelResolutionInput {
    /** Dedicated webfetch model(s) from the plugin config (highest priority). */
    webfetchModels?: Array<{
        id: string;
        variant?: string;
    }>;
    /** `small_model` from the host's already-loaded merged OpenCode config. */
    smallModel?: string;
    /** Explorer agent model id, resolved from in-memory config at construction. */
    explorerModel?: string;
    /** Librarian agent model id, resolved from in-memory config at construction. */
    librarianModel?: string;
}
export declare function pickAgentModelRef(value: unknown): string | undefined;
/**
 * Resolve the secondary-model chain purely from in-memory inputs.
 *
 * No filesystem or config-file access: every value is captured once at
 * plugin construction (`src/index.ts`) from the already-loaded plugin config
 * and the host's merged OpenCode config. Keeps the webfetch hot path free of
 * disk reads.
 */
export declare function resolveSecondaryModels(input?: SecondaryModelResolutionInput): SecondaryModel[];
export declare function decideSecondaryModelUse(fetchResult: CachedFetch, prompt: string | undefined, secondaryModels: SecondaryModel[]): {
    use: boolean;
    reason: 'no_prompt';
} | {
    use: boolean;
    reason: 'no_secondary_model_configured';
} | {
    use: boolean;
    reason: 'empty_content';
} | {
    use: boolean;
    reason: 'content_too_short';
} | {
    use: boolean;
    reason: 'prompt_present';
};
/**
 * Exposed for tests so they can avoid real wall-clock sleeps.
 * Not part of the public API.
 */
export declare const _testConfig: {
    deleteRetryDelayMs: number;
    secondaryModelTimeoutMs: number;
};
/** One-shot generation channel exposed by the v2 host
 * (`ctx.generate.text`), threaded through `PluginInput.experimental_v2`. */
export type V2GenerateText = (prompt: string, model?: {
    id: string;
    providerID: string;
    variant?: string;
}) => Promise<{
    text: string;
}>;
export declare function runSecondaryModelWithFallback(input: PluginInput, models: SecondaryModel[], prompt: string, content: string, parentSessionID?: string): Promise<{
    text: string;
    inputTruncated: boolean;
    inputChars: number;
    sourceChars: number;
    model: SecondaryModel;
}>;
