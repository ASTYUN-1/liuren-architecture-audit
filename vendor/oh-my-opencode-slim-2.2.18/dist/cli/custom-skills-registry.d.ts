/**
 * A custom skill bundled in this repository.
 * Unlike npx-installed skills, these are copied from src/skills/ to the OpenCode skills directory
 */
export interface CustomSkill {
    /** Skill name (folder name) */
    name: string;
    /** Human-readable description */
    description: string;
    /** List of agents that should auto-allow this skill */
    allowedAgents: string[];
    /** Source path in this repo (relative to project root) */
    sourcePath: string;
}
/**
 * Registry of custom skills bundled in this repository.
 */
export declare const CUSTOM_SKILLS: CustomSkill[];
