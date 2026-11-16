// Presentation and scoped reference access only; never decides efficacy or outcomes.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
const hash=s=>createHash('sha256').update(s).digest('hex');
const fail=s=>{throw new Error('LIUREN_CORE_HANDOFF: '+s);};
export const loadedCoreSha256=hash(await fs.readFile(new URL(import.meta.url),'utf8'));
const table=(rows,columns)=>({columns,rows:rows.map(row=>columns.map(k=>row[k]??null))});
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
 const nodeColumns=['id','symbol','element','ground','general','general_element','earth_upper','earth_upper_general','direct_yin','void_self','void_ground','xungan','engine_xungan','engine_nayin','kin','seasonal','growth','general_growth','local_relations','lesson_slots','transmission_slots'];
 // Repeated labels are factored into columns, never selected by the model.
 const compactNodes=d.nodes.map(n=>({...n,kin:[n.kin.reference,n.kin.value],seasonal:[n.seasonal.profiles['four-seasons'],n.seasonal.profiles['quarter-earth']],growth:[n.growth.ground,n.growth.yin],general_growth:[n.general_growth.branch??null,n.general_growth.ground],local_relations:[n.local_relations.branch_to_ground,n.local_relations.general_to_branch,n.local_relations.yin_to_branch]}));
 const stemColumns=['id','symbol','element','home','upper','direct_yin','seasonal','growth'];
 const compactStems=d.stems.map(n=>({...n,seasonal:[n.seasonal.profiles['four-seasons'],n.seasonal.profiles['quarter-earth']],growth:[n.growth.home,n.growth.upper??null,n.growth.day_branch]}));
 const ss=d.adopted_shensha;
 const shenshaColumns=ss?[...new Set(ss.items.flatMap(n=>Object.keys(n)))].filter(k=>k!=='engine_check'):[];
 const shensha=ss?{coordinate_contract:ss.coordinate_contract,calendar:ss.calendar,meaning:ss.meaning,table:table(ss.items.map(n=>({...n,places:n.places?.map(r=>[r.tian,r.di,r.jiang])})),shenshaColumns),disabled_names:ss.disabled_names,unregistered_names:ss.unregistered_names,unregistered_policy:ss.unregistered_policy,evidence_policy:ss.evidence_policy}:null;
 const core={schema:'liuren-reading-core-v1',request_id:p.request_id,
  reading_policy:'核心内容须读完；references只为索引，不要求逐项打开。决定性条件不清、摘要不足或新争点影响结论时，按material_id或module查连续原文；读了多少参考页不作为提交门槛。',
  original_question:p.input_origin?.source_text??null,questions:p.questions,
  chart:p.chart.facts,
  program:{policies:d.policies,xun:d.xun,anchors:d.anchors,
   table_legend:{nodes:'seasonal=[four-seasons,quarter-earth]；growth=[本支临地,本支直接阴神]；general_growth=[将自身对所乘天盘支,将自身对地盘]；支将十二气=五行顺行；旧绑定包缺层显示null不推造；local_relations=[支→地,将→支,阴神→支]',stems:'seasonal同上；growth=[本干寄宫,本干寄宫上神,本干日支]；各干采用stem-yang-forward-yin-reverse；原引擎表仍保存在chart.growth',shensha:'places每项=[天盘归属支,所临地盘,所乘将]；只有resolved可取用，状态不等于效力'},
   nodes:table(compactNodes,nodeColumns),stems:table(compactStems,stemColumns),structure:d.structure,shensha,calculations:d.calculations,special_requirements:d.special_requirements,warnings:d.warnings,limits:d.limits},
  preparation:{note:'以下是主智能体候选材料，不是程序事实或既定结论；可纠正并从完整盘补漏。已确认U01—U11须执行；focus_issues不重新开放既定口径，真实缺口见C编号。',entities:p.entities,facts:p.facts,observations:p.observations,focus_issues:p.focus_issues,unknowns:p.unknowns},
  shared_method:guide,specialty_methods:specialties,
  references:{materials:p.method_materials.map(({id,title,source_path,line_start,line_end})=>({id,title,source_path,line_start,line_end})),aliases:p.material_aliases?.map(({id,canonical_id})=>({id,canonical_id}))??[],available_modules:Object.keys(registry.modules),fixed_evidence:'E01—E22；按具体条目查，不逐条通读',access:'liuren_adjudication_read({file_path,sha256,material_id:来源ID,page:1,page_count:4})；详细方法改用module:模块ID；始终沿用本任务file_path/sha256。'}
 };
 const content=JSON.stringify(core)+'\n';
 return {core:{schema:'liuren-reading-core-v1',content,sha256:hash(content)},registry};
}
export async function readBoundReference(root,loaded,{material_id,module}){
 if(Boolean(material_id)===Boolean(module))fail('choose exactly one of material_id/module');
 const p=loaded.envelope.packet,registry=loaded.referenceRegistry;
 if(material_id){
  const alias=p.material_aliases?.find(a=>a.id===material_id),m=p.method_materials.find(m=>m.id===(alias?.canonical_id??material_id));
  if(m)return {id:material_id,canonical_id:m.id,title:m.title,source_path:m.source_path,line_start:m.line_start,line_end:m.line_end,line_mode:m.line_mode,source_sha256:m.sha256,content:m.quote,snapshot:'bound immutable archive'};
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
