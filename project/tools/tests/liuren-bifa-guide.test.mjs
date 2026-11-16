import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {readBoundReference} from '../liuren-core-handoff.mjs';
import {bifaView} from '../liuren-bifa-view.mjs';
import {geometryChart} from '../liuren-bifa-batch.mjs';

const root=fileURLToPath(new URL('../../',import.meta.url));
const readJSON=async file=>JSON.parse(await fs.readFile(file,'utf8'));
const hash=raw=>createHash('sha256').update(raw).digest('hex');
const active=await readJSON(path.join(root,'.opencode/liuren-active.json'));
const manifest=await readJSON(path.join(root,active.runtime,'manifest.json'));
const rel=manifest.modules['bifa-guide'].file;
const guide=await readJSON(path.join(root,active.runtime,rel));
const evidence=await readJSON(path.join(root,'tools/liuren-bifa-basic-rules.json'));
const loaded=(rows=[])=>({envelope:{packet:{method_materials:[]}},referenceRegistry:{
 runtime:active.runtime,bifaGuide:{file:rel,sha256:manifest.files[rel]},bifaMatchedView:rows,
 bifaEvidence:{file:'references/bifa-basic-evidence.json',sha256:manifest.files['references/bifa-basic-evidence.json']},
 modules:manifest.modules,
}});

test('all hundred cards resolve to exact source spans and registered complete chapters',async()=>{
 assert.deepEqual(guide.cards.map(c=>c.number),Array.from({length:100},(_,i)=>i+1));
 const source=await fs.readFile(path.join(root,guide.source.path));
 assert.equal(hash(source),guide.source.sha256);
 const lines=source.toString('utf8').replace(/\r\n?/g,'\n').split('\n');
 const known=new Map(evidence.sources.flatMap(s=>s.excerpts.map(e=>[e.id,e])));
 for(const card of guide.cards){
  assert.ok(card.understanding&&card.inquiry&&card.source_extracts.length);
  for(const id of card.originals)assert.ok(known.has(id),id);
  const chapter=known.get(card.originals[0]);
  for(const q of card.source_extracts){
   assert.equal(lines.slice(q.line_start-1,q.line_end).join('\n').trim(),q.quote);
   assert.ok(q.line_start>=chapter.line_start&&q.line_end<=chapter.line_end);
   assert.ok(chapter.quote.includes(q.quote));
  }
  const result=await readBoundReference(root,loaded(),{material_id:'BF-'+String(card.number).padStart(2,'0')});
  assert.equal(result.id,'BF-'+String(card.number).padStart(2,'0'));
  assert.equal(result.snapshot,'bound versioned Bifa reading guide');
  assert.ok(result.content.includes(card.inquiry));
 }
});

test('a law lookup shows only the saved chart subpatterns; source alternatives never become matches',async()=>{
 const variants=await readJSON(path.join(root,'output/liuren-bifa-audit-20261111/engine-day-night-1440.json'));
 const c=geometryChart(variants.find(v=>v.day==='庚寅'&&v.day_upper==='亥'&&v.mode==='昼贵'));
 c.nobleman.rule='甲戊庚牛羊';
 const rows=bifaView(c),each=rows.find(r=>r.条目.startsWith('毕法赋35：'));
 assert.ok(each);assert.ok(each.条目.includes('各脱'));assert.ok(!each.条目.includes('互脱'));
 const result=await readBoundReference(root,loaded(rows),{material_id:'BF-35'});
 const saved=result.content.split('本盘已列基本结构：')[1].split('本盘以上记录')[0];
 assert.ok(saved.includes(each.成格));assert.ok(!saved.includes('互脱'));
 assert.ok(result.content.includes('互脱')); // available interpretation, outside the saved matches
 const absent=await readBoundReference(root,loaded([]),{material_id:'BF-35'});
 assert.ok(absent.content.includes('未列为已成立基本结构'));
 assert.ok(!absent.content.includes(each.成格));
 // Lookup is a reading aid and must not mutate the chart.
 assert.deepEqual(bifaView(c),rows);
});

test('old tasks cannot silently read the newly active guide',async()=>{
 const old=loaded();delete old.referenceRegistry.bifaGuide;
 await assert.rejects(readBoundReference(root,old,{material_id:'BF-35'}),/未绑定此任务/);
 const original=await readBoundReference(root,old,{material_id:'BF-B35'});
 assert.ok(original.content.includes('遥克、昴星、别责'));
 for(const id of ['BF-00','BF-101','BF-1','BF-../35'])
  await assert.rejects(readBoundReference(root,loaded(),{material_id:id}),/unknown material_id/);
});

test('lookup follows frozen task binding, ignores active pointer changes and rejects changed source bytes',async t=>{
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-bifa-guide-'));
 t.after(async()=>{
  assert.equal(path.dirname(path.resolve(folder)),path.resolve(os.tmpdir()));
  assert.ok(path.basename(folder).startsWith('liuren-bifa-guide-'));
  await fs.rm(folder,{recursive:true,force:true});
 });
 const target=path.join(folder,active.runtime,rel);
 await fs.mkdir(path.dirname(target),{recursive:true});
 await fs.copyFile(path.join(root,active.runtime,rel),target);
 await fs.mkdir(path.join(folder,'.opencode'));
 await fs.writeFile(path.join(folder,'.opencode/liuren-active.json'),JSON.stringify({runtime:'runtime/liuren/unrelated'}));
 const result=await readBoundReference(folder,loaded(),{material_id:'BF-100'});
 assert.ok(result.content.includes('BF-B100'));
 await fs.appendFile(target,' ');
 await assert.rejects(readBoundReference(folder,loaded(),{material_id:'BF-100'}),/registered source hash changed/);
});
