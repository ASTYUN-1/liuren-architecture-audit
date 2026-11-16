/**
 * v2 TUI plugin entry (`./tui` subpath → `dist/tui2.js`).
 *
 * Composes the existing dual-contract TUI plugin (`../tui`): the v1 `tui`
 * field is re-exported unchanged so v1 hosts keep the exact sidebar
 * registration, while the v2 `setup` is extended with the `/preset` keymap
 * flow — v2 hosts get the sidebar plus an interactive preset switcher
 * (dialog select → on-disk persist → toast feedback).
 *
 * Hosts discover this entry through the package.json `./tui` export
 * (exports-map probe in the host's `kind: "tui"` loader pass); the
 * server-side default export (src/index.ts) plays no role in that — in
 * fact it must stay free of any `tui` key (see the note there).
 */
import type { PluginConfig } from '../config';
import { type PresetSwitchResult } from '../tools/preset-switch';
import omoTui from '../tui';
/** A single `ui.dialog.select` option for the preset picker. */
export interface PresetOption {
    title: string;
    value: string;
    description?: string;
}
/**
 * v2 TUI preset-switcher surface. Complements the sidebar context that
 * `../tui` mirrors (location/renderer/theme/ui.slot/ui.router); hosts may
 * provide either or both, so every field is optional and capability-guarded.
 */
export interface V2PresetTuiContext {
    location?: {
        directory: string;
    };
    ui?: {
        dialog?: {
            select: <Value>(options: {
                title: string;
                options: Array<{
                    title: string;
                    value: Value;
                    description?: string;
                }>;
                current?: Value;
            }) => Promise<Value | undefined>;
        };
        toast?: (toast: {
            title?: string;
            message: string;
            variant?: string;
        }) => void;
    };
    keymap?: {
        layer: (layer: {
            commands: Array<{
                title?: string;
                slash?: {
                    name: string;
                    aliases?: string[];
                };
                run: (input?: string) => void | Promise<void>;
            }>;
        }) => {
            dispose(): void;
        };
    };
}
/** Combined v2 TUI context: sidebar surface from `../tui` + preset surface. */
export type V2TuiPluginContext = Parameters<(typeof omoTui)['setup']>[0] & V2PresetTuiContext;
/**
 * Map a plugin config's presets to `ui.dialog.select` options. Each option's
 * description is the per-agent summary (e.g. "orchestrator → model: x"),
 * matching the v1 picker's tooltip.
 */
export declare function buildPresetOptions(config: PluginConfig): PresetOption[];
/**
 * Apply a preset by name through the shared on-disk switcher
 * (`switchPresetOnDisk`): the preset name is persisted to the user config so
 * the next reload/restart picks it up; the running session is untouched.
 * Returns the switch result whose `message` is user-facing (toast-ready).
 */
export declare function applyPresetByName(directory: string, config: PluginConfig, presetName: string): PresetSwitchResult;
/**
 * Interactive `/preset` flow: open the preset picker (or apply `presetArg`
 * directly when the slash command carried a name, e.g. `/preset cheap`),
 * persist the selection, and toast the result. Never throws — failures are
 * surfaced as a toast and logged.
 */
export declare function runPresetFlow(ctx: V2PresetTuiContext, presetArg?: string): Promise<void>;
/**
 * Dual contract, same as `../tui`: v1 hosts validate `{ id, tui }`, v2 hosts
 * validate `{ id, setup }`; both ignore extra keys. The `tui` field is the
 * identical v1 factory reference; the `setup` wraps the base v2 setup
 * (sidebar) and adds the `/preset` keymap layer.
 */
declare const plugin: {
    id: string;
    tui: import("@opencode-ai/plugin/tui").TuiPlugin;
    setup(ctx: V2TuiPluginContext): Promise<undefined | (() => void)>;
};
export default plugin;
