/**
 * v2 → v1 event mapper for the v2 event pump.
 *
 * v2 renamed/re-shaped several server events the v1 hooks depend on:
 * - `session.idle` is gone (`session.status` with `status.type: 'idle'`);
 * - `session.created` carries flat `{sessionID, parentID?}` instead of
 *   v1's `properties.info` object;
 * - token/cache telemetry moved to `session.usage.updated` /
 *   `session.step.ended` (v2 has no `message.updated`).
 *
 * `mapV2EventToV1` is additive synthesis only: the first element of the
 * returned array is ALWAYS the raw input event, unmodified (byte-identical
 * reference), so v2-native handlers (interview bridge) and any v1 handler
 * already tolerant of the v2 shape keep seeing it. Synthesized v1-shape
 * events are appended after it.
 *
 * The synthesized shapes are pinned to what the v1 consumers actually read:
 * - `session.created` early registration (task-session-manager
 *   event-router): `properties.info.{id,parentID,agent?}` — plugin
 *   relevance is gated on `info.parentID` (child sessions only).
 * - `message.updated` telemetry (cache-monitor
 *   parseCompletedAssistantMessage): `properties.info.{role:'assistant',
 *   sessionID, id, time.completed, tokens.input, tokens.cache.read,
 *   tokens.cache.write}`.
 */
/**
 * Map one v2 server event into zero or more v1-shape events.
 *
 * Returns `[rawEvent, ...synthesizedV1Shapes]` — the raw event is always
 * first and never mutated. Synthesis:
 * - idle `session.status` → v1 `session.idle` `{sessionID}`;
 * - child `session.created` (parentID present) → v1 early-registration
 *   shape `{info: {id, parentID, title?, agent?}}`;
 * - usage telemetry → v1 completed-assistant `message.updated`.
 *
 * `interviewBridge.handleEvent` keeps receiving the RAW v2 event (the
 * setup pump dispatches it before iterating this array).
 */
export declare function mapV2EventToV1(event: Record<string, unknown>): Array<Record<string, unknown>>;
