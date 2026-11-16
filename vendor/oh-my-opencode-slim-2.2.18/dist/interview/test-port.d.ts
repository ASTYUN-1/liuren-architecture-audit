import { type Server } from 'node:http';
/**
 * Bind an OS-assigned port on localhost and keep the server listening.
 *
 * Tests hand `server` to the interview server factories (via their
 * optional `server` config) so the real server adopts the already-bound
 * listener instead of racing through a bind/close/bind TOCTOU window
 * between port discovery and the real bind.
 *
 * The placeholder 404 handler makes dashboard health probes fail fast
 * (non-OK response, no timeout wait), so a held port never looks like a
 * live dashboard to `tryBecomeDashboard`.
 */
export declare function bindFreePort(): Promise<{
    port: number;
    server: Server;
}>;
