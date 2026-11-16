"""Read only selected metadata of the synthetic call, never reasoning text."""
from pathlib import Path
import base64, json, os, shutil, socket, subprocess, time, urllib.request, urllib.parse
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
record=json.loads((HERE/'smoke-host.json').read_text('utf-8'))
child=record['metadata']['sessionId']
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
    rows=get('/session/'+child+'/message')
    safe=[{k:m['info'].get(k) for k in ['role','agent','modelID','providerID','variant','finish','tokens','cost','error','time']} for m in rows]
    (HERE/'smoke-token-metadata.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(safe,ensure_ascii=False))
finally:
    p.terminate()
    try:p.wait(timeout=8)
    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
