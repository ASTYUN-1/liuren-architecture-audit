"""Stage/activate/verify the local loading-contract fix; never run model inference."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RELEASE = '20261023-modular-03'
PARENT = '20261023-modular-02'
SOURCE = ROOT / 'knowledge/liuren-v3'
PACKAGE = ROOT / 'runtime/liuren' / RELEASE
PREVIOUS = PACKAGE.with_name(PARENT)
OUT = ROOT / 'output/六壬技能结构重整-20261023' / RELEASE
LIVE = ROOT / '.opencode/skills'
POINTER = ROOT / '.opencode/liuren-active.json'
TOOLS = ['tools/load-liuren-methods.py', 'tools/load-liuren-procedure.py']


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = load('liuren_previous_build', 'restructure-liuren-skills.py')
loader = load('liuren_fixed_loader', 'load-liuren-methods.py')


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def render_tables(route, manifest):
    def link(key):
        return '[' + route['labels'][key] + '](' + manifest['modules'][key]['file'] + ')'
    lines = ['| 环节 | 实际动作与可见产物 | 读取要求 |', '|---|---|---|']
    for phase in route['stages']:
        reads = []
        if phase['required']:
            reads.append('必读' + '、'.join(link(key) for key in phase['required']) + '。')
        conditions = [key for key, value in route['conditional'].items() if value['stage'] == phase['id']]
        if conditions:
            reads.append('命中条件必读' + '、'.join(link(key) for key in conditions) + '（条件与参数见下表）。')
        if phase['id'] == route['domainStage']:
            reads.append('并读取命中占类。')
        reads.append(phase['note'])
        lines.append(f"| {phase['id']} {phase['title']} | {phase['action']} | {''.join(reads)} |")
    stages = '\n'.join(lines)
    lines = ['| 模块 ID | 触发条件 | 环节 | plan 参数 |', '|---|---|---|---|']
    for key, condition in route['conditional'].items():
        lines.append(f"| `{key}` | {condition['trigger']} | {condition['stage']} | `{condition['selectWith']}` |")
    return stages, '\n'.join(lines)


def render_entry(text, route, manifest):
    stages, conditions = render_tables(route, manifest)
    wrapped = '<!-- READING_STAGES_BEGIN -->\n' + stages + '\n<!-- READING_STAGES_END -->'
    if '<!-- READING_STAGES_BEGIN -->' in text:
        text = re.sub(r'<!-- READING_STAGES_BEGIN -->.*?<!-- READING_STAGES_END -->', lambda _: wrapped, text, flags=re.S)
    else:
        text, count = re.subn(r'\| 环节 \|.*?(?=\n\n## 占类)', lambda _: wrapped, text, count=1, flags=re.S)
        if count != 1:
            raise ValueError('workflow table not found')
    wrapped = '<!-- READING_CONDITIONS_BEGIN -->\n' + conditions + '\n<!-- READING_CONDITIONS_END -->'
    if '<!-- READING_CONDITIONS_BEGIN -->' in text:
        text = re.sub(r'<!-- READING_CONDITIONS_BEGIN -->.*?<!-- READING_CONDITIONS_END -->', lambda _: wrapped, text, flags=re.S)
    else:
        text = text.replace('\n\n本地无网站', '\n\n' + wrapped + '\n\n本地无网站')
    return text


def materialize(text):
    text = text.replace('@RELEASE@', RELEASE)
    return re.sub(r'\]\((methods|references|details|domains)/([^\)]+)\)',
                  lambda match: '](<' + os.path.relpath(PACKAGE / match[1] / match[2], LIVE / 'liuren/daliuren').replace('\\', '/') + '>)', text)


def check_route(route, manifest):
    if [stage['id'] for stage in route['stages']] != list(range(1, 12)):
        raise ValueError('workflow stages must remain 1..11')
    required = [key for stage in route['stages'] for key in stage['required']]
    if len(required) != len(set(required)) or set(required) != set(manifest['required']):
        raise ValueError('required module coverage changed')
    for key in required + list(route['conditional']):
        if key not in manifest['modules'] or key not in route['labels']:
            raise ValueError('unbound route module: ' + key)
    for item in route['conditional'].values():
        if item['stage'] not in range(1, 12):
            raise ValueError('invalid conditional stage')
    if route['conditional']['nianming']['stage'] != 1:
        raise ValueError('year/life rules must precede role interpretation')


def stage():
    if PACKAGE.exists() or (OUT / 'plan.json').exists():
        raise ValueError('candidate already exists; use verify, do not overwrite the frozen package')
    pointer = json.loads(POINTER.read_text('utf-8'))
    if pointer['release'] != PARENT:
        raise ValueError('unexpected active release')
    backup = OUT / 'backup'
    expected = json.loads((OUT / 'backup-receipt.json').read_text('utf-8'))
    if build.inventory(backup) != expected:
        raise ValueError('backup differs')
    before = build.inventory(LIVE)
    if before != build.inventory(backup / '.opencode/skills'):
        raise ValueError('live skills changed since backup')
    manifest = json.loads((PREVIOUS / 'manifest.json').read_text('utf-8'))
    route = json.loads((SOURCE / 'reading-route.json').read_text('utf-8'))
    check_route(route, manifest)
    source_entry = render_entry((SOURCE / 'entry.md').read_text('utf-8'), route, manifest)
    (SOURCE / 'entry.md').write_text(source_entry, encoding='utf-8', newline='\n')
    shutil.copytree(PREVIOUS, PACKAGE)
    shutil.copy2(SOURCE / 'reading-route.json', PACKAGE / 'reading-route.json')
    (PACKAGE / 'entry.md').write_text(source_entry.replace('@RELEASE@', RELEASE), encoding='utf-8', newline='\n')
    staged = OUT / 'staged/skills'
    shutil.copytree(LIVE, staged)
    for path in (staged / 'liuren').rglob('*.md'):
        text = path.read_text('utf-8').replace(PARENT, RELEASE)
        if path.name == 'SKILL.md' and path.parent.name != 'daliuren':
            text += '\n分页输出为 UTF-8、LF；页哈希仅覆盖 BEGIN/END 之间的正文，排除标记及额外分隔换行，保留正文原有末尾换行。直接 Read 不伪造页凭证；哈希不证明模型理解或执行。\n'
        path.write_text(text, encoding='utf-8', newline='\n')
    (staged / 'liuren/daliuren/SKILL.md').write_text(materialize(source_entry), encoding='utf-8', newline='\n')
    manifest.update(schemaVersion=4, release=RELEASE, parentRelease=PARENT, routingFile='reading-route.json',
                    required=[key for phase in route['stages'] for key in phase['required']],
                    conditional={key: item['trigger'] for key, item in route['conditional'].items()})
    for key, module in manifest['modules'].items():
        module['required'] = key in manifest['required']
        if key in route['conditional']:
            module['trigger'] = route['conditional'][key]['trigger']
    dump(PACKAGE / 'loader-contract.json', dict(encoding='utf-8', newline='LF',
         pageHash='SHA-256 of unmodified body bytes; excludes begin/end markers and separator LF',
         files={rel: build.digest((ROOT / rel).read_bytes()) for rel in TOOLS}))
    manifest['files'] = {key: value for key, value in build.inventory(PACKAGE).items() if key != 'manifest.json'}
    manifest['version'] = build.digest(json.dumps(manifest['files'], sort_keys=True).encode())
    dump(PACKAGE / 'manifest.json', manifest)
    dump(OUT / 'plan.json', dict(release=RELEASE, parentRelease=PARENT, before=before,
         staged=build.inventory(staged), previousPackage=build.inventory(PREVIOUS),
         previousPointerHash=build.digest(POINTER.read_bytes()), configHash=build.digest((ROOT / 'opencode.json').read_bytes()),
         sourceEntryHash=build.digest((SOURCE / 'entry.md').read_bytes()), packageVersion=manifest['version']))
    # Use the existing local dependency rather than install or fetch anything.
    sys.path.insert(0, str(OUT.parent / PARENT / 'validation-deps'))
    dump(OUT / 'official-validation.json', build.official_validate(staged))
    verify(False)
    print(json.dumps(dict(staged=True, release=RELEASE), ensure_ascii=False))


def verify(activated=True, discover=False):
    plan = json.loads((OUT / 'plan.json').read_text('utf-8'))
    manifest = json.loads((PACKAGE / 'manifest.json').read_text('utf-8'))
    files = build.inventory(PACKAGE)
    files.pop('manifest.json')
    if files != manifest['files'] or build.digest(json.dumps(files, sort_keys=True).encode()) != manifest['version']:
        raise ValueError('package differs from manifest')
    if build.inventory(PREVIOUS) != plan['previousPackage']:
        raise ValueError('previous frozen release changed')
    backup = json.loads((OUT / 'backup-receipt.json').read_text('utf-8'))
    if build.inventory(OUT / 'backup') != backup:
        raise ValueError('backup changed')
    if build.digest((ROOT / 'opencode.json').read_bytes()) != plan['configHash']:
        raise ValueError('unrelated OpenCode configuration changed')
    contract = json.loads((PACKAGE / 'loader-contract.json').read_text('utf-8'))
    if any(build.digest((ROOT / rel).read_bytes()) != hash_ for rel, hash_ in contract['files'].items()):
        raise ValueError('loader script differs from frozen contract')
    route = json.loads((PACKAGE / 'reading-route.json').read_text('utf-8'))
    check_route(route, manifest)
    source = (SOURCE / 'entry.md').read_text('utf-8')
    if source != render_entry(source, route, manifest):
        raise ValueError('entry workflow/conditional tables differ from canonical route')
    skills = LIVE if activated else OUT / 'staged/skills'
    if build.inventory(skills) != plan['staged']:
        raise ValueError('skill file set or hashes differ')
    if (skills / 'liuren/daliuren/SKILL.md').read_text('utf-8') != materialize(source):
        raise ValueError('entry does not implement canonical route')
    for module in manifest['modules'].values():
        build.check_markdown(PACKAGE / module['file'], ROOT)
    for path in (skills / 'liuren').rglob('*.md'):
        if activated:
            build.check_markdown(path, ROOT)
        else:
            for raw in re.findall(r'\[[^\]\n]+\]\((<[^>]+>|[^\s)]+)\)', path.read_text('utf-8')):
                final = LIVE / path.relative_to(skills)
                target = (final.parent / raw.strip('<>')).resolve()
                if not target.is_file():
                    raise ValueError('staged reference missing: ' + str(target))
    # Substantive modules and the complete archived sources are byte-identical.
    changed = [rel for rel, hash_ in plan['previousPackage'].items()
               if rel != 'manifest.json' and files.get(rel) != hash_]
    if changed != ['entry.md']:
        raise ValueError('unexpected content changes: ' + repr(changed))
    if build.inventory(skills / 'bazi') != build.inventory(OUT / 'backup/.opencode/skills/bazi'):
        raise ValueError('Bazi files changed')
    if activated:
        pointer = json.loads(POINTER.read_text('utf-8'))
        if (pointer['release'] != RELEASE or pointer['methodVersion'] != manifest['version']
                or pointer['files'] != plan['staged'] or pointer['runtime'] != PACKAGE.relative_to(ROOT).as_posix()):
            raise ValueError('active pointer differs')
        loader.active()  # Includes the hashed route/manifest consistency check.
    receipt = dict(active=activated, release=RELEASE, package='hash-verified', previousRelease='unchanged',
                   substantiveModules='byte-identical', archivedSources='byte-identical', bazi='byte-identical',
                   routingConsistent=True, discoveryVerified=False, predictionTested=False)
    if discover:
        proc = subprocess.run([str(Path.home() / 'scoop/shims/opencode.exe'), 'debug', 'skill'], cwd=ROOT,
                              env=dict(os.environ, OPENCODE_DISABLE_AUTOUPDATE='true'), capture_output=True, timeout=60)
        if proc.returncode:
            raise ValueError('OpenCode discovery failed: ' + proc.stderr.decode('utf-8', errors='replace')[-1200:])
        found = json.loads(proc.stdout)
        checked = []
        for name in build.NAMES:
            group = 'bazi' if name.startswith('bazi') else 'liuren'
            expected = LIVE / group / name / 'SKILL.md'
            hits = [item for item in found if item['name'] == name]
            body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', expected.read_text('utf-8'), count=1, flags=re.S).strip()
            if (len(hits) != 1 or Path(hits[0]['location']).resolve() != expected.resolve()
                    or hits[0]['content'].replace('\r\n', '\n').strip() != body):
                raise ValueError('wrong/duplicate/stale discovered entry: ' + name)
            checked.append(dict(name=name, location=str(expected), contentHash=build.digest(body.encode())))
        legacy = json.loads((ROOT / 'runtime/liuren/20261023-local-active-01/liuren-runtime.json').read_text('utf-8'))['legacyAliases']
        if any(item['name'] in set(legacy) - set(build.NAMES) for item in found):
            raise ValueError('retired aliases still discovered')
        if len([item for item in found if Path(item['location']).resolve().is_relative_to(LIVE.resolve())]) != 7:
            raise ValueError('unexpected project entry')
        receipt.update(discoveryVerified=True, entries=checked, retiredAliasesAbsent=True)
        dump(OUT / 'discovery-observed.json', [item for item in found if item['name'] in build.NAMES])
    dump(OUT / ('discovery-receipt.json' if discover else 'activation-receipt.json' if activated else 'staging-receipt.json'), receipt)
    return receipt


def activate():
    verify(False)
    plan = json.loads((OUT / 'plan.json').read_text('utf-8'))
    if build.inventory(LIVE) != plan['before'] or build.digest(POINTER.read_bytes()) != plan['previousPointerHash']:
        raise ValueError('live state changed since staging')
    for path in (OUT / 'staged/skills/liuren').rglob('*'):
        if path.is_file():
            shutil.copy2(path, LIVE / path.relative_to(OUT / 'staged/skills'))
    pointer = json.loads(POINTER.read_text('utf-8'))
    manifest = json.loads((PACKAGE / 'manifest.json').read_text('utf-8'))
    pointer.update(release=RELEASE, methodVersion=manifest['version'], runtime=PACKAGE.relative_to(ROOT).as_posix(),
                   backup=(OUT / 'backup').relative_to(ROOT).as_posix(), previousRelease=PARENT, files=plan['staged'])
    temporary = POINTER.with_suffix('.json.next')
    dump(temporary, pointer)
    temporary.replace(POINTER)
    return verify()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['stage', 'activate', 'verify', 'discover'])
    action = parser.parse_args().action
    if action == 'stage':
        stage()
    else:
        result = activate() if action == 'activate' else verify(discover=action == 'discover')
        print(json.dumps({key: value for key, value in result.items() if key != 'entries'}, ensure_ascii=False))
