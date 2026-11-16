"""Publish source-backed local methods as a new frozen version, active pointer last."""
from pathlib import Path
import hashlib,json,shutil,os
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
OLD='20261109-direct-answer-40';NEW='20261111-book-logic-41'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
encode=lambda v:(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
pointer=load(ROOT/'.opencode/liuren-active.json');assert pointer['release']==OLD
base=ROOT/pointer['runtime'];runtime=ROOT/'runtime/liuren'/NEW
assert not runtime.exists() and not (OUT/'before.json').exists()
manifest=load(base/'manifest.json')
assert all(sha(base/rel)==h for rel,h in manifest['files'].items())
changed_early=['tools/liuren-method-tools.mjs','tools/liuren-method-registry.json','tools/tests/liuren-codex.test.mjs']
for rel,h in pointer['workflowImplementation'].items():
 assert sha(OUT/'before'/rel if rel in changed_early else ROOT/rel)==h,rel
paths=['.opencode/liuren-active.json','opencode.json','.opencode/oh-my-opencode-slim.jsonc','README.md','目录总索引.md','AGENTS.md',
 'docs/本机六壬高效执行.md','integrations/codex/daliuren-codex/references/host.md','tools/liuren-compute-schema.mjs',*changed_early]
for rel in paths:
 dest=OUT/'before'/rel
 if rel not in changed_early:
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/rel).read_bytes())
 assert dest.is_file()
frozen={p.relative_to(ROOT).as_posix():sha(p) for p in base.rglob('*') if p.is_file()}
(OUT/'before.json').write_bytes(encode({'release':OLD,'files':{rel:sha(OUT/'before'/rel) for rel in paths},'frozen':frozen}))
shutil.copytree(base,runtime)
for name in ['book-logic.md','quantity-strength.md','void-class-applications.md','book-annotation-evidence.json']:
 shutil.copyfile(OUT/name,runtime/'references'/name)
core='''## 第41版书中批注：共同执行的增补

本轮用户指定采用《理法简易》24处批注及连续上下文，详见book-logic、quantity-strength、void-class-applications和book-annotation-evidence。仍依U01—U11与本问domain，以下是明确补充，不要求每案读全部新页。

- **表里与阴神**：阳显阴藏可用于人、物和项目的表面/内部条件。沿真实类神—直接阴神，分察扶类、益我、制伤、原因及承接；人的心理只是合题候选，不能把所有阴神固定作心事。阴神扶类不等于事情必为我得；不得无限递推。
- **发用与气势**：发用的月令五气、所临地盘、乘将和已采用神煞共同察发动、快慢、规模、虚实及持续；单宫指数不是整体气势。虎急烈、蛇迟缠是表现趋势，速度不等于吉凶。发用可以制干上鬼等四课节点，但须有对象、通路、施受状态和时序依据，采用跨宫作用后调用strength补算。
- **神将与类聚**：神克将是减权减力，不一概归零。传统神将吉凶名目只作倾向，重要判断以旺衰、结构、实际作用与制救为主；不凭青龙吉、勾陈凶定结果。类聚按共同实际作用，不数同名多票、不把“加倍”变成无据数值倍数。
- **类神、施受与结构**：类神不入课传仍按占类到完整盘、已核年命等有据位置寻类，通常降低显明性/直接参与程度，不单凭不现断败；失盗等专项保留类神优先。施者资源与意愿、受者能力、通路分开，能制不保证有益。课体名只作起机/结构，不作成败开关。
- **迟速与属性**：关键类神的初中末位置及临身/承接位置可辅助迟速，须结合事件阶段、气态和阻碍；财临门等保留原入课传条件，跨占类说明迁移理由。四建分工仍按U09，不设普遍固定快慢顺序。新旧、难易、数量分别推理，不都改写成吉凶。
- **年命与动**：命偏固有、年偏当前，当前可超一年；一般当前事行年较切题，专项不一律年胜命。动包括有据的调动、转岗、晋升等状态转换；关墓空及入庙核具体限制、有效冲解和无绊条件，启动与到达/受益分别答。季关神沿S33，不与罗网混同。
- **取数和旺衰分层**：数值任务在基数后主动核综合旺衰及空亡数量修正。strength计空不代表quantity已减数；“不重复扣空”只禁止同一计算层重复扣减。具体数量比例须原法或用户明确约定，禁止指数/5等自创换算。LF3329-class-ground保留本段相乘不倍、休加、囚死加后折半、旺倍进幅度未定，不与CY501混用。工具calculation_scope明确本次是否执行数量修正；最终核基数、修正及真实回执。
- **空亡逐类推**：分对象、坐标、所求/所忧、影响环节、气地通路和时间，按U08/U10综合；病空与身空、占产与占孕、龙将空与财爻空不可混。关键空亡影响结果而摘要不足时读void-class-applications。神生其将且神自空“出旬可望/出旬亦无望”为V41-01真冲突，用户已决定先保留现行、以后自行研判；本版不改口径，也不反复要求用户确认。

决定性采用上述推广而条件不足时，定点读相应连续方法/原段。原书、北海解释、用户本轮修订及整理者推广分别保留，不把“反馈贴近”作为独立效果证明。
'''
p=runtime/'references/judgment-core.md';text=p.read_text('utf-8');heading,rest=text.split('\n',1)
text=heading+'\n\n'+core+'\n'+rest
text=text.replace('原局空亡字段保留，已计的空亡不再扣一次。','原局空亡字段保留，已计入本次旺衰指数的空亡不在同一指数重复扣；这不表示另行取出的数量已经做了空亡数量修正，数量层见quantity-strength。')
p.write_text(text,'utf-8')
def append(rel,text):
 p=runtime/rel;p.write_text(p.read_text('utf-8')+'\n\n'+text.strip()+'\n','utf-8')
links={
 'methods/liqi.md':'41版：表里阴神、神将权能、发用气势及施受双方见book-logic。名将吉凶只作倾向；单宫指数不代整体气势，发用可对四课有据制救。按本问实际关系及U规则执行。',
 'methods/positioning.md':'41版用户修订：类神不入课传不单凭不现断败；继续在完整盘、已核年命等有据位置寻类，降低显明性/直接参与程度，特殊占类仍保留专类优先。保持真实坐标，不无限换神。详见book-logic。',
 'methods/movement.md':'41版：阴阳表里及直接阴神通法、发用对四课作用、非地理状态转换的动、关墓空入庙及有效冲解条件，见book-logic。能启动、能转换、能到任及能受益分别论。',
 'methods/timing.md':'41版：类神初中末及临身、入宅、临门辅助相对迟速，结合阶段与气态，财临门原有入课传条件不得丢失。推广其他关键类神须说明临近和承接机制；太岁月建等不构成全局固定快慢阶梯。身弱待身旺、类弱待类旺要看实际瓶颈。详见book-logic；数理时长同时核quantity-strength。',
 'methods/quantity.md':'41版：数值题必须查quantity-strength。strength计空不表示quantity已减数；区分状态层、数法层、数量修正层。基数后核气态及空亡是否另需有据修正，禁止遗漏或同层重复折减。新增LF3329-class-ground与CY501分支分开；calculation_scope=false表示本次未算，不代表本案不必考虑。',
 'methods/void.md':'41版：已连读《理法简易》空亡全节及寄宫续论，分占类条件见void-class-applications。V41-01同条件出旬两说真实相反，用户明确先保留现行U08/U10，后续自行研判；不另设可得/不得开关。空的数量修正与指数计空另见quantity-strength。',
 'methods/adjudication.md':'41版：依核心核类神/阴神、发用气势、施受、神将与空亡的实际作用。数值任务定点读quantity-strength，不将基础数冒充已修正结果。calculation_scope复核基数与各项修正是否确有回执；一次补核协议及模型设置不变。',
 'methods/report.md':'41版数值交付补核：基数、指数所算范围、数量修正及其依据分别记录。已计旺衰空亡不等于已执行数值折减；不能遗漏有据修正或同层重复扣减。41版源段/用户推广身份和V41-01保留现行的状态应如实说明。',
 'references/quantity-sources.md':'41版增补：本书LF-U3319—3347与CY501的相气倍率不同，具名LF3329-class-ground执行本段明晰分支；旺倍进幅度及3331“旺相/相”交叠另存校勘。空亡数量修正见quantity-strength，不能把指数计空当已减数。',
 'references/deterministic-tools.md':'41版：methods(quantity)现有5个分支，新增LF3329-class-ground；目标可为有据选定关键类神，不强制初传/入传。旺仅基础数、相相乘、休相加、囚死相加折半。具名取数回执新增calculation_scope，明确未读取综合指数/未作空亡数量修正。额外有据数值修正另次调用quantity expression，见quantity-strength。',
 'references/jiang-symbols.md':'41版LF-U3079：白虎偏急烈，螣蛇偏迟缠，按占类和实际状态作速度/表现候选。用户采用传统吉凶名目仅作倾向，重要判断看旺衰、结构、实际作用和制救。类聚不按名称数票，详见book-logic。',
 'references/void-method-conditions.md':'41版新增完整分类见void-class-applications；原空鬼附煞段与凶空免患段先分作鬼/附煞、对象和目标，尚不足证同条件互斥，不机械生成待用户问题。V41-01出旬冲突由用户决定保留现行待后研判。',
 'domains/finance.md':'41版：本问关键财类、类阴、与财者及其阴神依book-logic分看。财不现不单凭该项断败；施者愿给但资源弱与受者无力取分别论。问金额读quantity-strength，基数之后核实际气态和有据数量修正。',
 'domains/relationship.md':'41版相貌子问简要采用《理法简易》LF-U4189—4219：传统女性婚占以天后所乘察较稳定禀受，行年上神察当前外貌；五行、支、乘将及气地合参。迁移其他人先核角色依据；单象不定美丑，不由外貌断品德、私生活或医学状况。身高数值仍读quantity。原文与条件见book-logic。',
 'domains/travel.md':'41版：关墓、空、天官入庙的限制与冲解须合气态和无绊条件；动也可按用户约定指非地理状态转换。先固定本问动身/抵达/办成的目标。详见book-logic及void-class-applications。',
 'domains/promotion-salary.md':'41版：职位、职责或状态转换可属动，不须伴随地理远行；关墓空的实际限制及有力冲解按book-logic，启动、到任和获益分答。承办者能力和意愿与本人取得能力分看。',
 'domains/recruitment.md':'41版：岗位供给、承办者实际资源、求职者取得能力、承诺与落实条件分看；阴神可察内部支持/限制，不据盘断第三方秘密想法。录用、报到与岗位转换分别论。见book-logic。',
 'domains/illness.md':'41版空亡补充：病空与患者身、禄马、医药救神空分别定位，新病/久病按事实不按年龄；阶段、作用及反证见void-class-applications，不由单项空亡下死亡结论。',
 'domains/pregnancy.md':'41版空亡补充：求孕与已孕占产、胎与产妇及救应分开；胎空产速/孕难不属同条件冲突。详见void-class-applications，不由单项胎空推医学异常。'
}
for rel,text in links.items():append(rel,text)
# Remove an unconditioned old shorthand instead of leaving competing live instructions.
p=runtime/'references/nianming.md';text=p.read_text('utf-8')
a=text.index('- **日命相克之辨**：');b=text.index('\n## ⑤',a)
text=text[:a]+'''- **年命与日课关系**：看所求类神、本人及年命上神分别受何作用；能制有时为取财或去害，被制也可能有利于去病鬼。旧摘要“日上克命上必吉、命上克日上必凶、日克行年上必凶”未保留占类条件，本版不作通用开关。
- 课传与年命生合或刑克须核施受、气地及实际目标，不把符号替代结果。

## 命固有、年当前（41版）

《理法简易》LF-U3783—3805：命主生平，年关当前。占事时可将本命理解为较稳定/固有一面、行年理解为当前阶段，其“当前”可超过一年。一般眼前事务行年较切题，仍按本问占类职责，不规定年永远重于命；生死、行人等原段另有专项。此处不恢复出生推命，不由本命单项给人格定论。

年命及其上神真正在课传出现、或恰为关键类神，支持事情切身/显明；须标清实际槽位，不能以年命本来就有上神循环证明“入课”。行年资源、本人承受和类神作用都看：年命制类可为取财或制害，类制年命可能受害，也可能有原占类的其他关系，不脱离实际目标判吉凶。

年命冲合引动须核冲者气态及所开关墓/合绊，详见book-logic。相貌只在问到时简要查relationship及本书LF-U4189—4219；孤寡、破、克等单名不径断现实贫困、独身或生死。
'''+text[b:]
p.write_text(text,'utf-8')
p=runtime/'references/pending-conflicts.md';text=p.read_text('utf-8').replace('本轮未新增已证实的同条件互斥理论命题；','此前33版复核未新增已证实的同条件互斥理论命题；')
text+='\n\n## V41-01 新登记的真实冲突：保留现行，待用户后续研判\n\n理法简易LF-U3217所引“神生其将，而神自作空者，尚有出旬之可望”，3221北海明确反驳“出旬亦无望”。同组合同实现问题直接相反。用户2026-11-11回复：“此处先保留现行，后续由我仔细研判。”本版继续U08/U10，不另取绝对规则、不重复催问；连续原文见book-annotation-evidence，其他表面差异的分层见void-class-applications。\n'
p.write_text(text,'utf-8')
short='41版书中批注接入（20261111-book-logic-41）：补类神阴阳、发用气势、施受能力、迟速/年命与非地理动。神将名目只作倾向；数值任务查quantity-strength，指数计空不等于数量已减数，新增LF3329独立分支及计算范围回执。空亡逐类与阶段见void-class-applications，V41-01按用户决定保留现行U08/U10待后研判。24处连续书证和接入说明见output/liuren-book-integration-20261111/。仅本机新任务，网站未发布；冻结旧版与模型选择不变。'
pending={}
cfg=load(ROOT/'opencode.json');oldcfg=json.loads(json.dumps(cfg))
cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW).replace('runtime\\liuren\\'+OLD,'runtime\\liuren\\'+NEW))
cfg['agent']['liuren']['prompt']=short+'\n'+cfg['agent']['liuren']['prompt']
assert {k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}=={k:(v.get('model'),v.get('variant')) for k,v in oldcfg['agent'].items()}
pending['opencode.json']=encode(cfg)
slim=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc');slim['agents']['liuren-adjudicator']['prompt']=short+'\n'+slim['agents']['liuren-adjudicator']['prompt'];pending['.opencode/oh-my-opencode-slim.jsonc']=encode(slim)
for rel in ['README.md','目录总索引.md','AGENTS.md','docs/本机六壬高效执行.md','integrations/codex/daliuren-codex/references/host.md']:
 text=(ROOT/rel).read_text('utf-8')
 if rel in ['README.md','目录总索引.md']:text=text.replace('指向 `'+OLD+'`','指向 `'+NEW+'`').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/')
 pending[rel]=(text+'\n\n'+short+'\n').encode('utf-8')
rel='tools/liuren-compute-schema.mjs';text=(ROOT/rel).read_text('utf-8')
old='CY501-use-ground、WY244-month为初传分支；另两项仅基础步。旺衰读取月令五气，非综合指数。'
new='CY501-use-ground、WY244-month为初传分支；WY67/WY242仅基础步；LF3329-class-ground为选定类神与地盘分支。旺衰读取月令五气，非综合指数。calculation_scope说明未执行的空亡数量修正；有据修正另次expression，不以指数计空冒充数量已修正。'
assert text.count(old)==1;pending[rel]=text.replace(old,new).encode('utf-8')
for rel in changed_early:pending[rel]=(ROOT/rel).read_bytes()
def current_sha(rel):return hashlib.sha256(pending[rel]).hexdigest() if rel in pending else sha(ROOT/rel)
contract={'id':'book-annotation-41','selections':24,'continuousSourceSpans':13,'evidence':'references/book-annotation-evidence.json',
 'modules':['book-logic','quantity-strength','void-class-applications'],'userDecision':'V41-01 preserve U08/U10; deferred user review',
 'predictiveValidationCount':0,'fullBookCoverage':False,'scope':'local-opencode-and-codex'}
pointer.update(release=NEW,runtime=runtime.relative_to(ROOT).as_posix(),previousRelease=OLD,backup='output/liuren-book-integration-20261111/before',authoringSource='output/liuren-book-integration-20261111',bookAnnotationIntegration=contract)
pointer['bookRetrieval']['compatibleMethodRelease']=NEW
modules={'book-logic':('references/book-logic.md','阴阳表里、发用气势、类神/课传、施受、迟速及动的推广需要细则'),
 'quantity-strength':('references/quantity-strength.md','数值任务的旺衰/空亡数量修正；与quantity共同读取'),
 'void-class-applications':('references/void-class-applications.md','空亡对象、环节或跨占类条件将影响判断且摘要不足'),
 'book-annotation-evidence':('references/book-annotation-evidence.json','24处原连续段及本轮身份需要核对')}
for name in ['manifest.json','loader-contract.json']:
 d=load(runtime/name);d.update(release=NEW,parentRelease=OLD,bookAnnotationIntegration=contract,authoringSource='output/liuren-book-integration-20261111')
 if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=NEW
 if name=='loader-contract.json':d['sourceHashes']={rel:current_sha(rel) for rel in d['sourceHashes']}
 else:
  for key,(file,trigger) in modules.items():
   d['modules'][key]={'file':file,'required':False,'requires':[],'trigger':trigger};d['files'][file]=sha(runtime/file)
  # Quantity tasks must load the detailed correction rule, including via --condition quantity.
  d['modules']['quantity']['requires']=list(dict.fromkeys(d['modules']['quantity'].get('requires',[])+['quantity-strength']))
 (runtime/name).write_bytes(encode(d))
for name in ['references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
 d=load(runtime/name);d['release']=NEW
 if name=='references/confirmed-policy-register.json':d['bookAnnotationIntegration']=contract
 if name=='reading-route.json':
  for key,(file,trigger) in modules.items():
   d['labels'][key]=trigger;d['conditional'][key]={'stage':2,'trigger':trigger,'selectWith':'--condition '+key,'beforeRequired':'adjudication'}
  d['conditional']['quantity']['trigger']+='；同时读取quantity-strength，区分状态计空与数量修正'
 (runtime/name).write_bytes(encode(d))
m=load(runtime/'manifest.json');route=load(runtime/'reading-route.json')
m['required']=[key for stage in route['stages'] for key in stage['required']]
m['conditional']={key:item['trigger'] for key,item in route['conditional'].items()}
m['files']={rel:sha(runtime/rel) for rel in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();(runtime/'manifest.json').write_bytes(encode(m))
pointer['methodVersion']=m['version'];pointer['workflowImplementation']={rel:current_sha(rel) for rel in pointer['workflowImplementation']}
pending['.opencode/liuren-active.json']=encode(pointer)
for rel in sorted(pending,key=lambda rel:rel=='.opencode/liuren-active.json'):
 dest=ROOT/rel;tmp=dest.with_name(dest.name+'.book41.tmp')
 with tmp.open('xb') as handle:handle.write(pending[rel])
 os.replace(tmp,dest)
assert all(sha(ROOT/rel)==h for rel,h in frozen.items())
(OUT/'after.json').write_bytes(encode({'release':NEW,'files':{rel:sha(ROOT/rel) for rel in paths}}))
print('Activated',NEW,'; frozen40 unchanged; restart OpenCode for new tasks')
