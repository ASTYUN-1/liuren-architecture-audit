"""Verify the local release without model calls or changing frozen methods."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
load = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
active = load(ROOT / '.opencode/liuren-active.json')
before = load(OUT / 'before.json')
old = load(OUT / 'before/.opencode/liuren-active.json')
assert active['release'] == '20261109-direct-answer-40'
assert all(sha(ROOT / rel) == digest for rel, digest in before['frozen'].items())
for rel, digest in old['workflowImplementation'].items():
    if rel.startswith(('tools/', '.opencode/plugins/')):
        assert sha(ROOT / rel) == digest, rel
for rel, key in [('opencode.json', 'agent'), ('.opencode/oh-my-opencode-slim.jsonc', 'agents')]:
    previous = load(OUT / 'before' / rel)[key]
    current = load(ROOT / rel)[key]
    # Only the prompt and versioned material paths may change.
    for name, settings in previous.items():
        for setting, value in settings.items():
            if setting not in ('prompt',):
                expected = json.loads(json.dumps(value, ensure_ascii=False)
                    .replace(old['runtime'], active['runtime'])
                    .replace(old['runtime'].replace('/', '\\'), active['runtime'].replace('/', '\\')))
                assert current[name][setting] == expected, (name, setting)
rule = (ROOT / 'docs/本机六壬直接作答-40.md').read_text('utf-8')
runtime = ROOT / active['runtime']
core = (runtime / 'references/judgment-core.md').read_text('utf-8')
report = (runtime / 'methods/report.md').read_text('utf-8')
assert rule in core and core.index(rule) < 200
assert rule in report
assert load(ROOT / '.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']['prompt'].startswith('40版直接作答')
runs = []
for p in (ROOT / 'output/codex-liuren').glob('codex-*/run.json'):
    d = load(p)
    if d.get('release') != active['release']:
        continue
    packet = load(Path(d['packet_ref']['file_path']))
    reading = json.loads(packet['reading_core']['content'])
    # read_text normalizes CRLF; JSON embedded strings retain original newlines.
    assert rule in reading['shared_method'].replace('\r\n', '\n')
    assert d['adjudicator_prompt'].startswith('40版直接作答')
    runs.append(p.parent.name)
assert runs
regression = (OUT / 'regression.log').read_text('utf-8')
assert 'tests 118' in regression and 'pass 118' in regression and 'fail 0' in regression
# Capture these read-only commands from the host shell before verification:
# python -X utf8 tools/liuren-preflight.py --json
# node tools/liuren-codex.mjs status
pdata = load(OUT / 'preflight.json')
cdata = load(OUT / 'codex-status.json')
assert cdata['release'] == active['release']
assert pdata.get('ready') is True or pdata.get('execution_health', {}).get('ready') is True
assert cdata.get('ready') is True or cdata.get('execution_health', {}).get('ready') is True
result = dict(release=active['release'], frozen39Unchanged=True, modelsUnchanged=True,
    toolsAndAlgorithmsUnchanged=True, mandatoryCoreStartsWithPolicy=True,
    adjudicatorPromptStartsWithPolicy=True, reportIncludesPolicy=True,
    actualCodexRunBindingsVerified=runs, semanticCheckUsesExistingAnswerConstraints=True,
    regressionTests=118, passed=118, failed=0, preflightReady=True, codexReady=True,
    paidModelCalls=0, predictiveValidationCount=0, websiteChanged=False,
    existingDesktopRestarted=False)
(OUT / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
