import type { Plugin } from '@opencode-ai/plugin';
import { type MultiplexerConfig } from './config';
/**
 * Decide whether multiplexer pane management initializes for a plugin
 * input. v1 hosts (hostFlavor absent) keep the exact env-based
 * conditions — configured type, resolvable multiplexer, inside-session
 * env marker; v2 hosts, marked `hostFlavor: 'v2'` by the v2 client shim,
 * are gated off before any multiplexer initialization runs.
 */
export declare function shouldEnableMultiplexer(input: {
    hostFlavor?: string;
    multiplexerConfig: MultiplexerConfig;
}): boolean;
/**
 * Config handed to MultiplexerSessionManager. The manager is created
 * unconditionally (its lifecycle hooks are wired into the job coordinator),
 * but it self-gates only on env (inside tmux/zellij) — which would
 * incorrectly self-enable on a v2 host running inside tmux. v2 hosts are
 * therefore forced to type 'none', which disables every manager path (all
 * its public methods no-op when `enabled` is false). v1 hosts receive the
 * real config object unchanged.
 */
export declare function sessionManagerMultiplexerConfig(hostFlavor: string | undefined, config: MultiplexerConfig): MultiplexerConfig;
export declare const OhMyOpenCodeLite: Plugin;
declare const _default: {
    id: string;
    server: Plugin;
    setup: (ctx: import("./v2").V2Context) => Promise<import("./v2").V2Cleanup>;
};
export default _default;
export type { AgentName, AgentOverrideConfig, McpName, MultiplexerConfig, MultiplexerLayout, MultiplexerType, PluginConfig, } from './config';
export type { RemoteMcpConfig } from './mcp';
