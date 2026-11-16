// Export the bundled ancient examples only. This does not touch user-saved cases.
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const relative='排盘工具魔改/js/data.js';
const bytes=fs.readFileSync(path.join(root,relative));
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'tools/liuren-direct/legacy-engine-manifest.json'),'utf8'));
if(manifest.files.find(x=>x.path==='js/data.js')?.sha256!==sha)throw new Error('Engine data hash changed; inspect source version before export.');
const context=vm.createContext({console:{log(){},warn(){},error(){}},window:{},document:{}},{codeGeneration:{strings:false,wasm:false}});
vm.runInContext(bytes.toString('utf8'),context,{timeout:15000,filename:relative});
const entries=JSON.parse(vm.runInContext('JSON.stringify(GuAnLi2)',context,{timeout:5000}));
if(!Array.isArray(entries)||entries.some(x=>!x?.cundang||!x?.sizhu))throw new Error('Unexpected ancient example shape.');
const directory=path.join(root,'docs/六壬知识整理-20261102/引擎古例参考源');
fs.mkdirSync(directory,{recursive:true});
const source={path:relative,sha256:sha,array:'GuAnLi2',engine_id:manifest.engine_id};
const original={schema:'liuren-engine-ancient-reference-v1',source,count:entries.length,semantic_review_complete:false,
 notes:['仅导出引擎内置古例GuAnLi2；不是800个已核独立事件。','Date/Time/tys可能只是四柱模式显示占位，不是历史占时。','sizhu与设置是整理者输入，须与书中原文对照；不能自动覆盖原书。'],entries};
const lines=['# 排盘引擎内置古代课例参考源','',`来源：${relative}；SHA256：${sha}；数组：GuAnLi2。`,'',
 '本文件为程序逐项导出；原始对象未改写。问事、断语、反馈字段角色按原对象保留，空反馈不等于断语正文没有结果叙述。四柱模式Date/Time不作为真实历史日期。标题索引不表示逐案精读。',''];
const index=[];
for(const [i,entry] of entries.entries()){
 const id=`ENGINE-ANCIENT-${String(i+1).padStart(4,'0')}`;
 lines.push(`## ${id}`,'',`原数组序号（0起）：${i}；原ID：${entry.id??'未载'}`,'');
 // JSON fences preserve exact field text, escaped newlines, HTML and code-like content as data.
 lines.push('```json',JSON.stringify(entry,null,2),'```','');
 index.push({id,source_index:i,source_id:entry.id??null,
  question:entry.cundang.ws??'',state:'indexed_not_semantically_reviewed'});
}
const markdown=lines.join('\n');
// Derive ranges from rendered headings instead of trusting string-array element counts.
const rendered=markdown.split('\n');
const starts=[];
for(let i=0;i<rendered.length;i++)if(/^## ENGINE-ANCIENT-\d+$/.test(rendered[i]))starts.push(i+1);
if(starts.length!==entries.length)throw new Error('Rendered heading coverage mismatch');
for(let i=0;i<index.length;i++){index[i].line_start=starts[i];index[i].line_end=(starts[i+1]??rendered.length+1)-1;}
fs.writeFileSync(path.join(directory,'古例原始对象.json'),JSON.stringify(original,null,2)+'\n','utf8');
fs.writeFileSync(path.join(directory,'古例全文.md'),markdown,'utf8');
fs.writeFileSync(path.join(directory,'索引.json'),JSON.stringify({source,count:index.length,records:index},null,2)+'\n','utf8');
const reread=JSON.parse(fs.readFileSync(path.join(directory,'古例原始对象.json'),'utf8'));
if(JSON.stringify(reread.entries)!==JSON.stringify(entries))throw new Error('Roundtrip mismatch');
console.log(JSON.stringify({count:entries.length,source,output:path.relative(root,directory),roundtrip_equal:true}));
