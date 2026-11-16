// Serialize actual native tool definitions and simulate the host's root
// reconstruction. This is NOT an HTTP/provider capture or a model call.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {createHash} from 'node:crypto';
const root=fileURLToPath(new URL('../../',import.meta.url));
registerHooks({resolve(specifier,context,next){
 if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);
 return next(specifier,context);
}});
const {tool}=await import('@opencode-ai/plugin');
const {default:plugin}=await import(pathToFileURL(path.join(root,'.opencode/plugins/liuren-adjudication.ts')).href);
const hooks=await plugin({directory:root,client:{}}),definitions=[];
for(const [name,definition] of Object.entries(hooks.tool)){
 const full=tool.schema.toJSONSchema(tool.schema.object(definition.args));
 const rebuilt={type:'object',properties:full.properties,required:full.required,additionalProperties:false};
 if(JSON.stringify(full).includes('"$ref"')||JSON.stringify(rebuilt).includes('"$ref"'))throw Error(name+' has a schema reference');
 definitions.push({name,parameters:rebuilt});
}
const tracked=['.opencode/plugins/liuren-adjudication.ts','tools/liuren-compute-schema.mjs','tools/liuren-adjudication-schema.mjs','tools/liuren-consistency-audit.mjs','tools/liuren-quantity-review.mjs','tools/liuren-quantity-adjustment.mjs'];
const implementationSha256={};for(const f of tracked)implementationSha256[f]=createHash('sha256').update(await fs.readFile(path.join(root,f))).digest('hex');
const result={schema:'liuren-native-schema-check-v1',exitCode:0,realModelCalled:false,networkRequestCaptured:false,
 scope:'actual native tool serialization and host root reconstruction only; requests is a compatibility field holding the serialized tool projection, not a sent request',
 requests:[{tools:definitions}],implementationSha256};
await fs.writeFile(new URL('./native-schema.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({ok:true,native_tools:definitions.length,network_request_captured:false,real_model_called:false}));
