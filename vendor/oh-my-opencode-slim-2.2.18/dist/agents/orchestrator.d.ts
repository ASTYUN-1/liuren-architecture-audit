import type { AgentConfig } from '@opencode-ai/sdk/v2';
export interface AgentDefinition {
    name: string;
    displayName?: string;
    description?: string;
    config: AgentConfig;
    /** Priority-ordered model entries for runtime fallback resolution. */
    _modelArray?: Array<{
        id: string;
        variant?: string;
    }>;
}
/**
 * Resolve agent prompt from inline/file/append inputs.
 *
 * Precedence: inline prompt > file prompt > fallback. An explicit inline
 * `override.prompt` wins over a `<agent>.md` file; the file is the
 * shared default. `customAppendPrompt` always appends after whichever base
 * won. Deterministic per session (construction-time only) — cache-safe.
 */
export declare function resolvePrompt(agentName: string, inlinePrompt: string | undefined, filePrompt: string | undefined, fallback: string, customAppendPrompt?: string): string;
/**
 * Build the orchestrator prompt with dynamic agent filtering.
 * @param disabledAgents - Set of disabled agent names to exclude from the prompt
 * @param waitForUserEnabled - Whether explicit text-only HITL waiting is available
 * @param wakeSchedulerEnabled - Whether the orchestrator wake scheduler can resume the session after idle
 * @returns The complete orchestrator prompt string
 */
export declare function buildOrchestratorPrompt(disabledAgents?: ReadonlySet<string>, excludeDescriptions?: string[], waitForUserEnabled?: boolean, wakeSchedulerEnabled?: boolean): string;
export declare function createOrchestratorAgent(model?: string | Array<string | {
    id: string;
    variant?: string;
}>, customPrompt?: string, customAppendPrompt?: string, disabledAgents?: Set<string>, excludeDescriptions?: string[], waitForUserEnabled?: boolean, wakeSchedulerEnabled?: boolean): AgentDefinition;
