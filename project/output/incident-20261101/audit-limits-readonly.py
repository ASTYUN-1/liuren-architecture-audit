"""Read deployed constraints and safe configuration only; no customer content/secrets."""
import hashlib,json,os,subprocess,datetime,urllib.request
from pathlib import Path
def run(args):
 r=subprocess.run(args,text=True,capture_output=True,timeout=25)
 return {'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
root=Path('/opt/wenheng/current').resolve()
digest=hashlib.sha256();count=0
for p in sorted((root/'src').rglob('*')):
 if p.is_file():
  digest.update(p.relative_to(root).as_posix().encode()+b'\0'+hashlib.sha256(p.read_bytes()).digest());count+=1
print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'release':str(root),'sourceFiles':count,'sourceFingerprint':digest.hexdigest(),'buildId':(root/'.next/BUILD_ID').read_text().strip()}))
for svc in ['wenheng-web','wenheng-worker']:
 print(json.dumps({'service':svc,**run(['systemctl','show',svc,'-p','ActiveState','-p','MainPID','-p','WorkingDirectory','-p','MemoryMax','-p','TasksMax'])}))
 pid=subprocess.check_output(['systemctl','show',svc,'-p','MainPID','--value']).decode().strip()
 env={}
 for pair in Path('/proc/'+pid+'/environ').read_bytes().split(b'\0'):
  k,sep,v=pair.partition(b'=')
  if k.decode(errors='ignore') in ['WENHENG_WORKER_CONCURRENCY','ADMIN_REQUIRE_2FA','WENHENG_PUBLIC_UI_ENABLED','WENHENG_LIUREN_PROTOCOL','WENHENG_PROJECT_ROOT','PORT','NODE_ENV']:env[k.decode()]=v.decode()
 print(json.dumps({'serviceSafeEnv':svc,'values':env,'cwd':os.readlink('/proc/'+pid+'/cwd')}))
sql="""BEGIN READ ONLY; SET LOCAL statement_timeout='10s';
SELECT key,jsonb_build_object('aiEnabled',value->'aiEnabled','mode',value->'mode','paymentsEnabled',value->'paymentsEnabled','topupEnabled',value->'topupEnabled','humanEnabled',value->'humanEnabled','serviceNotificationsEnabled',value->'serviceNotificationsEnabled','nbzhifuEnabled',value->'nbzhifuEnabled','nbzhifuPublicEnabled',value->'nbzhifuPublicEnabled','model',value->'model') FROM service_settings WHERE key IN ('runtime','points');
SELECT 'queue',jsonb_build_object('name',name,'expireSeconds',expire_seconds,'retryLimit',retry_limit,'policy',policy) FROM pgboss.queue WHERE name='wenheng-interpretation';
SELECT 'tasks',status,count(*) FROM tasks GROUP BY status;
COMMIT;"""
print(json.dumps({'safeSettings':run(['sudo','-u','postgres','psql','-X','-At','-d','wenheng','-v','ON_ERROR_STOP=1','-c',sql])}))
with urllib.request.urlopen('http://127.0.0.1:3100/api/status',timeout=10) as r:
 d=json.load(r)['data'];print(json.dumps({'status':{k:d.get(k) for k in ['aiEnabled','workerOnline','modelConfigured','paymentsEnabled','aggregatePaymentsEnabled','resultNotificationsEnabled','aiUnavailableReason','paymentUnavailableReason']}}))
print(json.dumps({'memory':run(['free','-m']),'disk':run(['df','-m','/opt/wenheng'])}))
