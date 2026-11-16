import { z } from 'zod';
export declare const ProviderModelIdSchema: z.ZodString;
export declare const PermissionConfigSchema: z.ZodUnion<readonly [z.ZodEnum<{
    allow: "allow";
    ask: "ask";
    deny: "deny";
}>, z.ZodObject<{
    read: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>;
    edit: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>;
    glob: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>;
    grep: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>;
    list: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>;
    bash: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>;
    task: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>;
    external_directory: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>;
    lsp: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>;
    skill: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>;
    todowrite: z.ZodOptional<z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>;
    question: z.ZodOptional<z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>;
    webfetch: z.ZodOptional<z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>;
    websearch: z.ZodOptional<z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>;
    codesearch: z.ZodOptional<z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>;
    doom_loop: z.ZodOptional<z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>;
}, z.core.$catchall<z.ZodUnion<readonly [z.ZodEnum<{
    allow: "allow";
    ask: "ask";
    deny: "deny";
}>, z.ZodRecord<z.ZodString, z.ZodEnum<{
    allow: "allow";
    ask: "ask";
    deny: "deny";
}>>]>>>]>;
export declare const AgentColorSchema: z.ZodUnion<readonly [z.ZodString, z.ZodEnum<{
    accent: "accent";
    error: "error";
    info: "info";
    primary: "primary";
    secondary: "secondary";
    success: "success";
    warning: "warning";
}>]>;
export declare const ModelInheritanceSourceSchema: z.ZodEnum<{
    orchestrator: "orchestrator";
    session: "session";
}>;
export type ModelInheritanceSource = z.infer<typeof ModelInheritanceSourceSchema>;
export declare const AgentOverrideConfigSchema: z.ZodObject<{
    model: z.ZodOptional<z.ZodUnion<readonly [z.ZodString, z.ZodArray<z.ZodUnion<readonly [z.ZodString, z.ZodObject<{
        id: z.ZodString;
        variant: z.ZodOptional<z.ZodString>;
    }, z.core.$strip>]>>]>>;
    inheritModelFrom: z.ZodOptional<z.ZodEnum<{
        orchestrator: "orchestrator";
        session: "session";
    }>>;
    temperature: z.ZodOptional<z.ZodNumber>;
    variant: z.ZodCatch<z.ZodOptional<z.ZodString>>;
    skills: z.ZodOptional<z.ZodArray<z.ZodString>>;
    mcps: z.ZodOptional<z.ZodArray<z.ZodString>>;
    prompt: z.ZodOptional<z.ZodString>;
    orchestratorPrompt: z.ZodOptional<z.ZodString>;
    options: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    displayName: z.ZodOptional<z.ZodString>;
    color: z.ZodOptional<z.ZodUnion<readonly [z.ZodString, z.ZodEnum<{
        accent: "accent";
        error: "error";
        info: "info";
        primary: "primary";
        secondary: "secondary";
        success: "success";
        warning: "warning";
    }>]>>;
    description: z.ZodOptional<z.ZodString>;
    permission: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodObject<{
        read: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        edit: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        glob: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        grep: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        list: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        bash: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        task: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        external_directory: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        lsp: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        skill: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        todowrite: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
        question: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
        webfetch: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
        websearch: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
        codesearch: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
        doom_loop: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
    }, z.core.$catchall<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>>]>>;
}, z.core.$strict>;
export declare const MultiplexerTypeSchema: z.ZodEnum<{
    auto: "auto";
    cmux: "cmux";
    herdr: "herdr";
    kitty: "kitty";
    none: "none";
    tmux: "tmux";
    zellij: "zellij";
}>;
export type MultiplexerType = z.infer<typeof MultiplexerTypeSchema>;
export declare const MultiplexerLayoutSchema: z.ZodEnum<{
    "even-horizontal": "even-horizontal";
    "even-vertical": "even-vertical";
    "main-horizontal": "main-horizontal";
    "main-vertical": "main-vertical";
    tiled: "tiled";
}>;
export type MultiplexerLayout = z.infer<typeof MultiplexerLayoutSchema>;
export declare const ZellijPaneModeSchema: z.ZodEnum<{
    "agent-tab": "agent-tab";
    "current-tab": "current-tab";
}>;
export type ZellijPaneMode = z.infer<typeof ZellijPaneModeSchema>;
export declare const MultiplexerConfigSchema: z.ZodObject<{
    type: z.ZodDefault<z.ZodEnum<{
        auto: "auto";
        cmux: "cmux";
        herdr: "herdr";
        kitty: "kitty";
        none: "none";
        tmux: "tmux";
        zellij: "zellij";
    }>>;
    layout: z.ZodDefault<z.ZodEnum<{
        "even-horizontal": "even-horizontal";
        "even-vertical": "even-vertical";
        "main-horizontal": "main-horizontal";
        "main-vertical": "main-vertical";
        tiled: "tiled";
    }>>;
    main_pane_size: z.ZodDefault<z.ZodNumber>;
    zellij_pane_mode: z.ZodDefault<z.ZodEnum<{
        "agent-tab": "agent-tab";
        "current-tab": "current-tab";
    }>>;
}, z.core.$strip>;
export type MultiplexerConfig = z.infer<typeof MultiplexerConfigSchema>;
export type AgentOverrideConfig = z.infer<typeof AgentOverrideConfigSchema>;
/** Normalized model entry with optional per-model variant. */
export type ModelEntry = {
    id: string;
    variant?: string;
};
export declare const PresetSchema: z.ZodRecord<z.ZodString, z.ZodObject<{
    model: z.ZodOptional<z.ZodUnion<readonly [z.ZodString, z.ZodArray<z.ZodUnion<readonly [z.ZodString, z.ZodObject<{
        id: z.ZodString;
        variant: z.ZodOptional<z.ZodString>;
    }, z.core.$strip>]>>]>>;
    inheritModelFrom: z.ZodOptional<z.ZodEnum<{
        orchestrator: "orchestrator";
        session: "session";
    }>>;
    temperature: z.ZodOptional<z.ZodNumber>;
    variant: z.ZodCatch<z.ZodOptional<z.ZodString>>;
    skills: z.ZodOptional<z.ZodArray<z.ZodString>>;
    mcps: z.ZodOptional<z.ZodArray<z.ZodString>>;
    prompt: z.ZodOptional<z.ZodString>;
    orchestratorPrompt: z.ZodOptional<z.ZodString>;
    options: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    displayName: z.ZodOptional<z.ZodString>;
    color: z.ZodOptional<z.ZodUnion<readonly [z.ZodString, z.ZodEnum<{
        accent: "accent";
        error: "error";
        info: "info";
        primary: "primary";
        secondary: "secondary";
        success: "success";
        warning: "warning";
    }>]>>;
    description: z.ZodOptional<z.ZodString>;
    permission: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodObject<{
        read: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        edit: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        glob: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        grep: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        list: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        bash: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        task: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        external_directory: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        lsp: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        skill: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>;
        todowrite: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
        question: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
        webfetch: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
        websearch: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
        codesearch: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
        doom_loop: z.ZodOptional<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>;
    }, z.core.$catchall<z.ZodUnion<readonly [z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        deny: "deny";
    }>>]>>>]>>;
}, z.core.$strict>>;
export type Preset = z.infer<typeof PresetSchema>;
export declare const McpNameSchema: z.ZodEnum<{
    context7: "context7";
    gh_grep: "gh_grep";
}>;
export type McpName = z.infer<typeof McpNameSchema>;
export declare const InterviewConfigSchema: z.ZodObject<{
    maxQuestions: z.ZodDefault<z.ZodNumber>;
    outputFolder: z.ZodDefault<z.ZodString>;
    autoOpenBrowser: z.ZodDefault<z.ZodBoolean>;
    port: z.ZodDefault<z.ZodNumber>;
    dashboard: z.ZodDefault<z.ZodBoolean>;
}, z.core.$strip>;
export type InterviewConfig = z.infer<typeof InterviewConfigSchema>;
export declare const BackgroundTaskConcurrencyConfigSchema: z.ZodDefault<z.ZodObject<{
    defaultConcurrency: z.ZodDefault<z.ZodNumber>;
    providerConcurrency: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodNumber>>;
    modelConcurrency: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodNumber>>;
}, z.core.$strict>>;
export type BackgroundTaskConcurrencyConfig = z.infer<typeof BackgroundTaskConcurrencyConfigSchema>;
export declare const BackgroundJobsConfigSchema: z.ZodObject<{
    strategy: z.ZodDefault<z.ZodEnum<{
        "checkpoint-compatible": "checkpoint-compatible";
        latest: "latest";
    }>>;
    maxSessionsPerAgent: z.ZodDefault<z.ZodNumber>;
    maxContextLines: z.ZodDefault<z.ZodNumber>;
    readContextMinLines: z.ZodDefault<z.ZodNumber>;
    readContextMaxFiles: z.ZodDefault<z.ZodNumber>;
    maxRetainedSnapshots: z.ZodDefault<z.ZodNumber>;
    orchestratorWake: z.ZodDefault<z.ZodObject<{
        enabled: z.ZodDefault<z.ZodBoolean>;
        intervalMs: z.ZodDefault<z.ZodNumber>;
    }, z.core.$strip>>;
    wallClockTimeoutMs: z.ZodDefault<z.ZodUnion<readonly [z.ZodLiteral<0>, z.ZodNumber]>>;
    abortGraceMs: z.ZodDefault<z.ZodNumber>;
    concurrency: z.ZodDefault<z.ZodObject<{
        defaultConcurrency: z.ZodDefault<z.ZodNumber>;
        providerConcurrency: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodNumber>>;
        modelConcurrency: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodNumber>>;
    }, z.core.$strict>>;
    waitForUserGuard: z.ZodDefault<z.ZodBoolean>;
}, z.core.$strip>;
export type BackgroundJobsConfig = z.infer<typeof BackgroundJobsConfigSchema>;
/**
 * Fallback config fields accepted by versions before 2.3.x but no longer
 * meaningful. Kept only so that existing user/project configs containing
 * them still parse: the loader emits a deprecation warning and these keys
 * are stripped before strict validation. Without this, a stale field would
 * make the whole config file fail and drop all the user's settings.
 */
export declare const LEGACY_FALLBACK_KEYS: readonly ['timeoutMs', 'retryDelayMs', 'retry_on_empty', 'runtimeOverride'];
export declare const FailoverConfigSchema: z.ZodPreprocess<z.ZodObject<{
    enabled: z.ZodDefault<z.ZodBoolean>;
    maxRetries: z.ZodDefault<z.ZodNumber>;
}, z.core.$strict>>;
export type FailoverConfig = z.infer<typeof FailoverConfigSchema>;
export declare const CompanionConfigSchema: z.ZodObject<{
    enabled: z.ZodOptional<z.ZodBoolean>;
    binaryPath: z.ZodOptional<z.ZodString>;
    position: z.ZodOptional<z.ZodEnum<{
        "bottom-left": "bottom-left";
        "bottom-right": "bottom-right";
        "top-left": "top-left";
        "top-right": "top-right";
    }>>;
    size: z.ZodOptional<z.ZodEnum<{
        large: "large";
        medium: "medium";
        small: "small";
    }>>;
    gifPack: z.ZodOptional<z.ZodEnum<{
        default: "default";
    }>>;
    loopStyle: z.ZodOptional<z.ZodEnum<{
        classic: "classic";
        smooth: "smooth";
    }>>;
    speed: z.ZodOptional<z.ZodNumber>;
    debug: z.ZodOptional<z.ZodBoolean>;
}, z.core.$strip>;
export type CompanionConfig = z.infer<typeof CompanionConfigSchema>;
export declare const WebfetchConfigSchema: z.ZodObject<{
    enabled: z.ZodDefault<z.ZodBoolean>;
    model: z.ZodOptional<z.ZodUnion<readonly [z.ZodString, z.ZodArray<z.ZodUnion<readonly [z.ZodString, z.ZodObject<{
        id: z.ZodString;
        variant: z.ZodOptional<z.ZodString>;
    }, z.core.$strip>]>>]>>;
}, z.core.$strict>;
export type WebfetchConfig = z.infer<typeof WebfetchConfigSchema>;
export declare const AcpAgentPermissionModeSchema: z.ZodEnum<{
    allow: "allow";
    ask: "ask";
    reject: "reject";
}>;
export declare const MAX_ACP_TIMEOUT_MS = 2147483647;
export declare const AcpAgentConfigSchema: z.ZodObject<{
    command: z.ZodString;
    args: z.ZodDefault<z.ZodArray<z.ZodString>>;
    env: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodString>>;
    cwd: z.ZodOptional<z.ZodString>;
    description: z.ZodOptional<z.ZodString>;
    prompt: z.ZodOptional<z.ZodString>;
    orchestratorPrompt: z.ZodOptional<z.ZodString>;
    wrapperModel: z.ZodOptional<z.ZodString>;
    timeoutMs: z.ZodDefault<z.ZodNumber>;
    permissionMode: z.ZodDefault<z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        reject: "reject";
    }>>;
}, z.core.$strict>;
export declare const AcpAgentsConfigSchema: z.ZodRecord<z.ZodString, z.ZodObject<{
    command: z.ZodString;
    args: z.ZodDefault<z.ZodArray<z.ZodString>>;
    env: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodString>>;
    cwd: z.ZodOptional<z.ZodString>;
    description: z.ZodOptional<z.ZodString>;
    prompt: z.ZodOptional<z.ZodString>;
    orchestratorPrompt: z.ZodOptional<z.ZodString>;
    wrapperModel: z.ZodOptional<z.ZodString>;
    timeoutMs: z.ZodDefault<z.ZodNumber>;
    permissionMode: z.ZodDefault<z.ZodEnum<{
        allow: "allow";
        ask: "ask";
        reject: "reject";
    }>>;
}, z.core.$strict>>;
export type AcpAgentPermissionMode = z.infer<typeof AcpAgentPermissionModeSchema>;
export type AcpAgentConfig = z.infer<typeof AcpAgentConfigSchema>;
export type AcpAgentsConfig = z.infer<typeof AcpAgentsConfigSchema>;
export declare const PluginConfigSchema: z.ZodObject<{
    preset: z.ZodOptional<z.ZodString>;
    setDefaultAgent: z.ZodOptional<z.ZodBoolean>;
    compactSidebar: z.ZodOptional<z.ZodBoolean>;
    stripOrchestratorModel: z.ZodOptional<z.ZodBoolean>;
    autoUpdate: z.ZodOptional<z.ZodBoolean>;
    presets: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodRecord<z.ZodString, z.ZodObject<{
        model: z.ZodOptional<z.ZodUnion<readonly [z.ZodString, z.ZodArray<z.ZodUnion<readonly [z.ZodString, z.ZodObject<{
            id: z.ZodString;
            variant: z.ZodOptional<z.ZodString>;
        }, z.core.$strip>]>>]>>;
        inheritModelFrom: z.ZodOptional<z.ZodEnum<{
            orchestrator: "orchestrator";
            session: "session";
        }>>;
        temperature: z.ZodOptional<z.ZodNumber>;
        variant: z.ZodCatch<z.ZodOptional<z.ZodString>>;
        skills: z.ZodOptional<z.ZodArray<z.ZodString>>;
        mcps: z.ZodOptional<z.ZodArray<z.ZodString>>;
        prompt: z.ZodOptional<z.ZodString>;
        orchestratorPrompt: z.ZodOptional<z.ZodString>;
        options: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
        displayName: z.ZodOptional<z.ZodString>;
        color: z.ZodOptional<z.ZodUnion<readonly [z.ZodString, z.ZodEnum<{
            accent: "accent";
            error: "error";
            info: "info";
            primary: "primary";
            secondary: "secondary";
            success: "success";
            warning: "warning";
        }>]>>;
        description: z.ZodOptional<z.ZodString>;
        permission: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodObject<{
            read: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            edit: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            glob: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            grep: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            list: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            bash: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            task: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            external_directory: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            lsp: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            skill: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            todowrite: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
            question: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
            webfetch: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
            websearch: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
            codesearch: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
            doom_loop: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
        }, z.core.$catchall<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>>]>>;
    }, z.core.$strict>>>>;
    agents: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodObject<{
        model: z.ZodOptional<z.ZodUnion<readonly [z.ZodString, z.ZodArray<z.ZodUnion<readonly [z.ZodString, z.ZodObject<{
            id: z.ZodString;
            variant: z.ZodOptional<z.ZodString>;
        }, z.core.$strip>]>>]>>;
        inheritModelFrom: z.ZodOptional<z.ZodEnum<{
            orchestrator: "orchestrator";
            session: "session";
        }>>;
        temperature: z.ZodOptional<z.ZodNumber>;
        variant: z.ZodCatch<z.ZodOptional<z.ZodString>>;
        skills: z.ZodOptional<z.ZodArray<z.ZodString>>;
        mcps: z.ZodOptional<z.ZodArray<z.ZodString>>;
        prompt: z.ZodOptional<z.ZodString>;
        orchestratorPrompt: z.ZodOptional<z.ZodString>;
        options: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
        displayName: z.ZodOptional<z.ZodString>;
        color: z.ZodOptional<z.ZodUnion<readonly [z.ZodString, z.ZodEnum<{
            accent: "accent";
            error: "error";
            info: "info";
            primary: "primary";
            secondary: "secondary";
            success: "success";
            warning: "warning";
        }>]>>;
        description: z.ZodOptional<z.ZodString>;
        permission: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodObject<{
            read: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            edit: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            glob: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            grep: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            list: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            bash: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            task: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            external_directory: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            lsp: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            skill: z.ZodOptional<z.ZodUnion<readonly [z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>]>>;
            todowrite: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
            question: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
            webfetch: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
            websearch: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
            codesearch: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
            doom_loop: z.ZodOptional<z.ZodEnum<{
                allow: "allow";
                ask: "ask";
                deny: "deny";
            }>>;
        }, z.core.$catchall<z.ZodUnion<readonly [z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>, z.ZodRecord<z.ZodString, z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            deny: "deny";
        }>>]>>>]>>;
    }, z.core.$strict>>>;
    disabled_agents: z.ZodOptional<z.ZodArray<z.ZodString>>;
    image_routing: z.ZodOptional<z.ZodEnum<{
        auto: "auto";
        direct: "direct";
    }>>;
    disabled_mcps: z.ZodOptional<z.ZodArray<z.ZodString>>;
    disabled_tools: z.ZodOptional<z.ZodArray<z.ZodString>>;
    disabled_skills: z.ZodOptional<z.ZodArray<z.ZodString>>;
    multiplexer: z.ZodOptional<z.ZodObject<{
        type: z.ZodDefault<z.ZodEnum<{
            auto: "auto";
            cmux: "cmux";
            herdr: "herdr";
            kitty: "kitty";
            none: "none";
            tmux: "tmux";
            zellij: "zellij";
        }>>;
        layout: z.ZodDefault<z.ZodEnum<{
            "even-horizontal": "even-horizontal";
            "even-vertical": "even-vertical";
            "main-horizontal": "main-horizontal";
            "main-vertical": "main-vertical";
            tiled: "tiled";
        }>>;
        main_pane_size: z.ZodDefault<z.ZodNumber>;
        zellij_pane_mode: z.ZodDefault<z.ZodEnum<{
            "agent-tab": "agent-tab";
            "current-tab": "current-tab";
        }>>;
    }, z.core.$strip>>;
    interview: z.ZodOptional<z.ZodObject<{
        maxQuestions: z.ZodDefault<z.ZodNumber>;
        outputFolder: z.ZodDefault<z.ZodString>;
        autoOpenBrowser: z.ZodDefault<z.ZodBoolean>;
        port: z.ZodDefault<z.ZodNumber>;
        dashboard: z.ZodDefault<z.ZodBoolean>;
    }, z.core.$strip>>;
    backgroundJobs: z.ZodOptional<z.ZodObject<{
        strategy: z.ZodDefault<z.ZodEnum<{
            "checkpoint-compatible": "checkpoint-compatible";
            latest: "latest";
        }>>;
        maxSessionsPerAgent: z.ZodDefault<z.ZodNumber>;
        maxContextLines: z.ZodDefault<z.ZodNumber>;
        readContextMinLines: z.ZodDefault<z.ZodNumber>;
        readContextMaxFiles: z.ZodDefault<z.ZodNumber>;
        maxRetainedSnapshots: z.ZodDefault<z.ZodNumber>;
        orchestratorWake: z.ZodDefault<z.ZodObject<{
            enabled: z.ZodDefault<z.ZodBoolean>;
            intervalMs: z.ZodDefault<z.ZodNumber>;
        }, z.core.$strip>>;
        wallClockTimeoutMs: z.ZodDefault<z.ZodUnion<readonly [z.ZodLiteral<0>, z.ZodNumber]>>;
        abortGraceMs: z.ZodDefault<z.ZodNumber>;
        concurrency: z.ZodDefault<z.ZodObject<{
            defaultConcurrency: z.ZodDefault<z.ZodNumber>;
            providerConcurrency: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodNumber>>;
            modelConcurrency: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodNumber>>;
        }, z.core.$strict>>;
        waitForUserGuard: z.ZodDefault<z.ZodBoolean>;
    }, z.core.$strip>>;
    fallback: z.ZodOptional<z.ZodPreprocess<z.ZodObject<{
        enabled: z.ZodDefault<z.ZodBoolean>;
        maxRetries: z.ZodDefault<z.ZodNumber>;
    }, z.core.$strict>>>;
    council: z.ZodOptional<z.ZodPipe<z.ZodObject<{
        presets: z.ZodRecord<z.ZodString, z.ZodPipe<z.ZodRecord<z.ZodString, z.ZodRecord<z.ZodString, z.ZodUnknown>>, z.ZodTransform<Record<string, {
            model: string;
            variant: string | undefined;
            prompt: string | undefined;
            models: import("./council-schema").CouncillorModelEntry[];
        }>, Record<string, Record<string, unknown>>>>>;
        default_preset: z.ZodDefault<z.ZodString>;
    }, z.core.$loose>, z.ZodTransform<{
        presets: Record<string, Record<string, {
            model: string;
            variant: string | undefined;
            prompt: string | undefined;
            models: import("./council-schema").CouncillorModelEntry[];
        }>>;
        default_preset: string;
        _deprecated: string[] | undefined;
    }, {
        [x: string]: unknown;
        presets: Record<string, Record<string, {
            model: string;
            variant: string | undefined;
            prompt: string | undefined;
            models: import("./council-schema").CouncillorModelEntry[];
        }>>;
        default_preset: string;
    }>>>;
    companion: z.ZodOptional<z.ZodObject<{
        enabled: z.ZodOptional<z.ZodBoolean>;
        binaryPath: z.ZodOptional<z.ZodString>;
        position: z.ZodOptional<z.ZodEnum<{
            "bottom-left": "bottom-left";
            "bottom-right": "bottom-right";
            "top-left": "top-left";
            "top-right": "top-right";
        }>>;
        size: z.ZodOptional<z.ZodEnum<{
            large: "large";
            medium: "medium";
            small: "small";
        }>>;
        gifPack: z.ZodOptional<z.ZodEnum<{
            default: "default";
        }>>;
        loopStyle: z.ZodOptional<z.ZodEnum<{
            classic: "classic";
            smooth: "smooth";
        }>>;
        speed: z.ZodOptional<z.ZodNumber>;
        debug: z.ZodOptional<z.ZodBoolean>;
    }, z.core.$strip>>;
    webfetch: z.ZodOptional<z.ZodObject<{
        enabled: z.ZodDefault<z.ZodBoolean>;
        model: z.ZodOptional<z.ZodUnion<readonly [z.ZodString, z.ZodArray<z.ZodUnion<readonly [z.ZodString, z.ZodObject<{
            id: z.ZodString;
            variant: z.ZodOptional<z.ZodString>;
        }, z.core.$strip>]>>]>>;
    }, z.core.$strict>>;
    acpAgents: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodObject<{
        command: z.ZodString;
        args: z.ZodDefault<z.ZodArray<z.ZodString>>;
        env: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodString>>;
        cwd: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodString>;
        prompt: z.ZodOptional<z.ZodString>;
        orchestratorPrompt: z.ZodOptional<z.ZodString>;
        wrapperModel: z.ZodOptional<z.ZodString>;
        timeoutMs: z.ZodDefault<z.ZodNumber>;
        permissionMode: z.ZodDefault<z.ZodEnum<{
            allow: "allow";
            ask: "ask";
            reject: "reject";
        }>>;
    }, z.core.$strict>>>;
}, z.core.$strip>;
export type PluginConfig = z.infer<typeof PluginConfigSchema>;
export type { AgentName } from './constants';
