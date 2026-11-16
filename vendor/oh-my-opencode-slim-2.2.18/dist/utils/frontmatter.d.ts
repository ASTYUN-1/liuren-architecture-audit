/**
 * Parse `---` delimited frontmatter from a string.
 * Handles both `\n` and `\r\n` line endings.
 * Returns null if no frontmatter is found.
 */
export declare function parseFrontmatter(content: string): Record<string, string> | null;
