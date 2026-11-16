import {registerHooks} from 'node:module';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import readline from 'node:readline';
const root=process.cwd();
registerHooks({resolve(specifier,context,next){if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);return next(specifier,context);}});
const {tool}=await import('@opencode-ai/plugin');
const {default:plugin}=await import(pathToFileURL(path.join(root,'.opencode/plugins/liuren-adjudication.ts')).href);
const hooks=await plugin({directory:root,client:{session:{messages:async()=>({data:[]})}}});
const {runResolvedChart}=await import(pathToFileURL(path.join(root,'tools/liuren-resolved-chart.mjs')).href);
const chart=await runResolvedChart({datetime:'2026-08-04T14:32',label:'接口调用验收-合成场景'});
if(!chart.ok)throw Error('probe chart failed');
const allowed=['liuren_tool_help','liuren_compute'];
console.log(JSON.stringify({archive:chart.archive,tools:allowed.map(name=>({type:'function',function:{name,description:hooks.tool[name].description,parameters:tool.schema.toJSONSchema(tool.schema.object(hooks.tool[name].args))}}))}));
for await(const line of readline.createInterface({input:process.stdin})){
 try{const {name,args}=JSON.parse(line);if(!allowed.includes(name))throw Error('probe tool not allowed');const output=await hooks.tool[name].execute(args,{agent:'liuren',sessionID:'audit_real_model_usage_20261106'});console.log(JSON.stringify({ok:true,output}));}
 catch(e){console.log(JSON.stringify({ok:false,error:String(e)}));}
}
