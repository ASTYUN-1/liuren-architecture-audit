/**
 * Register a command hook in the OpenCode config if it doesn't already exist.
 * Returns true if the command was registered, false if it already existed.
 */
export declare function registerCommandHook(opencodeConfig: Record<string, unknown>, commandName: string, template: string, description: string): boolean;
