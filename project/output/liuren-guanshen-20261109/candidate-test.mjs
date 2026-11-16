import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {resolveShensha} from '../../tools/liuren-shensha.mjs';
import {correctEngineShensha} from '../../tools/liuren-engine-shensha.mjs';
const root=new URL('../../',import.meta.url);
const read=async p=>JSON.parse(await fs.readFile(new URL(p,root),'utf8'));
const old=await read('runtime/liuren/20261109-deterministic-tools-35/references/shensha-policy.json');
const policy=await read('runtime/liuren/20261109-guanshen-36/references/shensha-policy.json');
assert.deepEqual(policy.rules.slice(0,-1),old.rules);
assert.deepEqual(policy.disabled,old.disabled);
const Z=[...'子丑寅卯辰巳午未申酉戌亥'];
const J=['贵人','腾蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后'];
const fixture=m=>({schema:'liuren-chart-facts-v1',year_pillar:'丙午',day_pillar:'庚戌',month_branch:m,
 heaven_earth:Z.map((tian,i)=>({tian,di:Z[(i+5)%12],tianjiang:J[i],shensha:i===0?['关神']:[]}))});
let cases=0;
for(const [months,expected] of [['寅卯辰','丑'],['巳午未','辰'],['申酉戌','未'],['亥子丑','戌']])
 for(const month of months){
  const f=fixture(month),before=JSON.stringify(f),r=resolveShensha(f,policy),gate=r.items.find(x=>x.id==='S33');
  assert.equal(gate.status,'resolved');assert.deepEqual(gate.places,[{tian:expected,di:Z[(Z.indexOf(expected)+5)%12],jiang:J[Z.indexOf(expected)]}]);
  assert.equal(gate.engine_check,'不同，采用重算');
  assert.deepEqual(r.items.filter(x=>x.id!=='S33'),resolveShensha(f,old).items);
  const corrected=correctEngineShensha(f,policy,r).facts.heaven_earth;
  assert.deepEqual(corrected.filter(x=>x.shensha.includes('关神')).map(x=>x.tian),[expected]);
  assert.equal(JSON.stringify(f),before);
  assert.deepEqual(gate.places,r.items.find(x=>x.id==='S23').places);
  assert.equal(r.items.filter(x=>['S23','S33'].includes(x.id)).length,2);
  cases++;
 }
assert.equal(resolveShensha(fixture(null),policy).items.find(x=>x.id==='S33').status,'missing_input');
assert.equal(resolveShensha(fixture('错'),policy).items.find(x=>x.id==='S33').status,'invalid_input');
for(const e of Object.values((await read('output/liuren-guanshen-20261109/原文核查证据.json')).evidence)){
 const b=await fs.readFile(new URL(e.path,root));
 assert.equal(crypto.createHash('sha256').update(b).digest('hex'),e.sha256);
 assert.equal(b.toString('utf8').replace(/^\uFEFF/,'').split('\n').slice(e.line_start-1,e.line_end).map(x=>x.replace(/\r+$/,'')).join('\n'),e.quote);
}
console.log(JSON.stringify({passed:true,monthCases:cases,oldRulesUnchanged:38,disabledNamesUnchanged:22,sourceEvidencePassed:true}));
