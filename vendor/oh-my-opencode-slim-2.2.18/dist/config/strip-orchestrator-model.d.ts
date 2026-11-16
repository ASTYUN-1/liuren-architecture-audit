import type { PluginConfig, Preset } from './schema';
export declare function stripOrchestratorModel(agents: Record<string, unknown>, enabled: boolean | undefined, preset: Preset | undefined): void;
export declare function applyOrchestratorModelConfig(input: {
    agents: Record<string, unknown>;
    enabled: boolean | undefined;
    presets: PluginConfig['presets'];
    configPreset: string | undefined;
    runtimePreset: string | null;
}): void;
