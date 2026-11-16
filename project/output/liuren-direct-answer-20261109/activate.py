"""Version the direct-answer contract; preserve frozen runtimes and model choices."""
from pathlib import Path
import hashlib,json,shutil,os
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
OLD='20261109-consistency-39';NEW='20261109-direct-answer-40'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
encode=lambda v:(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
pointer=load(ROOT/'.opencode/liuren-active.json')
assert pointer['release']==OLD
base=ROOT/pointer['runtime'];runtime=ROOT/'runtime/liuren'/NEW
assert not runtime.exists() and not (OUT/'before.json').exists()
manifest=load(base/'manifest.json')
assert all(sha(base/rel)==h for rel,h in manifest['files'].items())
assert all(sha(ROOT/rel)==h for rel,h in pointer['workflowImplementation'].items())
paths=['.opencode/liuren-active.json','opencode.json','.opencode/oh-my-opencode-slim.jsonc','README.md','目录总索引.md','AGENTS.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬高效执行.md','docs/本机六壬稳定运行指南.md','integrations/codex/daliuren-codex/references/host.md']
for rel in paths:
    dest=OUT/'before'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/rel).read_bytes())
frozen={p.relative_to(ROOT).as_posix():sha(p) for p in base.rglob('*') if p.is_file()}
(OUT/'before.json').write_bytes(encode({'release':OLD,'files':{rel:sha(ROOT/rel) for rel in paths},'frozen':frozen}))
shutil.copytree(base,runtime)
policy=(ROOT/'docs/本机六壬直接作答-40.md').read_text('utf-8')
short=('40版直接作答：子智能体开始裁决前采用direct-answer规则，先综合依据再选主判。'
       '是非给是/否或倾向，数值给有依据的最佳估计值和单位，位置结合方向与分野给主选地区，原因给主因；'
       '不以中间类象、候选堆积、反复免责声明代替答案，不把未问的高精度设成拒答门槛。'
       '不随机选边、不编数值或过度定位，敏感隐私不凭盘面臆断。'
       '提交前自查，主智能体在39版answer_constraints复核直接作答及前后未撤回，calculation_scope核估计依据。'
       '主准备保持中性，不能替子智能体选结果；保留一次原子会话补核与未决项。'
       '仅本机OpenCode及共用Codex，新任务加载；网站未发布。详见docs/本机六壬直接作答-40.md。')
# The complete rule is at the start of the mandatory core, before chart reasoning.
for rel in ['references/judgment-core.md','methods/report.md']:
    p=runtime/rel;text=p.read_text('utf-8');heading,rest=text.split('\n',1)
    p.write_text(heading+'\n\n'+policy+'\n\n'+rest,encoding='utf-8')
for rel in ['methods/adjudication.md','references/deterministic-tools.md']:
    p=runtime/rel;p.write_text(p.read_text('utf-8')+'\n\n'+short+'\n',encoding='utf-8')
(runtime/'references/direct-answer.md').write_text(policy,encoding='utf-8')
pending={}
cfg=load(ROOT/'opencode.json');oldcfg=json.loads(json.dumps(cfg))
cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW).replace('runtime\\liuren\\'+OLD,'runtime\\liuren\\'+NEW))
cfg['agent']['liuren']['prompt']=short+'\n'+cfg['agent']['liuren']['prompt']
assert {k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}=={k:(v.get('model'),v.get('variant')) for k,v in oldcfg['agent'].items()}
pending['opencode.json']=encode(cfg)
slim=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc')
slim['agents']['liuren-adjudicator']['prompt']=short+'\n'+slim['agents']['liuren-adjudicator']['prompt']
pending['.opencode/oh-my-opencode-slim.jsonc']=encode(slim)
for rel in paths[3:]:
    text=(ROOT/rel).read_text('utf-8')
    if rel in ['README.md','目录总索引.md']:text=text.replace('指向 `'+OLD+'`','指向 `'+NEW+'`').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/')
    pending[rel]=(text+'\n\n'+short+'\n').encode('utf-8')
def current_sha(rel):return hashlib.sha256(pending[rel]).hexdigest() if rel in pending else sha(ROOT/rel)
contract={'id':'liuren-direct-answer-40','enabled':True,'guide':'references/direct-answer.md','entry':'mandatory-core-and-adjudicator-prompt','review':'existing answer_constraints; semantic review, no automatic verdict','scope':'local-opencode-and-codex','predictiveValidationCount':0}
pointer.update(release=NEW,runtime=runtime.relative_to(ROOT).as_posix(),previousRelease=OLD,backup='output/liuren-direct-answer-20261109/before',authoringSource='output/liuren-direct-answer-20261109',answerDelivery=contract)
pointer['bookRetrieval']['compatibleMethodRelease']=NEW
for name in ['manifest.json','loader-contract.json']:
    d=load(runtime/name);d.update(release=NEW,parentRelease=OLD,answerDelivery=contract,authoringSource='output/liuren-direct-answer-20261109')
    if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=NEW
    if name=='loader-contract.json':d['sourceHashes']={rel:current_sha(rel) for rel in d['sourceHashes']}
    else:
        d['modules']['direct-answer']={'file':'references/direct-answer.md','required':False,'requires':[],'trigger':'直接作答要求和精度缺口；全文已进入必读核心'}
        d['files']['references/direct-answer.md']=sha(runtime/'references/direct-answer.md')
    (runtime/name).write_bytes(encode(d))
for name in ['references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
    d=load(runtime/name);d['release']=NEW;(runtime/name).write_bytes(encode(d))
m=load(runtime/'manifest.json');m['files']={rel:sha(runtime/rel) for rel in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();(runtime/'manifest.json').write_bytes(encode(m))
pointer['methodVersion']=m['version'];pointer['workflowImplementation']={rel:current_sha(rel) for rel in pointer['workflowImplementation']}
pending['.opencode/liuren-active.json']=encode(pointer)
for rel in sorted(pending,key=lambda rel:rel=='.opencode/liuren-active.json'):
    dest=ROOT/rel;tmp=dest.with_name(dest.name+'.direct-answer.tmp')
    with tmp.open('xb') as handle:handle.write(pending[rel])
    os.replace(tmp,dest)
assert all(sha(ROOT/rel)==h for rel,h in frozen.items())
(OUT/'after.json').write_bytes(encode({'release':NEW,'files':{rel:sha(ROOT/rel) for rel in paths}}))
print('Activated',NEW,'; frozen39 unchanged; restart OpenCode for new tasks')
