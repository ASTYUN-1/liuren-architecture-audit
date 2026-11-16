export type ContinuationModelSelection = {
    model: {
        providerID: string;
        modelID: string;
    };
    variant?: string;
};
/**
 * Normalize the two runtime model shapes used across supported OpenCode
 * versions:
 * - chat.message / promptAsync: { providerID, modelID }
 * - current Session.model:      { providerID, id }
 */
export declare function parseContinuationModelSelection(value: unknown, variantOverride?: unknown): ContinuationModelSelection | undefined;
