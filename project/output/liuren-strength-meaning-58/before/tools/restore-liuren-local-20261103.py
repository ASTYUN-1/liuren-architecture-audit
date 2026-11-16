"""Assemble and activate the local professional workflow; no models or deployment.

The two existing frozen runtimes and historical case runs remain byte-identical.
Only the explicit before-manifest snapshot may be used as the activation baseline.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/liuren-local-restore-20261103'
PARENT = '20261102-integrated-01'
RELEASE = '20261103-local-restore-01'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def inventory(base):
    return {p.relative_to(base).as_posix(): sha(p.read_bytes()) for p in sorted(base.rglob('*')) if p.is_file()}


def main():
    pointer_path = ROOT / '.opencode/liuren-active.json'
    pointer = load(pointer_path)
    before = load(OUT / 'before-manifest.json')
    new = ROOT / 'runtime/liuren' / RELEASE
    old = ROOT / 'runtime/liuren' / PARENT
    if pointer['release'] != PARENT or new.exists() or (OUT / 'activation.json').exists():
        raise ValueError('unexpected baseline or release already exists; refusing overwrite')
    for rel, expected in before.items():
        if isinstance(expected, dict) and inventory(ROOT / rel) != expected:
            raise ValueError('frozen runtime changed: ' + rel)
    if sha(pointer_path.read_bytes()) != before['.opencode/liuren-active.json']:
        raise ValueError('active pointer changed since backup')
    live = ROOT / '.opencode/skills/liuren'
    for path in live.rglob('*'):
        if path.is_file() and sha(path.read_bytes()) != before[path.relative_to(ROOT).as_posix()]:
            raise ValueError('live skill changed since backup: ' + str(path))
    shutil.copytree(old, new)
    manifest = copy.deepcopy(load(old / 'manifest.json'))
    source = ROOT / 'knowledge/liuren-v3'
    for rel in ['entry.md', 'methods/evidence.md', 'methods/report.md']:
        text = (source / rel).read_text(encoding='utf-8').replace('@RELEASE@', RELEASE)
        if rel == 'entry.md':
            text = text.replace('(references/daliuren-paipan.md)', '(<../../../docs/本机六壬直接排盘.md>)')
        (new / rel).write_text(text, encoding='utf-8', newline='\n')
    # Retain an optional module at the old ID, but remove it from the required route.
    (new / 'methods/workflow-contract.md').write_text(
        '# 本机可选结构化审计\n\n'
        '本机默认按 daliuren 的专业十一环节研判、分别检索案例与经验、实际阅读原文并直接输出完整判断。'
        '同卦追问复用原盘、前情和有效来源，只补新争点；不强制 prepare、JSON 或 check。\n\n'
        'prepare/read/check 仅供需要结构化留痕或工程排错时选择。read 页码只表示工具输出；'
        'check 核声明的结构、来源与事实原值，不能证明实际阅读、术理或预测效果，不能充当网站报告交付门禁。'
        '网站公开报告隐藏、格式/字数约束和末步改写不在本机生效。\n\n'
        '完整执行方式见项目 docs/本机六壬完整研判流程.md；专业方法的条件、反证、来源身份仍须实际裁决。\n',
        encoding='utf-8', newline='\n')
    route = load(new / 'reading-route.json')
    for stage in route['stages']:
        stage['required'] = [key for key in stage['required'] if key != 'workflow-contract']
    route['labels']['workflow-contract'] = '可选结构化审计（非本机默认）'
    write(new / 'reading-route.json', route)
    manifest.update(release=RELEASE, parentRelease=PARENT, status='active-local',
                    required=[key for stage in route['stages'] for key in stage['required']])
    manifest['modules']['workflow-contract'].update(required=False, trigger='explicit structured audit only')
    implementation = [*pointer['workflowImplementation'], 'tools/restore-liuren-local-20261103.py']
    hashes = {rel: sha((ROOT / rel).read_bytes()) for rel in implementation}
    write(new / 'loader-contract.json', dict(schema='liuren-local-professional-loader-v1',
        entry='.opencode/skills/liuren/daliuren/SKILL.md', defaultMode='local-professional',
        optionalAuditEntry='tools/liuren-workflow.py', sourceHashes=hashes,
        websiteOutputPolicy=False, semanticCorrectness='unverified', independentValidation=0))
    manifest['files'] = {k: v for k, v in inventory(new).items() if k != 'manifest.json'}
    manifest['version'] = sha(json.dumps(manifest['files'], sort_keys=True).encode())
    write(new / 'manifest.json', manifest)
    # Preserve the live operation override and the full professional routing table.
    for path in live.rglob('*.md'):
        text = path.read_text(encoding='utf-8').replace(PARENT, RELEASE)
        if path == live / 'daliuren/SKILL.md':
            start = text.index('\n## 本机统一执行主路线')
            end = text.index('\n## 分流与读取约束', start)
            local = (source / 'entry.md').read_text(encoding='utf-8')
            begin = local.index('\n## 本机完整研判')
            finish = local.index('\n## 分流与读取约束', begin)
            section = local[begin:finish].replace('本项目 `docs/本机六壬完整研判流程.md`',
                '[本机完整研判流程](<../../../../docs/本机六壬完整研判流程.md>)')
            text = text[:start] + section + text[end:]
            text = text.replace(
                '本机通过统一 CLI 的 prepare/read/check 执行子问登记、来源读取和程序检查；网站工具不在本机调用。交付保留实际检查回执，不把结构检查写成术理验证。',
                '本机直接输出完整专业判断，不运行网站问题登记、公开输出或发布门禁。prepare/read/check 仅为可选审计；同卦追问不强制重跑。')
        path.write_text(text, encoding='utf-8', newline='\n')
    pointer.update(release=RELEASE, previousRelease=PARENT, runtime=new.relative_to(ROOT).as_posix(),
        methodVersion=manifest['version'], backup=(OUT / 'before').relative_to(ROOT).as_posix(),
        files={'liuren/' + rel: value for rel, value in inventory(live).items()},
        workflowImplementation=hashes, defaultMode='local-professional',
        workflowEntry='.opencode/skills/liuren/daliuren/SKILL.md', optionalAuditEntry='tools/liuren-workflow.py',
        websiteOutputPolicy=False, websiteChanged=False)
    # Validate local links before switching the pointer.
    for path in [*live.rglob('*.md'), new / 'entry.md', new / 'methods/evidence.md', new / 'methods/report.md']:
        body = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
        for target in re.findall(r'\[[^\]\n]+\]\((<[^>]+>|[^\s)]+)\)', body):
            target = target.strip('<>').split('#')[0]
            if target and not target.startswith(('https:', 'http:')):
                resolved = (path.parent / target).resolve()
                if not resolved.is_relative_to(ROOT) or not resolved.is_file():
                    raise ValueError('invalid local reference: ' + str(path) + ' -> ' + target)
    for rel, expected in before.items():
        if isinstance(expected, dict) and inventory(ROOT / rel) != expected:
            raise ValueError('frozen runtime changed during activation: ' + rel)
    # Atomic pointer replacement; no Git, model, service or network operation.
    temp = pointer_path.with_suffix('.new.json')
    write(temp, pointer)
    temp.replace(pointer_path)
    write(OUT / 'activation.json', dict(release=RELEASE, parentRelease=PARENT,
        methodVersion=manifest['version'], localOnly=True, websiteChanged=False,
        defaultMode='local-professional', optionalAudit=True, originalRuntimesUnchanged=True,
        implementation=hashes, runtimeFiles=len(manifest['files']), rollback='before/ + before-manifest.json',
        modelCalls=0, predictiveAccuracy='unverified'))
    print(json.dumps(dict(release=RELEASE, files=len(manifest['files']),
                         version=manifest['version'], defaultMode='local-professional'), ensure_ascii=False))


if __name__ == '__main__':
    main()
