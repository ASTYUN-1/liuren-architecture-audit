export declare const SLIM_INTERNAL_INITIATOR_MARKER = "<!-- SLIM_INTERNAL_INITIATOR -->";
export declare const INTERNAL_INITIATOR_METADATA_KEY = "oh-my-opencode-slim.internalInitiator";
export declare function createInternalAgentTextPart(text: string): {
    type: 'text';
    text: string;
    synthetic: true;
    metadata: {
        'oh-my-opencode-slim.internalInitiator': true;
    };
};
export declare function isInternalInitiatorPart(part: unknown): boolean;
