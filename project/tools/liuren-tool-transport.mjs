import fs from 'node:fs/promises';
import { spawn } from 'node:child_process';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

export const TRANSPORT_ROOT = fileURLToPath(new URL('../tmp/liuren-tool-transport/', import.meta.url));
export const TRANSPORT_VERSION = '20261103-node-04';

function launchProcess(nodePath, scriptPath, directory, signal) {
  return new Promise((resolve, reject) => {
    let stdout = '', stderr = '', startError;
    const child = spawn(nodePath, [scriptPath, '--exchange', directory], {
      windowsHide: true, shell: false, signal, timeout: 60000,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
    child.stdout.on('data', chunk => { stdout = (stdout + chunk).slice(0, 4096); });
    child.stderr.on('data', chunk => { stderr = (stderr + chunk).slice(0, 4096); });
    // Wait for close even after abort: do not delete files while the process
    // may still be writing its response.
    child.on('error', error => { startError = error; });
    child.on('close', (code, signal) => {
      if (startError) reject(startError);
      else resolve({ code, signal, stdout, stderr });
    });
  });
}

export async function executeChartTool(input, { nodePath, scriptPath, signal, launch = launchProcess } = {}) {
  if (signal?.aborted) throw new Error('排盘调用已取消。');
  await fs.mkdir(TRANSPORT_ROOT, { recursive: true });
  const directory = await fs.mkdtemp(path.join(TRANSPORT_ROOT, 'request-'));
  const requestId = crypto.randomUUID();
  const requestPath = path.join(directory, 'request.json');
  const responsePath = path.join(directory, 'response.json');
  let processResult, outcome = 'failed';
  try {
    await fs.writeFile(requestPath, JSON.stringify({ schema: 'liuren-tool-request-v1', request_id: requestId, input }), { encoding: 'utf8', flag: 'wx' });
    processResult = await launch(nodePath, scriptPath, directory, signal);
    const { code, signal: exitSignal } = processResult;
    if (exitSignal || ![0, 1, 2].includes(code)) throw new Error(`排盘进程异常退出（退出码=${code}，信号=${exitSignal || '无'}）。`);
    let envelope;
    try { envelope = JSON.parse(await fs.readFile(responsePath, 'utf8')); }
    catch { throw new Error(`排盘结果文件缺失或无效（退出码=${code}，传输版本=${TRANSPORT_VERSION}）；已记录启动诊断，未自动重复排盘。`); }
    const result = envelope.result;
    if (envelope.schema !== 'liuren-tool-response-v1' || envelope.request_id !== requestId ||
        !result || typeof result.ok !== 'boolean' ||
        !(result.schema === 'liuren-direct-result-v1' || (result.ok === false && result.error)) ||
        (result.ok === true && code !== 0)) throw new Error('排盘响应标识、结构或退出状态不匹配，拒绝读取其他请求的结果。');
    outcome = result.ok ? 'ok' : 'rejected-input-or-chart';
    return JSON.stringify(result);
  } finally {
    // No question, year-life input, or complete chart is copied to this log.
    const trace = { version: TRANSPORT_VERSION, at: new Date().toISOString(), request_id: requestId,
      host: { node: process.versions.node, bun: process.versions.bun }, node: nodePath,
      outcome, code: processResult?.code, signal: processResult?.signal,
      stdout_bytes: Buffer.byteLength(processResult?.stdout || ''), stdout_hex_prefix: Buffer.from(processResult?.stdout || '').subarray(0, 16).toString('hex'),
      stderr_bytes: Buffer.byteLength(processResult?.stderr || '') };
    await fs.appendFile(path.join(TRANSPORT_ROOT, 'events.jsonl'), JSON.stringify(trace) + '\n').catch(() => {});
    await fs.unlink(requestPath).catch(() => {});
    await fs.unlink(responsePath).catch(() => {});
    await fs.rmdir(directory).catch(() => {});
  }
}
