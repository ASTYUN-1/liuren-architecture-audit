from pathlib import Path
import json,hashlib,shutil,os
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
OLD='20261108-clarified-33'; NEW='20261109-palace-strength-34'
BASE=ROOT/'runtime/liuren'/OLD; R=ROOT/'runtime/liuren'/NEW
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def dump(p,d):write(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=load(ROOT/'.opencode/liuren-active.json')
assert p['release']==OLD
assert not R.exists(), 'new release exists; do not overwrite frozen release'
shutil.copytree(BASE,R)

policy='''## 单宫旺衰与取用后补算（34版，主、子共同执行）

默认`strength_index`只表示该对象的单宫旺衰：计月令、对象自身十二气、旬空/坐空以及本宫天地、自己的直接阴神、同宫神将的直接生扶泄耗克制。它不是全局旺衰、取用后的最终作用、成败概率，也不是吉凶分。天将对地盘只有十二气参照，不新增将地生克边；不凭同在课传就互相加减。原局空亡字段保留，已计的空亡不再扣一次。

固定分档：E=0表示本计算没有有效力量（缺失/null不能记0）；0<E<1极弱，通常难独立显著作用；1≤E<2.5弱但仍有作用；2.5≤E<5偏弱至中等可作用；5≤E<7.5较强；7.5≤E≤10强。5是基准，2.5是弱力参考，均非可用/不可用开关。极弱也不删除节点，仍看结构、触发、应期与具体任务；不能以低分直接断事情不成。不得把这些研究分档冒充已验证的自然能量单位或准确率。

实际取用后，其他宫位可能生扶、泄耗或克制类神。先依原法明确双方类神身份、实际影响通路和依据，再调用`liuren_compute(action="strength", strength=...)`补算；不能因五行相生克便自动全盘联算，不能自行估算、手加分或另乘空亡倍率。工具推导生克类型及固定系数，返回单宫分、补算分、差额与分档；主、子均直接采信程序数值，不复核排盘算术。工具不能验证取用理由的专业真伪：模型仍须解释取用、能否兑现及最强反证。取用纠正时，用完整的新关系清单重算，不在上次补算结果上层叠加。原有直接关系工具自动跳过，未提交关系不扩散。

补算沿用原盘月令条件表，季月有双表时说明原法依据并沿同表比较，不按得分高低择表；需敏感性比较则两表各算且分别解释，不平均、不计两票。时间改变另按U10查应期，当前补算不自动更新时柱或旬空。三合/半合/三会数值继续暂缓。

单宫E与对某对象的实际作用分层：官鬼、财、父母的直接贪生合及制救仍依U03/U06；自身旺不保证能为我用，弱也不等于不能用。补算已适配的直接贪生/合绊降低对外传递，尚未量化的刑冲、神煞、事件条件仍由原法分析，不拿研究分数覆盖。完整定向作用A若为null代表适配不足，不是没有作用。

仅在需要给出取用后的数值增减时强制调用补算，不把所有盘面关系变成新待办。主智能体准备保持中性，裁决者可改候选类神并调用同工具；主智能体核对分数含义、关系依据和口径一致性，不重新折中改判。详细参数及调用例见`deterministic-tools`，工程接口不限制自由裁决报告。
'''
example={"action":"strength","strength":{"mode":"selected_relations","season_profile":"quarter-earth","season_basis":"本问按所用原法采用季土条件表","actors":[{"id":"T:酉","role":"假设施助方","basis":"示例：经原法取用并确认施助身份"},{"id":"T:子","role":"假设目标类神","basis":"示例指定，非本课实际裁决"}],"links":[{"source":"T:酉","target":"T:子","basis":"示例：确认此施助方对目标存在生扶通路"}]}}
guide=policy+'''
### 工具参数与计算含义

`mode=single_palace`仅查询，给actors并省略links。`mode=selected_relations`必须给非空links；actors每项为`id/role/basis`，links每项为`source/target/basis`。T表示天盘支、J表示天将、S仅本日日干；不接受地盘D作为跨宫施受者。source是施生、施克或比和方，程序自行定类型，反向输入、重复关系、未取用对象或自定系数均拒绝。主智能体在OpenCode须带完整`archive`，裁决者自动用绑定盘而不填archive。

示例仅演示已经完成取用后的“金生子水”，不主张本案应取酉为施助者：

```json
'''+json.dumps(example,ensure_ascii=False,indent=2)+'''
```

Codex子智能体使用`node tools/liuren-codex.mjs --request 请求文件`，请求为`{"action":"compute","run":"本任务run绝对路径","request":上述对象}`。主智能体未建run时也可调用，省略run而在request中附可信盘的完整archive；沿用归档hash，不重新排盘。两宿主共用算法，调用结果留回执；旧绑定核心未含本版单宫算法的任务不混用新补算。

补算固定本宫已算平衡，令L_i=B_i+单宫净作用，H为通达系数，V为空亡保留率，则 E'_i=V_i×clip[0,10](H_i×(L_i+Σ新增受力−Σ新增施力耗费))。不是把已经扣空的E再乘一遍V。未取用宫位保持原单宫观察，不自动连锁传播；同次多个明确关系共同迭代，从0/5/10多初值验算收敛。每次请求是完整关系快照，不读取前次结果叠加。

新增通路系数固定0.75，同施者通路合计超过2时按比例归一。沿用研究参数：生入0.20×g×源分×τ，源泄0.10×g×源分×τ；克入−0.20×g×源分×τ/(1+受者分/5)，施克耗为克量绝对值×0.20；比和0.06×g×min(源分,源基础种子)。τ沿源节点已适配的直接贪生合限制取1−goal_loss，生与克均考虑；未适配的专项不冒充已量化。此处系数为工程研究约定，并非原书已有精确比例。

读返回的actors.single_palace、adjusted、delta、level及applied_relations；already_local_or_blocked说明本次未重复叠加的直接关系或初末时序限制。普通交付不贴全部审计迭代账；有疑问再查回执。任何分数都不能直接换算是否录用、职位或行业。
'''
# Replace stale prohibitions only in the new professional package.
old='生处、坐处、制处和承接条件共同分析，未确立数值能量单位、固定加权或胜负阈值，禁止伪造方程。'
new='生处、坐处、制处和承接条件共同分析；现采用34版固定研究算法描述单宫旺衰，并由工具依明确取用关系补算，模型不得自创系数或胜负阈值。该指数不是已验证的自然能量单位，不替代原法裁决。'
for f in R.rglob('*.md'):
 s=f.read_text('utf8').replace(old,new)
 # This is a method digest, not an alteration of the quoted evidence archive.
 s=s.replace('两者分列，不合成一个分数。','两者原始状态分列；34版允许工具按固定研究式综合成单宫指数，不称原文已有数值单位。')
 if f.name=='adjudicator-prompt.md':s=s.replace('程序表覆盖全部十二支与十干。','正式盘列十二宫及本日日干，其他天干不默认输出。')
 write(f,s)
for rel in ['references/judgment-core.md','references/confirmed-judgment-policy.md']:
 f=R/rel;write(f,f.read_text('utf8')+'\n\n'+policy)
f=R/'references/deterministic-tools.md';write(f,f.read_text('utf8')+'\n\n'+guide)
f=R/'references/adjudicator-prompt.md';write(f,f.read_text('utf8')+'\n\n'+policy)

short='34版单宫旺衰：默认分数仅为单宫直接关系的旺衰，5/2.5均非失用阈值，弱仍可作用。明确取用和跨宫作用依据后，必须调用liuren_compute(action=strength)补算，不自行加减、不重复扣空、不全盘五行联算。先读共用judgment-core，接口见deterministic-tools；三合/半合/三会数值继续暂缓。'
for rel in ['.opencode/skills/liuren/daliuren/SKILL.md','integrations/codex/daliuren-codex/SKILL.md','integrations/codex/daliuren-codex/references/host.md']:
 f=ROOT/rel;write(f,f.read_text('utf8')+'\n\n'+short+'\n')
cfg=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc');cfg['agents']['liuren-adjudicator']['prompt']=(R/'references/adjudicator-prompt.md').read_text('utf8');dump(ROOT/'.opencode/oh-my-opencode-slim.jsonc',cfg)
cfg=load(ROOT/'opencode.json');cfg['agent']['liuren']['prompt']+='\n'+short;dump(ROOT/'opencode.json',json.loads(json.dumps(cfg,ensure_ascii=False).replace(OLD,NEW)))

note='\n\n34版单宫旺衰接入（'+NEW+'）：'+short+' 仅本机，新OpenCode进程/新Codex任务使用新绑定；历史包和原盘不改。详细计算及回滚见output/liuren-palace-integration-20261109/接入说明.md。\n'
for rel in ['AGENTS.md','README.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md','docs/Codex大六壬工作流.md']:
 f=ROOT/rel;s=f.read_text('utf8');s=s.replace('指向 `'+OLD+'`','指向 `'+NEW+'`');write(f,s+note)
f=ROOT/'目录总索引.md';write(f,f.read_text('utf8').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/'))
f=ROOT/'docs/综合旺衰研究计算器.md';s=f.read_text('utf8').replace('默认入口未切换，所以停止使用`liuren-strength.mjs`即回到现行导出。','34版默认盘已接入v05单宫指数；独立研究CLI仍可输出详细定向A，不能把其适配缺口当单宫指数缺失。回退需按34版回滚说明恢复活动入口与工具。');write(f,s+'\n\n'+guide)
write(OUT/'计算规则与工具调用.md',guide)

meta={**p['confirmedJudgmentPolicy'],'id':'liuren-palace-policy-34','numericPolicy':'single-palace-and-selected-relations-v1'}
for name in ['loader-contract.json','manifest.json']:
 d=load(R/name);d.update(release=NEW,parentRelease=OLD,authoringSource=OUT.relative_to(ROOT).as_posix(),confirmedJudgmentPolicy=meta)
 if 'computeInterface' in d:d['computeInterface'].update(release=NEW,strengthAction=True)
 if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=NEW
 if name=='loader-contract.json':d['sourceHashes']={rel:sha(ROOT/rel) for rel in d['sourceHashes']}
 dump(R/name,d)
for rel in ['references/shensha-policy.json','reading-route.json','references/confirmed-policy-register.json']:
 f=R/rel;d=load(f);d['release']=NEW;dump(f,d)
m=load(R/'manifest.json');m['files']={rel:sha(R/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(R/'manifest.json',m)
p.update(release=NEW,runtime=R.relative_to(ROOT).as_posix(),previousRelease=OLD,backup=(OUT/'before').relative_to(ROOT).as_posix(),authoringSource=OUT.relative_to(ROOT).as_posix(),methodVersion=m['version'],confirmedJudgmentPolicy=meta)
if 'bookRetrieval' in p:
 p['bookRetrieval']['compatibleMethodRelease']=NEW;p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
if 'computeInterface' in p:p['computeInterface'].update(release=NEW,strengthAction=True)
p['files']={rel:sha(ROOT/'.opencode/skills'/rel) for rel in p['files']}
for rel in ['tools/liuren-palace-strength.mjs','tools/liuren-strength-engine.mjs','tools/liuren-strength-rules.mjs','tools/liuren-strength-profile.json','tools/liuren-codex.mjs']:p['workflowImplementation'][rel]=sha(ROOT/rel)
p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']}
p['chartPresentation'].update(numericProfile='liuren-palace-strength-v1',evidence=OUT.relative_to(ROOT).as_posix(),strengthScope='single-palace; selected cross-palace links require strength tool',bandsReference=5)
before=load(OUT/'before.json');assert all(sha(BASE/rel)==h for rel,h in before['frozen'].items())
tmp=ROOT/'.opencode/liuren-active.palace34.tmp';dump(tmp,p);os.replace(tmp,ROOT/'.opencode/liuren-active.json')
dump(OUT/'activation.json',{'release':NEW,'previous':OLD,'methodVersion':m['version'],'frozen33Intact':True,'paidModelCalls':0,'predictiveValidationCount':0})
print('Activated',NEW)
