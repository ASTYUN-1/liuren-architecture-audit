import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {scanBasicBifa,basicBifaCatalog,BASIC_BIFA_RULES_SHA256} from '../liuren-bifa-basic.mjs';
import {geometryChart} from '../liuren-bifa-batch.mjs';
const root=new URL('../../',import.meta.url),base=new URL('output/liuren-bifa-audit-20261111/',root);
const variants=JSON.parse(await fs.readFile(new URL('engine-day-night-1440.json',base),'utf8'));
const registry=JSON.parse(await fs.readFile(new URL('../liuren-bifa-basic-rules.json',import.meta.url),'utf8'));
const hash=x=>createHash('sha256').update(x).digest('hex');
const get=(day,upper,mode='昼贵')=>geometryChart(variants.find(v=>v.day===day&&v.day_upper===upper&&v.mode===mode));
const ids=c=>scanBasicBifa(c).matches.map(r=>r.id);

test('all 200 nonempty continuous quotations bind to unchanged approved source bytes',async()=>{
 assert.equal(registry.sources.reduce((n,s)=>n+s.excerpts.length,0),200);
 for(const s of registry.sources){
  const bytes=await fs.readFile(new URL(s.path,root));assert.equal(hash(bytes),s.sha256);
  const lines=bytes.toString('utf8').replace(/^\uFEFF/,'').replaceAll('\r\n','\n').replaceAll('\r','\n').split('\n');
  for(const e of s.excerpts){assert.ok(e.quote.trim().length>10,e.id);assert.equal(lines.slice(e.line_start-1,e.line_end).join('\n'),e.quote,e.id);}
 }
 const d22=registry.sources[0].excerpts.find(e=>e.id==='BF-D22');
 assert.ok(d22.quote.includes('甲申日干上亥'));assert.ok(d22.quote.includes('上下俱合格'));
});

test('explicit book examples are found without consulting native labels',()=>{
 const cases=[
  ['乙未','卯','BF02-boundary'],['乙丑','子','BF21-cross'],
  ['乙酉','辰','BF22-main'],['甲申','亥','BF22-vertical'],['戊辰','丑','BF22-upper'],
  ['甲申','亥','BF23-to-stem'],['庚寅','巳','BF24-to-branch'],
  ['己丑','卯','BF26-ding'],['己丑','卯','BF26-horse'],['己丑','卯','BF27-drain'],
  ['辛丑','子','BF31-chain'],['丙辰','戌','BF32-chain'],['庚午','午','BF37-assist'],
  ['丙寅','申','BF41-luma'],['壬午','戌','BF51-gate'],['辛丑','丑','BF61-tomb'],
  ['乙未','巳','BF70-two'],['辛卯','亥','BF77-cross'],['丙寅','寅','BF77-each'],
  ['乙酉','申','BF83-call'],['壬午','午','BF85-clamp','夜贵'],['己丑','卯','BF91-tiger','夜贵'],
 ];
 for(const [day,upper,id,mode] of cases){const c=get(day,upper,mode);c.bifa='deliberately false native labels';assert.ok(ids(c).includes(id),[day,upper,id,mode].join(' '));}
});

test('real 14:42 example excludes false ring and wrong-mode tiger, records void and chain endpoint',async()=>{
 const c=JSON.parse(await fs.readFile(new URL('current-example-1442/resolved-chart.json',base),'utf8')).facts;
 const r=scanBasicBifa(c);assert.equal(r.matches.filter(m=>!m.extended).length,7);
 assert.ok(!r.matches.some(r=>['BF02-return','BF91-tiger','BF61-tomb','BF22-vertical'].includes(r.id)));
 const chain=r.matches.find(r=>r.id==='BF31-chain');assert.equal(chain.direction,'初→中→末');assert.equal(chain.endpoint,'酉');assert.equal(chain.endpoint_to_day,'被生');assert.equal(chain.daquan_complete_chain,false);
 assert.equal(r.matches.find(r=>r.id==='BF69-plain-hidden').points.find(p=>p.tian==='卯').void_ground,true);
 assert.equal(r.matches.find(r=>r.id==='BF47-prison').branch,'贵人入狱');
 const night=scanBasicBifa(get('己丑','卯','夜贵'));assert.ok(night.matches.some(r=>r.id==='BF91-tiger'&&r.also_law61_tiger_on_stem));
 assert.notEqual(r.binding.geometry_sha256,night.binding.geometry_sha256);
});

test('1440 bound day/night geometries execute every registered rule and retain exact coordinates',()=>{
 const counts=Object.fromEntries(basicBifaCatalog().filter(r=>!r.extended).map(r=>[r.id,0])),geometries=new Set();
 for(const v of variants){
  const c=geometryChart(v),before=JSON.stringify(c),r=scanBasicBifa(c);assert.equal(JSON.stringify(c),before);
  assert.equal(r.coverage.all_registered_checked,true);assert.equal(r.coverage.registered_structures,134);assert.equal(r.binding.rules_sha256,BASIC_BIFA_RULES_SHA256);
  assert.equal(r.actual_mode,v.mode);geometries.add(r.binding.geometry_sha256);
  for(const m of r.matches){
   if(Object.hasOwn(counts,m.id))counts[m.id]++;assert.ok(m.checks.length>0&&m.checks.every(x=>x.met));
   for(const p of m.points){const native=c.heaven_earth.find(n=>n.tian===p.tian);assert.equal(p.di,native.di);assert.equal(p.tianjiang,native.tianjiang);}
   assert.ok(m.evidence_ids.every(id=>r.evidence.some(e=>e.id===id)));
  }
 }
 assert.equal(geometries.size,1440);for(const [id,n] of Object.entries(counts))assert.ok(n>0,id+' unreachable');
});

test('both terminal-to-day conditions and main/branch boundaries are preserved over all geometries',()=>{
 let notToDay=0,onlyGate=0,upperOnly=0,simpleTriple=0,prisonException=0,voidRelations=0;
 for(const v of variants){
  const c=geometryChart(v),r=scanBasicBifa(c),m=new Map(r.matches.map(m=>[m.id,m]));
  if(m.has('BF31-chain')&&!m.get('BF31-chain').daquan_complete_chain){notToDay++;assert.notEqual(m.get('BF31-chain').endpoint_to_day,'生');}
  if(c.heaven_earth.find(p=>p.tian==='戌').di==='亥'&&c.transmissions[0].diZhi!=='戌'){onlyGate++;assert.ok(!m.has('BF51-gate'));}
  if(m.has('BF22-upper')&&!m.has('BF22-main'))upperOnly++;
  if(m.has('BF27-drain')&&!m.has('BF83-call'))simpleTriple++;
  if(m.has('BF47-prison')&&(m.get('BF47-prison').exception_body||m.get('BF47-prison').exception_house)){prisonException++;assert.notEqual(m.get('BF47-prison').branch,'贵人入狱');}
  if(r.matches.some(m=>m.points.some(p=>p.void_self||p.void_ground)))voidRelations++;
 }
 for(const n of [notToDay,onlyGate,upperOnly,simpleTriple,prisonException,voidRelations])assert.ok(n>0);
});

test('missing mode or inconsistent coordinates stop handoff rather than emit plausible rules',()=>{
 const c=get('己丑','卯');assert.throws(()=>scanBasicBifa({...c,nobleman:{zhouye:'自动选择'}}),/actual noble mode/);
 const bad=structuredClone(c);bad.lessons[0].tianpan='子';assert.throws(()=>scanBasicBifa(bad),/lesson coordinates/);
 const badGeneral=structuredClone(c);badGeneral.transmissions[0].tianjiang='白虎';assert.throws(()=>scanBasicBifa(badGeneral),/generals mismatch/);
 assert.throws(()=>scanBasicBifa({...c,void_branches:['子','丑']}),/void\/day/);
});
