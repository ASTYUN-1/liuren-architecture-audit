// Contract checks for the slim-registered adjudicator. No model or filesystem calls.
export const AGENT = 'liuren-adjudicator';
export const MODEL = 'deepseek/deepseek-flash';
export const INPUT_SCHEMA = 'liuren-adjudication-input-v1';
export const OUTPUT_SCHEMA = 'liuren-adjudication-output-v1';
const idPattern = /^[A-Za-z][A-Za-z0-9_-]{0,63}$/;
const branchPattern = /^[子丑寅卯辰巳午未申酉戌亥]$/;
const fail = message => { throw new Error('LIUREN_ADJUDICATION_CONTRACT: '+message); };
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
function keys(x, required, optional=[], where='object') {
  if (!object(x)) fail(where+' must be an object');
  for (const k of required) if (!(k in x)) fail(where+' missing '+k);
  for (const k of Object.keys(x)) if (![...required,...optional].includes(k)) fail(where+' unexpected '+k);
}
function text(x,where,max=6000) { if(typeof x!=='string'||!x.trim()||x.length>max)fail(where+' invalid text'); }
function list(x,where,min=0,max=100) { if(!Array.isArray(x)||x.length<min||x.length>max)fail(where+' invalid array'); }
function texts(x,where) {list(x,where);x.forEach(v=>text(v,where));}
function choice(x,values,where){if(!values.includes(x))fail(where+' invalid value');}
function ids(rows,where){const seen=new Set();for(const row of rows){if(!idPattern.test(row.id)||seen.has(row.id))fail(where+' invalid/duplicate id');seen.add(row.id);}return seen;}
function refs(values,known,where){texts(values,where);for(const v of values)if(!known.has(v))fail(where+' unknown reference '+v);}
function bounded(x,max,where){if(JSON.stringify(x).length>max)fail(where+' exceeds size limit');}

export function validateInput(p) {
  keys(p,['schema','request_id','questions','chart','facts','entities','observations','method_materials','unknowns']);
  if(p.schema!==INPUT_SCHEMA||!idPattern.test(p.request_id))fail('input identity');
  bounded(p,100000,'input');
  list(p.questions,'questions',1,12);
  for(const q of p.questions){keys(q,['id','text','subject','stage','deadline','success_criteria','alternatives']);for(const k of ['text','subject','stage','deadline','success_criteria'])text(q[k],'question.'+k);texts(q.alternatives,'alternatives');}
  const qids=ids(p.questions,'questions');
  keys(p.chart,['source','facts']);text(p.chart.source,'chart.source',1200);
  const c=p.chart.facts;
  keys(c,['schema','pillars','day_stem','day_branch','month_branch','hour_branch','month_general','void_branches','heaven_earth','lessons','transmissions'],
    ['year_pillar','month_pillar','day_pillar','hour_pillar','xun','event_datetime','lunar','transmission_sequence','chart_types','participants','year_life_verified','declared_life','nobleman','growth','seasonal_strength']);
  if(c.schema!=='liuren-chart-facts-v1')fail('chart facts schema');
  if(!/^[甲乙丙丁戊己庚辛壬癸]$/.test(c.day_stem))fail('day_stem');
  for(const k of ['day_branch','month_branch','hour_branch','month_general'])if(!branchPattern.test(c[k]))fail(k);
  list(c.pillars,'pillars',4,4);c.pillars.forEach(v=>{if(!/^[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]$/.test(v))fail('pillar');});
  list(c.void_branches,'void_branches',2,2);if(new Set(c.void_branches).size!==2||!c.void_branches.every(v=>branchPattern.test(v)))fail('void branches');
  for(const [field,length,fields,extra] of [
    ['heaven_earth',12,['di','tian','tianjiang'],['shensha','nayin','xungan']],
    ['lessons',4,['index','tianpan','dizhi','tianjiang'],['name']],
    ['transmissions',3,['index','diZhi','tianjiang','liuqin'],['name','tianGan','status','earth_position']]]) {
    list(c[field],field,length,length);
    c[field].forEach(row=>{keys(row,fields,extra,field);for(const k of fields.filter(k=>k!=='index'))text(row[k],field+'.'+k,30);});
  }
  if(new Set(c.heaven_earth.map(r=>r.di)).size!==12||new Set(c.heaven_earth.map(r=>r.tian)).size!==12)fail('incomplete plate');
  for(const r of c.heaven_earth)if(!branchPattern.test(r.di)||!branchPattern.test(r.tian))fail('plate branch');
  for(const field of ['lessons','transmissions']) c[field].forEach((r,i)=>{if(r.index!==i+1)fail(field+' order');});
  list(p.facts,'facts');for(const r of p.facts){keys(r,['id','text','source']);text(r.text,'fact');text(r.source,'fact.source',1200);}const fids=ids(p.facts,'facts');
  list(p.entities,'entities',1,40);for(const r of p.entities){keys(r,['id','question_ids','referent','branch','position','mapping_basis']);refs(r.question_ids,qids,'entity questions');for(const k of ['referent','position','mapping_basis'])text(r[k],'entity.'+k);if(!branchPattern.test(r.branch))fail('entity branch');}const eids=ids(p.entities,'entities');
  list(p.observations,'observations',0,80);for(const r of p.observations){keys(r,['id','entity_ids','kind','statement','reference','source','verification']);refs(r.entity_ids,eids,'observation entities');choice(r.kind,['five_qi','twelve_states','relation','void','shenjiang','structure','movement','special_method'],'observation.kind');choice(r.verification,['chart_checked','method_interpretation','unverified'],'verification');for(const k of ['statement','reference','source'])text(r[k],'observation.'+k);}const oids=ids(p.observations,'observations');
  list(p.method_materials,'method_materials',0,20);for(const r of p.method_materials){keys(r,['id','title','source_path','quote']);for(const k of ['title','source_path','quote'])text(r[k],'method.'+k,16000);const path=r.source_path.replaceAll('\\','/');if(/案例项目库|经验日志|experience-index|liuren-experience|expert-adjudication-cases/.test(path))fail('excluded library method source');if(!/(^|\/)(书籍库|books|runtime\/liuren|docs)\//.test(path)||path.split('/').includes('..'))fail('method source outside approved material roots');}const mids=ids(p.method_materials,'method_materials');
  const all=[...qids,...fids,...eids,...oids,...mids];if(new Set(all).size!==all.length)fail('ids must be globally unique');
  if([...all].some(v=>/^E\d+$/.test(v)))fail('E IDs reserved for book basis');
  texts(p.unknowns,'unknowns');return p;
}

export function validateOutput(r,p) {
  validateInput(p);
  keys(r,['schema','request_id','status','entity_checks','relation_checks','answers','source_conflicts','missing_inputs']);
  if(r.schema!==OUTPUT_SCHEMA||r.request_id!==p.request_id)fail('output identity');
  bounded(r,80000,'output');choice(r.status,['completed','needs_input'],'output status');
  list(r.entity_checks,'entity_checks',0,60);
  for(const e of r.entity_checks){keys(e,['id','referent','branch','position','mapping_review','five_qi','twelve_states','site_yin','shenjiang','limits']);for(const k of ['referent','position','mapping_review','five_qi','twelve_states','site_yin','shenjiang'])text(e[k],'entity_check.'+k);if(!branchPattern.test(e.branch))fail('checked branch');texts(e.limits,'entity limits');}
  const eids=ids(r.entity_checks,'entity_checks');
  if(r.status==='completed')for(const e of p.entities)if(!eids.has(e.id))fail('omitted input entity '+e.id);
  const basis=new Set([...Array.from({length:22},(_,i)=>'E'+String(i+1).padStart(2,'0')),...p.observations.map(x=>x.id),...p.method_materials.map(x=>x.id),...p.facts.map(x=>x.id)]);
  list(r.relation_checks,'relation_checks',0,100);
  for(const x of r.relation_checks){keys(x,['id','from','to','relation','validity','basis_ids','reason','effect_scope']);if(!eids.has(x.from)||!eids.has(x.to))fail('relation entity missing');choice(x.validity,['effective','limited','ineffective','unresolved'],'relation validity');refs(x.basis_ids,basis,'relation basis');if(!x.basis_ids.length)fail('relation without basis');text(x.relation,'relation');text(x.reason,'relation reason');texts(x.effect_scope,'effect_scope');}
  const rids=ids(r.relation_checks,'relation_checks');
  list(r.answers,'answers',1,12);const answered=new Set();
  for(const a of r.answers){keys(a,['question_id','verdict','precision','decisive_relation_ids','counter_relation_ids','counter_resolution','process','timing','conditions','limits']);if(!p.questions.some(q=>q.id===a.question_id)||answered.has(a.question_id))fail('answer question mismatch');answered.add(a.question_id);choice(a.precision,['exact','direction','unresolved'],'answer precision');for(const k of ['verdict','counter_resolution','process','timing'])text(a[k],'answer.'+k);refs(a.decisive_relation_ids,rids,'decisive relations');refs(a.counter_relation_ids,rids,'counter relations');texts(a.conditions,'answer conditions');texts(a.limits,'answer limits');if(r.status==='completed'&&a.precision!=='unresolved'&&!a.decisive_relation_ids.length)fail('verdict without decisive relations');}
  if(answered.size!==p.questions.length)fail('missing question answer');
  list(r.source_conflicts,'source_conflicts');for(const x of r.source_conflicts){keys(x,['basis_ids','issue','resolution']);refs(x.basis_ids,basis,'conflict basis');text(x.issue,'source conflict');text(x.resolution,'conflict resolution');}
  texts(r.missing_inputs,'missing_inputs');
  if(r.status==='needs_input'&&!r.missing_inputs.length)fail('needs_input requires concrete missing inputs');
  if(r.status==='completed'&&r.missing_inputs.length)fail('missing inputs cannot be completed');
  return r;
}

export function parseTaskOutput(raw) {
  let value=raw.trim();
  const wrapped=value.match(/<task_result>\s*([\s\S]*?)\s*<\/task_result>/);
  if(wrapped)value=wrapped[1].trim();
  const fenced=value.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/);
  if(fenced)value=fenced[1].trim();
  try{return JSON.parse(value);}catch{fail('adjudicator did not return a JSON result');}
}
