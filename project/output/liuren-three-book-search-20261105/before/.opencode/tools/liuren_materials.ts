import { tool } from '@opencode-ai/plugin/tool';
import { execFile } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import os from 'node:os';
import { promisify } from 'node:util';

const run = promisify(execFile);
const script = fileURLToPath(new URL('../../tools/liuren-materials.py', import.meta.url));
const root = fileURLToPath(new URL('../../', import.meta.url));

async function pythonExecutable(signal: AbortSignal) {
  const name = process.platform === 'win32' ? 'python.exe' : 'python3';
  const envPath = Object.entries(process.env).find(([key]) => key.toUpperCase() === 'PATH')?.[1] || '';
  const candidates = envPath.split(path.delimiter).filter(Boolean).map(p => path.resolve(p.replace(/^"|"$/g, ''), name));
  if (process.platform === 'win32') candidates.push(
    path.join(process.env.ProgramFiles || 'C:/Program Files', 'Python313/python.exe'),
    path.join(os.homedir(), 'AppData/Local/Programs/Python/Python313/python.exe'),
  );
  for (const executable of [...new Set(candidates)]) {
    if (signal.aborted) throw new Error('资料读取已取消。');
    if (!existsSync(executable) || /WindowsApps/i.test(executable)) continue;
    try {
      const result = await run(executable, ['-X', 'utf8', '-c', 'import sys; print("LIUREN_PYTHON_3" if sys.version_info >= (3,9) else "unsupported")'],
        { encoding: 'utf8', windowsHide: true, timeout: 4000, signal });
      if (result.stdout.trim() === 'LIUREN_PYTHON_3') return executable;
    } catch { if (signal.aborted) throw new Error('资料读取已取消。'); }
  }
  throw new Error('没有找到可执行本机检索的 Python 3；请切换 Build 模式排查，不开放全盘扫描。');
}

export default tool({
  description: '本机六壬限定资料入口。普通研判用method按module ID一次读取当前步骤的方法全文，读后即分析；不先读全套。案例经验retrieve按活动实验策略启停；无两库对照时不调用。scan定位原文、read读原档、shensha复核已有课盘；methods仅供旧批次兼容审计。',
  args: {
    action: tool.schema.enum(['scope', 'method', 'methods', 'retrieve', 'scan', 'read', 'shensha']),
    module: tool.schema.string().optional().describe('method必填：当前步骤模块ID，例如relationship、liqi、movement；一次返回该模块全文，不需batch或plan_id。'),
    library: tool.schema.enum(['methods', 'cases', 'experience', 'books', 'research']).optional(),
    query: tool.schema.string().optional().describe('短争点词；scan按空格分词，不接受任意目录或正则脚本。'),
    case_query: tool.schema.string().optional(),
    experience_query: tool.schema.string().optional(),
    category: tool.schema.string().optional().describe('例如失物占、感情占。'),
    limit: tool.schema.number().int().min(1).max(100).optional(),
    domains: tool.schema.array(tool.schema.string()).optional().describe('methods的当前占类ID，例如lost-person-object。'),
    timing: tool.schema.boolean().optional(),
    nianming: tool.schema.boolean().optional(),
    conditions: tool.schema.array(tool.schema.string()).optional(),
    batch: tool.schema.number().int().min(1).optional(),
    plan_id: tool.schema.string().optional().describe('仅旧methods兼容接口：每次仍须带完整路由参数；本标识不恢复路由，不是普通研判的续读方式。'),
    full_plan: tool.schema.boolean().optional().describe('显式回查完整计划；上下文丢失时使用。'),
    path: tool.schema.string().optional().describe('read资料路径；shensha复用排盘存档/六壬中的完整JSON，不重起课。'),
    start: tool.schema.number().int().min(1).optional(),
    count: tool.schema.number().int().min(1).max(300).optional(),
  },
  async execute(args, context) {
    const python = await pythonExecutable(context.abort);
    try {
      const request = { ...args, _context_key: context.sessionID };
      const result = await run(python, ['-X', 'utf8', script, '--request', JSON.stringify(request)],
        { cwd: root, encoding: 'utf8', windowsHide: true, shell: false, timeout: 90000,
          maxBuffer: 4 * 1024 * 1024, signal: context.abort });
      return result.stdout;
    } catch (error: any) {
      if (context.abort.aborted) throw new Error('资料读取已取消。');
      throw new Error(error.stderr?.trim() || '本机限定资料工具执行失败；不改用全盘扫描。');
    }
  },
});
