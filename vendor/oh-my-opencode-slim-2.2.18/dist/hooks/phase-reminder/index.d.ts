/**
 * Phase reminder to append after each latest user message.
 *
 * Keeping this at the tail preserves immediate workflow guidance without
 * mutating the cached system prompt or prepending request-local content ahead
 * of the user's actual turn.
 */
import { PHASE_REMINDER } from '../../config/constants';
import { type MessagePart } from '../types';
export { PHASE_REMINDER };
export declare const PHASE_REMINDER_METADATA_KEY = "oh-my-opencode-slim.phaseReminder";
export declare function hasPhaseReminder(part: MessagePart): boolean;
interface PhaseReminderOptions {
    shouldInject?: (sessionID: string) => boolean;
}
/**
 * Creates the experimental.chat.messages.transform hook for phase reminder injection.
 * This hook runs right before sending to API, so it doesn't affect UI display.
 * Only injects for the orchestrator agent.
 */
export declare function createPhaseReminderHook(options?: PhaseReminderOptions): {
    'experimental.chat.messages.transform': (_input: Record<string, never>, output: {
        messages?: unknown;
    }) => Promise<void>;
};
