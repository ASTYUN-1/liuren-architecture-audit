"""Extend the existing local workflow; preserve runtime 44 and chart output."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil

R = Path(__file__).resolve().parents[2]
O = Path(__file__).resolve().parent
load = lambda p: json.loads(p.read_text('utf-8-sig'))
enc = lambda d: (json.dumps(d, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = load(R / '.opencode/liuren-active.json')
before = load(O / 'before.json')
OLD = '20261111-compact-bifa-44'
NEW = '20261111-bifa-use-45'
assert p['release'] == OLD
assert all(sha(R / f) == h for f, h in before['frozen'].items())
runtime = R / 'runtime/liuren' / NEW
assert not runtime.exists()
shutil.copytree(R / p['runtime'], runtime)
shutil.copyfile(R / 'knowledge/liuren-bifa/20261111/百法录.json', runtime / 'references/bifa-guide.json')

short = '毕法赋仅作关系、情况和倾向的描述性辅助，不决定结果。先依原问取用，再筛成格与本问的关联；无关可不用。原有取用、旺衰、有效作用、制救与阶段主线不变。按需用现有reader的material_id:BF-35查百法录（BF-01至BF-100），BF-B35/BF-D35查原章，不要求逐法解释。'
section = '''## 毕法赋：描述性辅助与百法录

程序chart.bifa_conditions只确认已登记基本结构的明列条件成立，沿用“条目、成格、意象”三字段；不表示每条都与所问有关，也没有完成取义。先依原问、占类、对象和阶段取用，再筛哪些结构确实涉及本问；可以判断某条影响轻微、无作用或无关而不采用，不强求每盘用毕法或逐条解释。

毕法赋用于描述关系、情况、表现和倾向，不能成为决定性判据。沿既有主线核类神、旺衰空实、施受方向、通路、制救和阶段，辨底层作用是否影响本问关键环节；这些作用进入原有综合判断，格名和意象不另加权、不数票、不压过专项。全局或双方之象不自动实体化为具体事件、现实事实、原因或应期；“耗损”不直接变成分手、失败、失窃，“动”不等于得财或达成目标。此项不妨碍依据完整分析回答原问。

遇到需要理解的条目，复用本任务reader：material_id:BF-35查第35法百法录，编号BF-01至BF-100；BF-B35/BF-D35查北海/大全连续原章。百法录摘取北海分析方法与取义线索，归纳、引文分别标识；不是固定盘式断语。查询同时显示本盘已列的子格，书中其他子格不自动成立；无匹配仍可查方法，不反向补成格。原文强语保留来源身份，按既定U口径和本问条件理解，第22成格继续依《大全》。只按需要查，不增必读百章、不另开裁决流程。

沿39版现有核对：看采用的毕法是否切题、是否把描述当结果、是否混用未成立子格或重复计证。有具体问题才定位原句并用原有一次补核机制；不新增长表、硬性采用数量或重派裁决。

'''
pending = {}
for rel in ['references/judgment-core.md', 'methods/adjudication.md', 'methods/structure.md', 'references/bifa.md', 'references/bifa-basic.md']:
    f = runtime / rel
    text = f.read_text('utf-8')
    text = re.sub(r'## 第44版：毕法固定语句导出\n[\s\S]*?(?=\n## |\Z)', '', text, count=1)
    text = text.replace('毕法百法基本适配（44版）', '毕法百法基本适配（45版）')
    text = text.replace('决定性条目应核完整条件，不以标签代替原文。', '用于本问的条目应核完整条件，不以标签代替原文，也不让条目独立决定结果。')
    head, rest = text.split('\n', 1)
    f.write_text(head + '\n\n' + section + rest.lstrip('\n'), encoding='utf-8')

# The old quick page contains obsolete/misleading definitions and fixed
# verdicts (e.g. B1 confuses BF02 with BF01). Keep runtime44 as provenance;
# the active quick page routes to the reviewed registry and reading guide.
(runtime / 'references/bifa.md').write_text('''# 毕法赋按号速查

''' + section + '''## 查询入口

- material_id:BF-01至BF-100：百法录，含本盘已列子格、理解、分析线索和北海摘录。
- material_id:BF-B35或BF-D35：北海或《大全》第35法连续原章，其他法号类推。
- module:bifa-basic：已登记基本条件的范围及采用边界。
- module:bifa-statements：固定展示句库，仅是程序描述，不是判断规则。

原先A/B/C等分类速查含构成简化和固定断语，已由上述按号入口替代；原样保留在冻结runtime44的references/bifa.md供追溯，不作为当前成格定义或解课依据。成格定义以已核条件表为准，应用回到本问专项和共用判断规范。
''', encoding='utf-8')
structure = runtime / 'methods/structure.md'
text = structure.read_text('utf-8').replace(
    '《毕法》课传结构是课体的重要外延，问答录反复以毕法口诀断成败：',
    '以下为《指南》问答录在特定原例中的结构取义摘录，保留原有强语供追溯，不是本盘固定结论。人宅、主客等属于原例定位；当前须依本问重新定位，按上方描述性原则和原有综合方法处理：')
structure.write_text(text, encoding='utf-8')

# Existing skill/host entrypoints: one routing paragraph, no new skill or mode.
for rel in ['.opencode/skills/liuren/daliuren/SKILL.md', 'integrations/codex/daliuren-codex/SKILL.md', 'integrations/codex/daliuren-codex/references/host.md']:
    text = (R / rel).read_text('utf-8')
    if rel.endswith('host.md'):
        text += '\n\n' + short + '\n'
    else:
        end = text.find('\n# ')
        first = text.find('\n', end + 1)
        assert end >= 0 and first >= 0
        text = text[:first + 1] + '\n' + short + '\n' + text[first + 1:]
    pending[rel] = text.encode('utf-8')

for rel in ['README.md', '目录总索引.md']:
    text = (R / rel).read_text('utf-8').replace('指向 `' + OLD + '`', '指向 `' + NEW + '`').replace('runtime/liuren/' + OLD + '/', 'runtime/liuren/' + NEW + '/')
    pending[rel] = (text + '\n\n45版本机毕法应用：' + short + '\n').encode('utf-8')
rel = 'docs/本机六壬高效执行.md'
pending[rel] = ((R / rel).read_text('utf-8') + '\n\n## 百法录按需查阅\n\n' + short + '\n\n继续使用原packet/read/submit/review链。Codex调用action=read、同一run、material_id=BF-35；OpenCode用同一liuren_adjudication_read及file_path/sha256。完整说明见[毕法辅助与百法录](毕法辅助与百法录-45.md)。\n').encode('utf-8')

cfg = load(R / 'opencode.json')
models = {k: (v.get('model'), v.get('variant')) for k, v in cfg['agent'].items()}
cfg = json.loads(json.dumps(cfg, ensure_ascii=False).replace('runtime/liuren/' + OLD, 'runtime/liuren/' + NEW))
cfg['agent']['liuren']['prompt'] = short + '\n' + cfg['agent']['liuren']['prompt']
assert models == {k: (v.get('model'), v.get('variant')) for k, v in cfg['agent'].items()}
pending['opencode.json'] = enc(cfg)
slim = load(R / '.opencode/oh-my-opencode-slim.jsonc')
slim['agents']['liuren-adjudicator']['prompt'] = short + '\n' + slim['agents']['liuren-adjudicator']['prompt']
pending['.opencode/oh-my-opencode-slim.jsonc'] = enc(slim)
current_sha = lambda rel: hashlib.sha256(pending[rel]).hexdigest() if rel in pending else sha(R / rel)
contract = {'id': 'bifa-descriptive-aid-45', 'guide': 'references/bifa-guide.json', 'cards': 100,
            'readerAlias': 'BF-01..BF-100', 'source': '北海闲人《毕法赋全解》',
            'descriptiveOnly': True, 'relevanceByQuestion': True, 'irrelevantMayBeUnused': True,
            'existingWorkflowRetained': True, 'mandatoryReadingAdded': False,
            'chartAlgorithmChanged': False, 'predictiveValidationCount': 0}
p.update(release=NEW, runtime=runtime.relative_to(R).as_posix(), previousRelease=OLD,
         backup='output/liuren-bifa-application-20261111/before',
         authoringSource='output/liuren-bifa-application-20261111', bifaApplication=contract)
p['bookRetrieval']['compatibleMethodRelease'] = NEW
for name in ['manifest.json', 'loader-contract.json']:
    d = load(runtime / name)
    d.update(release=NEW, parentRelease=OLD, authoringSource=p['authoringSource'], bifaApplication=contract)
    if 'bookRetrieval' in d:
        d['bookRetrieval']['compatibleMethodRelease'] = NEW
    if name == 'manifest.json':
        d['modules']['bifa-guide'] = {'file': 'references/bifa-guide.json', 'required': False,
                                     'title': '百法录：北海分析方法与取义线索', 'trigger': '按法号按需查阅；不作固定断语'}
        d['files']['references/bifa-guide.json'] = sha(runtime / 'references/bifa-guide.json')
    else:
        d['sourceHashes'] = {rel: current_sha(rel) for rel in d['sourceHashes']}
    (runtime / name).write_bytes(enc(d))
for name in ['references/shensha-policy.json', 'references/shensha-authority-evidence.json', 'references/confirmed-policy-register.json', 'reading-route.json']:
    d = load(runtime / name)
    d['release'] = NEW
    if name == 'references/confirmed-policy-register.json':
        d['bifaApplication'] = contract
    (runtime / name).write_bytes(enc(d))
m = load(runtime / 'manifest.json')
m['files'] = {rel: sha(runtime / rel) for rel in m['files']}
m['version'] = hashlib.sha256(json.dumps(m['files'], sort_keys=True).encode()).hexdigest()
(runtime / 'manifest.json').write_bytes(enc(m))
p['methodVersion'] = m['version']
p['workflowImplementation'] = {rel: current_sha(rel) for rel in p['workflowImplementation']}
p['files'] = {rel: current_sha('.opencode/skills/' + rel) for rel in p['files']}
pending['.opencode/liuren-active.json'] = enc(p)
for rel in sorted(pending, key=lambda s: s == '.opencode/liuren-active.json'):
    target = R / rel
    temp = target.with_name(target.name + '.bifa45.tmp')
    temp.write_bytes(pending[rel])
    os.replace(temp, target)
assert all(sha(R / f) == h for f, h in before['frozen'].items())
(O / 'after.json').write_bytes(enc({'release': NEW, 'runtime': p['runtime'], 'methodVersion': p['methodVersion'],
    'files': {f: sha(R / f) for f in before['files']}, 'frozen44_unchanged': True, 'models_unchanged': True}))
print('Activated', NEW, '; existing workflow and frozen44 retained')
