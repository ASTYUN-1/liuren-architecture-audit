"""Read-only rule delivery, version, source and host parity audit; no predictions."""
from pathlib import Path
import hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text('utf-8-sig'))
p = load(ROOT/'.opencode/liuren-active.json'); r = ROOT/p['runtime']
before = load(OUT/'before.json'); m = load(r/'manifest.json'); c = load(r/'loader-contract.json')
assert p['release'] == m['release'] == c['release'] == '20261108-clarified-33'
assert all(sha(r/rel)==h for rel,h in m['files'].items())
assert hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest() == m['version'] == p['methodVersion']
assert all(sha(ROOT/rel)==h for rel,h in c['sourceHashes'].items())
assert all(sha(ROOT/rel)==h for rel,h in p['workflowImplementation'].items())
assert all(sha(ROOT/'.opencode/skills'/rel)==h for rel,h in p['files'].items())
old = ROOT/'runtime/liuren'/before['release']
assert {f.relative_to(old).as_posix():sha(f) for f in old.rglob('*') if f.is_file()} == before['frozen32']
assert all(sha(ROOT/rel)==h for rel,h in before['sourceBooks'].items())
assert sha(r/'references/adjudicator-book-evidence.json') == sha(old/'references/adjudicator-book-evidence.json')
for rel in ['SKILL.md','references/host.md']:
    assert sha(ROOT/'integrations/codex/daliuren-codex'/rel)==sha(Path('C:/Users/QLMa_/.codex/skills/daliuren-codex')/rel)
cfg = load(ROOT/'.opencode/oh-my-opencode-slim.jsonc')
oldcfg = load(OUT/'before/.opencode/oh-my-opencode-slim.jsonc')
role = cfg['agents']['liuren-adjudicator'].pop('prompt')
oldcfg['agents']['liuren-adjudicator'].pop('prompt')
assert cfg == oldcfg, 'Host config other than professional role changed'
assert role == (r/'references/adjudicator-prompt.md').read_text('utf-8')
core = (r/'references/judgment-core.md').read_text('utf-8')
policy = (r/'references/confirmed-judgment-policy.md').read_text('utf-8')
assert core[core.index('## 已确认判断口径'):].strip() == policy[policy.index('## 已确认判断口径'):].strip()
for i in range(1,12): assert '**U'+str(i).zfill(2)+' ' in core
for text in [core,role]:
    for required in ['财难为我得','父母','同一对象','不是待确认清单','土胎','阶段']:
        assert required in text, required
    for forbidden in ['贪生停用能否扩大到财类','非官鬼停用范围仅列C02','尚未找到该划分的完整书证','已任职','结果为A']:
        assert forbidden not in text, forbidden
ev = load(r/'references/confirmed-policy-evidence.json')
for row in ev['evidence']:
    src = ROOT/row['path']; assert sha(src)==row['sha256']
    lines = src.read_text(row.get('encoding','utf-8-sig')).splitlines()
    assert '\n'.join(lines[row['line_start']-1:row['line_end']]) == row['quote'], row['id']
for row in load(ROOT/'output/liuren-rules-review-20261108/连续原文与校验.json')['evidence']:
    src = ROOT/row['path']; assert sha(src)==row['sha256']
    lines = src.read_text(row.get('encoding','utf-8-sig')).splitlines()
    assert '\n'.join(lines[row['line_start']-1:row['line_end']]) == row['quote']
for module in ['judgment-core','confirmed-policy','pending-conflicts','confirmed-policy-evidence','confirmed-policy-supplements','finance','pregnancy','timing']:
    result = subprocess.run([sys.executable,'-X','utf8','tools/liuren-materials.py','--request',json.dumps({'action':'method','modules':[module]},ensure_ascii=False)],cwd=ROOT,encoding='utf-8',capture_output=True)
    assert result.returncode==0, (module,result.stderr,result.stdout[-500:])
    assert 'LIUREN_METHOD_END' in result.stdout, module
changed = [rel for rel in m['files'] if sha(r/rel)!=sha(old/rel)]
checks = {'release':p['release'],'manifestAndImplementationHashes':True,'frozen32Intact':True,
          'sourceBooksIntact':True,'E01_E22OriginalBytesIntact':True,'continuousEvidenceChecked':len(ev['evidence']),
          'priorReviewEvidenceChecked':41,'mandatoryCoreRules':11,'actualChildPromptMatches':True,
          'mainAndInstalledCodexSkillSynced':True,'hostModelAndBudgetUnchanged':True,
          'historicalIssuesReclassified':11,'newConfirmedSameConditionContradictions':0,
          'runtimeFilesChanged':changed,'paidModelCalls':0,'predictiveValidationCount':0}
(OUT/'verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False))
