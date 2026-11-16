type SessionMetadataEviction = (sessionID: string) => void;
export declare class SessionMetadataStore {
    #private;
    constructor(options: {
        maxEntries: number;
        onEvict?: SessionMetadataEviction;
    });
    getAgent(sessionID: string): string | undefined;
    getModel(sessionID: string): string | undefined;
    setModel(sessionID: string, model: string): void;
    getDirectory(sessionID: string): string | undefined;
    setAgent(sessionID: string, agent: string): void;
    setDirectory(sessionID: string, directory: string): void;
    markOrchestratorActive(sessionID: string): void;
    markOrchestratorIdle(sessionID: string): void;
    delete(sessionID: string): void;
    get size(): number;
    hasAgent(sessionID: string): boolean;
    hasDirectory(sessionID: string): boolean;
}
export {};
