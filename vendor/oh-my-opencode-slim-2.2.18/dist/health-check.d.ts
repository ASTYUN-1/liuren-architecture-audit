/**
 * Plugin init health-check thresholds and helpers.
 *
 * Deliberately NOT re-exported from the package root (`src/index.ts`).
 * OpenCode's legacy plugin loader iterates every named export of the
 * root module and invokes each as a plugin factory with `PluginInput`.
 * A helper like `minimumExpectedToolCount` would then be called with a
 * `PluginInput` object instead of `string[]`, and its numeric return
 * value would be pushed into the hooks array as if it were a `Hooks`
 * object. Keeping this module internal (imported by, but not
 * re-exported from, `src/index.ts`) avoids that class of bug entirely;
 * see https://github.com/alvinunreal/oh-my-opencode-slim/issues/894.
 */
/** Minimum expected registrations for a healthy plugin load. */
export declare const HEALTH_CHECK: {
    readonly minAgents: 5;
    readonly minTools: 9;
    readonly minMcps: 1;
};
/**
 * Compute the minimum tool count the health check should expect, accounting
 * for baseline tools the user has intentionally disabled.
 *
 * @param disabledTools - Tool names disabled via config; non-array/malformed
 *   values (which should never occur post-validation, but are not trusted at
 *   runtime) are treated as "nothing disabled".
 * @param webfetchEnabled - Whether the enhanced webfetch tool is registered.
 * @returns The adjusted minimum expected tool count
 */
export declare function minimumExpectedToolCount(disabledTools?: readonly string[], webfetchEnabled?: boolean): number;
