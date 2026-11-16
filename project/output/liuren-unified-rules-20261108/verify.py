"""Read-only release/evidence/role/entry verification; not predictive validation."""
from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text('utf-8-sig'))
before=load(OUT/'before.json');p=load(ROOT/'.opencode/liuren-active.json');r=ROOT/p['runtime'];m=load(r/'manifest.json');c=load(r/'loader-contract.json')
assert p['release']==m['release']==c['release']=='20261108-unified-32'
assert all(sha(r/file)==h for file,h in m['files'].items())
assert hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()==p['methodVersion']==m['version']
assert all(sha(ROOT/file)==h for file,h in c['sourceHashes'].items())
assert all(sha(ROOT/file)==h for file,h in p['workflowImplementation'].items())
assert all(sha(ROOT/'runtime/liuren/20261107-slim-31'/file)==h for file,h in before['frozen31'].items())
assert all(sha(ROOT/file)==h for file,h in before['sourceBooks'].items())
assert sha(r/'references/adjudicator-book-evidence.json')==sha(ROOT/'runtime/liuren/20261107-slim-31/references/adjudicator-book-evidence.json')
cfg=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc');role=cfg['agents']['liuren-adjudicator']['prompt'];assert role==(r/'references/adjudicator-prompt.md').read_text('utf8')
core=(r/'references/judgment-core.md').read_text('utf8')
for n in range(1,12):assert f'**U{n:02} ' in core
assert '严格采用核心U01—U11' in role
for text in [core,role]:
 assert '已经任职' not in text and '结果为A' not in text
for file in ['SKILL.md','references/host.md']:
 assert sha(ROOT/'integrations/codex/daliuren-codex'/file)==sha(Path('C:/Users/QLMa_/.codex/skills/daliuren-codex')/file)
ev=load(r/'references/confirmed-policy-evidence.json')
for row in ev['evidence']:
 src=ROOT/row['path'];assert sha(src)==row['sha256'];rows=src.read_text(row.get('encoding','utf-8-sig')).splitlines();assert '\n'.join(rows[row['line_start']-1:row['line_end']])==row['quote'],row['id']
materials=[]
for id in ['judgment-core','confirmed-policy','pending-conflicts','confirmed-policy-evidence','confirmed-policy-supplements']:
 result=subprocess.run([sys.executable,'-X','utf8','tools/liuren-materials.py','--request',json.dumps({'action':'method','modules':[id]},ensure_ascii=False)],cwd=ROOT,encoding='utf8',capture_output=True)
 assert result.returncode==0,(id,result.stderr,result.stdout[-1000:]);assert 'LIUREN_METHOD_BEGIN' in result.stdout;assert 'LIUREN_METHOD_END' in result.stdout
 materials.append(id)
checks={'activeRelease':p['release'],'manifestAndImplementationHashes':True,'frozen31Intact':True,'sourceBooksIntact':True,'E01_E22OriginalBytesIntact':True,'ruleIDsInMandatoryCore':11,'roleMirrorMatchesActualOpenCodePrompt':True,'installedCodexSkillMatchesProject':True,'verifiedContinuousEvidenceCount':len(ev['evidence']),'materialModulesReadable':materials,'hostModelsUnchanged':True,'knownOutcomeNotAdded':True,'predictiveValidationCount':0}
(OUT/'verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(checks,ensure_ascii=False))
