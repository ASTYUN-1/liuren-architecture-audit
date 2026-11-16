import { CUSTOM_SKILLS, type CustomSkill } from './custom-skills-registry';
export { CUSTOM_SKILLS, type CustomSkill };
/**
 * Get the target directory for custom skills installation.
 */
export declare function getCustomSkillsDir(): string;
/**
 * Install a custom skill by copying from src/skills/ to the OpenCode skills directory
 * @param skill - The custom skill to install
 * @returns True if installation succeeded, false otherwise
 * @deprecated Use syncBundledSkillsFromPackage instead.
 */
export declare function installCustomSkill(skill: CustomSkill): boolean;
