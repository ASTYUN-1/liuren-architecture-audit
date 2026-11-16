/**
 * Runtime configuration interface for oh-my-opencode-slim.
 *
 * Single typed access point for everything the plugin reads from config at
 * runtime: the plugin file layer (loadPluginConfig result), the host config
 * layer (opencode.json snapshot captured by the config hook BEFORE it mutates
 * the host config), and runtime overrides (preset switching and model-switch
 * tracking).
 *
 * One instance per directory, created once per process. Seeded by
 * RuntimeConfig.init() at plugin factory start (plugin layer) and by
 * captureHostConfig() at the top of the config hook (host layer).
 *
 * Cache-safety contract: getters feed construction and hooks, never prompt
 * assembly. This module must never expose volatile text for prompts; any
 * prompt-injecting consumer must go through src/hooks/cache-safe-injection.ts.
 */
import { type ImageRouting } from './constants';
import type { CouncilConfig } from './council-schema';
import type { AcpAgentsConfig, AgentOverrideConfig, BackgroundJobsConfig, CompanionConfig, FailoverConfig, MultiplexerConfig, PluginConfig, WebfetchConfig } from './schema';
/** A single agent entry from the host opencode.json config. */
export interface HostAgentConfig {
    model?: unknown;
    variant?: unknown;
    temperature?: unknown;
    options?: Record<string, unknown>;
    [key: string]: unknown;
}
/** Snapshot of the host opencode config captured before mutation. */
export interface HostConfigSnapshot {
    default_agent?: string;
    agent?: Record<string, HostAgentConfig>;
    mcp?: Record<string, unknown>;
    small_model?: unknown;
    provider?: Record<string, unknown>;
    [key: string]: unknown;
}
/**
 * Runtime configuration interface: one typed instance per directory.
 *
 * Seed precedence for merged surfaces (host override > runtime override >
 * plugin file) mirrors the config hook's final application order.
 */
export declare class RuntimeConfig {
    /** Cache-safety marker: never expose volatile text for prompt assembly. */
    readonly isCacheSafe: true;
    private constructor();
    /**
     * Seed (or re-seed) the plugin file layer for a directory. Re-seeding
     * preserves runtime state (preset switch, model switches) so plugin reloads
     * keep behavior stable, matching the previous module-level singleton.
     */
    static init(directory: string, pluginConfig: PluginConfig): RuntimeConfig;
    /** Lazy per-directory accessor; creates an empty instance if unseeded. */
    static get(directory: string): RuntimeConfig;
    /** Remove a directory from the registry (plugin re-init / dispose). */
    static reset(directory: string): void;
    private pluginConfig;
    private hostSnapshot;
    private runtimePresetName;
    private switchedModels;
    private seedPlugin;
    /**
     * Capture the host opencode config snapshot. MUST be called at the top of
     * the config hook, BEFORE any mutation of opencodeConfig, or consumers see
     * post-merge state (double-application risk).
     */
    captureHostConfig(opencodeConfig: Record<string, unknown>): void;
    /** Frozen snapshot of the plugin config as loaded at factory start. */
    get plugin(): PluginConfig | undefined;
    /** Active preset name: runtime override wins over the config-file preset. */
    get preset(): string | undefined;
    /**
     * Merged agent overrides with seed precedence: runtime preset override >
     * plugin file (root agents override the config-file preset). Mirrors the
     * loader's preset merge so this is correct even when seeded with a raw
     * (not yet loader-merged) plugin config.
     */
    agents(): Record<string, AgentOverrideConfig>;
    /**
     * Effective override for one agent, alias-aware, with seed precedence
     * host override > runtime override > plugin file.
     */
    agent(name: string): AgentOverrideConfig | undefined;
    /** Disabled agent names, minus protected agents. */
    get disabledAgents(): ReadonlySet<string>;
    get disabledTools(): readonly string[];
    get disabledSkills(): readonly string[];
    /** Custom agent names declared in config.agents (was getCustomAgentNames). */
    get customAgentNames(): string[];
    get disabledMcps(): readonly string[];
    /** Final resolved image routing (explicit value or legacy conditional). */
    get imageRouting(): ImageRouting;
    get multiplexer(): MultiplexerConfig;
    get backgroundJobs(): BackgroundJobsConfig;
    get fallback(): FailoverConfig;
    get webfetch(): WebfetchConfig;
    get acpAgents(): AcpAgentsConfig;
    get companion(): CompanionConfig | undefined;
    get council(): CouncilConfig | undefined;
    get autoUpdate(): boolean;
    get stripOrchestratorModel(): boolean;
    get setDefaultAgent(): boolean;
    get compactSidebar(): boolean;
    /**
     * Agent name → model array (id + optional variant), derived once from
     * array-configured models. Was modelArrayMap in src/index.ts (built from
     * created agentDefs: disabled agents excluded, alias-aware, variants
     * preserved, plus multi-model councillor chains from council config).
     */
    get modelArrays(): Record<string, Array<{
        id: string;
        variant?: string;
    }>>;
    /**
     * Agent name → model chain (ids only), derived from modelArrays.
     * Was runtimeChains in src/index.ts (alias-aware, disabled excluded,
     * councillor chains included).
     */
    get runtimeChains(): Record<string, string[]>;
    /**
     * Primary model from the active preset (orchestrator model, else first
     * subagent model). Was getConfigPrimaryModel in src/agents/index.ts.
     */
    get primaryModel(): string | undefined;
    /** The captured host opencode config snapshot (pre-mutation). */
    host(): HostConfigSnapshot | undefined;
    /** The host's opencode.json agent entry for one agent. */
    hostAgent(name: string): HostAgentConfig | undefined;
    /** The host's top-level small_model, when configured. */
    smallModel(): string | undefined;
    /** The host's top-level mcp record, when configured. */
    hostMcp(): Record<string, unknown> | undefined;
    /**
     * Activate a runtime preset (replaces setActiveRuntimePreset). A name that
     * does not exist in plugin.presets clears the selection (stale-state
     * guard, mirrors the previous config-hook reset branch).
     */
    setRuntimePreset(name: string | null): void;
    getRuntimePreset(): string | null;
    /** Record that an agent's model was switched at runtime. */
    everModelSwitched(name: string): void;
    hasModelSwitched(name: string): boolean;
    private runtimePresetAgents;
    /** Alias-aware override lookup inside a merged agents record. */
    private aliasAwareOverride;
}
