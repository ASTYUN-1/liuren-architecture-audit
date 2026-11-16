"""Seal, verify and activate the local release, with byte-exact rollback."""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAND = HERE / 'candidate'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def readj(path): return json.loads(path.read_text('utf-8-sig'))
def jb(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
def save(path, value): path.write_bytes(jb(value))
def safe(base, rel):
    path = (base / rel).resolve()
    if Path(rel).is_absolute() or '..' in Path(rel).parts or not path.is_relative_to(base.resolve()):
        raise ValueError('unsafe path: ' + rel)
    return path
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def check_files(base, values):
    for rel, digest in values.items():
        path = safe(base, rel)
        if not path.is_file() or path.is_symlink() or sha(path.read_bytes()) != digest:
            raise ValueError('file identity mismatch: ' + str(path))

def seal():
    plan = readj(HERE / 'switch-plan.json')
    if safe(ROOT, plan['runtime']).exists(): raise ValueError('release already exists; refuse reseal')
    package = safe(CAND, plan['runtime'])
    for rel, before, after, reason in [
        ('references/daliuren-shensha.md', '同一支兼多标签归并为相关信息，不设“三煞无疑”。',
         '同一支兼多标签保留各自职责和有条件的类聚意义，不按名称投票，也不为去重拆散有效组合；不设“三煞无疑”。',
         'retain effective same-branch combinations while rejecting label voting'),
        ('methods/liqi.md', '## 本机候选总则：理气贯穿，因问定侧重',
         '## 本机总则：理气贯穿，因问定侧重', 'remove inherited candidate heading from the published method')]:
        path = package / rel
        text = path.read_text('utf-8')
        if text.count(before) == 1:
            path.write_text(text.replace(before, after, 1), encoding='utf-8', newline='\n')
        elif text.count(after) != 1:
            raise ValueError('missing seal edit anchor: ' + rel)
        row = dict(path=rel, before=sha((ROOT / plan['previousRuntime'] / rel).read_bytes()),
                   after=sha(path.read_bytes()), reason=reason)
        matching = [x for x in plan['packageChanges'] if x['path'] == rel]
        if matching:
            matching[-1]['after'] = row['after']
            if reason not in matching[-1]['reason']: matching[-1]['reason'] += '; ' + reason
        else: plan['packageChanges'].append(row)
        revision = readj(package / 'adjudication-revision-map.json')
        old = [x for x in revision['changes'] if x['path'] == rel]
        if old:
            old[-1]['after'] = row['after']
            if reason not in old[-1]['reason']: old[-1]['reason'] += '; ' + reason
        else: revision['changes'].append(row)
        save(package / 'adjudication-revision-map.json', revision)
    # Source disputes must be read before liqi is pulled forward by shenjiang-use.
    route = readj(package / 'reading-route.json')
    route['conditional']['liqi-sources']['beforeRequired'] = 'positioning'
    save(package / 'reading-route.json', route)
    primary_path = CAND / '.opencode/skills/liuren/daliuren/SKILL.md'
    text = primary_path.read_text('utf-8').replace(
        '| liqi-sources | 所采用方法存在来源或口径分歧 | 阶段1，liqi前 |',
        '| liqi-sources | 所采用方法存在来源或口径分歧 | 阶段1，positioning前，先于可能提前加载的liqi |')
    primary_path.write_text(text, encoding='utf-8', newline='\n')
    (package / 'entry.md').write_bytes(primary_path.read_bytes())
    revision = readj(package / 'adjudication-revision-map.json')
    for rel, reason in [('reading-route.json', 'source-dispute reference precedes early liqi dependency'),
                         ('entry.md', 'align source-dispute conditional route with dependency order')]:
        digest = sha((package / rel).read_bytes())
        for rows in (plan['packageChanges'], revision['changes']):
            matches = [x for x in rows if x['path'] == rel]
            if matches:
                matches[-1]['after'] = digest
                if reason not in matches[-1]['reason']: matches[-1]['reason'] += '; ' + reason
            else: rows.append(dict(path=rel, before=sha((ROOT/plan['previousRuntime']/rel).read_bytes()), after=digest, reason=reason))
    save(package / 'adjudication-revision-map.json', revision)
    manifest = readj(package / 'manifest.json')
    # The route trigger text and required list remain unchanged.
    manifest['files'] = {p.relative_to(package).as_posix(): sha(p.read_bytes())
                         for p in sorted(package.rglob('*')) if p.is_file() and p.name != 'manifest.json'}
    manifest['version'] = sha(json.dumps(manifest['files'], sort_keys=True).encode())
    save(package / 'manifest.json', manifest)
    pointer_path = CAND / '.opencode/liuren-active.json'
    pointer = readj(pointer_path)
    pointer['methodVersion'] = manifest['version']
    pointer['files']['liuren/daliuren/SKILL.md'] = sha(primary_path.read_bytes())
    save(pointer_path, pointer)
    plan['methodVersion'] = manifest['version']
    for row in plan['externalFiles']: row['after'] = sha((CAND / row['path']).read_bytes())
    plan['newRuntimeFiles'] = {p.relative_to(package).as_posix(): sha(p.read_bytes())
                               for p in package.rglob('*') if p.is_file()}
    save(HERE / 'switch-plan.json', plan)
    return dict(resealed=True, version=manifest['version'])

def verify(live=False):
    plan = readj(HERE / 'switch-plan.json')
    base = ROOT if live else CAND
    package = safe(base, plan['runtime'])
    manifest = readj(package / 'manifest.json')
    old = readj(ROOT / plan['previousRuntime'] / 'manifest.json')
    check_files(ROOT, plan['oldRuntimeHashes'])
    check_files(package, plan['newRuntimeFiles'])
    check_files(package, manifest['files'])
    assert manifest['version'] == sha(json.dumps(manifest['files'], sort_keys=True).encode())
    pointer = readj(base / '.opencode/liuren-active.json')
    assert pointer['methodVersion'] == plan['methodVersion'] == manifest['version']
    assert pointer['release'] == manifest['release'] == plan['release']
    assert pointer['runtime'] == plan['runtime']
    for row in plan['externalFiles']:
        assert sha((CAND / row['path']).read_bytes()) == row['after'], row['path']
        assert sha((ROOT / row['path']).read_bytes()) == row['after' if live else 'before'], row['path']
    for key in ('modules', 'required', 'conditional', 'domains', 'procedureFiles'):
        assert manifest[key] == old[key], key
    route = readj(package / 'reading-route.json')
    old_route = readj(ROOT / plan['previousRuntime'] / 'reading-route.json')
    assert route['legacyCoverage'] == old_route['legacyCoverage']
    expected_conditions = copy.deepcopy(old_route['conditional'])
    expected_conditions['liqi-sources']['beforeRequired'] = 'positioning'
    assert route['conditional'] == expected_conditions
    assert [s['required'] for s in route['stages']] == [s['required'] for s in old_route['stages']]
    assert len(manifest['modules']) == 59 and len(manifest['required']) == 14 and len(manifest['domains']) == 16
    loader = load('release_methods', ROOT / 'tools/load-liuren-methods.py')
    if live:
        actual_runtime, actual_manifest = loader.active(ROOT)
        assert actual_runtime == package
    routed = copy.deepcopy(manifest)
    routed['readingRoute'] = route
    for key in manifest['modules']: loader.content(package, manifest, key)
    plans = 0
    for domain, timing, nianming in itertools.product(manifest['domains'], (False, True), (False, True)):
        keys = loader.plan(routed, [domain], timing=timing, nianming=nianming)
        assert len(keys) == len(set(keys)) and set(manifest['required']).issubset(keys)
        assert keys.index('positioning') < keys.index(domain) < keys.index('structure')
        if timing: assert keys.index('adjudication') < keys.index('timing') < keys.index('evidence')
        if nianming: assert keys.index('nianming') < keys.index('class-mapping')
        assert keys.index('adjudication') < keys.index('evidence') < keys.index('report')
        plans += 1
    all_conditions = list(route['conditional'])
    keys = loader.plan(routed, manifest['domains'], extras=all_conditions)
    for key, condition in route['conditional'].items():
        assert keys.index(key) < keys.index(condition['beforeRequired']), key
    for key, item in manifest['modules'].items():
        if key in keys:
            for dep in item['requires']: assert keys.index(dep) < keys.index(key)
    combinations = 0
    for flags in itertools.product((False, True), repeat=len(all_conditions)):
        selected = [key for key, flag in zip(all_conditions, flags) if flag]
        sequence = loader.plan(routed, ['exam'], extras=selected)
        assert set(selected).issubset(sequence) and len(sequence) == len(set(sequence))
        for key in selected:
            assert sequence.index(key) < sequence.index(route['conditional'][key]['beforeRequired'])
        if 'liqi-sources' in selected:
            assert sequence.index('liqi-sources') < sequence.index('liqi')
        combinations += 1
    policy = readj(package / 'references/shensha-policy.json')
    old_policy = readj(ROOT / plan['previousRuntime'] / 'references/shensha-policy.json')
    assert policy.pop('release') == plan['release']
    old_policy.pop('release')
    assert policy == old_policy
    source_map = readj(package / 'source-read-map.json')
    old_map = readj(ROOT / plan['previousRuntime'] / 'source-read-map.json')
    expected = {k.replace(plan['previousRuntime']+'/', plan['runtime']+'/'):v for k,v in old_map['aliases'].items()}
    assert source_map['aliases'] == expected
    for item in source_map['aliases'].values(): assert sha((ROOT / item['path']).read_bytes()) == item['sha256']
    study = ROOT / 'output/liuren-expert-adjudication-study-20261105'
    for source, target in [('source-evidence.json', 'expert-adjudication-sources.json'),
                           ('所核连续原文.md', 'expert-adjudication-excerpts.md')]:
        assert (study/source).read_bytes() == (package/'references'/target).read_bytes()
    evidence = readj(package / 'references/expert-adjudication-sources.json')
    passages = evidence['passages']
    for row in passages:
        raw = (ROOT / row['path']).read_bytes()
        assert sha(raw) == row['sha256']
        lines = raw.decode(row['encoding']).replace('\r\n', '\n').split('\n')
        assert '\n'.join(lines[row['lf_start']-1:row['lf_end']]) == row['quote'], row['id']
    assert len(passages) == 34
    # New navigation links must resolve; historical virtual source links are retained separately.
    for rel in ['references/expert-adjudication.md', 'references/expert-adjudication-cases.md']:
        path = package / rel
        for target in re.findall(r'\]\(<?([^)>]+)>?\)', path.read_text('utf-8')):
            if '://' not in target and not target.startswith('#'):
                assert (path.parent / target.split('#')[0]).resolve().is_file(), target
    primary = base / '.opencode/skills/liuren/daliuren/SKILL.md'
    assert primary.read_bytes() == (package / 'entry.md').read_bytes()
    skill_checks = []
    for name in pointer['activeSkillNames']:
        path = base / '.opencode/skills/liuren' / name / 'SKILL.md'
        text = path.read_text('utf-8')
        header = re.match(r'^---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---', text)
        assert header and header[1] == name and 0 < len(header[2]) <= 1024
        assert plan['release'] in text and plan['previousRelease'] not in text
        assert sha(path.read_bytes()) == pointer['files']['liuren/'+name+'/SKILL.md']
        skill_checks.append(name)
    # Only the release-scoped paths and the Liuren prompt may change in host config.
    old_config_path = HERE / 'before/opencode.json' if live else ROOT / 'opencode.json'
    before = readj(old_config_path)
    after = readj(base / 'opencode.json')
    rebased = json.loads(json.dumps(before, ensure_ascii=False).replace(plan['previousRelease'], plan['release']))
    old_prompt = rebased['agent']['liuren']['prompt']
    new_prompt = after['agent']['liuren']['prompt']
    assert new_prompt.startswith(old_prompt)
    rebased['agent']['liuren']['prompt'] = new_prompt
    assert after == rebased
    result = dict(ok=True, phase='active' if live else 'candidate', release=plan['release'],
                  methodVersion=manifest['version'], packageFiles=len(plan['newRuntimeFiles']),
                  modulesRead=59, required=14, domains=16, domainPlansChecked=plans,
                  conditionalCombinationsChecked=combinations, sourcePassagesChecked=len(passages),
                  skillsManuallyChecked=skill_checks, oldRuntimeUnchanged=True,
                  calculationPolicyUnchanged=True, configDiffScopeChecked=True,
                  quickValidate='not run successfully: both existing Python runtimes lack PyYAML; native discovery checked separately',
                  modelCalls=0, predictiveValidationCount=0)
    save(HERE / ('active-verification.json' if live else 'candidate-verification.json'), result)
    return result

def atomic(path, raw):
    temp = path.with_name(path.name + '.adjudication-switch.tmp')
    if temp.exists(): raise ValueError('temporary path exists: ' + str(temp))
    with temp.open('xb') as stream: stream.write(raw)
    os.replace(temp, path)

def apply():
    result = verify()
    plan = readj(HERE / 'switch-plan.json')
    target = safe(ROOT, plan['runtime'])
    before = HERE / 'before'
    if target.exists() or before.exists(): raise ValueError('release/backup already exists; refuse overwrite')
    before.mkdir()
    rows = plan['externalFiles']
    for row in rows:
        backup = safe(before, row['path'])
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes((ROOT / row['path']).read_bytes())
    check_files(before, {x['path']:x['before'] for x in rows})
    target.mkdir(parents=True)
    for rel in plan['newRuntimeFiles']:
        dest = safe(target, rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((CAND / plan['runtime'] / rel).read_bytes())
    check_files(target, plan['newRuntimeFiles'])
    ordered = [r for r in rows if r['path'] != '.opencode/liuren-active.json']
    ordered += [r for r in rows if r['path'] == '.opencode/liuren-active.json']
    changed = []
    try:
        for row in ordered:
            dest = ROOT / row['path']
            if sha(dest.read_bytes()) != row['before']: raise ValueError('baseline drift: '+row['path'])
            atomic(dest, (CAND / row['path']).read_bytes())
            changed.append(row)
        result = verify(live=True)
    except BaseException:
        for row in reversed(changed): atomic(ROOT / row['path'], (before / row['path']).read_bytes())
        raise
    receipt = dict(release=plan['release'], previousRelease=plan['previousRelease'], activated=True,
                   methodVersion=plan['methodVersion'], externalFiles=len(rows), pointerWrittenLast=True,
                   oldRuntimeUnchanged=True, backup='before', modelCalls=0, predictiveValidationCount=0)
    save(HERE / 'activation-receipt.json', receipt)
    return receipt

def rollback(check_only=True):
    plan = readj(HERE / 'switch-plan.json')
    check_files(HERE / 'before', {x['path']:x['before'] for x in plan['externalFiles']})
    check_files(ROOT, {x['path']:x['after'] for x in plan['externalFiles']})
    check_files(ROOT, plan['oldRuntimeHashes'])
    if not check_only:
        # Pointer last in the original rows, so restoration also switches it last.
        for row in plan['externalFiles']:
            atomic(ROOT / row['path'], (HERE / 'before' / row['path']).read_bytes())
    result = dict(rollbackReady=True, performed=not check_only, retainedNewRuntime=plan['runtime'])
    save(HERE / ('rollback-check.json' if check_only else 'rollback-receipt.json'), result)
    return result

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['seal', 'verify', 'apply', 'verify-live', 'rollback-check', 'rollback'])
    action = parser.parse_args().action
    result = {'seal':seal, 'verify':verify, 'apply':apply, 'verify-live':lambda:verify(True),
              'rollback-check':rollback, 'rollback':lambda:rollback(False)}[action]()
    print(json.dumps(result, ensure_ascii=False))
