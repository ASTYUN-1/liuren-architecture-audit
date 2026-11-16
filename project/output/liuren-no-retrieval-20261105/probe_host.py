"""Inspect normal native discovery; retain only selected non-secret facts."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
pointer = json.loads((ROOT / '.opencode/liuren-active.json').read_text('utf-8'))
env = dict(os.environ)
env.update(OPENCODE_DISABLE_MODELS_FETCH='true', OPENCODE_DISABLE_AUTOUPDATE='true',
           OPENCODE_DISABLE_DEFAULT_PLUGINS='1', OPENCODE_DISABLE_FILEWATCHER='true')
for name in ('OPENCODE_CONFIG','OPENCODE_CONFIG_CONTENT','OPENCODE_CONFIG_DIR','OPENCODE_DISABLE_PROJECT_CONFIG'):
    env.pop(name, None)
checks = []
for command in ('config', 'skill'):
    proc = subprocess.run([shutil.which('opencode'), 'debug', command], cwd=ROOT, env=env,
                          capture_output=True, encoding='utf-8', errors='replace', timeout=55)
    if proc.returncode: raise RuntimeError('native discovery failed: ' + command + ', code=' + str(proc.returncode))
    value = json.loads(proc.stdout)
    if command == 'config':
        actual = value['agent']['liuren']['prompt']
        expected = json.loads((ROOT / 'opencode.json').read_text('utf-8'))['agent']['liuren']['prompt']
        assert actual == expected and '依问定所主' in actual and '再最终裁决' in actual
        assert value.get('default_agent') == 'liuren'
        checks.append(dict(check='resolved-config', promptMatches=True, defaultAgent='liuren'))
    else:
        rows = value if isinstance(value, list) else value['skills']
        names = set(pointer['activeSkillNames'])
        business = [row for row in rows if row.get('name') in names or row.get('name') == 'liuren-tuiming']
        assert len(business) == 3 and {r['name'] for r in business} == names
        safe_rows = []
        for row in business:
            path = Path(row.get('location') or row.get('path') or row.get('file')).resolve()
            expected = ROOT / '.opencode/skills/liuren' / row['name'] / 'SKILL.md'
            assert path == expected.resolve()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            assert digest == pointer['files']['liuren/' + row['name'] + '/SKILL.md']
            safe_rows.append(dict(name=row['name'], path=str(path), sha256=digest))
        checks.append(dict(check='resolved-three-skills', skills=safe_rows))
report = dict(ok=True, release=pointer['release'], checks=checks, modelCalls=0,
              normalLocalAndGlobalDiscovery=True, defaultPluginsDisabledForProbe=True,
              rawConfigRetained=False, actualModelCompliance='unverified')
(HERE / 'host-discovery.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(ok=True, release=pointer['release'], checks=len(checks), modelCalls=0)))
