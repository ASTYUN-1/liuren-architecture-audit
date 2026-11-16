import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {seasonal} from '../liuren-deterministic.mjs';
import {trialComputeRequest,withTrialChartBasis,TRIAL_DECISION_POLICY} from '../liuren-trial-decision.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
registerHooks({resolve(specifier,context,next){if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);return next(specifier,context);}});
const {default:plugin}=await import('../../.opencode/plugins/liuren-adjudication.ts');
const hooks=await plugin({directory:root,client:{session:{messages:async()=>({data:[]})}}});
const ctx={agent:'liuren',sessionID:'month_initial_synthetic_no_model'};
const audit=JSON.parse(await fs.readFile(path.join(root,'output/opencode-trial60-newfive-20261115-07-deepseek/execution-audit.json'),'utf8'));
const archive=audit.cases[0].archives[0];
const ref={path:archive.path,sha256:archive.sha256};

test('all twelve months follow element month qi including four earth months',()=>{
 const dominant={寅:'木',卯:'木',辰:'土',巳:'火',午:'火',未:'土',申:'金',酉:'金',戌:'土',亥:'水',子:'水',丑:'土'};
 for(const [month,el] of Object.entries(dominant))assert.equal(seasonal(el,month,'quarter-earth'),'旺');
 assert.deepEqual(['木','火','土','金','水'].map(el=>seasonal(el,'未','quarter-earth')),['囚','休','旺','相','死']);
});

test('actual trial chart query has one adopted profile and retains initial special conditions',async()=>{
 const f=JSON.parse(await hooks.tool.liuren_compute.execute({action:'chart',archive:ref},ctx));
 const row=f.heaven_earth.find(r=>r.tian==='巳');
 assert.equal(row.state.month_qi,'休');assert.equal(row.state.growth_ground,'病');
 assert.equal(row.state.strength_index,3.655);
 assert.equal(f.strength_model.season_profile,'quarter-earth');
 assert.equal(f.strength_model.seasonal_keys,undefined);
 const initial=f.trial_chart_basis.initial_transmission;
 assert.equal(initial.branch,'巳');assert.equal(initial.ground,'申');assert.equal(initial.general,'太阴');
 assert.ok(initial.shensha.some(s=>s[0]==='S07'));assert.equal(initial.branch_state.month_qi,'休');
 assert.equal(initial.role_in_question,null);assert.equal(initial.event_effect,null);
 assert.ok(!JSON.stringify(f).includes('"四季":'));
 const focused=JSON.parse(await hooks.tool.liuren_compute.execute({action:'chart',archive:ref,symbols:['寅']},ctx));
 assert.equal(focused.heaven_earth.length,1);
 assert.equal(focused.trial_chart_basis.initial_transmission.branch_state.month_qi,'休');
});

test('actual strength and lookup reject prohibited profile, default lookup uses month qi',async()=>{
 const q={action:'strength',archive:ref,strength:{mode:'single_palace',season_profile:'quarter-earth',season_basis:'五行月令旺相休囚死',actors:[{id:'T:巳',role:'接口核验对象',basis:'引用既有盘核月气，不作预测'}],review:true}};
 const out=JSON.parse(await hooks.tool.liuren_compute.execute(q,ctx));
 assert.ok(Math.abs(out.actors[0].single_palace-3.655152)<1e-6);
 assert.equal(out.review.state_basis[0].month_qi,'休');
 assert.equal(out.review.season_comparison,undefined);
 assert.equal(out.season_profile,'quarter-earth');
 assert.ok(!JSON.stringify(out).includes('"four-seasons":'));
 await assert.rejects(()=>hooks.tool.liuren_compute.execute({...q,strength:{...q.strength,season_profile:'four-seasons'}},ctx),/LIUREN_TRIAL_SEASON/);
 const lookup=JSON.parse(await hooks.tool.liuren_compute.execute({action:'lookup',archive:ref,lookup:{subject:'巳',place:'申'}},ctx));
 assert.equal(lookup.seasonal.value,'休');assert.equal(lookup.growth,'病');
 assert.ok(!JSON.stringify(lookup).includes('four-seasons'));
 assert.throws(()=>trialComputeRequest({action:'lookup',lookup:{subject:'巳',profile:'four-seasons'}}),/LIUREN_TRIAL_SEASON/);
});

test('compute help no longer offers competing seasonal enum',async()=>{
 const h=JSON.parse(await hooks.tool.liuren_tool_help.execute({topic:'compute'},ctx));
 assert.ok(!JSON.stringify(h.parameters).includes('four-seasons'));
 assert.ok(JSON.stringify(h.parameters).includes('quarter-earth'));
});

test('initial branch and general keep independent states; program does not choose event meaning',()=>{
 const raw={ok:true,facts:{transmissions:[{diZhi:'申',liuqin:'官鬼',tianjiang:'青龙',status:'旬空'}],heaven_earth:[{id:'D_B8',tian:'申',di:'巳',tianjiang:'青龙',liuqin:'官鬼',state:{month_qi:'相',growth_ground:'长生',strength_index:3.6},general_state:{month_qi:'囚',growth_carrier:'绝',strength_index:.855},shensha:[['S03','日驿马']]}]}};
 const original=structuredClone(raw),out=withTrialChartBasis(raw),i=out.trial_chart_basis.initial_transmission;
 assert.deepEqual(raw,original);assert.equal(i.branch_state.month_qi,'相');assert.equal(i.general_state.month_qi,'囚');
 assert.equal(i.role_in_question,null);assert.equal(i.event_effect,null);
 assert.match(TRIAL_DECISION_POLICY.initial,/不自动替换主类/);
 assert.match(TRIAL_DECISION_POLICY.event_dimensions,/待遇差直接判不录用/);
});
