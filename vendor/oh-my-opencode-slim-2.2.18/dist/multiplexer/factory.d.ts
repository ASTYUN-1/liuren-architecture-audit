/**
 * Multiplexer factory - creates the appropriate multiplexer instance
 */
import type { MultiplexerConfig } from '../config/schema';
import type { Multiplexer } from './types';
/**
 * Create a multiplexer instance based on config.
 *
 * Do not cache instances: tmux/zellij/herdr integrations may depend on
 * per-process environment like TMUX_PANE/ZELLIJ/HERDR_PANE_ID, which should
 * be captured fresh for each plugin context.
 */
export declare function getMultiplexer(config: MultiplexerConfig): Multiplexer | null;
/**
 * Start background availability check for a multiplexer
 */
export declare function startAvailabilityCheck(config: MultiplexerConfig): void;
