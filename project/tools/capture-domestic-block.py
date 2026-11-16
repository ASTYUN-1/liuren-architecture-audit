"""Persist public failure evidence; never read user records or credentials."""
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'web/test-results/domestic-entry'
out.mkdir(parents=True,exist_ok=True)
def fetch(url,direct=False):
    cmd=['curl.exe','--silent','--show-error','--max-time','20','--write-out','\n%{http_code}',url]
    if direct:cmd[1:1]=['--noproxy','*']
    r=subprocess.run(cmd,capture_output=True,encoding='utf-8',errors='replace')
    body,status=r.stdout.rsplit('\n',1) if '\n' in r.stdout else (r.stdout,'000')
    return {'url':url,'exitCode':r.returncode,'status':status,'body':body,'error':r.stderr.strip()}
evidence={'checkedAt':datetime.now(timezone.utc).isoformat(),
    'mainlandHttp':fetch('http://cn-wen.qiluhub.com/',True),
    'mainlandHttps':fetch('https://cn-wen.qiluhub.com/api/status',True),
    'hongKongHttps':fetch('https://wen.qiluhub.com/api/status')}
assert evidence['mainlandHttp']['status']=='403'
assert 'Non-compliance ICP Filing' in evidence['mainlandHttp']['body']
assert evidence['hongKongHttps']['status']=='200'
(out/'provider-block-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({**evidence,'mainlandHttp':{**evidence['mainlandHttp'],'body':'Aliyun Non-compliance ICP Filing block page'}},ensure_ascii=False,indent=2))
