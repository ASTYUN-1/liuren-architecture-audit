// Contract checks for the slim-registered adjudicator. No model or filesystem calls.
import {validateFoundation,validateFactualOutput} from './liuren-deterministic-io.mjs';
import {symbols} from './liuren-deterministic.mjs';
export const AGENT = 'liuren-adjudicator';
export const MODEL = 'deepseek/deepseek-flash';
export const INPUT_SCHEMA = 'liuren-adjudication-input-v2';
export const OUTPUT_SCHEMA = 'liuren-adjudication-output-v2';
import {ID_PATTERN as idPattern,OBSERVATION_KINDS,OBSERVATION_VERIFICATIONS} from './liuren-adjudication-schema.mjs';
export const REQUEST_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/;
export const MAX_INPUT_CHARACTERS = 200000;
const branchPattern = /^[子丑寅卯辰巳午未申酉戌亥]$/;
// Entities may be a day stem or an explicitly supplied composite symbol.
// Plate positions remain single branches and are still checked separately.
const entitySymbol = value => {try{symbols(value);return true;}catch{return false;}};
const fail = message => { throw new Error('LIUREN_ADJUDICATION_CONTRACT: '+message); };
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
function keys(x, required, optional=[], where='object') {
  if (!object(x)) fail(where+' must be an object');
  for (const k of required) if (!(k in x)) fail(where+'.'+k+' is required');
  for (const k of Object.keys(x)) if (![...required,...optional].includes(k)) fail(where+' unexpected '+k);
}
function text(x,where,max=6000) { if(typeof x!=='string'||!x.trim()||x.length>max)fail(where+' invalid text'); }
function list(x,where,min=0,max=100) { if(!Array.isArray(x)||x.length<min||x.length>max)fail(where+' invalid array: expected '+min+'..'+max+' items; actual '+(Array.isArray(x)?x.length:typeof x)); }
function texts(x,where) {list(x,where);x.forEach(v=>text(v,where));}
function choice(x,values,where){if(!values.includes(x))fail(where+': received '+JSON.stringify(x)+'; allowed '+JSON.stringify(values));}
function ids(rows,where){const seen=new Set();for(const [i,row] of rows.entries()){if(!idPattern.test(row.id))fail(where+'['+i+'].id: expected letter then up to 63 letters/digits/_/-; actual '+JSON.stringify(row.id));if(seen.has(row.id))fail(where+'['+i+'].id duplicate '+JSON.stringify(row.id));seen.add(row.id);}return seen;}
function refs(values,known,where){texts(values,where);for(const v of values)if(!known.has(v))fail(where+' unknown reference '+v);}
function bounded(x,max,where){const size=JSON.stringify(x).length;if(size>max)fail(where+' exceeds size limit: actual '+size+' characters; maximum '+max+'; do not discard facts/observations to probe unrelated fields');}

export function validateInput(p) {
  keys(p,['schema','request_id','questions','chart','facts','entities','observations','method_materials','focus_issues','unknowns'],['deterministic','computation_requests','input_origin','retry_context','event_positioning','material_aliases'],'packet');
  if(p.schema!==INPUT_SCHEMA)fail('packet.schema: expected '+INPUT_SCHEMA+'; actual '+JSON.stringify(p.schema));
  if(typeof p.request_id!=='string'||!REQUEST_ID_PATTERN.test(p.request_id))fail('packet.request_id: expected 1..128 ASCII letters/digits/_/-, first character letter or digit (date prefix and UUID allowed); actual '+JSON.stringify(p.request_id)+'; change only this identifier, preserve all materials');
  bounded(p,MAX_INPUT_CHARACTERS,'packet (including program-expanded chart, methods and calculations)');
  list(p.questions,'questions',1,12);
  for(const [i,q] of p.questions.entries()){keys(q,['id','text','subject','stage','deadline','success_criteria','alternatives'],['tasks','task_basis','domain','actor_entity_id'],'packet.questions['+i+']');for(const k of ['text','subject','stage','deadline','success_criteria'])text(q[k],'question.'+k);texts(q.alternatives,'alternatives');if(q.tasks){texts(q.tasks,'question.tasks');q.tasks.forEach(v=>choice(v,['outcome','timing','quantity'],'question task'));}}
  const qids=ids(p.questions,'questions');
  keys(p.chart,['source','facts'],['engine_context'],'packet.chart');text(p.chart.source,'chart.source',1200);
  const c=p.chart.facts;
  keys(c,['schema','pillars','day_stem','day_branch','month_branch','hour_branch','month_general','void_branches','heaven_earth','lessons','transmissions'],
    ['year_pillar','month_pillar','day_pillar','hour_pillar','xun','event_datetime','lunar','transmission_sequence','chart_types','participants','year_life_verified','declared_life','nobleman','growth','seasonal_strength'],'packet.chart.facts');
  if(c.schema!=='liuren-chart-facts-v1')fail('packet.chart.facts.schema must be liuren-chart-facts-v1; copy complete liuren_chart facts or use chart.archive');
  if(!/^[甲乙丙丁戊己庚辛壬癸]$/.test(c.day_stem))fail('day_stem');
  for(const k of ['day_branch','month_branch','hour_branch','month_general'])if(!branchPattern.test(c[k]))fail(k);
  list(c.pillars,'pillars',4,4);c.pillars.forEach(v=>{if(!/^[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]$/.test(v))fail('pillar');});
  list(c.void_branches,'void_branches',2,2);if(new Set(c.void_branches).size!==2||!c.void_branches.every(v=>branchPattern.test(v)))fail('void branches');
  for(const [field,length,fields,extra] of [
    ['heaven_earth',12,['di','tian','tianjiang'],['shensha','nayin','xungan']],
    ['lessons',4,['index','tianpan','dizhi','tianjiang'],['name']],
    ['transmissions',3,['index','diZhi','tianjiang','liuqin'],['name','tianGan','status','earth_position']]]) {
    list(c[field],field,length,length);
    c[field].forEach((row,i)=>{keys(row,fields,extra,'packet.chart.facts.'+field+'['+i+']');for(const k of fields.filter(k=>k!=='index'))text(row[k],field+'.'+k,30);});
  }
  if(new Set(c.heaven_earth.map(r=>r.di)).size!==12||new Set(c.heaven_earth.map(r=>r.tian)).size!==12)fail('incomplete plate');
  for(const r of c.heaven_earth)if(!branchPattern.test(r.di)||!branchPattern.test(r.tian))fail('plate branch');
  for(const field of ['lessons','transmissions']) c[field].forEach((r,i)=>{if(r.index!==i+1)fail(field+' order');});
  list(p.facts,'facts');for(const [i,r] of p.facts.entries()){keys(r,['id','text','source'],[],'packet.facts['+i+']');text(r.text,'fact');text(r.source,'fact.source',1200);}const fids=ids(p.facts,'facts');
  list(p.entities,'entities',1,40);for(const [i,r] of p.entities.entries()){keys(r,['id','question_ids','referent','branch','position','mapping_basis'],[],'packet.entities['+i+']');refs(r.question_ids,qids,'entity questions');for(const k of ['referent','position','mapping_basis'])text(r[k],'entity.'+k);if(!entitySymbol(r.branch))fail('entities['+i+'].branch: 只填单干支、纯支组合或戊（寄宫巳）；注释放mapping_basis');}const eids=ids(p.entities,'entities');
  list(p.observations,'observations',0,80);for(const [i,r] of p.observations.entries()){keys(r,['id','entity_ids','kind','statement','reference','source','verification'],[],'packet.observations['+i+']');refs(r.entity_ids,eids,'observation entities');choice(r.kind,OBSERVATION_KINDS,'packet.observations['+i+'].kind');choice(r.verification,OBSERVATION_VERIFICATIONS,'packet.observations['+i+'].verification');for(const k of ['statement','reference','source'])text(r[k],'observation.'+k);}const oids=ids(p.observations,'observations');
  list(p.method_materials,'method_materials',0,40);for(const [i,r] of p.method_materials.entries()){keys(r,['id','title','source_path','quote'],['line_start','line_end','line_mode','sha256'],'packet.method_materials['+i+']');for(const k of ['title','source_path','quote'])text(r[k],'method.'+k,16000);const path=r.source_path.replaceAll('\\','/');if(/案例项目库|经验日志|experience-index|liuren-experience|expert-adjudication-cases/.test(path))fail('excluded library method source');if(!/(^|\/)(书籍库|books|runtime\/liuren|docs)\//.test(path)||path.split('/').includes('..'))fail('method source outside approved material roots');}const mids=ids(p.method_materials,'method_materials');
  list(p.focus_issues,'focus_issues',0,12);
  for(const [i,x] of p.focus_issues.entries()){
    keys(x,['id','question_ids','entity_ids','observation_ids','question'],[],'packet.focus_issues['+i+']');
    list(x.question_ids,'issue questions',1,12);refs(x.question_ids,qids,'issue questions');
    refs(x.entity_ids,eids,'issue entities');refs(x.observation_ids,oids,'issue observations');
    text(x.question,'issue question',2000);
  }
  const iids=ids(p.focus_issues,'focus_issues');
  const aliases=p.material_aliases??[];list(aliases,'material_aliases',0,40);
  for(const a of aliases){
   keys(a,['id','title','source_path','line_start','line_end','line_mode','sha256','canonical_id'],[],'material_alias');
   const target=p.method_materials.find(m=>m.id===a.canonical_id);if(!target)fail('material_alias canonical ID missing');
   for(const k of ['source_path','sha256','line_start','line_end','line_mode'])if(a[k]!==target[k])fail('material_alias differs from canonical source '+k);
   text(a.title,'material_alias.title',16000);
  }
  const aids=ids(aliases,'material_aliases');
  const all=[...qids,...fids,...eids,...oids,...mids,...iids,...aids];if(new Set(all).size!==all.length)fail('ids must be globally unique');
  if([...all].some(v=>/^E\d+$/.test(v)||v.startsWith('D_')))fail('E/D IDs reserved for book/program basis');
  texts(p.unknowns,'unknowns');validateFoundation(p);return p;
}

export function validateOutput(r,p) {
  validateInput(p);
  keys(r,['schema','request_id','status','scope_review','entity_checks','relation_checks','issue_resolutions','answers','source_conflicts','missing_inputs'],['special_methods','calculations']);
  if(r.schema!==OUTPUT_SCHEMA||r.request_id!==p.request_id)fail('output identity');
  bounded(r,80000,'output');choice(r.status,['completed','needs_input'],'output status');
  list(r.entity_checks,'entity_checks',0,60);
  for(const e of r.entity_checks){keys(e,['id','referent','branch','position','mapping_review','five_qi','twelve_states','site_yin','shenjiang','limits'],['fact_refs']);for(const k of ['referent','position','mapping_review','five_qi','twelve_states','site_yin','shenjiang'])text(e[k],'entity_check.'+k);if(!entitySymbol(e.branch))fail('checked entity symbol');texts(e.limits,'entity limits');}
  const eids=ids(r.entity_checks,'entity_checks');
  if(r.status==='completed')for(const e of p.entities)if(!eids.has(e.id))fail('omitted input entity '+e.id);
  keys(r.scope_review,['question_ids','mapping_status','added_entity_ids','corrections','omission_check'],[],'scope_review');
  refs(r.scope_review.question_ids,new Set(p.questions.map(q=>q.id)),'scope questions');
  if(new Set(r.scope_review.question_ids).size!==p.questions.length||r.scope_review.question_ids.length!==p.questions.length)fail('scope review must cover every question once');
  choice(r.scope_review.mapping_status,['confirmed','corrected','needs_input'],'mapping_status');
  texts(r.scope_review.corrections,'scope corrections');text(r.scope_review.omission_check,'scope omission check');
  refs(r.scope_review.added_entity_ids,eids,'added entities');
  const originals=new Map(p.entities.map(e=>[e.id,e]));
  const additions=r.entity_checks.filter(e=>!originals.has(e.id));
  if(additions.some(e=>!/^J[A-Za-z0-9_-]*$/.test(e.id)))fail('new entities must use J IDs');
  if(r.scope_review.added_entity_ids.length!==additions.length||new Set(r.scope_review.added_entity_ids).size!==additions.length||additions.some(e=>!r.scope_review.added_entity_ids.includes(e.id)))fail('scope added_entity_ids must identify every new entity exactly once');
  if(r.status==='completed'&&r.scope_review.mapping_status==='needs_input')fail('unresolved mapping cannot be completed');
  const changedSymbols=r.entity_checks.some(e=>originals.has(e.id)&&['referent','branch','position'].some(k=>e[k]!==originals.get(e.id)[k]));
  if(r.scope_review.mapping_status==='confirmed'&&(additions.length||changedSymbols||r.scope_review.corrections.length))fail('mapping changes must be declared as corrected or needs_input');
  if(r.scope_review.mapping_status==='corrected'&&!additions.length&&!r.scope_review.corrections.length)fail('corrected mapping requires concrete corrections');
  const basis=new Set([...Array.from({length:22},(_,i)=>'E'+String(i+1).padStart(2,'0')),...p.observations.map(x=>x.id),...p.method_materials.map(x=>x.id),...p.facts.map(x=>x.id),...(p.deterministic?[...p.deterministic.nodes.map(x=>x.id),...p.deterministic.stems.map(x=>x.id)]:[])]);
  list(r.relation_checks,'relation_checks',0,100);
  for(const x of r.relation_checks){keys(x,['id','from','to','relation','validity','basis_ids','reason','effect_scope'],['application','computed_relations']);if(!eids.has(x.from)||!eids.has(x.to))fail('relation entity missing');choice(x.validity,['effective','limited','ineffective','unresolved'],'relation validity');refs(x.basis_ids,basis,'relation basis');if(!x.basis_ids.length)fail('relation without basis');text(x.relation,'relation');text(x.reason,'relation reason');texts(x.effect_scope,'effect_scope');}
  const rids=ids(r.relation_checks,'relation_checks');
  list(r.issue_resolutions,'issue_resolutions',0,12);
  const issues=new Set(p.focus_issues.map(x=>x.id)),resolved=new Set();
  for(const x of r.issue_resolutions){
    keys(x,['issue_id','status','relation_ids','resolution','limits'],[],'issue_resolution');
    if(!issues.has(x.issue_id)||resolved.has(x.issue_id))fail('issue resolution unknown or duplicate issue');
    resolved.add(x.issue_id);choice(x.status,['resolved','unresolved'],'issue status');
    refs(x.relation_ids,rids,'issue relations');text(x.resolution,'issue resolution');texts(x.limits,'issue limits');
    if(x.status==='resolved'&&!x.relation_ids.length)fail('resolved issue requires checked relations');
    if(x.status==='unresolved'&&!x.limits.length)fail('unresolved issue requires a concrete limit');
  }
  if(resolved.size!==issues.size)fail('missing focus issue resolution');
  list(r.answers,'answers',1,12);const answered=new Set();
  for(const a of r.answers){keys(a,['question_id','verdict','precision','decisive_relation_ids','counter_relation_ids','counter_resolution','process','timing','conditions','limits']);if(!p.questions.some(q=>q.id===a.question_id)||answered.has(a.question_id))fail('answer question mismatch');answered.add(a.question_id);choice(a.precision,['exact','direction','unresolved'],'answer precision');for(const k of ['verdict','counter_resolution','process','timing'])text(a[k],'answer.'+k);refs(a.decisive_relation_ids,rids,'decisive relations');refs(a.counter_relation_ids,rids,'counter relations');texts(a.conditions,'answer conditions');texts(a.limits,'answer limits');if(r.status==='completed'&&a.precision!=='unresolved'&&!a.decisive_relation_ids.length)fail('verdict without decisive relations');}
  if(answered.size!==p.questions.length)fail('missing question answer');
  list(r.source_conflicts,'source_conflicts');for(const x of r.source_conflicts){keys(x,['basis_ids','issue','resolution']);refs(x.basis_ids,basis,'conflict basis');text(x.issue,'source conflict');text(x.resolution,'conflict resolution');}
  texts(r.missing_inputs,'missing_inputs');
  if(r.status==='needs_input'&&!r.missing_inputs.length)fail('needs_input requires concrete missing inputs');
  if(r.status==='completed'&&r.missing_inputs.length)fail('missing inputs cannot be completed');
  validateFactualOutput(r,p);return r;
}

export function parseTaskOutput(raw) {
  let value=raw.trim();
  const wrapped=value.match(/<task_result>\s*([\s\S]*?)\s*<\/task_result>/);
  if(wrapped)value=wrapped[1].trim();
  const fenced=value.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/);
  if(fenced)value=fenced[1].trim();
  try{return JSON.parse(value);}catch{fail('adjudicator did not return a JSON result');}
}
