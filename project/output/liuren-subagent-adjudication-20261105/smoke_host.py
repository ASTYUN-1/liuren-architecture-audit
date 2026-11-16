"""Exercise slim's custom agent through a real native Task using synthetic data.

No credentials are read from files or logged. The local OpenCode host uses its
existing provider configuration. Only text results and selected metadata are saved.
"""
from pathlib import Path
import base64
import json
import os
import shutil
import socket
import subprocess
import time
import urllib.request
import urllib.error
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import sys

HERE=Path(__file__).resolve().parent
root=HERE.parents[1] if '--live' in sys.argv else HERE/'candidate'
packet=json.loads((HERE/'synthetic-input.json').read_text('utf-8'))
selected=json.loads((root/'.opencode/liuren-active.json').read_text('utf-8'))['adjudication']['model']
provider_id,model_id=selected.split('/',1)
with socket.socket() as sock:
    sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
url=f'http://127.0.0.1:{port}'
headers={'Content-Type':'application/json'}
password=os.environ.get('OPENCODE_SERVER_PASSWORD')
if password:
    user=os.environ.get('OPENCODE_SERVER_USERNAME','opencode')
    headers['Authorization']='Basic '+base64.b64encode((user+':'+password).encode()).decode()
def request(path,body=None,method=None,timeout=45):
    query='' if path.startswith('/global/') else '?'+urllib.parse.urlencode({'directory':str(root)})
    req=urllib.request.Request(url+path+query,data=json.dumps(body,ensure_ascii=False).encode() if body is not None else None,headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=timeout) as response:
        raw=response.read();return json.loads(raw) if raw else None
proc=subprocess.Popen([shutil.which('opencode'),'serve','--hostname','127.0.0.1','--port',str(port)],cwd=root,
    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
parent=None
try:
    deadline=time.monotonic()+40
    while True:
        try:
            health=request('/global/health');break
        except (OSError,ValueError):
            if time.monotonic()>deadline or proc.poll() is not None:raise RuntimeError('isolated OpenCode host failed to start')
            time.sleep(.3)
    config=request('/config',timeout=55)
    assert config.get('agent',{}).get('liuren-adjudicator'),'isolated slim config did not initialize'
    parent=request('/session',{'title':'Liuren synthetic adjudication wiring check'})['id']
    (HERE/'smoke-session.json').write_text(json.dumps({'parent':parent,'directory':str(root)},ensure_ascii=False),encoding='utf-8')
    # Both paths use native Task. The initial subtask shortcut failure was
    # traced to the now-fixed Bun import guard, not to the subtask interface.
    prompt='这是已授权的软件接线验收，不是普通起课研判。输入已由程序准备、契约已核。不要重新排盘、加载skill或方法、检索资料、整理todo。立即且仅调用一次task，subagent_type=liuren-adjudicator，description=大六壬独立裁决，不传task_id或background，prompt使用下面JSON原样序列化。收到结果后停止。不要自己回答合成占问。\n'+json.dumps(packet,ensure_ascii=False)
    pool=ThreadPoolExecutor(max_workers=1)
    parts=([{'type':'subtask','agent':'liuren-adjudicator','description':'大六壬独立裁决','prompt':json.dumps(packet,ensure_ascii=False)}]
           if '--native' in sys.argv else [{'type':'text','text':prompt}])
    future=pool.submit(request,'/session/'+parent+'/message',{
        'agent':'liuren','model':{'providerID':provider_id,'modelID':model_id},
        'parts':parts},None,610)
    print(json.dumps({'started':True,'syntheticOnly':True,'privateData':False,'provider':provider_id,'model':model_id}),flush=True)
    limit=600
    deadline=time.monotonic()+limit;last_notice=time.monotonic();toolpart=None
    while time.monotonic()<deadline:
        if future.done():
            try:future.result()
            except urllib.error.HTTPError as exc:
                detail=exc.read().decode('utf-8','replace')
                (HERE/'smoke-http-error.txt').write_text(detail,encoding='utf-8')
                raise RuntimeError('OpenCode prompt failed; diagnostic saved') from None
        messages=request('/session/'+parent+'/message',timeout=45)
        errors=[m.get('info',{}).get('error') for m in messages if m.get('info',{}).get('error')]
        if errors:
            (HERE/'smoke-provider-errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
            raise RuntimeError('Provider rejected synthetic request; saved error, no automatic model fallback')
        parts=[part for message in messages for part in message.get('parts',[]) if part.get('type')=='tool' and part.get('tool')=='task']
        done=[part for part in parts if part.get('state',{}).get('status') in ['completed','error']]
        if done:toolpart=done[-1];break
        if time.monotonic()-last_notice>20:
            errors=[m.get('info',{}).get('error') for m in messages if m.get('info',{}).get('error')]
            print(json.dumps({'waitingForSyntheticTask':True,'elapsedSeconds':round(limit-(deadline-time.monotonic())),'taskStates':[p.get('state',{}).get('status') for p in parts],'messageRoles':[m.get('info',{}).get('role') for m in messages],'errors':errors}),flush=True);last_notice=time.monotonic()
        time.sleep(1)
    if toolpart is None:raise RuntimeError('synthetic native task timed out')
    state=toolpart['state'];output=state.get('output','')
    meta=state.get('metadata',{})
    child=meta.get('sessionId') or meta.get('sessionID')
    child_messages=request('/session/'+child+'/message') if child else []
    child_summary=[]
    for message in child_messages:
        info=message.get('info',{})
        child_summary.append({k:info.get(k) for k in ['role','agent','modelID','providerID','variant','finish','error','tokens','cost'] if k in info}|{'partTypes':[p.get('type') for p in message.get('parts',[])]})
    result={'nativeTaskStatus':state.get('status'),'metadata':{k:v for k,v in meta.items() if k in ['sessionId','sessionID','liurenAdjudication']},'childMessages':child_summary,'syntheticOnly':True,'privateCaseData':False,'predictiveValidationCount':0}
    (HERE/'smoke-task-output.txt').write_text(output,encoding='utf-8')
    # Keep visible answers only; private reasoning parts are never exported.
    visible=[p.get('text','') for m in child_messages for p in m.get('parts',[]) if m.get('info',{}).get('role')=='assistant' and p.get('type')=='text']
    if visible:(HERE/'smoke-child-visible-output.txt').write_text('\n'.join(visible),encoding='utf-8')
    (HERE/'smoke-host.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)
    assert state.get('status')=='completed',state.get('error','native task failed')
    assert meta.get('liurenAdjudication',{}).get('contractChecked') is True,'contract hook did not accept native Task result'
    assert child,'child session identity not returned'
    assistants=[m['info'] for m in child_messages if m.get('info',{}).get('role')=='assistant']
    assert assistants and all(i.get('modelID')==model_id and i.get('providerID')==provider_id for i in assistants)
    user_messages=[m for m in child_messages if m.get('info',{}).get('role')=='user']
    assert len(user_messages)==1,'unexpected inherited/resumed child conversation'
    user_text=''.join(p.get('text','') for p in user_messages[0].get('parts',[]) if p.get('type')=='text')
    assert json.loads(user_text)==packet,'child did not receive exactly the neutral input packet'
    result['passed']=True;result['freshChildNeutralInputVerified']=True
    (HERE/'smoke-host.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
finally:
    if parent:
        try:request('/session/'+parent+'/abort',{},timeout=5)
        except (OSError,ValueError):pass
    proc.terminate()
    try:proc.wait(timeout=8)
    except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
    if 'pool' in globals():pool.shutdown(wait=False,cancel_futures=True)
