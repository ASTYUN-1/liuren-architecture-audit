import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const folder=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(folder,'../..');
const load=async name=>JSON.parse(await fs.readFile(path.join(folder,name),'utf8'));
const save=(name,value)=>fs.writeFile(path.join(folder,name),JSON.stringify(value,null,2)+'\n',{flag:'wx'});
const q=await load('04-selected-relations.request.json');
q.request.strength.review=false;
await save('14-no-review.request.json',q);
const text=execFileSync(process.execPath,['tools/liuren-codex.mjs','--request',path.join(folder,'14-no-review.request.json')],{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:1024*1024});
await fs.writeFile(path.join(folder,'15-no-review.response.json'),text,{flag:'wx'});
const value=JSON.parse(text);
const reviewed=await load('05-selected-relations.response.json');
for(const name of ['06-opencode-single-palace.response.json','07-opencode-selected-relations.response.json'])
 await save(name.replace('.response.json','.readable.json'),await load(name));
const result={default_output_has_review:Object.hasOwn(value,'review'),
 default_output_has_pending:JSON.stringify(value).includes('pending'),
 default_output_still_has_base:Object.hasOwn(value.quantity_basis.rows[0],'body_base'),
 default_output_still_has_void_counterfactuals:Object.hasOwn(value.quantity_basis.rows[0],'without_void'),
 scores_unchanged_by_review:JSON.stringify(value.actors)===JSON.stringify(reviewed.actors)};
await save('16-no-review-observation.json',result);
console.log(JSON.stringify(result,null,2));
