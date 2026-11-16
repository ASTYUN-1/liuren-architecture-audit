"""Inspect the real merged desktop configuration; emit only safe inventory fields."""
from pathlib import Path
import json,os,socket,subprocess,time,urllib.request,urllib.parse,concurrent.futures
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def main():
 env=os.environ.copy();env.update(ELECTRON_RUN_AS_NODE='1',OPENCODE_DISABLE_AUTOUPDATE='true',OPENCODE_DISABLE_MODELS_FETCH='true',OPENCODE_DISABLE_LSP_DOWNLOAD='true',OPENCODE_CONFIG_CONTENT=json.dumps({'snapshot':False}))
 sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
 exe=Path.home()/'AppData/Local/Programs/@opencode-aidesktop/OpenCode.exe'
 bootstrap=ROOT/'output/liuren-stalled-child-repair-20261107/desktop-server.mjs'
 log=(OUT/'live-server.log').open('w',encoding='utf-8')
 server=subprocess.Popen([str(exe),str(bootstrap),str(port)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 (OUT/'live-server.json').write_text(json.dumps({'pid':server.pid,'port':port,'directory':str(ROOT)}),'utf-8')
 url=f'http://127.0.0.1:{port}';query='?directory='+urllib.parse.quote(str(ROOT))
 def fetch(path):
  started=time.monotonic()
  try:
   with urllib.request.urlopen(url+path+query,timeout=120) as response:d=json.load(response)
   if path=='/config':
    d={'plugin':d.get('plugin'),'default_agent':d.get('default_agent'),'mcp':{k:{'enabled':v.get('enabled',True),'type':v.get('type')} for k,v in d.get('mcp',{}).items()},'tool_output':d.get('tool_output'),'instructions':d.get('instructions')}
   elif path=='/agent':d=[{k:v[k] for k in ['name','model','variant','mode','hidden','native','disable'] if k in v} for v in d]
   elif path=='/mcp':d={k:{'status':v.get('status'),'errorPresent':bool(v.get('error')),'errorType':('timeout' if 'timeout' in str(v.get('error','')).lower() else 'connection-or-startup-error') if v.get('error') else None} for k,v in d.items()}
   elif path=='/config/providers':
    d={'default':d.get('default'),'providers':[{'id':v.get('id'),'models':{k:{f:m.get(f) for f in ['id','limit','capabilities','variants']} for k,m in v.get('models',{}).items() if k=='deepseek-flash'}} for v in d.get('providers',[])]}
   return path,{'ok':True,'seconds':round(time.monotonic()-started,2),'data':d}
  except Exception as error:return path,{'ok':False,'errorType':type(error).__name__,'seconds':round(time.monotonic()-started,2)}
 for _ in range(100):
  try:urllib.request.urlopen(url+'/global/health',timeout=.5).close();break
  except Exception:time.sleep(.15)
 result={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  jobs=[pool.submit(fetch,p) for p in ['/config','/agent','/mcp','/config/providers']]
  for job in concurrent.futures.as_completed(jobs):
   path,value=job.result();result[path]=value
   (OUT/'live-host.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
   print(json.dumps({path:value},ensure_ascii=False),flush=True)
 print('LIVE_HOST_READY_FOR_TESTS',flush=True)
 # Kept alive for bounded follow-up calls; never stop any user-owned process.
 try:server.wait(timeout=1800)
 except subprocess.TimeoutExpired:server.terminate();server.wait(timeout=10)
 finally:log.close()
if __name__=='__main__':main()
