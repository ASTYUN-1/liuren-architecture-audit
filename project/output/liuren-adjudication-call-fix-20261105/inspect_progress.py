"""Read only selected metadata of the synthetic call, never reasoning text."""
from pathlib import Path
import base64, json, os, shutil, socket, subprocess, time, urllib.request, urllib.parse
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
parent=json.loads((HERE/'smoke-session.json').read_text('utf-8'))['parent']
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
    rows=get('/session/'+parent+'/message')
    tasks=[p for m in rows for p in m.get('parts',[]) if p.get('type')=='tool' and p.get('tool')=='task']
    child=next((p.get('state',{}).get('metadata',{}).get('sessionId') for p in tasks if p.get('state',{}).get('metadata',{}).get('sessionId')),None)
    if not child:
        child_sessions=get('/session/'+parent+'/children')
        child=child_sessions[-1]['id'] if child_sessions else None
    children=get('/session/'+child+'/message') if child else []
    safe={'parentTools':[{'tool':p['tool'],'status':p.get('state',{}).get('status')} for m in rows for p in m.get('parts',[]) if p.get('type')=='tool'], 'childMessages':[{k:m['info'].get(k) for k in ['role','agent','finish','tokens','time','error']} for m in children], 'childTools':[{'tool':p['tool'],'status':p.get('state',{}).get('status'),'page':p.get('state',{}).get('input',{}).get('page'),'error':p.get('state',{}).get('error')} for m in children for p in m.get('parts',[]) if p.get('type')=='tool']}
    (HERE/'progress-metadata.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(safe,ensure_ascii=False))
finally:
    p.terminate()
    try:p.wait(timeout=8)
    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
