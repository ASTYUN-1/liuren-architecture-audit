import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {DOMAIN_ROUTES,checkRoutes,checkQuantityEvidence,routeSchema} from '../liuren-analysis-route.mjs';
import {EVENT_DOMAINS} from '../liuren-event-positioning.mjs';
import {packet} from './fixtures/liuren-adjudication-v2.mjs';
import {normalizePacket} from '../liuren-adjudication-files.mjs';
import {checkDeliveryReview,REVIEW_CHECKS,auditHash,createAuditSchemas} from '../liuren-consistency-audit.mjs';
import {adjustQuantity} from '../liuren-quantity-adjustment.mjs';
import {methodQuantity} from '../liuren-method-tools.mjs';
import {calculateSelectedStrength} from '../liuren-palace-strength.mjs';
import {GENERALS,kin} from '../liuren-deterministic.mjs';
import {tool} from '../../.opencode/node_modules/@opencode-ai/plugin/dist/index.js';

const route=()=>({event:'合成验收事件',focus:'class',primary_entity_ids:['S1'],selection_basis:'合成测试只测传递，不判取用',time_scope:'本次结果形成及兑现，通知另看'});
function input(){const p=packet();p.input_review={questions:[{question_id:'Q1',route:route()}]};p.consistency_policy={analysis_route_required:true};return p;}

test('all registered active domains including litigation are actually selectable',async()=>{
 const pointer=JSON.parse(await fs.readFile(new URL('../../.opencode/liuren-active.json',import.meta.url)));
 const manifest=JSON.parse(await fs.readFile(new URL('../../'+pointer.runtime+'/manifest.json',import.meta.url)));
 assert.deepEqual([...manifest.domains].sort(),[...EVENT_DOMAINS].sort());
 assert.equal(EVENT_DOMAINS.length,17);assert.ok(EVENT_DOMAINS.includes('litigation'));
 for(const domain of EVENT_DOMAINS){const p=input();p.questions[0].domain=domain;assert.deepEqual(checkRoutes(p,{required:true}),[]);assert.ok(DOMAIN_ROUTES[domain]);}
});
test('a route must address the same question, while relation and overall questions keep their own focus',()=>{
 const p=input();assert.deepEqual(checkRoutes(p,{required:true}),[]);
 delete p.input_review.questions[0].route;assert.equal(checkRoutes(p,{required:true}).length,1);assert.deepEqual(checkRoutes(p),[]);
 p.input_review.questions[0].route=route();p.entities[0].question_ids=['Q2'];assert.ok(checkRoutes(p,{required:true}).length);
 p.entities[0].question_ids=['Q1'];p.input_review.questions[0].route.focus='relationship';assert.ok(checkRoutes(p,{required:true}).length);
 p.entities.push({...p.entities[0],id:'S2'});p.input_review.questions[0].route.primary_entity_ids.push('S2');assert.deepEqual(checkRoutes(p,{required:true}),[]);
 p.input_review.questions[0].route={...route(),focus:'overall',primary_entity_ids:[]};assert.deepEqual(checkRoutes(p,{required:true}),[]);
});
test('ID normalization preserves route identities instead of silently severing the main target',()=>{
 const p=input();p.questions[0].id='E1';p.entities[0].id='E2';p.entities[0].question_ids=['E1'];
 p.observations[0].entity_ids=['E2'];p.focus_issues=[];p.input_review.questions[0]={question_id:'E1',route:{...route(),primary_entity_ids:['E2']}};
 const n=normalizePacket(p).packet;assert.equal(n.input_review.questions[0].question_id,'I_E1');
 assert.deepEqual(n.input_review.questions[0].route.primary_entity_ids,['I_E2']);assert.deepEqual(checkRoutes(n,{required:true}),[]);
});
test('native schema carries the same route and evidence-backed review shape',()=>{
 routeSchema(tool.schema).parse(route());
 const schemas=createAuditSchemas(tool.schema);assert.ok(schemas.review);
 assert.throws(()=>routeSchema(tool.schema).parse({...route(),guaranteed_verdict:'通过'}));
});
test('quantity changes bind actual text; prose-only exceptions and invented quotations fail',()=>{
 const p=input(),base={request:{action:'quantity',expression:{value:8}}};
 p.method_materials=[{id:'M_source',quote:'合成原法在特定条件下另有处理。'}];
 p.input_review.facts=[{fact_id:'F_scale',origin:'user_explicit',source_quote:'每份约定100元'}];
 const q={route:'experimental',magnitude:{exponent:1},void:{status:'exception'}};
 assert.throws(()=>checkQuantityEvidence(p,q,base),/magnitude/);
 q.evidence=[{use:'magnitude',ref:'F_scale',quote:'每份约定100元',application:'合成单位换算证据，仅测绑定'}];
 assert.throws(()=>checkQuantityEvidence(p,q,base),/void/);
 q.evidence.push({use:'void',ref:'M_source',quote:'特定条件下另有处理',application:'合成专项例外，专业效力仍由裁决核'});
 assert.doesNotThrow(()=>checkQuantityEvidence(p,q,base));
 q.evidence[1].quote='不存在的免减条款';assert.throws(()=>checkQuantityEvidence(p,q,base),/原句/);
 assert.doesNotThrow(()=>checkQuantityEvidence({},q,base),'old bound tasks retain their policy');
});
test('a source base-only result can finish its independently declared void step without an experimental multiplier',()=>{
 // Synthetic identity plate. No real question, result feedback or accuracy test.
 const c=packet().chart.facts;c.pillars[2]='甲申';c.day_stem='甲';c.day_branch='申';c.month_general='未';c.void_branches=['午','未'];
 c.heaven_earth.forEach((n,i)=>n.tianjiang=GENERALS[(i+11)%12]);
 const at=b=>c.heaven_earth.find(n=>n.tian===b);
 c.lessons=[['寅','甲'],['寅','寅'],['申','申'],['申','申']].map(([tianpan,dizhi],i)=>({index:i+1,tianpan,dizhi,tianjiang:at(tianpan).tianjiang}));
 c.transmissions.forEach(n=>{n.tianjiang=at(n.diZhi).tianjiang;n.liuqin=kin(c.day_stem,n.diZhi);});
 const target='T:未',baseRequest={action:'quantity',quantity_method:{id:'WY67-shenjiang-base',target,basis:'合成神将基础乘数，不作占断',unit:'分'}};
 const base=methodQuantity(c,baseRequest.quantity_method),strengthRequest={action:'strength',strength:{mode:'single_palace',season_profile:'four-seasons',season_basis:'合成测试',actors:[{id:target,role:'合成对象',basis:'接口测试'}]}};
 const strength=calculateSelectedStrength(c,strengthRequest.strength);
 const receipts=[{receipt_sha256:'a'.repeat(64),request:baseRequest,result:base},{receipt_sha256:'b'.repeat(64),request:strengthRequest,result:strength}];
 const q={route:'source',target,kind:'score',base_receipt_sha256:'a'.repeat(64),strength_receipt_sha256:'b'.repeat(64),
  base_factors:{qi:'raw',void:false,basis:'纯神将相乘未含空'},magnitude:{exponent:0,unit:'分',upper_bound:100,basis:'合成指定单位'},
  void:{status:'apply_half',origin:'user_research',basis:'合成测试指定数量自身空半，非声称古籍通则'},basis:'仅核有据后续步骤可执行'};
 const r=adjustQuantity(c,q,{receipts,decisionContext:input()});assert.equal(base.value,40);assert.equal(r.value,20);
 assert.equal(r.strength_used.scope,'single_palace');assert.deepEqual(r.review.steps.map(s=>s.kind),['void']);
 q.void.status='exception';assert.throws(()=>adjustQuantity(c,q,{receipts,decisionContext:input()}),/void/);
});
test('review binds every question route and evidence; old reports and explicit unresolved outcomes remain deliverable',()=>{
 const p=input();p.method_materials=[];p.facts=[];p.observations=[];const body='合成自由正文，不设固定专业栏目。';
 const review={report_sha256:auditHash(body),checks:REVIEW_CHECKS.map(check=>({check,status:'checked',report_quote:body,basis:'核本问实际事件和绑定方法'}))};
 assert.equal(checkDeliveryReview(review,body).ok,true);
 assert.equal(checkDeliveryReview(review,body,{packet:p}).ok,false);
 for(const row of review.checks)row.evidence_refs=['input','core','route:Q1'];
 assert.equal(checkDeliveryReview(review,body,{packet:p}).ok,true);
 review.checks[1].status='unresolved';assert.equal(checkDeliveryReview(review,body,{packet:p}).unresolved.length,1);
 review.checks[1].evidence_refs=['core'];assert.ok(checkDeliveryReview(review,body,{packet:p}).issues.some(i=>i.code==='review_route_coverage'));
});
