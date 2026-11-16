// Validate original failed arguments without executing a tool or changing task state.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {createHash} from 'node:crypto';
import {parseResultArguments} from '../../tools/liuren-adjudication-schema.mjs';
import {checkDeliveryReview,inspectRecheckFindings} from '../../tools/liuren-consistency-audit.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
registerHooks({resolve(specifier,context,next){
 if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);
 return next(specifier,context);
}});
const {tool}=await import('@opencode-ai/plugin');
const {default:plugin}=await import(pathToFileURL(path.join(root,'.opencode/plugins/liuren-adjudication.ts')).href);
const hooks=await plugin({directory:root,client:{}});
const schema=tool.schema.object(hooks.tool.liuren_adjudication_result.args).strict();
let stdin='';for await(const chunk of process.stdin)stdin+=chunk;
const input=JSON.parse(stdin),state=JSON.parse(await fs.readFile(path.join(root,'output/liuren-flow-state',input.session+'.json'),'utf8'));
const outcomes=[];
for(const [index,args] of input.failed_results.entries()){
 const ref=state.results[args.task_id]?.artifact;if(!ref)throw Error('Missing saved result');
 const raw=await fs.readFile(ref.path,'utf8');
 if(createHash('sha256').update(raw).digest('hex')!==ref.sha256)throw Error('Saved artifact changed');
 const saved=JSON.parse(raw);
 try{
  const parsed=parseResultArguments(schema,args);
  const verdict=parsed.action==='review'
   ?checkDeliveryReview(parsed.review,saved.checked.result,{packet:saved.packet,receipts:saved.calculation_receipts})
   :inspectRecheckFindings(saved.packet,saved.checked.result,parsed.findings,saved.calculation_receipts);
  outcomes.push({index,action:parsed.action,ok:verdict.ok,issues:verdict.issues.map(({code,path,unknown_refs,missing_refs})=>({code,path,...(unknown_refs?{unknown_refs}:{}),...(missing_refs?{missing_refs}:{})}))});
 }catch(error){outcomes.push({index,action:args.action,ok:false,argument_error:String(error.message)});}
}
const result={scope:'read-only replay of exact failed result arguments; no task, review or recheck executed',real_model_called:false,total:outcomes.length,accepted_now:outcomes.filter(r=>r.ok).length,outcomes};
await fs.writeFile(new URL('./log-replay.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
