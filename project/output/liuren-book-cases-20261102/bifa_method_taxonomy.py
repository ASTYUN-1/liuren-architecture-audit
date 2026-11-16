"""Conditional navigation and legacy summary links, without flattening source cards."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/liuren-book-cases-20261102'
GROUPS=[
 ('ROLE','问事与角色定位',[1,17,18,21,22,43,45,117,118,121,126,127,128,133,138],'先定人、物、单位和目标，再用课体及类神；同一象不能跨占类无条件复制。'),
 ('OFFICE','德禄、官职及贵人',[2,3,13,15,16,56,57,58,59,60,61,62,63,64,65,95,129,130,134,135,136,139],'区别薪职、权位、虚名与官类；贵人的位置、空害、救制与正幕条件分别保留。'),
 ('CHAIN','生克传递及先后得失',[7,8,9,10,11,12,47,48,49,53,72,92,93,114],'核生克的施受方向、链条终点和受益对象，比较过程与归计，不把递生递克直接等同吉凶。'),
 ('GHOST','鬼的角色及救制',[4,5,6,19,20,37,38,39,40,41,42,81,82,83,84,109,137],'先分病、官、客来、财等鬼的角色，再辨神制、将救、空制的对象与效力。'),
 ('VOID','空实、落空与天空',[23,24,34,65,73,74,89,98,107,108,112,113,115,116,125],'先定何物何层为空，再定所求有无、阶段与时间尺度；天空不默认等于旬空。'),
 ('MOTION','去就、进退和引从',[14,25,36,66,67,70,71,88,106,122,123,124,125],'宜如何、能否动与实际如何分开，逐一定位方向、路径和夹引对象。'),
 ('BIRTH','胎产角色和已知状态',[26,27,28,29,30,31,46],'孕未孕、已生未生、母子、胎与财等分别取用；人数、生死和产期不互相代替。'),
 ('RELATION','合、离、刑害与内外关系',[32,33,35,55,79,90,91,100,101,117],'固定双方及四点坐标，合离只说明特定对象关系，不能直接替代成败或人格事实。'),
 ('TOMB','墓、死气及人宅病象',[44,51,52,68,75,76,77,80,96,97,104,105,131,137],'坐墓、乘墓、夹墓及死气的参照层不同，病名、生死、家宅和既往已知病情分开。'),
 ('PURSUIT','失脱、闭口与捕逃',[50,54,94],'玄武及阴神、闭口、太阳等需固定对象及链条；获人、放人、获赃不是一项。'),
 ('COMBINE','神将并聚、破网与内战',[69,78,85,86,87,102,103,109,110,111,119,120,130],'多象同向仍须核冲突与救制；课名、病符或一凶象不能代替全部判断。'),
 ('TIME','应期、数量与判验尺度',[29,38,44,50,68,89,99,108,109,110,113,123,129,131,132],'先定迟速和年/月/日/时尺度，再看实际入课的约束；成事和应期分别核验。'),
]
NORMAL=[
 ([13,135],'旺禄守动','135补龙禄与空马年期，13保留一般定义和有效性；同族并读而非删掉细条件。'),
 ([1,136],'日禄归支的角色分流','1以支为他人/单位为主，136增加夫妻空支、德禄绝及朝官/病的不同条件。'),
 ([15,16,139],'斫轮真假与改作别用','15为成立和迟速，16为杨的虚名居处子息，139比较周/朱的吉空凶实与官职类象。'),
 ([4,5,6,137],'鬼制化与并聚','神制、天将救、引鬼传鬼坐标及病课并聚效力不同，不压成有救必免。'),
 ([43,48,92],'互生俱生与互脱','初利末耗、对象主轴与空墓败反制保留；标题近义不取消先后条件。'),
 ([24,89,112,115],'全空与具体类神','空上空、满盘空、五遇、逐类空和天空含义不同，只统一先定对象层次的动作。'),
 ([68,75,104,105],'墓的坐标与冲破','两蛇夹墓、虎墓、地盘坐墓与阴神乘墓不是同一结构；年命冲墓也不能直接代换。'),
 ([29,132,113],'成事与时间分验','产期缓急、信用卡阴阳取日与升迁应月分别保留，不能共享一个固定期数。'),
]
LEGACY=[
 ('德丧禄绝',(1085,1087),[13,95,135,136],'旧摘要只列绝地，本书还须核禄空/乘将、角色与诸凶；不推出所有失职。'),
 ('权摄禄临支',(1089,1091),[1,2,136],'支为我之单位、家或他人不同，吉凶不由临支一项确定。'),
 ('鬼临三四',(1093,1095),[84],'全见与单见、年旬空实及救制分别保留。'),
 ('两蛇夹墓',(1097,1099),[68],'先核夹墓坐标、年命冲墓、逼煞与原病情；不把大凶伏尸压成确定病因。'),
 ('人宅皆死',(1101,1103),[96],'两种死气和实际所问不能被概括为任何住宅不可居。'),
 ('三传递克',(1105,1107),[9,10,11],'仕宦参劾、求财与内战结构分开，非递克一律众人欺。'),
 ('合中犯煞',(1109,1111),[101],'先定合的对象，再核煞和类象；与先应后解等时间条件并读。'),
 ('干神归支',(1113,1115),[25,36,106,107],'干传支、干神归支与上神互传不可互换；守动还看目标、丁马及空实。'),
 ('年命填空',(1117,1119),[112],'原摘要填实无条件化；本书逐类区分空之喜惧、年命与月建等，不套必然解空。'),
 ('制鬼良医',(1121,1123),[82],'救神角色和位置、空实及财多反伤另核，不保证治疗效果。'),
]
def ref(p,a,b):
 raw=(ROOT/p).read_bytes();ls=raw.decode('utf-8-sig').splitlines()
 return dict(path=p,line_start=a,line_end=b,quote='\n'.join(ls[a-1:b]),sha256=hashlib.sha256(raw).hexdigest(),role='旧AI归纳')
def enrich(RULES):
 for r in RULES:
  n=int(r['id'][-3:]);r['method_family_ids']=[f'BF26-{key}' for key,_,ids,_ in GROUPS if n in ids]
  assert r['method_family_ids'],r['id']
 for _,_,ids,_ in LEGACY:
  for n in ids:
   r=next(r for r in RULES if r['id']==f'LR26-BOOK-BIFA-{n:03}')
   if 'B0303' not in r['legacy_entry_ids']:r['legacy_entry_ids'].append('B0303')
 for ids,_,reason in NORMAL:
  for n in ids[1:]:
   r=next(r for r in RULES if r['id']==f'LR26-BOOK-BIFA-{n:03}')
   r['relations'].append(dict(type='合并候选',target_id=f'LR26-BOOK-BIFA-{ids[0]:03}',reason=reason+' 此为近义导航，未改来源卡，也未宣告术理等价。'))
def run():
 rules=json.loads((ROOT/'knowledge/liuren-research/20261102/rules/book-bifa.json').read_text(encoding='utf-8'))
 groups=[dict(id=f'BF26-{key}',title=t,common_method=c,rule_ids=[f'LR26-BOOK-BIFA-{n:03}' for n in ids],preserved_branches=[dict(rule_id=r['id'],conditions=r['conditions'],exclusions=r['exclusions'],conclusion=r['conclusion']) for r in rules if int(r['id'][-3:]) in ids],independent_validation_count=0) for key,t,ids,c in GROUPS]
 obj=dict(schema='bifa-conditional-taxonomy-v1',source_method_count=len(rules),families=groups,
  dimensions=['占问目标与角色','结构和施受方向','天地盘与阴阳层次','时令旺衰','神将类象','旬空/落空/天空','救制与反制','已知现实状态','阶段与时间尺度','原断/后述/后析/独立核验'],
  normalization_groups=[dict(common_label=t,rule_ids=[f'LR26-BOOK-BIFA-{n:03}' for n in ids],preserved_difference=note,disposition='导航归组，不删除来源条件') for ids,t,note in NORMAL],
  legacy_mappings=[dict(legacy_entry_id='B0303',subentry=t,source_ref=ref('经验日志/古籍-壬占汇选.md',*br),current_rule_ids=[f'LR26-BOOK-BIFA-{n:03}' for n in ids],disposition='条件化并读；旧AI摘要不冒充本书原话或同源案例',reason=note) for t,br,ids,note in LEGACY],
  untouched_legacy_policy='不修改旧案例或旧摘要；不是全旧库已审，也不以标题匹配将未知条目冒充已映射。',independent_validation_count=0)
 (OUT/'bifa_method_taxonomy.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(families=len(groups),normalized_groups=len(NORMAL),legacy_subentry_mappings=len(LEGACY),covered_rules=len({x for g in groups for x in g['rule_ids']})),ensure_ascii=False))
if __name__=='__main__':run()
