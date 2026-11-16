import { createRequire } from "node:module";
var __create = Object.create;
var __getProtoOf = Object.getPrototypeOf;
var __defProp = Object.defineProperty;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
function __accessProp(key) {
  return this[key];
}
var __toESMCache_node;
var __toESMCache_esm;
var __toESM = (mod, isNodeMode, target) => {
  var canCache = mod != null && typeof mod === "object";
  if (canCache) {
    var cache = isNodeMode ? __toESMCache_node ??= new WeakMap : __toESMCache_esm ??= new WeakMap;
    var cached = cache.get(mod);
    if (cached)
      return cached;
  }
  target = mod != null ? __create(__getProtoOf(mod)) : {};
  const to = isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target;
  for (let key of __getOwnPropNames(mod))
    if (!__hasOwnProp.call(to, key))
      __defProp(to, key, {
        get: __accessProp.bind(mod, key),
        enumerable: true
      });
  if (canCache)
    cache.set(mod, to);
  return to;
};
var __commonJS = (cb, mod) => () => (mod || cb((mod = { exports: {} }).exports, mod), mod.exports);
var __returnValue = (v) => v;
function __exportSetter(name, newValue) {
  this[name] = __returnValue.bind(null, newValue);
}
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, {
      get: all[name],
      enumerable: true,
      configurable: true,
      set: __exportSetter.bind(all, name)
    });
};
var __esm = (fn, res) => () => (fn && (res = fn(fn = 0)), res);
var __require = /* @__PURE__ */ createRequire(import.meta.url);

// src/utils/compat.ts
import { spawn as nodeSpawn } from "node:child_process";
import { existsSync, readdirSync, statSync } from "node:fs";
import { writeFile as fsWriteFile } from "node:fs/promises";
import * as path from "node:path";
function collectStream(stream) {
  if (!stream)
    return () => Promise.resolve("");
  const chunks = [];
  stream.on("data", (chunk) => chunks.push(chunk));
  return () => new Promise((resolve, reject) => {
    if (!stream.readable) {
      resolve(Buffer.concat(chunks).toString("utf-8"));
      return;
    }
    stream.on("end", () => resolve(Buffer.concat(chunks).toString("utf-8")));
    stream.on("error", reject);
  });
}
function isRegularFile(candidate) {
  try {
    return existsSync(candidate) && statSync(candidate).isFile();
  } catch {
    return false;
  }
}
function splitList(value, separator) {
  return value.split(separator).map((entry) => entry.trim()).filter((entry) => entry.length > 0);
}
function splitWindowsPath(pathEnv) {
  const parts = [];
  let current = "";
  let inQuotes = false;
  for (const char of pathEnv) {
    if (char === '"') {
      inQuotes = !inQuotes;
      continue;
    }
    if (char === path.delimiter && !inQuotes) {
      parts.push(current);
      current = "";
      continue;
    }
    current += char;
  }
  parts.push(current);
  return parts.map((part) => part === "" ? "." : part);
}
function resolveWindowsCommand(command, pathEnv = process.env.PATH ?? "", pathExtEnv = process.env.PATHEXT ?? WINDOWS_PATH_EXT_DEFAULT) {
  const extensions = splitList(pathExtEnv, ";").map((ext) => ext.startsWith(".") ? ext : `.${ext}`);
  const extensionsLower = new Set(extensions.map((ext) => ext.toLowerCase()));
  const commandExt = path.extname(command);
  const candidates = commandExt && extensionsLower.has(commandExt.toLowerCase()) ? [command] : extensions.map((ext) => `${command}${ext}`);
  const candidatesLower = candidates.map((candidate) => candidate.toLowerCase());
  for (const dir of splitWindowsPath(pathEnv)) {
    let entries;
    try {
      entries = readdirSync(dir);
    } catch {
      continue;
    }
    const byLowerName = new Map(entries.map((entry) => [entry.toLowerCase(), entry]));
    for (const candidateLower of candidatesLower) {
      const actualName = byLowerName.get(candidateLower);
      if (actualName === undefined)
        continue;
      const candidatePath = path.join(dir, actualName);
      if (!isRegularFile(candidatePath))
        continue;
      const resolvedExt = path.extname(actualName).toLowerCase();
      return {
        file: candidatePath,
        viaCmdShell: !DIRECT_EXECUTION_EXTENSIONS.has(resolvedExt)
      };
    }
  }
  return;
}
function isCmdUnsafeArgument(arg) {
  if (arg.includes("%") || arg.includes('"'))
    return true;
  for (let i = 0;i < arg.length; i++) {
    if (arg.charCodeAt(i) <= 31)
      return true;
  }
  return false;
}
function escapeWindowsArgument(arg) {
  if (isCmdUnsafeArgument(arg)) {
    throw new Error(`cannot pass ${JSON.stringify(arg)} through a .cmd shim: cmd.exe reinterprets '%', '"', and control characters even inside quotes`);
  }
  if (!CMD_METACHARACTERS.test(arg)) {
    return arg;
  }
  const escaped = arg.replace(/(\\*)$/, "$1$1");
  return `"${escaped}"`;
}
function buildWindowsCommandLine(file, args) {
  return `"${[file, ...args].map(escapeWindowsArgument).join(" ")}"`;
}
function crossSpawn(command, options) {
  const [cmd, ...args] = command;
  let file = cmd;
  const fileArgs = args;
  let viaCmdShell = false;
  if (process.platform === "win32" && !cmd.includes("/") && !cmd.includes("\\")) {
    const resolved = resolveWindowsCommand(cmd);
    if (resolved) {
      file = resolved.file;
      viaCmdShell = resolved.viaCmdShell;
    }
  }
  const spawnOptions = {
    stdio: [
      options?.stdin ?? "ignore",
      options?.stdout ?? "pipe",
      options?.stderr ?? "pipe"
    ],
    cwd: options?.cwd,
    env: options?.env
  };
  const proc = viaCmdShell ? nodeSpawn(process.env.ComSpec ?? "cmd.exe", ["/d", "/s", "/c", buildWindowsCommandLine(file, fileArgs)], { ...spawnOptions, windowsVerbatimArguments: true }) : nodeSpawn(file, fileArgs, spawnOptions);
  const stdoutCollector = collectStream(proc.stdout);
  const stderrCollector = collectStream(proc.stderr);
  const exited = new Promise((resolve, reject) => {
    proc.on("error", reject);
    proc.on("close", (code) => resolve(code ?? 1));
  });
  return {
    proc,
    stdout: stdoutCollector,
    stderr: stderrCollector,
    exited,
    kill: (signal) => proc.kill(signal),
    get exitCode() {
      return proc.exitCode;
    }
  };
}
async function crossWrite(path2, data) {
  if (typeof data === "string") {
    await fsWriteFile(path2, Buffer.from(data));
    return;
  }
  if (Buffer.isBuffer(data)) {
    await fsWriteFile(path2, data);
    return;
  }
  await fsWriteFile(path2, Buffer.from(data));
}
var WINDOWS_PATH_EXT_DEFAULT = ".COM;.EXE;.BAT;.CMD", DIRECT_EXECUTION_EXTENSIONS, CMD_METACHARACTERS;
var init_compat = __esm(() => {
  DIRECT_EXECUTION_EXTENSIONS = new Set([".exe", ".com"]);
  CMD_METACHARACTERS = /[\s&|<>()^!]/;
});

// src/tui.ts
import { parseColor, RGBA } from "@opentui/core";
import { createElement as createElement2, insert as insert2, setProp } from "@opentui/solid";
import { createSignal } from "solid-js";

// src/config/constants.ts
var AGENT_ALIASES = {
  explore: "explorer",
  "frontend-ui-ux-engineer": "designer"
};
var SUBAGENT_NAMES = [
  "explorer",
  "librarian",
  "oracle",
  "designer",
  "fixer",
  "observer",
  "council",
  "councillor"
];
var ALL_AGENT_NAMES = ["orchestrator", ...SUBAGENT_NAMES];
var AGENT_THEME_COLORS = [
  "primary",
  "secondary",
  "accent",
  "success",
  "warning",
  "error",
  "info"
];
var PROTECTED_AGENTS = new Set(["orchestrator", "councillor"]);
var DEFAULT_MODELS = {
  orchestrator: undefined,
  oracle: undefined,
  librarian: undefined,
  explorer: undefined,
  designer: undefined,
  fixer: undefined,
  observer: undefined,
  council: undefined,
  councillor: undefined
};
var POLL_INTERVAL_BACKGROUND_MS = 2000;
var MAX_POLL_TIME_MS = 5 * 60 * 1000;
var PHASE_REMINDER_TEXT = `!IMPORTANT! Scheduler workflow: First choose the lightest workflow that fits the work. If direct execution is justified, complete it and verify proportionately. Otherwise: plan lanes/dependencies → dispatch background specialists → track task IDs → wait for hook-driven completion → reconcile terminal results → verify. !END!`;
function formatSystemReminder(text) {
  return `<system-reminder>
${text}
</system-reminder>`;
}
var PHASE_REMINDER = formatSystemReminder(PHASE_REMINDER_TEXT);
var WRITABLE_FILE_OPERATIONS_RULES = `**File Operations Rules**:
- Prefer dedicated file tools for normal code work: glob/grep/ast_grep_search for discovery, read for file contents, and edit/write/apply_patch for targeted source changes.
- Use bash for execution and automation: git, package managers, tests, builds, scripts, diagnostics, and shell-native filesystem operations.
- Shell is acceptable for bulk or mechanical filesystem changes when it is clearer or safer than many individual edits (for example: truncate generated logs, remove build artifacts, batch rename/move files), especially when the user explicitly asks for that shell operation.
- Before destructive or broad shell operations, verify the target set and quote paths. Prefer a dry-run/listing first when practical.
- Do not use cat/head/tail/sed/awk only to read code into context; use read/grep unless a shell pipeline is genuinely the better diagnostic.`;
var READONLY_FILE_OPERATIONS_RULES = `**File Operations Rules**:
- READ-ONLY: inspect and report; do not modify files.
- Prefer dedicated file tools for codebase inspection: glob/grep/ast_grep_search for discovery and read for file contents.
- Bash is allowed for non-mutating diagnostics and shell-native inspection when it is the clearest tool, but not for modifying files.
- Do not use cat/head/tail/sed/awk only to read code into context; use read/grep unless a shell pipeline is genuinely the better diagnostic.`;
var NO_SHELL_READONLY_FILE_OPERATIONS_RULES = `**File Operations Rules**:
- READ-ONLY: inspect and report; do not modify files.
- Use glob/grep/ast_grep_search for discovery and read for file contents.
- Do not use bash or shell commands.`;
var TOAST_DURATION_MS = 1e4;
var DEFAULT_DISABLED_AGENTS = ["observer"];
var DEFAULT_MAX_SESSIONS_PER_AGENT = 2;
var DEFAULT_MAX_CONTEXT_LINES = 50000;
var DEFAULT_READ_CONTEXT_MIN_LINES = 10;
var DEFAULT_READ_CONTEXT_MAX_FILES = 8;
var DEFAULT_MAX_RETAINED_SNAPSHOTS = 20;
var DEFAULT_MAX_SESSION_METADATA_ENTRIES = 1000;
function resolveImageRouting(imageRouting, observerEnabled) {
  if (imageRouting !== undefined)
    return imageRouting;
  return observerEnabled ? "auto" : "direct";
}

// src/config/loader.ts
import * as fs from "node:fs";
import * as path2 from "node:path";

// src/plugin-entry.ts
var INSTALLER_MANAGED_PLUGIN_OPTION = "__ohMyOpencodeSlimManagedByInstaller";

// src/cli/config-io.ts
init_compat();

// src/cli/paths.ts
import { homedir } from "node:os";
import { dirname, join as join2 } from "node:path";
function getDefaultOpenCodeConfigDir() {
  const userConfigDir = process.env.XDG_CONFIG_HOME ? process.env.XDG_CONFIG_HOME : join2(homedir(), ".config");
  return join2(userConfigDir, "opencode");
}
function getCustomOpenCodeConfigDir() {
  const configDir = process.env.OPENCODE_CONFIG_DIR?.trim();
  return configDir || undefined;
}
function getCustomTuiConfigPath() {
  const configPath = process.env.OPENCODE_TUI_CONFIG?.trim();
  return configPath || undefined;
}
function getConfigDir() {
  const customConfigDir = getCustomOpenCodeConfigDir();
  if (customConfigDir) {
    return customConfigDir;
  }
  return getDefaultOpenCodeConfigDir();
}
function getConfigSearchDirs() {
  const dirs = [getCustomOpenCodeConfigDir(), getDefaultOpenCodeConfigDir()];
  return dirs.filter((dir, index) => {
    return Boolean(dir) && dirs.indexOf(dir) === index;
  });
}
function getOpenCodeConfigPaths() {
  const configDir = getConfigDir();
  return [join2(configDir, "opencode.json"), join2(configDir, "opencode.jsonc")];
}
function getTuiConfig() {
  const customConfigPath = getCustomTuiConfigPath();
  if (customConfigPath)
    return customConfigPath;
  return join2(getConfigDir(), "tui.json");
}
function getTuiConfigJsonc() {
  return join2(getConfigDir(), "tui.jsonc");
}

// src/config/agent-mcps.ts
var DEFAULT_AGENT_MCPS = {
  orchestrator: ["*", "!context7"],
  designer: [],
  oracle: [],
  librarian: ["context7", "gh_grep"],
  explorer: [],
  fixer: [],
  observer: [],
  council: [],
  councillor: []
};
function parseList(items, allAvailable) {
  if (!items || items.length === 0) {
    return [];
  }
  const allow = items.filter((i) => !i.startsWith("!"));
  const deny = items.filter((i) => i.startsWith("!")).map((i) => i.slice(1));
  if (deny.includes("*")) {
    return [];
  }
  if (allow.includes("*")) {
    return allAvailable.filter((item) => !deny.includes(item));
  }
  return allow.filter((item) => !deny.includes(item) && allAvailable.includes(item));
}
function getAgentMcpList(agentName, runtime) {
  const agents = runtime.agents();
  const agentConfig = agents[agentName] ?? agents[Object.keys(AGENT_ALIASES).find((key) => AGENT_ALIASES[key] === agentName) ?? ""];
  if (agentConfig?.mcps !== undefined) {
    return agentConfig.mcps;
  }
  const defaultMcps = DEFAULT_AGENT_MCPS[agentName];
  return defaultMcps ?? [];
}

// src/cli/custom-skills-registry.ts
var CUSTOM_SKILLS = [
  {
    name: "simplify",
    description: "Code simplification and readability-focused refactoring",
    allowedAgents: ["oracle"],
    sourcePath: "src/skills/simplify"
  },
  {
    name: "codemap",
    description: "Repository understanding and hierarchical codemap generation",
    allowedAgents: ["orchestrator"],
    sourcePath: "src/skills/codemap"
  },
  {
    name: "clonedeps",
    description: "Clone important dependency source for local inspection",
    allowedAgents: ["orchestrator"],
    sourcePath: "src/skills/clonedeps"
  },
  {
    name: "deepwork",
    description: "Heavy/complex coding sessions and large modifications workflow",
    allowedAgents: ["orchestrator"],
    sourcePath: "src/skills/deepwork"
  },
  {
    name: "verification-planning",
    description: "Plan credible, proportionate evidence before non-trivial implementation",
    allowedAgents: ["orchestrator"],
    sourcePath: "src/skills/verification-planning"
  },
  {
    name: "reflect",
    description: "Review repeated work and suggest reusable workflow improvements",
    allowedAgents: ["orchestrator"],
    sourcePath: "src/skills/reflect"
  },
  {
    name: "oh-my-opencode-slim",
    description: "Configure, customize, and safely improve oh-my-opencode-slim setups",
    allowedAgents: ["orchestrator"],
    sourcePath: "src/skills/oh-my-opencode-slim"
  },
  {
    name: "worktrees",
    description: "Manage Git worktrees as OMO safe isolated coding lanes for complex/risky/parallel work",
    allowedAgents: ["orchestrator"],
    sourcePath: "src/skills/worktrees"
  }
];

// src/cli/config-io.ts
function stripJsonComments(json) {
  const commentPattern = /\\"|"(?:\\"|[^"])*"|(\/\/.*|\/\*[\s\S]*?\*\/)/g;
  const trailingCommaPattern = /\\"|"(?:\\"|[^"])*"|(,)(\s*[}\]])/g;
  return json.replace(commentPattern, (match, commentGroup) => commentGroup ? "" : match).replace(trailingCommaPattern, (match, comma, closing) => comma ? closing : match);
}

// src/config/schema.ts
import { z as z2 } from "zod";

// src/config/council-schema.ts
import { z } from "zod";

// src/utils/councillor-models.ts
function normalizeCouncillorModels(model, fallbackVariant) {
  const raw = Array.isArray(model) ? model : [model];
  return raw.map((entry) => typeof entry === "string" ? { id: entry, variant: fallbackVariant } : { id: entry.id, variant: entry.variant ?? fallbackVariant });
}

// src/config/council-schema.ts
var ModelIdSchema = z.string().regex(/^[^/\s]+\/[^\s]+$/, 'Expected provider/model format (e.g. "openai/gpt-5.6-luna")');
var CouncillorModelEntrySchema = z.object({
  id: ModelIdSchema,
  variant: z.string().optional()
});
var CouncillorModelSchema = z.union([
  ModelIdSchema,
  z.array(z.union([ModelIdSchema, CouncillorModelEntrySchema])).min(1)
]).describe('Model ID in provider/model format (e.g. "openai/gpt-5.6-luna"), or an ' + "ordered fallback chain (array of model IDs or { id, variant } entries) " + "tried in order until one responds.");
var CouncillorConfigSchema = z.object({
  model: CouncillorModelSchema,
  variant: z.string().optional(),
  prompt: z.string().optional().describe("Optional role/guidance injected into the councillor user prompt")
}).transform((c) => {
  const models = normalizeCouncillorModels(c.model, c.variant);
  return {
    model: models[0].id,
    variant: c.variant,
    prompt: c.prompt,
    models
  };
});
var CouncilPresetSchema = z.record(z.string(), z.record(z.string(), z.unknown())).transform((entries, ctx) => {
  const councillors = {};
  for (const [key, raw] of Object.entries(entries)) {
    if (key === "master")
      continue;
    if (key === "councillors" && typeof raw === "object" && raw !== null) {
      for (const [innerKey, innerRaw] of Object.entries(raw)) {
        const innerParsed = CouncillorConfigSchema.safeParse(innerRaw);
        if (!innerParsed.success) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: `Invalid councillor "${innerKey}" (nested under legacy "councillors" key): ${innerParsed.error.issues.map((i) => i.message).join(", ")}`
          });
          return z.NEVER;
        }
        councillors[innerKey] = innerParsed.data;
      }
      continue;
    }
    const parsed = CouncillorConfigSchema.safeParse(raw);
    if (!parsed.success) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `Invalid councillor "${key}": ${parsed.error.issues.map((i) => i.message).join(", ")}`
      });
      return z.NEVER;
    }
    councillors[key] = parsed.data;
  }
  return councillors;
});
var CouncilConfigSchema = z.object({
  presets: z.record(z.string(), CouncilPresetSchema),
  default_preset: z.string().default("default")
}).passthrough().transform((data) => {
  const deprecated = [];
  if ("master" in data)
    deprecated.push("master");
  return {
    presets: data.presets,
    default_preset: data.default_preset,
    _deprecated: deprecated.length > 0 ? deprecated : undefined
  };
});

// src/config/schema.ts
var ProviderModelIdSchema = z2.string().regex(/^[^/\s]+\/[^\s]+$/, "Expected provider/model format (provider/.../model)");
var PermissionActionSchema = z2.enum(["ask", "allow", "deny"]);
var PermissionRuleSchema = z2.union([
  PermissionActionSchema,
  z2.record(z2.string(), PermissionActionSchema)
]);
var PermissionObjectSchema = z2.object({
  read: PermissionRuleSchema.optional(),
  edit: PermissionRuleSchema.optional(),
  glob: PermissionRuleSchema.optional(),
  grep: PermissionRuleSchema.optional(),
  list: PermissionRuleSchema.optional(),
  bash: PermissionRuleSchema.optional(),
  task: PermissionRuleSchema.optional(),
  external_directory: PermissionRuleSchema.optional(),
  lsp: PermissionRuleSchema.optional(),
  skill: PermissionRuleSchema.optional(),
  todowrite: PermissionActionSchema.optional(),
  question: PermissionActionSchema.optional(),
  webfetch: PermissionActionSchema.optional(),
  websearch: PermissionActionSchema.optional(),
  codesearch: PermissionActionSchema.optional(),
  doom_loop: PermissionActionSchema.optional()
}).catchall(PermissionRuleSchema);
var PermissionConfigSchema = z2.union([
  PermissionActionSchema,
  PermissionObjectSchema
]);
var AgentColorSchema = z2.union([
  z2.string().regex(/^#[0-9a-fA-F]{6}$/, "Expected a six-digit hex color (#RRGGBB)"),
  z2.enum(AGENT_THEME_COLORS)
]);
var ModelInheritanceSourceSchema = z2.enum(["session", "orchestrator"]);
var AgentOverrideConfigSchema = z2.object({
  model: z2.union([
    z2.string(),
    z2.array(z2.union([
      z2.string(),
      z2.object({
        id: z2.string(),
        variant: z2.string().optional()
      })
    ])).min(1)
  ]).optional(),
  inheritModelFrom: ModelInheritanceSourceSchema.optional(),
  temperature: z2.number().min(0).max(2).optional(),
  variant: z2.string().optional().catch(undefined),
  skills: z2.array(z2.string()).optional(),
  mcps: z2.array(z2.string()).optional(),
  prompt: z2.string().min(1).optional(),
  orchestratorPrompt: z2.string().min(1).optional(),
  options: z2.record(z2.string(), z2.unknown()).optional(),
  displayName: z2.string().min(1).optional(),
  color: AgentColorSchema.optional().describe("Agent display color as #RRGGBB or an OpenCode theme color"),
  description: z2.string().min(1).optional(),
  permission: PermissionConfigSchema.optional()
}).strict();
var MultiplexerTypeSchema = z2.enum([
  "auto",
  "tmux",
  "zellij",
  "herdr",
  "kitty",
  "cmux",
  "none"
]);
var MultiplexerLayoutSchema = z2.enum([
  "main-horizontal",
  "main-vertical",
  "tiled",
  "even-horizontal",
  "even-vertical"
]);
var ZellijPaneModeSchema = z2.enum(["agent-tab", "current-tab"]);
var MultiplexerConfigSchema = z2.object({
  type: MultiplexerTypeSchema.default("none"),
  layout: MultiplexerLayoutSchema.default("main-vertical"),
  main_pane_size: z2.number().min(20).max(80).default(60),
  zellij_pane_mode: ZellijPaneModeSchema.default("agent-tab")
});
var PresetSchema = z2.record(z2.string(), AgentOverrideConfigSchema);
var McpNameSchema = z2.enum(["context7", "gh_grep"]);
var InterviewOutputFolderSchema = z2.string().trim().min(1).regex(/^(?![\\/])(?![A-Za-z]:[\\/])(?!.*(?:^|[\\/])\.\.(?:[\\/]|$)).+$/, "outputFolder must be a relative path without parent-directory traversal");
var InterviewConfigSchema = z2.object({
  maxQuestions: z2.number().int().min(1).max(10).default(2),
  outputFolder: InterviewOutputFolderSchema.default("interview"),
  autoOpenBrowser: z2.boolean().default(true).describe("Automatically open the interview UI in your default browser during interactive runs. Disabled automatically in tests and CI."),
  port: z2.number().int().min(0).max(65535).default(0),
  dashboard: z2.boolean().default(false)
});
var ConcurrencyLimitSchema = z2.number().int().min(0).max(1000);
var BackgroundTaskConcurrencyConfigSchema = z2.object({
  defaultConcurrency: z2.number().int().min(0).max(1000).default(0).describe("Maximum concurrently running native background tasks. 0 disables the default cap."),
  providerConcurrency: z2.record(z2.string().min(1), ConcurrencyLimitSchema).default({}).describe("Per-provider concurrency caps keyed by provider ID. The most specific configured cap wins: model > provider > default. 0 means unlimited for that provider."),
  modelConcurrency: z2.record(z2.string().min(1), ConcurrencyLimitSchema).default({}).describe("Per-model concurrency caps keyed by provider/model ID. The most specific configured cap wins: model > provider > default. 0 means unlimited for that model.")
}).strict().default({
  defaultConcurrency: 0,
  providerConcurrency: {},
  modelConcurrency: {}
});
var BackgroundJobsConfigSchema = z2.object({
  strategy: z2.enum(["latest", "checkpoint-compatible"]).default("latest").describe('Board injection strategy. "latest" replaces prior board messages; "checkpoint-compatible" preserves them and appends only changed board snapshots.'),
  maxSessionsPerAgent: z2.number().int().min(1).max(10).default(2),
  maxContextLines: z2.number().int().min(0).max(500000).default(50000),
  readContextMinLines: z2.number().int().min(0).max(1000).default(10),
  readContextMaxFiles: z2.number().int().min(0).max(50).default(8),
  maxRetainedSnapshots: z2.number().int().min(1).max(100).default(DEFAULT_MAX_RETAINED_SNAPSHOTS).describe("Maximum board snapshots retained per checkpoint cache epoch (1–100). Exceeding the limit starts a new epoch with the current snapshot and intentionally creates one cache miss."),
  orchestratorWake: z2.object({
    enabled: z2.boolean().default(true).describe("When true, idle orchestrator sessions with incomplete todos may receive periodic internal wake prompts. Default enabled."),
    intervalMs: z2.number().int().min(60000).max(2147483647).default(300000).describe("Continuous parent-idle interval between orchestrator wake evaluations (60,000–2,147,483,647ms). Default 300,000 (5 minutes). 0 is invalid.")
  }).default({ enabled: true, intervalMs: 300000 }).describe("Periodic orchestrator wake scheduler for idle sessions with incomplete todos. Default enabled at a 5-minute interval. Requires host session APIs (session.get, todo, children, status, promptAsync); inactive on the v2 shim."),
  wallClockTimeoutMs: z2.union([z2.literal(0), z2.number().int().min(60000).max(2147483647)]).default(0).describe("Explicit opt-in wall-clock deadline for native task(..., background: true) child sessions. 0 disables supervision; finite values are 60,000–2,147,483,647ms."),
  abortGraceMs: z2.number().int().min(1000).max(60000).default(1e4).describe("Grace period after a wall-clock deadline while OpenCode confirms the child terminal state (1,000–60,000ms)."),
  concurrency: BackgroundTaskConcurrencyConfigSchema,
  waitForUserGuard: z2.boolean().default(true).describe("When true, intercept wait_for_user calls made while background tasks are still running and the orchestrator wake scheduler is enabled, returning guidance to end the turn instead of blocking on manual input. Default enabled.")
});
var LEGACY_FALLBACK_KEYS = [
  "timeoutMs",
  "retryDelayMs",
  "retry_on_empty",
  "runtimeOverride"
];
function stripLegacyFallbackKeys(value) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return value;
  }
  const record = value;
  const hasLegacy = LEGACY_FALLBACK_KEYS.some((key) => (key in record));
  if (!hasLegacy) {
    return value;
  }
  const cleaned = {};
  for (const [key, val] of Object.entries(record)) {
    if (!LEGACY_FALLBACK_KEYS.includes(key)) {
      cleaned[key] = val;
    }
  }
  return cleaned;
}
var FailoverConfigSchema = z2.preprocess(stripLegacyFallbackKeys, z2.object({
  enabled: z2.boolean().default(true),
  maxRetries: z2.number().int().min(0).default(3).describe("Number of consecutive 429/rate-limit responses tolerated on the " + "same model before aborting (or swapping to the next fallback " + "model when a chain is configured).")
}).strict());
var CompanionConfigSchema = z2.object({
  enabled: z2.boolean().optional(),
  binaryPath: z2.string().min(1).optional().describe("Path to a custom companion binary to launch."),
  position: z2.enum(["bottom-right", "bottom-left", "top-right", "top-left"]).optional(),
  size: z2.enum(["small", "medium", "large"]).optional(),
  gifPack: z2.enum(["default"]).optional().describe("Bundled companion animation pack to use."),
  loopStyle: z2.enum(["classic", "smooth"]).optional().describe("Companion animation playback style: classic loops or smooth ping-pong playback."),
  speed: z2.number().min(0.25).max(4).optional().describe("Companion animation playback speed multiplier. Defaults to 1."),
  debug: z2.boolean().optional().describe("Enable verbose native companion debug logs.")
});
var WebfetchConfigSchema = z2.object({
  enabled: z2.boolean().default(true).describe("When false, skip registering this enhanced webfetch so OpenCode uses its built-in version."),
  model: AgentOverrideConfigSchema.shape.model.describe("Dedicated model(s) for smartfetch secondary-model summarization. " + "Same shape as agent model config (string, array of strings/objects with id+variant). " + "Takes priority over small_model, agents.explorer.model, and agents.librarian.model.")
}).strict();
var AcpAgentPermissionModeSchema = z2.enum(["ask", "allow", "reject"]);
var MAX_ACP_TIMEOUT_MS = 2147483647;
var AcpAgentConfigSchema = z2.object({
  command: z2.string().min(1),
  args: z2.array(z2.string()).default([]),
  env: z2.record(z2.string(), z2.string()).default({}),
  cwd: z2.string().min(1).optional(),
  description: z2.string().min(1).optional(),
  prompt: z2.string().min(1).optional(),
  orchestratorPrompt: z2.string().min(1).optional(),
  wrapperModel: ProviderModelIdSchema.optional(),
  timeoutMs: z2.number().int().min(0).max(MAX_ACP_TIMEOUT_MS).default(0).describe("Timeout for a single ACP run in milliseconds. Set to 0 to disable the timeout."),
  permissionMode: AcpAgentPermissionModeSchema.default("ask")
}).strict();
var AcpAgentsConfigSchema = z2.record(z2.string(), AcpAgentConfigSchema);
function rejectOrchestratorPromptOnOrchestrator(overrides, ctx, pathPrefix) {
  for (const [name, override] of Object.entries(overrides)) {
    if (name === "orchestrator" && override.orchestratorPrompt !== undefined) {
      ctx.addIssue({
        code: z2.ZodIssueCode.custom,
        path: [...pathPrefix, name, "orchestratorPrompt"],
        message: "orchestratorPrompt is not supported for the orchestrator agent"
      });
    }
  }
}
var PluginConfigSchema = z2.object({
  preset: z2.string().optional(),
  setDefaultAgent: z2.boolean().optional(),
  compactSidebar: z2.boolean().optional().describe("Use the compact TUI sidebar layout. Defaults to true; set false to use the expanded layout."),
  stripOrchestratorModel: z2.boolean().optional().describe("When true, omit orchestrator.model and orchestrator.variant from the SDK config so OpenCode uses the session model selected with /model after subagent dispatch. An explicitly selected preset that sets orchestrator.model is preserved. Defaults to false."),
  autoUpdate: z2.boolean().optional().describe("Disable automatic installation of plugin updates when false. Defaults to true."),
  presets: z2.record(z2.string(), PresetSchema).optional(),
  agents: z2.record(z2.string(), AgentOverrideConfigSchema).optional(),
  disabled_agents: z2.array(z2.string()).optional().describe("Agent names to disable completely. " + "Disabled agents are not instantiated and cannot be delegated to. " + "Orchestrator and council internal agents (councillor) cannot be disabled. " + "By default, 'observer' is disabled. Remove it from this list and configure a vision-capable model to enable."),
  image_routing: z2.enum(["auto", "direct"]).optional().describe("How image attachments are handled. " + "When omitted, preserves legacy conditional behavior: intercept " + 'attachments only when observer is enabled. "auto": requires ' + "observer to be enabled and saves attachments to disk before " + 'nudging delegation to @observer. "direct": always passes ' + "attachments to the orchestrator untouched."),
  disabled_mcps: z2.array(z2.string()).optional().describe("MCP server names to disable completely. Disabled servers are not " + "started and cannot be used by agents."),
  disabled_tools: z2.array(z2.string()).optional().describe("Tool names to disable completely. Disabled tools are not registered with OpenCode and cannot be used by agents."),
  disabled_skills: z2.array(z2.string()).optional().describe("Skill names to disable completely. Disabled skills are not granted to agents, even when referenced by presets or agent overrides."),
  multiplexer: MultiplexerConfigSchema.optional(),
  interview: InterviewConfigSchema.optional(),
  backgroundJobs: BackgroundJobsConfigSchema.optional(),
  fallback: FailoverConfigSchema.optional(),
  council: CouncilConfigSchema.optional(),
  companion: CompanionConfigSchema.optional(),
  webfetch: WebfetchConfigSchema.optional(),
  acpAgents: AcpAgentsConfigSchema.optional()
}).superRefine((value, ctx) => {
  if (value.agents) {
    rejectOrchestratorPromptOnOrchestrator(value.agents, ctx, ["agents"]);
  }
  if (value.presets) {
    for (const [presetName, preset] of Object.entries(value.presets)) {
      rejectOrchestratorPromptOnOrchestrator(preset, ctx, [
        "presets",
        presetName
      ]);
    }
  }
});

// src/config/loader.ts
var PROMPTS_DIR_NAME = "oh-my-opencode-slim";
var INTERVIEW_CONFIG_KEYS = [
  "maxQuestions",
  "outputFolder",
  "autoOpenBrowser",
  "port",
  "dashboard"
];
var LEGACY_BACKGROUND_JOBS_KEYS = ["continueOnIdle"];
var DISABLED_CONFIG_KEYS = [
  "disabled_agents",
  "disabled_tools",
  "disabled_mcps",
  "disabled_skills"
];
function normalizeDisabledArrayKeys(rawConfig, warn) {
  if (typeof rawConfig !== "object" || rawConfig === null || Array.isArray(rawConfig)) {
    return;
  }
  const configRecord = rawConfig;
  for (const key of DISABLED_CONFIG_KEYS) {
    const value = configRecord[key];
    if (value === undefined || Array.isArray(value)) {
      continue;
    }
    if (typeof value === "string") {
      configRecord[key] = [value];
      warn?.(`Config key "${key}" should be an array; ` + `normalized to ["${value}"].`);
    } else {
      delete configRecord[key];
      warn?.(`Config key "${key}" must be an array; ignoring invalid value.`);
    }
  }
}
function migrateLegacyBackgroundJobsConfig(rawConfig) {
  if (typeof rawConfig !== "object" || rawConfig === null || Array.isArray(rawConfig)) {
    return rawConfig;
  }
  const configRecord = rawConfig;
  const backgroundJobs = configRecord.backgroundJobs;
  if (typeof backgroundJobs !== "object" || backgroundJobs === null || Array.isArray(backgroundJobs) || !Object.hasOwn(backgroundJobs, "continueOnIdle")) {
    return rawConfig;
  }
  const migratedBackgroundJobs = {
    ...backgroundJobs
  };
  const legacyContinueOnIdle = migratedBackgroundJobs.continueOnIdle;
  delete migratedBackgroundJobs.continueOnIdle;
  const wake = migratedBackgroundJobs.orchestratorWake;
  if (typeof legacyContinueOnIdle === "boolean" && (wake === undefined || typeof wake === "object" && wake !== null && !Array.isArray(wake))) {
    const wakeConfig = wake ?? {};
    if (!Object.hasOwn(wakeConfig, "enabled")) {
      migratedBackgroundJobs.orchestratorWake = {
        ...wakeConfig,
        enabled: legacyContinueOnIdle
      };
    }
  }
  return { ...configRecord, backgroundJobs: migratedBackgroundJobs };
}
function retainExplicitInterviewFields(parsedConfig, rawConfig) {
  if (!parsedConfig.interview) {
    return parsedConfig;
  }
  const rawInterview = typeof rawConfig === "object" && rawConfig !== null && !Array.isArray(rawConfig) && typeof rawConfig.interview === "object" && rawConfig.interview !== null && !Array.isArray(rawConfig.interview) ? rawConfig.interview : undefined;
  if (!rawInterview) {
    return { ...parsedConfig, interview: undefined };
  }
  const interview = {};
  for (const key of INTERVIEW_CONFIG_KEYS) {
    if (Object.hasOwn(rawInterview, key)) {
      interview[key] = parsedConfig.interview[key];
    }
  }
  return {
    ...parsedConfig,
    interview
  };
}
function retainExplicitBackgroundJobsFields(parsedConfig, rawConfig) {
  if (!parsedConfig.backgroundJobs) {
    return parsedConfig;
  }
  const rawBackgroundJobs = typeof rawConfig === "object" && rawConfig !== null && !Array.isArray(rawConfig) && typeof rawConfig.backgroundJobs === "object" && rawConfig.backgroundJobs !== null && !Array.isArray(rawConfig.backgroundJobs) ? rawConfig.backgroundJobs : undefined;
  if (!rawBackgroundJobs) {
    return parsedConfig;
  }
  const backgroundJobs = {};
  const parsedBackgroundJobs = parsedConfig.backgroundJobs;
  for (const key of Object.keys(rawBackgroundJobs)) {
    if (key !== "orchestratorWake" && Object.hasOwn(parsedBackgroundJobs, key)) {
      backgroundJobs[key] = parsedBackgroundJobs[key];
    }
  }
  const rawWake = typeof rawBackgroundJobs.orchestratorWake === "object" && rawBackgroundJobs.orchestratorWake !== null && !Array.isArray(rawBackgroundJobs.orchestratorWake) ? rawBackgroundJobs.orchestratorWake : undefined;
  const orchestratorWake = {};
  const parsedWake = parsedConfig.backgroundJobs.orchestratorWake;
  for (const key of Object.keys(rawWake ?? {})) {
    if (Object.hasOwn(parsedWake, key)) {
      orchestratorWake[key] = parsedWake[key];
    }
  }
  if (Object.keys(orchestratorWake).length > 0) {
    backgroundJobs.orchestratorWake = orchestratorWake;
  }
  return {
    ...parsedConfig,
    backgroundJobs
  };
}
function loadConfigFromPath(configPath, options) {
  try {
    const content = fs.readFileSync(configPath, "utf-8").replace(/^\uFEFF/, "");
    let rawConfig;
    try {
      const stripped = stripJsonComments(content);
      const interpolated = stripped.replace(/\{env:([^}]+)\}/g, (_, varName) => process.env[varName] ?? "");
      rawConfig = JSON.parse(interpolated);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      options?.onWarning?.({
        path: configPath,
        kind: "invalid-json",
        message
      });
      if (!options?.silent) {
        console.warn(`[oh-my-opencode-slim] Invalid JSON in ${configPath}:`, message);
      }
      return null;
    }
    if (typeof rawConfig === "object" && rawConfig !== null && "tmux" in rawConfig) {
      const tmuxMsg = "Deprecated tmux config key found and ignored. Use multiplexer config instead.";
      options?.onWarning?.({
        path: configPath,
        kind: "deprecated-key",
        message: tmuxMsg
      });
      if (!options?.silent) {
        console.warn(`[oh-my-opencode-slim] ${tmuxMsg}`);
      }
    }
    if (typeof rawConfig === "object" && rawConfig !== null && typeof rawConfig.council === "object" && rawConfig.council !== null && "master" in rawConfig.council) {
      const masterMsg = "Deprecated council.master config key found and ignored. Configure council agents via presets instead.";
      options?.onWarning?.({
        path: configPath,
        kind: "deprecated-key",
        message: masterMsg
      });
      if (!options?.silent) {
        console.warn(`[oh-my-opencode-slim] ${masterMsg}`);
      }
    }
    if (typeof rawConfig === "object" && rawConfig !== null && typeof rawConfig.backgroundJobs === "object" && rawConfig.backgroundJobs !== null) {
      const backgroundJobs = rawConfig.backgroundJobs;
      const present = LEGACY_BACKGROUND_JOBS_KEYS.filter((key) => (key in backgroundJobs));
      if (present.length > 0) {
        const backgroundJobsMsg = "Deprecated backgroundJobs.continueOnIdle config key found. " + "Boolean values are migrated to backgroundJobs.orchestratorWake.enabled " + "unless that replacement is explicit in the same config file; other values are ignored. " + "Use backgroundJobs.orchestratorWake.enabled instead.";
        options?.onWarning?.({
          path: configPath,
          kind: "deprecated-key",
          message: backgroundJobsMsg
        });
        if (!options?.silent) {
          console.warn(`[oh-my-opencode-slim] ${backgroundJobsMsg}`);
        }
      }
    }
    rawConfig = migrateLegacyBackgroundJobsConfig(rawConfig);
    if (typeof rawConfig === "object" && rawConfig !== null && typeof rawConfig.fallback === "object" && rawConfig.fallback !== null) {
      const fallback = rawConfig.fallback;
      const present = LEGACY_FALLBACK_KEYS.filter((key) => (key in fallback));
      if (present.length > 0) {
        const fallbackMsg = `Deprecated fallback config key${present.length === 1 ? "" : "s"} ${present.join(", ")} found and ignored. These fields were removed in 2.3.x; fallback behavior is controlled by fallback.enabled and fallback.maxRetries.`;
        options?.onWarning?.({
          path: configPath,
          kind: "deprecated-key",
          message: fallbackMsg
        });
        if (!options?.silent) {
          console.warn(`[oh-my-opencode-slim] ${fallbackMsg}`);
        }
      }
    }
    normalizeDisabledArrayKeys(rawConfig, (message) => {
      options?.onWarning?.({
        path: configPath,
        kind: "normalized",
        message
      });
      if (!options?.silent) {
        console.warn(`[oh-my-opencode-slim] ${message}`);
      }
    });
    const result = PluginConfigSchema.safeParse(rawConfig);
    if (!result.success) {
      options?.onWarning?.({
        path: configPath,
        kind: "invalid-schema",
        message: "Config does not match schema",
        formatted: result.error.format()
      });
      if (!options?.silent) {
        console.warn(`[oh-my-opencode-slim] Invalid config at ${configPath}:`);
        console.warn(result.error.format());
      }
      return null;
    }
    let layerConfig = retainExplicitInterviewFields(result.data, rawConfig);
    layerConfig = retainExplicitBackgroundJobsFields(layerConfig, rawConfig);
    if (layerConfig.webfetch && typeof rawConfig === "object" && rawConfig !== null && "webfetch" in rawConfig && typeof rawConfig.webfetch === "object" && rawConfig.webfetch !== null && !Array.isArray(rawConfig.webfetch) && !Object.hasOwn(rawConfig.webfetch, "enabled")) {
      const { enabled: _enabled, ...webfetch } = layerConfig.webfetch;
      return {
        ...layerConfig,
        webfetch
      };
    }
    return layerConfig;
  } catch (error) {
    if (error instanceof Error && "code" in error && error.code !== "ENOENT") {
      options?.onWarning?.({
        path: configPath,
        kind: "read-error",
        message: error.message
      });
      if (!options?.silent) {
        console.warn(`[oh-my-opencode-slim] Error reading config from ${configPath}:`, error.message);
      }
    }
    return null;
  }
}
function findConfigPath(basePath) {
  const jsoncPath = `${basePath}.jsonc`;
  const jsonPath = `${basePath}.json`;
  if (fs.existsSync(jsoncPath)) {
    return jsoncPath;
  }
  if (fs.existsSync(jsonPath)) {
    return jsonPath;
  }
  return null;
}
function findConfigPathInDirs(configDirs, baseName) {
  for (const configDir of configDirs) {
    const configPath = findConfigPath(path2.join(configDir, baseName));
    if (configPath) {
      return configPath;
    }
  }
  return null;
}
function validateFinalImageRouting(config, configPath, options) {
  if (config.image_routing !== "auto")
    return true;
  const disabledAgents = Array.isArray(config.disabled_agents) ? config.disabled_agents : DEFAULT_DISABLED_AGENTS;
  if (!disabledAgents.includes("observer"))
    return true;
  const message = 'image_routing "auto" requires observer to be enabled. ' + 'Remove "observer" from disabled_agents.';
  options?.onWarning?.({
    path: configPath,
    kind: "invalid-schema",
    message
  });
  if (!options?.silent) {
    console.warn(`[oh-my-opencode-slim] Invalid config: ${message}`);
  }
  return false;
}
function findPluginConfigPaths(directory) {
  const userConfigPath = findConfigPathInDirs(getConfigSearchDirs(), "oh-my-opencode-slim");
  const projectConfigBasePath = path2.join(directory, ".opencode", "oh-my-opencode-slim");
  const projectConfigPath = findConfigPath(projectConfigBasePath);
  return { userConfigPath, projectConfigPath };
}
function mergePluginConfigs(base, override) {
  return {
    ...base,
    ...override,
    agents: deepMerge(base.agents, override.agents),
    presets: deepMerge(base.presets, override.presets),
    multiplexer: deepMerge(base.multiplexer, override.multiplexer),
    interview: deepMerge(base.interview, override.interview),
    backgroundJobs: deepMerge(base.backgroundJobs, override.backgroundJobs),
    fallback: deepMerge(base.fallback, override.fallback),
    council: deepMerge(base.council, override.council),
    webfetch: deepMerge(base.webfetch, override.webfetch),
    acpAgents: deepMerge(base.acpAgents, override.acpAgents),
    companion: deepMerge(base.companion, override.companion)
  };
}
function deepMerge(base, override) {
  if (!base)
    return override;
  if (!override)
    return base;
  const result = { ...base };
  for (const key of Object.keys(override)) {
    const baseVal = base[key];
    const overrideVal = override[key];
    if (typeof baseVal === "object" && baseVal !== null && typeof overrideVal === "object" && overrideVal !== null && !Array.isArray(baseVal) && !Array.isArray(overrideVal)) {
      result[key] = deepMerge(baseVal, overrideVal);
    } else {
      result[key] = overrideVal;
    }
  }
  return result;
}
function loadPluginConfig(directory, options) {
  const { userConfigPath, projectConfigPath } = findPluginConfigPaths(directory);
  let config = userConfigPath ? loadConfigFromPath(userConfigPath, options) ?? {} : {};
  const projectConfig = projectConfigPath ? loadConfigFromPath(projectConfigPath, options) : null;
  if (projectConfig) {
    config = mergePluginConfigs(config, projectConfig);
  }
  if (config.webfetch) {
    config.webfetch = WebfetchConfigSchema.parse(config.webfetch);
  }
  if (config.interview) {
    config.interview = InterviewConfigSchema.parse(config.interview);
  }
  if (config.backgroundJobs) {
    config.backgroundJobs = BackgroundJobsConfigSchema.parse(config.backgroundJobs);
  }
  const envPreset = process.env.OH_MY_OPENCODE_SLIM_PRESET;
  if (envPreset) {
    config.preset = envPreset;
  }
  if (config.preset) {
    const preset = config.presets?.[config.preset];
    if (preset) {
      config.agents = deepMerge(preset, config.agents);
    } else {
      const presetSource = envPreset === config.preset ? "environment variable" : "config file";
      const availablePresets = config.presets ? Object.keys(config.presets).join(", ") : "none";
      const message = `Preset "${config.preset}" not found (from ${presetSource}). Available presets: ${availablePresets}`;
      options?.onWarning?.({
        path: projectConfigPath ?? userConfigPath ?? "",
        kind: "missing-preset",
        message
      });
      if (!options?.silent) {
        console.warn(`[oh-my-opencode-slim] ${message}`);
      }
    }
  }
  if (config.companion) {
    config.companion = {
      enabled: config.companion.enabled ?? false,
      binaryPath: config.companion.binaryPath,
      position: config.companion.position ?? "bottom-right",
      size: config.companion.size ?? "medium",
      gifPack: config.companion.gifPack ?? "default",
      loopStyle: config.companion.loopStyle ?? "classic",
      speed: config.companion.speed ?? 1,
      debug: config.companion.debug ?? false
    };
  }
  validateFinalImageRouting(config, projectConfigPath ?? userConfigPath ?? "", options);
  return config;
}
function loadAgentPrompt(agentName, optionsOrPreset) {
  let preset;
  let projectDirectory;
  if (typeof optionsOrPreset === "string") {
    preset = optionsOrPreset;
  } else if (optionsOrPreset && typeof optionsOrPreset === "object") {
    preset = optionsOrPreset.preset;
    projectDirectory = optionsOrPreset.projectDirectory;
  }
  const presetDirName = preset && /^[a-zA-Z0-9_-]+$/.test(preset) ? preset : undefined;
  const searchDirs = [];
  if (projectDirectory && presetDirName) {
    searchDirs.push(path2.join(projectDirectory, ".opencode", PROMPTS_DIR_NAME, presetDirName));
  }
  if (projectDirectory) {
    searchDirs.push(path2.join(projectDirectory, ".opencode", PROMPTS_DIR_NAME));
  }
  if (presetDirName) {
    for (const userDir of getConfigSearchDirs()) {
      searchDirs.push(path2.join(userDir, PROMPTS_DIR_NAME, presetDirName));
    }
  }
  for (const userDir of getConfigSearchDirs()) {
    searchDirs.push(path2.join(userDir, PROMPTS_DIR_NAME));
  }
  const readFirstPrompt = (fileName, errorPrefix) => {
    for (const dir of searchDirs) {
      const promptPath = path2.join(dir, fileName);
      if (!fs.existsSync(promptPath)) {
        continue;
      }
      try {
        return fs.readFileSync(promptPath, "utf-8");
      } catch (error) {
        console.warn(`[oh-my-opencode-slim] ${errorPrefix} ${promptPath}:`, error instanceof Error ? error.message : String(error));
      }
    }
    return;
  };
  const result = {};
  result.prompt = readFirstPrompt(`${agentName}.md`, "Error reading prompt file");
  result.appendPrompt = readFirstPrompt(`${agentName}_append.md`, "Error reading append prompt file");
  return result;
}

// src/multiplexer/tmux-pane-registry.ts
import { createHash, randomUUID } from "node:crypto";
import * as fs2 from "node:fs";
import * as os from "node:os";
import * as path3 from "node:path";
var TMUX_PANE_REGISTRATION_TTL_MS = 30000;
function dataDir() {
  return process.env.XDG_DATA_HOME ?? path3.join(os.homedir(), ".local", "share");
}
function sessionScope(sessionId) {
  return createHash("sha256").update(sessionId).digest("hex").slice(0, 24);
}
function getTmuxPaneRegistrationPath(sessionId) {
  return path3.join(dataDir(), "opencode", "storage", "oh-my-opencode-slim", "tmux-panes", `${sessionScope(sessionId)}.json`);
}
function isPaneId(value) {
  return typeof value === "string" && /^%\d+$/.test(value);
}
function recordTmuxPane(sessionId, paneId, ownerPid = process.pid) {
  if (!sessionId || !isPaneId(paneId))
    return false;
  const registration = {
    version: 1,
    sessionId,
    paneId,
    ownerPid,
    updatedAt: Date.now()
  };
  try {
    const filePath = getTmuxPaneRegistrationPath(sessionId);
    fs2.mkdirSync(path3.dirname(filePath), { recursive: true });
    const tmpPath = `${filePath}.${process.pid}.${randomUUID()}.tmp`;
    try {
      fs2.writeFileSync(tmpPath, `${JSON.stringify(registration)}
`);
      fs2.renameSync(tmpPath, filePath);
      return true;
    } finally {
      try {
        if (fs2.existsSync(tmpPath))
          fs2.unlinkSync(tmpPath);
      } catch {}
    }
  } catch {
    return false;
  }
}
function readTmuxPane(sessionId, now = Date.now()) {
  try {
    const parsed = JSON.parse(fs2.readFileSync(getTmuxPaneRegistrationPath(sessionId), "utf8"));
    if (parsed.version !== 1 || parsed.sessionId !== sessionId || !isPaneId(parsed.paneId) || typeof parsed.updatedAt !== "number" || now - parsed.updatedAt > TMUX_PANE_REGISTRATION_TTL_MS) {
      return;
    }
    return parsed.paneId;
  } catch {
    return;
  }
}
function removeTmuxPane(sessionId, paneId, ownerPid = process.pid) {
  try {
    const filePath = getTmuxPaneRegistrationPath(sessionId);
    const parsed = JSON.parse(fs2.readFileSync(filePath, "utf8"));
    if (parsed.paneId === paneId && parsed.ownerPid === ownerPid) {
      fs2.unlinkSync(filePath);
    }
  } catch {}
}

// src/tui-preset.ts
import { createElement, insert } from "@opentui/solid";

// src/tools/preset-switch.ts
import * as fs3 from "node:fs";
function switchPresetOnDisk(directory, presetName, config) {
  const presets = config.presets ?? {};
  const preset = presets[presetName];
  if (!preset) {
    const available = Object.keys(presets);
    const hint = available.length > 0 ? `Available presets: ${available.join(", ")}` : "No presets configured. Define presets in oh-my-opencode-slim.jsonc.";
    return {
      ok: false,
      presetName,
      message: `Preset "${presetName}" not found. ${hint}`,
      summary: []
    };
  }
  const agentUpdates = buildAgentUpdates(preset);
  if (Object.keys(agentUpdates).length === 0) {
    return {
      ok: false,
      presetName,
      message: `Preset "${presetName}" is empty (no agent overrides defined).`,
      summary: []
    };
  }
  persistPresetName(directory, presetName);
  return {
    ok: true,
    presetName,
    message: `Saved preset "${presetName}". Reload OpenCode (or start a new conversation) for it to take effect. The current session keeps its existing agent models to avoid truncating context, drifting prior turns, or destabilizing running subagents.`,
    summary: buildPresetSummary(agentUpdates)
  };
}
function buildAgentUpdates(preset) {
  const agentUpdates = {};
  for (const [agentName, override] of Object.entries(preset)) {
    const resolvedName = AGENT_ALIASES[agentName] ?? agentName;
    const agentConfig = mapOverrideToAgentConfig(override);
    if (Object.keys(agentConfig).length > 0) {
      agentUpdates[resolvedName] = agentConfig;
    }
  }
  return agentUpdates;
}
function mapOverrideToAgentConfig(override) {
  const agentConfig = {};
  if (typeof override.model === "string") {
    agentConfig.model = override.model;
  } else if (Array.isArray(override.model) && override.model.length > 0) {
    const first = override.model[0];
    agentConfig.model = typeof first === "string" ? first : first.id;
    if (typeof first !== "string" && first.variant) {
      agentConfig.variant = first.variant;
    }
  }
  if (typeof override.temperature === "number") {
    agentConfig.temperature = override.temperature;
  }
  if (typeof override.variant === "string") {
    agentConfig.variant = override.variant;
  }
  if (override.options && typeof override.options === "object" && !Array.isArray(override.options)) {
    agentConfig.options = override.options;
  }
  return agentConfig;
}
function buildPresetSummary(agentUpdates) {
  const summaryParts = [];
  for (const [name, cfg] of Object.entries(agentUpdates)) {
    const parts = [name];
    if (cfg.model)
      parts.push(`model: ${cfg.model}`);
    if (cfg.variant)
      parts.push(`variant: ${cfg.variant}`);
    if (cfg.temperature !== undefined)
      parts.push(`temp: ${cfg.temperature}`);
    if (cfg.options)
      parts.push("options: yes");
    summaryParts.push(parts.join(" → "));
  }
  return summaryParts;
}
function persistPresetName(directory, presetName) {
  try {
    const { userConfigPath } = findPluginConfigPaths(directory);
    if (!userConfigPath)
      return;
    const raw = fs3.readFileSync(userConfigPath, "utf-8").replace(/^\uFEFF/, "");
    const persisted = JSON.parse(stripJsonComments(raw));
    persisted.preset = presetName;
    fs3.writeFileSync(userConfigPath, `${JSON.stringify(persisted, null, 2)}
`);
  } catch {}
}
function readUserConfig(directory) {
  try {
    const { userConfigPath } = findPluginConfigPaths(directory);
    if (!userConfigPath)
      return null;
    const raw = fs3.readFileSync(userConfigPath, "utf-8").replace(/^\uFEFF/, "");
    return JSON.parse(stripJsonComments(raw));
  } catch {
    return null;
  }
}
function writeUserConfig(directory, config) {
  try {
    const { userConfigPath } = findPluginConfigPaths(directory);
    if (!userConfigPath)
      return false;
    fs3.writeFileSync(userConfigPath, `${JSON.stringify(config, null, 2)}
`);
    return true;
  } catch {
    return false;
  }
}
function writePreset(directory, name, preset) {
  const config = readUserConfig(directory) ?? {};
  const presets = config.presets ?? {};
  presets[name] = preset;
  config.presets = presets;
  return writeUserConfig(directory, config);
}
function deletePreset(directory, name) {
  const config = readUserConfig(directory);
  if (!config)
    return false;
  const presets = config.presets;
  if (!presets || !(name in presets))
    return false;
  delete presets[name];
  if (config.preset === name) {
    delete config.preset;
  }
  return writeUserConfig(directory, config);
}
function setAgentOverride(preset, agentName, override) {
  return { ...preset, [agentName]: override };
}
function removeAgentFromPreset(preset, agentName) {
  if (!(agentName in preset))
    return preset;
  const next = { ...preset };
  delete next[agentName];
  return next;
}

// src/tui-preset.ts
function desc(text) {
  const node = createElement("text");
  insert(node, text);
  return node;
}
var ACTION_NEW_PRESET = "__omo_new_preset__";
var ACTION_ADD_AGENT = "__omo_add_agent__";
var ACTION_BACK = "__omo_back__";
function openPresetManager(api, directory, snapshotRef) {
  showPresetList({ api, directory, snapshotRef });
}
function showPresetList(state) {
  const config = loadPluginConfig(state.directory, { silent: true });
  const presets = config.presets ?? {};
  const names = Object.keys(presets);
  const activePreset = config.preset ?? null;
  if (names.length === 0 && !activePreset) {
    promptAndCreatePreset(state, () => showPresetList(state));
    return;
  }
  const options = names.map((name) => ({
    title: name === activePreset ? `${name} (active)` : name,
    value: name,
    description: describePreset(presets[name])
  }));
  options.push({
    title: "+ Create new preset",
    value: ACTION_NEW_PRESET
  });
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogSelect({
      title: "Presets",
      placeholder: "Select a preset to apply or edit",
      options,
      onSelect: (option) => {
        if (option.value === ACTION_NEW_PRESET) {
          promptAndCreatePreset(state, () => showPresetList(state));
          return;
        }
        showPresetActions(state, option.value);
      }
    })
  }));
}
function showPresetActions(state, presetName) {
  const options = [
    { title: "Apply preset (reload to take effect)", value: "apply" },
    { title: "Edit agents", value: "edit" },
    { title: "Delete preset", value: "delete" },
    { title: "← Back", value: ACTION_BACK }
  ];
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogSelect({
      title: `Preset: ${presetName}`,
      options,
      onSelect: (option) => {
        switch (option.value) {
          case "apply":
            applyPreset(state, presetName);
            break;
          case "edit":
            editPreset(state, presetName);
            break;
          case "delete":
            confirmDeletePreset(state, presetName);
            break;
          default:
            showPresetList(state);
        }
      }
    })
  }));
}
function applyPreset(state, presetName) {
  applyPresetWithMessage(state, presetName, "Preset saved");
}
function applyPresetWithMessage(state, presetName, title) {
  const config = loadPluginConfig(state.directory, { silent: true });
  const result = switchPresetOnDisk(state.directory, presetName, config);
  state.api.ui.dialog.clear();
  state.api.ui.toast({
    variant: result.ok ? "success" : "warning",
    title: result.ok ? title : "Preset switch failed",
    message: result.ok ? `Saved preset "${presetName}". Start a new conversation (or reload OpenCode) to use it. ${result.summary.join("; ")}` : result.message
  });
}
function confirmDeletePreset(state, presetName) {
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogConfirm({
      title: "Delete preset",
      message: `Delete preset "${presetName}"? This cannot be undone.`,
      onConfirm: () => {
        const ok = deletePreset(state.directory, presetName);
        state.api.ui.dialog.clear();
        state.api.ui.toast({
          variant: ok ? "success" : "warning",
          title: ok ? "Preset deleted" : "Delete failed",
          message: ok ? `Deleted preset "${presetName}".` : `Could not delete "${presetName}" (it may not exist in the user config file).`
        });
        showPresetList(state);
      },
      onCancel: () => showPresetActions(state, presetName)
    })
  }));
}
function promptAndCreatePreset(state, onCancel) {
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogPrompt({
      title: "Create new preset",
      placeholder: "preset-name",
      onConfirm: (value) => {
        const name = value.trim();
        if (!name) {
          onCancel();
          return;
        }
        if (/\s/.test(name)) {
          state.api.ui.toast({
            variant: "warning",
            title: "Invalid name",
            message: "Preset names cannot contain spaces."
          });
          promptAndCreatePreset(state, onCancel);
          return;
        }
        const config = loadPluginConfig(state.directory, {
          silent: true
        });
        if (config.presets?.[name]) {
          confirmOverwritePreset(state, name, onCancel);
          return;
        }
        editPresetWorkingCopy(state, name, {});
      },
      onCancel
    })
  }));
}
function confirmOverwritePreset(state, name, onCancel) {
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogConfirm({
      title: "Preset exists",
      message: `A preset named "${name}" already exists. Overwrite it with a new empty preset?`,
      onConfirm: () => {
        editPresetWorkingCopy(state, name, {});
      },
      onCancel: () => promptAndCreatePreset(state, onCancel)
    })
  }));
}
function editPreset(state, presetName) {
  const config = loadPluginConfig(state.directory, { silent: true });
  const preset = config.presets?.[presetName] ?? {};
  editPresetWorkingCopy(state, presetName, { ...preset });
}
function editPresetWorkingCopy(state, presetName, working) {
  const agentNames = Object.keys(working);
  const options = agentNames.map((name) => ({
    title: name,
    value: name,
    description: describeOverride(working[name])
  }));
  options.push({ title: "+ Add agent", value: ACTION_ADD_AGENT });
  options.push({ title: "− Remove agent", value: "__omo_remove_agent__" });
  options.push({ title: "\uD83D\uDCBE Save", value: "__omo_save__" });
  options.push({
    title: "\uD83D\uDCBE Save & Apply",
    value: "__omo_save_apply__"
  });
  options.push({ title: "← Back", value: ACTION_BACK });
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogSelect({
      title: `Edit preset: ${presetName}`,
      options,
      onSelect: (option) => {
        switch (option.value) {
          case ACTION_ADD_AGENT:
            promptAddAgent(state, presetName, working);
            break;
          case "__omo_remove_agent__":
            promptRemoveAgent(state, presetName, working);
            break;
          case "__omo_save__":
            savePreset(state, presetName, working, false);
            break;
          case "__omo_save_apply__": {
            const saved = savePreset(state, presetName, working, false, true);
            if (saved) {
              applyPresetWithMessage(state, presetName, "Preset saved & applied");
            } else {
              state.api.ui.toast({
                variant: "warning",
                title: "Save failed",
                message: `Could not write preset "${presetName}" to the config file.`
              });
            }
            break;
          }
          case ACTION_BACK:
            showPresetList(state);
            break;
          default:
            editAgent(state, presetName, working, option.value);
        }
      }
    })
  }));
}
function promptAddAgent(state, presetName, working) {
  const present = new Set(Object.keys(working));
  const available = ALL_AGENT_NAMES.filter((n) => !present.has(n));
  if (available.length === 0) {
    state.api.ui.toast({
      variant: "info",
      title: "No agents left",
      message: "All known agents are already in this preset."
    });
    editPresetWorkingCopy(state, presetName, working);
    return;
  }
  const options = available.map((n) => ({
    title: n,
    value: n
  }));
  options.push({ title: "← Back", value: ACTION_BACK });
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogSelect({
      title: "Add agent",
      options,
      onSelect: (option) => {
        if (option.value === ACTION_BACK) {
          editPresetWorkingCopy(state, presetName, working);
          return;
        }
        const next = setAgentOverride(working, option.value, {});
        editAgent(state, presetName, next, option.value);
      }
    })
  }));
}
function promptRemoveAgent(state, presetName, working) {
  const agentNames = Object.keys(working);
  if (agentNames.length === 0) {
    state.api.ui.toast({
      variant: "info",
      title: "No agents",
      message: "This preset has no agents to remove."
    });
    editPresetWorkingCopy(state, presetName, working);
    return;
  }
  const options = agentNames.map((n) => ({
    title: n,
    value: n,
    description: describeOverride(working[n])
  }));
  options.push({ title: "← Back", value: ACTION_BACK });
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogSelect({
      title: "Remove agent",
      options,
      onSelect: (option) => {
        if (option.value === ACTION_BACK) {
          editPresetWorkingCopy(state, presetName, working);
          return;
        }
        const next = removeAgentFromPreset(working, option.value);
        state.api.ui.toast({
          variant: "success",
          title: "Agent removed",
          message: `Removed ${option.value} from preset.`
        });
        editPresetWorkingCopy(state, presetName, next);
      }
    })
  }));
}
function savePreset(state, presetName, working, returnToList, silent = false) {
  const cleaned = {};
  for (const [agent, override] of Object.entries(working)) {
    if (Object.keys(override).length > 0) {
      cleaned[agent] = override;
    }
  }
  const ok = writePreset(state.directory, presetName, cleaned);
  if (!silent) {
    state.api.ui.toast({
      variant: ok ? "success" : "warning",
      title: ok ? "Preset saved" : "Save failed",
      message: ok ? `Saved preset "${presetName}" to config.` : `Could not write preset "${presetName}" to the config file.`
    });
  }
  if (returnToList) {
    showPresetList(state);
  }
  return ok;
}
function editAgent(state, presetName, working, agentName) {
  const current = working[agentName] ?? {};
  pickModel(state, presetName, working, agentName, current);
}
async function fetchModelOptions(api) {
  if (!api.client?.config?.providers) {
    return [];
  }
  const res = await api.client.config.providers();
  const providers = res.data?.providers ?? [];
  const options = [];
  for (const provider of providers) {
    if (!provider?.models)
      continue;
    for (const [modelId, model] of Object.entries(provider.models)) {
      if (!model)
        continue;
      options.push({
        value: `${provider.id}/${modelId}`,
        title: model.name ?? modelId,
        description: provider.id,
        variants: model.variants ? Object.keys(model.variants) : []
      });
    }
  }
  return options;
}
function pickModel(state, presetName, working, agentName, current) {
  state.api.ui.toast({
    variant: "info",
    title: "Loading models",
    message: `Fetching available models for ${agentName}…`
  });
  (async () => {
    let options;
    try {
      options = await fetchModelOptions(state.api);
    } catch (err) {
      state.api.ui.toast({
        variant: "warning",
        title: "Could not load models",
        message: `Failed to fetch providers: ${String(err)}`
      });
      editPresetWorkingCopy(state, presetName, working);
      return;
    }
    if (options.length === 0) {
      state.api.ui.toast({
        variant: "warning",
        title: "No models available",
        message: "Could not retrieve the model list. You can edit the preset config file manually."
      });
      editPresetWorkingCopy(state, presetName, working);
      return;
    }
    try {
      const currentModel = typeof current.model === "string" ? options.find((o) => o.value === current.model)?.value : undefined;
      const selectOptions = options.map((o) => ({
        title: o.title,
        value: o.value,
        description: o.description
      }));
      state.api.ui.dialog.replace(() => state.api.ui.Dialog({
        size: "large",
        onClose: () => state.api.ui.dialog.clear(),
        children: state.api.ui.DialogSelect({
          title: `Edit ${agentName} — model`,
          placeholder: "Search models",
          current: currentModel,
          options: selectOptions,
          onSelect: (option) => {
            const chosen = options.find((o) => o.value === option.value);
            const next = {
              ...current,
              model: option.value
            };
            pickVariant(state, presetName, working, agentName, next, chosen?.variants ?? []);
          }
        })
      }));
    } catch (err) {
      state.api.ui.toast({
        variant: "error",
        title: "Model picker error",
        message: String(err)
      });
      editPresetWorkingCopy(state, presetName, working);
    }
  })();
}
function pickVariant(state, presetName, working, agentName, current, availableVariants) {
  if (availableVariants.length === 0) {
    pickTemperature(state, presetName, working, agentName, current);
    return;
  }
  const options = [
    { title: "none", value: "", description: "no variant" },
    ...availableVariants.map((v) => ({ title: v, value: v }))
  ];
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogSelect({
      title: `Edit ${agentName} — variant (thinking strength)`,
      current: typeof current.variant === "string" ? current.variant : "",
      options,
      onSelect: (option) => {
        const next = { ...current };
        if (option.value) {
          next.variant = option.value;
        } else {
          delete next.variant;
        }
        pickTemperature(state, presetName, working, agentName, next);
      }
    })
  }));
}
function pickTemperature(state, presetName, working, agentName, current) {
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogPrompt({
      title: `Edit ${agentName} — temperature`,
      description: () => desc("Enter a number 0–2, or leave blank for the provider default (typically 1.0)."),
      value: typeof current.temperature === "number" ? String(current.temperature) : "",
      placeholder: "none",
      onConfirm: (value) => {
        const trimmed = value.trim();
        const next = { ...current };
        if (trimmed) {
          const parsed = Number(trimmed);
          if (Number.isNaN(parsed) || parsed < 0 || parsed > 2) {
            state.api.ui.toast({
              variant: "warning",
              title: "Invalid temperature",
              message: "Temperature must be a number between 0 and 2."
            });
            pickTemperature(state, presetName, working, agentName, current);
            return;
          }
          next.temperature = parsed;
        } else {
          delete next.temperature;
        }
        pickOptions(state, presetName, working, agentName, next);
      },
      onCancel: () => editPresetWorkingCopy(state, presetName, working)
    })
  }));
}
function pickOptions(state, presetName, working, agentName, current) {
  const currentJson = current.options && typeof current.options === "object" ? JSON.stringify(current.options) : "{}";
  state.api.ui.dialog.replace(() => state.api.ui.Dialog({
    size: "large",
    onClose: () => state.api.ui.dialog.clear(),
    children: state.api.ui.DialogPrompt({
      title: `Edit ${agentName} — options (JSON)`,
      description: () => desc('Provider-specific options as JSON, e.g. {"thinking":{"type":"enabled","budgetTokens":10000}}. Use {} for none.'),
      value: currentJson,
      placeholder: "{}",
      onConfirm: (value) => {
        const trimmed = value.trim() || "{}";
        let parsed;
        try {
          parsed = JSON.parse(trimmed);
        } catch {
          state.api.ui.toast({
            variant: "warning",
            title: "Invalid JSON",
            message: "Options must be valid JSON."
          });
          pickOptions(state, presetName, working, agentName, current);
          return;
        }
        const next = { ...current };
        if (Object.keys(parsed).length > 0) {
          next.options = parsed;
        } else {
          delete next.options;
        }
        const updated = setAgentOverride(working, agentName, next);
        state.api.ui.toast({
          variant: "success",
          title: "Agent updated",
          message: `${agentName} → ${describeOverride(next)}`
        });
        editPresetWorkingCopy(state, presetName, updated);
      },
      onCancel: () => editPresetWorkingCopy(state, presetName, working)
    })
  }));
}
function describePreset(preset) {
  const parts = Object.entries(preset).map(([agent, override]) => `${agent}: ${describeOverride(override)}`);
  return parts.length > 0 ? parts.join(", ") : "(empty)";
}
function describeOverride(override) {
  const bits = [];
  if (typeof override.model === "string") {
    bits.push(override.model);
  } else if (Array.isArray(override.model) && override.model.length > 0) {
    const first = override.model[0];
    bits.push(typeof first === "string" ? first : first.id);
  }
  if (typeof override.variant === "string")
    bits.push(`variant=${override.variant}`);
  if (typeof override.temperature === "number")
    bits.push(`temp=${override.temperature}`);
  if (override.options && Object.keys(override.options).length > 0)
    bits.push("options");
  return bits.length > 0 ? bits.join(", ") : "(unset)";
}

// src/tui-state.ts
import { createHash as createHash2, randomUUID as randomUUID2 } from "node:crypto";
import * as fs4 from "node:fs";
import * as os2 from "node:os";
import * as path4 from "node:path";
var STATE_DIR = "oh-my-opencode-slim";
var STATE_FILE = "tui-state.json";
var STATE_LOCK_RETRY_MS = 5;
var STATE_LOCK_TIMEOUT_MS = 1000;
var STATE_LOCK_STALE_MS = 30000;
var STATE_LOCK_SLEEPER = new Int32Array(new SharedArrayBuffer(4));
function dataDir2() {
  return process.env.XDG_DATA_HOME ?? path4.join(os2.homedir(), ".local", "share");
}
function projectScope(projectDir) {
  return createHash2("sha256").update(path4.resolve(projectDir)).digest("hex").slice(0, 12);
}
function getTuiStatePath(projectDir) {
  return path4.join(dataDir2(), "opencode", "storage", STATE_DIR, projectScope(projectDir), STATE_FILE);
}
function emptySnapshot() {
  return {
    version: 1,
    updatedAt: Date.now(),
    agentModels: {},
    agentVariants: {},
    activeSessions: {}
  };
}
function parseSnapshot(value) {
  const parsed = JSON.parse(value);
  if (parsed?.version !== 1)
    return emptySnapshot();
  return {
    version: 1,
    updatedAt: typeof parsed.updatedAt === "number" ? parsed.updatedAt : Date.now(),
    agentModels: parsed.agentModels ?? {},
    agentVariants: parsed.agentVariants ?? {},
    activeSessions: parsed.activeSessions ?? {}
  };
}
function readTuiSnapshot(projectDir) {
  try {
    return parseSnapshot(fs4.readFileSync(getTuiStatePath(projectDir), "utf8"));
  } catch {
    return emptySnapshot();
  }
}
async function readTuiSnapshotAsync(projectDir) {
  try {
    return parseSnapshot(await fs4.promises.readFile(getTuiStatePath(projectDir), "utf8"));
  } catch {
    return emptySnapshot();
  }
}
function writeTuiSnapshot(snapshot, projectDir) {
  try {
    const filePath = getTuiStatePath(projectDir);
    fs4.mkdirSync(path4.dirname(filePath), { recursive: true });
    const tmpPath = `${filePath}.${process.pid}.${randomUUID2()}.tmp`;
    try {
      fs4.writeFileSync(tmpPath, `${JSON.stringify(snapshot)}
`);
      fs4.renameSync(tmpPath, filePath);
    } finally {
      try {
        if (fs4.existsSync(tmpPath))
          fs4.unlinkSync(tmpPath);
      } catch {}
    }
  } catch {}
}
function isProcessRunning(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error.code === "EPERM";
  }
}
function isStateLockStale(lockPath) {
  try {
    const metadata = JSON.parse(fs4.readFileSync(lockPath, "utf8"));
    if (typeof metadata.pid === "number" && metadata.pid > 0) {
      return !isProcessRunning(metadata.pid);
    }
  } catch {}
  try {
    return Date.now() - fs4.statSync(lockPath).mtimeMs > STATE_LOCK_STALE_MS;
  } catch {
    return false;
  }
}
function acquireStateLock(statePath) {
  const lockPath = `${statePath}.lock`;
  const deadline = Date.now() + STATE_LOCK_TIMEOUT_MS;
  while (Date.now() <= deadline) {
    const token = randomUUID2();
    let created = false;
    try {
      const handle = fs4.openSync(lockPath, "wx");
      created = true;
      try {
        fs4.writeFileSync(handle, JSON.stringify({ pid: process.pid, token, createdAt: Date.now() }));
      } finally {
        fs4.closeSync(handle);
      }
      return { path: lockPath, token };
    } catch (error) {
      if (created) {
        try {
          fs4.unlinkSync(lockPath);
        } catch {}
      }
      if (error.code !== "EEXIST")
        return;
      if (isStateLockStale(lockPath)) {
        try {
          fs4.unlinkSync(lockPath);
        } catch {}
        continue;
      }
      Atomics.wait(STATE_LOCK_SLEEPER, 0, 0, STATE_LOCK_RETRY_MS);
    }
  }
}
function releaseStateLock(lock) {
  try {
    const metadata = JSON.parse(fs4.readFileSync(lock.path, "utf8"));
    if (metadata.token === lock.token)
      fs4.unlinkSync(lock.path);
  } catch {}
}
function updateSnapshot(projectDir, mutator) {
  const statePath = getTuiStatePath(projectDir);
  try {
    fs4.mkdirSync(path4.dirname(statePath), { recursive: true });
  } catch {
    return;
  }
  const lock = acquireStateLock(statePath);
  if (!lock)
    return;
  try {
    const snapshot = readTuiSnapshot(projectDir);
    const beforeModels = JSON.stringify(snapshot.agentModels);
    const beforeVariants = JSON.stringify(snapshot.agentVariants);
    const beforeActiveSessions = JSON.stringify(snapshot.activeSessions);
    mutator(snapshot);
    if (JSON.stringify(snapshot.agentModels) === beforeModels && JSON.stringify(snapshot.agentVariants) === beforeVariants && JSON.stringify(snapshot.activeSessions) === beforeActiveSessions) {
      return;
    }
    snapshot.updatedAt = Date.now();
    writeTuiSnapshot(snapshot, projectDir);
  } finally {
    releaseStateLock(lock);
  }
}
function recordTuiAgentModels(input, projectDir) {
  updateSnapshot(projectDir, (snapshot) => {
    snapshot.agentModels = { ...input.agentModels };
    snapshot.agentVariants = { ...input.agentVariants ?? {} };
  });
}
function recordTuiAgentModel(input, projectDir) {
  updateSnapshot(projectDir, (snapshot) => {
    snapshot.agentModels[input.agentName] = input.model;
    if (input.variant !== undefined) {
      if (input.variant === null) {
        delete snapshot.agentVariants[input.agentName];
      } else {
        snapshot.agentVariants[input.agentName] = input.variant;
      }
    }
  });
}
function recordTuiAgentActivity(input, projectDir) {
  updateSnapshot(projectDir, (snapshot) => {
    if (input.active) {
      snapshot.activeSessions[input.sessionID] = input.agentName;
    } else {
      delete snapshot.activeSessions[input.sessionID];
    }
  });
}
function clearTuiAgentActivities(projectDir) {
  updateSnapshot(projectDir, (snapshot) => {
    snapshot.activeSessions = {};
  });
}

// src/utils/env.ts
var TRUTHY_ENV_VALUES = new Set(["1", "true", "yes", "on"]);
var PLUGIN_DISABLE_ENV = "OH_MY_OPENCODE_SLIM_DISABLE";
function isTruthyEnvValue(value) {
  return TRUTHY_ENV_VALUES.has(value?.trim().toLowerCase() ?? "");
}
function isPluginDisabledByEnv(env = process.env) {
  return isTruthyEnvValue(env[PLUGIN_DISABLE_ENV]);
}

// src/tui.ts
var PLUGIN_NAME = "oh-my-opencode-slim";
var CONFIG_WARNING_COLOR = "orange";
var FALLBACK_SIDEBAR_AGENTS = SUBAGENT_NAMES.filter((agent) => agent !== "councillor" && agent !== "council" && !DEFAULT_DISABLED_AGENTS.includes(agent));
var BORDER = { type: "single" };
var TMUX_PANE_HEARTBEAT_MS = 1e4;
var ACTIVITY_FRAME_MS = 100;
var ACTIVITY_FRAMES = [
  "⠋",
  "⠙",
  "⠹",
  "⠸",
  "⠼",
  "⠴",
  "⠦",
  "⠧",
  "⠇",
  "⠏"
];
async function readPackageVersion() {
  try {
    const packageJson = await Bun.file(new URL("../package.json", import.meta.url)).json();
    return typeof packageJson.version === "string" ? packageJson.version : undefined;
  } catch {
    return;
  }
}
function element(tag, props, children = []) {
  const node = createElement2(tag);
  for (const [key, value] of Object.entries(props)) {
    if (value !== undefined)
      setProp(node, key, value);
  }
  for (const child of children) {
    if (child === null || child === undefined || child === false)
      continue;
    insert2(node, child);
  }
  return node;
}
function text(props, children) {
  return element("text", props, children);
}
function box(props, children = []) {
  return element("box", props, children);
}
function reactiveElement(render) {
  const root = box({ width: "100%", flexDirection: "column" });
  insert2(root, render);
  return root;
}
function getTuiDirectory(api) {
  return api.state?.path?.directory ?? process.cwd();
}
function resolveRouteSessionId(route) {
  const view = route;
  if (view.name === "session" && typeof view.params?.sessionID === "string") {
    return view.params.sessionID;
  }
  if (view.type === "session" && typeof view.sessionID === "string") {
    return view.sessionID;
  }
  return;
}
function clearTmuxPaneRegistration(registration) {
  if (registration.sessionId && registration.paneId) {
    removeTmuxPane(registration.sessionId, registration.paneId, registration.ownerPid);
  }
  registration.sessionId = undefined;
  registration.paneId = undefined;
  registration.lastRecordedAt = 0;
}
function syncTmuxPaneRegistration(route, registration, now = Date.now()) {
  const paneId = process.env.TMUX_PANE;
  const sessionId = resolveRouteSessionId(route);
  const unchanged = registration.sessionId === sessionId && registration.paneId === paneId;
  if (!paneId || !sessionId) {
    clearTmuxPaneRegistration(registration);
    return;
  }
  if (unchanged && now - registration.lastRecordedAt < TMUX_PANE_HEARTBEAT_MS) {
    return;
  }
  if (!unchanged)
    clearTmuxPaneRegistration(registration);
  if (recordTmuxPane(sessionId, paneId, registration.ownerPid)) {
    registration.sessionId = sessionId;
    registration.paneId = paneId;
    registration.lastRecordedAt = now;
  }
}
function splitSidebarModelId(model) {
  const slashIndex = model.indexOf("/");
  if (slashIndex === -1) {
    return { model };
  }
  return {
    provider: model.slice(0, slashIndex),
    model: model.slice(slashIndex + 1)
  };
}
function getSidebarAgentNames(snapshot) {
  const configuredAgents = Object.keys(snapshot.agentModels);
  return configuredAgents.length > 0 ? configuredAgents : FALLBACK_SIDEBAR_AGENTS;
}
function getActiveSidebarAgentNames(snapshot) {
  return new Set(Object.values(snapshot.activeSessions));
}
function getSidebarActivityIndicator(active, now = Date.now()) {
  if (!active)
    return " ";
  const frame = Math.floor(now / ACTIVITY_FRAME_MS) % ACTIVITY_FRAMES.length;
  return ACTIVITY_FRAMES[frame];
}
function activityIndicator(active, now, theme) {
  return text({
    fg: active ? theme.accent ?? theme.text : theme.textMuted,
    width: 2
  }, [getSidebarActivityIndicator(active, now)]);
}
function agentRow(label, model, variant, active, now, theme) {
  const modelParts = splitSidebarModelId(model);
  const detailRows = [];
  function detailRow(fieldLabel, value) {
    return box({ width: "100%", flexDirection: "row", paddingLeft: 2 }, [
      text({ fg: theme.textMuted, width: 9 }, [fieldLabel]),
      text({ fg: theme.textMuted }, [value])
    ]);
  }
  if (modelParts.provider) {
    detailRows.push(detailRow("provider", modelParts.provider));
  }
  detailRows.push(detailRow("model", modelParts.model));
  if (variant) {
    detailRows.push(detailRow("variant", variant));
  }
  return box({ width: "100%", flexDirection: "column", marginBottom: 1 }, [
    box({ width: "100%", flexDirection: "row" }, [
      text({ fg: theme.textMuted, width: 14 }, [label]),
      activityIndicator(active, now, theme)
    ]),
    ...detailRows
  ]);
}
function compactAgentRow(label, model, _variant, active, now, theme) {
  const modelName = splitSidebarModelId(model).model;
  return box({
    width: "100%",
    flexDirection: "row",
    justifyContent: "space-between"
  }, [
    box({ width: 16, flexDirection: "row" }, [
      text({ fg: theme.textMuted, width: 14 }, [label]),
      activityIndicator(active, now, theme)
    ]),
    text({ fg: theme.textMuted }, [modelName])
  ]);
}
function getContrastForeground(accent, themeText, themeBackground) {
  if (!accent)
    return themeText;
  let accentRgba;
  try {
    accentRgba = parseColor(accent);
  } catch {
    return themeText;
  }
  const luminance = 0.299 * accentRgba.r + 0.587 * accentRgba.g + 0.114 * accentRgba.b;
  if (luminance > 0.5) {
    if (themeBackground) {
      try {
        const bgRgba = parseColor(themeBackground);
        if (bgRgba.a !== 0) {
          const bgLum = 0.299 * bgRgba.r + 0.587 * bgRgba.g + 0.114 * bgRgba.b;
          if (bgLum < 0.5) {
            return themeBackground;
          }
        }
      } catch {}
    }
    return RGBA.fromInts(0, 0, 0);
  }
  if (themeText) {
    try {
      const textRgba = parseColor(themeText);
      const textLum = 0.299 * textRgba.r + 0.587 * textRgba.g + 0.114 * textRgba.b;
      if (textLum > 0.5) {
        return themeText;
      }
    } catch {}
  }
  return RGBA.fromInts(255, 255, 255);
}
function renderSidebar(snapshot, version, theme, configInvalid, compactSidebar, now = Date.now()) {
  const configStatusRow = buildConfigStatusRow(configInvalid, theme);
  const activeAgents = getActiveSidebarAgentNames(snapshot);
  return box({
    width: "100%",
    flexDirection: "column",
    border: BORDER,
    borderColor: theme.borderActive,
    paddingTop: 1,
    paddingBottom: 1,
    paddingLeft: 1,
    paddingRight: 1
  }, [
    box({
      width: "100%",
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center"
    }, [
      box({ paddingLeft: 1, paddingRight: 1, backgroundColor: theme.accent }, [
        text({
          fg: getContrastForeground(theme.accent, theme.text, theme.background)
        }, ["OMO-Slim"])
      ]),
      text({ fg: theme.textMuted }, [`v${version}`])
    ]),
    configStatusRow,
    box({ width: "100%", marginTop: 1 }, [
      text({ fg: theme.text }, ["Agents"])
    ]),
    ...getSidebarAgentNames(snapshot).map((agentName) => {
      const model = snapshot.agentModels[agentName] ?? "pending";
      const variant = snapshot.agentVariants[agentName];
      const active = activeAgents.has(agentName);
      if (compactSidebar) {
        return compactAgentRow(agentName, model, variant, active, now, theme);
      }
      return agentRow(agentName, model, variant, active, now, theme);
    })
  ]);
}
function buildConfigStatusRow(configInvalid, theme) {
  if (!configInvalid)
    return null;
  return box({
    width: "100%",
    flexDirection: "column",
    marginTop: 1,
    marginBottom: 1
  }, [
    text({ fg: CONFIG_WARNING_COLOR }, ["Config invalid"]),
    text({ fg: theme.textMuted }, ["Run doctor for details"])
  ]);
}
function readConfigState(directory) {
  let configInvalid = false;
  const config = loadPluginConfig(directory, {
    silent: true,
    onWarning: (warning) => {
      if (warning.kind === "invalid-json" || warning.kind === "invalid-schema" || warning.kind === "read-error") {
        configInvalid = true;
      }
    }
  });
  const compactSidebar = config.compactSidebar ?? true;
  return { configInvalid, compactSidebar };
}
function readConfigInvalid(directory) {
  return readConfigState(directory).configInvalid;
}
function readCompactSidebar(directory) {
  return readConfigState(directory).compactSidebar;
}
function v2ThemeView(theme) {
  return {
    accent: undefined,
    background: theme.background.default,
    borderActive: theme.border.default,
    text: theme.text.default,
    textMuted: theme.text.subdued
  };
}
async function setup(ctx) {
  if (isPluginDisabledByEnv())
    return;
  const version = await readPackageVersion() ?? "dev";
  let configDirectory = ctx.location?.directory ?? process.cwd();
  let { configInvalid, compactSidebar } = readConfigState(configDirectory);
  const [snapshot, setSnapshot] = createSignal(readTuiSnapshot(configDirectory));
  const [animationNow, setAnimationNow] = createSignal(Date.now());
  const tmuxRegistration = {
    ownerPid: process.pid,
    lastRecordedAt: 0
  };
  syncTmuxPaneRegistration(ctx.ui.router.current(), tmuxRegistration);
  let disposed = false;
  const renderTimer = setInterval(async () => {
    if (disposed)
      return;
    try {
      const currentDirectory = ctx.location?.directory ?? process.cwd();
      syncTmuxPaneRegistration(ctx.ui.router.current(), tmuxRegistration);
      const nextSnapshot = await readTuiSnapshotAsync(currentDirectory);
      if (disposed)
        return;
      if (currentDirectory !== configDirectory) {
        configDirectory = currentDirectory;
        ({ configInvalid, compactSidebar } = readConfigState(configDirectory));
      }
      setSnapshot(nextSnapshot);
      ctx.renderer.requestRender();
    } catch {}
  }, 1000);
  const animationTimer = setInterval(() => {
    if (!disposed && Object.keys(snapshot().activeSessions).length > 0) {
      setAnimationNow(Date.now());
    }
  }, ACTIVITY_FRAME_MS);
  const disposeSlot = ctx.ui.slot({
    append: "sidebar.content",
    render: () => reactiveElement(() => renderSidebar(snapshot(), version, v2ThemeView(ctx.theme), configInvalid, compactSidebar, animationNow()))
  });
  return () => {
    disposed = true;
    disposeSlot();
    clearInterval(renderTimer);
    clearInterval(animationTimer);
    clearTmuxPaneRegistration(tmuxRegistration);
  };
}
function buildPresetCommand(api, directoryGetter, snapshotRef) {
  return {
    title: "Switch preset",
    value: "preset",
    description: "Switch agent presets at runtime (e.g. /preset cheap)",
    slash: { name: "preset" },
    onSelect: () => {
      openPresetManager(api, directoryGetter(), snapshotRef);
    }
  };
}
var plugin = {
  id: `${PLUGIN_NAME}:tui`,
  tui: async (api, _options, meta) => {
    if (isPluginDisabledByEnv())
      return;
    const version = meta.version ?? await readPackageVersion() ?? "dev";
    let configDirectory = getTuiDirectory(api);
    let { configInvalid, compactSidebar } = readConfigState(configDirectory);
    const [snapshot, setSnapshot] = createSignal(readTuiSnapshot(configDirectory));
    const [animationNow, setAnimationNow] = createSignal(Date.now());
    const tmuxRegistration = {
      ownerPid: process.pid,
      lastRecordedAt: 0
    };
    syncTmuxPaneRegistration(api.route.current, tmuxRegistration);
    const renderTimer = setInterval(async () => {
      try {
        const currentDirectory = getTuiDirectory(api);
        syncTmuxPaneRegistration(api.route.current, tmuxRegistration);
        const nextSnapshot = await readTuiSnapshotAsync(currentDirectory);
        if (currentDirectory !== configDirectory) {
          configDirectory = currentDirectory;
          ({ configInvalid, compactSidebar } = readConfigState(configDirectory));
        }
        setSnapshot(nextSnapshot);
        api.renderer.requestRender();
      } catch {}
    }, 1000);
    const animationTimer = setInterval(() => {
      if (Object.keys(snapshot().activeSessions).length > 0) {
        setAnimationNow(Date.now());
      }
    }, ACTIVITY_FRAME_MS);
    api.lifecycle.onDispose(() => {
      clearInterval(renderTimer);
      clearInterval(animationTimer);
      clearTmuxPaneRegistration(tmuxRegistration);
    });
    api.slots.register({
      order: 900,
      slots: {
        sidebar_content() {
          return reactiveElement(() => renderSidebar(snapshot(), version, api.theme.current, configInvalid, compactSidebar, animationNow()));
        }
      }
    });
    if (api.command) {
      const snapshotRef = {
        get snapshot() {
          return snapshot();
        },
        set snapshot(value) {
          setSnapshot(value);
        }
      };
      const disposeCommands = api.command.register(() => [
        buildPresetCommand(api, () => configDirectory, snapshotRef)
      ]);
      api.lifecycle.onDispose(disposeCommands);
    }
  },
  setup
};
var tui_default = plugin;
export {
  syncTmuxPaneRegistration,
  splitSidebarModelId,
  readConfigInvalid,
  readCompactSidebar,
  getSidebarAgentNames,
  getSidebarActivityIndicator,
  getContrastForeground,
  getActiveSidebarAgentNames,
  tui_default as default
};
