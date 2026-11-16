#!/usr/bin/env node
import { createRequire } from "node:module";
var __defProp = Object.defineProperty;
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
var WINDOWS_PATH_EXT_DEFAULT = ".COM;.EXE;.BAT;.CMD", DIRECT_EXECUTION_EXTENSIONS, CMD_METACHARACTERS;
var init_compat = __esm(() => {
  DIRECT_EXECUTION_EXTENSIONS = new Set([".exe", ".com"]);
  CMD_METACHARACTERS = /[\s&|<>()^!]/;
});

// src/utils/zip-extractor.ts
var exports_zip_extractor = {};
__export(exports_zip_extractor, {
  extractZip: () => extractZip
});
import { spawnSync } from "node:child_process";
import { release } from "node:os";
function getWindowsBuildNumber() {
  if (process.platform !== "win32")
    return null;
  const parts = release().split(".");
  if (parts.length >= 3) {
    const build = parseInt(parts[2], 10);
    if (!Number.isNaN(build))
      return build;
  }
  return null;
}
function isPwshAvailable() {
  if (process.platform !== "win32")
    return false;
  const result = spawnSync("where", ["pwsh"], {
    stdio: ["ignore", "pipe", "pipe"]
  });
  return result.status === 0;
}
function escapePowerShellPath(path4) {
  return path4.replace(/'/g, "''");
}
function getWindowsZipExtractor() {
  const buildNumber = getWindowsBuildNumber();
  if (buildNumber !== null && buildNumber >= WINDOWS_BUILD_WITH_TAR) {
    return "tar";
  }
  if (isPwshAvailable()) {
    return "pwsh";
  }
  return "powershell";
}
async function extractZip(archivePath, destDir) {
  let proc;
  if (process.platform === "win32") {
    const extractor = getWindowsZipExtractor();
    switch (extractor) {
      case "tar":
        proc = crossSpawn(["tar", "-xf", archivePath, "-C", destDir], {
          stdout: "ignore",
          stderr: "pipe"
        });
        break;
      case "pwsh":
        proc = crossSpawn([
          "pwsh",
          "-Command",
          `Expand-Archive -Path '${escapePowerShellPath(archivePath)}' -DestinationPath '${escapePowerShellPath(destDir)}' -Force`
        ], {
          stdout: "ignore",
          stderr: "pipe"
        });
        break;
      default:
        proc = crossSpawn([
          "powershell",
          "-Command",
          `Expand-Archive -Path '${escapePowerShellPath(archivePath)}' -DestinationPath '${escapePowerShellPath(destDir)}' -Force`
        ], {
          stdout: "ignore",
          stderr: "pipe"
        });
        break;
    }
  } else {
    proc = crossSpawn(["unzip", "-o", archivePath, "-d", destDir], {
      stdout: "ignore",
      stderr: "pipe"
    });
  }
  const exitCode = await proc.exited;
  if (exitCode !== 0) {
    const stderr = await proc.stderr();
    throw new Error(`zip extraction failed (exit ${exitCode}): ${stderr}`);
  }
}
var WINDOWS_BUILD_WITH_TAR = 17134;
var init_zip_extractor = __esm(() => {
  init_compat();
});

// src/cli/doctor.ts
import * as fs2 from "node:fs";
import { z as z3 } from "zod";

// src/config/loader.ts
import * as fs from "node:fs";
import * as path2 from "node:path";

// src/cli/config-io.ts
import {
  copyFileSync,
  existsSync as existsSync3,
  mkdirSync as mkdirSync2,
  readFileSync,
  renameSync,
  rmSync,
  statSync as statSync2,
  writeFileSync
} from "node:fs";
import { homedir as homedir2 } from "node:os";
import { dirname as dirname2, join as join3 } from "node:path";

// src/plugin-entry.ts
var INSTALLER_MANAGED_PLUGIN_OPTION = "__ohMyOpencodeSlimManagedByInstaller";

// src/cli/config-io.ts
init_compat();

// src/cli/paths.ts
import { existsSync as existsSync2, mkdirSync } from "node:fs";
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
function getConfigJson() {
  return getOpenCodeConfigPaths()[0];
}
function getConfigJsonc() {
  return getOpenCodeConfigPaths()[1];
}
function getLiteConfig() {
  return join2(getConfigDir(), "oh-my-opencode-slim.json");
}
function getLiteConfigJsonc() {
  return join2(getConfigDir(), "oh-my-opencode-slim.jsonc");
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
function getExistingLiteConfigPath() {
  const jsonPath = getLiteConfig();
  if (existsSync2(jsonPath))
    return jsonPath;
  const jsoncPath = getLiteConfigJsonc();
  if (existsSync2(jsoncPath))
    return jsoncPath;
  return jsonPath;
}
function getExistingTuiConfigPath() {
  const customConfigPath = getCustomTuiConfigPath();
  if (customConfigPath)
    return customConfigPath;
  const jsonPath = join2(getConfigDir(), "tui.json");
  if (existsSync2(jsonPath))
    return jsonPath;
  const jsoncPath = getTuiConfigJsonc();
  if (existsSync2(jsoncPath))
    return jsoncPath;
  return jsonPath;
}
function getExistingConfigPath() {
  const jsonPath = getConfigJson();
  if (existsSync2(jsonPath))
    return jsonPath;
  const jsoncPath = getConfigJsonc();
  if (existsSync2(jsoncPath))
    return jsoncPath;
  return jsonPath;
}
function ensureConfigDir() {
  const configDir = getConfigDir();
  if (!existsSync2(configDir)) {
    mkdirSync(configDir, { recursive: true });
  }
}
function ensureTuiConfigDir() {
  const configDir = dirname(getTuiConfig());
  if (!existsSync2(configDir)) {
    mkdirSync(configDir, { recursive: true });
  }
}
function ensureOpenCodeConfigDir() {
  const configDir = dirname(getConfigJson());
  if (!existsSync2(configDir)) {
    mkdirSync(configDir, { recursive: true });
  }
}

// src/config/constants.ts
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
var MAX_POLL_TIME_MS = 5 * 60 * 1000;
var PHASE_REMINDER_TEXT = `!IMPORTANT! Scheduler workflow: First choose the lightest workflow that fits the work. If direct execution is justified, complete it and verify proportionately. Otherwise: plan lanes/dependencies → dispatch background specialists → track task IDs → wait for hook-driven completion → reconcile terminal results → verify. !END!`;
function formatSystemReminder(text) {
  return `<system-reminder>
${text}
</system-reminder>`;
}
var PHASE_REMINDER = formatSystemReminder(PHASE_REMINDER_TEXT);
var DEFAULT_MAX_RETAINED_SNAPSHOTS = 20;

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

// src/cli/providers.ts
var SCHEMA_URL = "https://unpkg.com/oh-my-opencode-slim@latest/oh-my-opencode-slim.schema.json";
var GENERATED_PRESETS = ["openai", "opencode-go"];
var MODEL_MAPPINGS = {
  openai: {
    orchestrator: { model: "openai/gpt-5.6-terra", variant: "high" },
    oracle: { model: "openai/gpt-5.6-sol", variant: "high" },
    librarian: { model: "openai/gpt-5.6-luna", variant: "low" },
    explorer: { model: "openai/gpt-5.6-luna", variant: "low" },
    designer: { model: "openai/gpt-5.6-luna", variant: "medium" },
    fixer: { model: "openai/gpt-5.6-luna", variant: "high" }
  },
  kimi: {
    orchestrator: { model: "kimi-for-coding/k2p5", variant: "max" },
    oracle: { model: "kimi-for-coding/k2p5", variant: "high" },
    librarian: { model: "kimi-for-coding/k2p5", variant: "low" },
    explorer: { model: "kimi-for-coding/k2p5", variant: "low" },
    designer: { model: "kimi-for-coding/k2p5", variant: "medium" },
    fixer: { model: "kimi-for-coding/k2p5", variant: "low" }
  },
  copilot: {
    orchestrator: { model: "github-copilot/claude-opus-4.6", variant: "max" },
    oracle: { model: "github-copilot/claude-opus-4.6", variant: "high" },
    librarian: { model: "github-copilot/grok-code-fast-1", variant: "low" },
    explorer: { model: "github-copilot/grok-code-fast-1", variant: "low" },
    designer: {
      model: "github-copilot/gemini-3.1-pro-preview",
      variant: "medium"
    },
    fixer: { model: "github-copilot/claude-sonnet-4.6", variant: "low" }
  },
  "zai-plan": {
    orchestrator: { model: "zai-coding-plan/glm-5", variant: "max" },
    oracle: { model: "zai-coding-plan/glm-5", variant: "high" },
    librarian: { model: "zai-coding-plan/glm-5", variant: "low" },
    explorer: { model: "zai-coding-plan/glm-5", variant: "low" },
    designer: { model: "zai-coding-plan/glm-5", variant: "medium" },
    fixer: { model: "zai-coding-plan/glm-5", variant: "low" }
  },
  "opencode-go": {
    orchestrator: { model: "opencode-go/minimax-m3", variant: "thinking" },
    oracle: { model: "opencode-go/qwen3.7-max", variant: "max" },
    explorer: { model: "opencode-go/deepseek-v4-flash", variant: "high" },
    librarian: { model: "opencode-go/deepseek-v4-flash", variant: "high" },
    designer: { model: "opencode-go/kimi-k2.7-code" },
    fixer: { model: "opencode-go/deepseek-v4-flash", variant: "high" },
    observer: { model: "opencode-go/mimo-v2.5" }
  }
};
function isGeneratedPresetName(value) {
  return GENERATED_PRESETS.includes(value);
}
function getGeneratedPresetNames() {
  return [...GENERATED_PRESETS];
}
function generateLiteConfig(installConfig) {
  const preset = installConfig.preset ?? "openai";
  if (!isGeneratedPresetName(preset)) {
    throw new Error(`Unsupported preset "${preset}". Available generated presets: ${getGeneratedPresetNames().join(", ")}`);
  }
  const config = {
    $schema: SCHEMA_URL,
    preset,
    presets: {}
  };
  if (preset === "opencode-go") {
    config.disabled_agents = [];
  }
  const createAgentConfig = (agentName, modelInfo) => {
    const isOrchestrator = agentName === "orchestrator";
    const skills = isOrchestrator ? ["*"] : [
      ...CUSTOM_SKILLS.filter((s) => s.allowedAgents.includes("*") || s.allowedAgents.includes(agentName)).map((s) => s.name)
    ];
    return {
      model: modelInfo.model,
      variant: modelInfo.variant,
      skills,
      mcps: DEFAULT_AGENT_MCPS[agentName] ?? []
    };
  };
  const buildPreset = (mappingName) => {
    const mapping = MODEL_MAPPINGS[mappingName];
    return Object.fromEntries(Object.entries(mapping).map(([agentName, modelInfo]) => [
      agentName,
      createAgentConfig(agentName, modelInfo)
    ]));
  };
  const presets = config.presets;
  for (const presetName of GENERATED_PRESETS) {
    presets[presetName] = buildPreset(presetName);
  }
  if (installConfig.companion === "yes") {
    config.companion = {
      enabled: true,
      position: "bottom-right",
      size: "medium",
      gifPack: "default",
      loopStyle: "classic",
      speed: 1,
      debug: false
    };
  }
  return config;
}

// src/cli/config-io.ts
var PACKAGE_NAME = "oh-my-opencode-slim";
var DEFAULT_OPENCODE_AGENTS_TO_DISABLE = ["explore", "general"];
function isString(value) {
  return typeof value === "string";
}
function getModelIds(model) {
  if (isString(model))
    return [model];
  if (!Array.isArray(model))
    return [];
  return model.flatMap((entry) => {
    if (isString(entry))
      return [entry];
    if (entry && typeof entry === "object" && isString(entry.id)) {
      return [entry.id];
    }
    return [];
  });
}
function getPlugins(config) {
  return Array.isArray(config.plugin) ? config.plugin : [];
}
function getPluginSpec(entry) {
  if (isString(entry))
    return entry;
  if (!Array.isArray(entry))
    return;
  const spec = entry[0];
  return isString(spec) ? spec : undefined;
}
function normalizePathForMatch(path2) {
  return path2.replaceAll("\\", "/");
}
function findPackageRoot(startPath) {
  let currentPath = dirname2(startPath);
  while (true) {
    const packageJsonPath = join3(currentPath, "package.json");
    if (existsSync3(packageJsonPath)) {
      try {
        const packageJson = JSON.parse(readFileSync(packageJsonPath, "utf-8"));
        if (packageJson.name === PACKAGE_NAME) {
          return currentPath;
        }
      } catch {}
    }
    const parentPath = dirname2(currentPath);
    if (parentPath === currentPath) {
      return null;
    }
    currentPath = parentPath;
  }
}
function isLocalPackageRootEntry(entry) {
  if (!entry || entry.startsWith("file://")) {
    return false;
  }
  const packageJsonPath = join3(entry, "package.json");
  if (!existsSync3(packageJsonPath)) {
    return false;
  }
  try {
    const packageJson = JSON.parse(readFileSync(packageJsonPath, "utf-8"));
    return packageJson.name === PACKAGE_NAME;
  } catch {
    return false;
  }
}
function isPackageManagerInstall(path2) {
  const normalizedPath = normalizePathForMatch(path2);
  return normalizedPath.includes(`/node_modules/${PACKAGE_NAME}`);
}
function isPluginEntry(entry) {
  return entry === PACKAGE_NAME || entry.startsWith(`${PACKAGE_NAME}@`) || entry.startsWith("file://") && entry.includes(PACKAGE_NAME) || isLocalPackageRootEntry(entry);
}
function isMatchingPluginEntry(entry) {
  const spec = getPluginSpec(entry);
  return spec ? isPluginEntry(spec) : false;
}
function getPluginEntry() {
  const cliEntryPath = process.argv[1];
  if (!cliEntryPath) {
    return PACKAGE_NAME;
  }
  try {
    const packageRoot = findPackageRoot(cliEntryPath);
    if (!packageRoot) {
      return PACKAGE_NAME;
    }
    if (isPackageManagerInstall(packageRoot)) {
      const version = getVersionFromPackageRoot(packageRoot);
      const requestedTag = getRequestedPackageTag(packageRoot);
      if (!version || !requestedTag || requestedTag === "latest") {
        return PACKAGE_NAME;
      }
      return [
        `${PACKAGE_NAME}@${version}`,
        { [INSTALLER_MANAGED_PLUGIN_OPTION]: true }
      ];
    }
    return packageRoot;
  } catch {
    return PACKAGE_NAME;
  }
}
function getConfiguredExactVersion() {
  try {
    const { config } = parseConfig(getExistingConfigPath());
    if (!config)
      return;
    let version;
    for (const entry of getPlugins(config)) {
      const spec = getPluginSpec(entry);
      if (!spec)
        continue;
      if (spec === PACKAGE_NAME) {
        version = undefined;
      } else if (spec.startsWith(`${PACKAGE_NAME}@`)) {
        const candidate = spec.slice(PACKAGE_NAME.length + 1);
        version = candidate && candidate !== "latest" ? candidate : undefined;
      }
    }
    return version;
  } catch {}
  return;
}
function getRequestedPackageTag(packageRoot) {
  const normalizedPath = normalizePathForMatch(packageRoot);
  const marker = `/bunx-`;
  const markerIndex = normalizedPath.lastIndexOf(marker);
  if (markerIndex === -1)
    return;
  const bunxSegment = normalizedPath.slice(markerIndex + marker.length).split("/")[0];
  const packagePrefix = `${PACKAGE_NAME}@`;
  const packageIndex = bunxSegment.lastIndexOf(packagePrefix);
  if (packageIndex === -1)
    return;
  const tag = bunxSegment.slice(packageIndex + packagePrefix.length);
  return tag || undefined;
}
function getVersionFromPackageRoot(packageRoot) {
  try {
    const packageJsonPath = join3(packageRoot, "package.json");
    if (!existsSync3(packageJsonPath))
      return;
    const pkg = JSON.parse(readFileSync(packageJsonPath, "utf-8"));
    return pkg.version;
  } catch {
    return;
  }
}
function getOpenCodePluginCacheDir(version) {
  const cacheDir = process.env.XDG_CACHE_HOME?.trim() || join3(homedir2(), ".cache");
  const suffix = version ? `${PACKAGE_NAME}@${version}` : `${PACKAGE_NAME}@latest`;
  return join3(cacheDir, "opencode", "packages", suffix);
}
function writeOpenCodePluginCacheManifest(cacheDir, version = "latest") {
  try {
    writeFileSync(join3(cacheDir, "package.json"), JSON.stringify({
      name: `${PACKAGE_NAME}-cache`,
      private: true,
      dependencies: {
        [PACKAGE_NAME]: version
      }
    }, null, 2));
    return null;
  } catch (err) {
    return {
      success: false,
      configPath: cacheDir,
      error: `Failed to write cache package.json: ${err}`
    };
  }
}
function removeOpenCodePluginCacheArtifacts(cacheDir) {
  rmSync(join3(cacheDir, "node_modules", PACKAGE_NAME), {
    recursive: true,
    force: true
  });
  rmSync(join3(cacheDir, "bun.lock"), { force: true });
  rmSync(join3(cacheDir, "bun.lockb"), { force: true });
}
function verifyOpenCodePluginCache(cacheDir) {
  const pluginPackageJsonPath = join3(cacheDir, "node_modules", PACKAGE_NAME, "package.json");
  if (!existsSync3(pluginPackageJsonPath)) {
    return {
      success: false,
      configPath: cacheDir,
      error: `Cached plugin package not found at ${pluginPackageJsonPath}`
    };
  }
  try {
    const packageJson = JSON.parse(readFileSync(pluginPackageJsonPath, "utf-8"));
    if (packageJson.name !== PACKAGE_NAME) {
      return {
        success: false,
        configPath: cacheDir,
        error: `Cached plugin package has unexpected name: ${packageJson.name}`
      };
    }
  } catch (err) {
    return {
      success: false,
      configPath: cacheDir,
      error: `Failed to verify cached plugin package: ${err}`
    };
  }
  return null;
}
async function warmOpenCodePluginCache() {
  const cliEntryPath = process.argv[1];
  if (!cliEntryPath) {
    return null;
  }
  const packageRoot = findPackageRoot(cliEntryPath);
  if (!packageRoot || !isPackageManagerInstall(packageRoot)) {
    return null;
  }
  const configuredVersion = getConfiguredExactVersion();
  const runningVersion = getVersionFromPackageRoot(packageRoot);
  const requestedTag = getRequestedPackageTag(packageRoot);
  const cacheVersion = configuredVersion ?? requestedTag ?? runningVersion;
  const cacheDir = getOpenCodePluginCacheDir(cacheVersion);
  try {
    mkdirSync2(cacheDir, { recursive: true });
  } catch (err) {
    return {
      success: false,
      configPath: cacheDir,
      error: `Failed to create OpenCode cache directory: ${err}`
    };
  }
  const manifestError = writeOpenCodePluginCacheManifest(cacheDir, cacheVersion);
  if (manifestError)
    return manifestError;
  removeOpenCodePluginCacheArtifacts(cacheDir);
  try {
    const proc = crossSpawn(["bun", "install", "--ignore-scripts"], {
      cwd: cacheDir,
      stdout: "pipe",
      stderr: "pipe"
    });
    await proc.exited;
    if (proc.exitCode !== 0) {
      const stderr = (await proc.stderr()).trim();
      return {
        success: false,
        configPath: cacheDir,
        error: stderr || `bun install exited with code ${proc.exitCode}`
      };
    }
    const verificationError = verifyOpenCodePluginCache(cacheDir);
    if (verificationError)
      return verificationError;
    return { success: true, configPath: cacheDir };
  } catch (err) {
    return {
      success: false,
      configPath: cacheDir,
      error: `Failed to warm OpenCode cache: ${err}`
    };
  }
}
function stripJsonComments(json) {
  const commentPattern = /\\"|"(?:\\"|[^"])*"|(\/\/.*|\/\*[\s\S]*?\*\/)/g;
  const trailingCommaPattern = /\\"|"(?:\\"|[^"])*"|(,)(\s*[}\]])/g;
  return json.replace(commentPattern, (match, commentGroup) => commentGroup ? "" : match).replace(trailingCommaPattern, (match, comma, closing) => comma ? closing : match);
}
function parseConfigFile(path2) {
  try {
    if (!existsSync3(path2))
      return { config: null };
    const stat = statSync2(path2);
    if (stat.size === 0)
      return { config: null };
    const content = readFileSync(path2, "utf-8").replace(/^\uFEFF/, "");
    if (content.trim().length === 0)
      return { config: null };
    return { config: JSON.parse(stripJsonComments(content)) };
  } catch (err) {
    return { config: null, error: String(err) };
  }
}
function parseConfig(path2) {
  const result = parseConfigFile(path2);
  if (result.config || result.error)
    return result;
  if (path2.endsWith(".json")) {
    const jsoncPath = path2.replace(/\.json$/, ".jsonc");
    return parseConfigFile(jsoncPath);
  }
  return { config: null };
}
function writeConfig(configPath, config) {
  if (configPath.endsWith(".jsonc")) {
    console.warn("[config-manager] Writing to .jsonc file - comments will not be preserved");
  }
  const tmpPath = `${configPath}.tmp`;
  const bakPath = `${configPath}.bak`;
  const content = `${JSON.stringify(config, null, 2)}
`;
  if (existsSync3(configPath)) {
    copyFileSync(configPath, bakPath);
  }
  writeFileSync(tmpPath, content);
  renameSync(tmpPath, configPath);
}
async function addPluginToOpenCodeConfig() {
  const configPath = getExistingConfigPath();
  try {
    ensureOpenCodeConfigDir();
  } catch (err) {
    return {
      success: false,
      configPath,
      error: `Failed to create config directory: ${err}`
    };
  }
  try {
    const { config: parsedConfig, error } = parseConfig(configPath);
    if (error) {
      return {
        success: false,
        configPath,
        error: `Failed to parse config: ${error}`
      };
    }
    const config = parsedConfig ?? {};
    const plugins = getPlugins(config);
    const pluginEntry = getPluginEntry();
    const filteredPlugins = plugins.filter((plugin) => !isMatchingPluginEntry(plugin));
    filteredPlugins.push(pluginEntry);
    config.plugin = filteredPlugins;
    writeConfig(configPath, config);
    return { success: true, configPath };
  } catch (err) {
    return {
      success: false,
      configPath,
      error: `Failed to update opencode config: ${err}`
    };
  }
}
async function addPluginToOpenCodeTuiConfig() {
  const configPath = getExistingTuiConfigPath();
  try {
    ensureTuiConfigDir();
  } catch (err) {
    return {
      success: false,
      configPath,
      error: `Failed to create config directory: ${err}`
    };
  }
  try {
    const { config: parsedConfig, error } = parseConfig(configPath);
    if (error) {
      return {
        success: false,
        configPath,
        error: `Failed to parse TUI config: ${error}`
      };
    }
    const config = parsedConfig ?? {};
    const plugins = getPlugins(config);
    const pluginEntry = getPluginEntry();
    const filteredPlugins = plugins.filter((plugin) => !isMatchingPluginEntry(plugin));
    filteredPlugins.push(pluginEntry);
    config.plugin = filteredPlugins;
    writeConfig(configPath, config);
    return { success: true, configPath };
  } catch (err) {
    return {
      success: false,
      configPath,
      error: `Failed to update opencode TUI config: ${err}`
    };
  }
}
function writeLiteConfig(installConfig, targetPath) {
  const configPath = targetPath ?? getLiteConfig();
  try {
    ensureConfigDir();
    const config = generateLiteConfig(installConfig);
    const tmpPath = `${configPath}.tmp`;
    const bakPath = `${configPath}.bak`;
    const content = `${JSON.stringify(config, null, 2)}
`;
    if (existsSync3(configPath)) {
      copyFileSync(configPath, bakPath);
    }
    writeFileSync(tmpPath, content);
    renameSync(tmpPath, configPath);
    return { success: true, configPath };
  } catch (err) {
    return {
      success: false,
      configPath,
      error: `Failed to write lite config: ${err}`
    };
  }
}
function disableDefaultAgents() {
  const configPath = getExistingConfigPath();
  try {
    ensureOpenCodeConfigDir();
    const { config: parsedConfig, error } = parseConfig(configPath);
    if (error) {
      return {
        success: false,
        configPath,
        error: `Failed to parse config: ${error}`
      };
    }
    const config = parsedConfig ?? {};
    const agent = config.agent ?? {};
    for (const agentName of DEFAULT_OPENCODE_AGENTS_TO_DISABLE) {
      const existing = agent[agentName];
      agent[agentName] = {
        ...existing && typeof existing === "object" && !Array.isArray(existing) ? existing : {},
        disable: true
      };
    }
    config.agent = agent;
    writeConfig(configPath, config);
    return { success: true, configPath };
  } catch (err) {
    return {
      success: false,
      configPath,
      error: `Failed to disable default agents: ${err}`
    };
  }
}
function enableLspByDefault() {
  const configPath = getExistingConfigPath();
  try {
    ensureOpenCodeConfigDir();
    const { config: parsedConfig, error } = parseConfig(configPath);
    if (error) {
      return {
        success: false,
        configPath,
        error: `Failed to parse config: ${error}`
      };
    }
    const config = parsedConfig ?? {};
    if (config.lsp === undefined) {
      config.lsp = true;
      writeConfig(configPath, config);
    }
    return { success: true, configPath };
  } catch (err) {
    return {
      success: false,
      configPath,
      error: `Failed to enable LSP: ${err}`
    };
  }
}
function detectCurrentConfig() {
  const result = {
    isInstalled: false,
    hasKimi: false,
    hasOpenAI: false,
    hasAnthropic: false,
    hasCopilot: false,
    hasZaiPlan: false,
    hasAntigravity: false,
    hasChutes: false,
    hasOpencodeZen: false
  };
  const { config } = parseConfig(getExistingConfigPath());
  if (!config)
    return result;
  const plugins = getPlugins(config);
  result.isInstalled = plugins.some((p) => isMatchingPluginEntry(p));
  result.hasAntigravity = plugins.some((p) => {
    const spec = getPluginSpec(p);
    return spec?.startsWith("opencode-antigravity-auth") ?? false;
  });
  const providers = config.provider;
  result.hasKimi = !!providers?.kimi;
  result.hasAnthropic = !!providers?.anthropic;
  result.hasCopilot = !!providers?.["github-copilot"];
  result.hasZaiPlan = !!providers?.["zai-coding-plan"];
  result.hasChutes = !!providers?.chutes;
  if (providers?.google)
    result.hasAntigravity = true;
  const { config: liteConfig } = parseConfig(getLiteConfig());
  if (liteConfig && typeof liteConfig === "object") {
    const configObj = liteConfig;
    const presetName = configObj.preset;
    const presets = configObj.presets;
    const agents = presets?.[presetName];
    if (agents && typeof agents === "object") {
      const models = Object.values(agents).filter((a) => a && typeof a === "object").flatMap((a) => getModelIds(a.model));
      result.hasOpenAI ||= models.some((m) => m.startsWith("openai/"));
      result.hasAnthropic ||= models.some((m) => m.startsWith("anthropic/"));
      result.hasCopilot ||= models.some((m) => m.startsWith("github-copilot/"));
      result.hasZaiPlan ||= models.some((m) => m.startsWith("zai-coding-plan/"));
      result.hasOpencodeZen ||= models.some((m) => m.startsWith("opencode/"));
      if (models.some((m) => m.startsWith("google/"))) {
        result.hasAntigravity = true;
      }
      if (models.some((m) => m.startsWith("chutes/"))) {
        result.hasChutes = true;
      }
    }
  }
  return result;
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

// src/cli/doctor.ts
function parseDoctorArgs(args) {
  const result = {};
  for (const arg of args) {
    if (arg === "--json") {
      result.json = true;
    } else if (arg === "--help" || arg === "-h") {
      result.help = true;
    } else {
      result.error ??= `Unknown doctor option: ${arg}`;
    }
  }
  return result;
}
function checkConfigFile(scope, configPath) {
  if (configPath === null) {
    return { scope, path: null, exists: false, ok: true };
  }
  try {
    const stat = fs2.statSync(configPath);
    if (stat.size === 0) {
      return {
        scope,
        path: configPath,
        exists: true,
        ok: false,
        error: {
          kind: "invalid-json",
          message: "Empty file is not valid JSON"
        }
      };
    }
    const content = fs2.readFileSync(configPath, "utf-8").replace(/^\uFEFF/, "");
    const rawConfig = JSON.parse(stripJsonComments(content));
    normalizeDisabledArrayKeys(rawConfig, (message) => {
      console.warn(`[oh-my-opencode-slim] ${message}`);
    });
    const parseResult = PluginConfigSchema.safeParse(rawConfig);
    if (!parseResult.success) {
      return {
        scope,
        path: configPath,
        exists: true,
        ok: false,
        error: {
          kind: "invalid-schema",
          message: z3.prettifyError(parseResult.error),
          issues: parseResult.error.issues
        }
      };
    }
    return {
      scope,
      path: configPath,
      exists: true,
      ok: true,
      config: parseResult.data
    };
  } catch (err) {
    if (err instanceof SyntaxError) {
      return {
        scope,
        path: configPath,
        exists: true,
        ok: false,
        error: {
          kind: "invalid-json",
          message: err.message
        }
      };
    } else if (err instanceof Error && "code" in err && err.code === "ENOENT") {
      return {
        scope,
        path: configPath,
        exists: false,
        ok: false,
        error: {
          kind: "read-error",
          message: "File was not found while reading"
        }
      };
    }
    return {
      scope,
      path: configPath,
      exists: true,
      ok: false,
      error: {
        kind: "read-error",
        message: err instanceof Error ? err.message : String(err)
      }
    };
  }
}
function checkPreset(mergedConfig) {
  const envPreset = process.env.OH_MY_OPENCODE_SLIM_PRESET;
  const presetName = envPreset || mergedConfig.preset;
  if (presetName === undefined) {
    return;
  }
  if (!mergedConfig.presets?.[presetName]) {
    return {
      preset: presetName,
      ok: false,
      error: {
        kind: "missing-preset",
        message: `Preset "${presetName}" not found in config`
      }
    };
  }
  return { preset: presetName, ok: true };
}
function getMergedConfig(userConfig, projectConfig) {
  return projectConfig ? mergePluginConfigs(userConfig ?? {}, projectConfig) : userConfig ?? {};
}
function runDoctorCheck(cwd) {
  const { userConfigPath, projectConfigPath } = findPluginConfigPaths(cwd);
  const userCheck = checkConfigFile("user", userConfigPath);
  const projectCheck = checkConfigFile("project", projectConfigPath);
  const configs = [userCheck, projectCheck];
  const hasInvalidConfig = configs.some((c) => !c.ok);
  let presetCheckResult;
  if (!hasInvalidConfig) {
    const mergedConfig = getMergedConfig(userCheck.config, projectCheck.config);
    presetCheckResult = checkPreset(mergedConfig);
  }
  return {
    ok: configs.every((c) => c.ok) && (!presetCheckResult || presetCheckResult.ok),
    project: cwd,
    configs,
    presetCheck: presetCheckResult
  };
}
function formatHumanDoctorResult(result) {
  const lines = [];
  lines.push(`Project: ${result.project}`);
  lines.push("");
  for (const config of result.configs) {
    if (config.path === null) {
      lines.push(`[${config.scope}] No config file found`);
    } else {
      const status = config.ok ? "✓" : "✗";
      lines.push(`[${config.scope}] ${config.path} ${status}`);
      if (!config.ok && config.error) {
        if (config.error.kind === "invalid-json") {
          lines.push(`  Invalid JSON: ${config.error.message}`);
        } else if (config.error.kind === "invalid-schema") {
          lines.push("  Schema error:");
          for (const line of config.error.message.split(`
`)) {
            lines.push(`  ${line}`);
          }
        } else if (config.error.kind === "read-error") {
          lines.push(`  Read error: ${config.error.message}`);
        }
      }
    }
  }
  if (result.presetCheck) {
    lines.push("");
    const status = result.presetCheck.ok ? "✓" : "✗";
    lines.push(`[preset] ${result.presetCheck.preset} ${status}`);
    if (result.presetCheck.error) {
      lines.push(`  ${result.presetCheck.error.message}`);
    }
  }
  return lines.join(`
`);
}
function formatJsonDoctorResult(result) {
  return JSON.stringify({
    ...result,
    configs: result.configs.map(({ config: _config, ...config }) => config)
  }, null, 2);
}
async function doctor(args) {
  if (args.help) {
    console.log(`Usage: oh-my-opencode-slim doctor [OPTIONS]

Options:
  --json              Print diagnostics as JSON
  -h, --help          Show this help message`);
    return 0;
  }
  if (args.error) {
    console.error(args.error);
    return 1;
  }
  const result = runDoctorCheck(process.cwd());
  if (args.json) {
    console.log(formatJsonDoctorResult(result));
  } else {
    console.log(formatHumanDoctorResult(result));
  }
  return result.ok ? 0 : 1;
}

// src/cli/install.ts
import { existsSync as existsSync8 } from "node:fs";
import { createInterface } from "node:readline/promises";
import { fileURLToPath } from "node:url";

// src/hooks/auto-update-checker/skill-sync.ts
import * as crypto from "node:crypto";
import {
  copyFileSync as copyFileSync2,
  existsSync as existsSync5,
  lstatSync,
  mkdirSync as mkdirSync3,
  readdirSync as readdirSync2,
  readFileSync as readFileSync4,
  renameSync as renameSync2,
  rmSync as rmSync2,
  unlinkSync,
  writeFileSync as writeFileSync2
} from "node:fs";
import * as os from "node:os";
import * as path3 from "node:path";

// src/utils/logger.ts
import { appendFile } from "node:fs/promises";
var RETENTION_MS = 7 * 24 * 60 * 60 * 1000;
var FALLBACK_WARNING = "[oh-my-opencode-slim] file logging unavailable, falling back to stderr";
var loggerGeneration = 0;
var currentSink = { kind: "uninitialized" };
var writeChain = Promise.resolve();
function safeStderr(message) {
  try {
    console.error(message);
  } catch {}
}
function enterStderrFallback(expectedGeneration) {
  if (expectedGeneration !== loggerGeneration)
    return;
  if (currentSink.kind === "stderr")
    return;
  currentSink = { kind: "stderr" };
  safeStderr(FALLBACK_WARNING);
}
function handleAppendFailure(failedGeneration, logEntry) {
  enterStderrFallback(failedGeneration);
  safeStderr(logEntry.trimEnd());
}
function log(message, data) {
  try {
    const sink = currentSink;
    const entryGeneration = loggerGeneration;
    if (sink.kind === "uninitialized")
      return;
    const timestamp = new Date().toISOString();
    let dataStr = "";
    if (data !== undefined) {
      try {
        dataStr = JSON.stringify(data);
      } catch {
        dataStr = "[unserializable]";
      }
    }
    const logEntry = `[${timestamp}] ${message} ${dataStr}
`;
    if (sink.kind === "stderr") {
      safeStderr(logEntry.trimEnd());
      return;
    }
    const filePath = sink.filePath;
    writeChain = writeChain.catch(() => {
      return;
    }).then(async () => {
      if (entryGeneration === loggerGeneration && currentSink.kind === "stderr") {
        safeStderr(logEntry.trimEnd());
        return;
      }
      try {
        await appendFile(filePath, logEntry);
      } catch {
        handleAppendFailure(entryGeneration, logEntry);
      }
    }).catch(() => {
      return;
    });
  } catch {}
}

// src/hooks/auto-update-checker/skill-sync.ts
var localProcessToken = globalThis.OMO_SKILL_SYNC_PROCESS_TOKEN;
if (!localProcessToken) {
  localProcessToken = crypto.randomUUID();
  globalThis.OMO_SKILL_SYNC_PROCESS_TOKEN = localProcessToken;
}
var PROCESS_TOKEN = localProcessToken;
var ACQUIRED_LOCKS = new Set;
var LEGACY_MANAGED_SKILL_HASHES = {};
function validateManifest(data) {
  if (typeof data !== "object" || data === null)
    return false;
  const d = data;
  if (d.schemaVersion !== 1)
    return false;
  if (typeof d.skills !== "object" || d.skills === null)
    return false;
  const allowedStatuses = new Set([
    "managed",
    "customized",
    "deleted",
    "conflict"
  ]);
  const skillsObj = d.skills;
  for (const key of Object.keys(skillsObj)) {
    const entry = skillsObj[key];
    if (typeof entry !== "object" || entry === null)
      return false;
    if (typeof entry.status !== "string" || !allowedStatuses.has(entry.status))
      return false;
    if (typeof entry.packageVersion !== "string")
      return false;
    if (typeof entry.sourceHash !== "string")
      return false;
    if (typeof entry.lastManagedHash !== "string")
      return false;
    if (typeof entry.lastSeenHash !== "string")
      return false;
    if (entry.stagedPath !== undefined && typeof entry.stagedPath !== "string")
      return false;
    if (typeof entry.updatedAt !== "string")
      return false;
  }
  return true;
}
function copyDirRecursive(src, dest) {
  const stat = lstatSync(src);
  if (stat.isSymbolicLink()) {
    return;
  }
  if (stat.isDirectory()) {
    mkdirSync3(dest, { recursive: true });
    const entries = readdirSync2(src);
    for (const entry of entries) {
      copyDirRecursive(path3.join(src, entry), path3.join(dest, entry));
    }
  } else if (stat.isFile()) {
    const destDir = path3.dirname(dest);
    if (!existsSync5(destDir)) {
      mkdirSync3(destDir, { recursive: true });
    }
    copyFileSync2(src, dest);
  }
}
function computeDirectoryHash(dirPath) {
  const hash = crypto.createHash("sha256");
  const entriesToHash = [];
  function traverse(currentDir) {
    const entries = readdirSync2(currentDir);
    for (const entry of entries) {
      const absolutePath = path3.join(currentDir, entry);
      const stat = lstatSync(absolutePath);
      const relativePath = path3.relative(dirPath, absolutePath);
      if (stat.isSymbolicLink()) {
        continue;
      }
      if (stat.isDirectory()) {
        entriesToHash.push({
          relativePath,
          absolutePath,
          kind: "directory",
          mode: stat.mode
        });
        traverse(absolutePath);
      } else if (stat.isFile()) {
        entriesToHash.push({
          relativePath,
          absolutePath,
          kind: "file",
          mode: stat.mode
        });
      }
    }
  }
  traverse(dirPath);
  entriesToHash.sort((a, b) => {
    if (a.relativePath < b.relativePath)
      return -1;
    if (a.relativePath > b.relativePath)
      return 1;
    return 0;
  });
  for (const entry of entriesToHash) {
    hash.update(entry.kind);
    hash.update("\x00");
    hash.update(entry.relativePath);
    hash.update("\x00");
    hash.update(String(entry.mode & 4095));
    hash.update("\x00");
    if (entry.kind === "file") {
      const content = readFileSync4(entry.absolutePath);
      hash.update(content);
    }
  }
  return hash.digest("hex");
}
function isPidRunning(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (err) {
    return err.code === "EPERM";
  }
}
var CROSS_HOST_LOCK_EXPIRY_MS = 5 * 60 * 1000;
function acquireLock(lockDir) {
  const metadataPath = path3.join(lockDir, "owner.json");
  const currentHost = os.hostname();
  const currentPid = process.pid;
  const writeMetadata = () => {
    try {
      const metadata = {
        pid: currentPid,
        host: currentHost,
        time: Date.now(),
        token: PROCESS_TOKEN
      };
      writeFileSync2(metadataPath, JSON.stringify(metadata), "utf-8");
    } catch {}
  };
  try {
    mkdirSync3(lockDir);
    writeMetadata();
    ACQUIRED_LOCKS.add(path3.resolve(lockDir));
    return true;
  } catch (err) {
    if (err.code !== "EEXIST") {
      throw err;
    }
  }
  try {
    let shouldSteal = false;
    let ageMs = 0;
    if (existsSync5(metadataPath)) {
      try {
        const content = readFileSync4(metadataPath, "utf-8");
        const metadata = JSON.parse(content);
        ageMs = Date.now() - metadata.time;
        if (metadata.host === currentHost) {
          if (!isPidRunning(metadata.pid)) {
            log(`[skill-sync] Lock owner process ${metadata.pid} is not running on this host. Recovery path.`);
            shouldSteal = true;
          }
        } else {
          if (ageMs > CROSS_HOST_LOCK_EXPIRY_MS) {
            log(`[skill-sync] Lock owned by different host ${metadata.host} has expired (${Math.round(ageMs / 1000)}s old). Reclaiming lock.`);
            shouldSteal = true;
          } else {
            log(`[skill-sync] Lock is owned by different host ${metadata.host}; failing closed.`);
          }
        }
      } catch {
        shouldSteal = true;
      }
    } else {
      const stat = lstatSync(lockDir);
      ageMs = Date.now() - stat.mtimeMs;
      if (ageMs > 30000) {
        shouldSteal = true;
      }
    }
    if (!shouldSteal)
      return false;
    log(`[skill-sync] Stealing/recovering lock directory.`);
    rmSync2(lockDir, { recursive: true, force: true });
    mkdirSync3(lockDir);
    writeMetadata();
    ACQUIRED_LOCKS.add(path3.resolve(lockDir));
    return true;
  } catch (err) {
    log(`[skill-sync] Failed to check/recover lock at ${lockDir}:`, err);
    return false;
  }
}
function releaseLock(lockDir) {
  const resolvedPath = path3.resolve(lockDir);
  try {
    let isOurLock = false;
    const metadataPath = path3.join(lockDir, "owner.json");
    if (existsSync5(metadataPath)) {
      try {
        const content = readFileSync4(metadataPath, "utf-8");
        const metadata = JSON.parse(content);
        if (metadata.host === os.hostname() && metadata.pid === process.pid && metadata.token === PROCESS_TOKEN) {
          isOurLock = true;
        } else {
          isOurLock = false;
        }
      } catch (err) {
        log(`[skill-sync] Lock owner.json is unreadable/corrupt:`, err);
        isOurLock = false;
      }
    } else if (ACQUIRED_LOCKS.has(resolvedPath)) {
      isOurLock = true;
    }
    if (isOurLock) {
      if (existsSync5(lockDir)) {
        rmSync2(lockDir, { recursive: true, force: true });
      }
    } else if (existsSync5(lockDir)) {
      log(`[skill-sync] Skipping lock directory removal: lock is not owned by this process/token or owner.json check failed.`);
    }
  } catch (err) {
    log(`[skill-sync] Failed to release lock at ${lockDir}:`, err);
  } finally {
    ACQUIRED_LOCKS.delete(resolvedPath);
  }
}
function atomicReplaceDir(sourceDir, destDir) {
  const parentDir = path3.dirname(destDir);
  if (!existsSync5(parentDir)) {
    mkdirSync3(parentDir, { recursive: true });
  }
  const uniqueSuffix = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
  const stagingDir = path3.join(parentDir, `.staging-${path3.basename(destDir)}-${uniqueSuffix}`);
  const backupDir = path3.join(parentDir, `.backup-${path3.basename(destDir)}-${uniqueSuffix}`);
  let backupCreated = false;
  try {
    copyDirRecursive(sourceDir, stagingDir);
    if (existsSync5(destDir)) {
      renameSync2(destDir, backupDir);
      backupCreated = true;
    }
    renameSync2(stagingDir, destDir);
    if (backupCreated) {
      rmSync2(backupDir, { recursive: true, force: true });
    }
  } catch (err) {
    log(`[skill-sync] Error during atomic replace for ${destDir}. Rolling back:`, err);
    if (backupCreated) {
      try {
        if (existsSync5(destDir)) {
          rmSync2(destDir, { recursive: true, force: true });
        }
        renameSync2(backupDir, destDir);
      } catch (rollbackErr) {
        log(`[skill-sync] Critical error during rollback for ${destDir}:`, rollbackErr);
      }
    }
    try {
      if (existsSync5(stagingDir)) {
        rmSync2(stagingDir, { recursive: true, force: true });
      }
    } catch {}
    throw err;
  }
}
function matchesArtifactPattern(entry, prefix, skillName) {
  if (!entry.startsWith(prefix))
    return false;
  const rest = entry.slice(prefix.length);
  if (!rest.startsWith(`${skillName}-`))
    return false;
  const suffix = rest.slice(skillName.length + 1);
  const firstPart = suffix.split("-")[0];
  const timestamp = Number(firstPart);
  if (Number.isNaN(timestamp) || timestamp <= 0)
    return false;
  return true;
}
function recoverOrphanArtifacts(destSkillsDir, skillName) {
  if (!existsSync5(destSkillsDir))
    return false;
  let hadArtifacts = false;
  let entries = [];
  try {
    entries = readdirSync2(destSkillsDir);
  } catch {
    return false;
  }
  const backups = [];
  const stagings = [];
  for (const entry of entries) {
    if (matchesArtifactPattern(entry, ".backup-", skillName)) {
      backups.push(path3.join(destSkillsDir, entry));
      hadArtifacts = true;
    } else if (matchesArtifactPattern(entry, ".staging-", skillName)) {
      stagings.push(path3.join(destSkillsDir, entry));
      hadArtifacts = true;
    }
  }
  const destPath = path3.join(destSkillsDir, skillName);
  if (backups.length > 0) {
    backups.sort();
    const mostRecentBackup = backups[backups.length - 1];
    if (!existsSync5(destPath)) {
      backups.pop();
      try {
        renameSync2(mostRecentBackup, destPath);
        log(`[skill-sync] Recovered backup for ${skillName} back to destination.`);
      } catch (err) {
        log(`[skill-sync] Failed to restore backup for ${skillName}:`, err);
      }
    }
    for (const backup of backups) {
      try {
        rmSync2(backup, { recursive: true, force: true });
      } catch (err) {
        log(`[skill-sync] Failed to clean up backup folder ${backup}:`, err);
      }
    }
  }
  for (const staging of stagings) {
    try {
      rmSync2(staging, { recursive: true, force: true });
    } catch (err) {
      log(`[skill-sync] Failed to clean up staging folder ${staging}:`, err);
    }
  }
  return hadArtifacts;
}
function removeManagedStagedPath(stagedPath, manifestDir, skillName) {
  try {
    const absoluteStagedPath = path3.resolve(stagedPath);
    const absoluteAllowedRoot = path3.resolve(path3.join(manifestDir, "skill-updates"));
    const relative2 = path3.relative(absoluteAllowedRoot, absoluteStagedPath);
    const isUnderRoot = relative2 && !relative2.startsWith("..") && !path3.isAbsolute(relative2);
    if (isUnderRoot) {
      if (existsSync5(absoluteStagedPath)) {
        rmSync2(absoluteStagedPath, { recursive: true, force: true });
        log(`[skill-sync] Safely cleaned up staged path for ${skillName}: ${absoluteStagedPath}`);
      }
    } else {
      log(`[skill-sync] Refusing to delete staged path for ${skillName}: path ${absoluteStagedPath} is not under managed root ${absoluteAllowedRoot}`);
    }
  } catch (err) {
    log(`[skill-sync] Error while trying to verify and remove staged path for ${skillName} (${stagedPath}):`, err);
  }
}
function syncBundledSkillsFromPackage(packageRoot, options = {}) {
  const installed = [];
  const skippedExisting = [];
  const failed = [];
  const staged = [];
  const adopted = [];
  const customized = [];
  const stagedThisSync = [];
  const sourceSkillsDir = path3.join(packageRoot, "src", "skills");
  try {
    const stat = lstatSync(sourceSkillsDir);
    if (stat.isSymbolicLink() || !stat.isDirectory()) {
      log(`[skill-sync] Source skills directory is not a valid directory: ${sourceSkillsDir}`);
      return {
        installed,
        skippedExisting,
        failed,
        staged,
        adopted,
        customized,
        stagedThisSync
      };
    }
  } catch {
    log(`[skill-sync] Source skills directory does not exist or is unreadable: ${sourceSkillsDir}`);
    return {
      installed,
      skippedExisting,
      failed,
      staged,
      adopted,
      customized,
      stagedThisSync
    };
  }
  let packageVersion = "unknown";
  try {
    const pkgJsonPath = path3.join(packageRoot, "package.json");
    if (existsSync5(pkgJsonPath)) {
      const content = readFileSync4(pkgJsonPath, "utf-8");
      const pkg = JSON.parse(content);
      if (pkg.version) {
        packageVersion = pkg.version;
      }
    }
  } catch (err) {
    log(`[skill-sync] Failed to read package version from ${packageRoot}:`, err);
  }
  const manifestDir = path3.join(getConfigDir(), ".oh-my-opencode-slim");
  const lockDir = path3.join(manifestDir, "skills.lock");
  try {
    mkdirSync3(manifestDir, { recursive: true });
  } catch (err) {
    log(`[skill-sync] Failed to create manifest directory: ${manifestDir}`, err);
  }
  if (!acquireLock(lockDir)) {
    log("[skill-sync] Failed to acquire lock for skill synchronization. Skipping.");
    return {
      installed,
      skippedExisting,
      failed: ["__lock__"],
      staged,
      adopted,
      customized,
      stagedThisSync
    };
  }
  try {
    const manifestPath = path3.join(manifestDir, "skills-manifest.json");
    let manifest = {
      schemaVersion: 1,
      updatedAt: new Date().toISOString(),
      skills: {}
    };
    let isManifestCorrupt = false;
    if (existsSync5(manifestPath)) {
      try {
        const content = readFileSync4(manifestPath, "utf-8");
        const parsed = JSON.parse(content);
        if (validateManifest(parsed)) {
          manifest = parsed;
        } else {
          throw new Error("Manifest validation failed");
        }
      } catch (err) {
        log("[skill-sync] Manifest is corrupt/unreadable. Failing closed.", err);
        isManifestCorrupt = true;
      }
    }
    const destSkillsDir = path3.join(getConfigDir(), "skills");
    try {
      if (!existsSync5(destSkillsDir)) {
        mkdirSync3(destSkillsDir, { recursive: true });
      }
    } catch (err) {
      log(`[skill-sync] Failed to create destination skills directory: ${destSkillsDir}`, err);
    }
    const skillsToProcess = (options.skills ?? CUSTOM_SKILLS).map((s) => ({
      name: s.name,
      sourcePath: s.sourcePath
    }));
    for (const skill of skillsToProcess) {
      try {
        const sourcePath = path3.join(packageRoot, skill.sourcePath);
        try {
          const stat = lstatSync(sourcePath);
          if (stat.isSymbolicLink() || !stat.isDirectory()) {
            continue;
          }
          const skillMdPath = path3.join(sourcePath, "SKILL.md");
          const skillMdStat = lstatSync(skillMdPath);
          if (skillMdStat.isSymbolicLink() || !skillMdStat.isFile()) {
            continue;
          }
        } catch {
          continue;
        }
        const destPath = path3.join(destSkillsDir, skill.name);
        const hadArtifacts = recoverOrphanArtifacts(destSkillsDir, skill.name);
        let destExists = false;
        let destIsDir = false;
        try {
          const destStat = lstatSync(destPath);
          destExists = true;
          destIsDir = destStat.isDirectory() && !destStat.isSymbolicLink();
        } catch {}
        if (destExists && !destIsDir) {
          log(`[skill-sync] Skill ${skill.name} destination is a file or symlink (conflict). Skipping.`);
          skippedExisting.push(skill.name);
          const sourceHash2 = computeDirectoryHash(sourcePath);
          const entry2 = manifest.skills[skill.name];
          if (entry2?.stagedPath) {
            removeManagedStagedPath(entry2.stagedPath, manifestDir, skill.name);
          }
          manifest.skills[skill.name] = {
            status: "conflict",
            packageVersion,
            sourceHash: sourceHash2,
            lastManagedHash: "",
            lastSeenHash: "",
            updatedAt: new Date().toISOString()
          };
          continue;
        }
        const sourceHash = computeDirectoryHash(sourcePath);
        const entry = manifest.skills[skill.name];
        if (options.force && destExists) {
          try {
            atomicReplaceDir(sourcePath, destPath);
            if (entry?.stagedPath) {
              removeManagedStagedPath(entry.stagedPath, manifestDir, skill.name);
            }
            installed.push(skill.name);
            manifest.skills[skill.name] = {
              status: "managed",
              packageVersion,
              sourceHash,
              lastManagedHash: sourceHash,
              lastSeenHash: sourceHash,
              updatedAt: new Date().toISOString()
            };
            log(`[skill-sync] Force-updated skill: ${skill.name}`);
          } catch (err) {
            log(`[skill-sync] Failed to force-update skill ${skill.name}:`, err);
            failed.push(skill.name);
          }
          continue;
        }
        if (isManifestCorrupt) {
          if (!destExists) {
            try {
              atomicReplaceDir(sourcePath, destPath);
              installed.push(skill.name);
              manifest.skills[skill.name] = {
                status: "managed",
                packageVersion,
                sourceHash,
                lastManagedHash: sourceHash,
                lastSeenHash: sourceHash,
                updatedAt: new Date().toISOString()
              };
            } catch (err) {
              log(`[skill-sync] Failed to install missing skill ${skill.name} (corrupt manifest mode):`, err);
              failed.push(skill.name);
            }
          } else {
            log(`[skill-sync] Skipping existing skill ${skill.name} because manifest is corrupt.`);
            skippedExisting.push(skill.name);
            const destHash2 = computeDirectoryHash(destPath);
            if (destHash2 === sourceHash) {
              manifest.skills[skill.name] = {
                status: "managed",
                packageVersion,
                sourceHash,
                lastManagedHash: sourceHash,
                lastSeenHash: sourceHash,
                updatedAt: new Date().toISOString()
              };
            } else {
              try {
                const stagedSkillDir = path3.join(manifestDir, "skill-updates", packageVersion, skill.name);
                if (existsSync5(stagedSkillDir)) {
                  rmSync2(stagedSkillDir, { recursive: true, force: true });
                }
                mkdirSync3(stagedSkillDir, { recursive: true });
                copyDirRecursive(sourcePath, stagedSkillDir);
                manifest.skills[skill.name] = {
                  status: "customized",
                  packageVersion,
                  sourceHash,
                  lastManagedHash: "",
                  lastSeenHash: destHash2,
                  stagedPath: stagedSkillDir,
                  updatedAt: new Date().toISOString()
                };
                staged.push(skill.name);
                customized.push(skill.name);
                stagedThisSync.push(skill.name);
              } catch (err) {
                log(`[skill-sync] Failed to stage update for customized skill ${skill.name} during recovery:`, err);
                manifest.skills[skill.name] = {
                  status: "customized",
                  packageVersion: "unknown",
                  sourceHash: "",
                  lastManagedHash: "",
                  lastSeenHash: destHash2,
                  updatedAt: new Date().toISOString()
                };
              }
            }
          }
          continue;
        }
        if (!destExists) {
          if (entry && entry.status === "deleted") {
            log(`[skill-sync] Skill ${skill.name} was deleted by user. Skipping.`);
            skippedExisting.push(skill.name);
            continue;
          }
          if (entry && entry.status !== "deleted") {
            if (hadArtifacts) {
              log(`[skill-sync] Managed skill ${skill.name} has backup/staging artifacts. Skipping delete, re-installing.`);
              try {
                atomicReplaceDir(sourcePath, destPath);
                installed.push(skill.name);
                manifest.skills[skill.name] = {
                  status: "managed",
                  packageVersion,
                  sourceHash,
                  lastManagedHash: sourceHash,
                  lastSeenHash: sourceHash,
                  updatedAt: new Date().toISOString()
                };
              } catch (err) {
                log(`[skill-sync] Failed to re-install skill ${skill.name}:`, err);
                failed.push(skill.name);
              }
              continue;
            } else {
              if (entry.stagedPath) {
                removeManagedStagedPath(entry.stagedPath, manifestDir, skill.name);
                delete entry.stagedPath;
              }
              const rawEntry = entry;
              delete rawEntry.stagedVersion;
              delete rawEntry.stagedHash;
              entry.status = "deleted";
              entry.updatedAt = new Date().toISOString();
              log(`[skill-sync] Skill ${skill.name} was deleted by user (detected now). Skipping.`);
              skippedExisting.push(skill.name);
              continue;
            }
          }
          try {
            atomicReplaceDir(sourcePath, destPath);
            installed.push(skill.name);
            manifest.skills[skill.name] = {
              status: "managed",
              packageVersion,
              sourceHash,
              lastManagedHash: sourceHash,
              lastSeenHash: sourceHash,
              updatedAt: new Date().toISOString()
            };
            log(`[skill-sync] Successfully installed missing skill: ${skill.name}`);
          } catch (err) {
            log(`[skill-sync] Failed to install skill ${skill.name}:`, err);
            failed.push(skill.name);
          }
          continue;
        }
        const destHash = computeDirectoryHash(destPath);
        if (entry) {
          if (entry.status === "managed") {
            if (destHash === entry.lastManagedHash) {
              if (destHash === sourceHash) {
                entry.packageVersion = packageVersion;
                entry.sourceHash = sourceHash;
                entry.lastManagedHash = sourceHash;
                entry.lastSeenHash = sourceHash;
                entry.updatedAt = new Date().toISOString();
                skippedExisting.push(skill.name);
              } else {
                try {
                  atomicReplaceDir(sourcePath, destPath);
                  installed.push(skill.name);
                  manifest.skills[skill.name] = {
                    status: "managed",
                    packageVersion,
                    sourceHash,
                    lastManagedHash: sourceHash,
                    lastSeenHash: sourceHash,
                    updatedAt: new Date().toISOString()
                  };
                  log(`[skill-sync] Updated managed skill: ${skill.name}`);
                } catch (err) {
                  log(`[skill-sync] Failed to update managed skill ${skill.name}:`, err);
                  failed.push(skill.name);
                }
              }
            } else {
              if (destHash === sourceHash) {
                manifest.skills[skill.name] = {
                  status: "managed",
                  packageVersion,
                  sourceHash,
                  lastManagedHash: sourceHash,
                  lastSeenHash: sourceHash,
                  updatedAt: new Date().toISOString()
                };
                skippedExisting.push(skill.name);
              } else {
                try {
                  const stagedSkillDir = path3.join(manifestDir, "skill-updates", packageVersion, skill.name);
                  if (entry.stagedPath && entry.stagedPath !== stagedSkillDir) {
                    removeManagedStagedPath(entry.stagedPath, manifestDir, skill.name);
                  }
                  if (existsSync5(stagedSkillDir)) {
                    rmSync2(stagedSkillDir, { recursive: true, force: true });
                  }
                  mkdirSync3(stagedSkillDir, { recursive: true });
                  copyDirRecursive(sourcePath, stagedSkillDir);
                  entry.status = "customized";
                  entry.lastSeenHash = destHash;
                  entry.stagedPath = stagedSkillDir;
                  entry.sourceHash = sourceHash;
                  entry.packageVersion = packageVersion;
                  entry.updatedAt = new Date().toISOString();
                  staged.push(skill.name);
                  customized.push(skill.name);
                  stagedThisSync.push(skill.name);
                  skippedExisting.push(skill.name);
                  log(`[skill-sync] Skill ${skill.name} is customized. Staged update at ${stagedSkillDir}`);
                } catch (err) {
                  log(`[skill-sync] Failed to stage update for customized skill ${skill.name}:`, err);
                  failed.push(skill.name);
                }
              }
            }
          } else if (entry.status === "customized") {
            if (destHash === sourceHash) {
              if (entry.stagedPath) {
                removeManagedStagedPath(entry.stagedPath, manifestDir, skill.name);
              }
              entry.status = "managed";
              entry.lastManagedHash = sourceHash;
              entry.lastSeenHash = sourceHash;
              entry.sourceHash = sourceHash;
              entry.packageVersion = packageVersion;
              delete entry.stagedPath;
              entry.updatedAt = new Date().toISOString();
              adopted.push(skill.name);
              skippedExisting.push(skill.name);
              log(`[skill-sync] Customized skill ${skill.name} converged with current version. Adopted back to managed.`);
            } else {
              entry.lastSeenHash = destHash;
              entry.updatedAt = new Date().toISOString();
              if (destHash !== sourceHash && entry.sourceHash !== sourceHash) {
                try {
                  const stagedSkillDir = path3.join(manifestDir, "skill-updates", packageVersion, skill.name);
                  if (entry.stagedPath && entry.stagedPath !== stagedSkillDir) {
                    removeManagedStagedPath(entry.stagedPath, manifestDir, skill.name);
                  }
                  if (existsSync5(stagedSkillDir)) {
                    rmSync2(stagedSkillDir, { recursive: true, force: true });
                  }
                  mkdirSync3(stagedSkillDir, { recursive: true });
                  copyDirRecursive(sourcePath, stagedSkillDir);
                  entry.stagedPath = stagedSkillDir;
                  entry.sourceHash = sourceHash;
                  entry.packageVersion = packageVersion;
                  staged.push(skill.name);
                  customized.push(skill.name);
                  stagedThisSync.push(skill.name);
                  skippedExisting.push(skill.name);
                  log(`[skill-sync] Staged new update for customized skill ${skill.name} at ${stagedSkillDir}`);
                } catch (err) {
                  log(`[skill-sync] Failed to stage update for customized skill ${skill.name}:`, err);
                  failed.push(skill.name);
                }
              } else {
                customized.push(skill.name);
                skippedExisting.push(skill.name);
              }
            }
          } else if (entry.status === "deleted") {
            if (destHash === sourceHash) {
              entry.status = "managed";
              entry.packageVersion = packageVersion;
              entry.sourceHash = sourceHash;
              entry.lastManagedHash = sourceHash;
              entry.lastSeenHash = sourceHash;
              entry.updatedAt = new Date().toISOString();
              skippedExisting.push(skill.name);
              adopted.push(skill.name);
              log(`[skill-sync] Skill ${skill.name} re-created by user (matching current). Adopted as managed.`);
            } else {
              try {
                const stagedSkillDir = path3.join(manifestDir, "skill-updates", packageVersion, skill.name);
                if (entry.stagedPath && entry.stagedPath !== stagedSkillDir) {
                  removeManagedStagedPath(entry.stagedPath, manifestDir, skill.name);
                }
                if (existsSync5(stagedSkillDir)) {
                  rmSync2(stagedSkillDir, { recursive: true, force: true });
                }
                mkdirSync3(stagedSkillDir, { recursive: true });
                copyDirRecursive(sourcePath, stagedSkillDir);
                entry.status = "customized";
                entry.packageVersion = packageVersion;
                entry.sourceHash = sourceHash;
                entry.lastManagedHash = sourceHash;
                entry.lastSeenHash = destHash;
                entry.stagedPath = stagedSkillDir;
                entry.updatedAt = new Date().toISOString();
                staged.push(skill.name);
                customized.push(skill.name);
                stagedThisSync.push(skill.name);
                skippedExisting.push(skill.name);
                log(`[skill-sync] Skill ${skill.name} re-created by user (custom). Marked customized and staged.`);
              } catch (err) {
                log(`[skill-sync] Failed to stage update for deleted/recreated skill ${skill.name}:`, err);
                failed.push(skill.name);
              }
            }
          } else if (entry.status === "conflict") {
            if (destHash === sourceHash) {
              if (entry.stagedPath) {
                removeManagedStagedPath(entry.stagedPath, manifestDir, skill.name);
              }
              entry.status = "managed";
              entry.packageVersion = packageVersion;
              entry.sourceHash = sourceHash;
              entry.lastManagedHash = sourceHash;
              entry.lastSeenHash = sourceHash;
              delete entry.stagedPath;
              entry.updatedAt = new Date().toISOString();
              adopted.push(skill.name);
            } else {
              try {
                const stagedSkillDir = path3.join(manifestDir, "skill-updates", packageVersion, skill.name);
                if (entry.stagedPath && entry.stagedPath !== stagedSkillDir) {
                  removeManagedStagedPath(entry.stagedPath, manifestDir, skill.name);
                }
                if (existsSync5(stagedSkillDir)) {
                  rmSync2(stagedSkillDir, { recursive: true, force: true });
                }
                mkdirSync3(stagedSkillDir, { recursive: true });
                copyDirRecursive(sourcePath, stagedSkillDir);
                entry.status = "customized";
                entry.packageVersion = packageVersion;
                entry.sourceHash = sourceHash;
                entry.lastManagedHash = sourceHash;
                entry.lastSeenHash = destHash;
                entry.stagedPath = stagedSkillDir;
                entry.updatedAt = new Date().toISOString();
                staged.push(skill.name);
                customized.push(skill.name);
                stagedThisSync.push(skill.name);
                skippedExisting.push(skill.name);
                log(`[skill-sync] Conflicted skill ${skill.name} recovered as customized and staged at ${stagedSkillDir}`);
              } catch (err) {
                log(`[skill-sync] Failed to stage update for conflicted skill ${skill.name}:`, err);
                failed.push(skill.name);
              }
            }
          }
        } else {
          if (destHash === sourceHash) {
            manifest.skills[skill.name] = {
              status: "managed",
              packageVersion,
              sourceHash,
              lastManagedHash: sourceHash,
              lastSeenHash: sourceHash,
              updatedAt: new Date().toISOString()
            };
            skippedExisting.push(skill.name);
            adopted.push(skill.name);
            log(`[skill-sync] Adopted existing matching skill: ${skill.name}`);
          } else if (LEGACY_MANAGED_SKILL_HASHES[skill.name]?.includes(destHash)) {
            try {
              atomicReplaceDir(sourcePath, destPath);
              installed.push(skill.name);
              manifest.skills[skill.name] = {
                status: "managed",
                packageVersion,
                sourceHash,
                lastManagedHash: sourceHash,
                lastSeenHash: sourceHash,
                updatedAt: new Date().toISOString()
              };
              log(`[skill-sync] Adopted and updated legacy skill: ${skill.name}`);
            } catch (err) {
              log(`[skill-sync] Failed to update legacy skill ${skill.name}:`, err);
              failed.push(skill.name);
            }
          } else {
            try {
              const stagedSkillDir = path3.join(manifestDir, "skill-updates", packageVersion, skill.name);
              if (existsSync5(stagedSkillDir)) {
                rmSync2(stagedSkillDir, { recursive: true, force: true });
              }
              mkdirSync3(stagedSkillDir, { recursive: true });
              copyDirRecursive(sourcePath, stagedSkillDir);
              manifest.skills[skill.name] = {
                status: "customized",
                packageVersion,
                sourceHash,
                lastManagedHash: "",
                lastSeenHash: destHash,
                stagedPath: stagedSkillDir,
                updatedAt: new Date().toISOString()
              };
              staged.push(skill.name);
              customized.push(skill.name);
              stagedThisSync.push(skill.name);
              skippedExisting.push(skill.name);
              log(`[skill-sync] Skill ${skill.name} is customized (no manifest entry). Staged update at ${stagedSkillDir}`);
            } catch (err) {
              log(`[skill-sync] Failed to stage update for customized skill ${skill.name}:`, err);
              failed.push(skill.name);
            }
          }
        }
      } catch (err) {
        log(`[skill-sync] Failed processing skill ${skill.name}:`, err);
        failed.push(skill.name);
      }
    }
    let manifestWriteFailed = false;
    manifest.updatedAt = new Date().toISOString();
    const tempManifestPath = `${manifestPath}.${Math.random().toString(36).slice(2, 9)}.tmp`;
    try {
      writeFileSync2(tempManifestPath, JSON.stringify(manifest, null, 2), "utf-8");
      renameSync2(tempManifestPath, manifestPath);
    } catch (err) {
      log("[skill-sync] Failed to write skills manifest atomically:", err);
      manifestWriteFailed = true;
      try {
        if (existsSync5(tempManifestPath)) {
          unlinkSync(tempManifestPath);
        }
      } catch {}
    }
    if (manifestWriteFailed) {
      failed.push("__manifest__");
    }
  } finally {
    releaseLock(lockDir);
  }
  return {
    installed,
    skippedExisting,
    failed,
    staged,
    adopted,
    customized,
    stagedThisSync
  };
}

// src/cli/background-subagents.ts
import { existsSync as existsSync6, mkdirSync as mkdirSync4, readFileSync as readFileSync5, writeFileSync as writeFileSync3 } from "node:fs";
import { homedir as homedir3 } from "node:os";
import { dirname as dirname4, join as join6 } from "node:path";
var ENV_NAME = "OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS";
var EXA_ENV_NAME = "OPENCODE_ENABLE_EXA";
var START_MARKER = "# >>> oh-my-opencode-slim background subagents >>>";
var END_MARKER = "# <<< oh-my-opencode-slim background subagents <<<";
function isBackgroundSubagentsEnabled(value) {
  if (!value)
    return false;
  const normalized = value.trim().toLowerCase();
  return normalized !== "" && !["0", "false", "no", "off"].includes(normalized);
}
function detectShellKind(shell) {
  const name = shell?.split("/").at(-1);
  if (name === "zsh" || name === "bash" || name === "fish")
    return name;
  return;
}
function detectBackgroundSubagentsTarget(env = process.env) {
  const shell = detectShellKind(env.SHELL);
  const home = env.HOME || homedir3();
  if (shell === "zsh")
    return join6(home, ".zshrc");
  if (shell === "bash")
    return join6(home, ".bashrc");
  if (shell === "fish") {
    const configHome = env.XDG_CONFIG_HOME || join6(home, ".config");
    return join6(configHome, "fish", "conf.d", "opencode-background-subagents.fish");
  }
  return;
}
function getBackgroundSubagentsBlock(targetPath) {
  const isFish = targetPath.endsWith(".fish");
  const commands = isFish ? `set -gx ${ENV_NAME} true
set -gx ${EXA_ENV_NAME} 1` : `export ${ENV_NAME}=true
export ${EXA_ENV_NAME}=1`;
  return `${START_MARKER}
${commands}
${END_MARKER}`;
}
function manualBackgroundSubagentsInstructions(options) {
  const shell = options?.shell ?? (options?.targetPath?.endsWith(".fish") ? "fish" : undefined) ?? detectShellKind(options?.targetPath);
  const bashZshSnippet = `export ${ENV_NAME}=true`;
  const fishSnippet = `set -gx ${ENV_NAME} true`;
  const bashZshExaSnippet = `export ${EXA_ENV_NAME}=1`;
  const fishExaSnippet = `set -gx ${EXA_ENV_NAME} 1`;
  if (shell === "fish") {
    return `Start OpenCode with background subagents and websearch enabled:
  env ${ENV_NAME}=true ${EXA_ENV_NAME}=1 opencode

Or add these to your fish startup file:
  ${fishSnippet}
  ${fishExaSnippet}`;
  }
  if (shell === "bash" || shell === "zsh") {
    return `Start OpenCode with background subagents and websearch enabled:
  ${ENV_NAME}=true ${EXA_ENV_NAME}=1 opencode

Or add these to your shell startup file:
  ${bashZshSnippet}
  ${bashZshExaSnippet}`;
  }
  return `Start OpenCode with background subagents and websearch enabled:
  ${ENV_NAME}=true ${EXA_ENV_NAME}=1 opencode

Or add the matching pair to your shell startup file:
  bash/zsh: ${bashZshSnippet}
            ${bashZshExaSnippet}
  fish: ${fishSnippet}
        ${fishExaSnippet}`;
}
function expandHomePath(targetPath) {
  if (targetPath === "~")
    return homedir3();
  if (targetPath.startsWith("~/"))
    return join6(homedir3(), targetPath.slice(2));
  return targetPath;
}
function upsertBackgroundSubagentsBlock(content, block) {
  const start = content.indexOf(START_MARKER);
  const end = content.indexOf(END_MARKER);
  if (start !== -1 && end !== -1 && end > start) {
    const afterEnd = end + END_MARKER.length;
    return `${content.slice(0, start)}${block}${content.slice(afterEnd)}`;
  }
  const separator = content.length > 0 && !content.endsWith(`
`) ? `

` : "";
  const prefix = content.length > 0 && content.endsWith(`
`) ? `
` : separator;
  return `${content}${prefix}${block}
`;
}
function writeBackgroundSubagentsBlock(targetPath) {
  const block = getBackgroundSubagentsBlock(targetPath);
  const content = existsSync6(targetPath) ? readFileSync5(targetPath, "utf8") : "";
  const nextContent = upsertBackgroundSubagentsBlock(content, block);
  mkdirSync4(dirname4(targetPath), { recursive: true });
  writeFileSync3(targetPath, nextContent);
}

// src/companion/updater.ts
import { createHash as createHash2 } from "node:crypto";
import {
  chmodSync,
  copyFileSync as copyFileSync3,
  existsSync as existsSync7,
  mkdirSync as mkdirSync5,
  mkdtempSync,
  readFileSync as readFileSync6,
  renameSync as renameSync3,
  rmSync as rmSync3,
  statSync as statSync4,
  writeFileSync as writeFileSync4
} from "node:fs";
import { homedir as homedir4, platform, tmpdir } from "node:os";
import * as path4 from "node:path";
import { setTimeout as delay } from "node:timers/promises";

// src/hooks/apply-patch/errors.ts
function getErrorMessage(error) {
  return error instanceof Error ? error.message : String(error);
}

// src/companion/updater.ts
init_compat();
var DOWNLOAD_TIMEOUT_MS = 30000;
var LOCK_TIMEOUT_MS = 2000;
var STALE_LOCK_MS = 5 * 60000;
var FIRST_METADATA_VERSION = "0.1.2";
var COMPANION_MANIFEST = {
  version: "0.1.3",
  tag: "companion-v0.1.3",
  repo: "alvinunreal/oh-my-opencode-slim",
  checksums: {
    "oh-my-opencode-slim-companion-v0.1.3-aarch64-apple-darwin.tar.gz": "b4885f9b1900c02376e5f8f5ae6f3b8a89d26f7514b03f836d7e3d618164a0ed",
    "oh-my-opencode-slim-companion-v0.1.3-aarch64-unknown-linux-gnu.tar.gz": "ed7cffc583e1eaa78c9bea702e6b6aa3bbc5bb4d881713fb2050237ba6b7aca5",
    "oh-my-opencode-slim-companion-v0.1.3-x86_64-apple-darwin.tar.gz": "98d8ea7c7bc4415b18e0d4c524adb4eb9a84c872919840fdc021f0f50c61f808",
    "oh-my-opencode-slim-companion-v0.1.3-x86_64-pc-windows-msvc.zip": "9316a49bf01f3b4fb1ce2d62edfc46094e73bb153d6ce023fb7df085afcf77bd",
    "oh-my-opencode-slim-companion-v0.1.3-x86_64-unknown-linux-gnu.tar.gz": "33f5fd4b6c80155a019391e5efb13904ca9531ba8dd8c6cba30a161f1b07b764"
  }
};
function getCompanionTarget() {
  const p = process.platform;
  const a = process.arch;
  if (p === "darwin") {
    if (a === "arm64")
      return "aarch64-apple-darwin";
    if (a === "x64")
      return "x86_64-apple-darwin";
  } else if (p === "linux") {
    if (a === "x64")
      return "x86_64-unknown-linux-gnu";
    if (a === "arm64")
      return "aarch64-unknown-linux-gnu";
  } else if (p === "win32") {
    if (a === "x64")
      return "x86_64-pc-windows-msvc";
  }
  return null;
}
function getCompanionBinaryPath() {
  const xdg = process.env.XDG_DATA_HOME?.trim();
  const base = xdg && path4.isAbsolute(xdg) ? xdg : path4.join(homedir4(), ".local", "share");
  return path4.join(base, "opencode", "storage", "oh-my-opencode-slim", "bin", platform() === "win32" ? "oh-my-opencode-slim-companion.exe" : "oh-my-opencode-slim-companion");
}
async function ensureCompanionVersion(options) {
  const { config, dryRun = false } = options;
  const manifest = options.manifest ?? COMPANION_MANIFEST;
  const binaryPath = getCompanionBinaryPath();
  if (config?.enabled !== true) {
    return { status: "skipped", reason: "disabled", binaryPath };
  }
  if (config.binaryPath?.trim()) {
    return { status: "skipped", reason: "custom-binary", binaryPath };
  }
  const target = getCompanionTarget();
  if (!target) {
    return {
      status: "failed",
      binaryPath,
      error: `Unsupported platform/architecture: ${process.platform} ${process.arch}`
    };
  }
  const current = readInstallMetadata(binaryPath);
  if (existsSync7(binaryPath) && !current && manifest.version === FIRST_METADATA_VERSION) {
    const archiveName = companionArchiveName(manifest.version, target);
    writeInstallMetadata(binaryPath, {
      version: manifest.version,
      tag: manifest.tag,
      target,
      installedAt: new Date().toISOString(),
      archiveName,
      checksum: manifest.checksums?.[archiveName]
    });
    return { status: "current", binaryPath, version: manifest.version };
  }
  if (existsSync7(binaryPath) && current?.target === target && compareSemver(current.version, manifest.version) >= 0) {
    return { status: "current", binaryPath, version: current.version };
  }
  if (dryRun) {
    return { status: "installed", binaryPath, version: manifest.version };
  }
  return withCompanionInstallLock(binaryPath, options.lockTimeoutMs, options.lockStaleMs, async () => {
    const lockedCurrent = readInstallMetadata(binaryPath);
    if (existsSync7(binaryPath) && !lockedCurrent && manifest.version === FIRST_METADATA_VERSION) {
      const archiveName = companionArchiveName(manifest.version, target);
      writeInstallMetadata(binaryPath, {
        version: manifest.version,
        tag: manifest.tag,
        target,
        installedAt: new Date().toISOString(),
        archiveName,
        checksum: manifest.checksums?.[archiveName]
      });
      return { status: "current", binaryPath, version: manifest.version };
    }
    if (existsSync7(binaryPath) && lockedCurrent?.target === target && compareSemver(lockedCurrent.version, manifest.version) >= 0) {
      return {
        status: "current",
        binaryPath,
        version: lockedCurrent.version
      };
    }
    return installCompanionArchive(binaryPath, target, manifest, options.downloadTimeoutMs ?? DOWNLOAD_TIMEOUT_MS);
  });
}
async function installCompanionArchive(finalBinaryPath, target, manifest, downloadTimeoutMs) {
  const isWindows = process.platform === "win32";
  const archiveName = companionArchiveName(manifest.version, target, isWindows);
  const downloadUrl = `https://github.com/${manifest.repo}/releases/download/${manifest.tag}/${archiveName}`;
  const expectedChecksum = manifest.checksums?.[archiveName];
  if (!expectedChecksum) {
    return {
      status: "failed",
      binaryPath: finalBinaryPath,
      error: `Missing SHA256 checksum for companion archive: ${archiveName}`
    };
  }
  let buffer;
  const controller = new AbortController;
  const timeout = setTimeout(() => controller.abort(), downloadTimeoutMs);
  try {
    const res = await fetch(downloadUrl, { signal: controller.signal });
    if (!res.ok) {
      return {
        status: "failed",
        binaryPath: finalBinaryPath,
        error: `Failed to download companion binary (HTTP ${res.status}): ${res.statusText}`
      };
    }
    buffer = await res.arrayBuffer();
  } catch (err) {
    return {
      status: "failed",
      binaryPath: finalBinaryPath,
      error: `Failed to fetch companion archive: ${getErrorMessage(err)}`
    };
  } finally {
    clearTimeout(timeout);
  }
  const checksum = createHash2("sha256").update(Buffer.from(buffer)).digest("hex");
  if (checksum !== expectedChecksum) {
    return {
      status: "failed",
      binaryPath: finalBinaryPath,
      error: "Companion archive checksum mismatch"
    };
  }
  let tempDir = "";
  try {
    tempDir = mkdtempSync(path4.join(tmpdir(), "companion-install-"));
    const archivePath = path4.join(tempDir, archiveName);
    writeFileSync4(archivePath, Buffer.from(buffer));
    const extractedDir = path4.join(tempDir, "extracted");
    mkdirSync5(extractedDir, { recursive: true });
    if (isWindows) {
      const { extractZip: extractZip2 } = await Promise.resolve().then(() => (init_zip_extractor(), exports_zip_extractor));
      await extractZip2(archivePath, extractedDir);
    } else {
      const proc = crossSpawn(["tar", "-xzf", archivePath, "-C", extractedDir]);
      const exitCode = await proc.exited;
      if (exitCode !== 0) {
        const stderr = await proc.stderr();
        return {
          status: "failed",
          binaryPath: finalBinaryPath,
          error: `Archive extraction failed (tar exited with ${exitCode}): ${stderr}`
        };
      }
    }
    const binaryName = isWindows ? "oh-my-opencode-slim-companion.exe" : "oh-my-opencode-slim-companion";
    const extractedBinaryPath = path4.join(extractedDir, binaryName);
    if (!existsSync7(extractedBinaryPath)) {
      return {
        status: "failed",
        binaryPath: finalBinaryPath,
        error: `Binary ${binaryName} not found in extracted archive`
      };
    }
    const binDir = path4.dirname(finalBinaryPath);
    mkdirSync5(binDir, { recursive: true });
    const tmpFinalPath = `${finalBinaryPath}.tmp`;
    copyFileSync3(extractedBinaryPath, tmpFinalPath);
    if (!isWindows) {
      chmodSync(tmpFinalPath, 493);
    }
    renameSync3(tmpFinalPath, finalBinaryPath);
    writeInstallMetadata(finalBinaryPath, {
      version: manifest.version,
      tag: manifest.tag,
      target,
      installedAt: new Date().toISOString(),
      archiveName,
      checksum
    });
    return {
      status: "installed",
      binaryPath: finalBinaryPath,
      version: manifest.version
    };
  } catch (err) {
    return {
      status: "failed",
      binaryPath: finalBinaryPath,
      error: `Failed to install companion: ${getErrorMessage(err)}`
    };
  } finally {
    if (tempDir) {
      try {
        rmSync3(tempDir, { recursive: true, force: true });
      } catch (err) {
        log("[updater] install cleanup failed", String(err));
      }
    }
  }
}
function readInstallMetadata(binaryPath) {
  try {
    const parsed = JSON.parse(readFileSync6(metadataPath(binaryPath), "utf8"));
    if (parsed?.version && parsed.tag && parsed.target) {
      return parsed;
    }
  } catch (err) {
    log("[updater] metadata read failed", String(err));
  }
  return null;
}
function writeInstallMetadata(binaryPath, metadata) {
  writeFileSync4(metadataPath(binaryPath), JSON.stringify(metadata, null, 2));
}
function metadataPath(binaryPath) {
  return `${binaryPath}.json`;
}
async function withCompanionInstallLock(binaryPath, timeoutMs, staleMs, run) {
  const lock = `${binaryPath}.lock`;
  const deadline = Date.now() + (timeoutMs ?? LOCK_TIMEOUT_MS);
  const staleAfterMs = staleMs ?? STALE_LOCK_MS;
  mkdirSync5(path4.dirname(binaryPath), { recursive: true });
  while (Date.now() <= deadline) {
    try {
      mkdirSync5(lock);
      try {
        return await run();
      } finally {
        try {
          rmSync3(lock, { recursive: true, force: true });
        } catch (err) {
          log("[updater] lock release failed", String(err));
        }
      }
    } catch (err) {
      const code = err.code;
      if (code !== "EEXIST")
        throw err;
      try {
        const ageMs = Date.now() - statSync4(lock).mtimeMs;
        if (ageMs > staleAfterMs) {
          rmSync3(lock, { recursive: true, force: true });
          log("[companion] removed stale install lock", lock);
          continue;
        }
      } catch (statErr) {
        const statCode = statErr.code;
        if (statCode !== "ENOENT")
          throw statErr;
      }
      await delay(25);
    }
  }
  log("[companion] install lock timed out", lock);
  return {
    status: "failed",
    binaryPath,
    error: "Timed out waiting for companion install lock"
  };
}
function companionArchiveName(version, target, isWindows = process.platform === "win32") {
  const ext = isWindows ? "zip" : "tar.gz";
  return `oh-my-opencode-slim-companion-v${version}-${target}.${ext}`;
}
function compareSemver(a, b) {
  const left = parseSemver(a);
  const right = parseSemver(b);
  if (!left || !right)
    return a.localeCompare(b);
  for (let i = 0;i < 3; i++) {
    const diff = left[i] - right[i];
    if (diff !== 0)
      return diff;
  }
  return 0;
}
function parseSemver(version) {
  const match = version.match(/^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$/);
  if (!match)
    return null;
  return [Number(match[1]), Number(match[2]), Number(match[3])];
}

// src/cli/companion.ts
async function installCompanion(config) {
  const target = getCompanionTarget();
  const finalBinaryPath = getCompanionBinaryPath();
  if (!target) {
    return {
      success: false,
      configPath: finalBinaryPath,
      error: `Unsupported platform/architecture: ${process.platform} ${process.arch}`
    };
  }
  const ext = process.platform === "win32" ? "zip" : "tar.gz";
  const archiveName = `oh-my-opencode-slim-companion-v${COMPANION_MANIFEST.version}-${target}.${ext}`;
  const downloadUrl = `https://github.com/${COMPANION_MANIFEST.repo}/releases/download/${COMPANION_MANIFEST.tag}/${archiveName}`;
  if (config.dryRun) {
    console.log(`  [dry-run] Detected companion target: ${target}`);
    console.log(`  [dry-run] Would download archive: ${downloadUrl}`);
    console.log(`  [dry-run] Would extract and install to: ${finalBinaryPath}`);
    return {
      success: true,
      configPath: finalBinaryPath
    };
  }
  const result = await ensureCompanionVersion({
    config: { enabled: true },
    manifest: COMPANION_MANIFEST
  });
  if (result.status === "installed" || result.status === "current") {
    return {
      success: true,
      configPath: finalBinaryPath
    };
  }
  return {
    success: false,
    configPath: finalBinaryPath,
    error: result.status === "failed" ? result.error : `Companion install skipped: ${result.reason}`
  };
}
// src/cli/system.ts
init_compat();
import { spawnSync as spawnSync2 } from "node:child_process";
import { statSync as statSync5 } from "node:fs";
var cachedOpenCodePath = null;
function resolvePathCommand(command, environment = process.env) {
  try {
    const isWindows = process.platform === "win32";
    const resolver = isWindows ? "where" : "which";
    const result = spawnSync2(resolver, [command], {
      encoding: "utf-8",
      stdio: ["ignore", "pipe", "ignore"],
      env: environment,
      shell: isWindows
    });
    if (result.status !== 0) {
      return null;
    }
    const lines = result.stdout.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
    if (lines.length === 0) {
      return null;
    }
    if (isWindows) {
      const executable = lines.find((line) => /\.(cmd|exe|ps1|bat)$/i.test(line));
      return executable ?? lines[0];
    }
    return lines[0];
  } catch {
    return null;
  }
}
function canExecute(command, args, environment = process.env) {
  try {
    const isWindows = process.platform === "win32";
    const result = spawnSync2(command, args, {
      stdio: "ignore",
      env: environment,
      shell: isWindows && !/\.exe$/i.test(command)
    });
    return result.status === 0;
  } catch {
    return false;
  }
}
function getOpenCodePaths(environment = process.env) {
  const home = environment.HOME || environment.USERPROFILE || "";
  const isWindows = process.platform === "win32";
  const appData = environment.APPDATA || `${home}\\AppData\\Roaming`;
  const localAppData = environment.LOCALAPPDATA || `${home}\\AppData\\Local`;
  const windowsPaths = isWindows ? [
    `${appData}\\npm\\opencode.cmd`,
    `${appData}\\npm\\opencode.ps1`,
    `${localAppData}\\pnpm\\opencode.cmd`,
    `${localAppData}\\Yarn\\bin\\opencode.cmd`,
    `${localAppData}\\Programs\\opencode\\opencode.exe`,
    `${home}\\scoop\\shims\\opencode.exe`,
    `${home}\\scoop\\apps\\opencode\\current\\bin\\opencode.exe`,
    `C:\\ProgramData\\chocolatey\\bin\\opencode.exe`
  ] : [];
  return [
    "opencode",
    ...windowsPaths,
    `${home}/.local/bin/opencode`,
    `${home}/.opencode/bin/opencode`,
    `${home}/bin/opencode`,
    "/usr/local/bin/opencode",
    "/opt/opencode/bin/opencode",
    "/usr/bin/opencode",
    "/bin/opencode",
    "/Applications/OpenCode.app/Contents/MacOS/opencode",
    `${home}/Applications/OpenCode.app/Contents/MacOS/opencode`,
    "/opt/homebrew/bin/opencode",
    "/home/linuxbrew/.linuxbrew/bin/opencode",
    `${home}/homebrew/bin/opencode`,
    `${home}/Library/Application Support/opencode/bin/opencode`,
    "/snap/bin/opencode",
    "/var/snap/opencode/current/bin/opencode",
    "/var/lib/flatpak/exports/bin/ai.opencode.OpenCode",
    `${home}/.local/share/flatpak/exports/bin/ai.opencode.OpenCode`,
    "/nix/store/opencode/bin/opencode",
    `${home}/.nix-profile/bin/opencode`,
    "/run/current-system/sw/bin/opencode",
    `${home}/.cargo/bin/opencode`,
    `${home}/.npm-global/bin/opencode`,
    "/usr/local/lib/node_modules/opencode/bin/opencode",
    `${home}/.yarn/bin/opencode`,
    `${home}/.pnpm-global/bin/opencode`
  ];
}
function resolveOpenCodePath(environment = process.env) {
  const useCache = environment === process.env;
  if (useCache && cachedOpenCodePath) {
    return cachedOpenCodePath;
  }
  const pathOpenCodePath = resolvePathCommand("opencode", environment);
  if (pathOpenCodePath) {
    if (useCache) {
      cachedOpenCodePath = pathOpenCodePath;
    }
    return pathOpenCodePath;
  }
  const paths = getOpenCodePaths(environment);
  for (const opencodePath of paths) {
    if (opencodePath === "opencode")
      continue;
    try {
      const stat = statSync5(opencodePath);
      if (stat.isFile()) {
        if (useCache) {
          cachedOpenCodePath = opencodePath;
        }
        return opencodePath;
      }
    } catch {}
  }
  return "opencode";
}
async function isOpenCodeInstalled(environment = process.env) {
  const useCache = environment === process.env;
  const pathOpenCodePath = resolvePathCommand("opencode", environment);
  if (pathOpenCodePath && canExecute(pathOpenCodePath, ["--version"], environment)) {
    if (useCache) {
      cachedOpenCodePath = pathOpenCodePath;
    }
    return true;
  }
  const paths = getOpenCodePaths(environment);
  for (const opencodePath of paths) {
    if (opencodePath === "opencode")
      continue;
    if (canExecute(opencodePath, ["--version"], environment)) {
      if (useCache) {
        cachedOpenCodePath = opencodePath;
      }
      return true;
    }
  }
  return false;
}
async function getOpenCodeVersion() {
  const opencodePath = resolveOpenCodePath();
  try {
    const proc = crossSpawn([opencodePath, "--version"], {
      stdout: "pipe",
      stderr: "pipe"
    });
    const outputPromise = proc.stdout();
    await proc.exited;
    if (proc.exitCode === 0) {
      return (await outputPromise).trim();
    }
  } catch {}
  return null;
}
function getOpenCodePath() {
  const path5 = resolveOpenCodePath();
  return path5 === "opencode" ? null : path5;
}
// src/cli/install.ts
var GREEN = "\x1B[32m";
var BLUE = "\x1B[34m";
var YELLOW = "\x1B[33m";
var RED = "\x1B[31m";
var BOLD = "\x1B[1m";
var DIM = "\x1B[2m";
var RESET = "\x1B[0m";
var SYMBOLS = {
  check: `${GREEN}[ok]${RESET}`,
  cross: `${RED}[x]${RESET}`,
  arrow: `${BLUE}->${RESET}`,
  bullet: `${DIM}-${RESET}`,
  info: `${BLUE}[i]${RESET}`,
  warn: `${YELLOW}[!]${RESET}`,
  star: `${YELLOW}★${RESET}`
};
var GITHUB_REPO = "alvinunreal/oh-my-opencode-slim";
var GITHUB_URL = `https://github.com/${GITHUB_REPO}`;
function printHeader(isUpdate) {
  console.log();
  console.log(`${BOLD}oh-my-opencode-slim ${isUpdate ? "Update" : "Install"}${RESET}`);
  console.log("=".repeat(30));
  console.log();
}
function printStep(step, total, message) {
  console.log(`${DIM}[${step}/${total}]${RESET} ${message}`);
}
function printSuccess(message) {
  console.log(`${SYMBOLS.check} ${message}`);
}
function printError(message) {
  console.log(`${SYMBOLS.cross} ${RED}${message}${RESET}`);
}
function printWarning(message) {
  console.log(`${SYMBOLS.warn} ${YELLOW}${message}${RESET}`);
}
function printInfo(message) {
  console.log(`${SYMBOLS.info} ${message}`);
}
async function confirm(message, defaultYes = true) {
  const suffix = defaultYes ? " (Y/n) " : " (y/N) ";
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    const answer = (await rl.question(`${message}${suffix}`)).trim().toLowerCase();
    if (!answer)
      return defaultYes;
    return answer === "y" || answer === "yes";
  } finally {
    rl.close();
  }
}
async function askToStarRepo(config) {
  if (!config.promptForStar || config.dryRun || !process.stdin.isTTY)
    return;
  console.log();
  const shouldStar = await confirm(`${SYMBOLS.star} Star the repo on GitHub?`, true);
  if (!shouldStar)
    return;
  try {
    const { execFileSync } = await import("node:child_process");
    execFileSync("gh", ["api", "--silent", "--method", "PUT", `/user/starred/${GITHUB_REPO}`], { stdio: "ignore", timeout: 1e4 });
    printSuccess("Thanks for starring! ★");
  } catch {
    printInfo(`Couldn't star automatically. You can star manually:
  ${BLUE}${GITHUB_URL}${RESET}`);
  }
}
async function checkOpenCodeInstalled() {
  const installed = await isOpenCodeInstalled();
  if (!installed) {
    const isWindows = process.platform === "win32";
    printError("OpenCode is not installed on this system.");
    printInfo("Install it with:");
    if (isWindows) {
      console.log(`     ${BLUE}powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://opencode.ai/install.ps1 | iex"${RESET}`);
      console.log();
      printInfo("Or with winget:");
      console.log(`     ${BLUE}winget install opencode${RESET}`);
      console.log();
      printInfo("Or if already installed, add it to your PATH:");
      console.log(`     ${BLUE}setx PATH "%PATH%;%LOCALAPPDATA%\\Programs\\opencode"${RESET}`);
    } else {
      console.log(`     ${BLUE}curl -fsSL https://opencode.ai/install | bash${RESET}`);
      console.log();
      printInfo("Or if already installed, add it to your PATH:");
      console.log(`     ${BLUE}export PATH="$HOME/.local/bin:$PATH"${RESET}`);
      console.log(`     ${BLUE}export PATH="$HOME/.opencode/bin:$PATH"${RESET}`);
    }
    return { ok: false };
  }
  const version = await getOpenCodeVersion();
  const path5 = getOpenCodePath();
  const detectedVersion = version ?? "";
  const pathInfo = path5 ? ` (${DIM}${path5}${RESET})` : "";
  printSuccess(`OpenCode ${detectedVersion} detected${pathInfo}`);
  return { ok: true, version: version ?? undefined, path: path5 ?? undefined };
}
async function configureBackgroundSubagents(config) {
  const backgroundSubagentsEnabled = isBackgroundSubagentsEnabled(process.env.OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS);
  const exaEnabled = ["true", "1"].includes(process.env.OPENCODE_ENABLE_EXA?.toLowerCase() ?? "");
  if (backgroundSubagentsEnabled && exaEnabled) {
    printSuccess("OpenCode background subagents and Exa websearch already enabled in environment");
    return { enabledNow: true };
  }
  const target = config.backgroundSubagentsTarget !== undefined ? expandHomePath(config.backgroundSubagentsTarget) : detectBackgroundSubagentsTarget();
  if (config.backgroundSubagents === "no") {
    printInfo("OpenCode background subagents shell setup skipped.");
    console.log(manualBackgroundSubagentsInstructions({ targetPath: target }));
    return { enabledNow: false };
  }
  if (!target) {
    printInfo("No safe shell startup file detected.");
    console.log(manualBackgroundSubagentsInstructions());
    return { enabledNow: false };
  }
  const block = getBackgroundSubagentsBlock(target);
  if (config.dryRun) {
    printInfo("Dry run mode - background subagents block that would be written:");
    console.log(`Target: ${target}`);
    console.log(`
${block}
`);
    return { enabledNow: false, configuredTarget: target };
  }
  if (config.backgroundSubagents === "ask") {
    if (!process.stdin.isTTY) {
      printInfo("Skipped background subagents shell setup in non-TTY mode.");
      console.log(manualBackgroundSubagentsInstructions({ targetPath: target }));
      return { enabledNow: false };
    }
    console.log();
    printInfo("V2 requires OpenCode background subagents for default orchestration.");
    printInfo(`The installer can add the required environment exports to ${target}.`);
    const shouldWrite = await confirm("Enable background subagents and Exa websearch now?", true);
    if (!shouldWrite) {
      printInfo("Skipped background subagents shell setup.");
      console.log(manualBackgroundSubagentsInstructions({ targetPath: target }));
      return { enabledNow: false };
    }
  }
  try {
    writeBackgroundSubagentsBlock(target);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    printError(`Could not write background subagents shell config: ${message}`);
    printInfo("Add the setting manually instead:");
    console.log(manualBackgroundSubagentsInstructions({ targetPath: target }));
    return { enabledNow: false };
  }
  printSuccess(`Background subagents and Exa websearch enabled ${SYMBOLS.arrow} ${DIM}${target}${RESET}`);
  return { enabledNow: false, configuredTarget: target };
}
async function shouldInstallCompanion(config) {
  if (config.companion === "yes") {
    return true;
  }
  if (config.companion === "no")
    return false;
  if (config.dryRun) {
    printInfo("Dry run mode - would ask to install the desktop companion (default: no).");
    config.companion = "no";
    return false;
  }
  if (!process.stdin.isTTY) {
    printInfo("Skipped desktop companion prompt in non-TTY mode. Use --companion=yes to install it.");
    config.companion = "no";
    return false;
  }
  console.log();
  printInfo("The optional desktop companion shows live agent activity.");
  const shouldInstall = await confirm("Install and enable the desktop companion?", false);
  config.companion = shouldInstall ? "yes" : "no";
  if (!shouldInstall) {
    printInfo("Desktop companion install skipped.");
  }
  return shouldInstall;
}
function handleStepResult(result, successMsg) {
  if (!result.success) {
    printError(`Failed: ${result.error}`);
    return false;
  }
  printSuccess(`${successMsg} ${SYMBOLS.arrow} ${DIM}${result.configPath}${RESET}`);
  return true;
}
function handleOptionalCompanionResult(result) {
  if (result.success) {
    printSuccess(`Companion installed ${SYMBOLS.arrow} ${DIM}${result.configPath}${RESET}`);
    return;
  }
  printWarning(`Desktop companion install skipped: ${result.error}`);
  printInfo("The desktop companion is optional; continuing plugin installation without it.");
}
async function runInstall(config) {
  const detected = detectCurrentConfig();
  const isUpdate = detected.isInstalled;
  printHeader(isUpdate);
  const companionInstall = await shouldInstallCompanion(config);
  let totalSteps = 7;
  if (config.installCustomSkills)
    totalSteps += 1;
  if (companionInstall)
    totalSteps += 1;
  totalSteps += 1;
  let step = 1;
  printStep(step++, totalSteps, "Checking OpenCode installation...");
  if (config.dryRun) {
    printInfo("Dry run mode - skipping OpenCode check");
  } else {
    const { ok } = await checkOpenCodeInstalled();
    if (!ok)
      return 1;
  }
  printStep(step++, totalSteps, "Adding oh-my-opencode-slim plugin...");
  if (config.dryRun) {
    printInfo("Dry run mode - skipping plugin installation");
  } else {
    const pluginResult = await addPluginToOpenCodeConfig();
    if (!handleStepResult(pluginResult, "Plugin added"))
      return 1;
  }
  printStep(step++, totalSteps, "Adding TUI version badge...");
  if (config.dryRun) {
    printInfo("Dry run mode - skipping TUI plugin installation");
  } else {
    const tuiResult = await addPluginToOpenCodeTuiConfig();
    if (!tuiResult.success) {
      printInfo(`Skipped TUI badge: ${tuiResult.error}`);
    } else {
      handleStepResult(tuiResult, "TUI badge added");
    }
  }
  printStep(step++, totalSteps, "Warming OpenCode plugin cache...");
  if (config.dryRun) {
    printInfo("Dry run mode - skipping cache warm-up");
  } else {
    const cacheResult = await warmOpenCodePluginCache();
    if (cacheResult === null) {
      printInfo("Local development install - cache warm-up not required");
    } else if (!cacheResult.success) {
      printInfo(`Skipped cache warm-up: ${cacheResult.error}`);
    } else {
      handleStepResult(cacheResult, "OpenCode cache warmed");
    }
  }
  printStep(step++, totalSteps, "Disabling OpenCode default agents...");
  if (config.dryRun) {
    printInfo("Dry run mode - skipping agent disabling");
  } else {
    const agentResult = disableDefaultAgents();
    if (!handleStepResult(agentResult, "Default agents disabled"))
      return 1;
  }
  printStep(step++, totalSteps, "Enabling OpenCode LSP integration...");
  if (config.dryRun) {
    printInfo("Dry run mode - skipping LSP configuration");
  } else {
    const lspResult = enableLspByDefault();
    if (!handleStepResult(lspResult, "LSP enabled"))
      return 1;
  }
  printStep(step++, totalSteps, "Configuring OpenCode background subagents...");
  const backgroundSubagents = await configureBackgroundSubagents(config);
  if (companionInstall) {
    printStep(step++, totalSteps, "Installing desktop companion binary...");
    const companionResult = await installCompanion(config);
    handleOptionalCompanionResult(companionResult);
    if (!companionResult.success)
      config.companion = "no";
  }
  printStep(step++, totalSteps, "Writing oh-my-opencode-slim configuration...");
  if (config.dryRun) {
    const liteConfig = generateLiteConfig(config);
    printInfo("Dry run mode - configuration that would be written:");
    console.log(`
${JSON.stringify(liteConfig, null, 2)}
`);
  } else {
    const configPath2 = getExistingLiteConfigPath();
    const configExists = existsSync8(configPath2);
    if (configExists && !config.reset) {
      printInfo(`Configuration already exists at ${configPath2}. Use --reset to overwrite.`);
    } else {
      const liteResult = writeLiteConfig(config, configExists ? configPath2 : undefined);
      if (!handleStepResult(liteResult, configExists ? "Config reset" : "Config written"))
        return 1;
    }
  }
  if (config.installCustomSkills) {
    printStep(step++, totalSteps, "Synchronizing custom skills...");
    if (config.dryRun) {
      printInfo("Dry run mode - would synchronize custom skills:");
      for (const skill of CUSTOM_SKILLS) {
        printInfo(`  - ${skill.name}`);
      }
    } else {
      try {
        const packageRoot = fileURLToPath(new URL("../..", import.meta.url));
        const result = syncBundledSkillsFromPackage(packageRoot, {
          force: config.forceSkillSync
        });
        const categorizedSkipped = new Set([
          ...result.staged,
          ...result.adopted,
          ...result.customized
        ]);
        const preservedSkills = result.skippedExisting.filter((skill) => !categorizedSkipped.has(skill));
        if (result.installed.length > 0) {
          for (const skill of result.installed) {
            printSuccess(`Installed/Updated: ${skill}`);
          }
        }
        if (preservedSkills.length > 0) {
          for (const skill of preservedSkills) {
            printInfo(`Skipped/Preserved: ${skill}`);
          }
        }
        if (result.failed.length > 0) {
          for (const skill of result.failed) {
            if (skill === "__lock__") {
              printError("Lock acquisition failed");
            } else if (skill === "__manifest__") {
              printError("Manifest write failed");
            } else {
              printError(`Failed: ${skill}`);
            }
          }
        }
        if (result.staged.length > 0) {
          for (const skill of result.staged) {
            printInfo(`Staged for review: ${skill}`);
          }
        }
        if (result.adopted.length > 0) {
          for (const skill of result.adopted) {
            printInfo(`Adopted: ${skill}`);
          }
        }
        if (result.customized.length > 0) {
          for (const skill of result.customized) {
            printInfo(`Customized: ${skill}`);
          }
        }
        const realFailed = result.failed.filter((skill) => skill !== "__lock__" && skill !== "__manifest__");
        printSuccess(`Skill synchronization complete: ${result.installed.length} installed/updated, ${preservedSkills.length} skipped/preserved, ${result.staged.length} staged, ${result.adopted.length} adopted, ${result.customized.length} customized, ${realFailed.length} failed.`);
      } catch (err) {
        printError(`Failed to synchronize custom skills: ${err}`);
      }
    }
  }
  const statusMsg = isUpdate ? "Configuration updated!" : "Installation complete!";
  console.log(`${SYMBOLS.star} ${BOLD}${GREEN}${statusMsg}${RESET}`);
  console.log();
  console.log(`${BOLD}Next steps:${RESET}`);
  console.log();
  const configPath = getExistingLiteConfigPath();
  console.log("  1. Log in to the provider(s) you want to use:");
  console.log(`     ${BLUE}$ opencode auth login${RESET}`);
  console.log();
  console.log("  2. Refresh the models OpenCode can see:");
  console.log(`     ${BLUE}$ opencode models --refresh${RESET}`);
  console.log();
  console.log("  3. Review your generated config:");
  console.log(`     ${BLUE}${configPath}${RESET}`);
  console.log();
  console.log("  4. Start OpenCode:");
  if (backgroundSubagents.enabledNow) {
    console.log(`     ${BLUE}$ opencode${RESET}`);
  } else if (backgroundSubagents.configuredTarget) {
    console.log(`     ${BLUE}$ source ${backgroundSubagents.configuredTarget}${RESET}`);
    console.log(`     ${BLUE}$ opencode${RESET}`);
    console.log(`     ${DIM}Or restart your terminal before running opencode.${RESET}`);
  } else {
    console.log(`     ${BLUE}$ OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true OPENCODE_ENABLE_EXA=1 opencode${RESET}`);
  }
  console.log();
  console.log("  5. Verify the agents are responding:");
  console.log(`     ${BLUE}> ping all agents${RESET}`);
  console.log();
  const modelsInfo = config.preset && config.preset !== "openai" ? `Generated OpenAI and OpenCode Go presets; ${config.preset} is active.` : "Generated OpenAI and OpenCode Go presets; OpenAI is active by default.";
  console.log(`${modelsInfo}`);
  const altProviders = "For the full configuration reference, see:";
  console.log(altProviders);
  const docsUrl = "https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/docs/configuration.md";
  console.log(`  ${BLUE}${docsUrl}${RESET}`);
  console.log();
  await askToStarRepo(config);
  return 0;
}
async function install(args) {
  const config = {
    installCustomSkills: args.skills === "yes" || args.skills === "force",
    forceSkillSync: args.skills === "force",
    preset: args.preset,
    promptForStar: args.tui,
    dryRun: args.dryRun,
    reset: args.reset ?? false,
    backgroundSubagents: args.backgroundSubagents ?? "ask",
    backgroundSubagentsTarget: args.backgroundSubagentsTarget,
    companion: args.companion
  };
  return runInstall(config);
}

// src/cli/index.ts
function parseArgs(args) {
  const result = {
    tui: true,
    skills: "yes",
    companion: "ask"
  };
  for (const arg of args) {
    if (arg === "--no-tui") {
      result.tui = false;
    } else if (arg.startsWith("--skills=")) {
      const mode = arg.split("=")[1];
      if (!["yes", "no", "force"].includes(mode)) {
        console.error("Unsupported --skills value: use yes, no, or force");
        process.exit(1);
      }
      result.skills = mode;
    } else if (arg.startsWith("--companion=")) {
      const mode = arg.split("=")[1];
      if (!["ask", "yes", "no"].includes(mode)) {
        console.error("Unsupported --companion value: use ask, yes, or no");
        process.exit(1);
      }
      result.companion = mode;
    } else if (arg.startsWith("--preset=")) {
      const preset = arg.split("=")[1];
      if (!isGeneratedPresetName(preset)) {
        console.error(`Unsupported preset: ${preset}. Available presets: ${getGeneratedPresetNames().join(", ")}`);
        process.exit(1);
      }
      result.preset = preset;
    } else if (arg.startsWith("--background-subagents=")) {
      const mode = arg.split("=")[1];
      if (!["ask", "yes", "no"].includes(mode)) {
        console.error("Unsupported --background-subagents value: use ask, yes, or no");
        process.exit(1);
      }
      result.backgroundSubagents = mode;
    } else if (arg.startsWith("--background-subagents-target=")) {
      result.backgroundSubagentsTarget = arg.split("=")[1];
    } else if (arg === "--dry-run") {
      result.dryRun = true;
    } else if (arg === "--reset") {
      result.reset = true;
    } else if (arg === "-h" || arg === "--help") {
      printHelp();
      process.exit(0);
    }
  }
  result.backgroundSubagents ??= "ask";
  return result;
}
function printHelp() {
  console.log(`
oh-my-opencode-slim installer

Usage:
  bunx oh-my-opencode-slim install [OPTIONS]
  bunx oh-my-opencode-slim doctor [OPTIONS]

Options:
  --skills=yes|no|force  Install bundled skills; force replaces existing skill
                         directories (default: yes)
  --companion=ask|yes|no Install desktop companion binary and enable config
                         (default: ask; prompt defaults to no)
  --preset=<name>        Active generated config preset (default: openai)
  --background-subagents=ask|yes|no
                          Persist required OpenCode background subagent env
                          (default: ask; prompt defaults to yes)
  --background-subagents-target=<path>
                          Shell startup file to update
  --no-tui               Non-interactive mode
  --dry-run              Simulate install without writing files
  --reset                Force overwrite of existing configuration
  -h, --help             Show this help message

Doctor options:
  --json                 Print diagnostics as JSON

Available presets: ${getGeneratedPresetNames().join(", ")}

The installer generates OpenAI and OpenCode Go presets by default.
OpenAI is active unless --preset selects another generated preset.
For the full config reference, see docs/configuration.md.

Examples:
  bunx oh-my-opencode-slim install
  bunx oh-my-opencode-slim install --no-tui --skills=yes
  bunx oh-my-opencode-slim install --background-subagents=yes
  bunx oh-my-opencode-slim install --preset=opencode-go
  bunx oh-my-opencode-slim install --reset
  bunx oh-my-opencode-slim doctor
`);
}
async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0 || args[0] === "install") {
    const hasSubcommand = args[0] === "install";
    const installArgs = parseArgs(args.slice(hasSubcommand ? 1 : 0));
    const exitCode = await install(installArgs);
    process.exit(exitCode);
  } else if (args[0] === "doctor") {
    const doctorArgs = parseDoctorArgs(args.slice(1));
    const exitCode = await doctor(doctorArgs);
    process.exit(exitCode);
  } else if (args[0] === "-h" || args[0] === "--help") {
    printHelp();
    process.exit(0);
  } else {
    console.error(`Unknown command: ${args[0]}`);
    console.error("Run with --help for usage information");
    process.exit(1);
  }
}
if (__require.main == __require.module) {
  main().catch((err) => {
    console.error("Fatal error:", err);
    process.exit(1);
  });
}
export {
  parseArgs
};
