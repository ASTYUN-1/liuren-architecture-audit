from pathlib import Path
import shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
prior=ROOT/'output/liuren-real-case-20261106';dest=OUT/'real-run'
assert not dest.exists();dest.mkdir()
for name in ['selection.json','desktop-server.mjs','collect.py']:
    shutil.copyfile(prior/name,dest/name)
t=(prior/'run.py').read_text('utf-8-sig')
t=t.replace("ROOT=OUT.parents[1]","ROOT=OUT.parents[2]")
t=t.replace("hooks.tool={...slim.tool,...own.tool,liuren_materials:{...materials,async execute(args,context){const r=await run('python',['-X','utf8',path.join(ctx.directory,'tools/liuren-materials.py'),'--request',JSON.stringify({...args,_context_key:context.sessionID})],{cwd:ctx.directory,encoding:'utf8',windowsHide:true,timeout:90000,maxBuffer:4*1024*1024});return r.stdout;}}};return hooks;", "hooks.tool={...slim.tool,...own.tool,liuren_materials:materials};return hooks;")
assert 'async execute(args,context)' not in t
t=t.replace("events=[];lock=threading.Lock();started=time.monotonic()", "events=[];wire=[];lock=threading.Lock();started=time.monotonic()")
t=t.replace("names=[x.get('function',{}).get('name') for x in payload.get('tools',[])]", "names=[x.get('function',{}).get('name') for x in payload.get('tools',[])]\n  if not wire:\n   wire.extend({'name':x['function']['name'],'parameters':x['function']['parameters']} for x in payload.get('tools',[]) if x.get('function',{}).get('name','').startswith('liuren_'))")
t=t.replace("config=load(ROOT/'opencode.json');", "def remap(v):\n if isinstance(v,str):return v.replace(str(ROOT),str(project)).replace(ROOT.as_posix(),project.as_posix())\n if isinstance(v,list):return [remap(x) for x in v]\n if isinstance(v,dict):return {remap(k):remap(x) for k,x in v.items()}\n return v\nconfig=remap(load(ROOT/'opencode.json'));")
t=t.replace("print(json.dumps({'exitCode':code,'requests':len(events),'elapsedSeconds':summary['elapsedSeconds']},ensure_ascii=False),flush=True)", "print(json.dumps({'exitCode':code,'requests':len(events),'elapsedSeconds':summary['elapsedSeconds']},ensure_ascii=False),flush=True)\n evidence={'exitCode':code,'realModelCalled':True,'scope':'real DeepSeek request emitted by installed desktop host; production material executor; isolated permission paths remapped','requests':[{'tools':wire}],'implementationSha256':{r:sha(ROOT/r) for r in ['.opencode/plugins/liuren-adjudication.ts','tools/liuren-flow-control.mjs','tools/liuren-compute-schema.mjs','.opencode/tools/liuren_materials.ts']}}\n (OUT.parent/'current-wire.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\\n','utf-8')")
(dest/'run.py').write_text(t,'utf-8')
print('Prepared real rerun: actual material executor, no custom execute replacement, mapped permissions')
