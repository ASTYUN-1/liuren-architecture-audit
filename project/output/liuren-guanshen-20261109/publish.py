"""Activate the prepared, source-checked local gate rule, pointer last."""
from pathlib import Path
import json, hashlib, os, shutil, subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
OLD='20261109-deterministic-tools-35';NEW='20261109-guanshen-36'
BASE=ROOT/'runtime/liuren'/OLD;R=ROOT/'runtime/liuren'/NEW
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def dump(p,d):p.write_bytes(encoded(d))
before=load(OUT/'before.json');pointer_path=ROOT/'.opencode/liuren-active.json';p=load(pointer_path)
assert p['release']==OLD
assert all(sha(BASE/rel)==digest for rel,digest in before['frozen'].items()),'Frozen35 changed'
for rel,digest in before['files'].items():
 if rel!='tools/tests/liuren-shensha.test.mjs':assert sha(ROOT/rel)==digest,'Concurrent change: '+rel
subprocess.run(['node',str(OUT/'candidate-test.mjs')],cwd=ROOT,check=True)
short='36版新增季关神S33：春丑夏辰秋未冬戌；采用规则共39条，原38条及22停用名不变。关墓阻隔、冲解及掌管仓库吉用按原段取用，寡宿同表不重复计证。仅本机，新任务绑定；原盘与旧冻结包不改。'
pending={}
cfg=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc')
cfg['agents']['liuren-adjudicator']['prompt']=(R/'references/adjudicator-prompt.md').read_text('utf-8')
pending['.opencode/oh-my-opencode-slim.jsonc']=encoded(cfg)
cfg=load(ROOT/'opencode.json')
cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace(OLD,NEW))
cfg['agent']['liuren']['prompt']+='\n'+short
pending['opencode.json']=encoded(cfg)
for rel in ['AGENTS.md','README.md','目录总索引.md']:
 s=(ROOT/rel).read_text('utf-8').replace('指向 `'+OLD+'`','指向 `'+NEW+'`').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/')
 s+='\n\n36版关神接入（'+NEW+'）：'+short+' 原文复核与回滚见output/liuren-guanshen-20261109/。\n'
 pending[rel]=s.encode('utf-8')
def proposed_sha(rel):return hashlib.sha256(pending[rel]).hexdigest() if rel in pending else sha(ROOT/rel)
p.update(release=NEW,runtime=R.relative_to(ROOT).as_posix(),previousRelease=OLD,
 backup=(OUT/'before').relative_to(ROOT).as_posix(),authoringSource=OUT.relative_to(ROOT).as_posix())
p['shenshaGateAddition']={'release':NEW,'id':'S33','name':'季关神','ruleCount':39,
 'previousRulesChanged':False,'disabledNamesChanged':False,'sourceEvidence':'references/shensha-authority-evidence.json',
 'predictiveValidationCount':0,'scope':'local-opencode-and-codex'}
for filename in ['loader-contract.json','manifest.json']:
 d=load(R/filename);d.update(release=NEW,parentRelease=OLD,authoringSource=OUT.relative_to(ROOT).as_posix())
 if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=NEW
 if filename=='loader-contract.json':d['sourceHashes']={rel:proposed_sha(rel) for rel in d['sourceHashes']}
 dump(R/filename,d)
m=load(R/'manifest.json');m['files']={rel:sha(R/rel) for rel in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(R/'manifest.json',m)
p['methodVersion']=m['version'];p['files']={rel:sha(ROOT/'.opencode/skills'/rel) for rel in p['files']}
p['workflowImplementation']={rel:proposed_sha(rel) for rel in p['workflowImplementation']}
if 'bookRetrieval' in p:
 p['bookRetrieval']['compatibleMethodRelease']=NEW
 p['bookRetrieval']['files']={rel:proposed_sha(rel) for rel in p['bookRetrieval']['files']}
pending['.opencode/liuren-active.json']=encoded(p)
after={rel:(hashlib.sha256(pending[rel]).hexdigest() if rel in pending else sha(ROOT/rel)) for rel in before['files']}
dump(OUT/'after.json',{'files':after})
written=[]
try:
 for rel,contents in pending.items():
  target=ROOT/rel;tmp=target.with_name(target.name+'.guanshen36.tmp');tmp.write_bytes(contents);os.replace(tmp,target);written.append(rel)
except Exception:
 for rel in written:shutil.copy2(OUT/'before'/rel,ROOT/rel)
 raise
assert all(sha(BASE/rel)==digest for rel,digest in before['frozen'].items())
dump(OUT/'activation.json',{'release':NEW,'previousRelease':OLD,'methodVersion':m['version'],
 'frozen35Intact':True,'original38RulesUnchanged':True,'disabled22NamesUnchanged':True,
 'rules':39,'paidModelCalls':0,'predictiveValidationCount':0,'scope':'local-opencode-and-codex'})
print('Activated',NEW)
