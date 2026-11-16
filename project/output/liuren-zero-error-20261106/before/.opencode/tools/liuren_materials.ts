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
  description: '本机六壬限定资料入口。method元数据与完整book_search结果附handoff，可原样放进liuren_adjudication_packet.packet.method_materials，勿猜路径/hash/行号；handoff=null先按continuation补读。method按module ID读当前方法全文；不先全读。需查壬归、理法简易、天一群笔记时优先book_search，一次返回排序后的原段、相邻上下文及相关口径，queries可合并最多4个争点；已返完整原段不重复read。book_outline查三书目录。其他书用scan/books，必要时read补上下文。索引不证明整书精读或术理正确。无两库对照时不调用retrieve/cases/experience。shensha复核已有课盘；methods仅兼容审计。',
  args: {
    action: tool.schema.enum(['scope', 'method', 'methods', 'retrieve', 'scan', 'read', 'shensha', 'book_search', 'book_outline']),
    module: tool.schema.string().optional().describe('method必填：当前步骤模块ID，例如relationship、liqi、movement；一次返回该模块全文，不需batch或plan_id。'),
    library: tool.schema.enum(['methods', 'cases', 'experience', 'books', 'research']).optional(),
    query: tool.schema.string().optional().describe('短争点词。book_search按原词、章节和相关性排序返回原文；scan是全书库字面定位。不能传目录或脚本。'),
    queries: tool.schema.array(tool.schema.string()).min(1).max(4).optional().describe('仅book_search：一次合并最多4个相关争点，与query二选一；不要为凑批次扩大查书范围。'),
    book: tool.schema.enum(['RG', 'LF', 'TY']).optional().describe('book_search/book_outline可限定：RG壬归、LF理法简易、TY天一群笔记；不传时检索三本或显示三书概览。'),
    max_chars: tool.schema.number().int().min(2000).max(24000).optional().describe('book_search原文总字符预算，默认14000；含相关原文。超长段明确给续读位置。'),
    case_query: tool.schema.string().optional(),
    experience_query: tool.schema.string().optional(),
    category: tool.schema.string().optional().describe('例如失物占、感情占。'),
    limit: tool.schema.number().int().min(1).max(100).optional().describe('book_search总结果数1..12，默认4；scan上限100，retrieve上限50。'),
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
    if (args.limit !== undefined && args.action === 'book_search' && args.limit > 12)
      throw new Error('liuren_materials.limit: action=book_search只允许1..12，默认4；保留query/queries，仅改limit。scan仍允许1..100。');
    if (args.limit !== undefined && args.action === 'retrieve' && args.limit > 50)
      throw new Error('liuren_materials.limit: action=retrieve只允许1..50；当前无两库对照不执行retrieve。');
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
