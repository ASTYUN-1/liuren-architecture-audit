"""Read local OpenCode inventory. Never emit credentials or endpoint values."""
from pathlib import Path
import json,shutil,subprocess,os
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def parse_jsonc(s):
 def clean(s,trailing=False):
  out=[];i=0;quoted=False;escaped=False
  while i<len(s):
   c=s[i]
   if quoted:
    out.append(c)
    if escaped:escaped=False
    elif c=='\\':escaped=True
    elif c=='"':quoted=False
    i+=1;continue
   if c=='"':quoted=True;out.append(c);i+=1;continue
   if not trailing and s[i:i+2]=='//':
    j=s.find('\n',i);i=len(s) if j<0 else j;continue
   if not trailing and s[i:i+2]=='/*':
    j=s.find('*/',i+2)
    if j<0:raise ValueError('unclosed JSONC comment')
    i=j+2;continue
   if trailing and c==',':
    j=i+1
    while j<len(s) and s[j].isspace():j+=1
    if j<len(s) and s[j] in '}]':i+=1;continue
   out.append(c);i+=1
  return ''.join(out)
 return json.loads(clean(clean(s),True))
def config_summary(p):
 d=parse_jsonc(p.read_text('utf-8-sig'));result={}
 for key in ['plugin','default_agent','disabled_mcps','disabled_agents','instructions','tool_output','enabled_providers','disabled_providers']:
  if key in d:result[key]=d[key]
 result['mcp']={name:{'type':v.get('type'),'enabled':v.get('enabled',True),'commandExecutable':v.get('command',[None])[0],'commandFound':bool(shutil.which(v['command'][0])) if v.get('command') else None,'timeout':v.get('timeout'),'hasEnvironment':bool(v.get('environment')),'hasHeaders':bool(v.get('headers'))} for name,v in d.get('mcp',{}).items() if isinstance(v,dict)}
 result['providers']={name:{'npm':v.get('npm'),'models':{mid:{k:m[k] for k in ['limit','reasoning','tool_call','variants'] if k in m} for mid,m in v.get('models',{}).items()},'hasOptions':bool(v.get('options'))} for name,v in d.get('provider',{}).items()}
 result['agents']={name:{k:v[k] for k in ['model','variant','mode','hidden','disable'] if k in v} for name,v in d.get('agent',d.get('agents',{})).items() if isinstance(v,dict)}
 return result
def main():
 report={'configs':{},'versions':{},'globalFiles':[],'projectPlugins':[],'projectTools':[]}
 config_root=Path.home()/'.config/opencode'
 report['globalFiles']=[p.name for p in config_root.iterdir() if p.is_file()]
 for p in [ROOT/'opencode.json',ROOT/'.opencode/oh-my-opencode-slim.jsonc',config_root/'opencode.json',config_root/'opencode.jsonc',config_root/'oh-my-opencode-slim.json',config_root/'oh-my-opencode-slim.jsonc']:
  if p.exists():report['configs'][str(p)]=config_summary(p)
 for name,p in {'projectSDK':ROOT/'.opencode/node_modules/@opencode-ai/plugin/package.json','globalSDK':config_root/'node_modules/@opencode-ai/plugin/package.json','slim':Path.home()/'.cache/opencode/packages/oh-my-opencode-slim/node_modules/oh-my-opencode-slim/package.json'}.items():
  if p.exists():d=json.loads(p.read_text('utf-8'));report['versions'][name]={'name':d['name'],'version':d['version']}
 report['projectPlugins']=[p.name for p in (ROOT/'.opencode/plugins').glob('*') if p.is_file()]
 report['projectTools']=[p.name for p in (ROOT/'.opencode/tools').glob('*') if p.is_file()]
 report['environmentOverrideNames']=[k for k in os.environ if k.startswith('OPENCODE_')]
 cli=Path.home()/'scoop/apps/opencode/current/opencode.exe'
 result=subprocess.run([str(cli),'--version'],capture_output=True,text=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
 report['versions']['cli']=result.stdout.strip()
 (OUT/'local-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
