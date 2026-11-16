import { type MessageWithParts } from './types';
export declare function processImageAttachments(args: {
    messages: MessageWithParts[];
    workDir: string;
    imageRouting: 'auto' | 'direct';
    disabledAgents: ReadonlySet<string>;
    log: (msg: string) => void;
}): boolean;
