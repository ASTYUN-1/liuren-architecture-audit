import type { AgentOverrideConfig, PluginConfig, Preset } from '../config';
/**
 * Result of a preset switch attempt. `message` is user-facing and intended for
 * a TUI toast/dialog (it is never injected into the LLM context).
 */
export interface PresetSwitchResult {
    ok: boolean;
    presetName: string;
    message: string;
    /** Per-agent summary lines, e.g. "orchestrator → model: x, variant: y". */
    summary: string[];
}
/** A flattened, SDK-shaped agent override derived from a preset entry. */
export interface AgentUpdate {
    model?: string;
    temperature?: number;
    variant?: string;
    options?: Record<string, unknown>;
}
/**
 * Switch the active preset purely through on-disk state: persist the preset
 * name to the user config file. The sidebar snapshot is deliberately NOT
 * touched — the new preset applies on the next reload/restart, when
 * `loadPluginConfig` re-reads the config file and merges the preset into
 * `config.agents`. Refreshing the sidebar mid-session while the agent
 * registry is unchanged would show models that don't match the running
 * agents, which is confusing.
 *
 * This is the shared core used by the TUI `/preset` slash command. It
 * deliberately does NOT touch OpenCode's in-memory agent registry. It also
 * does not set the server-side runtime-preset singleton, because the TUI
 * runs in a separate process from the server and cannot reach that state.
 */
export declare function switchPresetOnDisk(directory: string, presetName: string, config: PluginConfig): PresetSwitchResult;
/**
 * Build the SDK-shaped agent overrides from a preset, resolving legacy alias
 * keys (e.g. "explore" → "explorer").
 */
export declare function buildAgentUpdates(preset: Preset): Record<string, AgentUpdate>;
/**
 * Map an AgentOverrideConfig (from plugin config) to the subset of agent
 * config fields shown in the saved preset summary.
 */
export declare function mapOverrideToAgentConfig(override: AgentOverrideConfig): AgentUpdate;
/** Build the per-agent summary lines for a switch result / picker tooltip. */
export declare function buildPresetSummary(agentUpdates: Record<string, AgentUpdate>): string[];
/**
 * Persist a preset (create or overwrite) into the user config's `presets`
 * object. Returns true on success.
 */
export declare function writePreset(directory: string, name: string, preset: Preset): boolean;
/**
 * Delete a preset from the user config. Returns true if removed, false if the
 * preset did not exist or the write failed.
 */
export declare function deletePreset(directory: string, name: string): boolean;
/**
 * Set (or replace) an agent override within an in-memory preset. Returns a
 * new preset object; does not mutate the input.
 */
export declare function setAgentOverride(preset: Preset, agentName: string, override: AgentOverrideConfig): Preset;
/**
 * Remove an agent from an in-memory preset. Returns a new preset object; does
 * not mutate the input. If the agent was not present, the preset is unchanged.
 */
export declare function removeAgentFromPreset(preset: Preset, agentName: string): Preset;
