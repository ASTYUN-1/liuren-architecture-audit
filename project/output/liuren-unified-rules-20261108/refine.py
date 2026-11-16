from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;R=ROOT/'runtime/liuren/20261108-unified-32'
def write(p,s):p.write_text(s,encoding='utf8')
def load(p):return json.loads(p.read_text('utf-8-sig'))
def dump(p,x):write(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def change(p,a,b):
 s=p.read_text('utf8');assert a in s,(p,a);write(p,s.replace(a,b))
assert len(load(R/'references/confirmed-policy-evidence.json')['evidence'])==18, 'One-time refinement already applied; do not overwrite its backups'
# Register the additional concrete contradictions uncovered during the update.
additional='''
| C08 | 胎神专项与通用十二气是否同一术语：pregnancy的D02；《毕法》1463—1467土胎子午并取 | U04的干/支将十二气表已定，不重新开放。待确认专项“胎神/互胎格”是否另有独立取类法；日干状态不得再退回五行表，亦不能按喜欢的胎位双取。 |
| C09 | 应期视用还是视末：timing“ce-lli视用vs视末”旧整理 | 旧文把二者解释为事未动/事已动的分工，但本轮尚未找到该划分的完整书证。保留为待核解释，不能写成已定裁决法。需核连续原文，再定何事件节点适用何法。 |
| C10 | 取类的排除与扩展：positioning所引金针“不作为类象”与神将/支神取类；classical-mapping卡D03 | 候选抽象义与本题直接类神是否不同层次，须逐条查明。不能从“不作为类象”推出整支不取，也不能用通用象辞绕过专项明确排除。 |
| C11 | 文本疑误而非已证明的术理分歧：shenjiang-use巳章两句阴阳吉凶相反；agriculture D04蚕丝寅卯申异文、吴四公戌亥差别；timing“河SA合”异文 | 不采疑字生成通断，原书保持原字。需版本或扫描校勘；这是资料待校，不能靠模型折中、投票或改盘解决。 |
'''
p=R/'references/pending-conflicts.md';s=p.read_text('utf8');needle='\n行号说明：';assert needle in s;write(p,s.replace(needle,'\n'+additional+needle))
for p in list(R.rglob('*.md'))+[ROOT/'.opencode/skills/liuren/daliuren/SKILL.md',ROOT/'integrations/codex/daliuren-codex/SKILL.md',ROOT/'integrations/codex/daliuren-codex/references/host.md',ROOT/'AGENTS.md',ROOT/'README.md',ROOT/'docs/本机六壬高效执行.md',ROOT/'docs/本机六壬完整研判流程.md',ROOT/'docs/本机六壬稳定运行指南.md',ROOT/'docs/Codex大六壬工作流.md']:
 s=p.read_text('utf8');s=s.replace('C01—C07','C01—C11');write(p,s)
change(R/'methods/positioning.md','涉及土胎取类仍按mapping-provenance D02的未决条件，不双取凑答案','干支十二气统一采用U04；专项胎神是否另属独立取类见C08，不双取凑答案')
change(R/'domains/pregnancy.md','待辨：通用讨论可先列北海理法五行法为默认研究口径；实际胎产条文中另起例须明示，待专项校勘后才能固化计算。','本版采用：通用状态按U04，日干天干阳顺阴逆、支将五行顺行，不能再任择土随水火。尚待辨的是专项胎神/互胎格是否另有独立取类法，见C08；此处原书差异保留为来源。')
change(R/'methods/timing.md','两法并存按事态阶段择用，标注出处。','这项按阶段划分属于旧整理解释，尚待核连续原文，登记C09，不能按结果方便直接择用。')
change(R/'methods/timing.md','**空亡选法未决**：同条件下生扶/填实与有生亦空可能有真实冲突，按空亡模块“生扶、填实与实现的选法分路”','**空的具体实现条件C04**：U08/U10的综合分析及时间变化已定；生扶/填实在何种组合足以落实，仍须核空亡模块的原法条件')
change(R/'methods/liqi.md','遇到土寄生、阴阳顺逆、月令用节月还是其他约定等资料分歧，使用程序已选定口径；只有尚未确定且会改变本问的专业解释分歧才给条件分支','通用土寄生与阴阳顺逆按U04已定，历法沿可信程序盘；只有C05季土细分、C08专项胎神等尚未确认且会改变本问的边界才列具体条件')
change(R/'methods/void.md','保留批评强度；与讲义的直接张力尚未化解，不虚构“特殊生才解空”或著作年代先后','原文强度保留，执行按U01/U08，不把绝对强语当开关；只有具体实现边界列C04，不虚构“特殊生才解空”或著作年代先后')
# Make adoption status explicit before the book summary can be mistaken for active alternative instructions.
for name in ['references/adjudicator-book-basis.md','references/adjudicator-prompt.md']:
 p=R/name;s=p.read_text('utf8').replace('E18《六壬笔记》有十二长生以日干为准','E18【总参照不采用】《六壬笔记》有十二长生以日干为准');write(p,s)
cfg=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc');cfg['agents']['liuren-adjudicator']['prompt']=(R/'references/adjudicator-prompt.md').read_text('utf8');dump(ROOT/'.opencode/oh-my-opencode-slim.jsonc',cfg)
e=load(R/'references/confirmed-policy-evidence.json')
spans=[('SP01','书籍库/北海闲人/理法简易.txt',803,819,'衰得生扶、直接临生临合及官鬼停害'),('SP02','书籍库/北海闲人/理法简易.txt',821,849,'生克刑合并行与所乘将条件，原文强语保留'),('SP03','书籍库/北海闲人/理法简易.txt',4913,4923,'喜旺恶衰、官鬼权威比喻、鬼禁日及仕庶条件'),('SP04','书籍库/北海闲人/毕法赋全解-正式整理本.md',1235,1245,'旺鬼当时时限与喜旺恶衰'),('SP05','书籍库/北海闲人/毕法赋全解-正式整理本.md',1261,1273,'财贪荣与取者旺衰'),('SP06','书籍库/神煞资料/413711725175564精校大六壬指南(珍藏全本).txt',5131,5133,'庄按区分五行长生与十干长生，身份为注解')]
for id,path,a,b,topic in spans:
 src=ROOT/path;rows=src.read_text('utf-8-sig').splitlines();e['evidence'].append({'id':id,'path':path,'encoding':'utf-8-sig','line_mode':'universal','line_start':a,'line_end':b,'quote':'\n'.join(rows[a-1:b]),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'topic':topic,'source_identity':'本地整理/讲解或注解电子文本，依段落分层；非预测效果证据'})
dump(R/'references/confirmed-policy-evidence.json',e)
# Supplemental evidence stays in a separate readable module so each complete method fits sourceMaterial's 16k limit.
write(R/'references/confirmed-policy-supplements.md','# 规则补充连续书据 SP01—SP06\n\n'+ '\n\n'.join('## '+x['id']+' '+x['topic']+'\n\n来源：'+x['path']+'；splitlines '+str(x['line_start'])+'—'+str(x['line_end'])+'；SHA256 '+x['sha256']+'\n\n'+x['quote'] for x in e['evidence'] if x['id'].startswith('SP')))
register=[]
refs={1:[],2:['SP03','SP04','E20','E21'],3:['SP01','SP05','E03'],4:['SP06','E02','E11'],5:['SP02','E04'],6:['E05','E09','E10','E14','E15'],7:['SG03','SG10','SG17','E11'],8:['SG13','SG14','SG15'],9:['SG01','SG02','SG03','SG05','SG06','SG09','SG17','SG18'],10:['SG10','SG11','SP04'],11:[]}
for n in range(1,12):register.append({'id':f'U{n:02}','status':'adopted-local-policy','authority':'用户本轮确认的体系与执行约定；所列书据仅在其实际段落范围支持','evidence':refs[n],'independent_predictive_validation_count':0})
dump(R/'references/confirmed-policy-register.json',{'schema':'liuren-adopted-policy-register-v1','release':'20261108-unified-32','rules':register,'excluded':{'E18-total-reference':'不采用日干总参照','SG07-total-order':'不采用年最小时最大总排序'},'pending':'C01-C11'})
m=load(R/'manifest.json');m['modules']['confirmed-policy-supplements']={'file':'references/confirmed-policy-supplements.md','required':False,'requires':[],'trigger':'U规则具体出处需要核对时；非每案通读'}
for file in ['references/confirmed-policy-supplements.md','references/confirmed-policy-register.json']:m['files'][file]='pending-refresh'
dump(R/'manifest.json',m)
# The bridge's earlier fixed 'professional_content_changed:false' described host migration; report the live policy instead.
p=ROOT/'tools/liuren-codex.mjs';backup=OUT/'before/tools/liuren-codex.mjs';backup.write_bytes(p.read_bytes())
before=load(OUT/'before.json');before['files']['tools/liuren-codex.mjs']=hashlib.sha256(p.read_bytes()).hexdigest();dump(OUT/'before.json',before)
change(p,'modules:Object.keys(manifest.modules),professional_content_changed:false','modules:Object.keys(manifest.modules),professional_content_changed:Boolean(pointer.confirmedJudgmentPolicy),judgment_policy:pointer.confirmedJudgmentPolicy??null')
write(OUT/'待确认矛盾清单.md',(R/'references/pending-conflicts.md').read_text('utf8'))
write(OUT/'已确认判断规则.md',(R/'references/confirmed-judgment-policy.md').read_text('utf8'))
print('Added concrete follow-up findings C08-C11 and verified policy evidence; refreshed role mirror.')
