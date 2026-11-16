/**
 * A skill that is managed externally (e.g. user-installed) and needs
 * permission grants but is NOT installed by this plugin's CLI.
 */
export interface PermissionOnlySkill {
    /** Skill name - must match the name OpenCode uses for permission checks */
    name: string;
    /** List of agents that should auto-allow this skill */
    allowedAgents: string[];
    /** Human-readable description (for documentation only) */
    description: string;
}
/**
 * Skills managed externally (not installed by this plugin's CLI).
 * Entries here only affect agent permission grants - nothing is installed.
 */
export declare const PERMISSION_ONLY_SKILLS: PermissionOnlySkill[];
/**
 * Get permission presets for a specific agent based on bundled skills.
 * @param agentName - The name of the agent
 * @param skillList - Optional explicit list of skills to allow (overrides defaults)
 * @returns Permission rules for the skill permission type
 */
export declare function getSkillPermissionsForAgent(agentName: string, skillList?: readonly string[], disabledSkillNames?: readonly string[]): Record<string, 'allow' | 'ask' | 'deny'>;
