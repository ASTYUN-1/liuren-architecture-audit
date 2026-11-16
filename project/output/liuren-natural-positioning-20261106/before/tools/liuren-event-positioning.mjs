// Event roles are the user's local workflow policy, not a universal classical claim.
// No model calls, outcome selection, kinship recursion, or silent remapping.
import fs from 'node:fs/promises';
import path from 'node:path';
export const EVENT_POLICY='liuren-event-positioning-v1';
export const EVENT_DOMAINS=['finance','recruitment','promotion-salary','relationship','interpersonal','period-outlook','long-period','pregnancy','exam','illness','lost-person-object','classical-conflict','home','travel','weather','agriculture'];
const fail=issues=>{throw new Error('LIUREN_EVENT_POSITIONING: '+JSON.stringify({issues,action:'按原问的事件主体修正定位/分类；保留占日干和原盘，不能换寄宫、改题干或换占类绕过检查。'}));};
export async function eventPolicy(root){
 const p=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
 return p.eventPositioning?.enabled===true;
}
export async function checkEventDispatch(root,p){
 if(!await eventPolicy(root))return;
 const pointer=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
 if(p.event_positioning?.schema!==EVENT_POLICY||p.event_positioning.release!==pointer.release)fail([{path:'/event_positioning',code:'rebuild_event_packet',expected:'用当前packet工具重新保存已核材料；旧裁决仍可领取，不重派'}]);
 const roles=checkEventInput(p);
 if(JSON.stringify(roles)!==JSON.stringify(p.event_positioning.questions))fail([{path:'/event_positioning/questions',code:'actor_record_mismatch'}]);
}
export async function eventDomains(root,p){
 if(!await eventPolicy(root))return [];
 const issues=[];
 for(const [i,q] of (p?.questions??[]).entries())if(!EVENT_DOMAINS.includes(q.domain))issues.push({path:'/questions/'+i+'/domain',code:'classification_required',expected:EVENT_DOMAINS});
 if(!p?.questions?.length)issues.push({path:'/questions',code:'questions_required'});
 if(issues.length)fail(issues);
 return [...new Set(p.questions.map(q=>q.domain))];
}
export function checkEventInput(p){
 const issues=[];
 for(const [i,q] of p.questions.entries()){
  if(!EVENT_DOMAINS.includes(q.domain)){issues.push({path:'/questions/'+i+'/domain',code:'classification_required'});continue;}
  const actor=p.entities.find(e=>e.id===q.actor_entity_id);
  if(q.actor_entity_id!==undefined&&(!actor||!actor.question_ids.includes(q.id)))issues.push({path:'/questions/'+i+'/actor_entity_id',code:'actor_reference',expected:'本问现有实体ID'});
  if(!['exam','illness'].includes(q.domain))continue;
  if(!actor){issues.push({path:'/questions/'+i+'/actor_entity_id',code:'event_actor_required',expected:q.domain==='exam'?'考生实体ID':'患者实体ID'});continue;}
  // Allow an explicit stem lodging annotation, but never substitute the lodging branch.
  if(![p.chart.facts.day_stem,p.chart.facts.day_stem+'（寄宫'+({甲:'寅',乙:'辰',丙:'巳',丁:'未',戊:'巳',己:'未',庚:'申',辛:'戌',壬:'亥',癸:'丑'}[p.chart.facts.day_stem])+'）',p.chart.facts.day_stem+'(寄宫'+({甲:'寅',乙:'辰',丙:'巳',丁:'未',戊:'巳',己:'未',庚:'申',辛:'戌',壬:'亥',癸:'丑'}[p.chart.facts.day_stem])+')'].includes(actor.branch))issues.push({path:'/entities/'+p.entities.indexOf(actor)+'/branch',code:'actor_must_be_day_stem',actual:actor.branch,expected:p.chart.facts.day_stem,referent:actor.referent});
 }
 if(issues.length)fail(issues);
 return p.questions.map(q=>({question_id:q.id,domain:q.domain,actor_entity_id:q.actor_entity_id??null,subject:q.subject}));
}
export function eventOutputIssues(r,p){
 if(p.event_positioning?.schema!==EVENT_POLICY||r.status!=='completed')return [];
 const issues=[];
 for(const role of p.event_positioning.questions){
  if(!['exam','illness'].includes(role.domain))continue;
  const input=p.entities.find(e=>e.id===role.actor_entity_id),at=(r.entity_checks??[]).findIndex(e=>e.id===role.actor_entity_id),actor=r.entity_checks?.[at];
  if(!actor||actor.branch!==input?.branch)issues.push({path:at<0?'/entity_checks':'/entity_checks/'+at+'/branch',code:'event_actor_mapping_changed',expected:input?.branch,actor_entity_id:role.actor_entity_id,action:'考生/患者仍为日干；纠正对象定位及受影响作用，不能沿用代问者六亲递推。'});
 }
 return issues;
}
