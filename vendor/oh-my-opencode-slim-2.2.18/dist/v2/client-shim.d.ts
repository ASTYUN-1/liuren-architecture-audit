/**
 * v1 PluginInput shim (real delegation).
 *
 * The v1 plugin factory expects a `PluginInput` with an HTTP `client`,
 * project metadata, and a shell. v2's plugin context exposes none of these,
 * so this shim builds a v1-shaped input whose `client` translates the v1
 * SDK call shapes (Hono-style `{path, body}` or flat `{sessionID}`) into
 * v2 flat session calls (`get`/`interrupt`/`switchModel`/`prompt`/
 * `context`). Delegation is real where the v2 host provides the method and
 * explicitly fails or degrades with a log where it does not — the shim
 * never fakes success shapes.
 *
 * The v2 model-switch semantics (prompts carry no model; `switchModel`
 * must precede the prompt) are encapsulated in the `promptAsync`
 * translation, which is what lets the v1 foreground-fallback pipeline work
 * unmodified on v2.
 */
import type { V2Context } from './types';
/** v2 model reference accepted by `ctx.generate.text`. */
export interface V2GenerateModelRef {
    id: string;
    providerID: string;
    variant?: string;
}
/** Optional v2 capabilities threaded into the v1 PluginInput. Absent
 * capabilities must leave the input object unchanged (v1 parity). */
export interface ExperimentalV2 {
    /** One-shot generation (`ctx.generate.text`); no session involved. */
    generateText?: (prompt: string, model?: V2GenerateModelRef) => Promise<{
        text: string;
    }>;
}
/** Directory from the host-reported location; cwd on hosts without
 * `ctx.location` (or with an empty directory). */
export declare function resolveV2Directory(ctx: V2Context): string;
/** Build a v1-compatible PluginInput from the v2 context. The optional
 * `extras` threads probed v2 capabilities (e.g. one-shot generation)
 * through as `experimental_v2`; when absent no `experimental_v2` key is
 * added so the v1 pipeline stays byte-identical. */
export declare function buildPluginInput(ctx: V2Context, extras?: ExperimentalV2): Record<string, unknown>;
