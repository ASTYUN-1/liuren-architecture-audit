import fs from 'node:fs/promises';
import {checkSubmission} from '../../tools/liuren-adjudication-output.mjs';
const dir=new URL('./',import.meta.url),first=JSON.parse(await fs.readFile(new URL('first-child-report.json',dir),'utf8')),last=JSON.parse(await fs.readFile(new URL('last-child-submission.json',dir),'utf8'));
const ref=JSON.parse(await fs.readFile(new URL('historical-request-ref.json',dir),'utf8')),p=JSON.parse(await fs.readFile(ref.file_path,'utf8')).packet;
const results=[];
for(const [label,raw] of [['first-rejected',first],['fourth-rejected',last]]){const checked=checkSubmission('',raw,p);if(!checked.ok||JSON.stringify(checked.result)!==JSON.stringify(raw))throw Error(label+' not preserved');results.push({label,accepted:true,byteEquivalentContent:true,professionalContentChecked:checked.professionalContentChecked});}
await fs.writeFile(new URL('historical-regression.json',dir),JSON.stringify({historyUnchanged:true,realSessionModified:false,results},null,2));console.log(JSON.stringify(results));
