"""Read only selected metadata of the synthetic call, never reasoning text."""
from pathlib import Path
import base64, json, os, shutil, socket, subprocess, time, urllib.request, urllib.parse
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
with socket.socket() as sock:
    sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
headers={}
if os.environ.get('OPENCODE_SERVER_PASSWORD'):
    headers['Authorization']='Basic '+base64.b64encode((os.environ.get('OPENCODE_SERVER_USERNAME','opencode')+':'+os.environ['OPENCODE_SERVER_PASSWORD']).encode()).decode()
def get(path):
    url=f'http://127.0.0.1:{port}'+path+'?'+urllib.parse.urlencode({'directory':str(ROOT)})
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=45) as r:return json.load(r)
p=subprocess.Popen([shutil.which('opencode'),'serve','--hostname','127.0.0.1','--port',str(port)],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
try:
    deadline=time.monotonic()+40
    while True:
        try:get('/global/health');break
        except OSError:
            if time.monotonic()>deadline:raise
            time.sleep(.3)
    sessions=get('/session')
    safe=[]
    sessions=sorted([s for s in sessions if s.get('directory','').lower()==str(ROOT).lower()],key=lambda s:s.get('time',{}).get('updated',0),reverse=True)
    for session in sessions[:12]:
        rows=get('/session/'+session['id']+'/message')
        for m in rows:
            for part in m.get('parts',[]):
                if part.get('type')!='tool' or part.get('tool')!='task':continue
                state=part.get('state',{});args=state.get('input',{})
                if args.get('subagent_type')!='liuren-adjudicator' or state.get('status')!='error':continue
                raw=args.get('prompt',''); error=state.get('error','')
                shape={}
                try:
                    packet=json.loads(raw)
                    shape={'entities':[{k:e.get(k) for k in ['id','branch']} for e in packet.get('entities',[])], 'ids':{field:[e.get('id') for e in packet.get(field,[])] for field in ['questions','facts','observations','method_materials']}}
                except (ValueError,TypeError):pass
                safe.append({'session':session['id'],'model':{k:m.get('info',{}).get(k) for k in ['modelID','providerID']},'error':error[:400],'promptLength':len(raw),'startsEscapedObject':raw.lstrip().startswith('{\\"'),'startsObject':raw.lstrip().startswith('{"'),'hasChild':bool(state.get('metadata',{}).get('sessionId')),'shape':shape})
    (HERE/'failure-metadata.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(safe,ensure_ascii=False))
finally:
    p.terminate()
    try:p.wait(timeout=8)
    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
