"""Activate the frozen fusion release in this project's local OpenCode skills.

prepare writes only a reviewable staging/backup plan. activate moves replaced
directories outside skill discovery before installing adapters. No model calls.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from liuren_runtime import ROOT, sha, verify, write_json

RELEASE = '20261023-local-active-01'
CANDIDATE = ROOT / 'output/壬归融合实施-20261023/20261023-local-01/enhanced'
OUT = ROOT / 'output/壬归融合实施-20261023' / RELEASE
LIVE = ROOT / '.opencode/skills'
RUNTIME = ROOT / 'runtime/liuren' / RELEASE
PLAN = OUT / 'activation-plan.json'
POINTER = ROOT / '.opencode/liuren-active.json'


def bounded(path, base):
    path, base = Path(path).resolve(), Path(base).resolve()
    if not path.is_relative_to(base) or path == base:
        raise ValueError('path outside intended directory: ' + str(path))
    return path


def inventory(base):
    return {p.relative_to(base).as_posix(): sha(p.read_bytes())
            for p in sorted(base.rglob('*')) if p.is_file()}


def link(from_file, target):
    return os.path.relpath(target, from_file.parent).replace('\\', '/')


def mdlink(label, from_file, target):
    return f'[{label}](<{link(from_file, target)}>)'


def runtime_refs(base=RUNTIME):
    return base / '.opencode/skills/daliuren/refs/runtime'


def check_links(path, text, preparing=False):
    text = re.sub(r'```.*?```|<!--.*?-->', '', text, flags=re.S)
    for target in re.findall(r'\[[^\]\n]+\]\((<[^>]+>|[^\s)]+)\)', text):
        target = target.strip('<>').split('#')[0]
        if not target or target.startswith(('https:', 'http:')):
            continue
        p = (path.parent / target).resolve()
        bounded(p, ROOT)
        actual = p
        if preparing and p.is_relative_to(RUNTIME):
            actual = CANDIDATE / p.relative_to(RUNTIME)
        if preparing and p.is_relative_to(OUT / 'backup/skills'):
            actual = LIVE / p.relative_to(OUT / 'backup/skills')
        if not actual.is_file():
            raise ValueError('missing adapter reference: ' + str(p))


def prepare():
    if OUT.exists() or RUNTIME.exists() or POINTER.exists():
        raise ValueError('activation output or pointer already exists')
    result = verify(CANDIDATE)
    m = json.loads((CANDIDATE / 'liuren-runtime.json').read_text('utf-8'))
    before = inventory(LIVE)
    staged = OUT / 'staged/skills'
    staged.mkdir(parents=True)
    refs = runtime_refs()
    files = {}
    for name, keys in m['legacyAliases'].items():
        current = LIVE / name / 'SKILL.md'
        old = current.read_text('utf-8-sig')
        frontmatter = re.match(r'^---\s*\n(.*?)\n---', old, re.S).group(1)
        if name == 'daliuren':
            frontmatter = ('name: daliuren\ndescription: 大六壬排盘、起课、断课、解课、占卜、四课三传与单事研判的统一入口；'
                          '使用北海三步法与壬归融合增强版。出生推命、案例归档及资料提取分流到对应维护入口。')
        header = (f'---\n{frontmatter}\n---\n\n# 本地 OpenCode 六壬融合版：{name}\n\n'
                  f'已启用版本：`{RELEASE}`；方法包：`{m["version"]}`（enhanced）。\n\n')
        main = mdlink('统一入口', current, LIVE / 'daliuren/SKILL.md')
        core = mdlink('判断核心', current, refs / 'core.md')
        evidence = mdlink('证据纪律', current, refs / 'evidence.md')
        shensha = mdlink('神煞基础', current, refs / 'mechanisms/shensha.md')
        if name == 'daliuren':
            body = (f'单事研判先完整读取{core}、{evidence}及{shensha}，固定原问、对象、阶段和成功标准；'
                    '再按问项读取对应占类及触发的机制。按同一版本复用已完整读过的内容。\n\n'
                    '本地执行：已有可靠程序 facts 时直接使用；需要起课或仅排盘时，先完整读取'
                    + mdlink('本地排盘操作手册', current, refs / 'sources/snapshots/.opencode/skills/daliuren/refs/daliuren-paipan.md')
                    + '，使用既有 localhost:3456 服务，不自行重排天地盘、四课或三传。纯排盘到此完成。\n\n'
                    '出生推命转 `liuren-tuiming`；案例查询和归档转 `liuren-cases`；书籍与经验提取转 `liuren-extract`。'
                    '八字沿用原入口。案例、经验及工具路径以项目根目录为基准。\n\n'
                    '本地 OpenCode 没有网站的 `register_questions`、`record_judgment` 工具；'
                    '以核心要求的逐问论证摘要记录对象、盘面关系、状态、反证取舍、结论依赖及未定项，'
                    '不臆造工具调用，也不声称已通过网站程序校验。历史正文中的旧方法名使用下列新版模块别名，'
                    '旧 localhost/文件操作仅用于本地环境，不另行启动旧版八套判断流程。\n\n'
                    '以下模块均属于同一融合流程；完整原文、原例和旧稿位于运行包的 sources 中，'
                    '仅供按争点查证。运行规则依核心的适配口径执行。\n\n')
            body += '\n'.join(mdlink(k, current, refs / v['file']) + '：' + v['when']
                              for k, v in m['modules'].items()) + '\n'
        else:
            body = (f'这是{main}的新版兼容入口，不包含旧判断正文。先按统一入口取得可靠固定盘，'
                    f'完整读取{core}、{evidence}及{shensha}；已完整读取的同版本内容可复用。\n\n'
                    '本方法对应的融合模块：\n\n')
            body += '\n'.join('- ' + mdlink(k, current, refs / m['modules'][k]['file']) for k in keys) + '\n\n'
            body += '只围绕当前问项执行相关模块；保留原条件、反例和来源差异，不因旧名称再执行旧版主流程。\n'
            if name == 'liuren-cases':
                body += ('\n常规断课检索按上述证据模块执行。用户明确要求案例归档、复盘整理或库维护时，再完整读取'
                         + mdlink('案例维护原完整规程', current, OUT / 'backup/skills/liuren-cases/SKILL.md')
                         + '；该备份仅供资料维护，不取代新版研判核心。案例和经验仍写回项目原库。\n')
        text = header + body
        check_links(current, text, preparing=True)
        dest = staged / name / 'SKILL.md'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding='utf-8', newline='\n')
        files[f'{name}/SKILL.md'] = sha(dest.read_bytes())

    # Keep paths referenced by the separate extraction/lifetime skills working,
    # with redirects rather than old method bodies under skill discovery.
    bridges = {
        'daliuren/refs/liqi-analysis.md': refs / 'mechanisms/state-and-rescue.md',
        'daliuren/refs/judgment-workflow.md': refs / 'core.md',
        'daliuren/refs/shensha-use.md': refs / 'mechanisms/shensha.md',
        'daliuren/refs/liqi-sources.md': refs / 'sources/fusion-sources.md',
    }
    for name in ['rule-semantics.md', 'daliuren-paipan.md']:
        bridges['daliuren/refs/' + name] = refs / 'sources/snapshots/.opencode/skills/daliuren/refs' / name
    for name in ['case-retrieval-v2.md', 'experience-retrieval-v2.md']:
        bridges['liuren-cases/refs/' + name] = refs / 'sources/snapshots/.opencode/skills/liuren-cases/refs' / name
    for relative, target in bridges.items():
        current = LIVE / relative
        text = '# 本地融合版资源入口\n\n完整读取' + mdlink('对应模块或原规程', current, target) + '。旧判断正文已移出 Skill 配置目录；研判以新版核心执行口径为准。\n'
        check_links(current, text, preparing=True)
        dest = staged / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding='utf-8', newline='\n')
        files[relative] = sha(dest.read_bytes())

    aliases = list(m['legacyAliases'])
    preserve = sorted({x.split('/')[0] for x in before} - set(aliases))
    plan = dict(release=RELEASE, methodVersion=m['version'], candidate=str(CANDIDATE),
                runtime=str(RUNTIME), replaced=aliases, preserved=preserve,
                before=before, staged=files, candidateVerification=result,
                configHash=sha((ROOT / 'opencode.json').read_bytes()))
    write_json(PLAN, plan)
    print(json.dumps({'prepared': True, 'release': RELEASE, 'replaced': len(aliases),
                      'preserved': preserve, 'stagedFiles': len(files)}, ensure_ascii=False))


def validate_entries(plan):
    sys.path.insert(0, str(ROOT / 'output/壬归融合实施-20261023/20261023-local-01/validation-deps'))
    validator = Path.home() / '.codex/skills/.system/skill-creator/scripts/quick_validate.py'
    spec = importlib.util.spec_from_file_location('official_skill_validator', validator)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    staged = OUT / 'staged/skills'
    for name in plan['replaced']:
        ok, message = module.validate_skill(staged / name)
        if not ok:
            raise ValueError(name + ': ' + message)
    return len(plan['replaced'])


def activate():
    plan = json.loads(PLAN.read_text('utf-8'))
    if POINTER.exists():
        raise ValueError('release already active; use verify')
    if inventory(LIVE) != plan['before']:
        raise ValueError('active files changed since preparation')
    if inventory(OUT / 'staged/skills') != plan['staged']:
        raise ValueError('staged files changed')
    verify(CANDIDATE)
    validation_count = validate_entries(plan)
    backup = OUT / 'backup/skills'
    backup.mkdir(parents=True, exist_ok=True)
    preserved_files = {p: h for p, h in plan['before'].items() if p.split('/')[0] in plan['preserved']}
    if inventory(backup) not in ({}, preserved_files):
        raise ValueError('backup contains a partial or different activation')
    # Include untouched skills in the archival tree so old relative links remain
    # usable for explicitly requested maintenance. They remain active unchanged.
    for name in plan['preserved']:
        source, dest = bounded(LIVE / name, LIVE), bounded(backup / name, backup)
        if not dest.exists():
            shutil.copytree(source, dest)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    if not RUNTIME.exists():
        shutil.copytree(CANDIDATE, bounded(RUNTIME, ROOT / 'runtime'))
    verify(RUNTIME)
    moved, installed = [], []
    try:
        # Windows desktop watchers can keep directory handles open. Relocate
        # individual files, retaining empty directory shells until reuse.
        for relative in plan['before']:
            if relative.split('/')[0] not in plan['replaced']:
                continue
            source, dest = bounded(LIVE / relative, LIVE), bounded(backup / relative, backup)
            dest.parent.mkdir(parents=True, exist_ok=True)
            source.rename(dest)
            moved.append(relative)
        for relative in plan['staged']:
            dest = bounded(LIVE / relative, LIVE)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(OUT / 'staged/skills' / relative, dest)
            installed.append(relative)
        write_json(POINTER, {'release': RELEASE, 'status': 'active', 'scope': 'local-opencode',
                            'methodVersion': plan['methodVersion'], 'runtime': RUNTIME.relative_to(ROOT).as_posix(),
                            'backup': backup.relative_to(ROOT).as_posix(), 'entry': '.opencode/skills/daliuren/SKILL.md',
                            'files': plan['staged']})
        result = verify_active(plan)
        result['officialSkillValidation'] = validation_count
        write_json(OUT / 'activation-receipt.json', result)
        print(json.dumps(result, ensure_ascii=False))
    except Exception:
        failed = OUT / 'failed-new-skills'
        failed.mkdir(exist_ok=True)
        for relative in reversed(installed):
            source, dest = bounded(LIVE / relative, LIVE), bounded(failed / relative, failed)
            dest.parent.mkdir(parents=True, exist_ok=True)
            source.rename(dest)
        for relative in reversed(moved):
            source = bounded(LIVE / relative, LIVE)
            source.parent.mkdir(parents=True, exist_ok=True)
            bounded(backup / relative, backup).rename(source)
        if POINTER.exists():
            POINTER.rename(OUT / 'failed-active-pointer.json')
        raise


def verify_active(plan):
    result = verify(RUNTIME)
    actual = inventory(LIVE)
    final_path = OUT / 'final-layout.json'
    if final_path.exists():
        final = json.loads(final_path.read_text('utf-8'))
        expected = final['files']
    else:
        expected = {p: h for p, h in plan['before'].items() if p.split('/')[0] in plan['preserved']}
        expected.update(plan['staged'])
    if actual != expected:
        raise ValueError('active file set/hash mismatch')
    if inventory(OUT / 'backup/skills') != plan['before']:
        raise ValueError('backup bytes differ from original')
    if sha((ROOT / 'opencode.json').read_bytes()) != plan['configHash']:
        raise ValueError('project config changed')
    linked_files = [p for p in expected if p.startswith(('daliuren/', 'liuren-cases/', 'liuren-extract/', 'liuren-tuiming/'))]
    for name in linked_files:
        path = LIVE / name
        check_links(path, path.read_text('utf-8'))
    return dict(active=True, release=RELEASE, methodVersion=result['version'],
                replacedSkillDirectories=len(plan['replaced']) + (2 if final_path.exists() else 0),
                preserved=['bazi', 'bazi-extract', 'bazi-yingqi'] if final_path.exists() else plan['preserved'],
                modules=result['modules'], paragraphs=result['paragraphs'], backup='byte-identical',
                oldBodiesInReplacedDirectories=False, links='passed', projectConfig='unchanged',
                discoveryVerified=False, predictionTested=False)


def finalize():
    """Keep one interpretation skill and three explicit maintenance routes."""
    plan = json.loads(PLAN.read_text('utf-8'))
    verify_active(plan)
    final_file = OUT / 'final-layout.json'
    if final_file.exists():
        raise ValueError('final layout already installed')
    entry_names = ['daliuren', 'liuren-cases', 'liuren-extract', 'liuren-tuiming']
    retired = sorted(set(plan['replaced']) - {'daliuren', 'liuren-cases'})
    relocated = [*retired, 'liuren-extract', 'liuren-tuiming']
    staged = OUT / 'final-staged/skills'
    generated = {}
    for name in ['liuren-extract', 'liuren-tuiming']:
        current = LIVE / name / 'SKILL.md'
        old = current.read_text('utf-8-sig')
        fm = re.match(r'^---\s*\n(.*?)\n---', old, re.S).group(1)
        reference = OUT / 'backup/skills' / name / 'SKILL.md'
        purpose = '出生推命' if name == 'liuren-tuiming' else '书籍、经验与可观察方法的提取维护'
        body = (f'---\n{fm}\n---\n\n# 本地融合版功能入口：{name}\n\n'
                f'已启用版本：`{RELEASE}`。\n\n'
                f'本入口负责{purpose}。执行前完整读取'
                + mdlink('该功能的完整规程', current, reference)
                + '；原条件、来源、工具及完整参考均保留在配置目录外，不缩减功能。'
                '资料中相对链接相对所读原文件解析；项目库、排盘服务和脚本的执行根目录仍是本项目。\n\n'
                '用户问当下具体事情时，转'
                + mdlink('新版大六壬单事研判', current, LIVE / 'daliuren/SKILL.md')
                + '，使用统一融合模块。历史方法名只用于模块映射，不调用已撤出的旧 Skill。'
                '本次单事增强版没有将出生推命或资料维护改造成另一套单事判断流程。\n')
        generated[f'{name}/SKILL.md'] = body
    current = LIVE / 'daliuren/SKILL.md'
    body = current.read_text('utf-8')
    body = body.replace('以下模块均属于同一融合流程；',
                        '单事研判只加载本总入口。旧子 Skill 名称仅为模块别名，直接读取对应模块文件，不再调用同名 Skill。\n\n以下模块均属于同一融合流程；')
    generated['daliuren/SKILL.md'] = body
    for relative, body in generated.items():
        check_links(LIVE / relative, body)
        dest = staged / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding='utf-8', newline='\n')
    # Run the official validator on all changed entrypoints before any move.
    staged_plan = {**plan, 'replaced': ['daliuren', 'liuren-extract', 'liuren-tuiming']}
    sys.path.insert(0, str(ROOT / 'output/壬归融合实施-20261023/20261023-local-01/validation-deps'))
    spec = importlib.util.spec_from_file_location('official_skill_validator', Path.home() / '.codex/skills/.system/skill-creator/scripts/quick_validate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in staged_plan['replaced']:
        ok, message = module.validate_skill(staged / name)
        if not ok:
            raise ValueError(name + ': ' + message)
    before = inventory(LIVE)
    expected = {p: h for p, h in before.items() if p.split('/')[0] not in relocated}
    expected.update({p: sha(v.encode()) for p, v in generated.items()})
    write_json(OUT / 'final-layout-plan.json', dict(entryNames=entry_names, removedAliases=retired, files=expected))
    retired_root = OUT / 'retired-during-finalization/skills'
    moved, written = [], []
    main_before = current.read_bytes()
    try:
        for relative in before:
            if relative.split('/')[0] not in relocated:
                continue
            source, dest = bounded(LIVE / relative, LIVE), bounded(retired_root / relative, retired_root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            source.rename(dest)
            moved.append(relative)
        for relative in generated:
            dest = bounded(LIVE / relative, LIVE)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(staged / relative, dest)
            written.append(relative)
        if inventory(LIVE) != expected:
            raise ValueError('final layout differs from reviewed plan')
        # Remove only verified empty directories; Windows may retain an empty
        # watched shell, which never contributes a discoverable skill.
        for name in retired:
            base = bounded(LIVE / name, LIVE)
            for directory in sorted([*base.rglob('*'), base], key=lambda p: len(p.parts), reverse=True):
                bounded(directory, LIVE)
                if directory.is_dir() and not any(directory.iterdir()):
                    try:
                        directory.rmdir()
                    except PermissionError:
                        pass
        layout = dict(entryNames=entry_names, removedAliases=retired, files=expected)
        write_json(final_file, layout)
        pointer = json.loads(POINTER.read_text('utf-8'))
        pointer.update(activeSkillNames=entry_names, legacyAliases='module-mapping-only', files=expected)
        write_json(POINTER, pointer)
        receipt = verify_active(plan)
        receipt.update(activeLiurenSkills=entry_names, retiredStandaloneAliases=retired,
                       untouchedSkills=['bazi', 'bazi-extract', 'bazi-yingqi'])
        write_json(OUT / 'final-layout-receipt.json', receipt)
        print(json.dumps(receipt, ensure_ascii=False))
    except Exception:
        for relative in written:
            dest = LIVE / relative
            if relative == 'daliuren/SKILL.md':
                dest.write_bytes(main_before)
            else:
                failed = OUT / 'failed-finalization' / relative
                failed.parent.mkdir(parents=True, exist_ok=True)
                dest.rename(failed)
        for relative in reversed(moved):
            dest = LIVE / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            (retired_root / relative).rename(dest)
        if final_file.exists():
            final_file.rename(OUT / 'failed-final-layout.json')
        raise


def verify_opencode():
    plan = json.loads(PLAN.read_text('utf-8'))
    result = verify_active(plan)
    env = dict(os.environ, OPENCODE_DISABLE_AUTOUPDATE='true')
    p = subprocess.run(['opencode', 'debug', 'skill'], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=45)
    if p.returncode:
        raise RuntimeError('OpenCode discovery failed: ' + p.stderr[-1500:])
    skills = json.loads(p.stdout)
    verified = []
    final_path = OUT / 'final-layout.json'
    final = json.loads(final_path.read_text('utf-8')) if final_path.exists() else None
    names = final['entryNames'] if final else plan['replaced']
    if final:
        for name in final['removedAliases']:
            if any(s.get('name') == name for s in skills):
                raise ValueError('retired alias still discoverable: ' + name)
    for name in names:
        matches = [s for s in skills if s.get('name') == name]
        expected = (LIVE / name / 'SKILL.md').resolve()
        if len(matches) != 1 or Path(matches[0].get('location', '')).resolve() != expected:
            raise ValueError('OpenCode resolved wrong entry: ' + name)
        if RELEASE not in matches[0].get('content', ''):
            raise ValueError('OpenCode did not load activated entry content: ' + name)
        verified.append({'name': name, 'location': str(expected), 'contentHash': sha(matches[0]['content'].encode())})
    result.update(discoveryVerified=True, opencodeEntries=verified,
                  activeLiurenSkills=names, retiredAliasesAbsent=bool(final))
    write_json(OUT / 'opencode-discovery-receipt.json', result)
    if final:
        write_json(OUT / 'final-layout-receipt.json', {**result, 'retiredStandaloneAliases': final['removedAliases']})
    print(json.dumps({k: v for k, v in result.items() if k != 'opencodeEntries'}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'activate', 'finalize', 'verify', 'verify-opencode'])
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare()
    elif args.mode == 'activate':
        activate()
    elif args.mode == 'finalize':
        finalize()
    elif args.mode == 'verify-opencode':
        verify_opencode()
    else:
        print(json.dumps(verify_active(json.loads(PLAN.read_text('utf-8'))), ensure_ascii=False))
