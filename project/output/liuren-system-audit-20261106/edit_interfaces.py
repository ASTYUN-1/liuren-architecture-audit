from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def edit(rel,fn):
 p=ROOT/rel;p.write_text(fn(p.read_text(encoding='utf-8-sig')),encoding='utf-8')
def plugin(t):
 t=t.replace("const texts=s.array(s.string());","const {text,id,texts:makeTexts}=contractScalars(s);\nconst texts=makeTexts();")
 t=t.replace("const s=tool.schema;","const s=tool.schema;")
 t=t.replace("import {type Plugin, tool}","import {contractScalars} from '../../tools/liuren-adjudication-schema.mjs';\nimport {type Plugin, tool}")
 start=t.index('const packetSchema=');end=t.index('\nconst plugin:',start)
 part=t[start:end]
 part=part.replace('id:s.string()','id:id()')
 for field in ['text','subject','stage','deadline','success_criteria','reason','referent','mapping_basis','statement','reference','source','title','source_path','question','previous_task_id','error_path']:
  part=part.replace(field+':s.string()',field+':text()')
 part=part.replace('source:text()','source:text(1200)')
 part=part.replace('question:text().max(2000)','question:text(2000)')
 part=part.replace('quote:s.string().optional()','quote:text(16000).optional()')
 part=part.replace('request_quote:s.string().optional()','request_quote:text().optional()')
 part=part.replace("}).strict()).optional().describe('12版每个task", "}).strict()).min(1).max(3).describe('每个task")
 part=part.replace(".min(1).describe('必填，只声明", ".min(1).max(3).describe('必填，只声明")
 part=part.replace("}).strict()),\n  chart:","}).strict()).min(1).max(12),\n  chart:")
 part=part.replace("source:text(1200)}).strict()),","source:text(1200)}).strict()).max(100),")
 part=part.replace("mapping_basis:text()}).strict()),","mapping_basis:text()}).strict()).min(1).max(40),")
 part=part.replace("['method_interpretation','unverified'])}).strict()),","['method_interpretation','unverified'])}).strict()).max(80),")
 part=part.replace('question_ids:texts.min(1)','question_ids:texts.min(1).max(12)')
 t=t[:start]+part+t[end:]
 # A successfully saved submission is authoritative even if plugin memory was lost.
 t=t.replace("        const bound=authorized.get(child);\n        if(!bound||bound.readPages.size!==bound.pages)throw new Error('LIUREN_ADJUDICATION_FILE_NOT_FULLY_READ');\n        if(flow){", "        if(flow){")
 t=t.replace("          const raw=parseTaskOutput(output.output);", "          const bound=authorized.get(child)??await binding(child);\n          if(bound.readPages.size!==bound.pages)throw new Error('LIUREN_ADJUDICATION_FILE_NOT_FULLY_READ');\n          const raw=parseTaskOutput(output.output);")
 t=t.replace("        const result=validateOutput(finalizeFoundation", "        const bound=authorized.get(child)??await binding(child);\n        if(bound.readPages.size!==bound.pages)throw new Error('LIUREN_ADJUDICATION_FILE_NOT_FULLY_READ');\n        const result=validateOutput(finalizeFoundation")
 return t
edit('.opencode/plugins/liuren-adjudication.ts',plugin)
edit('tools/liuren-adjudication-contract.mjs',lambda t:t.replace("const idPattern = /^[A-Za-z][A-Za-z0-9_-]{0,63}$/;", "import {ID_PATTERN as idPattern} from './liuren-adjudication-schema.mjs';"))
def output(t):
 t=t.replace("import {symbols,", "import {contractScalars} from './liuren-adjudication-schema.mjs';\nimport {symbols,")
 start=t.index(' const texts=');end=t.index('\nexport function checkSubmission',start)
 part=t[start:end].replace("const texts=s.array(s.string()),candidate=", "const {text,id,texts:makeTexts}=contractScalars(s);\n const texts=makeTexts(),candidate=")
 part=part.replace('s.string()','text()')
 for k in ['id','question_id','issue_id','from','to']:part=part.replace(k+':text()',k+':id()')
 part=part.replace("request_id:text()", "request_id:text(128)")
 part=part.replace('candidates:s.array(candidate).optional()','candidates:s.array(candidate).max(732).optional()')
 part=part.replace('limits:texts}).strict()),','limits:texts}).strict()).max(60),',1)
 part=part.replace('}).strict().optional()}).strict()),','}).strict().optional()}).strict()).max(100),')
 part=part.replace('resolution:text(),limits:texts}).strict()),','resolution:text(),limits:texts}).strict()).max(12),')
 part=part.replace('conditions:texts,limits:texts}).strict()),','conditions:texts,limits:texts}).strict()).min(1).max(12),')
 part=part.replace('resolution:text()}).strict()),missing_inputs','resolution:text()}).strict()).max(100),missing_inputs')
 part=part.replace("s.discriminatedUnion('kind',[timing,quantity]))", "s.discriminatedUnion('kind',[timing,quantity])).max(24)")
 t=t[:start]+part+t[end:]
 t=t.replace("const at='/entity_checks/'+i;", "const at='/entity_checks/'+i;\n  if(!e||typeof e!=='object'||Array.isArray(e)){issue(at,'object_required',e,'entity object');continue;}")
 t=t.replace("const at='/special_methods/'+i;", "const at='/special_methods/'+i;\n  if(!s||typeof s!=='object'||Array.isArray(s)){issue(at,'object_required',s,'special method object');continue;}\n  for(const k of ['basis_ids','fact_ids','calculation_ids','alternatives','limits'])if(s[k]!==undefined&&!Array.isArray(s[k]))issue(at+'/'+k,'array_required',s[k],'array');\n  if(issues.some(e=>e.path.startsWith(at+'/')))continue;")
 return t
edit('tools/liuren-adjudication-output.mjs',output)
def flow(t):
 t=t.replace("const state=await read(parent),checked={ok:false,issues:[{path:'/',code:'execution_error',message}]};", "const state=await read(parent);\n  if(['completed','needs_input'].includes(state.results[child]?.status))return receipt(parent,child);\n  const previous=state.results[child];\n  const checked={ok:false,issues:[{path:'/',code:'execution_error',message}]};")
 t=t.replace("artifact:artifactRef,submissions:1};await write(state);", "artifact:artifactRef,submissions:Math.max(1,previous?.submissions??0)};\n  const attempt=state.attempts.find(a=>a.child===child);if(attempt)attempt.status='invalid_output';await write(state);")
 return t
edit('tools/liuren-flow-control.mjs',flow)
edit('tools/liuren-compute-schema.mjs',lambda t:t.replace("line_start:s.number().int(),line_end:s.number().int(),line_mode:s.enum(['lf','universal'])", "line_start:s.number().int().min(1).optional(),line_end:s.number().int().min(1).optional(),line_mode:s.enum(['lf','universal']).optional()").replace("source:s.object({", "source:s.object({").replace("sha256:s.string().optional()}).strict().optional()", "sha256:s.string().optional()}).strict().optional().describe('当前runtime方法可省略行界，程序核manifest并装入全文；书籍必须给line_start/line_end/line_mode')"))
edit('tools/tests/test_liuren_method_loader.py',lambda t:t.replace("steps[keys.index('timing')]['stage'], 9", "steps[keys.index('timing')]['stage'], route['conditional']['timing']['stage']"))
def scope(t):
 t=t.replace('import importlib.util','import hashlib\nimport importlib.util')
 t=t.replace("        self.write('.opencode/liuren-active.json', json.dumps({'runtime': 'runtime/liuren/current'}))\n        self.write('runtime/liuren/current/manifest.json', json.dumps({'modules': {'timing': {'file': 'methods/timing.md'}}}))\n",'')
 line="        self.write('runtime/liuren/current/methods/timing.md', '失物应期条件\\n最强反证\\n')"
 t=t.replace(line,line+"\n        digest = hashlib.sha256((self.root/'runtime/liuren/current/methods/timing.md').read_bytes()).hexdigest()\n        self.write('.opencode/liuren-active.json', json.dumps({'release':'test-current','methodVersion':'test-v1','runtime':'runtime/liuren/current'}))\n        self.write('runtime/liuren/current/manifest.json', json.dumps({'release':'test-current','version':'test-v1','files':{'methods/timing.md':digest},'modules':{'timing':{'file':'methods/timing.md'}}}))")
 return t
edit('tools/tests/test_liuren_material_scope.py',scope)
