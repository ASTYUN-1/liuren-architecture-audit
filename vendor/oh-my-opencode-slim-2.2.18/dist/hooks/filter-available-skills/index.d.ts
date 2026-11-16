/**
 * Filter available_skills block based on the current agent's permission.skill rules.
 * OpenCode core injects `<available_skills>` globally, so this hook rewrites that
 * block before the prompt is sent.
 */
import type { PluginInput } from '@opencode-ai/plugin';
import type { RuntimeConfig } from '../../config/runtime';
type SkillRule = 'allow' | 'ask' | 'deny';
declare function filterAvailableSkillsText(text: string, permissionRules: Record<string, SkillRule>): string;
/**
 * Creates the experimental.chat.messages.transform hook for filtering available skills.
 * This hook runs right before sending to API, so it doesn't affect UI display.
 */
export declare function createFilterAvailableSkillsHook(_ctx: PluginInput, runtime: RuntimeConfig): {
    'experimental.chat.messages.transform': (_input: Record<string, never>, output: {
        messages?: unknown;
    }) => Promise<void>;
};
export { filterAvailableSkillsText };
