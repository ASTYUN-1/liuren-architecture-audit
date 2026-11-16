"""Public, unauthenticated smoke checks. No account or paid AI calls."""
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

root=Path(__file__).resolve().parents[1]
out=root/'web/test-results/domestic-entry'
out.mkdir(parents=True,exist_ok=True)
receipt={'checkedAt':datetime.now(timezone.utc).isoformat(),'hosts':[]}
def request(origin,path='/',method='GET',body=None,source=None):
    command=['curl.exe','--silent','--show-error','--max-time','25','--retry','1','--write-out','\n%{http_code}',origin+path]
    if origin=='https://cn-wen.qiluhub.com': command[1:1]=['--noproxy','*']
    if method!='GET':
        command+=['-X',method,'-H','Content-Type: application/json','-H','Origin: '+(source or origin),'--data-binary',json.dumps(body,ensure_ascii=False)]
    result=subprocess.run(command,capture_output=True,encoding='utf-8',check=True)
    content,status=result.stdout.rsplit('\n',1)
    return int(status),content

for origin in ['https://cn-wen.qiluhub.com','https://wen.qiluhub.com']:
    status,html=request(origin)
    assert status==200 and '问衡' in html
    title=re.search(r'<title>([^<]+)',html)
    status,body=request(origin,'/api/status')
    assert status==200
    service=json.loads(body)['data']
    assert service['workerOnline'] and service['aiEnabled'] and service['smtpConfigured']
    assert not service['paymentsEnabled']
    assert request(origin,'/api/admin/users')[0]==401
    assert request(origin,'/api/cases','POST',{})[0]==401
    assert request(origin,'/api/cases','POST',{},'https://untrusted.invalid')[0]==403
    assert request(origin,'/api/auth/sign-in/email','POST',{'email':'invalid','password':'[REDACTED_CREDENTIAL]'})[0] in [400,422]
    assert request(origin,'/api/auth/sign-in/email','POST',{'email':'invalid','password':'[REDACTED_CREDENTIAL]'},'https://untrusted.invalid')[0]==403
    chart_input={'method':'time','date':'2026-10-15','time':'13:04','calendar':'solar','leapMonth':False,'pillars':{'year':'丙午','month':'戌','day':'壬戌','hour':'未','monthGeneral':'辰'},'rules':{'guiren':'甲戊庚牛羊','zhouye':'自动选择','shehai':'孟仲季','yuejiang':'中气换将'},'participants':[{'role':'本人','gender':'male','birthYear':1990}]}
    status,body=request(origin,'/api/chart/professional','POST',{'input':chart_input})
    assert status==200,(origin,status,body[:200])
    assert len(json.loads(body)['data']['chart']['palaces'])==12
    receipt['hosts'].append({'origin':origin,'homepage':200,'title':title.group(1) if title else None,'service':service,'anonymousChartPalaces':12,'anonymousAdmin':401,'anonymousCase':401,'foreignOrigin':403,'authSecondaryOriginAccepted':True})

(out/'public-smoke.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
