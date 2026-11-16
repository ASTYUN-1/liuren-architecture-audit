import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {savePacket,loadPacket,parseReference,normalizePacket} from './source/liuren-adjudication-files.mjs';
const packet=JSON.parse(await fs.readFile(new URL('./synthetic-input.json',import.meta.url),'utf8'));
test('file round trip retains packet and delegates only path and hash',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-file-'));
  const saved=await savePacket(root,packet,'parent-1');
  assert.ok(saved.task_prompt.length<500);
  assert.deepEqual((await loadPacket(root,parseReference(saved.task_prompt))).envelope.packet,packet);
  assert.equal((await loadPacket(root,saved)).envelope.parent_session_id,'parent-1');
});
test('double-escaped JSON screenshot failure gets actionable file handoff error',()=>{
  assert.throws(()=>parseReference('{\\"schema\\":\\"x\\"}'),/liuren_adjudication_packet/);
  assert.throws(()=>parseReference(JSON.stringify(packet)),/liuren_adjudication_packet/);
});
test('reserved entity IDs are renamed with references, not technical content',()=>{
  const p=structuredClone(packet);p.entities[0].id='E01';
  p.observations=[{id:'O1',entity_ids:['E01'],kind:'relation',statement:'原观察不改',reference:'日干',source:'本盘',verification:'unverified'}];
  const normalized=normalizePacket(p);
  assert.equal(normalized.packet.entities[0].id,'I_E01');
  assert.deepEqual(normalized.packet.observations[0].entity_ids,['I_E01']);
  assert.equal(normalized.packet.observations[0].statement,'原观察不改');
  p.entities[1].id='E01';assert.throws(()=>normalizePacket(p),/duplicate/);
});
test('day stem explicit residence and composite symbols are accepted without remapping',()=>{
  for(const symbol of ['辛','辛（寄宫戌）','未卯亥']){
    const p=structuredClone(packet);p.entities[0].branch=symbol;
    assert.equal(normalizePacket(p).packet.entities[0].branch,symbol);
  }
});
test('tampered hash and outside path fail closed',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-file-'));
  const saved=await savePacket(root,packet,'parent-1');
  await assert.rejects(loadPacket(root,{...saved,file_path:path.join(root,'other.json')}),/outside/);
  await fs.appendFile(saved.file_path,' ');
  await assert.rejects(loadPacket(root,saved),/changed/);
});
