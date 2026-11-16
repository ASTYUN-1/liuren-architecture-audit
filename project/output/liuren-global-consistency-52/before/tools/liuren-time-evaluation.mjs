import {calendar} from './liuren-deterministic-calendar.mjs';
import {calculateSelectedStrength} from './liuren-palace-strength.mjs';
import {hash} from './liuren-deterministic.mjs';
export function evaluateTimes(c,q,{root}={}){
 const fail=m=>{throw Error('LIUREN_EVALUATION: '+m);};
 if(!q||Object.keys(q).some(k=>!['calendar','strength','void_policy'].includes(k)))fail('requires calendar, strength and optional void_policy');
 if(!q.calendar||!q.strength)fail('calendar and strength are required');
 const policy=q.void_policy??'original';
 if(!['original','evaluation-xun-research'].includes(policy))fail('void_policy must be original/evaluation-xun-research');
 const dates=calendar(q.calendar,{root});
 if(dates.rows.length>128)fail('more than 128 matched times; narrow query, do not truncate');
 const originalHash=hash(c);
 const rows=dates.rows.map(t=>{
  const evaluation={month_branch:t.month[1],basis:'引擎历法时间情景；'+q.strength.season_basis,
   ...(policy==='evaluation-xun-research'?{day_pillar:t.day}:{})};
  const r=calculateSelectedStrength(c,q.strength,{evaluation});
  return {datetime:t.datetime??t.date+'T'+String(q.calendar.hour??12).padStart(2,'0')+':'+String(q.calendar.minute??0).padStart(2,'0')+':00',
   day:t.day,month:t.month,hour:t.hour,xun:t.xun,evaluation_void:t.void_branches,
   ...(t.in_origin_xun!==undefined?{in_origin_xun:t.in_origin_xun}:{}),
   actors:r.actors,receipt_sha256:r.receipt_sha256};
 });
 if(hash(c)!==originalHash)fail('original chart mutated');
 return {schema:'liuren-time-evaluation-v1',chart_sha256:originalHash,void_policy:policy,original_void:c.void_branches,
  scope:'原盘位置和日干固定；按评价节月更新五气。original保留原空亡条件；evaluation-xun-research仅为以新旬替换的研究情景，不等于出旬填实规则已确定。',
  rows,calendar_sha256:dates.calendar_sha256};
}
