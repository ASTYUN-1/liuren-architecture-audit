import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { resolveShensha, factsForShensha, loadShenshaPolicy } from '../liuren-shensha.mjs';
import { runChart, ROOT } from '../liuren-direct.mjs';
import { runResolvedChart } from '../liuren-resolved-chart.mjs';
import { enrichChartResult } from '../liuren-shensha.mjs';
import { correctEngineShensha } from '../liuren-engine-shensha.mjs';

const active=JSON.parse(await fs.readFile(path.join(ROOT,'.opencode/liuren-active.json'),'utf8'));
const runtime=path.join(ROOT,active.runtime);
const policy=JSON.parse(await fs.readFile(path.join(runtime,'references/shensha-policy.json'),'utf8'));
const Z=[...'子丑寅卯辰巳午未申酉戌亥'], G=[...'甲乙丙丁戊己庚辛壬癸'];
const J=['贵人','腾蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后'];
function fixture(extra={}) {
  return {schema:'liuren-chart-facts-v1',year_pillar:'丙午',month_branch:'寅',day_pillar:'庚戌',
    nobleman:{rule:'甲戊庚牛羊',actual_zhouye:'昼贵',heaven_branch:'丑'},
    heaven_earth:Z.map((b,i)=>({tian:b,di:Z[(i+1)%12],tianjiang:J[i],shensha:[]})),...extra};
}
const result=f=>resolveShensha(f,policy);
const item=(f,id)=>result(f).items.find(r=>r.id===id);
const branches=(f,id)=>item(f,id).places?.map(p=>p.tian).join('');

test('32 core checks and six distinct additions, with executable sources and tables',()=>{
  const ids=new Set(policy.rules.map(r=>r.id));
  for(let n=1;n<=32;n++) assert.ok(ids.has('S'+String(n).padStart(2,'0')));
  assert.equal(ids.size,38); assert.equal(policy.disabled.length,22);
  for(const r of policy.rules) {
    assert.ok(r.sources.length);
    if(r.basis!=='opposite_nobleman') assert.equal(r.table.length,policy.indices[r.basis].length,r.id);
  }
});

test('庚日德禄申，原丑标签被比对而非沿用；坐标不互换，输入不变',()=>{
  const f=fixture(); f.heaven_earth[1].shensha=['日德','日禄','干德'];
  const before=JSON.stringify(f);
  assert.equal(branches(f,'S12'),'申');assert.equal(branches(f,'S13'),'申');
  const r=item(f,'S12');assert.deepEqual(r.engine_tian,['丑']);
  assert.equal(r.engine_check,'不同，采用重算');
  assert.deepEqual(r.places,[{tian:'申',di:'酉',jiang:'太常'}]);
  assert.equal(JSON.stringify(f),before);
});

test('ten stems: 德禄基表及阴干两刃区别，别名不重复建项',()=>{
  const de=[...'寅申巳亥巳寅申巳亥巳'],lu=[...'寅卯巳午巳午申酉亥子'];
  for(let i=0;i<10;i++) {
    const f=fixture({day_pillar:G[i]+Z[i]});
    assert.equal(branches(f,'S12'),de[i]);assert.equal(branches(f,'S13'),lu[i]);
    const a=branches(f,'S31'),b=branches(f,'S31Y');
    if(i%2===0) assert.equal(a,b);
    else {assert.equal(a,undefined);assert.equal(item(f,'S31').status,'disabled');}
    assert.equal(result(f).items.filter(r=>r.id==='S12').length,1);
  }
  assert.equal(item(fixture({day_pillar:'乙丑'}),'S31').status,'disabled');
  assert.equal(policy.rules.find(r=>r.id==='S31').table[1],'寅'); // 研究表不删除
  assert.equal(branches(fixture({day_pillar:'乙丑'}),'S31Y'),'辰');
});

test('午加丑：神煞属于天盘午，绝不移到丑；庚日申临丑也不误判日德禄在丑',()=>{
  const f=fixture();f.heaven_earth.forEach((row,i)=>{row.di=Z[(i+7)%12];});
  assert.deepEqual(item(f,'S01').places.map(p=>[p.tian,p.di]),[['午','丑']]);
  const corrected=correctEngineShensha(f,policy,result(f));
  assert.ok(corrected.facts.heaven_earth.find(p=>p.tian==='午').shensha.includes('太岁'));
  assert.ok(!corrected.facts.heaven_earth.find(p=>p.tian==='丑').shensha.includes('太岁'));
  f.heaven_earth.forEach((row,i)=>{row.di=Z[(i+5)%12];});
  assert.deepEqual(item(f,'S12').places.map(p=>[p.tian,p.di]),[['申','丑']]);
  assert.equal(item(f,'S12').places[0].tian,'申');
});

test('60日旬丁癸和旬仪实际是本旬的丁癸甲，矛盾旬名明确不采用',()=>{
  for(let n=0;n<60;n++) {
    const f=fixture({day_pillar:G[n%10]+Z[n%12]});
    const start=Math.floor(n/10)*10;
    assert.equal(branches(f,'S05'),Z[(start+3)%12]);
    assert.equal(branches(f,'S07'),Z[(start+9)%12]);
    assert.equal(branches(f,'S27'),Z[start%12]);
  }
  assert.equal(item(fixture({xun:'甲子'}),'S05').status,'invalid_input');
});

test('12月按月建节月，医神成对，生死气冲，死神明取巳顺',()=>{
  for(let m=0;m<12;m++) {
    const f=fixture({month_branch:Z[(m+2)%12],lunar:{month:99},month_general:'子'});
    assert.equal(branches(f,'S17'),Z[(m+4)%12]);
    assert.equal(branches(f,'S18'),Z[(m+10)%12]);
    assert.equal(branches(f,'S10'),Z[m]);
    assert.equal(branches(f,'S21'),Z[(m+6)%12]);
    assert.equal(branches(f,'S21S'),Z[(m+5)%12]);
  }
  assert.equal(branches(fixture({month_branch:'未'}),'S17'),'酉');
  assert.equal(branches(fixture({month_branch:'未'}),'S18'),'卯');
  assert.equal(branches(fixture({month_branch:'巳'}),'S22'),'申');
  assert.equal(branches(fixture({month_branch:'巳'}),'S23'),'辰');
});

test('12岁丧吊病符与原同表标签分离；死符固定岁干表',()=>{
  for(let y=0;y<12;y++) {
    const f=fixture({year_pillar:G[y%10]+Z[y]});
    assert.equal(branches(f,'S19'),Z[(y+11)%12]);
    assert.equal(branches(f,'S32'),Z[(y+2)%12]);
    assert.equal(branches(f,'S32D'),Z[(y+10)%12]);
  }
  const f=fixture();f.heaven_earth[8].shensha=['丧门','吊客'];
  assert.equal(branches(f,'S32'),'申');assert.equal(branches(f,'S32D'),'辰');
  assert.equal(item(f,'S32D').engine_check,'不同，采用重算');
  assert.equal(branches(f,'S20'),'亥'); // 丙年，指南岁干死符；不是午顺五亥以外的临时择法。
  assert.equal(branches(fixture({year_pillar:'甲午'}),'S20'),'申');
});

test('帘幕沿已核昼夜和两套贵人设置；未知起例不猜',()=>{
  assert.equal(branches(fixture(),'S02'),'未');
  assert.equal(branches(fixture({nobleman:{rule:'甲戊庚牛羊',actual_zhouye:'夜贵',heaven_branch:'未'}}),'S02'),'丑');
  assert.equal(branches(fixture({day_pillar:'乙丑',nobleman:{rule:'甲羊戊庚牛',actual_zhouye:'昼贵',heaven_branch:'申'}}),'S02'),'子');
  assert.equal(item(fixture({nobleman:{}}),'S02').status,'missing_input');
  assert.equal(item(fixture({nobleman:{rule:'未知',actual_zhouye:'昼贵'}}),'S02').status,'invalid_input');
});

test('缺月只停月季项目，缺岁只停岁煞；参数矛盾不包装成背景',()=>{
  const f=fixture({month_branch:null,year_pillar:null});
  assert.equal(item(f,'S17').status,'missing_input');assert.equal(item(f,'S32').status,'missing_input');
  assert.equal(item(f,'S12').status,'resolved');
  const conflict=fixture({day_stem:'甲'});
  assert.equal(item(conflict,'S12').status,'invalid_input');assert.equal(item(conflict,'S05').status,'invalid_input');
  assert.equal(item(conflict,'S32').status,'resolved');
  const duplicate=fixture();duplicate.heaven_earth[1].tian='子';
  assert.equal(item(duplicate,'S12').status,'invalid_input');
  assert.ok(!('places' in item(duplicate,'S12')));
});

test('未核名停用，不按字面出背景或伤情结论；空亡不自动推断伤轻',()=>{
  const f=fixture({void_branches:['申','酉']});
  f.heaven_earth[0].shensha=['干胎神','从未登记的煞'];
  const r=result(f);
  assert.ok(r.disabled_names.includes('干胎神'));assert.ok(r.unregistered_names.includes('从未登记的煞'));
  assert.equal(item(f,'S31').status,'resolved');
  assert.ok(!Object.hasOwn(r,'prediction'));assert.ok(!Object.hasOwn(item(f,'S31'),'auspicious'));
});

test('旧盘原档/facts两种输入可复用；报告文本和验证失败盘不采用',()=>{
  const f=fixture();assert.deepEqual(factsForShensha({_direct:{facts:f}}),f);
  assert.deepEqual(factsForShensha({facts:f}),f);
  assert.throws(()=>factsForShensha({report:'庚日德禄丑'}));
  assert.throws(()=>factsForShensha({facts:f,validation:{ok:false}}));
});

test('活动表身份校验，真实引擎样本与归档采用层一致，保留原标签',async()=>{
  const loaded=await loadShenshaPolicy();assert.equal(loaded.policy.release,policy.release);
  const chart=await runResolvedChart({datetime:'2026-08-04T14:32'},{persist:false});
  const r=chart.shensha_resolution;
  assert.ok(chart.validation.ok);assert.equal(r.policy_sha256,loaded.sha256);
  const byId=id=>r.items.find(i=>i.id===id);
  assert.equal(byId('S12').places[0].tian,'申');assert.equal(byId('S12').engine_check,'一致');
  assert.equal(byId('S19').places[0].tian,'巳');assert.equal(byId('S19').engine_check,'一致');
  assert.equal(byId('S32D').places[0].tian,'辰');assert.equal(byId('S17').places[0].tian,'酉');
  assert.ok(chart.facts.heaven_earth.find(p=>p.tian==='巳').shensha.includes('病符'));
  assert.ok(!chart.facts.heaven_earth.find(p=>p.tian==='未').shensha.includes('病符'));
  const dir=path.join(ROOT,'tmp/liuren-materials/shensha-test-'+Date.now());
  await fs.mkdir(dir,{recursive:true});const archive=path.join(dir,'旧盘.json');
  await fs.writeFile(archive,JSON.stringify({_direct:{facts:chart.facts,validation:chart.validation}}));
  const request={action:'shensha',path:archive};
  const child=spawnSync('python',['-X','utf8','tools/liuren-materials.py','--request',JSON.stringify(request)],{cwd:ROOT,encoding:'utf8',windowsHide:true});
  assert.equal(child.status,0,child.stderr);assert.deepEqual(JSON.parse(child.stdout),r);
  const denied=spawnSync('python',['-X','utf8','tools/liuren-materials.py','--request',JSON.stringify({action:'shensha',path:'opencode.json'})],{cwd:ROOT,encoding:'utf8',windowsHide:true});
  assert.equal(denied.status,2);assert.match(denied.stderr,/仅复用/);
});

test('新增采用层独立保存，原档字节不改；节气边界仍留原档但神煞明确停用',async()=>{
  const archiveRoot=path.join(ROOT,'tmp/liuren-materials/shensha-sidecar-'+Date.now());
  const original=await runChart({datetime:'2026-08-04T14:32'},{archiveRoot});
  const before=await fs.readFile(original.archive.path);
  const chart=await enrichChartResult(original);
  assert.deepEqual(await fs.readFile(original.archive.path),before);
  const sidecar=JSON.parse(await fs.readFile(chart.shensha_archive.path,'utf8'));
  assert.equal(sidecar.source_archive.sha256,original.archive.sha256);
  assert.deepEqual(sidecar.shensha_resolution,chart.shensha_resolution);
  assert.notEqual(chart.archive.path,original.archive.path);
  const corrected=JSON.parse(await fs.readFile(chart.archive.path,'utf8'));
  assert.deepEqual(corrected.tiandipan.map(r=>r.shensha),chart.facts.heaven_earth.map(r=>r.shensha));
  assert.equal(corrected._direct.engine.algorithm_modified,true);
  for(const key of Object.keys(JSON.parse(before)))if(!['_direct','tiandipan','keyShensha'].includes(key))
    assert.deepEqual(corrected[key],JSON.parse(before)[key],key);
  assert.equal(chart.engine_corrections.find(r=>r.id==='S32D').corrected_heaven_branches[0],'辰');
  const bad=await runResolvedChart({datetime:'2026-07-23T03:13'},{archiveRoot});
  assert.equal(bad.ok,false);assert.ok(bad.archive.path);
  assert.equal(bad.shensha_resolution.status,'chart_unusable');
  assert.deepEqual(bad.shensha_resolution.items,[]);
});

test('来源按LF字节行可回查，旧引用与新增方向证据哈希和原文相符',async()=>{
  const source=JSON.parse(await fs.readFile(path.join(runtime,'references/shensha-source-map.json'),'utf8'));
  const ev=JSON.parse(await fs.readFile(path.join(runtime,'references/shensha-policy-evidence.json'),'utf8'));
  const authority=JSON.parse(await fs.readFile(path.join(runtime,'references/shensha-authority-evidence.json'),'utf8'));
  const all=[ev['SP-01'],...ev.additional,...Object.values(authority.evidence)];
  const h=await import('node:crypto');
  for(const r of all) {
    const b=await fs.readFile(path.join(ROOT,r.path));assert.equal(h.createHash('sha256').update(b).digest('hex'),r.sha256);
    const quote=b.toString('utf8').replace(/^\uFEFF/,'').split('\n').slice(r.line_start-1,r.line_end).map(s=>s.replace(/\r+$/,'')).join('\n');
    assert.equal(quote,r.quote);
  }
  for(const rule of policy.rules) for(const id of rule.sources) assert.ok(authority.evidence[id] || source.cards[id] || ev[id] || ev.local_convention[id],id);
});

test('阴干阳刃停用会清除旧标签，原表及十干羊刃保留，其他项目继续采用',()=>{
  for (const [stem,branch] of [['乙','丑'],['丁','卯'],['己','巳'],['辛','未'],['癸','酉']]) {
    const f=fixture({day_pillar:stem+branch});
    f.heaven_earth[0].shensha=['阳刃','羊刃'];
    const resolution=result(f),corrected=correctEngineShensha(f,policy,resolution);
    assert.equal(item(f,'S31').status,'disabled');
    assert.ok(!('places' in item(f,'S31')));
    assert.ok(corrected.facts.heaven_earth.every(p=>!p.shensha.includes('阳刃')));
    assert.equal(corrected.facts.heaven_earth.filter(p=>p.shensha.includes('羊刃')).length,1);
    assert.equal(item(f,'S12').status,'resolved');
    assert.ok(f.heaven_earth[0].shensha.includes('阳刃')); // 输入及原档不改
  }
});

test('古籍羊刃十干表及38项复核身份完整，古籍来源与研究旧源分开',async()=>{
  assert.deepEqual(policy.rules.find(r=>r.id==='S31Y').table,[...'卯辰午未午未酉戌子丑']);
  const ev=JSON.parse(await fs.readFile(path.join(runtime,policy.authority_sources),'utf8'));
  assert.equal(ev.reviews.length,38);
  assert.equal(ev.reviews.filter(r=>r.status==='source_checked').length,35);
  assert.equal(ev.reviews.filter(r=>r.status==='derived_from_cycle').length,2);
  assert.equal(ev.reviews.filter(r=>r.status==='partial_source_checked').length,1);
  for(const r of policy.rules)for(const id of r.sources)assert.ok(ev.evidence[id],r.id+': '+id);
});
