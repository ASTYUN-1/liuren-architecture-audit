// Read-only engine/policy audit. Only writes evidence beside this script.
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadShenshaPolicy} from '../../tools/liuren-shensha.mjs';
const OUT=path.dirname(fileURLToPath(import.meta.url)),ROOT=path.resolve(OUT,'../..');
const read=p=>fs.readFileSync(path.join(ROOT,p),'utf8');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const manifest=JSON.parse(read('tools/liuren-direct/legacy-engine-manifest.json'));
for(const f of manifest.files)if(sha(fs.readFileSync(path.join(ROOT,'排盘工具魔改',f.path)))!==f.sha256)throw Error('Engine changed: '+f.path);
const {policy,sha256:policyHash}=await loadShenshaPolicy(ROOT);
const noop=()=>{},ctx=vm.createContext({console:{log:noop,warn:noop,error:noop},window:{addEventListener:noop,indexedDB:{open:()=>({})}},document:{addEventListener:noop},setTimeout:noop,clearTimeout:noop,setInterval:noop,clearInterval:noop,vm_glob:{USER_ALL_DATA:{pages_config:{zhuti_config:{zhuti_bord_clor:'#cccccc'}}}}});
for(const f of ['js/lunar.js','js/data.js','js/hexin.js','js/api.js','js/guize.js','js/paipan.js'])vm.runInContext(read('排盘工具魔改/'+f),ctx,{filename:f,timeout:15000});
const js=read('排盘工具魔改/index.js'),start=js.indexOf('function getCurrentSolarTerm('),end=js.indexOf('function enterFullscreenElement(',start);
if(start<0||end<start)throw Error('Missing helper');
vm.runInContext(js.slice(start,end),ctx);
const html=read('排盘工具魔改/index.html'),marker=html.indexOf('<pre id="paipan-json-ai"'),es=html.indexOf('(function() {',marker),ee=html.indexOf('</script>',es);
if(marker<0||es<0||ee<es)throw Error('Missing exporter');
const keyNames=JSON.parse(html.match(/var KEY_SS = (\[[^;]+\]);/)[1].replaceAll("'",'"'));
const GAN=[...'甲乙丙丁戊己庚辛壬癸'],ZHI=[...'子丑寅卯辰巳午未申酉戌亥'];
const base={Date:'2026-11-09',Time:'12:00',yuejiang:'中气换将',guiren:'甲戊庚牛羊',zhouye:'自动选择',shehai:'孟仲季',user:[],cundang:{ws:'',dy:'',fk:'',tag:'inventory'},zhenghuoshi:'四柱',sizhu:{yg:'甲',yz:'子',mz:'寅',dg:'甲',dz:'子',hz:'午',yuejiang:'寅'}};
const inputs=Array.from({length:60},(_,i)=>({...base,sizhu:{...base.sizhu,yg:GAN[i%10],yz:ZHI[i%12],dg:GAN[i%10],dz:ZHI[i%12]}}));
for(const mz of ZHI)for(const zhouye of ['昼贵','夜贵'])inputs.push({...base,zhouye,sizhu:{...base.sizhu,mz}});
for(const hz of ZHI)inputs.push({...base,sizhu:{...base.sizhu,hz}});
const groups={},observations=new Map(),exported=new Set(),samples=[];
for(const [i,input]of inputs.entries()){
 ctx.input=input;
 vm.runInContext('P=LiuRenPaiPan(JSON.parse(JSON.stringify(input)))',ctx,{timeout:20000});
 const P=ctx.P,timers=[],element={textContent:''};
 P.id='inventory-'+i;ctx.vm_paipan={currentPpdata:[P]};ctx.document.getElementById=id=>id==='paipan-json-ai'?element:null;ctx.setInterval=fn=>{timers.push(fn);return timers.length;};
 vm.runInContext(html.slice(es,ee),ctx,{timeout:15000});timers[0]();timers[1]();
 if(!element.textContent)throw Error('Empty export '+i);
 const raw=JSON.parse(element.textContent),names=new Set(raw.tiandipan.flatMap(r=>r.shensha));
 for(const n of names)exported.add(n);
 for(const [g,items]of Object.entries(P.shensha_list)){
  groups[g]??=[];
  for(const [n,v]of Object.entries(items)){
   if(!groups[g].includes(n))groups[g].push(n);
   const id=g+':'+n;
   if(!observations.has(id))observations.set(id,{group:g,name:n,values:[],seen:0,export_seen:0,missing_samples:[]});
   const o=observations.get(id),values=Array.isArray(v)?v:[v];o.seen++;if(names.has(n))o.export_seen++;
   for(const x of values)if(!o.values.includes(x))o.values.push(x);
   if(!names.has(n)&&o.missing_samples.length<3)o.missing_samples.push({input:input.sizhu,value:v});
  }
 }
 samples.push({id:i,mode:'manual-pillars-synthetic',pillars:raw.basic.pillars,names_count:names.size,key_count:new Set(raw.keyShensha.map(x=>x.name)).size,not_exported:[...new Set(Object.values(P.shensha_list).flatMap(g=>Object.keys(g)))].filter(n=>!names.has(n))});
}
const names=[...new Set(Object.values(groups).flat())],aliases=new Set(policy.rules.flatMap(r=>r.aliases));
const indexNames=read('runtime/liuren/'+policy.release+'/references/shensha-engine-index.md').split(/\r?\n/).filter(l=>/^\| [^|]+ \| (sui|ji|yue|xun|dg|dz)/.test(l)).map(l=>l.split('|')[1].trim());
const rows=names.map(n=>({name:n,groups:Object.entries(groups).filter(([,ns])=>ns.includes(n)).map(([g])=>g),export_seen:exported.has(n),adopted_rule_ids:policy.rules.filter(r=>r.aliases.includes(n)).map(r=>r.id),status:policy.disabled.includes(n)?'explicitly_disabled':aliases.has(n)?'adopted_alias':'unregistered',observations:[...observations.values()].filter(r=>r.name===n)}));
const specialNote=n=>n==='贵人'?'贵人作为十二天将之一另有正式盘字段；此状态仅指神煞采用表':n==='岁德'?'内部值为甲/庚/丙/壬/戊；本轮未进入十二宫JSON':n==='旬盗'?'条件性字段，部分输入不生成':n==='干胎神'||n==='支胎神'?'仅原引擎此神煞标签停用，不代表胎爻专项退出':/^(岁刑|岁破|月刑|月害|月合|支刑|支破|支冲|支害|日官|日鬼)$/.test(n)?'关系或身份项应另核正式盘关系层，不能将未登记解释为所有相关计算均缺失':'';
const result={date:'2026-11-09',release:policy.release,policy_sha256:policyHash,engine_manifest:manifest,scope:'Synthetic manual-pillar inventory, not a divination or exhaustive correctness test',sample_count:inputs.length,counts:{group_entries:Object.values(groups).reduce((n,g)=>n+g.length,0),distinct_names:names.length,export_seen:exported.size,adopted_rules:policy.rules.length,disabled_names:policy.disabled.length},groups,not_export_seen:names.filter(n=>!exported.has(n)),keyShensha_whitelist:keyNames,keyShensha_not_seen:keyNames.filter(n=>!exported.has(n)),historical_index_only:indexNames.filter(n=>!names.includes(n)),runtime_only:names.filter(n=>!indexNames.includes(n)),rows,rules:policy.rules,disabled_names:policy.disabled,samples};
fs.writeFileSync(path.join(OUT,'神煞清点.json'),JSON.stringify(result,null,2)+'\n');
const statusText={adopted_alias:'已登记名称或别名（以固定表重算）',explicitly_disabled:'明确停用此标签',unregistered:'未登记为正式采用神煞'};
const csv=[['原引擎名称','基准组','JSON全量曾导出','现行规则ID','当前状态','备注','本轮专业核查结论','增补决定'],...rows.map(r=>[r.name,r.groups.join('、'),r.export_seen?'是':'未观察到',r.adopted_rule_ids.join('、'),statusText[r.status],specialNote(r.name),'',''])].map(r=>r.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\r\n');
fs.writeFileSync(path.join(OUT,'神煞核查台账.csv'),'\uFEFF'+csv+'\r\n');
const labels={sui:'岁',ji:'季',yue:'月',xun:'旬',dg:'日干',dz:'日支'};
const lines=['# 当前排盘引擎、导出与采用神煞对照','',`核对日期：2026-11-09。活动版本：${policy.release}。`,'',
'本次清点核对当前源文件、活动采用表和96组受控四柱输入，不作占断。覆盖六十甲子的年/日输入、十二月建与四季、昼夜贵人、十二时支；不是所有参数组合的穷举，也不是全部起法或预测有效性验收。本脚本只读取已生效36版，不修改引擎、活动表、冻结包或历史盘；本轮新增关神的接入另见接入说明。','',
'## 数量及导出边界','',
'| 层次 | 数量 | 含义 |','|---|---:|---|',
`| 原引擎分组字段 | ${result.counts.group_entries} | 六个基准组；同名跨组分计 |`,
`| 原引擎去重名称 | ${names.length} | 含别名及部分关系/身份标签，不等于独立神煞数 |`,
`| 原页面全量JSON实际观察到 | ${exported.size} | tiandipan[].shensha；岁德未进入此结构 |`,
`| keyShensha摘要白名单 | ${keyNames.length} | 其中月将未作为神煞命中；月将有basic.jiang独立字段 |`,
`| 我们的现行固定规则 | ${policy.rules.length} | 原32个常用编号族及6条细分规则，另增S33关神 |`,
`| 原引擎名称匹配现行别名 | ${rows.filter(r=>r.status==='adopted_alias').length} | 名称/别名数不等于规则数；别名合并、额外细分项目须分别看 |`,
`| 明确停用名称 | ${policy.disabled.length} | 其中岁德也未进入十二宫导出 |`,
`| 其余未登记名称 | ${rows.filter(r=>r.status==='unregistered').length} | 未自动采用，不等于已判错；贵人和关系计算另分层 |`,'',
'原页面十二宫全量导出与keyShensha是不同层。JSON中名称已摊平，丢失岁/月/季/日干等原分组身份；同名跨组必须回查运行对象，不按同名自动合并。当前修正版内部归档保留未登记旧标签，但AI正式盘heaven_earth[].shensha只展示采用表中本盘resolved的[编号,名称]，缺失/停用项不自动进入判断。','',
'岁德：本轮内部输出天干甲、庚、丙、壬、戊，未转换到十二宫神煞数组。可从运行对象提取原始值，但不能说当前页面JSON已给出其完整落宫。此项也在明确停用表内。','',
'## 原引擎可计算的名称（按原组）',''];
for(const [g,ns]of Object.entries(groups))lines.push(`### ${labels[g]}煞 ${g}：${ns.length}个字段`,'',ns.join('、')+'。','');
lines.push('五个跨组同名为：天盗（季/日干）、金神（月/日支）、天贼（月/日干）、直符（月/日干）、天解（月/日干）。所以177个字段去重为172名。旬盗为条件生成，不能由单张盘缺失认定引擎不支持。','',
'## 导出清单','',
'全量JSON：上列172名中，本轮已观察到除岁德以外的171名。不是每张盘必含171名；旬盗等有生成条件。','',
'keyShensha白名单：'+keyNames.join('、')+'。','',
'其中月将只是白名单项，本轮没有在神煞数组中命中；月将值另在basic.jiang。白名单因此是18项配置、17名实际观察到的摘要神煞。','',
'## 我们已选的原32个常用编号族、S33与39条现行规则','',
'规则编号保留原身份；细分增加S08M、S21S、S30Z、S30J、S31Y、S32D六条。日德/干德是别名合并，不计两条。','',
'| 编号 | 现行名称 | 输入基准 | 引擎别名/导出别名 |','|---|---|---|---|');
const basis={year_branch:'年支',year_stem:'年干',season:'月建所属季',month_index:'节月序（寅起正月）',month_branch:'月建',day_stem:'日干',day_branch:'日支',xun:'日柱旬',opposite_nobleman:'本盘昼夜相反贵人'};
for(const r of policy.rules)lines.push(`| ${r.id} | ${r.name} | ${basis[r.basis]} | ${r.aliases.join('、')} |`);
lines.push('',
'阳刃S31：只采用五阳干位置；乙丁己辛癸对应分支停用。羊刃S31Y另按十干全表，不能替代阴干阳刃命中。缺参或输入矛盾时，正式盘实际采用数还会减少。','',
'固定表不是照抄原引擎标签。岁病符、吊客、天医/地医已有与旧引擎不同的采用值；小耗岁/月分开，死符取岁干，死神取月表。神煞归属天盘tian，di只是所临地盘。','',
'## 明确停用的22个名称','',policy.disabled.join('、')+'。','',
'这里的干胎神/支胎神仅指旧引擎字段身份，不能扩大解释为胎爻专项退出。未登记的天德、月德、天赦等即使有旧释义或在原始JSON中出现，也不等于已经进入现行自动采用表。','',
'## 后续核查、增补建议（尚未采用）','',
'1. 先复核现有边界：阴干刃法、两医起法、岁/月小耗、死符岁干/岁支、同名跨组、节月与季界。已有固定选择不代表其他传法已被证伪。',
'2. 候选先从实际使用面较广的项目核起：天德、月德、天赦、解神；官禄文书的皇恩、天诏、皇书、华盖；盗失等专项的游都、鲁都、劫煞、灾煞。这是建议核查顺序，不是本轮已作采用决定。',
'3. 22个停用项逐项追本地字段来源、原文、完整起法与作用条件；保留天才/天财、飞镰/飞廉、天史/天吏等原名，不据近名替换。关系项与十二天将另列，不以神煞标签数量衡量覆盖。',
'4. 每项记录：标准名、别名、基准、完整起表、历法边界、原典连续引文、异法、适用占类、成立条件、反证、导出字段、采用决定；先完成资料核查，再按授权增补代码与活动表。','',
'## 证据与使用限制','',
'- 活动指针：.opencode/liuren-active.json。',
'- 原引擎文件及SHA256：tools/liuren-direct/legacy-engine-manifest.json；本次运行全部匹配。',
'- 原页面导出器：排盘工具魔改/index.html，tiandipan生成约2120行，KEY_SS约2240行。',
'- 现行采用表：runtime/liuren/'+policy.release+'/references/shensha-policy.json；由loadShenshaPolicy校验绑定身份与hash。',
'- 正式AI盘筛选：tools/liuren-chart-view.mjs，约84行。',
'- 现有专业复核入口：同运行包references/shensha-authority-review.md、shensha-authority-conflicts.md。本轮读取了复核说明，没有重新校勘全部原典。',
'- 原引擎172名与现有shensha-engine-index.md名称完全一致；本次重新运行核实，未只凭旧文档数量。',
'- 同目录神煞清点.json包含逐组观察值、输入样本摘要、引擎哈希与固定规则；神煞核查台账.csv供筛选填写。',
'- 本轮没有专业预测验证；工程可算、可导出、文献有据、预测有效分别判断。','');
fs.writeFileSync(path.join(OUT,'神煞清单与核查说明.md'),lines.join('\n'));
console.log(JSON.stringify({counts:result.counts,groups:Object.fromEntries(Object.entries(groups).map(([g,ns])=>[g,{count:ns.length,names:ns}])),not_export_seen:result.not_export_seen,historical_index_only:result.historical_index_only,runtime_only:result.runtime_only,keyShensha_whitelist:keyNames,keyShensha_not_seen:result.keyShensha_not_seen,status_counts:Object.fromEntries(['adopted_alias','explicitly_disabled','unregistered'].map(s=>[s,rows.filter(r=>r.status===s).length]))},null,2));
