import { type ToolDefinition } from '@opencode-ai/plugin';
import { type AcpAgentsConfig } from '../config';
export declare function createAcpInitializeParams(): {
    protocolVersion: number;
    clientCapabilities: {};
    clientInfo: {
        name: string;
        version: string;
    };
};
export declare function createAcpRunTool(agents?: AcpAgentsConfig): ToolDefinition;
