/**
 * Compile-time contract for OpenCode session/tool client call shapes.
 *
 * WHY THIS EXISTS
 * ---------------
 * The runtime OpenCode client (`input.client`, typed from the root
 * `@opencode-ai/sdk`) uses a NESTED `{ path, query, body }` request shape.
 * A premature v2 migration shipped FLAT shapes (`{ sessionID }`) against that
 * v1 runtime client. Unit tests mocked the client with `as never`/`as any`
 * and test files are excluded from `tsc` (the tsconfig excludes `*.test.ts`), so
 * the shape mismatch was never caught at compile time.
 *
 * This file is NOT a `.test.ts` — it lives in `src/` so `bun run typecheck`
 * compiles it. The valid calls pin the exact shapes the source produces; the
 * `@ts-expect-error` blocks assert the broken flat shapes are REJECTED. If a
 * revert re-introduces a flat call, `tsc --noEmit` fails.
 *
 * It is type-only: the no-op handle means nothing executes. It has no runtime
 * test and is intentionally not part of the bun test suite.
 */
export {};
