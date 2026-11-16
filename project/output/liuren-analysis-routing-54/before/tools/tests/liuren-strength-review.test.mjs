import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {calculateSelectedStrength} from '../liuren-palace-strength.mjs';
const {facts:c}=JSON.parse(await fs.readFile(new URL('../../output/liuren-energy-yin-20261106-1443/chart-result.json',import.meta.url),'utf8'));
const actors=['T:酉','T:子','T:卯'].map(id=>({id,role:'工程核查对象',basis:'只检验事实与传输，不作本课取用或预测'}));
const request={mode:'selected_relations',season_profile:'quarter-earth',season_basis:'工程固定条件表',actors,
 links:[{source:'T:酉',target:'T:子',basis:'工程指定金生水通路'}]};

test('review preserves numerical results, scopes factual pairs and never silently applies candidates',()=>{
 const before=JSON.stringify(c),plain=calculateSelectedStrength(c,request),reviewed=calculateSelectedStrength(c,{...request,review:true});
 assert.equal(JSON.stringify(c),before);
 assert.deepEqual(reviewed.actors,plain.actors);assert.deepEqual(reviewed.applied_relations,plain.applied_relations);
 assert.equal(plain.review,undefined);assert.equal(reviewed.coverage.semantic_role_validated,false);
 assert.equal(reviewed.coverage.relation_applicability_validated,false);assert.equal(reviewed.coverage.event_verdict_supported,false);
 assert.equal(reviewed.review.relation_candidates.length,3);
 const clash=reviewed.review.relation_candidates.find(x=>x.actors.includes('T:酉')&&x.actors.includes('T:卯'));
 assert.ok(clash.facts.some(x=>x.type==='六冲'));assert.equal(clash.submitted,false);
 const punishment=reviewed.review.relation_candidates.find(x=>x.actors.includes('T:子')&&x.actors.includes('T:卯'));
 assert.ok(punishment.facts.some(x=>x.type==='刑'&&x.from==='子'));
 assert.ok(punishment.facts.some(x=>x.type==='刑'&&x.from==='卯'));
 assert.equal(reviewed.applied_relations.length,1);
});
test('season comparison reuses the same actors and links and exposes differences without choosing a winner',()=>{
 const a=calculateSelectedStrength(c,{...request,review:true});
 const b=calculateSelectedStrength(c,{...request,season_profile:'four-seasons'});
 for(const row of a.review.season_comparison.rows){
  assert.equal(row.comparison,b.actors.find(x=>x.id===row.id).adjusted);
  assert.equal(row.selected,a.actors.find(x=>x.id===row.id).adjusted);
 }
 assert.ok(a.review.season_comparison.rows.some(x=>x.delta!==0));
 assert.equal(a.season_profile,'quarter-earth');
});
test('state inspection distinguishes original and evaluated voids; generals have no own branch void flag',()=>{
 const q={...request,mode:'single_palace',links:[],actors:[...actors,{id:'J:白虎',role:'工程天将对象',basis:'工程核查'}],review:true};
 const a=calculateSelectedStrength(c,q,{evaluation:{month_branch:'寅',day_pillar:'甲子',basis:'明确时间情景'}});
 const row=a.review.state_basis.find(x=>x.id==='T:子');
 assert.equal(row.month,'寅');assert.equal(row.void_self,false);assert.equal(row.references.length,2);
 assert.deepEqual(row.evaluation_void,['戌','亥']);
 assert.equal(a.review.state_basis.find(x=>x.id==='J:白虎').void_self,null);
 assert.equal(a.actors.find(x=>x.id==='T:子').delta,0);
});
test('review cannot inject arbitrary coefficients or bypass request validation',()=>{
 for(const review of ['true',1,{},null])assert.throws(()=>calculateSelectedStrength(c,{...request,review}),/布尔/);
 assert.throws(()=>calculateSelectedStrength(c,{...request,review:true,coefficient:1}),/系数/);
 assert.throws(()=>calculateSelectedStrength(c,{...request,review:true,actors:[]}),/取用对象/);
});
