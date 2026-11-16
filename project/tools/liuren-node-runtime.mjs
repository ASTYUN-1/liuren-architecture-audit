import { execFile } from 'node:child_process';
import { existsSync, realpathSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);
const marker = 'liuren-node-runtime-v1';
const probeScript = `process.stdout.write(JSON.stringify({marker:${JSON.stringify(marker)},release:process.release.name,node:process.versions.node,bun:process.versions.bun,electron:process.versions.electron}))`;

// Desktop OpenCode can expose process.versions.node without versions.bun.
// Its execPath is still OpenCode.exe, not a standalone Node interpreter.
export function nodeCandidates({ execPath = process.execPath, env = process.env, platform = process.platform, home = os.homedir() } = {}) {
  const paths = platform === 'win32' ? path.win32 : path.posix;
  const name = platform === 'win32' ? 'node.exe' : 'node';
  const candidates = [];
  if (paths.basename(execPath).toLowerCase() === name) candidates.push(execPath);
  const searchPath = Object.entries(env).find(([key]) => key.toUpperCase() === 'PATH')?.[1] || '';
  candidates.push(...searchPath.split(paths.delimiter).filter(Boolean).map(dir => paths.resolve(dir.replace(/^"|"$/g, ''), name)));
  if (platform === 'win32') candidates.push(
    paths.join(env.LOCALAPPDATA || paths.join(home, 'AppData/Local'), 'Programs/nodejs/node.exe'),
    paths.join(env.ProgramFiles || 'C:/Program Files', 'nodejs/node.exe'),
    paths.join(home, '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'),
  );
  const seen = new Set();
  return candidates.filter(candidate => {
    const key = platform === 'win32' ? candidate.toLowerCase() : candidate;
    if (seen.has(key)) return false;
    seen.add(key); return true;
  });
}

export async function probeNodeExecutable(executable, signal) {
  if (signal?.aborted) throw new Error('排盘调用已取消。');
  try {
    // A version string or exit code 0 is insufficient: packaged hosts can
    // return successfully without evaluating a script. This runs no chart.
    const { stdout } = await execFileAsync(executable, ['--input-type=commonjs', '-e', probeScript], {
      windowsHide: true, shell: false, timeout: 4000, maxBuffer: 16384,
      encoding: 'utf8', signal,
    });
    const result = JSON.parse(stdout.trim());
    return result.marker === marker && result.release === 'node' &&
      /^\d+\./.test(result.node || '') && !result.bun && !result.electron;
  } catch {
    if (signal?.aborted) throw new Error('排盘调用已取消。');
    return false;
  }
}

export async function resolveNodeExecutable({ signal, probe = probeNodeExecutable, exists = existsSync, canonical = realpathSync.native, ...host } = {}) {
  for (const candidate of nodeCandidates(host)) {
    if (signal?.aborted) throw new Error('排盘调用已取消。');
    try {
      if (exists(candidate) && await probe(candidate, signal)) return canonical(candidate);
    } catch (error) {
      if (signal?.aborted) throw error;
      // An inaccessible/stale PATH entry must not hide a working installation.
    }
  }
  throw new Error('找不到可执行脚本的独立 Node.js；已检查本机 node 路径，未启动排盘。OpenCode.exe 不能作为 Node.js 使用。');
}
