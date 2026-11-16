import fs from 'node:fs/promises';
import {buildFacts} from '../../tools/liuren-deterministic.mjs';
import {BASE_INDEX_PROFILE as p,LOCAL_STRENGTH_PROFILE as r} from '../../tools/liuren-chart-view.mjs';
import {localStrength} from '../../tools/liuren-local-strength.mjs';
const folder=new URL('./',import.meta.url);
const raw=JSON.parse(await fs.readFile(new URL('../../排盘存档/六壬/六壬-20261108-214237-基础状态接入验收-41b34a16-3c4e-400f-a551-35c73cd652da.corrected-7d8f4da2258d400a.json',folder),'utf8'));
const c=raw._direct.facts,d=buildFacts(c),audit=localStrength(d,c.month_branch,p,r);
await fs.writeFile(new URL('本课计算审计.json',folder),JSON.stringify(audit,null,2)+'\n');
const fmt=x=>Number(x).toFixed(4),label=id=>({'T':'天盘','D':'地盘','J':'天将','S':'日干'}[id[0]]+id.slice(2));
const ids=['T:申','J:青龙','T:酉','J:勾陈'];
const lines=['# 天地、阴神及神将的数值计算','',
'本课：2026-11-06 14:43。数值是固定研究参数的局部作用结果，未作真实预测验收。正式AI盘只显示作用后strength_index，旧基础值和收支明细在此供审阅。','',
'| 对象 | 四季原基础 → 生克后 | 季土原基础 → 生克后 |','| --- | ---: | ---: |'];
for(const id of ids){const a=audit.outputs['four-seasons'].solution.rows.find(n=>n.id===id),b=audit.outputs['quarter-earth'].solution.rows.find(n=>n.id===id);lines.push(`| ${label(id)} | ${fmt(a.base)} → ${fmt(a.value)} | ${fmt(b.base)} → ${fmt(b.value)} |`);}
lines.push('','生扶=0.20×通路×施者实际力量；泄耗=0.10×通路×施者实际力量；受克=0.20×通路×施者实际力量÷(1+受者实际力量/5)；施克成本为受克量的20%；比和配合=0.06×通路×施者实际力量。直接通路原始值1，阴神0.75，各施者输出通路总和最多2，同一作用不重复计。','',
'以下加减是求解收敛后的账本；天盘子与地盘子是不同位置主体，编号明确，不因同名合并。');
for(const [name,entry]of Object.entries(audit.outputs)){
 const s=entry.solution;lines.push('',`## ${name==='four-seasons'?'四季':'季土'}条件`,'',`共同求解${s.iterations}次，残差${s.residual}。`);
 for(const id of ids){
  const n=s.rows.find(n=>n.id===id);lines.push('',`### ${label(id)}`,'',`基础${fmt(n.base)} → 作用后${fmt(n.value)}；净变化${fmt(n.change)}。`,'','| 作用 | 对象 | 通路 | 增减分 |','| --- | --- | --- | ---: |');
  for(const e of s.ledger.filter(e=>e.target===id&&e.received!==0))lines.push(`| ${e.type==='克'?'受到克制':e.type==='生'?'受到生扶':'比和配合'} | ${label(e.source)} | ${e.routes.join('、')} | ${fmt(e.received)} |`);
  for(const e of s.ledger.filter(e=>e.source===id&&e.source_cost!==0))lines.push(`| ${e.type==='生'?'施生泄耗':'施克成本'} | ${label(e.target)} | ${e.routes.join('、')} | -${fmt(e.source_cost)} |`);
 }
}
lines.push('','## 计算边界','',
'本版已把天地、直接阴神、同宫神将及日干直接作用纳入数值。没有给所有十二宫两两建立远程生克，也没有自动给三合/三会、德煞、冲墓、贪生行为及刑冲破害附加统一倍数；这些尚未完成数值适配，保留在专业方法判断中。课传之间如果属于上述直接通路已计算，其他跨课传及异宫天将的远程作用尚未计入。',
'地盘以月令底数作为固定环境；不是一个自坐十二气的新神。日干仍按天干十二长生，支将按五行十二气。地盘环境这一建模约定没有等价于古籍定量验证。',
'旬空和坐空的同一损失只扣一次；天将不另继承一份旬空扣分。长生兼泄、临绝受生同时进入底数和关系收支，不另免费加一次修复分。',
'季土与四季仍是两套条件计算，不相加、平均或逐节点挑最大值；月令统一采用的历法边界仍待解决。参数尚未经验校准，因此不可把此分数称为客观能量、成功概率或直接套2.5删节点。',
'正式工具、CLI/Codex及子智能体核心共用同一个作用后结果，默认不附过程账本。新调用生效；运行中的OpenCode须重启。');
await fs.writeFile(new URL('两宫计算说明.md',folder),lines.join('\n')+'\n');
console.log(JSON.stringify({model:audit.model,iterations:Object.fromEntries(Object.entries(audit.outputs).map(([k,o])=>[k,o.solution.iterations]))}));
