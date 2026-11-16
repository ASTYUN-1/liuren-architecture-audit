import { tool } from '@opencode-ai/plugin/tool';
import { fileURLToPath } from 'node:url';
import { realpathSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import {withTrialChartBasis} from '../../tools/liuren-trial-decision.mjs';
import { executeChartTool } from '../../tools/liuren-tool-transport.mjs';
import { resolveNodeExecutable } from '../../tools/liuren-node-runtime.mjs';
import { runChartWithShensha } from '../../tools/liuren-shensha.mjs';
import {exportAIChart} from '../../tools/liuren-chart-view.mjs';
import {lifeInputSchema} from '../../tools/liuren-year-life.mjs';

export default tool({
  description: '本机大六壬一次起课，返回合并正式盘facts及可查看的chart_file：完整12宫、四课三传、日干寄宫、旬空/坐空、已采用神煞、支将基础状态和具版本研究局部生克指数。程序结果直接采信；archive仅供compute/packet原样传递，无需打开。固定占断和工程校验不交给模型。已有同盘复用。活时报数/真太阳时暂不支持。',
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
    participants: tool.schema.array(lifeInputSchema(tool.schema)).optional().describe('传用户给定出生年、本命或行年；无需生日。工具计算year_life供直接使用，缺性别只影响行年顺逆候选。本数组与declared_life相同下标指同一人；同人资料尽量放同一对象，不传姓名。'),
    declared_life: tool.schema.array(lifeInputSchema(tool.schema)).optional().describe('兼容明确本命/行年输入，接受甲子或申等单支，用户给定直接采用。同下标与participants合并，明确本命优先整年推算；推荐同人资料放同一对象。'),
    label: tool.schema.string().optional().describe('可选归档代号，1—32个文字/数字/下划线/连字符，不填姓名。'),
  },
  async execute(args, context) {
    if (context.abort.aborted) throw new Error('排盘调用已取消。');
    const rawResult=await runChartWithShensha(async () => {
      // Validate a standalone interpreter for CLI, Bun and desktop hosts alike.
      const script = realpathSync.native(fileURLToPath(new URL('../../tools/liuren-direct.mjs', import.meta.url)));
      const nodePath = await resolveNodeExecutable({ signal: context.abort });
      const original = JSON.parse(await executeChartTool(args, { nodePath, scriptPath: script, signal: context.abort }));
      if (context.abort.aborted) throw new Error('排盘调用已取消。');
      return original;
    },{sidecar:false});
    const pointer=JSON.parse(await readFile(new URL('../liuren-active.json',import.meta.url),'utf8'));
    const trial=context.agent==='liuren'&&pointer.classSelectionTrial?.enabled===true&&pointer.classSelectionTrial?.decisionBasis?.enabled===true;
    const result=await exportAIChart(rawResult,trial?{seasonProfile:'quarter-earth'}:{});
    return JSON.stringify(trial?withTrialChartBasis(result):result);
  },
});
