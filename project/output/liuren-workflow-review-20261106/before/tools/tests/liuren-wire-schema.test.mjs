import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
import {registerHooks} from 'node:module';
import {moduleURL} from './fixtures/liuren-adjudication-v2.mjs';
const ROOT=fileURLToPath(new URL('../../',import.meta.url));
const OUT=path.join(ROOT,'output/liuren-schema-compat-20261106');
registerHooks({resolve(specifier,context,next){
 if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(ROOT,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);
 return next(specifier,context);
}});
const {tool}=await import('@opencode-ai/plugin');const s=tool.schema;
const {createComputeSchemas}=await import(moduleURL('tools/liuren-compute-schema.mjs'));
const previous=await import(pathToFileURL(path.join(OUT,'before/tools/liuren-compute-schema.mjs')).href);
const {default:plugin}=await import(moduleURL('.opencode/plugins/liuren-adjudication.ts'));
const hooks=await plugin({directory:ROOT,client:{}});
const before=JSON.parse(await readFile(path.join(OUT,'before-wire.json'),'utf8'));
const fixed=JSON.parse(await readFile(path.join(ROOT,'output/liuren-system-audit-20261106/current-wire.json'),'utf8'));
function refs(schema){
 const all=[],missing=[];
 function walk(node){
  if(!node||typeof node!=='object')return;
  if(node.$ref){
   const ref=node.$ref;all.push(ref);let cursor=schema;
   if(ref!=='#'){
    if(!ref.startsWith('#/'))missing.push(ref);
    else try{for(const key of ref.slice(2).split('/')){cursor=cursor[key.replaceAll('~1','/').replaceAll('~0','~')];if(cursor===undefined)throw Error();}}catch{missing.push(ref);}
   }
  }
  for(const child of Object.values(node))if(child&&typeof child==='object')walk(child);
 }
 walk(schema);return {all,missing};
}

test('real OpenCode 1.18.29 outbound request reproduced both dangling references before the fix',()=>{
 assert.equal(before.exitCode,1);assert.ok(before.requests.length);
 const errors=before.requests.flatMap(r=>r.referenceErrors);
 assert.ok(errors.some(e=>e.tool==='liuren_adjudication_packet'&&e.missing.includes('#/$defs/__schema0')));
 assert.ok(errors.some(e=>e.tool==='liuren_compute'&&e.missing.includes('#/$defs/__schema0')));
});

test('failure is root reconstruction dropping definitions, not failed execution of a tool',()=>{
 const full=s.toJSONSchema(s.object(previous.createComputeSchemas(s).args));
 assert.equal(refs(full).missing.length,0);assert.ok(refs(full).all.length);
 const rebuilt={type:'object',properties:full.properties,required:full.required,additionalProperties:false};
 assert.ok(refs(rebuilt).missing.includes('#/$defs/__schema0'));
});

test('every published native tool schema remains valid after OpenCode root reconstruction',()=>{
 for(const [name,definition] of Object.entries(hooks.tool)){
  const full=s.toJSONSchema(s.object(definition.args));
  const rebuilt={type:'object',properties:full.properties,required:full.required,additionalProperties:false};
  assert.deepEqual(refs(full),{all:[],missing:[]},name+' must not depend on reference preservation');
  assert.deepEqual(refs(rebuilt),{all:[],missing:[]},name+' reconstructed');
 }
});

test('actual fixed outbound request contains all five tools without refs or definitions',()=>{
 assert.equal(fixed.exitCode,0);assert.equal(fixed.realModelCalled,false);assert.equal(fixed.loopbackOnlyProvider,true);
 const tools=fixed.requests.flatMap(r=>r.tools);
 assert.deepEqual([...new Set(tools.map(t=>t.name))].sort(),['liuren_adjudication_packet','liuren_adjudication_read','liuren_adjudication_result','liuren_adjudication_submit','liuren_compute']);
 for(const t of tools){assert.deepEqual(refs(t.parameters),{all:[],missing:[]},t.name);assert.equal(t.parameters.$defs,undefined);}
 assert.ok(fixed.requests.every(r=>r.referenceErrors.length===0));
});

test('actual outbound calendar retains typed required values and quantity retains visible node variants',()=>{
 const compute=fixed.requests.flatMap(r=>r.tools).find(t=>t.name==='liuren_compute').parameters;
 assert.deepEqual(compute.properties.calendar.required,['start','end','timezone','day_boundary']);
 assert.deepEqual(compute.properties.calendar.properties.day_boundary.enum,['civil-midnight','zi-hour']);
 assert.equal(compute.properties.calendar.properties.timezone.const,'Asia/Shanghai');
 assert.ok(JSON.stringify(compute.properties.expression).includes('multiply'));
 assert.ok(JSON.stringify(compute.properties.expression).includes('args'));
});

test('captured request is tied to the exact schema and plugin implementations under test',async()=>{
 for(const [rel,sha] of Object.entries(fixed.implementationSha256)){
  const content=await readFile(fileURLToPath(moduleURL(rel)));
  assert.equal(createHash('sha256').update(content).digest('hex'),sha,rel);
 }
});

test('reference-free publication preserves strict recursive execution validation',()=>{
 const schemas=createComputeSchemas(s);
 const expression={op:'multiply',args:[{value:8},{op:'add',args:[{value:2},{value:4}]}]};
 assert.deepEqual(schemas.parse({action:'quantity',expression}).expression,expression);
 const bad=structuredClone(expression);bad.args[1].args[1]={op:'eval',args:[{value:1},{value:2}]};
 assert.throws(()=>schemas.parse({action:'quantity',expression:bad}),/expression/);
 const mixed={op:'multiply',args:[{value:8},{value:6,table:'branch',symbol:'丑'}]};
 assert.throws(()=>schemas.parse({action:'quantity',expression:mixed}),/expression/);
});
