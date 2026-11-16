import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=fileURLToPath(new URL('./',import.meta.url));
const root=path.resolve(here,'../..');
const ptr=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
assert.equal(ptr.release,'20261105-no-retrieval-01');
const tool=(await import(pathToFileURL(path.join(root,'.opencode/tools/liuren_materials.ts')).href)).default;
const context={sessionID:'no-case-experience-variant-probe',abort:new AbortController().signal};
const checks=[];
const scope=JSON.parse(await tool.execute({action:'scope'},context));
assert.equal(scope.case_experience_retrieval,'disabled-by-experiment');
assert.equal(scope.libraries.cases,undefined);assert.equal(scope.libraries.experience,undefined);
assert.ok(scope.libraries.books.length>0);
checks.push('scope-excludes-two-libraries-retains-books');
const requests=[
  {action:'retrieve',case_query:'考试',experience_query:'等级',category:'考试占'},
  {action:'scan',library:'cases',query:'考试'},
  {action:'scan',library:'experience',query:'考试'},
  {action:'read',path:'案例项目库/probe.md',start:1,count:1},
  {action:'read',path:'经验日志/probe.md',start:1,count:1},
];
for(const request of requests){
  await assert.rejects(()=>tool.execute(request,context),/LIUREN_EXPERIMENT_NO_RETRIEVAL|超出本机研判资料范围/);
  checks.push(`denied-${request.action}-${request.library||request.path||'dual-search'}`);
}
const aliases=JSON.parse(await fs.readFile(path.join(root,ptr.runtime,'source-read-map.json'),'utf8'));
for(const [alias,item] of Object.entries(aliases.aliases)){
  if(item.path.includes('/经验日志/')){
    await assert.rejects(()=>tool.execute({action:'read',path:alias,start:1,count:1},context),/LIUREN_EXPERIMENT_NO_RETRIEVAL/);
    checks.push('historical-experience-alias-denied');
  }
}
const book='书籍库/经典古籍/佚名/壬归.txt';
const text=JSON.parse(await tool.execute({action:'read',path:book,start:355,count:5},context));
assert.equal(text.path,book);assert.equal(text.start,355);assert.ok(text.text.length>0);
checks.push('original-book-read-retained');
const scan=JSON.parse(await tool.execute({action:'scan',library:'books',query:'专视青龙',limit:1},context));
assert.ok(scan.hits.length>0);assert.equal(scan.library,'books');
checks.push('book-search-retained');
const cache=path.join(root,'tmp/liuren-materials',`no-retrieval-probe-${process.pid}.json`);
await fs.mkdir(path.dirname(cache),{recursive:true});
await fs.writeFile(cache,'{}\n',{flag:'wx'});
try{
  await assert.rejects(()=>tool.execute({action:'read',path:cache,start:1,count:1},context),/LIUREN_EXPERIMENT_NO_RETRIEVAL/);
  checks.push('old-retrieval-cache-read-denied');
}finally{await fs.unlink(cache);}
await fs.writeFile(path.join(here,'variant-tools.json'),JSON.stringify({ok:true,release:ptr.release,checks,modelCalls:0},null,2)+'\n');
process.stdout.write(JSON.stringify({ok:true,release:ptr.release,checks:checks.length,modelCalls:0})+'\n');
