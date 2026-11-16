import type { InstallConfig } from './types';
export declare const GENERATED_PRESETS: readonly ['openai', 'opencode-go'];
export declare const MODEL_MAPPINGS: {
    readonly openai: {
        readonly orchestrator: {
            readonly model: 'openai/gpt-5.6-terra';
            readonly variant: 'high';
        };
        readonly oracle: {
            readonly model: 'openai/gpt-5.6-sol';
            readonly variant: 'high';
        };
        readonly librarian: {
            readonly model: 'openai/gpt-5.6-luna';
            readonly variant: 'low';
        };
        readonly explorer: {
            readonly model: 'openai/gpt-5.6-luna';
            readonly variant: 'low';
        };
        readonly designer: {
            readonly model: 'openai/gpt-5.6-luna';
            readonly variant: 'medium';
        };
        readonly fixer: {
            readonly model: 'openai/gpt-5.6-luna';
            readonly variant: 'high';
        };
    };
    readonly kimi: {
        readonly orchestrator: {
            readonly model: 'kimi-for-coding/k2p5';
            readonly variant: 'max';
        };
        readonly oracle: {
            readonly model: 'kimi-for-coding/k2p5';
            readonly variant: 'high';
        };
        readonly librarian: {
            readonly model: 'kimi-for-coding/k2p5';
            readonly variant: 'low';
        };
        readonly explorer: {
            readonly model: 'kimi-for-coding/k2p5';
            readonly variant: 'low';
        };
        readonly designer: {
            readonly model: 'kimi-for-coding/k2p5';
            readonly variant: 'medium';
        };
        readonly fixer: {
            readonly model: 'kimi-for-coding/k2p5';
            readonly variant: 'low';
        };
    };
    readonly copilot: {
        readonly orchestrator: {
            readonly model: 'github-copilot/claude-opus-4.6';
            readonly variant: 'max';
        };
        readonly oracle: {
            readonly model: 'github-copilot/claude-opus-4.6';
            readonly variant: 'high';
        };
        readonly librarian: {
            readonly model: 'github-copilot/grok-code-fast-1';
            readonly variant: 'low';
        };
        readonly explorer: {
            readonly model: 'github-copilot/grok-code-fast-1';
            readonly variant: 'low';
        };
        readonly designer: {
            readonly model: 'github-copilot/gemini-3.1-pro-preview';
            readonly variant: 'medium';
        };
        readonly fixer: {
            readonly model: 'github-copilot/claude-sonnet-4.6';
            readonly variant: 'low';
        };
    };
    readonly 'zai-plan': {
        readonly orchestrator: {
            readonly model: 'zai-coding-plan/glm-5';
            readonly variant: 'max';
        };
        readonly oracle: {
            readonly model: 'zai-coding-plan/glm-5';
            readonly variant: 'high';
        };
        readonly librarian: {
            readonly model: 'zai-coding-plan/glm-5';
            readonly variant: 'low';
        };
        readonly explorer: {
            readonly model: 'zai-coding-plan/glm-5';
            readonly variant: 'low';
        };
        readonly designer: {
            readonly model: 'zai-coding-plan/glm-5';
            readonly variant: 'medium';
        };
        readonly fixer: {
            readonly model: 'zai-coding-plan/glm-5';
            readonly variant: 'low';
        };
    };
    readonly 'opencode-go': {
        readonly orchestrator: {
            readonly model: 'opencode-go/minimax-m3';
            readonly variant: 'thinking';
        };
        readonly oracle: {
            readonly model: 'opencode-go/qwen3.7-max';
            readonly variant: 'max';
        };
        readonly explorer: {
            readonly model: 'opencode-go/deepseek-v4-flash';
            readonly variant: 'high';
        };
        readonly librarian: {
            readonly model: 'opencode-go/deepseek-v4-flash';
            readonly variant: 'high';
        };
        readonly designer: {
            readonly model: 'opencode-go/kimi-k2.7-code';
        };
        readonly fixer: {
            readonly model: 'opencode-go/deepseek-v4-flash';
            readonly variant: 'high';
        };
        readonly observer: {
            readonly model: 'opencode-go/mimo-v2.5';
        };
    };
};
export type PresetName = keyof typeof MODEL_MAPPINGS;
export type GeneratedPresetName = (typeof GENERATED_PRESETS)[number];
export declare function isGeneratedPresetName(value: string): value is GeneratedPresetName;
export declare function getGeneratedPresetNames(): GeneratedPresetName[];
export declare function generateLiteConfig(installConfig: InstallConfig): Record<string, unknown>;
