import { type AgentDefinition } from './orchestrator';
/**
 * Create the council agent definition.
 * The council agent synthesizes councillor responses into a structured report.
 * It does not dispatch councillors — the orchestrator handles that.
 */
export declare function createCouncilAgent(model: string, customPrompt?: string, customAppendPrompt?: string): AgentDefinition;
