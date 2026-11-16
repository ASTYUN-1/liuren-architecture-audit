type AgentPermission = Record<string, 'allow' | 'ask' | 'deny' | Record<string, 'allow' | 'ask' | 'deny'>>;
/**
 * Strict read-only tool permissions for advisory agents.
 *
 * Start with wildcard deny so newly-added tools are unavailable by default,
 * then allow only inspection/search tools. Explicitly deny known mutating and
 * delegation tools to make the read-only boundary obvious in generated config.
 */
export declare function createReadOnlyAgentPermission(): AgentPermission;
/**
 * Strict deny-all permissions for the council synthesis agent.
 *
 * The council agent is text-in/text-out only — it must NOT use any
 * file-inspection tools. Councillors already perform codebase exploration;
 * the council only reconciles their text output.
 */
export declare function createSynthesisOnlyPermission(): AgentPermission;
export {};
