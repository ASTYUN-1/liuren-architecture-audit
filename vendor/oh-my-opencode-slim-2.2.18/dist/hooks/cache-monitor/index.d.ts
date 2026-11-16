/**
 * Cache monitor — runtime watchdog for provider prompt-cache busts.
 *
 * Offline tests prove the plugin projects a byte-stable payload, but only
 * the provider knows whether a cache prefix was actually reused. OpenCode
 * surfaces per-request cache telemetry on assistant messages
 * (`tokens.cache.read` / `tokens.cache.write`); this hook watches those
 * numbers and logs a loud warning when a session that previously enjoyed
 * cache hits suddenly reports zero cached tokens on a sizeable request —
 * the field signature of a mid-session prompt-prefix change.
 *
 * Observation only: it never mutates messages or state, and it fails open
 * on any unexpected event shape.
 */
export interface CacheMonitorOptions {
    logger?: (message: string, data?: unknown) => void;
}
export declare function createCacheMonitorHook(options?: CacheMonitorOptions): {
    event: (input: {
        event: unknown;
    }) => Promise<void>;
};
