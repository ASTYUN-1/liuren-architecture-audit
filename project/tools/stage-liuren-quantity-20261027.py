"""Build and inspect the frozen Liuren package before or after local activation. No activation or model calls."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'knowledge/liuren-v3'
PARENT = '20261023-modular-03'
RELEASE = '20261027-quantity-02'
PREVIOUS = ROOT / 'runtime/liuren' / PARENT
PACKAGE = PREVIOUS.with_name(RELEASE)
OUT = ROOT / 'output/应期取数接入-20261027' / RELEASE
LIVE = ROOT / '.opencode/skills/liuren'
POINTER = ROOT / '.opencode/liuren-active.json'
CHECKPOINT = 'liuren-pre-timing-quantity-20261027'
CHECKPOINT_HASH = 'fffb14cbb62a1a0130c7acb85e12ed9e9b6b5ba7'  # Verified with git rev-parse before editing.
CHANGES = {
    'methods/timing.md': '沿原E节补起点、尺度、条件、轮次；六组导航与行路语境',
    'methods/liqi.md': '区分力量、时态、大小与运算；日干及遁干的参助职责',
    'methods/quantity.md': '同一Skill内条件加载的共用数量六环及精度',
    'references/quantity-sources.md': '按需核数表、互斥数法、原断和待补算法',
    'domains/finance.md': '数量入口接共用规程，保留金额口径职责',
    'domains/exam.md': '数量入口接共用规程，保留成绩口径职责',
    'domains/lost-person-object.md': '数量入口接共用规程，保留空间和距离口径',
    'methods/report.md': '复用逐问结论给数式；应期补起点，不增常驻附表',
}
EVIDENCE = [
    'docs/应期取数归纳-20261027/原文证据摘录.md',
    'docs/应期取数归纳-20261027/核心归纳-审阅稿.md',
    'docs/应期取数归纳-20261027/天干参与及奇门参照-补充审阅稿.md',
    'docs/应期取数归纳-20261027/天一群笔记专项核查.md',
    'output/应期取数归纳-20261027/curated-evidence.json',
]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = load('candidate_build_helpers', 'restructure-liuren-skills.py')
render = load('candidate_route_helpers', 'patch-liuren-loading-20261023.py')
pages = load('candidate_page_helpers', 'load-liuren-methods.py')


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def dump(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def hash_files(rels):
    return {rel: pages.sha((ROOT / rel).read_bytes()) for rel in rels}


def relocate(text, origin, dest):
    def link(match):
        raw = match[2].strip('<>')
        if raw.startswith(('http:', 'https:', 'mailto:', '#')):
            return match[0]
        target, sep, fragment = raw.partition('#')
        absolute = (origin.parent / target).resolve()
        if absolute.is_relative_to(SOURCE.resolve()):
            absolute = PACKAGE / absolute.relative_to(SOURCE)
        relative = os.path.relpath(absolute, dest.parent).replace('\\', '/')
        return '[' + match[1] + '](<' + relative + sep + fragment + '>)'
    return re.sub(r'\[([^\]\n]+)\]\((<[^>]+>|[^\s)]+)\)', link, text)


def manifest_checked():
    manifest = json.loads((PACKAGE / 'manifest.json').read_text('utf-8'))
    actual = build.inventory(PACKAGE)
    actual.pop('manifest.json')
    if actual != manifest['files'] or pages.sha(json.dumps(actual, sort_keys=True).encode()) != manifest['version']:
        raise ValueError('candidate package differs from frozen manifest')
    route = json.loads((PACKAGE / 'reading-route.json').read_text('utf-8'))
    render.check_route(route, manifest)
    if (manifest['required'] != [key for step in route['stages'] for key in step['required']]
            or manifest['conditional'] != {key: value['trigger'] for key, value in route['conditional'].items()}
            or manifest['domains'] != route['domains']):
        raise ValueError('route/manifest mismatch')
    manifest['readingRoute'] = route
    return manifest


def stage():
    if PACKAGE.exists() or OUT.exists():
        raise ValueError('candidate/output already exists; verify instead of overwriting')
    active_package, active_manifest = pages.active()
    if active_package != PREVIOUS.resolve() or active_manifest['release'] != PARENT:
        raise ValueError('unexpected baseline')
    before = build.inventory(PREVIOUS)
    if {k: v for k, v in before.items() if k != 'manifest.json'} != active_manifest['files']:
        raise ValueError('baseline package is not intact')
    checkpoint = CHECKPOINT_HASH
    protection = hash_files(['.opencode/liuren-active.json', 'tools/load-liuren-methods.py',
                             'tools/load-liuren-procedure.py'])
    route = json.loads((SOURCE / 'reading-route.json').read_text('utf-8'))
    manifest = json.loads((PREVIOUS / 'manifest.json').read_text('utf-8'))
    manifest.update(release=RELEASE, parentRelease=PARENT, status='candidate-inactive')
    for key, relative in [('quantity', 'methods/quantity.md'),
                          ('quantity-sources', 'references/quantity-sources.md')]:
        manifest['modules'][key] = dict(file=relative, required=False,
                                       requires=['quantity'] if key.endswith('-sources') else [])
    manifest.update(required=[key for step in route['stages'] for key in step['required']],
                    conditional={key: item['trigger'] for key, item in route['conditional'].items()},
                    domains=route['domains'], integrationFile='integration-map.json')
    for key, item in route['conditional'].items():
        manifest['modules'][key]['trigger'] = item['trigger']
    render.check_route(route, manifest)
    entry = render.render_entry((SOURCE / 'entry.md').read_text('utf-8'), route, manifest)
    write(SOURCE / 'entry.md', entry)
    shutil.copytree(PREVIOUS, PACKAGE)
    for relative in CHANGES:
        write(PACKAGE / relative, relocate((SOURCE / relative).read_text('utf-8'),
                                          SOURCE / relative, PACKAGE / relative))
    shutil.copyfile(SOURCE / 'reading-route.json', PACKAGE / 'reading-route.json')
    write(PACKAGE / 'entry.md', entry.replace('@RELEASE@', RELEASE))
    changes = {relative: dict(reason=reason, before=before.get(relative),
                              after=pages.sha((PACKAGE / relative).read_bytes()),
                              sourceSha256=pages.sha((SOURCE / relative).read_bytes()))
               for relative, reason in (CHANGES | {'entry.md': '生成条件读取入口',
                                                  'reading-route.json': '新增数量及来源条件，仍为十一环节'}).items()}
    dump(PACKAGE / 'integration-map.json', dict(parent=PARENT, checkpoint=checkpoint, changes=changes,
         historicalCoverage='coverage.json/seed-receipt.json retain parent migration history; this map records the delta',
         evidence=hash_files(EVIDENCE), predictionTested=False))
    manifest['files'] = {k: v for k, v in build.inventory(PACKAGE).items() if k != 'manifest.json'}
    manifest['version'] = pages.sha(json.dumps(manifest['files'], sort_keys=True).encode())
    dump(PACKAGE / 'manifest.json', manifest)
    staged = OUT / 'staged/skills/liuren'
    shutil.copytree(LIVE, staged)
    for path in staged.rglob('*.md'):
        write(path, path.read_text('utf-8').replace(PARENT, RELEASE))
    final_entry = LIVE / 'daliuren/SKILL.md'
    write(staged / 'daliuren/SKILL.md', relocate(entry.replace('@RELEASE@', RELEASE),
                                              SOURCE / 'entry.md', final_entry))
    dump(OUT / 'plan.json', dict(release=RELEASE, status='candidate-inactive', checkpoint=checkpoint,
         parentInventory=before, activeInventory=build.inventory(LIVE), protection=protection,
         sourceHashes=hash_files(['knowledge/liuren-v3/' + key for key in changes]),
         stagedInventory=build.inventory(staged), evidence=hash_files(EVIDENCE)))
    return verify()


def verify():
    manifest = manifest_checked()
    plan = json.loads((OUT / 'plan.json').read_text('utf-8'))
    live_package, live_manifest = pages.active()
    activated = live_manifest['release'] == RELEASE and live_package == PACKAGE.resolve()
    if not activated and (live_manifest['release'] != PARENT or live_package != PREVIOUS.resolve()):
        raise ValueError('unexpected active release')
    expected_live = plan['stagedInventory'] if activated else plan['activeInventory']
    protection = {key: value for key, value in plan['protection'].items()
                  if not (activated and key == '.opencode/liuren-active.json')}
    if (build.inventory(PREVIOUS) != plan['parentInventory']
            or build.inventory(LIVE) != expected_live
            or hash_files(protection) != protection):
        raise ValueError('active baseline or loaders changed')
    if hash_files(plan['sourceHashes']) != plan['sourceHashes'] or hash_files(EVIDENCE) != plan['evidence']:
        raise ValueError('source or research evidence changed since staging')
    staged = OUT / 'staged/skills/liuren'
    if build.inventory(staged) != plan['stagedInventory']:
        raise ValueError('staged entry files changed')
    allowed = set(CHANGES) | {'entry.md', 'reading-route.json', 'manifest.json', 'integration-map.json'}
    changed = {key for key, hash_ in build.inventory(PACKAGE).items()
               if plan['parentInventory'].get(key) != hash_}
    if changed != allowed:
        raise ValueError('unexpected package delta: ' + repr(changed ^ allowed))
    if set(plan['parentInventory']) - set(build.inventory(PACKAGE)):
        raise ValueError('parent files were removed')
    for module in manifest['modules'].values():
        build.check_markdown(PACKAGE / module['file'], ROOT)
    for path in staged.rglob('*.md'):
        final = LIVE / path.relative_to(staged)
        for raw in re.findall(r'\[[^\]\n]+\]\((<[^>]+>|[^\s)]+)\)', path.read_text('utf-8')):
            target = raw.strip('<>').split('#')[0]
            if target and not target.startswith(('http:', 'https:', 'mailto:')):
                if not (final.parent / target).resolve().is_file():
                    raise ValueError('staged link unresolved at intended final location: ' + raw)
    source_entry = (SOURCE / 'entry.md').read_text('utf-8')
    if source_entry != render.render_entry(source_entry, manifest['readingRoute'], manifest):
        raise ValueError('entry tables differ from route')
    expected = relocate(source_entry.replace('@RELEASE@', RELEASE), SOURCE / 'entry.md', LIVE / 'daliuren/SKILL.md')
    if (staged / 'daliuren/SKILL.md').read_text('utf-8') != expected:
        raise ValueError('staged entry differs from canonical source')
    # The candidate must preserve every old base route unless a new condition is selected.
    baseline = json.loads((PREVIOUS / 'manifest.json').read_text('utf-8'))
    baseline['readingRoute'] = json.loads((PREVIOUS / 'reading-route.json').read_text('utf-8'))
    route_checks = []
    for domain in manifest['domains']:
        for timing in [False, True]:
            old = pages.plan(baseline, [domain], timing)
            new = pages.plan(manifest, [domain], timing)
            if new != old:
                raise ValueError('unselected quantity changed baseline route')
            selected = pages.plan_steps(manifest, [domain], timing, ['quantity-sources', 'quantity'])
            keys = [item['id'] for item in selected]
            if (len(keys) != len(set(keys)) or keys[-1] != 'report'
                    or keys.index('quantity') < keys.index('adjudication')
                    or keys.index('quantity-sources') < keys.index('quantity')
                    or any(item['stage'] != 9 for item in selected if item['id'].startswith('quantity'))):
                raise ValueError('quantity routing order/deduplication failed')
            route_checks.append(dict(domain=domain, timing=timing, unchangedWithoutQuantity=True))
    sys.path.insert(0, str(ROOT / 'output/六壬技能结构重整-20261023/20261023-modular-02/validation-deps'))
    validation = build.official_validate(OUT / 'staged/skills')
    receipt = dict(release=RELEASE, active=activated, filesVerified=len(manifest['files']),
                   changedFiles=sorted(changed), baselineUnchanged=True, sourceAndEvidenceVerified=True,
                   linksChecked=True, routeChecks=route_checks, entryValidation=validation,
                   modelCalls=0, predictiveTrials=0, accuracyConclusion='not evaluated')
    dump(OUT / ('verification-active.json' if activated else 'verification.json'), receipt)
    return receipt


def preview():
    verify()
    # Reuse the existing CLI, page framing, hashes and planner without changing live code/pointer.
    pages.active = lambda: (PACKAGE, manifest_checked())
    pages.main()


if __name__ == '__main__':
    pages.configure_stdout()
    action = sys.argv[1] if len(sys.argv) > 1 else ''
    if action in ('stage', 'verify'):
        result = stage() if action == 'stage' else verify()
        print(json.dumps({key: value for key, value in result.items()
                          if key not in ('routeChecks', 'entryValidation', 'changedFiles')}, ensure_ascii=False))
    elif action in ('plan', 'read'):
        preview()
    else:
        raise SystemExit('Usage: stage-liuren-quantity-20261027.py stage|verify|plan [loader arguments]|read ID --page N')
