import { type PluginConfig } from './schema';
/**
 * Warning kinds produced during config loading.
 */
export type ConfigLoadWarningKind = 'invalid-json' | 'invalid-schema' | 'read-error' | 'missing-preset' | 'deprecated-key' | 'normalized';
/**
 * A warning emitted while loading plugin configuration.
 */
export interface ConfigLoadWarning {
    path: string;
    kind: ConfigLoadWarningKind;
    message: string;
    formatted?: unknown;
}
/**
 * Options for loadPluginConfig.
 */
export interface LoadPluginConfigOptions {
    /**
     * Called with a warning whenever config loading produces a non-fatal issue.
     * The loader still falls back to defaults and continues normally.
     */
    onWarning?: (warning: ConfigLoadWarning) => void;
    /**
     * Suppress console warnings while still invoking onWarning.
     */
    silent?: boolean;
}
/**
 * Normalize disabled_* config keys in place so a non-array value does not
 * reject the whole config object during schema validation. A string value
 * (e.g. "explorer") becomes a single-element array so the user's disable
 * intent survives; any other non-array value (number, boolean, object, ...)
 * is dropped. Array and undefined values are left untouched. Each
 * normalization is reported through `warn` (if provided) with a plain
 * message; callers wrap it in their own warning channel (loader uses
 * onWarning + console.warn, doctor just reports the message).
 *
 * @param rawConfig - Parsed config to normalize (mutated in place)
 * @param warn - Optional callback invoked with each warning message
 */
export declare function normalizeDisabledArrayKeys(rawConfig: unknown, warn?: (message: string) => void): void;
/**
 * Find plugin config paths (user and project) for a given directory.
 * User config uses getConfigSearchDirs() for lookup.
 * Project config uses <directory>/.opencode/oh-my-opencode-slim.
 *
 * @param directory - Project directory to search for .opencode config
 * @returns Object with userConfigPath and projectConfigPath (null if not found)
 */
export declare function findPluginConfigPaths(directory: string): {
    userConfigPath: string | null;
    projectConfigPath: string | null;
};
/**
 * Merge two plugin configs using the loader's merge rules.
 * Project/override takes precedence over base.
 */
export declare function mergePluginConfigs(base: PluginConfig, override: PluginConfig): PluginConfig;
/**
 * Recursively merge two objects, with override values taking precedence.
 * For nested objects, merges recursively. For arrays and primitives, override replaces base.
 *
 * @param base - Base object to merge into
 * @param override - Override object whose values take precedence
 * @returns Merged object, or undefined if both inputs are undefined
 */
export declare function deepMerge<T extends Record<string, unknown>>(base?: T, override?: T): T | undefined;
/**
 * Load plugin configuration from user and project config files, merging them appropriately.
 *
 * Configuration is loaded from two locations:
 * 1. User config: $OPENCODE_CONFIG_DIR/oh-my-opencode-slim.jsonc or .json,
 *    or ~/.config/opencode/oh-my-opencode-slim.jsonc or .json (or $XDG_CONFIG_HOME)
 * 2. Project config: <directory>/.opencode/oh-my-opencode-slim.jsonc or .json
 *
 * JSONC format is preferred over JSON (allows comments and trailing commas).
 * Project config takes precedence over user config. Nested objects (agents, multiplexer) are
 * deep-merged, while top-level arrays are replaced entirely by project config.
 *
 * @param directory - Project directory to search for .opencode config
 * @param options - Optional load options including onWarning callback
 * @returns Merged plugin configuration (empty object if no configs found)
 */
export declare function loadPluginConfig(directory: string, options?: LoadPluginConfigOptions): PluginConfig;
/**
 * Load custom prompt for an agent from the prompts directory.
 * Checks for {agent}.md (replaces default) and {agent}_append.md (appends to default).
 * If preset is provided and safe for paths, it first checks {preset}/ subdirectory,
 * then falls back to the root prompts directory.
 *
 * @param agentName - Name of the agent (e.g., "orchestrator", "explorer")
 * @param optionsOrPreset - Optional preset name or options configuration
 * @returns Object with prompt and/or appendPrompt if files exist
 */
export declare function loadAgentPrompt(agentName: string, optionsOrPreset?: string | {
    preset?: string;
    projectDirectory?: string;
}): {
    prompt?: string;
    appendPrompt?: string;
};
