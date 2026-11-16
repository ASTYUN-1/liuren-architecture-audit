// Classification and versioned method transport only; event roles are interpreted by the model.
import fs from 'node:fs/promises';
import path from 'node:path';
export const EVENT_POLICY='liuren-event-positioning-v1';
export const EVENT_DOMAINS=['finance','recruitment','promotion-salary','relationship','interpersonal','period-outlook','long-period','pregnancy','exam','illness','lost-person-object','classical-conflict','home','travel','weather','agriculture'];
const fail=issues=>{throw new Error('LIUREN_METHOD_HANDOFF: '+JSON.stringify({issues,action:'补齐本问分类或重新保存当前版本文件；程序不判断人物身份或指定干支角色。'}));};
export async function eventPolicy(root){
 const p=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
 return p.eventPositioning?.enabled===true;
}
export async function checkDomainHandoff(root,p){
 if(!await eventPolicy(root))return;
 const pointer=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
 if(p.event_positioning?.schema!==EVENT_POLICY||p.event_positioning.release!==pointer.release)fail([{path:'/event_positioning',code:'rebuild_method_packet',expected:'用当前packet工具重新保存材料；旧裁决仍可领取，不重派'}]);
 const questions=classificationRecord(p);
 if(JSON.stringify(questions)!==JSON.stringify(p.event_positioning.questions))fail([{path:'/event_positioning/questions',code:'classification_record_mismatch'}]);
}
export async function eventDomains(root,p){
 if(!await eventPolicy(root))return [];
 classificationRecord(p);
 return [...new Set(p.questions.map(q=>q.domain))];
}
export function classificationRecord(p){
 const issues=[];
 for(const [i,q] of (p?.questions??[]).entries())if(!EVENT_DOMAINS.includes(q.domain))issues.push({path:'/questions/'+i+'/domain',code:'classification_required',expected:EVENT_DOMAINS});
 if(!p?.questions?.length)issues.push({path:'/questions',code:'questions_required'});
 if(issues.length)fail(issues);
 return p.questions.map(q=>({question_id:q.id,domain:q.domain,subject:q.subject}));
}
