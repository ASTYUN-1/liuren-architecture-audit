import {createHash, randomUUID} from 'node:crypto';
import {mkdir, readFile, writeFile, realpath, lstat} from 'node:fs/promises';
import {resolve, relative, isAbsolute, sep} from 'node:path';
import {validateInput} from './liuren-adjudication-contract.mjs';

export const FILE_MARKER='LIUREN_ADJUDICATION_FILE_V1';
export const PAGE_SIZE=10000;
const fail=s=>{throw new Error('LIUREN_ADJUDICATION_FILE: '+s);};
export const digest=raw=>createHash('sha256').update(raw).digest('hex');
const inside=(root,path)=>{const rel=relative(root,path);return rel!==''&&!rel.startsWith('..'+sep)&&rel!=='..'&&!isAbsolute(rel);};

// Rename only identifiers, never facts, rankings, relations or conclusions.
export function normalizePacket(input){
  if(input===null||typeof input!=='object'||Array.isArray(input))fail('packet must be an object; use {packet:{...}}; do not stringify or flatten it');
  const p=structuredClone(input), changes=[], names=new Set();
  for(const field of ['questions','facts','entities','observations','method_materials','focus_issues']) {
    if(!Array.isArray(p[field]))fail('packet.'+field+' must be an array');
    if(p[field].some(row=>row===null||typeof row!=='object'||Array.isArray(row)))fail('packet.'+field+' rows must be objects');
  }
  const fields=['questions','facts','entities','observations','method_materials','focus_issues'];
  for(const field of fields)for(const row of p[field]??[]){
    if(!row||typeof row.id!=='string')continue;
    if(names.has(row.id))fail('duplicate input ID '+row.id);
    names.add(row.id);
  }
  const map=new Map();
  for(const id of names)if(/^E\d+$/.test(id)){
    let next='I_'+id;while(names.has(next))next='I_'+next;
    names.add(next);map.set(id,next);changes.push({from:id,to:next});
  }
  for(const field of fields)for(const row of p[field]??[]){
    row.id=map.get(row.id)??row.id;
    for(const key of ['question_ids','entity_ids','observation_ids'])if(Array.isArray(row[key]))row[key]=row[key].map(id=>map.get(id)??id);
  }
  return {packet:validateInput(p),renamed_ids:changes};
}

// Archive mode copies only validated program facts, never native summary or analysis.
// The caller supplies the exact archive path and hash returned by liuren_chart.
export async function resolveChartArchive(root,input){
  if(input===null||typeof input!=='object'||Array.isArray(input))return input;
  const chart=input.chart;
  if(!chart||typeof chart!=='object'||Array.isArray(chart)||!('archive' in chart))return input;
  if(Object.keys(chart).some(k=>!['source','archive'].includes(k)))fail('packet.chart: use archive OR complete facts, never both');
  const ref=chart.archive;
  if(!ref||typeof ref!=='object'||Array.isArray(ref)||Object.keys(ref).some(k=>!['path','sha256'].includes(k))||typeof ref.path!=='string'||!isAbsolute(ref.path)||!/^([a-f0-9]{64})$/.test(ref.sha256))fail('packet.chart.archive requires exact absolute path and sha256 from liuren_chart.archive');
  const base=await realpath(root),folder=resolve(base,'排盘存档/六壬'),file=resolve(ref.path);
  if(!inside(folder,file)||!file.endsWith('.json'))fail('packet.chart.archive.path outside 排盘存档/六壬');
  const actual=await realpath(file);
  if(!inside(folder,actual)||(await lstat(file)).isSymbolicLink()||actual!==file)fail('packet.chart.archive linked path rejected');
  if((await lstat(file)).size>1000000)fail('packet.chart.archive oversized');
  const raw=await readFile(file,'utf8');
  if(digest(raw)!==ref.sha256)fail('packet.chart.archive.sha256 mismatch; use the original liuren_chart archive');
  const record=JSON.parse(raw),metadata=record._direct;
  if(!['liuren-direct-export-v1','liuren-direct-corrected-export-v1'].includes(metadata?.schema)||metadata?.validation?.ok!==true||metadata?.facts?.schema!=='liuren-chart-facts-v1')fail('packet.chart.archive is not a validated program chart; do not substitute a hand-written chart');
  const p=structuredClone(input);
  p.chart={source:chart.source+' [program archive: '+file+'; sha256='+ref.sha256+']',facts:structuredClone(metadata.facts)};
  return p;
}

async function directory(root){
  const base=await realpath(root),folder=resolve(base,'output/liuren-adjudication-requests');
  await mkdir(folder,{recursive:true});
  if((await lstat(folder)).isSymbolicLink()||!(inside(base,await realpath(folder))))fail('request directory escapes workspace');
  return folder;
}
export async function savePacket(root,input,parentSessionID){
  if(!/^[A-Za-z0-9_-]+$/.test(parentSessionID))fail('invalid parent session');
  const {packet,renamed_ids}=normalizePacket(await resolveChartArchive(root,input));
  const folder=await directory(root);
  const envelope={schema:'liuren-adjudication-file-v1',parent_session_id:parentSessionID,packet};
  const raw=JSON.stringify(envelope,null,2)+'\n';
  const file=resolve(folder,packet.request_id+'-'+randomUUID()+'.json');
  await writeFile(file,raw,{flag:'wx',mode:0o600});
  const sha256=digest(raw);
  return {file_path:file,sha256,request_id:packet.request_id,renamed_ids,task_prompt:FILE_MARKER+'\n'+file+'\n'+sha256};
}
export function parseReference(text){
  if(typeof text!=='string')fail('task prompt must be the saved task_prompt');
  const lines=text.trim().split(/\r?\n/);
  if(lines.length!==3||lines[0]!==FILE_MARKER||!isAbsolute(lines[1])||!/^([a-f0-9]{64})$/.test(lines[2]))fail('先调用liuren_adjudication_packet保存材料，再将返回的task_prompt原样传给task；不要在prompt内粘贴或转义长JSON');
  return {file_path:lines[1],sha256:lines[2]};
}
export async function loadPacket(root,ref){
  const folder=await directory(root),file=resolve(ref.file_path);
  if(!inside(folder,file)||relative(folder,file).includes(sep)||!file.endsWith('.json'))fail('path outside request directory');
  if((await lstat(file)).isSymbolicLink()||await realpath(file)!==file)fail('linked request file rejected');
  const raw=await readFile(file,'utf8');
  if(Buffer.byteLength(raw)>300000||digest(raw)!==ref.sha256)fail('request file changed or oversized; save a new packet');
  const envelope=JSON.parse(raw);
  if(envelope.schema!=='liuren-adjudication-file-v1'||typeof envelope.parent_session_id!=='string')fail('file envelope');
  validateInput(envelope.packet);
  return {raw,envelope,pages:Math.ceil(raw.length/PAGE_SIZE)};
}
