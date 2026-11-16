import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {createHash} from 'node:crypto';
import {packet,result} from './fixtures/liuren-adjudication-v2.mjs';
import {runResolvedChart} from '../liuren-resolved-chart.mjs';
import {store} from '../liuren-flow-control.mjs';
import {loadPacket,digest} from '../liuren-adjudication-files.mjs';
import {readBoundReference} from '../liuren-core-handoff.mjs';
import {checkSubmission} from '../liuren-adjudication-output.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
registerHooks({resolve(specifier,context,next){if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);return next(specifier,context);}});
const {default:plugin}=await import('../../.opencode/plugins/liuren-adjudication.ts');
const hash=s=>createHash('sha256').update(s).digest('hex');
const active=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
const manifest=JSON.parse(await fs.readFile(path.join(root,active.runtime,'manifest.json'),'utf8'));
const chart=await runResolvedChart({datetime:'2026-10-18T13:22'},{persist:false});
async function harness(t,{missing=[],text='姐姐的女儿参加转校考试，能否转入？',eventPolicy=false}={}){
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-flow-test-'));
 t.after(async()=>{assert.equal(path.dirname(path.resolve(folder)),path.resolve(os.tmpdir()));assert.ok(path.basename(folder).startsWith('liuren-flow-test-'));await fs.rm(folder,{recursive:true,force:true});});
 const pointer={...active,compactHandoff:{enabled:true},flowControl:{enabled:true},eventPositioning:{enabled:eventPolicy}};
 for(const rel of ['tools/liuren-direct/legacy-engine-manifest.json','排盘工具魔改/js/lunar.js',active.runtime+'/manifest.json',active.runtime+'/references/shensha-policy.json',active.runtime+'/references/adjudicator-book-evidence.json',active.runtime+'/methods/positioning.md',active.runtime+'/domains/finance.md',active.runtime+'/domains/exam.md',active.runtime+'/domains/illness.md',active.runtime+'/methods/timing.md',active.runtime+'/methods/quantity.md',active.runtime+'/references/quantity-sources.md']){const dst=path.join(folder,rel);await fs.mkdir(path.dirname(dst),{recursive:true});await fs.copyFile(path.join(root,rel),dst);}
 await fs.cp(path.join(root,active.runtime),path.join(folder,active.runtime),{recursive:true});
 await fs.mkdir(path.join(folder,'.opencode'),{recursive:true});await fs.writeFile(path.join(folder,'.opencode/liuren-active.json'),JSON.stringify(pointer));
 const methodParts=[];
 for(const id of [...manifest.required,'finance','exam','illness'].filter(id=>!missing.includes(id))){
  const body=(await fs.readFile(path.join(root,active.runtime,manifest.modules[id].file),'utf8')).replaceAll('\r\n','\n');
  const meta={module:id,release:active.release,fileSha256:manifest.files[manifest.modules[id].file],textSha256:hash(body)};
  methodParts.push({type:'tool',tool:'liuren_materials',state:{status:'completed',output:'LIUREN_METHOD_BEGIN '+JSON.stringify(meta)+'\n'+body+'\nLIUREN_METHOD_END '+JSON.stringify({module:id,textSha256:hash(body)})}});
 }
 const childParts=[],childInfo={role:'assistant',id:'msg_initial'},continuations=[],client={session:{get:async()=>({data:{parentID:'parent'}}),messages:async({path:{id}})=>({data:id==='parent'?[{info:{role:'user'},parts:[{type:'text',text}]},{info:{role:'assistant'},parts:methodParts}]:[{info:{role:'user'},parts:[{type:'text',text:saved?.task_prompt}]},{info:childInfo,parts:childParts},...continuations]})}};
 let hooks=await plugin({directory:folder,client}),saved;
 const input=()=>{const p=packet();p.chart={source:'synthetic live engine test',facts:structuredClone(chart.facts)};p.entities[0].branch='丑';delete p.entities[0].position;p.questions[0].task_basis=[{task:'outcome',origin:'user_requested',request_quote:'能否转入',reason:'原问成败'}];return p;};
 const output=()=>{const r=result();r.entity_checks[0].branch='丑';for(const k of ['position','five_qi','twelve_states','site_yin','shenjiang'])delete r.entity_checks[0][k];r.special_methods=[];r.calculations=[];r.relation_checks[0].application={object:'合成',mechanism:'合成',stage:'合成',goal_effect:'合成',alternative_resolution:'合成'};return r;};
 const save=async(p=input())=>saved=JSON.parse(await hooks.tool.liuren_adjudication_packet.execute({packet:hooks.tool.liuren_adjudication_packet.args.packet.parse(p)},{agent:'liuren',sessionID:'parent'}));
 const event={tool:'task',sessionID:'parent',callID:'first'};
 const start=()=>hooks['tool.execute.before'](event,{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}});
 const read=async()=>{let pages=1;for(let page=1;page<=pages;page++){const a={file_path:saved.file_path,sha256:saved.sha256,page};const raw=await hooks.tool.liuren_adjudication_read.execute(a,{agent:'liuren-adjudicator',sessionID:'child'});pages=JSON.parse(raw).pages;childParts.push({type:'tool',tool:'liuren_adjudication_read',state:{status:'completed',input:a,output:raw}});}return pages;};
 const submit=async(r=output())=>JSON.parse(await hooks.tool.liuren_adjudication_submit.execute({result:hooks.tool.liuren_adjudication_submit.args.result.parse(r)},{agent:'liuren-adjudicator',sessionID:'child'}));
 const finish=async(r)=>{const o={output:JSON.stringify(r),metadata:{sessionId:'child'}};await hooks['tool.execute.after'](event,o);return o;};
 const get=async(action='read')=>JSON.parse(await hooks.tool.liuren_adjudication_result.execute({action,task_id:'child'},{agent:'liuren',sessionID:'parent'}));
 const acknowledge=async()=>{const event={tool:'task_result',sessionID:'parent',callID:'ack'};await hooks['tool.execute.before'](event,{args:{task_id:'child'}});const out={output:'Existing task result',metadata:{}};await hooks['tool.execute.after'](event,out);return JSON.parse(out.output);};
 const restart=async()=>{hooks=await plugin({directory:folder,client});};
 return {get hooks(){return hooks;},folder,input,output,save,start,read,submit,finish,get,restart,event,childParts,childInfo,continuations,acknowledge,client,get saved(){return saved;}};
}

async function referenceFixture(h){
 const content='UNIQUE_REFERENCE_BODY\n'+'连续原书测试段。'.repeat(1600)+'\n段尾条件完整保留。';
 const rel='references/test-reference.md',m=structuredClone(manifest);
 m.modules['test-reference']={file:rel,required:false};m.files[rel]=hash(content);
 const ascii=v=>JSON.stringify(v).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
 m.version=hash('{'+Object.keys(m.files).sort().map(k=>ascii(k)+': '+ascii(m.files[k])).join(', ')+'}');
 const pointerPath=path.join(h.folder,'.opencode/liuren-active.json'),pointer=JSON.parse(await fs.readFile(pointerPath,'utf8'));
 pointer.methodVersion=m.version;await fs.writeFile(pointerPath,JSON.stringify(pointer));
 await fs.writeFile(path.join(h.folder,active.runtime,rel),content);
 await fs.writeFile(path.join(h.folder,active.runtime,'manifest.json'),JSON.stringify(m));
 const p=h.input();p.method_modules=['test-reference'];return {p,content};
}
async function refRead(h,extra){
 const args={file_path:h.saved.file_path,sha256:h.saved.sha256,page:1,...extra};
 const raw=await h.hooks.tool.liuren_adjudication_read.execute(args,{agent:'liuren-adjudicator',sessionID:'child'});
 const output=typeof raw==='string'?raw:raw.output;
 h.childParts.push({type:'tool',tool:'liuren_adjudication_read',state:{status:'completed',input:args,output}});
 return JSON.parse(output);
}

test('core keeps the complete chart, every node and adopted shensha without embedding reference body',async t=>{
 const h=await harness(t),r=await referenceFixture(h);await h.save(r.p);
 const main=JSON.parse(await fs.readFile(h.saved.file_path,'utf8'));
 assert.ok(main.packet_archive);assert.equal(main.packet,undefined);
 const loaded=await loadPacket(h.folder,h.saved),core=JSON.parse(loaded.raw),p=loaded.envelope.packet;
 assert.equal(loaded.readView,'core');assert.deepEqual(core.chart,chart.facts);
 assert.equal(core.program.nodes.rows.length,12);assert.equal(core.program.stems.rows.length,10);
 for(const name of ['nodes','stems'])for(let i=0;i<p.deterministic[name].length;i++){
  const row=Object.fromEntries(core.program[name].columns.map((k,j)=>[k,core.program[name].rows[i][j]]));
  for(const k of ['id','symbol','element'])assert.deepEqual(row[k],p.deterministic[name][i][k]);
 }
 const table=core.program.shensha.table;
 const restored=table.rows.map(row=>Object.fromEntries(table.columns.map((k,i)=>[k,row[i]])));
 for(let i=0;i<restored.length;i++){
  const original=p.deterministic.adopted_shensha.items[i];
  assert.equal(restored[i].status,original.status);
  assert.deepEqual(restored[i].places,original.places?.map(r=>[r.tian,r.di,r.jiang])??null);
 }
 assert.ok(!loaded.raw.includes('UNIQUE_REFERENCE_BODY'));
 assert.ok(core.references.materials.some(m=>m.id==='M_test-reference'));
 assert.equal(p.method_materials.find(m=>m.id==='M_test-reference').quote,r.content);
});

test('core alone submits, survives restart, and delivers the exact free report',async t=>{
 const h=await harness(t),r=await referenceFixture(h);await h.save(r.p);await h.start();await h.read();
 const report='# 正式报告\n\n仅为合成工程测试，保留正文与限制。';
 const submitted=await h.submit(report);assert.equal(submitted.status,'completed');
 await h.finish(submitted);await h.restart();await h.acknowledge();
 assert.equal((await h.get('deliver')).report_markdown,report);
 assert.ok(h.childParts.every(p=>JSON.parse(p.state.output).view==='core'));
});

test('reference pages never satisfy the mandatory core gate',async t=>{
 const h=await harness(t),r=await referenceFixture(h);await h.save(r.p);await h.start();
 const page=await refRead(h,{material_id:'M_test-reference',page_count:4});
 assert.equal(page.required_for_submit,false);assert.equal(page.view,'reference');assert.equal(page.content,r.content);
 await assert.rejects(()=>h.submit('未读核心'),/READ|PAGE/);
 await h.read();assert.equal((await h.submit('已读核心')).status,'completed');
});

test('bound sources paginate faithfully and module and fixed evidence lookups work',async t=>{
 const h=await harness(t),r=await referenceFixture(h);await h.save(r.p);await h.start();
 let page=await refRead(h,{material_id:'M_test-reference'}),text=page.content;
 assert.equal(page.next_call.arguments.material_id,'M_test-reference');
 while(page.next_call){page=await refRead(h,page.next_call.arguments);text+=page.content;}
 assert.equal(text,r.content);assert.equal(page.reference_sha256,hash(r.content));
 assert.equal((await refRead(h,{module:'test-reference',page_count:4})).content,r.content);
 const e=await refRead(h,{material_id:'E01',page_count:4});assert.ok(e.content.length>100);assert.ok(e.source_sha256);
 await assert.rejects(()=>refRead(h,{material_id:'not-registered'}),/unknown material_id/);
 await assert.rejects(()=>refRead(h,{module:'../../outside'}),/unknown module/);
 await assert.rejects(()=>refRead(h,{module:'void',material_id:'E01'}),/exactly one/);
 await assert.rejects(()=>refRead(h,{sha256:'0'.repeat(64),material_id:'E01'}),/UNAUTHORIZED/);
});

test('tampered or truncated core tool output cannot submit',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();
 const original=h.childParts[0].state.output,out=JSON.parse(original);out.content=out.content.slice(0,-1);
 h.childParts[0].state.output=JSON.stringify(out);
 await assert.rejects(()=>h.submit('不完整'),/READ|PAGE/);
 h.childParts[0].state.output=original;assert.equal((await h.submit('完整')).status,'completed');
});

test('main and archive tampering is rejected by their bound hashes',async t=>{
 const h=await harness(t);await h.save();
 const original=await fs.readFile(h.saved.file_path,'utf8'),main=JSON.parse(original);
 await fs.writeFile(h.saved.file_path,original+' ');
 await assert.rejects(()=>loadPacket(h.folder,h.saved),/changed/);
 await fs.writeFile(h.saved.file_path,original);
 const archive=path.join(path.dirname(h.saved.file_path),main.packet_archive.file);
 await fs.appendFile(archive,' ');await assert.rejects(()=>loadPacket(h.folder,h.saved),/archive changed/);
});

test('core hash, archive owner and archive path are independently validated',async t=>{
 const h=await harness(t);await h.save();const main=JSON.parse(await fs.readFile(h.saved.file_path,'utf8'));
 const write=async m=>{const raw=JSON.stringify(m);await fs.writeFile(h.saved.file_path,raw);return {...h.saved,sha256:digest(raw)};};
 const broken=structuredClone(main);broken.reading_core.content+='x';
 await assert.rejects(async()=>loadPacket(h.folder,await write(broken)),/core hash/);
 const traversal=structuredClone(main);traversal.packet_archive.file='../outside.archive.json';
 await assert.rejects(async()=>loadPacket(h.folder,await write(traversal)),/archive reference/);
 const archive=path.join(path.dirname(h.saved.file_path),main.packet_archive.file),full=JSON.parse(await fs.readFile(archive,'utf8'));
 full.parent_session_id='another';const raw=JSON.stringify(full);await fs.writeFile(archive,raw);main.packet_archive.sha256=digest(raw);
 await assert.rejects(async()=>loadPacket(h.folder,await write(main)),/owner mismatch/);
});

test('bound method hash cannot drift, while archived source text remains available',async t=>{
 const h=await harness(t),r=await referenceFixture(h);await h.save(r.p);await h.start();
 await fs.appendFile(path.join(h.folder,active.runtime,'references/test-reference.md'),'changed');
 await assert.rejects(()=>refRead(h,{module:'test-reference'}),/hash changed/);
 assert.equal((await refRead(h,{material_id:'M_test-reference',page_count:4})).content,r.content);
});

test('identical module and explicit handoff share one source without a model retry',async t=>{
 const h=await harness(t),p=h.input(),file=manifest.modules.finance.file;
 p.method_modules=['finance'];p.method_materials=[{id:'M_finance',title:'explicit handoff title retained',source_path:active.runtime+'/'+file,sha256:manifest.files[file]}];
 await h.save(p);const loaded=await loadPacket(h.folder,h.saved),materials=loaded.envelope.packet.method_materials;
 assert.equal(materials.filter(m=>m.id==='M_finance').length,1);
 assert.equal(materials.find(m=>m.id==='M_finance').title,'explicit handoff title retained');
});

test('same ID with a different verified source is still rejected instead of overwritten',async t=>{
 const h=await harness(t),p=h.input(),file=manifest.modules.exam.file;
 p.method_modules=['finance'];p.method_materials=[{id:'M_finance',title:'different source',source_path:active.runtime+'/'+file,sha256:manifest.files[file]}];
 await assert.rejects(()=>h.save(p),/same ID must identify the identical source/);
});

