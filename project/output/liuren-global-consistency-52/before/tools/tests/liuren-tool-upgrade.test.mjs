import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {calendar} from '../liuren-deterministic-calendar.mjs';
import {compute,requestNeedsChart} from '../liuren-deterministic-io.mjs';
import {methodCatalog,methodQuantity,methodImagery} from '../liuren-method-tools.mjs';
import {calculateSelectedStrength} from '../liuren-palace-strength.mjs';
import {buildFacts,hash,ZHI} from '../liuren-deterministic.mjs';
const c=JSON.parse(await fs.readFile(new URL('../../output/liuren-energy-yin-20261106-1443/chart-result.json',import.meta.url),'utf8')).facts;
const dateQuery={start:'2026-11-06',end:'2026-11-18',timezone:'Asia/Shanghai',day_boundary:'civil-midnight'};
const use='T:'+c.transmissions[0].diZhi;
function month(b){const x=structuredClone(c);x.month_branch=b;x.pillars[1]=(ZHI.indexOf(b)%2?'乙':'甲')+b;return x;}
const q=(id,extra={})=>({id,target:use,basis:'合成方法测试，非实际数量预测',...extra});
test('method catalogs separate complete branches, base steps and source editions',()=>{
 const d=methodCatalog({kind:'quantity'});assert.deepEqual(d.methods.map(x=>x.id).sort(),
  ['CY501-use-ground','WY67-shenjiang-base','WY244-month','WY242-generated-base','LF3329-class-ground'].sort());
 assert.equal(methodCatalog({kind:'imagery'}).methods.length,3);
 assert.equal(d.methods.filter(x=>x.precision==='base-only').length,2);
 assert.ok(d.methods.every(x=>x.source.sha256.length===64&&x.source.line_mode===(x.id==='LF3329-class-ground'?'universal':'lf')));
 assert.throws(()=>methodCatalog({kind:'quantity',id:'invented'}),/unknown/);
});
test('civil-midnight and zi-hour derive hour stems from the same explicit day convention',()=>{
 const a=calendar({...dateQuery,start:'2026-11-08',end:'2026-11-08',hour:23,minute:30}).rows[0];
 const b=calendar({...dateQuery,start:'2026-11-08',end:'2026-11-08',hour:23,minute:30,day_boundary:'zi-hour'}).rows[0];
 assert.equal(a.day,'丙戌');assert.equal(a.hour,'戊子');assert.equal(b.day,'丁亥');assert.equal(b.hour,'庚子');
});
test('exact solar-term and month boundaries, xun boundaries and branch relationship filters',()=>{
 const r=calendar({...dateQuery,mode:'boundaries'}).rows;
 const ld=r.find(x=>x.name==='立冬');assert.equal(ld.datetime,'2026-11-07T17:52:05');assert.ok(ld.types.includes('节月'));assert.equal(ld.month,'己亥');
 assert.ok(r.some(x=>x.datetime==='2026-11-16T00:00:00'&&x.types.includes('旬界')));
 const hits=calendar({...dateQuery,match:{target:'子',relation:'冲'}}).rows;
 assert.ok(hits.length);assert.ok(hits.every(x=>x.day[1]==='午'));
 assert.ok(calendar({...dateQuery,match:{target:'子',relation:'六合'}}).rows.every(x=>x.day[1]==='丑'));
});
test('original xun is one dated interval, not every future repetition of its name',()=>{
 const a=calendar({...dateQuery,origin:'2026-11-06'}).rows;
 assert.equal(a.find(x=>x.date==='2026-11-15').in_origin_xun,true);
 assert.equal(a.find(x=>x.date==='2026-11-16').in_origin_xun,false);
 const b=calendar({...dateQuery,start:'2027-01-05',end:'2027-01-05',origin:'2026-11-06'}).rows[0];
 assert.equal(b.xun,'甲申');assert.equal(b.in_origin_xun,false);
 const z=calendar({...dateQuery,start:'2026-11-15',end:'2026-11-15',hour:23,day_boundary:'zi-hour',origin:'2026-11-06'}).rows[0];
 assert.equal(z.in_origin_xun,false);
 const origin23=calendar({...dateQuery,start:'2026-11-15',end:'2026-11-15',hour:23,day_boundary:'zi-hour',origin:'2026-11-15T23:30'});
 assert.equal(origin23.origin.day,'甲午');assert.equal(origin23.rows[0].in_origin_xun,true);
});
test('bounded intraday sampling and unknown or inapplicable parameters fail explicitly',()=>{
 assert.equal(calendar({...dateQuery,end:dateQuery.start,sample_minutes:120}).rows.length,12);
 assert.throws(()=>calendar({...dateQuery,sample_minutes:1}),/10000/);
 assert.throws(()=>calendar({...dateQuery,sample_minutes:120,hour:12}),/mixed/);
 assert.throws(()=>calendar({...dateQuery,mode:'boundaries',branches:['子']}),/filters/);
 assert.throws(()=>calendar({...dateQuery,origin_state:'outside'}),/origin/);
});
test('CY501 applies distinct five-qi arithmetic and keeps the source scale ambiguity',()=>{
 assert.equal(use,'T:戌');
 const options={season_profile:'four-seasons'};
 assert.equal(methodQuantity(month('巳'),q('CY501-use-ground',options)).value,70); // 相
 assert.equal(methodQuantity(month('申'),q('CY501-use-ground',options)).value,12); // 休
 assert.equal(methodQuantity(month('亥'),q('CY501-use-ground',options)).value,6); // 囚
 assert.equal(methodQuantity(month('寅'),q('CY501-use-ground',options)).value,6); // 死
 const wang=methodQuantity(month('戌'),q('CY501-use-ground',{season_profile:'quarter-earth'}));
 assert.equal(wang.value,null);assert.deepEqual(wang.candidates,[350,3500]);
 assert.throws(()=>methodQuantity(c,q('CY501-use-ground',{...options,target:'T:子'})),/initial transmission|transmissions/);
});
test('month identity correction is independent of generic strength; named general table stays local',()=>{
 assert.equal(methodQuantity(month('戌'),q('WY244-month',{number_table:'branch'})).value,10);
 assert.equal(methodQuantity(month('辰'),q('WY244-month',{number_table:'branch'})).value,2.5);
 assert.equal(methodQuantity(month('寅'),q('WY244-month',{number_table:'branch'})).value,5);
 const a=methodQuantity(c,q('WY67-shenjiang-base'));
 assert.equal(a.value,5*a.facts.general_number);assert.equal(a.stage,'base-only');
 const outside=methodQuantity(c,q('WY67-shenjiang-base',{target:'T:子'}));
 assert.equal(outside.value,9*outside.facts.general_number); // Selected class need not be transmitted in this base formula.
 assert.equal(methodQuantity(month('巳'),q('WY242-generated-base',{season_profile:'four-seasons'})).value,10);
 assert.equal(methodQuantity(month('寅'),q('WY242-generated-base',{season_profile:'four-seasons'})).value,5);
 assert.throws(()=>methodQuantity(c,{...q('WY244-month',{number_table:'branch'}),factor:20}),/unknown/);
 assert.throws(()=>methodQuantity(c,q('WY67-shenjiang-base',{season_profile:'four-seasons'})),/seasonal/);
});
test('imagery matches source conditions and named growth, never interprets weak score as failure',()=>{
 const a=methodImagery(month('寅'),q('MG104-material',{season_profile:'four-seasons'}));assert.equal(a.matches[0].candidate,'灰尘');
 const b=methodImagery(c,q('DF449-growth',{reference:'ground'}));assert.equal(b.facts.growth,buildFacts(c).nodes.find(x=>x.symbol==='戌').growth.ground);
 const v=methodImagery(c,{id:'DF75-void',target:'T:寅',basis:'只验证本支不空且坐午空的区别'});
 assert.equal(v.facts.self_void,false);assert.equal(v.facts.sitting_void,true);assert.deepEqual(v.matches,[]);
 assert.throws(()=>methodImagery(c,q('DF449-growth',{reference:'ground',season_profile:'four-seasons'})),/not seasonal/);
});
const strength={mode:'selected_relations',season_profile:'quarter-earth',season_basis:'固定采用季土表，不比较选高值',
 actors:[{id:'T:酉',role:'测试施助',basis:'合成接口'},{id:'T:子',role:'测试目标',basis:'合成接口'}],links:[{source:'T:酉',target:'T:子',basis:'测试已选金生水通路'}]};
test('calendar-to-strength evaluation preserves original chart and returns same-state parity',()=>{
 const before=hash(c),direct=calculateSelectedStrength(c,strength);
 const r=compute({action:'evaluation',evaluation:{calendar:{...dateQuery,end:dateQuery.start,hour:14,minute:43},strength}} ,c);
 assert.equal(hash(c),before);assert.equal(r.void_policy,'original');assert.deepEqual(r.rows[0].actors,direct.actors);
 const across=compute({action:'evaluation',evaluation:{calendar:{...dateQuery,start:'2026-11-07',end:'2026-11-07',mode:'boundaries',boundary_types:['节月']},strength}},c);
 assert.equal(across.rows[0].month,'己亥');assert.ok(across.rows[0].actors.every(x=>Number.isFinite(x.adjusted)));
 const changed=compute({action:'evaluation',evaluation:{calendar:{...dateQuery,start:'2026-11-16',end:'2026-11-16'},strength,void_policy:'evaluation-xun-research'}},c);
 assert.equal(changed.void_policy,'evaluation-xun-research');assert.deepEqual(changed.rows[0].evaluation_void,['辰','巳']);
 assert.throws(()=>compute({action:'evaluation',evaluation:{calendar:{...dateQuery,end:'2027-11-06'},strength}},c),/128/);
});
test('dispatch requires chart only for chart-bound calculations and refuses mixed quantity requests',()=>{
 assert.equal(requestNeedsChart({action:'methods'}),false);assert.equal(requestNeedsChart({action:'quantity',quantity_method:q('WY67-shenjiang-base')}),true);
 assert.deepEqual(compute({action:'quantity',quantity_method:q('WY67-shenjiang-base')},c),methodQuantity(c,q('WY67-shenjiang-base')));
 assert.throws(()=>compute({action:'quantity',expression:{value:3},quantity_method:q('WY67-shenjiang-base')},c),/not both/);
});
