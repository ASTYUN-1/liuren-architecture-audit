import fs from 'node:fs/promises';
import path from 'node:path';
import {canonicalEntity} from '../../tools/liuren-deterministic.mjs';
import {finalizeFoundation} from '../../tools/liuren-deterministic-io.mjs';
import {validateOutput} from '../../tools/liuren-adjudication-contract.mjs';
const root=process.cwd(),dir=path.join(root,'output/liuren-flow-audit-20261106');
const files=(await fs.readdir(path.join(root,'output/liuren-adjudication-requests'))).filter(f=>f.startsWith('LR-20261106-113121-transfer-school-')).sort();
const packets=[];const report={replay:[],changes:[]};
for(let i=0;i<files.length;i++){
 const p=JSON.parse(await fs.readFile(path.join(root,'output/liuren-adjudication-requests',files[i]),'utf8')).packet;packets.push(p);
 if(i>=2)continue;
 const r=JSON.parse(await fs.readFile(path.join(dir,`child-${i+1}-output.json`),'utf8'));
 const a={child:i+1,input_entities:p.entities.map(({id,branch})=>({id,branch})),invalid_entities:[]};
 for(let j=0;j<r.entity_checks.length;j++){const e=r.entity_checks[j];try{canonicalEntity(e.branch,p.deterministic);}catch(error){a.invalid_entities.push({path:`entity_checks[${j}].branch`,id:e.id,branch:e.branch,error:String(error)});}}
 try{validateOutput(finalizeFoundation(root,r,p),p);a.passed=true;}catch(error){a.error=String(error);}
 if(i===0){
  const diagnostic=structuredClone(r);
  for(const e of diagnostic.entity_checks)e.branch=e.branch.replace(/（.*）$/u,'');
  try{validateOutput(finalizeFoundation(root,diagnostic,p),p);a.diagnostic_branch_only_passed=true;}catch(error){a.diagnostic_next_error=String(error);}
  for(const s of diagnostic.special_methods??[])s.basis_ids=s.basis_ids.filter(id=>!/^D_/.test(id));
  try{validateOutput(finalizeFoundation(root,diagnostic,p),p);a.diagnostic_branch_and_source_only_passed=true;}catch(error){a.diagnostic_next_error_after_source_filter=String(error);}
  const filled=finalizeFoundation(root,diagnostic,p);
  a.diagnostic_timing=filled.special_methods.filter(s=>s.kind==='timing').map(s=>({calculation_ids:s.calculation_ids,candidates:s.record.candidates,computed_dates:[...p.deterministic.calculations,...filled.calculations].filter(c=>s.calculation_ids.includes(c.id)&&c.action==='calendar').flatMap(c=>c.result.rows).map(d=>({date:d.date,day:d.day}))}));
  for(const s of diagnostic.special_methods??[])if(s.kind==='timing'&&s.candidates){s.record.candidates=s.candidates;delete s.candidates;}
  try{validateOutput(finalizeFoundation(root,diagnostic,p),p);a.diagnostic_three_format_changes_passed=true;}catch(error){a.diagnostic_next_error_after_candidate_move=String(error);}
 }
 report.replay.push(a);
}
for(let i=1;i<packets.length;i++){
 const a=packets[i-1],b=packets[i];const keys=[...new Set([...Object.keys(a),...Object.keys(b)])];
 report.changes.push({from:i,to:i+1,fields:keys.filter(k=>JSON.stringify(a[k])!==JSON.stringify(b[k])).map(k=>({field:k,before_length:JSON.stringify(a[k])?.length,after_length:JSON.stringify(b[k])?.length,before_count:Array.isArray(a[k])?a[k].length:undefined,after_count:Array.isArray(b[k])?b[k].length:undefined})),entity_ids:b.entities.map(e=>({id:e.id,branch:e.branch})),facts:b.facts,observations:b.observations});
}
await fs.writeFile(path.join(dir,'replay-evidence.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({replay:report.replay,changes:report.changes.map(({from,to,fields,entity_ids})=>({from,to,fields,entity_ids}))},null,2));
