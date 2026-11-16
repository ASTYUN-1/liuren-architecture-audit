import fs from 'node:fs/promises';
import path from 'node:path';
import {buildFacts,focusFacts,canonicalEntity,hash,calculate,growth,kin,seasonal,relations,ZHI,GAN,symbols} from './liuren-deterministic.mjs';
import {calendar} from './liuren-deterministic-calendar.mjs';
import {EVENT_POLICY,eventPolicy,eventDomains,classificationRecord} from './liuren-event-positioning.mjs';
import {loadShenshaPolicy,resolveShensha} from './liuren-shensha.mjs';
const fail=(m,at)=>{const e=new Error('LIUREN_FOUNDATION: '+m);if(at)e.path=at;throw e;};
export async function foundationEnabled(root){
 const p=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
 return p.deterministicFoundation?.enabled===true;
}
function linesOf(raw,mode){
 const text=raw.toString('utf8').replace(/^\uFEFF/,'');
 if(mode==='lf')return text.split('\n');
 if(mode!=='universal')fail('line_mode must be lf or universal');
 const rows=text.split(/\r\n|[\n\r\v\f\u001c-\u001e\u0085\u2028\u2029]/);if(rows.at(-1)==='')rows.pop();return rows;
}
export async function sourceMaterial(root,request){
 const pointer=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
 const at='method_materials[id='+request.id+']';
 const base=await fs.realpath(root),original=request.source_path;
 const prefixes=['书籍库/','books/',pointer.runtime+'/','docs/应期取数归纳-20261027/'];
 const invalid=()=>fail(at+'.source_path: source outside current registered method/book scope; received='+JSON.stringify(original)+'; expected workspace-relative path under '+prefixes.join(' | ')+' or its exact workspace absolute path. Copy handoff from liuren_materials, or source_path from liuren_compute(action="source"); preserve other materials.',at+'.source_path');
 if(typeof original!=='string'||!original||original.replaceAll('\\','/').split('/').includes('..'))invalid();
 let rel=original.replaceAll('\\','/');
 if(path.isAbsolute(original))rel=path.relative(base,path.resolve(original)).replaceAll('\\','/');
 if(!rel||path.isAbsolute(rel)||rel.split('/').includes('..')||!/\.(txt|md|json)$/.test(rel)||!prefixes.some(prefix=>rel.startsWith(prefix)))invalid();
 let file;
 try{file=await fs.realpath(path.join(base,rel));}catch(e){fail(at+'.source_path: cannot read '+JSON.stringify(rel)+' ('+e.code+'); copy the exact existing tool-returned path.',at+'.source_path');}
 if(!file.startsWith(base+path.sep)||file!==path.resolve(base,rel))fail(at+'.source_path: source linked or escaped',at+'.source_path');
 const stat=await fs.stat(file);if(stat.size>12*1024*1024)fail('source oversized');
 const raw=await fs.readFile(file);if(raw.toString('utf8').includes('\uFFFD'))fail('only verified UTF-8 source supported; do not silently decode other encodings');
 const digest=hash(raw.toString('utf8'));
 if(rel.startsWith(pointer.runtime+'/')){
  const manifest=JSON.parse(await fs.readFile(path.join(base,pointer.runtime,'manifest.json'),'utf8'));
  if(manifest.files[rel.slice(pointer.runtime.length+1)]!==digest)fail('runtime source differs from registered manifest');
 }
 if(request.sha256&&request.sha256!==digest)fail('source sha256 changed '+rel);
 const line_mode=request.line_mode??'universal',lines=linesOf(raw,line_mode);
 let start=request.line_start,end=request.line_end;
 // A manifest-verified current method is an exact complete document, not a book search range.
 if(start===undefined&&end===undefined&&request.quote===undefined&&rel.startsWith(pointer.runtime+'/')){start=1;end=lines.length;}
 if(start===undefined&&end===undefined&&request.quote){
  const q=request.quote.replaceAll('\r\n','\n'),hits=[];
  const qs=q.split('\n');
  for(let i=0;i<=lines.length-qs.length;i++)if(lines.slice(i,i+qs.length).join('\n')===q)hits.push(i);
  if(hits.length!==1)fail(at+'.quote: expected a unique complete source-line match; matches='+hits.length+'; supply exact line_start/line_end for this material only');
  start=hits[0]+1;end=hits[0]+qs.length;
 }
 if(!Number.isInteger(start)||!Number.isInteger(end)||start<1||end<start||end>lines.length)fail(at+'.line_start/line_end: expected integers 1 <= start <= end <= '+lines.length+' for line_mode='+line_mode+'; actual start='+String(start)+', end='+String(end)+'; current runtime method without a range loads its complete verified text; book passages require exact bounds. Preserve other materials.');
 const selected=lines.slice(start-1,end).join('\n');
 if(request.quote!==undefined&&request.quote.replaceAll('\r\n','\n')!==selected)fail(at+'.quote differs from continuous source span; use the original lines, not a paraphrase');
 // Include the whole selected paragraphs; never synthesize omitted conditions.
 while(start>1&&lines[start-2].trim())start--;
 while(end<lines.length&&lines[end].trim())end++;
 const quote=lines.slice(start-1,end).join('\n');if(!quote.trim()||quote.length>16000)fail('source context too large/empty; choose a complete narrower section');
 return {id:request.id,title:request.title,source_path:rel,quote,line_start:start,line_end:end,line_mode,sha256:digest};
}
export function compute(request,c,{root}={}){
 const d=['chart','lookup','life'].includes(request.action)?buildFacts(c):null;
 switch(request.action){
  case 'chart':return focusFacts(d,request.symbols??[]);
  case 'lookup':{
   const {subject,place,reference}=request.lookup??{};
   const ref=reference??c.day_stem;return {subject,reference:ref,kin:kin(ref,subject),
    seasonal:{profile:request.lookup.profile??'four-seasons',month:c.month_branch,value:seasonal(subject,c.month_branch,request.lookup.profile??'four-seasons')},
    ...(place?{place,growth:growth(subject,place),subject_to_place:relations(subject,place)}:{}),
    ...(ZHI.includes(subject)||GAN.includes(subject)?canonicalEntity(subject,d):{}),note:'Relationship and state lookup, not efficacy.'};
  }
  case 'life':{
   const {age,sex,age_basis,birth_pillar}=request.life??{};
   if(!Number.isInteger(age)||age<1||age>150||!['男','女'].includes(sex)||age_basis!=='虚岁-已核')fail('life requires verified nominal age (1-150), sex and age_basis=虚岁-已核; no inferred birth year');
   const n=((sex==='男'?2+age-1:8-age+1)%60+60)%60,xingnian=GAN[n%10]+ZHI[n%12];
   const at=b=>c.heaven_earth.find(r=>r.di===b);
   if(birth_pillar!==undefined&&(typeof birth_pillar!=='string'||birth_pillar.length!==2||!GAN.includes(birth_pillar[0])||!ZHI.includes(birth_pillar[1])||GAN.indexOf(birth_pillar[0])%2!==ZHI.indexOf(birth_pillar[1])%2))fail('invalid declared birth pillar');
   return {age,sex,age_basis,xingnian,upper:at(xingnian[1]),direct_yin:at(at(xingnian[1]).tian).tian,
    ...(birth_pillar?{declared_birth_pillar:birth_pillar,life_branch:birth_pillar[1],life_upper:at(birth_pillar[1])}:{}),
    method:'references/nianming.md: 男一岁丙寅顺数，女一岁壬申逆数；输入年龄已核，不从出生年推测',limits:['Age declaration is not independently verified by arithmetic.']};
  }
  case 'calendar':return calendar(request.calendar,{root});
  case 'quantity':return calculate(request.expression);
  default:fail('unsupported computation action');
 }
}
function runRequest(root,r,c){
 if(!r||!/^C_[A-Za-z0-9_-]+$/.test(r.id)||!['calendar','quantity'].includes(r.action))fail('calculation id/action');
 return {id:r.id,action:r.action,request:r.action==='calendar'?r.calendar:r.expression,
  result:r.action==='calendar'?calendar(r.calendar,{root}):calculate(r.expression)};
}
export async function prepareFoundation(root,input){
 const p=structuredClone(input);
 const useEventPolicy=await eventPolicy(root);
 if(useEventPolicy){if(p.event_positioning!==undefined)fail('event_positioning is program-owned');await eventDomains(root,p);}
 if(!await foundationEnabled(root)){if(useEventPolicy)fail('event positioning requires deterministicFoundation.enabled');return p;}
 if(p.deterministic!==undefined)fail('deterministic is generated by program; do not supply it');
 const d=buildFacts(p.chart.facts);
 const currentShensha=await loadShenshaPolicy(root);
 const adoptedShensha=resolveShensha(p.chart.facts,currentShensha.policy,currentShensha.sha256);
 if(p.chart.engine_context?.shensha_resolution){
  p.chart.engine_context.source_shensha_resolution_sha256=hash(p.chart.engine_context.shensha_resolution);
  delete p.chart.engine_context.shensha_resolution;
 }
 for(const q of p.questions){
  if(!Array.isArray(q.tasks)||!q.tasks.length||new Set(q.tasks).size!==q.tasks.length||q.tasks.some(x=>!['outcome','timing','quantity'].includes(x)))fail('questions.'+q.id+'.tasks must declare outcome/timing/quantity');
 }
 for(const e of p.entities){const canonical=canonicalEntity(e.branch,d);
  if(e.position!==undefined&&e.position!=='@program'&&e.position!==canonical.position)fail('entity '+e.id+' position is program-owned; omit it or use @program');
  e.position=canonical.position;
 }
 for(const o of p.observations)if(o.verification==='chart_checked')fail('observations.'+o.id+': chart_checked is program-owned; use method_interpretation/unverified and reference D_* facts');
 const materials=[];
 for(const m of p.method_materials)materials.push(await sourceMaterial(root,m));
 const required=new Set(p.questions.flatMap(q=>q.tasks));
 const pointer=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
 if(p.material_aliases!==undefined)fail('material_aliases is program-owned');
 if(p.method_modules!==undefined){
  if(!Array.isArray(p.method_modules)||p.method_modules.length>40||p.method_modules.some(x=>typeof x!=='string'))fail('method_modules requires up to 40 current module IDs');
  const manifest=JSON.parse(await fs.readFile(path.join(root,pointer.runtime,'manifest.json'),'utf8'));
  for(const key of new Set(p.method_modules)){
   const row=Object.hasOwn(manifest.modules,key)?manifest.modules[key]:null;if(!row)fail('unknown method_modules ID '+key);
   const id='M_'+key,expanded=await sourceMaterial(root,{id,title:key,source_path:pointer.runtime+'/'+row.file,sha256:manifest.files[row.file]});
   const existing=materials.find(m=>m.id===id);
   if(existing){
    // Exact duplicate handoffs are one source, not a model judgment or a lost ID.
    if(!['source_path','line_start','line_end','line_mode','sha256','quote'].every(k=>existing[k]===expanded[k]))fail('method_modules conflicts with explicit material ID '+id+'; same ID must identify the identical source version and complete span');
   }else materials.push(expanded);
  }
  delete p.method_modules;
 }
 const modules=[...(useEventPolicy?[['M_EVENT_POSITIONING','methods/positioning.md'],...[...new Set(p.questions.map(q=>q.domain))].map(domain=>['M_DOMAIN_'+domain.replaceAll('-','_'),'domains/'+domain+'.md'])]:[]),...(required.has('timing')?[['M_AUTO_TIMING','methods/timing.md']]:[]),...(required.has('quantity')?[['M_AUTO_QUANTITY','methods/quantity.md'],['M_AUTO_NUMBERS','references/quantity-sources.md']]:[])];
 if(useEventPolicy)p.event_positioning={schema:EVENT_POLICY,release:pointer.release,questions:classificationRecord(p),method_ids:modules.filter(([id])=>id.startsWith('M_EVENT_')||id.startsWith('M_DOMAIN_')).map(([id])=>id)};
 for(const [id,file] of modules){
  if(materials.some(m=>m.id===id))fail('reserved method id '+id);
  const source_path=pointer.runtime+'/'+file,raw=await fs.readFile(path.join(root,source_path));
  const lines=linesOf(raw,'universal');
  materials.push(await sourceMaterial(root,{id,title:'程序装入完整专法 '+file,source_path,line_start:1,line_end:lines.length,line_mode:'universal',sha256:hash(raw.toString('utf8'))}));
 }
 // Share only byte-identical source spans. Every former ID remains resolvable
 // via an explicit alias; differing versions, ranges or texts stay separate.
 const unique=[],aliases=[],seen=new Map();
 for(const m of materials){
  const key=JSON.stringify([m.source_path,m.sha256,m.line_start,m.line_end,m.line_mode,m.quote]);
  const canonical=seen.get(key);
  if(canonical){const {quote,...locator}=m;aliases.push({...locator,canonical_id:canonical.id});}
  else {seen.set(key,m);unique.push(m);}
 }
 p.method_materials=unique;
 if(aliases.length)p.material_aliases=aliases;
 const requests=p.computation_requests??[];
 if(!Array.isArray(requests)||requests.length>30||new Set(requests.map(r=>r.id)).size!==requests.length)fail('calculation requests duplicate/over limit');
 const calculations=requests.map(r=>runRequest(root,r,p.chart.facts));
 delete p.computation_requests;
 p.deterministic={...d,calculations,
  adopted_shensha:adoptedShensha,
  special_requirements:p.questions.flatMap(q=>q.tasks.filter(t=>t!=='outcome').map(kind=>({question_id:q.id,kind}))),
  note:'Program-owned; full original facts remain. D_* identifiers are facts, not weighted evidence.'};
 return p;
}
export function validateFoundation(p){
 const d=p.deterministic;if(!d)return;
 const rebuilt=buildFacts(p.chart.facts);
 for(const key of Object.keys(rebuilt))if(JSON.stringify(d[key])!==JSON.stringify(rebuilt[key]))fail('deterministic facts changed '+key);
 for(const e of p.entities)if(e.position!==canonicalEntity(e.branch,d).position)fail('input entity position changed');
 for(const o of p.observations)if(o.verification==='chart_checked')fail('manual chart_checked not allowed');
 if(p.questions.some(q=>!Array.isArray(q.tasks)||!q.tasks.length))fail('missing question tasks');
 const required=p.questions.flatMap(q=>q.tasks.filter(t=>t!=='outcome').map(kind=>({question_id:q.id,kind})));
 if(JSON.stringify(d.special_requirements)!==JSON.stringify(required))fail('special requirements mismatch');
}
export function validateFactualOutput(r,p){
 if(!p.deterministic)return;
 for(const e of r.entity_checks){const expected=canonicalEntity(e.branch,p.deterministic);
  for(const k of Object.keys(expected))if(JSON.stringify(e[k])!==JSON.stringify(expected[k]))fail('entity '+e.id+' wrong computed '+k);
 }
 const required=p.deterministic.special_requirements,records=r.special_methods??(r.status==='needs_input'?[]:undefined);
 if(!Array.isArray(records)||(r.status==='completed'&&records.length!==required.length))fail('missing special method records');
 const seen=new Set(),basis=new Set([...p.method_materials.map(m=>m.id),...Array.from({length:22},(_,i)=>'E'+String(i+1).padStart(2,'0'))]);
 const factual=new Set([...p.facts.map(f=>f.id),...p.observations.map(o=>o.id),...p.deterministic.nodes.map(n=>n.id),...p.deterministic.stems.map(n=>n.id)]);
 const calculations=[...p.deterministic.calculations,...(r.calculations??[])];
 const calcIDs=new Set(calculations.map(c=>c.id));
 if(calcIDs.size!==calculations.length)fail('duplicate calculation id');
 for(const [index,s] of records.entries()){
  const at='/special_methods/'+index;
  const key=s.question_id+':'+s.kind;
  if(seen.has(key)||!required.some(q=>q.question_id===s.question_id&&q.kind===s.kind))fail('unknown/duplicate special method',at);seen.add(key);
  if(!['completed','unresolved'].includes(s.status)||typeof s.target!=='string'||!s.target.trim())fail('special method status/target');
  if(!Array.isArray(s.basis_ids)||!s.basis_ids.length||s.basis_ids.some(id=>!basis.has(id)))fail('special method requires actual method source');
  if(s.fact_ids!==undefined&&(!Array.isArray(s.fact_ids)||s.fact_ids.some(id=>!factual.has(id))))fail('special method fact_ids contains unknown factual reference');
  if(!Array.isArray(s.calculation_ids)||s.calculation_ids.some(id=>!calcIDs.has(id)))fail('unknown special calculation');
  if(!Array.isArray(s.limits)||(s.status==='unresolved'&&!s.limits.length))fail('unresolved special method needs concrete limits');
  const fields=s.kind==='timing'?['event','stage','scale','start','count_rule','trigger','selected_method','round_comparison']:['object','position','number_table','operation','adjustments','magnitude','unit','precision'];
  if(!s.record)fail('incomplete '+s.kind+' record',at+'/record');
  for(const field of fields)if(typeof s.record[field]!=='string'||!s.record[field].trim())fail('incomplete '+s.kind+' record',at+'/record/'+field);
  if(!Array.isArray(s.alternatives))fail('special alternatives required');
  if(s.status==='completed'&&!s.calculation_ids.length)fail('completed timing/quantity needs deterministic date/arithmetic calculation');
  const used=calculations.filter(c=>s.calculation_ids.includes(c.id));
  if(s.status==='completed'&&s.kind==='quantity'){
   if(!Number.isFinite(s.record.value)||!used.some(c=>c.action==='quantity'&&c.result.value===s.record.value))fail('reported quantity differs from computed value',at+'/record/value');
  }
  if(s.status==='completed'&&s.kind==='timing'){
   const dates=used.filter(c=>c.action==='calendar').flatMap(c=>c.result.rows);
   const candidates=s.record.candidates;
   if(!Array.isArray(candidates)||!candidates.length)fail('timing candidates must match enumerated calendar dates and event stages',at+'/record/candidates');
   for(const [j,v] of candidates.entries())if(!v||!dates.some(d=>d.date===v.date&&d.day===v.day)||typeof v.event!=='string'||!v.event.trim())fail('timing candidates must match enumerated calendar dates and event stages',at+'/record/candidates/'+j);
  }
 }
 for(const rel of r.relation_checks){
  if(JSON.stringify(rel.computed_relations)!==JSON.stringify(relationFacts(rel,r.entity_checks)))fail('relation '+rel.id+' wrong computed relationships');
  if(!r.answers.some(a=>a.decisive_relation_ids.includes(rel.id)||a.counter_relation_ids.includes(rel.id)))continue;
  if(!rel.application||['object','mechanism','stage','goal_effect','alternative_resolution'].some(k=>typeof rel.application[k]!=='string'||!rel.application[k].trim()))fail('decisive relation '+rel.id+' missing application chain');
 }
}
function relationFacts(rel,entities){
 const a=entities.find(e=>e.id===rel.from),b=entities.find(e=>e.id===rel.to);
 if(!a||!b)fail('relation entity missing');
 return symbols(a.branch).flatMap(x=>symbols(b.branch).map(y=>({from:x,to:y,relationships:relations(x,y)})));
}
export function finalizeFoundation(root,result,p){
 if(!p.deterministic)return result;
 const r=structuredClone(result);
 for(const e of r.entity_checks??[]){
  const expected=canonicalEntity(e.branch,p.deterministic);
  for(const [k,v] of Object.entries(expected)){if(e[k]!==undefined&&JSON.stringify(e[k])!==JSON.stringify(v))fail('entity '+e.id+' supplied wrong '+k+'; omit program fields');e[k]=v;}
 }
 for(const rel of r.relation_checks??[]){const expected=relationFacts(rel,r.entity_checks);
  if(rel.computed_relations!==undefined&&JSON.stringify(rel.computed_relations)!==JSON.stringify(expected))fail('incorrect computed relations '+rel.id);
  rel.computed_relations=expected;
 }
 const requests=r.calculations??[];if(!Array.isArray(requests)||requests.length>30)fail('output calculations limit');
 r.calculations=requests.map(v=>runRequest(root,v,p.chart.facts));
 return r;
}
