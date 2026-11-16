/**
 * Runtime model fallback for foreground (interactive) agent sessions.
 *
 * When OpenCode fires a session.error, message.updated, or session.status
 * event containing a transient error (rate-limit, 403/Forbidden, etc.), this
 * manager:
 *   1. Looks up the next untried model in the agent's configured chain
 *   2. Aborts the rate-limited prompt via client.session.abort() on the
 *      session.status retry path; session.error and message.updated paths
 *      re-prompt directly without abort.
 *   3. Re-queues the last user message via client.session.promptAsync()
 *      with the new model - promptAsync returns immediately so we never
 *      block the event handler waiting for a full LLM response.
 *
 * This mirrors the same fallback loop used for delegated sessions, but operates
 * reactively through the event system instead of wrapping prompt() in a
 * try/catch, which is not possible for interactive (foreground) sessions.
 */
import type { PluginInput } from '@opencode-ai/plugin';
import type { SessionLifecycle } from '../session-lifecycle';
export declare function isFailoverError(error: unknown): boolean;
/**
 * Checks whether an error is a transient/retryable error (rate-limit,
 * 403/Forbidden, etc.) that should trigger model fallback.
 */
export declare function isRetryableError(error: unknown): boolean;
/**
 * True when the error is the kind the runtime surfaces inline (401 auth,
 * 410 model gone) — persistent, user-visible, already in the conversation.
 * These should NOT get a toast; the runtime's inline rendering is enough.
 * Other failover errors (429 rate-limit, outage, etc.) get a toast instead.
 */
export declare function isInlineFailoverError(error: unknown): boolean;
/**
 * Manages runtime model fallback for foreground agent sessions.
 *
 * Constructed at plugin init with the ordered fallback chains for each agent
 * (built from _modelArray entries in agents.<name>.model).
 */
export declare class ForegroundFallbackManager {
    /**
     * Ordered fallback chains per agent.
     * e.g. { orchestrator: ['anthropic/claude-opus-4-5', 'openai/gpt-4o'] }
     * The first model that hasn't been tried yet is selected on each fallback.
     */
    private chains;
    private readonly enabled;
    private readonly input;
    /** Consecutive 429s tolerated on the same model before swap/abort. */
    private readonly maxRetries;
    /** sessionID → last observed model string ("providerID/modelID") */
    private readonly sessionModel;
    /** sessionID → agent name (populated from message.updated info.agent field) */
    private readonly sessionAgent;
    /** sessionID → set of models already attempted this session */
    private readonly sessionTried;
    /** Process-local sessions with an active fallback switch in flight. */
    private readonly inProgress;
    /** sessionID → timestamp of last trigger (for deduplication) */
    private readonly lastTrigger;
    /** sessionID → model in use when lastTrigger was set; dedup is bypassed
     *  when the model has changed, allowing the cascade to continue when a
     *  new fallback model also fails within the dedup window. */
    private readonly lastTriggerModel;
    /** sessionID → consecutive 429 count for the current model.
     *  Reset on model swap or session deletion. */
    private readonly sessionRetries;
    /** sessionID → chain-exhaustion stage:
     *   0 = not exhausted; 1 = chain exhausted once, reset to sticky fallback
     *   (one retry chance); 2 = exhausted again, aborted — stop intervening.
     *   Reset to 0 on successful responses or session deletion. */
    private readonly chainExhaustion;
    /** sessionID → notified when the session switched to a new model mid-flight
     *  (e.g. after a fallback re-prompt). Lets the background-task admission
     *  scheduler migrate provider/model accounting to the new model. */
    private readonly onSessionModelChanged?;
    /** Exposed for task-session-manager: prevents idle reconciliation
     *  while a fallback abort/re-prompt is in flight for this session. */
    isFallbackInProgress(sessionID: string): boolean;
    /**
     * True when this manager could still recover the session via fallback:
     * fallback is enabled, the session has a chain, and the chain is not
     * exhausted (stage < 2). Consumers (task-session-manager event router)
     * defer terminal bookkeeping for persistent 401/410 errors until
     * recovery is actually impossible.
     */
    willAttemptFallback(sessionID: string): boolean;
    /**
     * Disable the fallback chain for a specific agent.
     * After calling this, rate-limit errors for that agent surface instead of
     * silently falling back through the chain.
     */
    disableChain(agentName: string): void;
    registerSessionAgent(sessionID: string, agentName: string): void;
    constructor(
    /**
     * Ordered fallback chains per agent.
     * e.g. { orchestrator: ['anthropic/claude-opus-4-5', 'openai/gpt-4o'] }
     * The first model that hasn't been tried yet is selected on each fallback.
     */
    chains: Record<string, string[]>, enabled: boolean, input: PluginInput, 
    /** Consecutive 429s tolerated on the same model before swap/abort. */
    maxRetries?: number, coordinator?: SessionLifecycle, onSessionModelChanged?: (sessionID: string, model: string) => void);
    /**
     * Process an OpenCode plugin event.
     * Call this from the plugin's `event` hook for every event received.
     */
    handleEvent(rawEvent: unknown): Promise<void>;
    /** Increment retry counter and return true when the budget is exhausted.
     *  Used by shouldIntervene when tried > 0 — each retry counts toward the
     *  budget and only triggers fallback after maxRetries - 1 absorptions.
     *  First failover retry (tried === 0) bypasses the counter via shouldIntervene. */
    private consumeRetryBudget;
    /** Intervene immediately on first occurrence (tried === 0), otherwise
     *  delegate to retry budget. Used by all three event paths. */
    private shouldTriggerFallback;
    private tryFallback;
    /**
     * Fallback path for session.status retry events.  Aborts the retry loop
     * before falling back because promptAsync alone is ignored while the
     * session is in retry mode.  inProgress is set first so the
     * task-session-manager sees isFallbackInProgress()=true during the
     * abort idle window and does not cancel the pending task call.
     *
     * When no chain is available, do nothing (no abort, no log). Aborting
     * without a replacement model only races owners that manage their own
     * lifecycle (e.g. CouncilManager for councillor) and produces noise.
     */
    private tryFallbackWithAbort;
    private isDeduped;
    private execFallback;
    /**
     * Surface a TUI toast when the fallback switches models, so the user isn't
     * surprised by a different model responding (e.g. after a rate-limit on the
     * primary). 401/410 errors (auth, model gone) are already rendered inline by
     * the runtime, so those get no toast — the inline rendering is the notice.
     * Fire-and-forget; a failed toast is never fatal.
     */
    private showFallbackToast;
    /** True when resolveChain yields at least one model for this session. */
    private hasFallbackChain;
    /**
     * Determine the fallback chain to use for a session.
     *
     * Priority:
     * 1. Agent name known AND has a configured chain → return it directly
     * 2. Agent name known but NO chain → return [] (no fallback; never
     *    bleed into other agents' chains)
     * 3. Agent name unknown, current model known → search all chains for
     *    the model to infer which chain to use
     * 4. Nothing matches → flatten all chains as a last resort (only
     *    reached when both agent name and current model are unavailable)
     */
    private resolveChain;
}
