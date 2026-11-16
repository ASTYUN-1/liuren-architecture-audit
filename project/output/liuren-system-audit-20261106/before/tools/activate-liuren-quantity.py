"""Activate the verified local timing/quantity package, retaining a bounded rollback."""
import argparse
import datetime
import importlib.util
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('quantity_activation_package', ROOT / 'tools/stage-liuren-quantity-20261027.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
OUT = ROOT / 'output/本机应期取数激活-20261029'
BACKUP = OUT / 'backup'
POINTER = ROOT / '.opencode/liuren-active.json'
LIVE = ROOT / '.opencode/skills/liuren'
STAGED = candidate.OUT / 'staged/skills/liuren'


def protected():
    paths = [ROOT / name for name in ['opencode.json', 'AGENTS.md', 'docs/本机OpenCode完整输出规则.md',
             '.opencode/bazi-active.json', 'tools/load-liuren-methods.py', 'tools/load-liuren-procedure.py']]
    for name in ['.opencode/skills/bazi', 'website-skills', 'web/src/agent']:
        paths.extend(p for p in (ROOT / name).rglob('*') if p.is_file())
    return {p.relative_to(ROOT).as_posix(): candidate.pages.sha(p.read_bytes()) for p in paths}


def verify():
    receipt = candidate.verify()
    pointer = json.loads(POINTER.read_text('utf-8'))
    if pointer['release'] != candidate.RELEASE or pointer['status'] != 'active':
        raise ValueError('quantity release is not active')
    if not receipt['active']:
        raise ValueError('active package verification failed')
    plan = json.loads((candidate.OUT / 'plan.json').read_text('utf-8'))
    for rel, digest in plan['stagedInventory'].items():
        if pointer['files'].get('liuren/' + rel) != digest:
            raise ValueError('pointer entry hash mismatch: ' + rel)
    if protected() != json.loads((OUT / 'protected-before.json').read_text('utf-8')):
        raise ValueError('unrelated local configuration or website source changed')
    return receipt


def restore():
    inventory = json.loads((OUT / 'before.json').read_text('utf-8'))
    if candidate.build.inventory(BACKUP / 'skills') != inventory:
        raise ValueError('backup content differs')
    for rel in inventory:
        target = (LIVE / rel).resolve()
        if not target.is_relative_to(LIVE.resolve()):
            raise ValueError('rollback path outside local Liuren skill group')
        shutil.copyfile(BACKUP / 'skills' / rel, target)
    shutil.copyfile(BACKUP / 'liuren-active.json', POINTER)


def activate():
    before_check = candidate.verify()
    if before_check['active']:
        raise ValueError('already active; use verify')
    if OUT.exists():
        raise ValueError('activation output exists; inspect before retrying')
    previous = json.loads(POINTER.read_text('utf-8'))
    plan = json.loads((candidate.OUT / 'plan.json').read_text('utf-8'))
    if set(plan['activeInventory']) != set(plan['stagedInventory']):
        raise ValueError('activation unexpectedly adds or removes skill files')
    BACKUP.mkdir(parents=True)
    shutil.copytree(LIVE, BACKUP / 'skills')
    shutil.copyfile(POINTER, BACKUP / 'liuren-active.json')
    candidate.dump(OUT / 'before.json', candidate.build.inventory(LIVE))
    candidate.dump(OUT / 'protected-before.json', protected())
    try:
        for rel in plan['stagedInventory']:
            target = (LIVE / rel).resolve()
            if not target.is_relative_to(LIVE.resolve()):
                raise ValueError('activation path outside local Liuren skill group')
            shutil.copyfile(STAGED / rel, target)
        manifest = candidate.manifest_checked()
        pointer = dict(previous)
        pointer.update(release=candidate.RELEASE, status='active', methodVersion=manifest['version'],
                       runtime=candidate.PACKAGE.relative_to(ROOT).as_posix(),
                       backup=BACKUP.relative_to(ROOT).as_posix(), previousRelease=previous['release'])
        pointer['files'] = dict(previous['files'])
        pointer['files'].update({'liuren/' + rel: digest for rel, digest in plan['stagedInventory'].items()})
        pending = POINTER.with_name('liuren-active.quantity-next.json')
        candidate.dump(pending, pointer)
        pending.replace(POINTER)
        receipt = verify()
    except Exception:
        restore()
        raise
    record = dict(release=candidate.RELEASE, previousRelease=previous['release'], scope='local-opencode',
                  activatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  checkpointTag='liuren-pre-activation-20261029', backup=str(BACKUP.relative_to(ROOT)),
                  active=True, packageContentUnchanged=True, unrelatedFilesUnchanged=True,
                  verification=receipt, modelCalls=0, predictiveAccuracyEvaluated=False)
    candidate.dump(OUT / 'activation.json', record)
    return {key: value for key, value in record.items() if key != 'verification'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['activate', 'verify', 'rollback'])
    action = parser.parse_args().action
    if action == 'activate':
        result = activate()
    elif action == 'verify':
        receipt = verify()
        result = dict(release=receipt['release'], active=True, filesVerified=receipt['filesVerified'],
                      unrelatedFilesUnchanged=True, modelCalls=0, predictiveAccuracyEvaluated=False)
    else:
        verify()
        restore()
        candidate.verify()
        result = dict(activeRelease=json.loads(POINTER.read_text('utf-8'))['release'], restored=True)
        candidate.dump(OUT / 'rollback.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
