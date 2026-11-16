"""Reviewed basic definitions; source bytes are never edited."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
enc=lambda x:json.dumps(x,ensure_ascii=False,indent=2)+'\n'
reg=json.loads((O/'before/tools/liuren-bifa-basic-rules.json').read_text('utf-8'))
# 连续章节范围保留定义、旁格和限制，规则定义本身另存，避免摘句充当完整书义。
bs=R/'书籍库/北海闲人/毕法赋全解-正式整理本.md'
bl=bs.read_text('utf-8-sig').split('\n')
starts={int(m.group(1)):i+1 for i,s in enumerate(bl) if (m:=re.search(r'<a id="law-(\d+)">',s))}
# 双法共章，取同一个完整连续章节。
for a,b in [(5,6),(23,24),(59,60),(97,98)]: starts[a]=starts[b]=min(starts[a],starts[b])
endpoints=sorted(set(starts.values()))+[len(bl)+1]
dstarts=[13003,13027,13039,13067,13077,13085,13095,13101,13107,13125,13131,13149,13153,13159,13167,13175,13183,13189,13197,13243,13247,13269,13287,13291,13295,13311,13321,13333,13345,13353,13363,13375,13387,13393,13405,13415,13421,13439,13457,13475,13479,13483,13491,13495,13499,13507,13521,13525,13535,13545,13555,13559,13567,13571,13575,13581,13587,13593,13597,13601,13605,13613,13625,13629,13635,13643,13649,13705,13713,13719,13729,13735,13745,13755,13761,13785,13791,13801,13807,13815,13821,13839,13845,13849,13853,13861,13887,13893,13901,13915,13925,13931,13935,13939,13959,13993,14009,14013,14017,14021]
assert len(dstarts)==100 and len(starts)==100
for tag,source in zip(['D','B'],reg['sources']):
 lines=(R/source['path']).read_text('utf-8-sig').split('\n')
 assert hashlib.sha256((R/source['path']).read_bytes()).hexdigest()==source['sha256']
 source['excerpts']=[]
 for n in range(1,101):
  a=dstarts[n-1] if tag=='D' else starts[n]
  b=(dstarts[n] if n<100 else 14029)-1 if tag=='D' else endpoints[endpoints.index(a)+1]-1
  quote='\n'.join(lines[a-1:b]);assert quote.strip(),(tag,n)
  source['excerpts'].append(dict(id=f'BF-{tag}{n:02}',line_start=a,line_end=b,quote=quote))
rows=[]
def add(key,n,name,op,definition,**args):
 rows.append(dict(id=f'BF{n:02}-{key}',law_number=n,name=name,evidence_ids=[f'BF-B{n:02}',f'BF-D{n:02}'],definition=definition,extended=True,operation=op,**args))
add('stem',1,'初末引从干上','bracket','初末分居干上神前后一辰',target='stem')
add('branch',1,'初末引从支上','bracket','初末分居支上神前后一辰',target='branch')
add('curtain',3,'帘幕贵人临干','curtain','本日另一昼夜贵人支临干；另贵查当前已采用贵人表')
add('usher',4,'催官使者临干','usher','日鬼乘实际白虎临日干；与91、61虎鬼同象去重')
add('warrant',4,'催官符结构','warrant','日鬼临干，三传合财局生该鬼；赴任用途另核')
add('lu',7,'旺禄临干','lu-strong','乙卯、丁午、己午、辛酉、癸子之禄临干；空闭口仍列限制')
add('lu',8,'日禄临支','lu-branch','日干禄临日支；不能由标题断权摄不正')
add('routes',9,'避难逃生取舍核查','method','比较干上、支上、干寄宫所坐地与三传的生财禄、克墓脱空；需依本问选择可走路径')
add('wheel',10,'斫轮基本结构','wheel','卯加申发用；再区分卯自空与坐空')
add('rotten',10,'朽木难雕','rotten','卯加申发用且卯旬空；坐空单列不混称朽木')
add('rescue',11,'课传鬼与子孙制鬼','rescue','相关课传有日鬼、子孙能克该鬼；只确认关系不宣布获救')
add('ghost-parent',11,'传鬼为生','group-parent','三传合鬼局，干上或支上父母承接局生')
add('fox',12,'狐假虎威','fox','干上鬼或脱气，地盘干寄宫克制干上神；离位后的作用由AI判断')
add('season',13,'三传鬼局当四时旺','ghost-season','三传合鬼局且其五行为本季旺气；只确认季令，不承诺不侵')
add('wealth-season',14,'传财当令旺相','wealth-season','三传合财局，按春木夏火秋金冬水之旺相核实；还须比较日主承受能力')
add('double',15,'脱上逢脱','double-drain','干生日上，日上又生所乘天将')
add('thief',15,'脱盗乘玄','drain-thief','干上子孙乘玄武')
add('advance',17,'进茹逢空','advance-void','三传依次进一辰，至少一传旬空或坐空；是否宜退仍核退路')
add('retreat',18,'退茹逢空','retreat-void','三传依次退一辰，至少一传旬空或坐空；全空另列，不混后旬空')
add('stem-fetus',19,'干胎财兼月生气','fetus','本段五行胎：木酉火子金卯水午土子午；干胎作财兼月生气且见干支上或三传',side='stem',dead=False)
add('branch-fetus',19,'支胎兼月生气','fetus','支五行胎兼月生气，见干支上或三传；不强制日财',side='branch',dead=False)
add('fetus-dead',20,'干胎财兼月死气','fetus','干胎作财兼月死气，见干支上或三传；孕产阶段另核',side='stem',dead=True)
add('ding',25,'金日逢旬丁','metal-ding','庚辛日，旬遁丁见干支上或三传；不能由此自动断凶动')
add('real-wealth',28,'鬼局财实鬼空','ghost-wealth','三传合鬼局，其中两位空陷，唯一不空陷位作日财')
for n,typ,definition in [(29,'group-house-drain','三传合局生日干，日支又生该局'),(30,'group-stem-drain','三传合局生日支，日干又生该局')]:
 add('main',n,'局生一方而脱另一方',typ,definition)
add('birth-tomb',33,'长生传墓','birth-tomb','初为日五行长生，末为日五行墓；不混通用阴干逆行法',reverse=False)
add('tomb-birth',33,'墓传长生','birth-tomb','初日五行墓，末日五行长生',reverse=True)
add('ghost-child',34,'初鬼末子孙','ghost-child','初传为日鬼、末传为日子孙；兼列末能制初，不自动断先凶后吉')
add('two-edged',34,'两面刀（戊日伏吟）','two-edged','戊日天地盘伏吟、三传巳申寅；末鬼生初且克干')
for n,rel,label in [(35,'drain','脱'),(36,'bath','败'),(63,'attack','伤'),(78,'peak','旺'),(79,'end','绝'),(80,'death','死'),(88,'tomb','墓')]:
 for cross in [False,True]:
  if n==63 and cross:continue
  add('cross' if cross else 'each',n,('互' if cross else '各')+label,'upper-pair',('干上对日支、支上对日干' if cross else '干上对日干、支上对日支')+'分别为'+label+'；五行十二气专项，土随水，不改U通用天干气',relation=rel,cross=cross)
add('tail-head',38,'旬尾加旬首','tail-head','天盘旬尾临地盘旬首；不强制发用，发用与否另列')
add('head-thief',38,'天盘旬首乘玄武（北海）','head-thief','天盘旬首乘玄武；标明与大全地盘旬首乘玄不同取法')
add('ground-head-thief',38,'地盘旬首上乘玄武（大全）','ground-head-thief','玄武所临地盘为旬首；不混天盘旬首乘玄')
add('closed-lu',38,'日禄作旬尾','closed-lu','日禄为本旬旬尾；按大全此旁格可全盘核，不虚填财或其他类神')
add('closed-wealth',38,'课传财作旬尾','closed-wealth','旬尾作日财并见干支上或三传；此为旬尾旁义，不宣称标准闭口全具')
add('sun-thief',39,'玄武与太阳邻接','sun-thief','玄武乘支、所临地、直接阴神见月将分别标记；真实日照条件仍未核实，列候选')
add('queen-match',40,'后合分居干支','queen-match','干支上分乘实际天后、六合；不推断私情')
add('queen-trans',40,'后合同入三传','queen-trans','实际天后与六合同入三传；次序另列，不推断私情')
for mode in ['xun','five-zi']: add(mode,42,'三奇（'+('旬遁' if mode=='xun' else '五子元遁')+'）','three-wonders','三传遁干集齐甲戊庚或乙丙丁；两种遁法各自计算，不拼接',mode=mode)
add('harm',43,'害干上贵','harm-noble','实际贵人临干，初传与该贵人支六害；不以害另一贵人替代')
add('crowd',44,'遍地贵人基本例','crowd-noble','干支上分两贵且初、中又分两贵；按大全丁酉例取严格基本条件')
add('stack',45,'昼夜贵相加入课传','stack-noble','昼贵支与夜贵支天地相加，且上支见干支上或三传')
add('cover',45,'两贵覆干支','cover-noble','干支上分见同日昼、夜贵支；实际天乙只依本盘昼夜')
add('mismatch',46,'贵人差迭','mismatch-noble','昼贵支临酉至寅夜方、夜贵支临卯至申昼方；这是方位分类，不代替实际日出入')
add('ghost',48,'鬼乘实际天乙','noble-ghost','实际贵人所乘支为日鬼，见干支上或三传')
add('restrained',49,'两贵各受地克','noble-restrained','本日昼夜贵支各被自身所临地盘克；原文不要求入传')
add('empty',50,'二贵皆空陷','noble-void','昼夜贵支分别自空或坐空，两者均须空陷；一贵空不算二贵皆空')
add('snake',53,'两蛇夹墓基本结构','snake-tomb','日五行墓神临地盘巳且乘实际螣蛇；临干另列')
add('tiger',54,'柔日虎视复见虎','tiger-star','柔日昴星，课传再见实际白虎；申寅旁象不混实际白虎')
for cross in [False,True]: add('cross' if cross else 'each',55,'互网' if cross else '各网','net','干支上分别乘对方/自身前一辰，标明空与可冲解位置',cross=cross)
add('life',56,'本命墓覆干候选','life-net','日墓临干，且本人已核本命支为该墓；缺本人身份或本命不判成格')
add('cost',57,'生空与鬼脱对照','cost','干支上有父母空陷；四课或三传再见鬼/脱（原文明看二四课）；是否实另核，不因古例概括抹掉鬼的坐空')
add('broken',58,'用破且中末无依','broken-use','初为财禄父母而空陷或受上下夹克，中末各为鬼脱或空陷；仅基本分支')
add('canopy',59,'华盖兼日墓临干发用','canopy','日支三合华盖为日五行墓，临干且发用；单墓不混华盖')
add('sun-house',60,'太阳临支','sun-house','月将临日支；实际照耀与占类用途另核，不直断光辉')
add('house',62,'干墓或支墓乘虎临支','house-tomb-tiger','日墓或支墓乘实际白虎临日支；克支与月将例外另列')
add('mutual-attack',64,'交互克（芜淫结构）','mutual-attack','干上克支、支上克干；不推断婚外私情')
add('separation',64,'交互下克上（解离结构）','separation','干克支上、支克干上；事项与阶段另核')
add('gate',65,'干墓兼季关发用','season-gate','初传为日五行墓并当季关神：春丑夏辰秋未冬戌；列发自哪课')
add('wealth-tomb',66,'支墓作日财发用','house-wealth-tomb','日支五行墓为日财且发用；不能由此概断行程')
add('carrier',67,'白虎乘神所克五行','tiger-carrier','白虎见干支上或三传，计算所乘支克何五行；疾病类仍须人事与其他依据，不自动病证')
add('rescue',68,'制鬼位置','rescue','干支上或三传有日鬼与制鬼子孙；空实坐地和位置随条目交接，不保证奏效')
add('illness',71,'岁病符克宅','illness','旧太岁支临日支且克日支；必须有岁支')
add('mourning',72,'丧吊全逢','mourning','岁前二丧门、岁后二吊客，同见干支上或三传；不能由标题宣告亲人死亡')
add('return-clamp',73,'初传克处回归又受克','return-clamp','初传受所临下位克（临干以日干论），回其地盘本宫又被上神克')
add('all-void',74,'三传全空陷','all-void','三传每位各自旬空或坐空；保留具体是空还是陷')
add('sky-void',74,'两空一天空','sky-void','三传两位空陷，其余一位乘天空；天空仍不改记为旬空')
add('lessons-void',74,'四课全空陷','lessons-void','四课上神各自旬空或坐空')
add('two-punish',75,'二字刑（子卯在两上）','two-punish','干支上分见子卯；不混三传三刑')
add('three-punish',75,'三字刑','three-punish','三传集齐寅巳申或丑戌未；记录实际传序')
add('self-punish',75,'四课全逢自刑支','self-punish','四课上神皆在辰午酉亥范围；这是大全一字刑分支，不必四字各异')
for typ,name in [('each','各上下害'),('upper','两上害'),('base-upper','本位与两上皆害'),('trans','三传相邻六害'),('cross','交互六害')]:
 add('harm-'+typ,76,name,'harm','按对应位置逐对六害，不把任意全盘两害支凑成格',mode=typ)
add('tomb-chain',81,'初传入中墓且末入墓乡','tomb-chain','中传为初五行墓，末传所临地盘正为中传墓；按初传类神分憎爱')
add('stop',82,'初实中末空陷','stop','初传自支与坐地皆不空，中末各空陷；初传以何义使用仍按事类')
add('break-union',84,'合中犯煞','break-union','三合局中神与干上或支上发生刑冲害，列明具体关系')
for cross in [False,True]: add('cross-seat' if cross else 'each-seat',87,'互坐墓' if cross else '各坐墓','seat-tomb','天盘干寄宫支、天盘日支分别坐对方/自身五行墓；干之墓用日干五行，不用寄宫五行替换',cross=cross)
add('moving',89,'伏吟逢旬丁日马','moving','天地盘伏吟，干支上或三传见旬丁或日驿马；月天马另按正式S04核查')
add('empty-return',90,'返吟三传空陷','empty-return','天地盘对冲，三传每位旬空或坐空；并非凡返吟皆不动')
add('dragon',92,'龙乘生日之神','dragon','青龙所乘支生日干且见干支上或三传；是否兼月生气单独标记，不混大全正格',strict=False)
add('dragon-month',92,'龙乘父母兼月生气（大全正格）','dragon','上述龙乘生干之神再兼月内生气；不直接断吉迟迟',strict=True)
add('origin',93,'可信程序盘起例核查','method','核三传来源和采用起法；不按趋避需要改三传，保留北海对古例另起法的批评')
add('void-action',94,'空陷与作用核查','method','分别看见生/克/财/救/盗的真实作用条件；空亡、受克、恋生及直接临身分层，沿用U08')
add('kin-group',95,'三传六亲合局','kin-group','三传三合成局，列局相对于日干之六亲、两上受克与承接通关；不直接宣告某亲属遭灾')
add('void-kins',96,'本旬两空逐类映射','method','本旬两空分别映射六亲、将、禄及所在位置；不将“空”固定翻译成没有')
add('absent-kind',97,'所筮不入按类补查','method','主类神取准后检查干支上、三传、已核年命；不现时按占类补天地盘，不一律否决')
add('scope',98,'非占现类问项约束','method','仅解释与原问和主线相关之象；不凭无关格名扩写疾病、外遇、死亡等事实')
add('context',99,'因人因事因时取义','method','结合真实职业角色、目标、进退阶段取义；不把古代身份贵贱判辞直接套今人')
add('stage',100,'已灾与未灾阶段核查','method','灾已发不能保证后续无灾；北海明确反驳大全概括，暂不采用灾已发即免灾自动规则')
add('finish',100,'干上绝神作鬼或财','finish','干上为日五行绝神且作鬼或财；是否适合了结须核实际问事')
add('earth-conflict',100,'初末土鬼互冲','earth-conflict','壬癸日初末皆土鬼且辰戌或丑未相冲；只是以凶制凶基本关系，官职目标可反不利')
reg['rules']+=rows
reg['nobleman_tables']=json.loads((R/'runtime/liuren/20261111-basic-bifa-42/references/shensha-policy.json').read_text('utf-8'))['nobleman_tables']
reg.update(schema='liuren-basic-bifa-rules-v2',release='20261111-reviewed-bifa-43',scope='百法逐法核查；已核基本分支及方法项，非所有偏僻正变类格穷尽')
reg['deferred']=['原引擎未经核实的其他旁格标签','四时返本煞两书季表差异，暂停自动采用','第79法土绝亥为古文寄寅支法，本版五行土随水取巳，不混算法','大全第100法已灾即免灾概括与北海反驳，暂停概括判辞，采用明确结构与阶段核查','未核天文日出日落，太阳照武只交邻接候选','年命必须有本人可绑定资料；不能使用任一参与者本命代替本人']
reg['policy']='按实际昼夜独立重算；matches仅条件全真，conditional_candidates保留未知项，method_checks为推理义务，不是几何成格或成败判辞；所有条目按位置去重。'
by={n:[r for r in reg['rules'] if r['law_number']==n] for n in range(1,101)}
assert all(by.values()),[n for n,x in by.items() if not x]
reg['law_review']=[dict(law_number=n,previously_42=any(not r.get('extended') for r in by[n]),title=next((s.removeprefix('## ') for s in bl[starts[n]-1:] if s.startswith('## ')),''),rule_ids=[r['id'] for r in by[n]],basic_reviewed=True,all_variants_complete=False) for n in by]
(R/'tools/liuren-bifa-basic-rules.json').write_text(enc(reg),encoding='utf-8')
(O/'百法逐法台账.json').write_text(enc(reg['law_review']),encoding='utf-8')
(O/'百法逐法台账.md').write_text('# 毕法百法基本定义核查\n\n全书逐法登记；“已核”指下列基本分支，不等于本章所有偏僻类格已实现。程序测例也不等于预测验证。\n\n|法|42版已有|本轮基本格/方法|\n|---|---|---|\n'+''.join(f"|{n:02}|{'是' if any(not r.get('extended') for r in rs) else '否'}|"+'；'.join(r['name']+'：'+r['definition'] for r in rs)+'|\n' for n,rs in by.items())+'\n待用范围：\n\n'+'\n'.join('- '+s for s in reg['deferred'])+'\n',encoding='utf-8')
print('rules',len(reg['rules']),'laws',len(by),'new',len(rows),'methods',sum(r.get('operation')=='method' for r in rows))
