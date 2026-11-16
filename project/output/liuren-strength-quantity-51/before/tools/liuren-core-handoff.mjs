// Presentation and scoped reference access only; never decides efficacy or outcomes.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {chartView} from './liuren-chart-view.mjs';
import {BASIC_BIFA_RULES_SHA256,loadedBasicBifaSha256} from './liuren-bifa-basic.mjs';
import {BIFA_STATEMENTS_SHA256,loadedBifaViewSha256} from './liuren-bifa-view.mjs';
import {audited,AUDIT_GUIDE} from './liuren-consistency-audit.mjs';
const hash=s=>createHash('sha256').update(s).digest('hex');
const fail=s=>{throw new Error('LIUREN_CORE_HANDOFF: '+s);};
export const loadedCoreSha256=hash(await fs.readFile(new URL(import.meta.url),'utf8'));
export async function compactEnabled(root){
 return JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8')).compactHandoff?.enabled===true;
}
async function checkedRuntimeFile(root,runtime,file,sha){
 const base=await fs.realpath(root),folder=path.resolve(base,runtime),target=path.resolve(folder,file);
 if(!/^runtime\/liuren\/[A-Za-z0-9_-]+$/.test(runtime)||!target.startsWith(folder+path.sep)||await fs.realpath(target)!==target||(await fs.lstat(target)).isSymbolicLink())fail('source outside bound runtime');
 if((await fs.stat(target)).size>1000000)fail('source oversized');
 const raw=await fs.readFile(target,'utf8');if(hash(raw)!==sha)fail('registered source hash changed: '+file);return raw;
}
export async function makeReadingCore(root,p){
 const pointer=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
 const manifest=JSON.parse(await fs.readFile(path.join(root,pointer.runtime,'manifest.json'),'utf8'));
 const file='references/judgment-core.md',guide=await checkedRuntimeFile(root,pointer.runtime,file,manifest.files[file]);
 const domains=[...new Set(p.questions.map(q=>q.domain))],specialties=[];
 for(const id of domains){const row=manifest.modules[id];if(!row)fail('unknown domain '+id);specialties.push({id,content:await checkedRuntimeFile(root,pointer.runtime,row.file,manifest.files[row.file])});}
 // Capture the versioned registry once. Future reads cannot select arbitrary paths.
 const registry={runtime:pointer.runtime,modules:Object.fromEntries(Object.entries(manifest.modules).map(([id,r])=>[id,{file:r.file,sha256:manifest.files[r.file]}])),evidence:{file:'references/adjudicator-book-evidence.json',sha256:manifest.files['references/adjudicator-book-evidence.json']}};
 const d=p.deterministic;if(!d?.nodes||!d?.stems)fail('complete deterministic chart required');
 const bifaFile='references/bifa-basic-evidence.json';
 const bifaRaw=await checkedRuntimeFile(root,pointer.runtime,bifaFile,manifest.files[bifaFile]);
 if(hash(bifaRaw)!==BASIC_BIFA_RULES_SHA256)fail('Bifa source registry differs from bound runtime');
 if(pointer.workflowImplementation?.['tools/liuren-bifa-basic.mjs']!==loadedBasicBifaSha256)fail('Bifa implementation changed; restart with active code');
 const statementFile='references/bifa-statements.json';
 const statementRaw=await checkedRuntimeFile(root,pointer.runtime,statementFile,manifest.files[statementFile]);
 if(hash(statementRaw)!==BIFA_STATEMENTS_SHA256||pointer.workflowImplementation?.['tools/liuren-bifa-view.mjs']!==loadedBifaViewSha256)fail('Bifa statements differ from bound runtime; restart with active code');
 registry.bifaEvidence={file:bifaFile,sha256:manifest.files[bifaFile]};
 // Optional for old bound tasks. New guides remain on demand, outside the core.
 if(registry.modules['bifa-guide']){
  const ref=registry.modules['bifa-guide'];
  const guide=JSON.parse(await checkedRuntimeFile(root,pointer.runtime,ref.file,ref.sha256));
  if(guide.schema!=='liuren-bifa-reading-guide-v1'||guide.source_registry_sha256!==BASIC_BIFA_RULES_SHA256)fail('Bifa reading guide/source registry mismatch');
  registry.bifaGuide={...ref};
 }
 const core={schema:'liuren-reading-core-v1',request_id:p.request_id,
  reading_policy:'核心内容须读完；references只为索引，不要求逐项打开。决定性条件不清、摘要不足或新争点影响结论时，按material_id或module查连续原文；读了多少参考页不作为提交门槛。',
  original_question:p.input_origin?.source_text??null,questions:p.questions,
  ...(audited(p)?{input_review:p.input_review,consistency_policy:p.consistency_policy,consistency_guide:AUDIT_GUIDE}:{}),
  chart:chartView(p.chart.facts,{deterministic:d,shensha:d.adopted_shensha,conventions:p.chart.engine_context?.conventions}),
  program:{calculations:d.calculations,special_requirements:d.special_requirements},
  preparation:{note:'以下是主智能体候选材料，不是程序事实或既定结论；可纠正并从完整盘补漏。已确认U01—U11须执行；focus_issues不重新开放既定口径，真实缺口见C编号。',entities:p.entities,facts:p.facts,observations:p.observations,focus_issues:p.focus_issues,unknowns:p.unknowns},
  shared_method:guide,specialty_methods:specialties,
  references:{materials:p.method_materials.map(({id,title,source_path,line_start,line_end})=>({id,title,source_path,line_start,line_end})),aliases:p.material_aliases?.map(({id,canonical_id})=>({id,canonical_id}))??[],available_modules:Object.keys(registry.modules),fixed_evidence:'E01—E22；按具体条目查，不逐条通读',...(registry.bifaGuide?{bifa_lookup:'material_id:BF-35查第35法百法录（BF-01至BF-100）；BF-B35/BF-D35查北海/大全连续原章。按需查，不要求逐法解释。'}:{}),access:'liuren_adjudication_read({file_path,sha256,material_id:来源ID,page:1,page_count:4})；详细方法改用module:模块ID；始终沿用本任务file_path/sha256。'}
 };
 if(registry.bifaGuide)registry.bifaMatchedView=structuredClone(core.chart.bifa_conditions);
 if(pointer.integratedAnalysis?.bifaCoreMode==='conditions-only'){
  core.chart.bifa_conditions=core.chart.bifa_conditions.map(({条目,成格})=>({条目,成格}));
  core.reading_policy+=' 毕法核心仅列客观成格条件，未按问取义；相关意象及原章按BF法号查，无关可不用，不逐条解释。';
 }
 const content=JSON.stringify(core)+'\n';
 return {core:{schema:'liuren-reading-core-v1',content,sha256:hash(content)},registry};
}
export async function readBoundReference(root,loaded,{material_id,module}){
 if(Boolean(material_id)===Boolean(module))fail('choose exactly one of material_id/module');
 const p=loaded.envelope.packet,registry=loaded.referenceRegistry;
 if(material_id){
  if(/^BF-(?:0[1-9]|[1-9]\d|100)$/.test(material_id)){
   if(!registry?.bifaGuide?.sha256)fail('百法录未绑定此任务；沿用该任务原有书证，不读取当前活动版本替换旧资料');
   const ref=registry.bifaGuide;
   const guide=JSON.parse(await checkedRuntimeFile(root,registry.runtime,ref.file,ref.sha256));
   const number=Number(material_id.slice(3)),card=guide.cards.find(c=>c.number===number);
   if(!card)fail('unknown Bifa law '+number);
   const matched=(registry.bifaMatchedView??[]).filter(row=>Number(row.条目.match(/^毕法赋(\d+)：/)?.[1])===number);
   const content=[`# 毕法赋${String(number).padStart(2,'0')}：${card.title}`,'',
    '阅读辅助：先依原问取用；本条只帮助描述关系、情况与倾向，不决定结果，亦可能与本问无关。','',
    '本盘已列基本结构：',
    matched.length?matched.map(r=>`- ${r.条目}\n  成格：${r.成格}`).join('\n'):'未列为已成立基本结构；可查方法，但不能据此补称本盘成格。',
    '本盘以上记录只确认结构，不确认与所问的关联；书中其他子格仍须另核。','',
    '理解（本轮归纳）：'+card.understanding,'','分析线索（本轮提示）：'+card.inquiry,'',
    ...(card.adoption_note?['采用边界：'+card.adoption_note,'']:[]),
    '北海摘录（保留原措辞，不是对本盘的断语）：',
    ...card.source_extracts.flatMap(q=>['',q.quote,`〔${guide.source.path}:${q.line_start}—${q.line_end}〕`]),'',
    '完整原章：'+card.originals.join(' / ')+'；沿用本任务reader的material_id按需查。',
    '归纳未覆盖全章全部旁格；条件或上下文不足时查原章。'].join('\n');
   return {id:material_id,title:'百法录：'+card.title,source_path:registry.runtime+'/'+ref.file,source_sha256:ref.sha256,content,snapshot:'bound versioned Bifa reading guide'};
  }
  const alias=p.material_aliases?.find(a=>a.id===material_id),m=p.method_materials.find(m=>m.id===(alias?.canonical_id??material_id));
  if(m)return {id:material_id,canonical_id:m.id,title:m.title,source_path:m.source_path,line_start:m.line_start,line_end:m.line_end,line_mode:m.line_mode,source_sha256:m.sha256,content:m.quote,snapshot:'bound immutable archive'};
  if(/^BF-[DB](?:\d{2}|100)$/.test(material_id)&&registry?.bifaEvidence?.sha256){
   const ref=registry.bifaEvidence,bundle=JSON.parse(await checkedRuntimeFile(root,registry.runtime,ref.file,ref.sha256));
   for(const source of bundle.sources){
    const e=source.excerpts.find(e=>e.id===material_id);
    if(e)return {id:e.id,title:'毕法基本结构连续书证',source_path:source.path,source_sha256:source.sha256,line_start:e.line_start,line_end:e.line_end,line_mode:source.line_mode,content:e.quote,snapshot:'bound versioned Bifa evidence'};
   }
  }
  if(/^E\d{2}$/.test(material_id)&&registry?.evidence?.sha256){
   const bundle=JSON.parse(await checkedRuntimeFile(root,registry.runtime,registry.evidence.file,registry.evidence.sha256));
   const row=bundle.evidence.find(e=>e.id===material_id);if(row)return {id:row.id,title:row.topic,source_path:row.path,line_start:row.line_start,line_end:row.line_end,source_sha256:row.sha256,source_identity:row.source_identity,content:row.quote,snapshot:'bound versioned evidence'};
  }
  fail('unknown material_id '+material_id+'; use IDs from references');
 }
 if(!registry?.modules||!Object.hasOwn(registry.modules,module))fail('unknown module '+module+'; use references.available_modules');
 const ref=registry.modules[module],content=await checkedRuntimeFile(root,registry.runtime,ref.file,ref.sha256);
 return {id:module,title:module,source_path:registry.runtime+'/'+ref.file,source_sha256:ref.sha256,content,snapshot:'bound versioned method'};
}
