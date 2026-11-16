"""Bounded live tool-use probe. Credentials remain in memory, never printed/saved."""
from pathlib import Path
import os,json,subprocess,urllib.request,time,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
summary={'schema':'liuren-real-model-probe-v1','model':'deepseek-flash','scope':'真实模型根据当前工具schema调用help、life、calendar；非完整预测/非预测效果验证','credentialPersisted':False,'calls':[],'completed':False}
bridge=None
try:
 auth=json.loads((Path.home()/'.local/share/opencode/auth.json').read_text('utf-8-sig')).get('deepseek',{})
 key=auth.get('key') if auth.get('type')=='api' else os.environ.get('DEEPSEEK_API_KEY')
 base='https://api.deepseek.com/v1'
 for folder in [Path.home()/'.config/opencode',Path(os.environ['APPDATA'])/'opencode']:
  for name in ['opencode.json','opencode.jsonc']:
   f=folder/name
   if not f.is_file():continue
   try:v=json.loads(f.read_text('utf-8-sig'))
   except ValueError:continue
   options=v.get('provider',{}).get('deepseek',{}).get('options',{})
   base=options.get('baseURL',base)
   candidate=options.get('apiKey')
   if candidate and not candidate.startswith('{'):key=candidate
 if not key:raise RuntimeError('Configured DeepSeek API key unavailable; no credential requested or guessed')
 bridge=subprocess.Popen([shutil.which('node'),str(OUT/'model-tool-bridge.mjs')],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding='utf-8')
 initial=json.loads(bridge.stdout.readline());archive=initial['archive']
 question='这是工具参数验收，不作占断。已有可靠课盘archive='+json.dumps(archive,ensure_ascii=False)+'。先用liuren_tool_help查compute；然后用liuren_compute核已核虚岁25岁、男、壬午本命的行年及上神/阴神，另枚举2026-11-03至2026-11-05，Asia/Shanghai、civil-midnight的日期。随后查packet帮助，说明记录编号如何避免事实/争点冲突，以及神煞观察kind如何填。不保存packet、不派裁决、不输出预测。最多8次工具调用。'
 messages=[{'role':'system','content':'你在进行本机大六壬工具调用验收。按实际工具schema及返回说明调用，不猜字段；程序返回不证明预测效果。'},{'role':'user','content':question}]
 deadline=time.monotonic()+180
 for turn in range(7):
  if time.monotonic()>deadline:raise RuntimeError('bounded probe deadline reached')
  body={'model':'deepseek-flash','messages':messages,'tools':initial['tools'],'stream':False,'max_tokens':2500,'reasoning_effort':'high'}
  req=urllib.request.Request(base.rstrip('/')+'/chat/completions',data=json.dumps(body,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=min(60,max(1,deadline-time.monotonic()))) as r:response=json.load(r)
  except urllib.error.HTTPError as e:raise RuntimeError('provider HTTP '+str(e.code)) from None
  message=response['choices'][0]['message'];messages.append(message)
  calls=message.get('tool_calls',[])
  if not calls:
   summary['finalText']=message.get('content','');break
  for call in calls:
   if len(summary['calls'])>=8:raise RuntimeError('tool call budget reached')
   name=call['function']['name'];args=json.loads(call['function']['arguments'])
   bridge.stdin.write(json.dumps({'name':name,'args':args},ensure_ascii=False)+'\n');bridge.stdin.flush()
   result=json.loads(bridge.stdout.readline())
   # Store operation names/outcomes only, never the credential or full requests.
   summary['calls'].append({'tool':name,'action':args.get('action'),'topic':args.get('topic'),'ok':result['ok'],**({'error':result.get('error')} if not result['ok'] else {})})
   messages.append({'role':'tool','tool_call_id':call['id'],'content':result.get('output',result.get('error'))})
   if not result['ok']:raise RuntimeError('real model tool argument error')
 needed={('liuren_tool_help',None,'compute'),('liuren_tool_help',None,'packet'),('liuren_compute','life',None),('liuren_compute','calendar',None)}
 summary['completed']=needed.issubset({(x['tool'],x.get('action'),x.get('topic')) for x in summary['calls']}) and bool(summary.get('finalText'))
except Exception as e:summary['error']=type(e).__name__+': '+str(e)
finally:
 if bridge is not None:bridge.terminate();bridge.wait(timeout=5)
 (OUT/'real-model-probe.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:summary.get(k) for k in ['completed','calls','error']},ensure_ascii=False))
