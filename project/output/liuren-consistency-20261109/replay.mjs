// Replay public historical evidence; never calls a model or modifies the old run.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {auditHash,POLICY,checkAudit,checkInputReview} from '../../tools/liuren-consistency-audit.mjs';
const out=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(out,'../..');
const read=rel=>fs.readFile(path.join(root,rel),'utf8');
const old='output/liuren-adjudication-requests/20261109-liuren-interview-97m-01-9785dfd2-565d-4d71-b707-b5ec75f96b9f.archive.json';
const original=await read(old),p=JSON.parse(original).packet,body=await read('output/dual-deepseek-audit-20261109/child-report.md');
const evidence=JSON.parse(await read('output/dual-deepseek-audit-20261109/evidence.json'));
const parts=evidence.sessions.ses_e40041ce9ffe2MOyH46R9WP7b9.parts;
const rows=parts.filter(r=>r.tool==='liuren_compute'&&r.status==='completed'&&r.input?.action==='strength').map(r=>({request:r.input,result:r.result}));
assert.equal(rows.length,2);
// Reconstructed audit attachment is an explicit audit annotation, not an old model submission.
const receipts=rows.map(r=>({ref:{sha256:auditHash(r)},...r}));
p.consistency_policy={...POLICY};
const source=p.input_origin.source_text,quote=needle=>{assert.ok(source.includes(needle));return needle;};
const line=needle=>{const value=body.split(/\r?\n/).find(s=>s.includes(needle));assert.ok(value,'report line '+needle);return value;};
p.input_review={questions:p.questions.map(q=>({question_id:q.id,request_quote:q.id==='Q_job'?quote('是什么工作？限二'):quote('面试是否通过'),success_basis:'历史交接复核，仅标记原问身份',stage_origin:'unknown',stage_basis:'原问未提供实际轮次和通过事实',...(q.id==='Q_job'?{max_candidates:2,limit_quote:quote('限二')}:{})})),facts:p.facts.map(f=>({fact_id:f.id,origin:'inferred',basis:'本回放不把历史主智能体整理的事实当作新增用户确认'})),neutrality_review:'审计重建附件，保留原交接的倾向问题，不改写原文件'};
assert.equal(checkInputReview(p).ok,true);
const relation=(id,source,target,role,report_quote)=>({id,source,target,question_ids:['Q_interview'],role,basis_refs:['program','core'],basis:'历史报告及盘面已有作用，审计不新增成败规则',effect_scope:'面试、文书及入职成功条件',disposition:'used',reason:'复核历史报告实际使用的扶助、克制和制救范围',report_quote,numeric:'supported'});
const audit={schema:POLICY.schema,
 questions:p.questions.map(q=>({question_id:q.id,request_quote:p.input_review.questions.find(x=>x.question_id===q.id).request_quote,stage_origin:'user_explicit',stage_basis:'面试后、结果未出',success_review:'审计重建：原问没有确认此阶段',answer_quote:line(q.id==='Q_job'?'文书':'面试'),candidates:q.id==='Q_job'?['文书/行政/合同资料大集合','金融/财务/贸易/物流大集合']:[],counterevidence:{present:q.id==='Q_interview',relation_ids:q.id==='Q_interview'?['R_hurt']:[],report_quote:q.id==='Q_interview'?line('这是通过后的一关'):'',resolution:q.id==='Q_interview'?'历史报告把申冲寅放在通过之后；审计要求核阶段依据':'职业候选边界由语义核查',basis_refs:['program']}})),
 relations:[relation('R_help_job','T:寅','T:巳','support',line('寅生')),relation('R_help_person','T:寅','S:丙','support',line('生干')),relation('R_hurt','T:申','T:寅','obstruction',line('申克寅')),relation('R_rescue','T:巳','T:申','rescue',line('巳克申'))],
 calculations:receipts.map((r,i)=>({receipt_sha256:r.ref.sha256,scope:'local',relation_ids:[i===0?'R_help_job':'R_help_person'],report_quote:line(i===0?'5.210':'5.703'),score_claims:[{actor:r.result.actors[0].id,path:'/actors/0/adjusted',value:r.result.actors[0].adjusted,report_quote:line(i===0?'5.210':'5.703')}]})),omission_review:'由公开日志重建核对附件；没有重新占断，不把已知反馈写入算法'};
const local=checkAudit(p,body,audit,receipts);
assert.ok(local.warnings.some(x=>x.code==='scenario_coverage'&&x.message.includes('R_hurt')));
assert.ok(local.issues.some(x=>x.code==='stage_quote'));
const combined=structuredClone(audit);combined.calculations.forEach(c=>c.scope='combined');
const result=checkAudit(p,body,combined,receipts);
assert.ok(result.issues.some(x=>x.code==='scenario_coverage'));
assert.equal(auditHash(await read(old)),auditHash(original));
const report={scope:'historical public-log replay; reconstructed attachment, not a new prediction',source_sha256:auditHash(original),modelCalls:0,oldPacketUnchanged:true,successfulStrengthCalls:rows.length,selectedLinks:rows.flatMap(r=>r.request.strength.links),localScenarioCheck:local,claimedCombinedScenarioCheck:result,manualSemanticFindings:['通过后阶段的分配没有用户事实依据；自动程序只能核来源声明，不能证明术理阶段归属。','两个职业条目各扩为多个行业；数量检查仍需主智能体复核候选边界。'],outcomeAssertion:false};
await fs.writeFile(path.join(out,'historical-replay.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({oldPacketUnchanged:true,modelCalls:0,successfulStrengthCalls:rows.length,detectedStageSourceGap:true,detectedOmittedNumericRelations:true,outcomeAssertion:false}));
