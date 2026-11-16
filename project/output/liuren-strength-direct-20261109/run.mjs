import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {loadStrengthSource,analyzeStrengthChart} from '../../tools/liuren-strength.mjs';
import {chartView,formatChart} from '../../tools/liuren-chart-view.mjs';
const root=process.cwd();
const out=path.join(root,'output/liuren-strength-direct-20261109');
await fs.mkdir(out,{recursive:true});
const json=async file=>JSON.parse((await fs.readFile(file,'utf8')).replace(/^\uFEFF/,''));
const digest=async file=>createHash('sha256').update(await fs.readFile(file)).digest('hex');
const hiringFile=(await json('output/liuren-energy-prototype-20261108/fixed-v02/本课固定参数计算.json')).chart_archive;
const cases=[
 {id:'应聘盘',file:hiringFile,context:{seasonProfile:'four-seasons',seasonBasis:'原盘申月金旺，不涉季土边界',phase:'outcome',goal:{id:'work-to-day',target:'S:庚',mode:'external'}},subjects:['申','午','戌']},
 {id:'寅午戌盘',file:'output/liuren-energy-yin-20261106-1443/chart-result.json',context:{seasonProfile:'quarter-earth',seasonBasis:'原盘11月6日戌月末；沿用该研究盘季土用事条件，不推为全戌月规则',phase:'outcome',goal:{id:'movement-to-day',target:'S:甲',mode:'movement'}},subjects:['寅','午','戌','丑','辰','子','亥']}
];
const protectedFiles=[...cases.map(c=>c.file),'.opencode/liuren-active.json','tools/liuren-base-index-profile.json','tools/liuren-local-strength-profile.json'];
const before=await Promise.all(protectedFiles.map(async file=>({file,sha256:await digest(file)})));
const artifacts=[];
for(const item of cases){
 const source=await loadStrengthSource(item.file),result=analyzeStrengthChart(source.facts,item.context,source);
 const old=formatChart(chartView(source.facts,{shensha:source.shensha,conventions:source.conventions}));
 const folder=path.join(out,item.id);await fs.mkdir(folder,{recursive:true});
 await fs.writeFile(path.join(folder,'计算条件.json'),JSON.stringify(item.context,null,2)+'\n');
 await fs.writeFile(path.join(folder,'AI盘.json'),formatChart(result.chart));
 await fs.writeFile(path.join(folder,'计算审计.json'),JSON.stringify(result.calculation,null,2)+'\n');
 await fs.writeFile(path.join(folder,'结果摘要.json'),JSON.stringify(result.summary,null,2)+'\n');
 const current=formatChart(chartView(source.facts,{shensha:source.shensha,conventions:source.conventions}));
 if(current!==old)throw Error('研究调用改变默认导出');
 artifacts.push({id:item.id,input:item.file,source_sha256:await digest(item.file),phase:item.context.phase,
  research_chart_bytes:Buffer.byteLength(formatChart(result.chart)),default_chart_unchanged:true,
  convergence:result.calculation.audit.convergence,
  known_feedback:item.id==='应聘盘',subject_rows:result.calculation.rows.filter(r=>r.kind==='branch'&&item.subjects.includes(r.symbol)).map(r=>({symbol:r.symbol,E:r.strength,A:r.action_index,partial_A:r.partial_action_index,void_self:r.void_self,void_ground:r.void_ground,pending:r.pending})),
  coverage:result.calculation.coverage});
}
for(const f of before)if(await digest(f.file)!==f.sha256)throw Error('受保护来源改变 '+f.file);
await fs.writeFile(path.join(out,'验收记录.json'),JSON.stringify({model:'liuren-strength-research-v05-direct',protected_files:before,source_and_active_unchanged:true,artifacts},null,2)+'\n');
const lines=['# 实施与复算结果','',
 '2026年11月9日。已按用户纠正收紧为直接加临生克：天地、同宫神将、本节点直接阴神；无跨宫课传或将地生克。原先扩大的通路已移除。研究入口显式调用，默认盘和裁决口径保留。用户后续要求合局先不做，三合、半合、三会仅保留成员事实，无数值加权，也不作为待办阻止其他计算。','',
 '以下E是本版已实现范围内的研究旺衰值；A为空表示尚有必要专项未适配，不能用局部A冒充完整A。应聘盘结果已知，仅作开发盘，不证明预测正确。','',
 '| 盘 | 类神 | 旬空/坐空 | E | A | 尚未适配条数 |','|---|---|---|---:|---:|---:|'];
for(const a of artifacts)for(const r of a.subject_rows)lines.push(`| ${a.id} | ${r.symbol} | ${[r.void_self?'旬空':'',r.void_ground?'坐空':''].filter(Boolean).join('、')||'无'} | ${r.E.toFixed(3)} | ${r.A===null?'未完成':r.A.toFixed(3)} | ${r.pending.length} |`);
lines.push('','两张盘均用0、5、10三个初值求解，得到一致结果；这说明所测输入数值稳定，不证明所有盘唯一收敛或专业预测有效。',
 '','## 查看入口','',
 '- [应聘盘AI盘](</C:/Users/QLMa_/Documents/六壬八字测算/output/liuren-strength-direct-20261109/应聘盘/AI盘.json>)',
 '- [应聘盘完整计算账本](</C:/Users/QLMa_/Documents/六壬八字测算/output/liuren-strength-direct-20261109/应聘盘/计算审计.json>)',
 '- [寅午戌盘AI盘](</C:/Users/QLMa_/Documents/六壬八字测算/output/liuren-strength-direct-20261109/寅午戌盘/AI盘.json>)',
 '- [寅午戌盘完整计算账本](</C:/Users/QLMa_/Documents/六壬八字测算/output/liuren-strength-direct-20261109/寅午戌盘/计算审计.json>)',
 '','## 当前仍有缺口','',
 '刑冲破害等已支持按真实关系选择具体作用，但尚未将所有占类的原文条件自动编译；部分神煞专项仍无完整事件适配。主智能体可以在有依据时提交结构化条件，不需要复算五气、长生或神煞起法。未知必要条件保留pending；工具不裁录用、行业、职级或成败。',
 '','详细使用与参数见[说明](</C:/Users/QLMa_/Documents/六壬八字测算/docs/综合旺衰研究计算器.md>)。','');
await fs.writeFile(path.join(out,'实施与复算结果.md'),lines.join('\n'));
console.log(JSON.stringify({out,source_and_active_unchanged:true,cases:artifacts.map(a=>({id:a.id,pending:a.coverage.pending.length,subjects:a.subject_rows.map(x=>({symbol:x.symbol,E:x.E,A:x.A}))}))}));
