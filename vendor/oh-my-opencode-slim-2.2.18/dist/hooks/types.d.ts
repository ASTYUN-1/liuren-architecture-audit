/**
 * Shared message type shapes for the OpenCode plugin API's `messages` array.
 *
 * These types describe the structure of chat messages passed through
 * `experimental.chat.messages.transform` and related hooks. All fields
 * are unioned across the files that previously defined them privately -
 * optional extras are harmless under structural typing.
 */
export type MessageInfo = {
    role: string;
    agent?: string;
    sessionID?: string;
    id?: string;
};
export type MessagePart = {
    type: string;
    text?: string;
    [key: string]: unknown;
};
export type MessageWithParts = {
    info: MessageInfo;
    parts: MessagePart[];
};
export declare function isMessageWithParts(message: unknown): message is MessageWithParts;
export declare function isUserMessageWithParts(message: unknown): message is MessageWithParts;
export declare function findLatestUserMessage(messages: unknown[]): MessageWithParts | undefined;
/**
 * A user message that can be replayed into a fallback prompt.
 *
 * Accepts both the v1 transform shape (`{ info: { role: 'user' }, parts }`)
 * and the v2 `session.messages()` shape (`{ type: 'user', text }`) returned
 * by the plugin SDK's HTTP API since OpenCode 1.18.
 */
export type ReplayableUserMessage = MessageWithParts | {
    type: 'user';
    text?: string;
};
export declare function isReplayableUserMessage(message: unknown): message is ReplayableUserMessage;
export declare function partsFromReplayMessage(message: ReplayableUserMessage): MessagePart[];
