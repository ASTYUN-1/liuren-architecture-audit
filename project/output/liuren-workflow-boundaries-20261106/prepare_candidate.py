"""Finish candidate integration only; never mutate the active installation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
LIVE = OUT / 'candidate-live'
RUN = OUT / 'candidate-runtime'
OLD = '20261105-subagent-adjudication-07'
NEW = '20261106-workflow-boundaries-08'


def read(path):
    return path.read_text(encoding='utf-8-sig')


def write(path, value):
    path.write_text(value, encoding='utf-8', newline='\n')


def dump(path, obj):
    write(path, json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def edit(path, old, new):
    text = read(path)
    if old not in text:
        if new in text:
            return
        raise ValueError(f'Missing replacement in {path}: {old[:90]}')
    write(path, text.replace(old, new))


def replace_json_string(path, old, new):
    # Replace the serialized string alone, preserving all unrelated settings.
    raw = path.read_bytes()
    a = json.dumps(old, ensure_ascii=False).encode()
    b = json.dumps(new, ensure_ascii=False).encode()
    if raw.count(a) != 1:
        raise ValueError(f'Ambiguous JSON string: {path}')
    path.write_bytes(raw.replace(a, b))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def effective(path):
    candidate = LIVE / path
    return candidate if candidate.exists() else ROOT / path


# Entrypoint is concise; detailed responsibilities stay in the existing modules.
entry = RUN / 'entry.md'
edit(entry, OLD, NEW)
edit(entry, '本版保留无案例库、经验库设置，并将裁决交给独立子智能体；',
     '本版保留无案例库、经验库设置，明确主智能体准备、子智能体裁决、主智能体采信交付的边界；')
edit(entry, '主智能体不再形成暂定或最终主判；',
     '主智能体准备到可裁决：核取用候选、状态、关系和原法条件，不预先完成全部矛盾取舍；')
edit(entry, 'evidence仍必读，用于本盘依据、原书条件与最强反证的自核。',
     'evidence仍必读，用于本盘依据、原书条件与最强反证材料的核证，不预先裁完全部矛盾。')
edit(entry, '主智能体依问整理取用、气态、关系及原法条件，不夹带初判、倾向或已知答案；正反材料按盘位／稳定ID排列。同一输入只裁决一次；新增事实或发现错误才补材料重裁。子智能体返回后保持其结论和精度，不自行折中、降档或改判。',
     '主智能体依问整理已核材料，以focus_issues引用观察ID列关键中性争点，不夹带初判、倾向或已知答案，不凑正反。裁决者对照完整盘复核取用、查漏补J实体，再裁关键作用；每条依据展开一次。主智能体返回后核事实、引用、问项与争点覆盖及报告一致性，复用裁决理由和结论，不重新权衡折中。具体错误或新增材料才补核重裁，细节见adjudication。')
edit(entry, '裁决委派先用liuren_adjudication_packet保存中性packet对象，',
     '本版交接采用input/output-v2（focus_issues、scope_review、issue_resolutions），文件协议仍为v1。裁决委派先用liuren_adjudication_packet保存中性packet对象，')

route_path = RUN / 'reading-route.json'
route = json.loads(read(route_path))
route['labels']['evidence'] = '材料核证与争点交接（无两库对照）'
route['stages'][1]['action'] = '核主象真假、主客取与候选及制救条件，整理可能改变本问的关系和待裁处'
route['stages'][1]['note'] = '专业检查保留；前置不完整裁完全部矛盾，已核同版资料复用。'
route['stages'][2]['action'] = '必要专法与材料核证→中性争点文件→裁决者查漏及裁决→主智能体核查复用→完整正文'
route['stages'][2]['note'] = '完整盘随交接；争点不是封闭清单。返回只核事实、引用、覆盖和报告一致性，不重新权衡；具体错误或新增资料才重裁。'
dump(route_path, route)

# Agent prompt is the exact canonical runtime prompt, with unchanged routing/model.
slim_path = LIVE / '.opencode/oh-my-opencode-slim.jsonc'
slim = json.loads(read(slim_path))
old_prompt = slim['agents']['liuren-adjudicator']['prompt']
replace_json_string(slim_path, old_prompt, read(RUN / 'references/adjudicator-prompt.md'))

config_path = LIVE / 'opencode.json'
config = json.loads(read(config_path))
old_prompt = config['agent']['liuren']['prompt']
new_prompt = old_prompt.replace(
    '依问定所主，察真假变质、取与和有效组合，明确取舍；阶段3先完成专法与本盘/原书条件资料核证，再按adjudication契约调用slim注册的liuren-adjudicator新建task独立裁决；主智能体不形成暂定或最终主判，不夹带初判、候选排序或已知答案，不提供task_id，不自行改判。',
    '依问核定位候选、气态、关系及原法条件，准备到可以裁决，不预先裁完全部矛盾；阶段3以focus_issues引用观察ID列关键中性争点（可为空），按adjudication契约调用slim注册的liuren-adjudicator新建task。裁决者对照完整盘检查错取遗漏，可纠正和补J实体，再裁关键作用，不能只在给定争点中选择。主智能体不夹带初判、候选排序或已知答案，不提供task_id；返回后核事实、引用、问项与争点覆盖及报告一致性，复用裁决依据交付，不重新权衡折中。具体错误或新增资料才补核重裁。')
if new_prompt == old_prompt and '准备到可以裁决，不预先裁完全部矛盾' not in old_prompt:
    raise ValueError('Main prompt replacement missing')
new_prompt = new_prompt.replace('只有completed且契约通过才可完整交付。', '只有completed且契约通过才可完整交付；未定维度如实保留，不能变成自动降档。')
replace_json_string(config_path, old_prompt, new_prompt)

# Existing public/local instructions: update the relevant paragraph, not a new flow.
for relative in ['README.md', '目录总索引.md', 'docs/本机六壬高效执行.md',
                 '.opencode/skills/liuren/liuren-cases/SKILL.md',
                 '.opencode/skills/liuren/liuren-extract/SKILL.md']:
    path = LIVE / relative
    write(path, read(path).replace(OLD, NEW))

edit(LIVE / 'README.md',
     '主智能体只组织中性材料、核对返回和完整交付，不先判后让子智能体附和，也不在返回后自行折中。',
     '主智能体核定位、气态、关系和原法条件，准备到可裁决，以中性争点交接；裁决者对照完整盘查错漏并裁关键作用。返回后主智能体只核事实、引用、问项/争点覆盖和报告一致性，复用裁决理由完整交付，不另做一轮权衡折中。')

flow = LIVE / 'docs/本机六壬完整研判流程.md'
edit(flow, '以evidence整理完整课盘、背景、取用候选、正反关系和原法条件；不形成暂定主判。',
     '以evidence核完整课盘、背景、取用候选、正反关系和原法条件，准备到可裁决，以focus_issues引用观察ID列关键未决处；不先完整裁完全部矛盾，不传初判或排序。')
edit(flow, '返回completed且契约通过后按report交付完整正文；不夹带主判或已知答案，不由主智能体再折中改判。',
     '裁决者先对照完整盘核取用与遗漏，再裁争点及清单外关键作用，以scope_review及issue_resolutions登记。返回completed且契约通过后，主智能体核事实、引用、问项/争点覆盖和报告一致性，复用裁决理由按report交付完整正文，不再做一轮理气权衡或折中改判。')

efficient = LIVE / 'docs/本机六壬高效执行.md'
edit(efficient, '主智能体不再先形成主判，也不在返回后自行折中改判。固定书据已随裁决提示加载，子智能体无工具，不重复检索书籍。输入完整，单次裁决；缺必要条件则补齐后新裁；失败明确未完成。',
     '主智能体核材料到可裁决，以focus_issues列中性争点，不先完成全部取舍。裁决者以完整盘查错漏，允许补J实体和纠正取用，每条关键关系只展开一次。主智能体返回后核事实、引用、问项/争点覆盖及报告一致性，复用裁决依据，不另做一轮权衡。固定书据随裁决提示加载，裁决者只用专用reader读本次材料，不重检书籍；已读同版书段直接复用。输入完整，单次裁决；具体错误或确需新增资料才补核重裁；失败明确未完成。')
edit(efficient, '专业方法包仍为上述07，裁决分工不变。',
     '三书索引与检索工具沿用，兼容上述08方法包。')

edit(LIVE / 'docs/本机OpenCode完整输出规则.md',
     '- 最终表达忠实于专业裁决，说明为何取此舍彼；',
     '- 返回后核事实、引用、问项与争点覆盖及报告一致性；复用裁决者的实体、关系、争点取舍及逐问答案整理完整正文，不另起一轮全盘权衡。具体错误或新增材料须补核重裁，纯排版或表述修正可直接处理。最终表达忠实于专业裁决，说明为何取此舍彼；')
edit(LIVE / 'AGENTS.md',
     '本版裁决交接：先调用liuren_adjudication_packet保存中性材料，',
     '本版分工：主智能体准备到可裁决，以focus_issues列中性争点；裁决者对照完整盘查错漏、裁关键作用；主智能体返回后核事实、引用、问项/争点覆盖和报告一致性，复用裁决依据，不重新权衡折中。具体错误或新增材料才补核重裁。裁决交接采用input/output-v2、文件协议v1：先调用liuren_adjudication_packet保存中性材料，')

# Declaration of changes in role/position as well as branch prevents hidden remapping.
contract = LIVE / 'tools/liuren-adjudication-contract.mjs'
edit(contract, "const changedSymbols=r.entity_checks.some(e=>originals.has(e.id)&&e.branch!==originals.get(e.id).branch);",
     "const changedSymbols=r.entity_checks.some(e=>originals.has(e.id)&&['referent','branch','position'].some(k=>e[k]!==originals.get(e.id)[k]));")

for rel in ['references/adjudicator-contract.md', 'references/adjudicator-prompt.md']:
    path = RUN / rel
    write(path, read(path).replace('取用新增或干支更正', '取用新增或对象、干支、位置更正'))
edit(RUN / 'references/adjudicator-contract.md', '新增实体或改动干支不能标confirmed；',
     '新增实体或改动对象、干支、位置不能标confirmed；')
# Retain the fixed source-basis suffix including its original line endings.
prompt_path = RUN / 'references/adjudicator-prompt.md'
marker = '# 固定书据：条件摘要与关键短引'.encode()
prefix = prompt_path.read_bytes().split(marker, 1)[0]
suffix = (ROOT / 'runtime/liuren' / OLD / 'references/adjudicator-prompt.md').read_bytes().split(marker, 1)[1]
prompt_path.write_bytes(prefix + marker + suffix)
# Sync again after last canonical edit.
slim = json.loads(read(slim_path))
replace_json_string(slim_path, slim['agents']['liuren-adjudicator']['prompt'], read(RUN / 'references/adjudicator-prompt.md'))
(LIVE / '.opencode/skills/liuren/daliuren/SKILL.md').write_bytes(entry.read_bytes())

# Preserve policy rules exactly: only the release identity changes.
policy_path = RUN / 'references/shensha-policy.json'
policy = json.loads(read(policy_path))
policy['release'] = NEW
dump(policy_path, policy)

pointer_path = LIVE / '.opencode/liuren-active.json'
pointer = json.loads(read(pointer_path))
pointer.update(release=NEW, runtime='runtime/liuren/' + NEW, previousRelease=OLD,
               backup=str(OUT.relative_to(ROOT) / 'before').replace('\\', '/'),
               authoringSource=str(OUT.relative_to(ROOT)).replace('\\', '/'))
pointer['adjudication'].update(inputSchema='liuren-adjudication-input-v2', outputSchema='liuren-adjudication-output-v2')
pointer['adjudication']['workflowBoundaries'] = {
    'preparation': 'verified chart, candidate mappings, observations, source conditions and neutral focus issues; no completed verdict',
    'adjudicator': 'whole-chart mapping and omission review, critical relations, focus issue resolutions and answers',
    'delivery': 'verify facts, references, coverage and consistency; reuse adjudicated reasons and verdict',
    'changedEvidenceOnlyRetry': True,
}
for path in pointer['workflowImplementation']:
    pointer['workflowImplementation'][path] = sha(effective(path))
for path in pointer['files']:
    pointer['files'][path] = sha(LIVE / '.opencode/skills' / path)
retrieval = pointer['bookRetrieval']
retrieval['originMethodRelease'] = retrieval.pop('methodsReleaseUnchanged', OLD)
retrieval['compatibleMethodRelease'] = NEW
for path in retrieval['files']:
    retrieval['files'][path] = sha(effective(path))

loader_path = RUN / 'loader-contract.json'
loader = json.loads(read(loader_path))
loader.update(release=NEW, authoringSource=pointer['authoringSource'])
for path in loader['sourceHashes']:
    loader['sourceHashes'][path] = sha(effective(path))
for path in pointer['workflowImplementation']:
    loader['sourceHashes'][path] = sha(effective(path))
loader['defaultMethodTransport']['execution'] = 'prepare verified neutral material; scoped file task; whole-chart omission review and focused adjudication; verify and reuse result for complete report'
loader['workflowBoundaries'] = pointer['adjudication']['workflowBoundaries']
dump(loader_path, loader)

integration_path = RUN / 'integration-map.json'
previous = json.loads(read(integration_path))
if previous.get('revisionMap') == 'workflow-boundaries-revision.json':
    previous = previous['previousIntegration']
dump(integration_path, dict(parent=OLD, change='准备到可裁决；完整盘查错漏与重点裁决；返回核查和依据复用',
                           authoringSource=pointer['authoringSource'], previousIntegration=previous,
                           revisionMap='workflow-boundaries-revision.json', independentValidation=0))
dump(RUN / 'workflow-boundaries-revision.json', {
    'release': NEW, 'parent': OLD, 'scope': 'local-opencode',
    'goals': ['prepare to adjudicate without completing all conflicts twice',
              'adjudicate focus issues and independently check mapping omissions against the full chart',
              'verify facts/references/coverage/consistency and reuse the adjudicated reasons'],
    'inputSchema': pointer['adjudication']['inputSchema'], 'outputSchema': pointer['adjudication']['outputSchema'],
    'fileProtocolUnchanged': 'liuren-adjudication-file-v1',
    'retained': ['14 required modules', '16 domains', '11 legacy coverage mappings', 'professional source rules',
                 'fixed E01-E22 basis', 'no-case-experience experiment', 'full report', 'model and high reasoning', 'three-book search'],
    'registrationCorrection': 'tools/liuren-local-read.py source unchanged; register current bytes instead of stale pointer receipt',
    'predictiveValidationCount': 0, 'liveTimingTokenBenchmark': False,
})

manifest_path = RUN / 'manifest.json'
manifest = json.loads(read(manifest_path))
manifest.update(release=NEW, parentRelease=OLD, authoringSource=pointer['authoringSource'],
                revisionFile='workflow-boundaries-revision.json', adjudication=pointer['adjudication'],
                status='active')
manifest['files'] = {str(path.relative_to(RUN)).replace('\\', '/'): sha(path)
                     for path in sorted(RUN.rglob('*')) if path.is_file() and path != manifest_path}
manifest['version'] = hashlib.sha256(json.dumps(manifest['files'], sort_keys=True).encode()).hexdigest()
dump(manifest_path, manifest)
pointer['methodVersion'] = manifest['version']
dump(pointer_path, pointer)
print(json.dumps({'candidate': NEW, 'files': len(manifest['files']), 'version': manifest['version']}, ensure_ascii=False))
