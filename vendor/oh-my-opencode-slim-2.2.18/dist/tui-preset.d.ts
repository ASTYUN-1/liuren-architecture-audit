/**
 * Three-level `/preset` manager for the TUI.
 *
 * Level 1 — preset list (Apply / Edit / Create / Delete)
 * Level 2 — agents in a preset (Add / Edit / Remove / Save)
 * Level 3 — edit one agent's model, variant, temperature, options
 *
 * Pure TUI: uses `api.ui.*` dialog primitives and `api.client.providers()`
 * for the model list. Never sends a message to the server's `command()` flow,
 * so it triggers no LLM turn — same channel as the built-in `/models`.
 *
 * All preset mutations are written to the user-level config file
 * (`oh-my-opencode-slim.json[c]`). Applying a preset persists the preset
 * name only — the sidebar is NOT refreshed mid-session, because the agent
 * registry is unchanged and showing new models against running agents
 * would be misleading. The new preset takes effect on the next
 * conversation/reload, when `loadPluginConfig` re-reads the config and
 * merges the preset into `config.agents`. This is deliberate: hot-swapping
 * the agent tree during an active conversation could truncate context (a
 * new model may have a smaller window), drift prior assistant turns under a
 * changed system prompt, leave running subagents referencing stale agent
 * definitions, or shift tool/skill availability underfoot. A future path
 * to true in-session switching without reset requires a host API for atomic
 * agent-registry refresh with session compatibility checks.
 */
import type { TuiPluginApi } from '@opencode-ai/plugin/tui';
import type { TuiSnapshot } from './tui-state';
/**
 * Entry point: open the preset manager at Level 1. Re-reads the config each
 * time it is opened so newly-edited files are reflected.
 */
export declare function openPresetManager(api: TuiPluginApi, directory: string, snapshotRef: {
    snapshot: TuiSnapshot;
}): void;
