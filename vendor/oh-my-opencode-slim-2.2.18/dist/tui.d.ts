import type { TuiPlugin } from '@opencode-ai/plugin/tui';
import type { JSX } from '@opentui/solid';
import { type TuiSnapshot } from './tui-state';
export interface ActiveTmuxPaneRegistration {
    sessionId?: string;
    paneId?: string;
    ownerPid: number;
    lastRecordedAt: number;
}
/** Route shapes accepted by `syncTmuxPaneRegistration`: v1 `{ name, params }` and v2 `{ type, sessionID }`. */
export type TuiRouteView = {
    name?: string;
    params?: {
        sessionID?: unknown;
    };
} | {
    type?: string;
    sessionID?: string;
};
export declare function syncTmuxPaneRegistration(route: TuiRouteView, registration: ActiveTmuxPaneRegistration, now?: number): void;
export declare function splitSidebarModelId(model: string): {
    provider?: string;
    model: string;
};
export declare function getSidebarAgentNames(snapshot: TuiSnapshot): string[];
export declare function getActiveSidebarAgentNames(snapshot: TuiSnapshot): ReadonlySet<string>;
export declare function getSidebarActivityIndicator(active: boolean, now?: number): string;
export declare function getContrastForeground(accent: unknown, themeText: unknown, themeBackground: unknown): unknown;
export declare function readConfigInvalid(directory: string): boolean;
export declare function readCompactSidebar(directory: string): boolean;
interface V2TuiThemeTokens {
    text: {
        default: unknown;
        subdued: unknown;
    };
    background: {
        default: unknown;
    };
    border: {
        default: unknown;
    };
}
interface V2TuiSlotClaim {
    append?: string;
    prepend?: string;
    before?: string;
    after?: string;
    replace?: string;
    render: (input: {
        sessionID: string;
    }) => JSX.Element;
}
interface V2TuiContext {
    location?: {
        directory: string;
    };
    renderer: {
        requestRender: () => void;
    };
    theme: V2TuiThemeTokens;
    ui: {
        slot: (claim: V2TuiSlotClaim) => () => void;
        router: {
            current: () => {
                type?: string;
                sessionID?: string;
            };
        };
    };
}
/**
 * Dual contract: v1 hosts validate `{ id, tui }`, opencode2 validates
 * `{ id, setup }`; both ignore extra keys. Fixes #1002.
 */
interface TuiDualContractModule {
    id: string;
    tui: TuiPlugin;
    setup: (ctx: V2TuiContext) => Promise<undefined | (() => void)>;
}
declare const plugin: TuiDualContractModule;
export default plugin;
