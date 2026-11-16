"""Publish local quantity clarification as a new bound runtime; retain old tasks."""
from pathlib import Path
import hashlib
import json
import os
import shutil

R = Path(__file__).resolve().parents[2]
O = Path(__file__).resolve().parent
OLD = '20261111-bifa-use-45-final'
NEW = '20261111-quantity-logic-46'
load = lambda p: json.loads(p.read_text('utf-8-sig'))
enc = lambda d: (json.dumps(d, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = load(R / '.opencode/liuren-active.json')
before = load(O / 'before.json')
assert p['release'] == OLD
assert all(sha(R / f) == h for f, h in before['frozen'].items())
runtime = R / 'runtime/liuren' / NEW
assert not runtime.exists()
shutil.copytree(R / p['runtime'], runtime)

def amend(rel, old, new):
    f = runtime / rel
    s = f.read_text('utf-8')
    assert old in s, (rel, old)
    f.write_text(s.replace(old, new, 1), encoding='utf-8')

def append(rel, content):
    f = runtime / rel
    f.write_text(f.read_text('utf-8').rstrip() + '\n\n' + content + '\n', encoding='utf-8')

short = ('数值追问含名次、次序、等第和进退差值；沿既有quantity及quantity-strength取用，'
         '序数专法按需查quantity-rank。无实物、未给满分或工具目录未收录，不等于不能取数。'
         '说明数字与所求含义的对应；旺衰指数不直接换排名，序位不机械折半，区间同样须有依据。'
         '保留用户原问，不把前问倾向追加成未经用户限定的条件。')

amend('methods/quantity.md', '金额、分数、数量、重量、距离等数值',
      '金额、分数、数量、重量、距离、名次、序位、等第或进退差值等数值')
amend('methods/quantity.md', '## 六环执行', '''## 数字的含义先于算式

物数、连续量、序数、等级和变化量分别确定对象；无形目标也可取数，不因没有实物或满分一概拒用。名次第几、前后次序、几等奖及进退几名按[名次、等第与变化量](../references/quantity-rank.md)查适用专法；总榜/分组榜、人数、并列规则只在相关时纳入，不把评分制当作所有名次题的前提。百分比要明确分母；已有旺衰指数不能直接转成分数、百分位或概率。

先选对象和有源适用方法，再取数。具名工具目录只是已实现算式，不是数法全集；目录无匹配时沿现有reader查原书/参考，完整有据的算式可用quantity expression计算。工具拒绝某个参数或问句只说明接口问题，不替代术理判断，也不得虚构工具没有返回的拒绝理由。需要补充信息时指出具体缺步，不通过改写原问来规避检查。

## 六环执行''')
amend('methods/quantity.md', '距离/方位不是同一对象；',
      '距离/方位、最终名次/变化名次/等级不是同一对象；')
amend('methods/quantity.md', '分、元、件、斤、里/公里、天等；',
      '分、元、件、斤、里/公里、天、名次及等级口径等；')
amend('methods/quantity.md', '不用现实猜测补成“精确推得”。',
      '不用现实猜测补成“精确推得”。区间、中心值与点值都要有形成依据；人数中位、候选平均、可见几个同类宫不能无据变成当事人的排名或全体样本。')
append('references/quantity-strength.md', '''## 序数、等级与差值的修正

先确定修正的含义：得分、实得份额、名次数字和进退幅度不能互代。名次数字通常越小越好，不能因空衰将第12名直接折半成第6名；原法已有气态分支时，不再无据叠加另一法的折减。等级的高低方向也依本题定义。

综合旺衰核关键类神与已选施受作用，须标实际计算覆盖；指数及其增量不直接换算为能升几名、百分位或概率。状态层计空不等于数值层已修正，但数值层是否修正、对象和比例仍须有本法依据。详见quantity-rank，沿用原有制救与依赖重评。''')
append('references/quantity-sources.md', '''## 名次及抽象数值目标

名次、相对先后、等第与进退差值另查[quantity-rank](quantity-rank.md)；连续原文见module:quantity-rank-evidence。该页分别保留《说约》名次专法、《粹言》具体名次例、《壬窍》次第方法及北海对《指南》起遁的质疑，不合成统一名次表。具名计算目录未收这些分支，不构成禁止采用的理由；关键步骤未明也不能自补成精确通法。''')
amend('domains/exam.md', '明确分数满分、允许误差、时间与候选限制。',
      '问分数时明确评分尺度及误差，问名次时区分全体/分组/入选者内部及并列口径；时间与候选限制依原问。')
amend('domains/exam.md', '要分数时接 [数量与精度]',
      '要分数、具体名次、进退几名或数值等第时接 [数量与精度]')
amend('domains/exam.md', '本占类明确原始分、赋分、单科/总分、满分及误差，再由共用规程核算法和精度。',
      '分数题明确原始分/赋分、单科/总分及满分；序数题另查quantity-rank，不因无满分而禁用。名次、得分与入选分别核，前问仅有成败倾向不能变成未经用户限定的事实前提。再由共用规程核算法和精度。')

for rel in ['references/judgment-core.md', 'methods/adjudication.md', 'methods/report.md',
            'references/direct-answer.md']:
    append(rel, '## 取数与序位（46版）\n\n' + short)
append('references/consistency-audit.md', '''## 数值/序位的现有五项核对

input_fidelity核原问是否被擅改为“若落选”等条件；calculation_scope核对象、数表、算式与修正是否真正完成，能否落到所求数值，不以只查目录算完成取数；answer_constraints核点值/区间及等级的形成依据。不因区间较宽就当有据，不以人数中位或研究指数直接定位。发现具体问题仍只走原有一次补核，不增加强制字段、裁决轮次或数法投票。''')
shutil.copyfile(O / 'quantity-rank.md', runtime / 'references/quantity-rank.md')
evidence = load(R / 'output/liuren-rank-method-audit-20261111/原文证据.json')
rows = evidence['evidence'][:7]
for i, e in enumerate(rows, 1):
    source = R / e['path']
    assert sha(source) == e['sha256']
    assert '\n'.join(source.read_text('utf-8-sig').splitlines()[e['line_start']-1:e['line_end']]) == e['quote']
    e['id'] = f'QR{i:02}'
(runtime / 'references/quantity-rank-evidence.json').write_bytes(enc({
    'schema': 'liuren-quantity-rank-evidence-v1',
    'scope': '连续原文；原载方法/注解/反馈，不是本轮独立预测验证', 'evidence': rows}))

pending = {}
entry_files = ['.opencode/skills/liuren/daliuren/SKILL.md',
               'integrations/codex/daliuren-codex/SKILL.md',
               'integrations/codex/daliuren-codex/references/host.md']
for rel in entry_files:
    pending[rel] = ((R / rel).read_text('utf-8').rstrip() + '\n\n' + short + '\n').encode()
cfg = load(R / 'opencode.json')
models = {k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}
cfg = json.loads(json.dumps(cfg, ensure_ascii=False).replace('runtime/liuren/'+OLD, 'runtime/liuren/'+NEW))
cfg['agent']['liuren']['prompt'] = short + '\n' + cfg['agent']['liuren']['prompt']
assert models == {k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}
pending['opencode.json'] = enc(cfg)
slim = load(R / '.opencode/oh-my-opencode-slim.jsonc')
slim['agents']['liuren-adjudicator']['prompt'] = short + '\n' + slim['agents']['liuren-adjudicator']['prompt']
pending['.opencode/oh-my-opencode-slim.jsonc'] = enc(slim)
for rel in ['README.md','目录总索引.md']:
    s = (R / rel).read_text('utf-8').replace('runtime/liuren/'+OLD+'/', 'runtime/liuren/'+NEW+'/').replace('指向 `'+OLD+'`','指向 `'+NEW+'`')
    pending[rel] = (s.rstrip()+'\n\n46版取数逻辑：'+short+' 仅本机新任务，说明见docs/取数与序位逻辑-46.md。\n').encode()
for rel in ['AGENTS.md','docs/本机六壬高效执行.md']:
    link='取数与序位逻辑-46.md' if rel.startswith('docs/') else 'docs/取数与序位逻辑-46.md'
    pending[rel] = ((R / rel).read_text('utf-8').rstrip()+'\n\n46版取数逻辑：'+short+' 仅本机新任务；原书条件与接入说明见[取数与序位逻辑]('+link+')。\n').encode()
current_sha = lambda f: hashlib.sha256(pending[f]).hexdigest() if f in pending else sha(R/f)
contract = {'id':'quantity-semantics-46','guide':'references/quantity-rank.md',
            'evidence':'references/quantity-rank-evidence.json','existingWorkflowRetained':True,
            'ordinalQuestionRecognition':True,'toolCatalogIsExhaustive':False,
            'ordinalFormulaAutomaticallyChosen':False,'numericStrengthConvertedToRank':False,
            'predictiveValidationCount':0,'scope':'local-opencode-and-codex'}
p.update(release=NEW,runtime=runtime.relative_to(R).as_posix(),previousRelease=OLD,
         backup=O.relative_to(R).as_posix()+'/before',authoringSource=O.relative_to(R).as_posix(),quantityLogic=contract)
p['bookRetrieval']['compatibleMethodRelease'] = NEW
for name in ['loader-contract.json','references/shensha-policy.json','references/shensha-authority-evidence.json',
             'references/confirmed-policy-register.json','reading-route.json']:
    d=load(runtime/name);d['release']=NEW
    if name=='loader-contract.json':
        d.update(parentRelease=OLD,authoringSource=p['authoringSource'],quantityLogic=contract)
        d['sourceHashes']={f:current_sha(f) for f in d['sourceHashes']}
    if name=='reading-route.json':
        d['labels'].update({'quantity-rank':'名次、等第与变化量专法','quantity-rank-evidence':'序位专法连续原文'})
    (runtime/name).write_bytes(enc(d))
m=load(runtime/'manifest.json')
m.update(release=NEW,parentRelease=OLD,authoringSource=p['authoringSource'],quantityLogic=contract)
if 'bookRetrieval' in m:m['bookRetrieval']['compatibleMethodRelease']=NEW
m['modules']['quantity']['trigger']='原问要求数量、连续量、名次/序位、等第或变化量；数值目标不要求有形实物'
m['modules']['quantity-rank']={'file':'references/quantity-rank.md','required':False,'requires':[],
 'title':'名次、等第与变化量取数','trigger':'第几名/进退几名/几等奖等序数任务；查专法及修正方向'}
m['modules']['quantity-rank-evidence']={'file':'references/quantity-rank-evidence.json','required':False,'requires':[],
 'title':'名次取数连续书证QR01—QR07','trigger':'需要核查序位专法原文、来源身份及限制'}
for f in ['references/quantity-rank.md','references/quantity-rank-evidence.json']:m['files'][f]=sha(runtime/f)
# Save all version-bearing documents before calculating the manifest.
m['files']={f:sha(runtime/f) for f in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
(runtime/'manifest.json').write_bytes(enc(m))
p['methodVersion']=m['version']
p['workflowImplementation']={f:current_sha(f) for f in p['workflowImplementation']}
p['files']={f:current_sha('.opencode/skills/'+f) for f in p['files']}
pending['.opencode/liuren-active.json']=enc(p)
# Validate frozen sources and prospective closure before the pointer is changed.
assert all(sha(R/f)==h for f,h in before['frozen'].items())
assert all(sha(runtime/f)==h for f,h in m['files'].items())
for f,h in load(runtime/'loader-contract.json')['sourceHashes'].items():assert current_sha(f)==h,f
for rel in sorted(pending,key=lambda f:f=='.opencode/liuren-active.json'):
    target=R/rel;tmp=target.with_name(target.name+'.quantity46.tmp');tmp.write_bytes(pending[rel]);os.replace(tmp,target)
(O/'after.json').write_bytes(enc({'release':NEW,'runtime':p['runtime'],'methodVersion':p['methodVersion'],
 'files':{f:sha(R/f) for f in before['files']},'frozen45_unchanged':True,'models_unchanged':True}))
print('Activated',NEW,'; frozen45 unchanged; no model calls or website changes')
