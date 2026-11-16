import { tool } from '@opencode-ai/plugin/tool';
import { fileURLToPath } from 'node:url';
import { existsSync, realpathSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { executeChartTool } from '../../tools/liuren-tool-transport.mjs';

function nodeExecutable() {
  if (!process.versions.bun) return process.execPath;
  const name = process.platform === 'win32' ? 'node.exe' : 'node';
  const candidates = (process.env.PATH || '').split(path.delimiter).filter(Boolean).map(dir => path.resolve(dir.replace(/^"|"$/g, ''), name));
  if (process.platform === 'win32') candidates.push(
    path.join(process.env.ProgramFiles || 'C:/Program Files', 'nodejs/node.exe'),
    path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'),
  );
  const executable = candidates.find(file => existsSync(file));
  if (!executable) throw new Error('找不到Node.js；请让本机OpenCode可访问node命令后再用直接排盘工具。');
  return executable;
}

export default tool({
  description: '本机大六壬一次调用排盘并自动导出完整JSON。直接执行原魔改引擎，无需浏览器、选时间控件或3456服务。返回全部12宫神煞、四课三传、核验结果和归档路径。已有可靠同盘时复用，不重复起课。活时报数/真太阳时暂不支持。',
  args: {
    mode: tool.schema.enum(['datetime', 'now', 'manual-pillars']).optional().describe('默认datetime；未指定占时用now，由程序取得北京时间；manual-pillars须完整原始四柱参数。'),
    datetime: tool.schema.string().optional().describe('北京时间公历YYYY-MM-DDTHH:mm，可附:00+08:00。不是事件发生时间；不传非零秒或其他时区。'),
    timezone: tool.schema.literal('Asia/Shanghai').optional(),
    time_basis: tool.schema.literal('civil').optional(),
    settings: tool.schema.object({
      yuejiang: tool.schema.enum(['中气换将', '交节换将', '日躔换将']).optional(),
      guiren: tool.schema.enum(['甲戊庚牛羊', '甲羊戊庚牛']).optional(),
      zhouye: tool.schema.enum(['自动选择', '昼贵', '夜贵']).optional(),
      shehai: tool.schema.enum(['孟仲季', '深度']).optional(),
    }).strict().optional(),
    pillars: tool.schema.object({ year: tool.schema.string(), month_branch: tool.schema.string(), day: tool.schema.string(), hour_branch: tool.schema.string() }).strict().optional(),
    month_general: tool.schema.string().optional().describe('仅四柱模式，须用户或来源明确给出的月将地支。'),
    reference_datetime: tool.schema.string().optional().describe('仅四柱模式的显示参考日期；不会认定为真实占时。'),
    participants: tool.schema.array(tool.schema.object({ sex: tool.schema.enum(['男', '女']), birth_year: tool.schema.number().int().optional(), age: tool.schema.number().int().optional() }).strict()).optional().describe('仅在出生年或原工具年龄明确时传入，birth_year与age必须有且只有一项。只有性别时省略participants，不猜出生年。'),
    declared_life: tool.schema.array(tool.schema.object({ birth_pillar: tool.schema.string(), sex: tool.schema.enum(['男', '女']).optional() }).strict()).optional().describe('birth_pillar须是用户明确给出的完整六十甲子，例如乙亥；仅给亥、寅等单支时省略本字段，在正文保留原信息，不猜天干或出生年。与未经核验的引擎年命计算分开。'),
    label: tool.schema.string().optional().describe('可选归档代号，1—32个文字/数字/下划线/连字符，不填姓名。'),
  },
  async execute(args, context) {
    // OpenCode runs tools in Bun. Launch Node explicitly; do not treat Bun's
    // process.execPath (the opencode executable) as a Node worker executable.
    const script = realpathSync.native(fileURLToPath(new URL('../../tools/liuren-direct.mjs', import.meta.url)));
    return executeChartTool(args, { nodePath: nodeExecutable(), scriptPath: script, signal: context.abort });
  },
});
