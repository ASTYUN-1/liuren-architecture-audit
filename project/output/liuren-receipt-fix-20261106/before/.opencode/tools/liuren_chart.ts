import { tool } from '@opencode-ai/plugin/tool';
import { fileURLToPath } from 'node:url';
import { realpathSync } from 'node:fs';
import { executeChartTool } from '../../tools/liuren-tool-transport.mjs';
import { resolveNodeExecutable } from '../../tools/liuren-node-runtime.mjs';
import { runChartWithShensha } from '../../tools/liuren-shensha.mjs';
import {buildFacts,focusFacts} from '../../tools/liuren-deterministic.mjs';

export default tool({
  description: '本机大六壬一次起课，按活动固定表修正神煞计算与导出，保存修正版及旧引擎原档。返回完整12宫、四课三传和神煞采用记录。神煞只属天盘tian，di仅为所临地盘。已有可靠同盘时复用，不重起。活时报数/真太阳时暂不支持。',
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
    if (context.abort.aborted) throw new Error('排盘调用已取消。');
    const result=await runChartWithShensha(async () => {
      // Validate a standalone interpreter for CLI, Bun and desktop hosts alike.
      const script = realpathSync.native(fileURLToPath(new URL('../../tools/liuren-direct.mjs', import.meta.url)));
      const nodePath = await resolveNodeExecutable({ signal: context.abort });
      const original = JSON.parse(await executeChartTool(args, { nodePath, scriptPath: script, signal: context.abort }));
      if (context.abort.aborted) throw new Error('排盘调用已取消。');
      return original;
    });
    if(result.ok&&result.facts)result.program_facts=focusFacts(buildFacts(result.facts));
    return JSON.stringify(result);
  },
});
