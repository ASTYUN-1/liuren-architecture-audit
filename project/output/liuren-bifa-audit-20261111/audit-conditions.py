"""Independent, bounded semantic audit. Writes evidence only; no runtime changes.

Pass means the stated structural condition matches, never that a prediction holds.
Unimplemented subclasses stay pending, rather than inheriting their parent's test.
"""
import collections, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BOOK = '书籍库/北海闲人/毕法赋全解-正式整理本.md'
Z = '子丑寅卯辰巳午未申酉戌亥'
G = '甲乙丙丁戊己庚辛壬癸'
PY = 'zi chou yin mao chen si wu wei shen you xu hai'.split()
H = dict(zip(G, '寅辰巳未巳未申戌亥丑'))
LU = dict(zip(G, '寅卯巳午巳午申酉亥子'))
E = dict(zip(G, '木木火火土土金金水水')) | dict(zip(Z, '水土木木土火火土金金土水'))
GENERALS = dict(zip(['贵人','腾蛇','螣蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后'], '土火火火木土木土金土水金水'))
E.update(GENERALS)
BIRTH = dict(zip('木火土金水', '亥寅申巳申'))
TOMB = dict(zip('木火土金水', '未戌辰丑辰'))
WANG = dict(zip('木火土金水', '卯午子酉子'))
S = dict(zip('木火土金水','火土金水木'))
K = dict(zip('木火土金水','土金水木火'))
PAIRS = [set(x) for x in ['子丑','寅亥','卯戌','辰酉','巳申','午未']]
HARM = [set(x) for x in ['子未','丑午','寅巳','卯辰','申亥','酉戌']]
GENERAL_ORDER=['贵人','腾蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后']
def sheng(a,b): return S[E[a]] == E[b]
def ke(a,b): return K[E[a]] == E[b]
def he(a,b): return any({a,b} == p for p in PAIRS)
def hai(a,b): return any({a,b} == p for p in HARM)
def adj(a,b): return (Z.index(a)-Z.index(b)) % 12 in (1,11)
def birth(x): return BIRTH[E[x]]
def tomb(x): return TOMB[E[x]]
def wang(x): return WANG[E[x]]
def neighbor(x,offset): return Z[(Z.index(x)+offset)%12]
def chain(t,relation): return (relation(t[0],t[1]) and relation(t[1],t[2])) or (relation(t[2],t[1]) and relation(t[1],t[0]))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data): (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

D = json.loads((OUT/'engine-720-geometries.json').read_text(encoding='utf-8'))
V = json.loads((OUT/'engine-day-night-1440.json').read_text(encoding='utf-8'))
variants = {(v['day'],v['day_upper'],v['mode']):v for v in V}
source = (ROOT/BOOK).read_text(encoding='utf-8').splitlines()
titles = {}
for line in source:
    m = re.match(r'- \[第\S+法 (.+)\]\(#law-(\d{3})\)',line)
    if m: titles[int(m[2])] = m[1]
assert len(titles)==100
headings = {int(m[1]):i+1 for i,l in enumerate(source) if (m:=re.search(r'id="law-(\d{3})"',l))}

def check(x,line):
    dg,dz = x['day']; home=H[dg]
    u=[r[1] for r in x['sike']]; t=[r[3] for r in x['sanchuan']]
    tp=dict(zip(Z,[x['tianpan'][k] for k in PY])); inv={v:k for k,v in tp.items()}
    void=set(x['xunkong']); effective_void=void|{tp[z] for z in void}
    cycle=next(i for i in range(60) if G[i%10]+Z[i%12]==x['day'])
    head=Z[(cycle-cycle%10)%12]; tail=neighbor(head,9); ding=neighbor(head,3)
    hidden_stems={neighbor(head,j):G[j] for j in range(10)}
    used=set(u+t)
    def r(conditions,lines,scope='所列结构条件',partial=False):
        good=all(conditions.values())
        status='结构符合' if good else ('部分条件符合' if partial and any(conditions.values()) else '条件不符')
        return {'status':status,'checked_scope':scope,'conditions':conditions,'source_lines':lines}
    def modecheck(predicate,lines,scope):
        explicit='昼贵' if '昼' in line else ('夜贵' if '夜' in line else None)
        modes=[explicit] if explicit else ['昼贵','夜贵']
        answers={mode:predicate(variants[(x['day'],x['day_upper'],mode)]) for mode in modes}
        good=any(answers.values())
        return {'status':('结构符合' if explicit or all(answers.values()) else '需昼夜条件') if good else '条件不符',
                'checked_scope':scope,'conditions':answers,'source_lines':lines,'requires_mode':explicit or '按实际昼夜筛选'}
    def genmap(v): return {tp[z]:v['shenpan'][PY[i]] for i,z in enumerate(Z)}
    def on_general(v,g): return next(z for z,k in genmap(v).items() if k==g)
    nobles=[on_general(variants[(x['day'],x['day_upper'],mode)],'贵人') for mode in ['昼贵','夜贵']]

    if not re.match(r'^\d+\.',line): return {'status':'导出污染','checked_scope':'非毕法条目','conditions':{},'source_lines':[]}
    # Check exact subtypes; sibling variants never inherit these tests.
    if line=='01.前后引从升迁吉.Ⅰ.引干例': return r({'初末夹干上神':set([t[0],t[2]])=={neighbor(u[0],1),neighbor(u[0],-1)}},[188,196])
    if line=='01.前后引从升迁吉.B.初末引从地支格': return r({'初末夹支上神':set([t[0],t[2]])=={neighbor(u[2],1),neighbor(u[2],-1)}},[188,200])
    if line.startswith('02.') and ('Ⅰ.' in line or 'Ⅱ.' in line):
        a,b=(tail,head) if 'Ⅰ.' in line else (head,tail)
        return r({'干上旬首尾对应':u[0]==a,'支上旬首尾对应':u[2]==b},[366,368],partial=True)
    if line.startswith('05.'): return r({'四课三传全阳':all(Z.index(z)%2==0 for z in u+t)},[678,680])
    if line.startswith('06.'): return r({'四课三传全阴':all(Z.index(z)%2==1 for z in u+t)},[678,680])
    if line=='07.旺禄临身徒妄作.Ⅰ': return r({'阴干旺禄临干':dg in '乙丁己辛癸' and u[0]==LU[dg]},[788,792,796],scope='旺禄临干；未把“徒妄作”当作结果')
    if line.startswith('08.'):
        c={'日禄临支':u[2]==LU[dg]}
        if '①墓' in line:c['支为禄墓']=dz==tomb(u[2])
        if '②克' in line:c['支克禄']=ke(dz,u[2])
        if '③脱' in line:c['支脱禄']=sheng(u[2],dz)
        return r(c,[856,890,892],partial=True)
    if line.startswith('10.'):
        if '卯加申' in line or '卯加戌' in line:
            ground='申' if '卯加申' in line else '戌'
            return r({'卯临所列地盘':tp[ground]=='卯','卯空亡': '卯' in void},[996,998,1016],scope='斫轮所列落点及朽木所需卯空；几何成立不等于朽木成立',partial=True)
        return {'status':'待核','checked_scope':'伤斧还须春季、甲乙日、寅卯时，查表未绑定这些条件','conditions':{},'source_lines':[1012,1014]}
    if line.startswith('12.'):
        tests=[('干受上神生',lambda:sheng(u[0],dg)),('干受上神克',lambda:ke(u[0],dg)),('干受上神脱',lambda:sheng(dg,u[0])),
               ('干寄宫受上神克',lambda:ke(u[0],home)),('干寄宫受上神生',lambda:sheng(u[0],home)),('干寄宫克上神',lambda:ke(home,u[0])),('干寄宫生上神',lambda:sheng(home,u[0]))]
        return r({word:fn() for word,fn in tests if word in line},[1171,1175,1177],scope='标签逐字列出的干、寄宫、上神关系',partial=True)
    if line in ['15.脱上逢脱防虚诈.Ⅰ.昼贵','15.脱上逢脱防虚诈.Ⅱ.夜贵']:
        return modecheck(lambda v:sheng(dg,u[0]) and sheng(u[0],v['sike'][0][0]),[1315],'日干生干上神，干上神又生其所乘天将')
    if line=='16.空上乘空事莫追':
        return modecheck(lambda v:any(g=='天空' and z in void for z,g in genmap(v).items()),[1355],'天空乘旬空；未推导具体占类成败')
    if line.startswith('17.') or line.startswith('18.'):
        step=1 if line.startswith('17.') else -1
        return r({'进退连茹方向':t[1]==neighbor(t[0],step) and t[2]==neighbor(t[1],step),'传中见旬空或落空':bool(set(t)&effective_void)},[1385,1397,1419,1421],scope='进退连茹及逢空；宜进宜退另须按事取用',partial=True)
    if line.startswith('21.'):
        c={'干上合支':he(u[0],dz),'支上合干寄宫':he(u[2],home)}
        if '.A.' in line:c|={'干上支长生':u[0]==birth(dz),'支上干长生':u[2]==birth(dg)}
        elif '①交财' in line:c|={'干上为支财':ke(dz,u[0]),'支上为干财':ke(dg,u[2])}
        elif '②自财' in line:c|={'干上为干财':ke(dg,u[0]),'支上为支财':ke(dz,u[2])}
        elif '①交克' in line:c|={'干上克支':ke(u[0],dz),'支上克干':ke(u[2],dg)}
        elif '②自克' in line:c|={'干上克干':ke(u[0],dg),'支上克支':ke(u[2],dz)}
        elif '①交脱' in line:c|={'干上脱支':sheng(dz,u[0]),'支上脱干':sheng(dg,u[2])}
        elif '②自脱' in line:c|={'干上脱干':sheng(dg,u[0]),'支上脱支':sheng(dz,u[2])}
        return r(c,[1684,1686,1702,1708,1712],partial=True)
    if line.startswith('22.'):
        if '.A.' in line:c={'干加支且合或支加干且合':(u[2]==home and he(home,dz)) or (u[0]==dz and he(dz,home))}
        elif '.B.' in line:
            # The original 大全 defines this as two vertical 六合 pairs. 北海's
            # identically named subsection uses two horizontal pairs instead.
            # A valid original-source definition must not be marked false merely
            # because a later commentator reused the name differently.
            answer=r({'日干寄宫合干上':he(home,u[0]),'日支合支上':he(dz,u[2])},[1764],partial=True)
            answer['additional_source']={'path':'书籍库/经典古籍/明代/六壬大全-明-郭载騋.txt','anchor':'上下俱合格  如日干与上神作六合，地支亦与上神作六合者'}
            answer['definition_note']='符合《大全》的纵向两合定义；北海同名段落用横向两合，须区分口径，不能据北海同名定义判引擎错配。'
            return answer
        elif line=='22.上下皆合两心齐':c={'上神六合':he(u[0],u[2]),'下神六合':he(home,dz)}
        elif '.C.' in line:c={'干支上神六合':he(u[0],u[2])}
        elif '.D.' in line:c={'交互六合':he(u[0],dz) and he(u[2],home)}
        elif '.E.' in line:c={'上神六合':he(u[0],u[2]),'下神六害':hai(home,dz)}
        else:return None
        return r(c,[1764,1768,1774,1776,1778],partial=True)
    if line.startswith(('23.','24.')):
        start,end=(u[2],u[0]) if line.startswith('23.') else (u[0],u[2])
        if t[0]==start and t[2]==end:return r({'初末互传':True},[1797,1801,1822])
        direct=any(t[i]==start and t[j]==end for i in range(3) for j in range(i+1,3))
        s,e=(u[2:4],u[0:2]) if line.startswith('23.') else (u[0:2],u[2:4])
        broad=any(t[i] in s and t[j] in e for i in range(3) for j in range(i+1,3))
        if direct or broad:return {'status':'扩展符合','checked_scope':'中末/初中或干支二课扩展互传，不冒称初末正格','conditions':{'两上互传':direct,'二课互传':broad},'source_lines':[1820,1824]}
        return r({'初末互传':False,'二课或相邻传互传':False},[1797,1801,1820,1824])
    if line=='25.金日逢丁凶祸动':return r({'金日':dg in '庚辛','旬丁入课传':ding in used},[1836],partial=True)
    if line=='26.水日逢丁财动之':return r({'水日':dg in '壬癸','旬丁入课传':ding in used},[1929,1943,1945,1947,1949,1951,1953],scope='水日逢旬丁；不误加“丁所乘地支也必须为财”的条件；年命未提供',partial=True)
    if line=='31.三传递生人举荐':return r({'顺向或逆向两段递生':chain(t,sheng)},[2125,2133],scope='三传递生几何结构；空亡与作用对象另论')
    if line=='31.三传递生人举荐.B.支干相生格':return r({'干上生干':sheng(u[0],dg),'支上生干上':sheng(u[2],u[0])},[2144],partial=True)
    if line=='32.三传互克众人欺':return r({'顺向或逆向两段递克':chain(t,ke)},[2156],scope='三传递克正格，不能用其他类格替代')
    if line=='32.三传互克众人欺.A.求财大获格':return r({'初克中且中克末':ke(t[0],t[1]) and ke(t[1],t[2]),'日干或干上克初':ke(dg,t[0]) or ke(u[0],t[0])},[2173,2175],partial=True)
    if line=='32.三传互克众人欺.D.三传内战格':return r({'初克中且中克末':ke(t[0],t[1]) and ke(t[1],t[2]),'地盘克初':ke(inv[t[0]],t[0])},[2183],partial=True)
    if line.startswith('33.'):
        is_first='Ⅰ.' in line
        return r({'初传生墓对应':t[0]==(birth(dg) if is_first else tomb(dg)),'末传生墓对应':t[2]==(tomb(dg) if is_first else birth(dg))},[2211],partial=True)
    if line=='35.人宅受脱俱招盗.Ⅰ.干支上脱':return r({'干上脱干':sheng(dg,u[0]),'支上脱支':sheng(dz,u[2])},[2295],partial=True)
    if line=='35.人宅受脱俱招盗.Ⅰ.干支互脱':return r({'干上脱支':sheng(dz,u[0]),'支上脱干':sheng(dg,u[2])},[2295],partial=True)
    if line.startswith('37.') and any('论.'+a in line for a in ['Ⅰ.','Ⅱ.','Ⅲ.']):
        rel=sheng(t[0],dg) if '.Ⅰ.' in line else (ke(t[0],dg) if '.Ⅱ.' in line else ke(dg,t[0]))
        return r({'末生初':sheng(t[2],t[0]),'初传所列对干关系':rel},[2404,2406,2408,2410,2412],partial=True)
    if line.startswith('38.'):
        if '.Ⅴ.' in line:return r({'旬尾加旬首':tp[head]==tail},[2468])
        if '.Ⅳ.' in line:return r({'旬尾加旬首':tp[head]==tail,'旬尾发用':t[0]==tail},[2468,2474],partial=True)
        if '.Ⅵ.' in line:return r({'日禄作旬尾':LU[dg]==tail},[2472,2481])
        if '.Ⅲ.' in line:return modecheck(lambda v:tp[head]==tail and genmap(v)[tail]=='玄武',[2468,2474],'旬尾加旬首乘玄武')
        if '.Ⅰ.' in line:return modecheck(lambda v:v['shenpan'][PY[Z.index(head)]]=='玄武',[2467,2487],'标签所列玄武临地盘旬首；仅核落点')
        if '.Ⅱ.' in line:return modecheck(lambda v:genmap(v)[head]=='玄武',[2470],'旬首乘玄武')
    if line.startswith('40.'):
        expected=('六合','天后') if '干上合' in line else ('天后','六合')
        return modecheck(lambda v:(v['sike'][0][0],v['sike'][2][0])==expected,[headings[40]+2],'所列昼夜后合分别临干支')
    if line.startswith('44.'):
        subjects=u if '.Ⅰ.' in line else t
        # 贵将 itself, 正贵, and 幕贵 all matter in original examples. This test
        # checks only the explicitly listed 日/夜贵 branches; a failure stays
        # pending rather than rejecting all extended 贵人 usage.
        c={'所列课或传皆为昼夜贵支':set(subjects)<=set(nobles)}
        if not all(c.values()):return {'status':'待核','checked_scope':'未全落昼夜贵支，须再核贵将、幕贵等原例口径','conditions':c,'source_lines':[2667,2669]}
        return r(c,[2667,2669],scope='所列课或传贵人支分布，不用遍贵直断无依')
    if line=='45.昼夜贵加求两贵':
        return r({'昼夜贵上下相加':any(tp[a]==b for a,b in [nobles,nobles[::-1]]),'上层贵人入课传':any(tp[a]==b and b in used for a,b in [nobles,nobles[::-1]])},[2691],scope='两贵上下相加并入课传；若只满足相加，年命未给，不能确认本问六处全式',partial=True)
    if line=='45.昼夜贵加求两贵.A.贵覆干支格':
        answer=r({'干支上皆贵人支':all(z in nobles for z in [u[0],u[2]])},[2695],scope='按《大全》干支皆贵定义核，保留八专两上同贵')
        answer['additional_source']={'path':'书籍库/经典古籍/明代/六壬大全-明-郭载騋.txt','anchor':'贵覆干支格  缘干支上皆乘昼夜贵人例'}
        return answer
    if line.startswith('46.') or line.startswith('4.'):
        def noble_position(v):
            j=GENERAL_ORDER.index(v['sike'][0][0])
            return j in range(6,12) if '在干前' in line else j in range(1,6)
        answer=modecheck(noble_position,[2725,2727],'按干上天将所居贵前五、贵后六核贵在干前后；不等于已成立差迭正格')
        if answer['status']=='条件不符':
            answer['status']='口径待核'
            answer['definition_note']='标签疑用贵支与日干寄宫的固定支位，和北海按干上天将判贵前后的口径不同；未据此直接计入已确认引擎错配。'
        return answer
    if line.startswith('48.'):
        def noble_ghost(v):
            z=on_general(v,'贵人')
            return ke(z,dg) and (z in used if '在六处' in line else True)
        answer=modecheck(noble_ghost,[2784],'所列昼夜贵人乘日鬼；“在六处”标签另核入课传，未给年命不补造')
        if answer['status']=='条件不符' and '在六处' in line:
            answer['status']='待核';answer['definition_note']='课传未见该贵，年命资料缺失，不能排除年命候选，也不能确认六处成立。'
        return answer
    if line=='49.两贵受克难干贵':return r({'昼贵坐受克':ke(inv[nobles[0]],nobles[0]),'夜贵坐受克':ke(inv[nobles[1]],nobles[1])},[2803],partial=True)
    if line.startswith('49.') and '.A.' in line:
        return modecheck(lambda v:on_general(v,'白虎')=='丑' or v['shenpan']['chou']=='白虎',[2809],'白虎乘天盘丑或临地盘丑')
    if line=='50.二贵皆空虚喜期':return r({'昼贵旬空或落空':nobles[0] in effective_void,'夜贵旬空或落空':nobles[1] in effective_void},[2825],partial=True)
    if line=='51.魁度天门关隔定':return r({'天盘戌加地盘亥':tp['亥']=='戌'},[2835])
    if line=='52.罡塞鬼户任谋为':return r({'天盘辰加地盘寅':tp['寅']=='辰'},[2847,2873])
    if line.startswith('53.'):
        return modecheck(lambda v:tp['巳']==tomb(dg) and genmap(v)[tomb(dg)]=='腾蛇',[2881],'日墓临巳并乘螣蛇；不据此断具体占类凶吉')
    if line.startswith('55.'):
        a,b=(neighbor(dz,1),neighbor(home,1)) if '互罗网' in line else (neighbor(home,1),neighbor(dz,1))
        return r({'干上网对应':u[0]==a,'支上网对应':u[2]==b},[2939,2941,3884],partial=True)
    if line.startswith('61.'):
        if '.A.' in line:return modecheck(lambda v:v['sike'][0][0]=='白虎' and ke(u[0],dg),[3147,3151],'虎鬼加干类格')
        if '不临干' in line:return modecheck(lambda v:genmap(v)[tomb(dg)]=='白虎' and u[0]!=tomb(dg),[3151],'日墓乘虎、明确不临干；年命作用未核')
        return modecheck(lambda v:u[0]==tomb(dg) and v['sike'][0][0]=='白虎',[3149,3151],'墓虎临干')
    if line.startswith('62.'):
        if line.endswith('.干墓临支'):return r({'干墓临支':u[2]==tomb(dg)},[3186,3190],scope='仅干墓临支；标签未含昼夜虎，不补成墓虎全式')
        if line.endswith('.支墓临支'):return r({'支墓临支':u[2]==tomb(dz)},[3186,3190],scope='仅支墓临支；不补成墓虎全式')
        if '.A.' in line:return modecheck(lambda v:v['sike'][2][0]=='白虎' and ke(u[2],dz),[3188],'虎鬼克支类格')
    if line=='63.彼此全伤防两损':return r({'干上克干':ke(u[0],dg),'支上克支':ke(u[2],dz)},[3254,3256],partial=True)
    if line=='64.夫妇芜淫各有私':return r({'干上克支':ke(u[0],dz),'支上克干':ke(u[2],dg)},[3280,3282],partial=True)
    if line=='64.夫妇芜淫各有私.A.真解离卦':return r({'干克支上':ke(dg,u[2]),'支克干上':ke(dz,u[0])},[1706],partial=True)
    if line=='70.鬼临三四讼灾随':return r({'第三课上神为日鬼':ke(u[2],dg),'第四课上神为日鬼':ke(u[3],dg)},[3467],partial=True)
    if line in ['69.虎乘遁鬼殃非浅.昼虎','69.虎乘遁鬼殃非浅.夜虎']:
        return modecheck(lambda v:(z:=on_general(v,'白虎')) in hidden_stems and ke(hidden_stems[z],dg),[3441,3443],'白虎所乘支的旬遁天干克日干；旬遁独立按六十甲子生成')
    if line in ['69.虎乘遁鬼殃非浅.A.明暗二鬼格.干暗支明','69.虎乘遁鬼殃非浅.A.明暗二鬼格.干明支暗']:
        a,b=(u[0],u[2]) if '干暗' in line else (u[2],u[0])
        return r({'暗鬼所在旬遁干克日':a in hidden_stems and ke(hidden_stems[a],dg),'明鬼所在支克日':ke(b,dg)},[3445,3447],partial=True)
    if line=='74.空空如也事休追.A.四课全空格':return r({'四课上神皆旬空或落空':set(u)<=effective_void},[3603,3607],scope='标签明示四课全空，按旬空/落空核结构；不代替三传全空')
    if line in ['74.空空如也事休追.昼空','74.空空如也事休追.夜空']:
        answer=modecheck(lambda v:all(z in effective_void or genmap(v)[z]=='天空' for z in t),[3603,3613,3615],'三传逐位为旬空/落空/天空；严格区别空上乘空')
        if answer['status']=='条件不符':
            answer['status']='待核';answer['definition_note']='标签未明示三传全空，本盘仅中末空而初传实；须核是否误归74法或另指空空类格。'
        return answer
    if line.startswith('77.'):
        if '.A.' in line:c={'干上生支':sheng(u[0],dz),'支上生干':sheng(u[2],dg)}
        elif '.B.' in line:c={'干上生干':sheng(u[0],dg),'支上生支':sheng(u[2],dz)}
        elif '.C.' in line:c={'支加干':u[0]==dz,'支生干':sheng(dz,dg)}
        else:return None
        return r(c,[3814,3822,3842],partial=True)
    if line.startswith('78.'):
        if E[dg]=='土' or E[dz]=='土':return {'status':'待核','checked_scope':'土旺口径须单独核原文；不默认为一致','conditions':{},'source_lines':[3886]}
        c={'干上对应旺':u[0]==wang(dz if '.A.' in line else dg),'支上对应旺':u[2]==wang(dg if '.A.' in line else dz)}
        return r(c,[3878,3880,3882],partial=True)
    if line=='82.不行传者考初时':return r({'初实':t[0] not in effective_void,'中空':t[1] in effective_void,'末空':t[2] in effective_void},[4074,4076],scope='初实中末空，含旬空和地盘落空',partial=True)
    if line.startswith('85.') and '.B.' not in line:
        subjects=t if '.A.' in line else t[:1]
        return modecheck(lambda v:all(ke(inv[z],z) and ke(genmap(v)[z],z) for z in subjects),[4269,4290],'初传夹克或三传夹克，严格区分类格')
    if line=='86.将逢内战所谋危.A.三传日辰内战格':return r({'日克日上':ke(dg,u[0]),'支克支上':ke(dz,u[2]),'三传皆受地盘克':all(ke(inv[z],z) for z in t)},[4354,4356],partial=True)
    if line in ['86.将逢内战所谋危.昼','86.将逢内战所谋危.夜']:
        return modecheck(lambda v:any(ke(inv[z],z) and ke(z,genmap(v)[z]) for z in used),[4334],'课传所见地盘克神、神克将的内战链')
    if line.startswith('87.'):
        a,b=(tomb(dz),tomb(dg)) if '.A.' in line else (tomb(dg),tomb(dz))
        return r({'日干寄宫所坐墓':inv[home]==a,'日支所坐墓':inv[dz]==b},[4362],partial=True)
    if line in ['88.干支乘墓各昏迷.自墓','88.干支乘墓各昏迷.A.互乘墓神格']:
        a,b=(tomb(dz),tomb(dg)) if '.A.' in line else (tomb(dg),tomb(dz))
        return r({'干上墓对应':u[0]==a,'支上墓对应':u[2]==b},[4390],partial=True)
    if line.startswith('89.'):
        horse={'申':'寅','子':'寅','辰':'寅','寅':'申','午':'申','戌':'申','亥':'巳','卯':'巳','未':'巳','巳':'亥','酉':'亥','丑':'亥'}[dz]
        target=ding if '乘丁' in line else horse
        if target not in used:
            return {'status':'待核','checked_scope':'课传未见所列丁马；年命未提供，不能排除年命候选，也不能当当前成立',
                    'conditions':{'课传见所列丁或日驿马':False,'丁马所乘支':target},'source_lines':[4416,4424,4426]}
        return r({'课传见所列丁或日驿马':True},[4416,4420,4424,4426],scope='丁马入课传的动象；原文允许非伏吟，不误加伏吟前提')
    if line.startswith('90.'):
        return r({'返吟':x['shift']==6,'三传皆旬空或落空':set(t)<=effective_void},[4452],partial=True)
    if line in ['91.虎乘干鬼凶速速.昼','91.虎乘干鬼凶速速.夜']:
        return modecheck(lambda v:ke(on_general(v,'白虎'),dg),[4528,4530],'白虎所乘支为日鬼；作用位置、占类与凶速均另论')
    if line.startswith('92.'):
        return modecheck(lambda v:sheng(on_general(v,'青龙'),dg),[4570,4574],'青龙乘生日父母爻；不误以月生气煞代替父母爻')
    return None

rows=[]
for x in D:
    for line in x['bifa'].splitlines():
        if not line.strip():continue
        m=re.match(r'^(\d+)\.([^.]*)',line)
        number=int(m[1]) if m else None
        result=check(x,line) or {'status':'待核','checked_scope':'本轮未完成该细分条目的独立条件定义','conditions':{},'source_lines':[]}
        flags=[]
        if number==4:flags.append('题名属46法，却标4法')
        if number==84:flags.append('题名疑指82法，编号及语序均错；不自动当82法通过')
        row={'day':x['day'],'day_upper':x['day_upper'],'label':line,'raw_number':number,
             'canonical_number':46 if number==4 else (82 if number==84 else number),
             **result,'text_flags':flags,'prediction_or_effect_validated':False}
        rows.append(row)
save('condition-audit-entries.json',rows)
counts=collections.Counter(r['status'] for r in rows)
families=[]
for n in range(1,101):
    relevant=[r for r in rows if r['canonical_number']==n]
    families.append({'number':n,'standard_title':titles[n],'entry_count':len(relevant),'chart_count':len({(r['day'],r['day_upper']) for r in relevant}),
                     'unique_labels':len({r['label'] for r in relevant}),'status_counts':dict(collections.Counter(r['status'] for r in relevant)),
                     'audit_state':'本轮未导出' if not relevant else ('全部所列条目完成结构核对' if all(r['status'] not in ['待核','口径待核','部分条件符合','需昼夜条件'] for r in relevant) else '有待核或需条件条目')})
save('coverage-100.json',families)
flagged=[r for r in rows if r['status'] in ['条件不符','部分条件符合','口径待核','导出污染'] or r['text_flags']]
save('flagged-entries.json',flagged)
per_label=[]
for label in sorted({r['label'] for r in rows}):
    rr=[r for r in rows if r['label']==label]
    per_label.append({'label':label,'count':len(rr),'statuses':dict(collections.Counter(r['status'] for r in rr)),
                      'examples':[{k:r[k] for k in ['day','day_upper','status','conditions']} for r in rr if r['status'] not in ['结构符合','待核']][:5]})
save('audit-by-label.json',per_label)

# Explicitly bounded completeness probes: presence of geometry is not proof that
# the engine intended to report every occurrence outside the relevant positions.
probes=[]
for n,title,predicate in [
 (5,'六阳数足须公用',lambda x:all(Z.index(z)%2==0 for z in [r[1] for r in x['sike']]+[r[3] for r in x['sanchuan']])),
 (6,'六阴相继尽昏迷',lambda x:all(Z.index(z)%2==1 for z in [r[1] for r in x['sike']]+[r[3] for r in x['sanchuan']])),
 (31,'三传递生人举荐',lambda x:chain([r[3] for r in x['sanchuan']],sheng)),
 (32,'三传互克众人欺',lambda x:chain([r[3] for r in x['sanchuan']],ke)),
 (51,'魁度天门关隔定',lambda x:x['tianpan']['hai']=='戌'),
 (52,'罡塞鬼户任谋为',lambda x:x['tianpan']['yin']=='辰')]:
    match=[x for x in D if predicate(x)]
    absent=[{'day':x['day'],'day_upper':x['day_upper'],'sanchuan':[r[3] for r in x['sanchuan']]} for x in match if not any(re.match(r'0?'+str(n)+r'\.',l) for l in x['bifa'].splitlines())]
    probes.append({'law':n,'title':title,'geometry_matches':len(match),'no_family_label_count':len(absent),'no_family_label':absent,'not_automatically_an_engine_bug':True})
save('bounded-completeness-probes.json',probes)
summary={'schema':'bifa-structural-audit-v1','charts':len(D),'day_night_variants':len(V),'entries':len(rows),'unique_labels':len(per_label),
         'status_counts':dict(counts),'families_exported_by_corrected_number':sum(bool(f['entry_count']) for f in families),
         'text_flags':dict(collections.Counter(flag for r in rows for flag in r['text_flags'])),
         'source_scope':'用户网页转录整理本，非原刻影印逐页验校；本轮为所列条件结构核对，未验证吉凶及预测效果',
         'same_lookup_for_both_day_night':all(variants[(x['day'],x['day_upper'],'昼贵')]['bifa']==variants[(x['day'],x['day_upper'],'夜贵')]['bifa']==x['bifa'] for x in D)}
save('audit-summary.json',summary)
paths=[BOOK,'书籍库/经典古籍/明代/六壬大全-明-郭载騋.txt','.opencode/liuren-active.json','排盘工具魔改/index.html','排盘工具魔改/index.js','排盘工具魔改/js/data.js','排盘工具魔改/js/paipan.js','排盘工具魔改/js/hexin.js','排盘工具魔改/js/guize.js','tools/liuren-direct/chart.mjs','tools/liuren-chart-view.mjs','tools/liuren-direct/legacy-engine-manifest.json',
       *['output/liuren-bifa-audit-20261111/'+name for name in ['engine-720-geometries.json','engine-bifa-lookup-720.json','engine-day-night-1440.json','audit-conditions.py']]]
save('source-hashes.json',[{'path':p,'sha256':digest(ROOT/p)} for p in paths])
md=['# 百法导出与本轮核查覆盖表','', '状态只针对结构条件；“本轮未导出”不等于该法无效或引擎应逐盘报告它。编号4归46；错号84的文本单独标错，并只在统计题名时归82。','', '|法|标准题名|导出盘数|条目数|结构符合|扩展符合|需昼夜|部分条件|不符|待核|口径待核|','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for f in families:
    c=f['status_counts'];md.append('|'+str(f['number'])+'|'+f['standard_title']+'|'+str(f['chart_count'])+'|'+str(f['entry_count'])+'|'+ '|'.join(str(c.get(k,0)) for k in ['结构符合','扩展符合','需昼夜条件','部分条件符合','条件不符','待核','口径待核'])+'|')
(OUT/'百法覆盖表.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('FLAGGED SUBTYPES')
for item in per_label:
    if any(k in item['statuses'] for k in ['条件不符','部分条件符合','导出污染']):print(json.dumps(item,ensure_ascii=False))
