"""One-time local33 clarification; keep frozen32, books and prior evidence intact."""
from pathlib import Path
import hashlib, json, os, shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
OLD, NEW = '20261108-unified-32', '20261108-clarified-33'
BASE = ROOT/'runtime/liuren'/OLD
R = ROOT/'runtime/liuren'/NEW
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text('utf-8-sig'))
def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding='utf-8')
def dump(p, value): write(p, json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def replace(p, old, new):
    s = p.read_text('utf-8'); assert old in s, (str(p), old)
    write(p, s.replace(old, new))
def replace_line(p, prefix, line):
    lines = p.read_text('utf-8').splitlines()
    matches = [i for i, s in enumerate(lines) if s.startswith(prefix)]
    assert len(matches) == 1, (str(p), prefix, matches)
    lines[matches[0]] = line
    write(p, '\n'.join(lines)+'\n')
def link(rel, line, label=None):
    return '['+(label or f'{Path(rel).name}:{line}')+'](<'+(ROOT/rel).as_posix()+':'+str(line)+'>)'

p = load(ROOT/'.opencode/liuren-active.json')
assert p['release'] == OLD and not R.exists(), 'One-time publisher; do not overwrite snapshots'
live = ['.opencode/liuren-active.json', '.opencode/oh-my-opencode-slim.jsonc', 'opencode.json',
        '.opencode/skills/liuren/daliuren/SKILL.md', 'integrations/codex/daliuren-codex/SKILL.md',
        'integrations/codex/daliuren-codex/references/host.md', 'AGENTS.md', 'README.md', '目录总索引.md',
        'docs/本机六壬高效执行.md', 'docs/本机六壬完整研判流程.md', 'docs/本机六壬稳定运行指南.md',
        'docs/Codex大六壬工作流.md', 'tools/tests/liuren-codex.test.mjs']
review = load(ROOT/'output/liuren-rules-review-20261108/连续原文与校验.json')
source_paths = sorted({row['path'] for row in review['evidence']} |
                      {row['path'] for row in load(BASE/'references/confirmed-policy-evidence.json')['evidence']})
before = {'release': OLD, 'files': {rel: sha(ROOT/rel) for rel in live},
          'frozen32': {f.relative_to(BASE).as_posix(): sha(f) for f in BASE.rglob('*') if f.is_file()},
          'sourceBooks': {rel: sha(ROOT/rel) for rel in source_paths}}
for rel in live:
    dest = OUT/'before'/rel; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT/rel, dest)
for rel in ['SKILL.md', 'references/host.md']:
    installed = Path('C:/Users/QLMa_/.codex/skills/daliuren-codex')/rel
    dest = OUT/'before/installed-skill'/rel; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(installed, dest)
dump(OUT/'before.json', before)
shutil.copytree(BASE, R)

u03 = '- **U03 直接临生合、类神状态与对我作用。**“类神临生临合，自贪其荣，不能为我所用”按原文执行，不限官鬼：所减弱或难发挥的是该类神对日主、本问本应承担的作用，不是断其自身能量消失。财贪生合则财难为我得，父母/生气贪生合则难以生我，鬼煞贪生合则难来刑冲克害于我；所求为何决定这种停用是利是弊。须定位上下直接临处，不能把别处生扶等同贪恋所在之处。自身得养、旺相有权与对我实际发挥作用分层看；日干、吉神得旺禄照喜旺恶衰论，不因一切生合便自动判失用。此为已定解释，C02关闭，不再要求用户确认非官鬼范围。'
u04_tail = '胎爻专项依北海《毕法》1463—1467另按其明示取类：甲乙寅卯胎酉，丙丁巳午胎子，庚辛申酉胎卯，壬癸亥子胎午，戊己辰戌丑未胎子或午；干支胎同等重要，土胎两处都登记。该专项取类不改通用日干状态表，不以事后结果选有利胎位；不等同采用引擎未登记的同名神煞。C08关闭。'
layer = '通类定大方向、分类/专类定具体对象，二者分层兼看，不列作互斥方法。实际财物得失以财爻为主线；财源、办证等具体事项依对应专类细断，不能拿通类吉替代专类所示的具体阻碍。'
gate = '只有同一对象、同一位置关系、同一时段气态、同一占类及判断目标下，完整上下文仍给出互不相容的结论，才登记真正矛盾；须附双方原句、条件和直接跳转。对象、层次、阶段或条件不同而原书已有明确解释的，模型自行理解并执行，不留作用户确认。资料覆盖不足、OCR校勘、程序取法差异分别登记，不冒充理论矛盾。'
u11 = '- **U11 两级裁决与矛盾处理。**'+gate+' '+layer+' 主智能体准备中性材料，候选可纠正；focus_issues只列本问真实未知条件或通过上述检验的冲突，无则[]，不因历史C编号尚存便自动重开。裁决者从完整盘独立查漏，依同版U规则及连续原文裁关键作用和结果，不能任选旧句反向执行。C01—C11是分类复核历史，不是待确认清单，也不限制发现真正的新矛盾。决定性处说明采用规则、实际条件及最强反证；主智能体核事实、引用、覆盖、内部及U口径一致性，不另行折中改判。具体违规逐字定位报告、U编号和绑定证据，依宿主一次补核协议处理，Codex复用原子智能体；格式差异或单纯不同意结果不重裁。已知反馈不混入新盲断材料。'

for rel in ['references/confirmed-judgment-policy.md', 'references/judgment-core.md']:
    f = R/rel
    replace_line(f, '- **U03 ', u03)
    lines = f.read_text('utf-8').splitlines()
    for i, s in enumerate(lines):
        if s.startswith('- **U04 '): lines[i] = s+' '+u04_tail
        if s.startswith('- **U02 '): lines[i] = s.replace('刑虎等交叉见C03。', '刑虎等组合按原文明示条件分析，不因组合复杂便另列未解矛盾。')
        if s.startswith('- **U07 '): lines[i] = s.replace('季土细分见C05。', '季土条件表差异属C05程序取法记录，不据此宣称已发现同条件理论矛盾。')
        if s.startswith('- **U08 '): lines[i] = s.replace('此处已统一分析方法；具体何种中间组合足以落实尚见C04，不能又把整个空亡问题泛称未决。', '此处综合分析方法已定，由模型按具体条件判断；原书强语差别见C04来源复核记录，不要求用户逐一确认中间组合，也不重开整个空亡争论。')
        if s.startswith('- **U10 '): lines[i] = s+' 应期视用/视末依《理法简易》985明文分阶段：一般视用；吉事已动、凶事已萌而问后续成散时宜视末，不以结果倒选方法，C09关闭。'
    write(f, '\n'.join(lines)+'\n')
    replace_line(f, '- **U11 ', u11)
    replace(f, '尚未定清的具体边界只登记在pending-conflicts，不能把已确认内容重新列为二说。', 'pending-conflicts保留历史条目的分类复核；已明文解释者直接执行，只有经同条件检验仍互斥者才列真正矛盾。')

# Replace old artificial-pending banners without altering source quotations.
old_banner = '尚待确认的具体边界只见pending-conflicts的C01—C11，不能笼统重开全部理气争论。'
new_banner = '历史C01—C11的关闭或重新分类见pending-conflicts；明确的分层、阶段及条件解释直接执行，只有完整上下文不能化解的同条件互斥才列真正矛盾。'
for f in R.rglob('*.md'):
    s = f.read_text('utf-8')
    if old_banner in s: write(f, s.replace(old_banner, new_banner))

f = R/'methods/positioning.md'
replace(f, '专项胎神是否另属独立取类见C08，不双取凑答案', '胎爻专项依北海明示取类，干支胎同重、土胎子午两处保留，详见pregnancy，不更改通用日干状态')
replace_line(f, '财通专、类不现的内部差异', layer+' 类不现按原书占类路径、气态及实际联系分析，不能用无关系统补成必现；明确排除条款与特殊组合按各自范围执行。已有解释直接采用，不用作者排序或结果换法。')
f = R/'methods/adjudication.md'
replace_line(f, '主智能体先采用核心U01—U11，真实未决仅限', '主智能体先采用核心U01—U11。focus_issues只列本问真实未知条件或完整上下文不能化解的同条件互斥；历史C编号不是待确认清单，不限制发现新的真实矛盾。通类与分类的层次、贪生合对日主作用、北海胎爻取类及视用/视末阶段分工均已明确，直接执行，不要求用户再确认。必要观察带适用U编号及最强反证，不先写完整判词。裁决者对照同版核心从完整盘补漏，独立裁作用和结果；旧书异句不自动成为反向指令。只有同对象、同位置关系、同时段气态、同占类及判断目标仍互不相容时，才列双方原句、条件和原文跳转供复核。')
f = R/'methods/liqi.md'
replace(f, '只有C05季土细分、C08专项胎神等尚未确认且会改变本问的边界才列具体条件', '胎爻专项按北海已定；C05季土条件表差异单列程序口径，真实影响本问时依相应来源说明所用表及理由')
f = R/'methods/timing.md'
replace_line(f, '- **ce-lli 视用 vs 视末之争', '- **视用与视末的阶段分工（C09已关闭）**：《理法简易》983—989，尤其985明说一般应期宜视用；“惟吉事已动，凶事已萌之际占之，应期宜视末传耳”。按已知事态及所问起始/终结采用，不再列为两种竞争理论或待补书证。')
replace_line(f, '- **空的具体实现条件C04**', '- **空的实现与时间**：按U08/U10及空亡模块核具体对象、生坐制处、承接和时段；原书差别见C04来源复核记录。不能由预期结果反选方便方法，也不把缺少数字阈值当成必须请用户确认的矛盾。')
f = R/'methods/void.md'
replace(f, '决定性中间条件未定时定位C04，说明缺的是何种实现条件。', '由裁决者依实际组合分析，只有缺少决定性事实或同条件原文确实互斥才具体报告；C04保留来源措辞的复核记录。')
replace(f, '只有具体实现边界列C04', '具体实现依U08综合分析，C04留存来源措辞差别')
replace(f, '具体适用阈值仍属C04。', '不设未经确立的数值阈值，也不以缺少阈值为由要求用户确认每种组合。')
replace(f, 'C04只保留未定的具体效应边界', 'C04只保留原文措辞的待核记录，非另一条执行规则')

f = R/'domains/finance.md'
replace(f, '财不现的分支与通专优先有内部差异，见D01，不以单句永久否定其他条文。', '通类与专类按D01分层，财不现依原书所列年命、遁财、生合气地等条件分析，不从单句推出全盘无财可得。')
s = f.read_text('utf-8'); a = s.index('### LR26-TXY-D01 '); b = s.index('## 原有方法的独有检查', a)
section = '''### LR26-TXY-D01 已明确：通类与分类分层，得财与财源分职责

适用：先明确问的是实际钱物能否取得，还是某项财源、办证、经营等具体事件。

'''+layer+'''

执行：通类提供一般方向，专类提供精确条件。问贵人办证，不能以贵人实替代朱雀所指文书的状态；问实际得财，以财爻的气态、阴神、与财者及取者通路判断得失，同时由天乙、勾陈等说明对应财源及条件。原文“财现以财为主”落实到财物得失主线，“俱入以专类为断”落实到具体所问，不当作两个模型可以任选的全局优先表。

财不现亦须读完整条件：课传、年命、遁财、生合有路、旺相不空伤及类阴益日等按各自原条使用；不能把课传不现和与我完全无涉混同。

身份：用户本轮确认的执行解释及连续原文分层；不是更改原书字句。C01关闭，不再列候选未裁定。

出处（Python splitlines）：《理法简易》1393—1395、2709—2715、3437—3447、3479—3487；《壬归》355—359。原书措辞保持，当前解释不能冒称原书逐字一致。

'''
write(f, s[:a]+section+s[b:])
replace(f, '## 本批分工与未决采用记录', '## 分工与来源覆盖记录（覆盖不足不等于理论矛盾）')
replace_line(f, '| 通类、专类俱现或类不现 |', '| 通类、专类俱现或类不现 | 通类定方向，专类定具体目标；财爻主实际钱物，专类察财源/专事，兼看作用通路 | D01已按层次解释，不列待确认；不现依相应原条的年命、遁财、生合等条件，不换法凑结果 |')

f = R/'domains/pregnancy.md'
replace(f, '土胎子午存在北海内部起法差异，须列法别，不能双取凑命中。；', '依北海明文，土胎子午两处均保留，干支胎同等重要；先登记位置与实际关系，再判断，不能事后挑有利一处。')
s = f.read_text('utf-8'); a = s.index('### LR26-TXY-D02 '); b = s.index('## 原有方法的独有检查', a)
section = '''### LR26-TXY-D02 已采用：北海胎爻专项取类

'''+u04_tail+'''

《毕法赋全解》1463明确胎爻表，1465以戊寅日干上酉、支上午说明互胎，1467明说“干支之胎爻同等重要”“土之胎有两处”。照此执行，无须另请用户确认专项是否存在。子午并列是本条明示的两个胎位，不是任取两套通用长生表。

通用状态仍依U04：日干天干阳顺阴逆，支将五行顺行；胎爻取类与某对象在某处的状态分别标明。干胎、支胎均核真实落点、气态及组合，不因双胎位就计两票或保证有孕。

身份：用户指定以北海为准，并由上述原文明示支持；C08关闭。原先对不同起法的来源记录保留在冻结32及原书，不再作为本版任选指令。

出处：《毕法赋全解-正式整理本.md》1463—1467（Python splitlines一基行号）。

'''
write(f, s[:a]+section+s[b:])

# Role text and actual executable host prompts must agree.
f = R/'references/adjudicator-book-basis.md'
replace(f, '类神停用能否扩及财类尚见C02，不把一切得生解释为失用。', '按U03，财难为我得、父母难生我、鬼难害我，均指对我的预期作用受限，非类神自身能量归零；C02已关闭。不把一切得旺禄解释成失用。')
replace(f, '与E20/E21的交叉边界并未全部统一。', '与E20/E21按占类、仕庶、位置、刑害及制救条件逐项解释；不因条件复杂便标为未解矛盾。')
replace(f, '非官鬼停用范围只保留C02。', '类神对我的作用受限不局限官鬼，C02已按原文解释关闭。')
replace(f, 'E07/E15/E20/E21的组合边界仅属C03。', 'E07/E15/E20/E21的具体条件照原文分析，C03为已重新分类的组合说明。')
role = (BASE/'references/adjudicator-prompt.md').read_text('utf-8').split('# 固定书据：条件摘要与关键短引')[0]
role = role.replace('C03具体组合仍缺条件时才指出边界，不逐盘择吉换法。', '按原文具体组合自行分析；只有满足同条件互斥检验才报矛盾，不逐盘择吉换法。')
role = role.replace('非官鬼停用范围仅列C02，不把所有生合重新列为未决。', '财难为我得、父母难以生我、鬼难以害我均为对我作用受限，非自身能量消失；C02已关闭，不再以非官鬼范围请用户确认。')
start = role.index('严格采用核心U01—U11')
role = role[:start]+'严格采用核心U01—U11。'+gate+' '+layer+' 胎爻专项按北海、土胎子午并存、干支胎同重；应期视用/视末按明示阶段执行。C01—C11是已关闭、来源复核、程序或校勘事项的分类历史，不是待确认清单，不限制核出新的真实矛盾。只在实际影响本问时查相应连续原文，已有明确解释直接采用。决定性处说明规则、实际条件及最强反证；具体违规依一次补核协议纠正，主智能体不得另行折中改判。\n\n'
role += f.read_text('utf-8')
write(R/'references/adjudicator-prompt.md', role)
cfg = load(ROOT/'.opencode/oh-my-opencode-slim.jsonc'); cfg['agents']['liuren-adjudicator']['prompt'] = role
dump(ROOT/'.opencode/oh-my-opencode-slim.jsonc', cfg)

LF = '书籍库/北海闲人/理法简易.txt'; BF = '书籍库/北海闲人/毕法赋全解-正式整理本.md'; RG = '书籍库/经典古籍/佚名/壬归.txt'
rows = [
 ('C01', '已明确，关闭', layer, [(LF,1393),(LF,2709),(LF,3437),(LF,3479),(RG,355)]),
 ('C02', '已明确，关闭', '贪生合使类神对日主的预期作用减弱/难发挥；财难得、父母难生、鬼难害。自身得养与对我作用分开，直接临处与别处生扶分开。', [(LF,815),(LF,6053),(BF,1259),(LF,2607)]),
 ('C03', '组合条件，非已证矛盾', '按喜旺恶衰及原段的仕庶、刑害、发用、凶将、本人和救神状态判断；没有同条件相反证据前，不因关系多就要求用户确认。', [(LF,1007),(LF,4901),(BF,1235),(RG,759)]),
 ('C04', '来源措辞待核；执行口径已定', '“得生得助不为空”与“有生也为空”确有文字对立，须连同各自案例条件解释，不能抹平；目前不据这两句话宣称同条件规则已互斥。旬空事实保留，依U08/U10察生处、坐处、制处及时间和承接，由模型具体判断，不重开空亡原则。', [(LF,5495),('书籍库/北海闲人/北海闲人，特训班讲义.txt',77),(LF,5579),(LF,5597)]),
 ('C05', '程序条件表/取法记录，非理论矛盾', '程序同时给four-seasons与quarter-earth（例如戌月土休/旺不同），未在本轮擅自统一为单一季土算法。沿所用原法说明适用表及理由，不把两表当两票、不按期望结果换表；决定性差异缺依据时具体披露为程序取法缺口，不冒充古籍同条件矛盾。', [('书籍库/现代著作/六壬大全（简体版）.txt',4027)]),
 ('C06', '原文已有条件解释', '生克刑合并行，依旺衰、乘将及上下位置定主作用；北海二字刑、单见自刑、半合按原条采用。四纲引化只属该笔记方法，不混同半合与化局，不由四纲推出普遍免刑。', [(LF,821),(LF,843)]),
 ('C07', '占类范围分路，非已证矛盾', '类不现按北海对应占类路径处理；原神将、乘支、坐处保持真实位置，查八门只是有出处的专项条件，不自动补成课传中有类，不把四课与八门的不同用途称为冲突。', [(BF,4794),(LF,3437)]),
 ('C08', '北海专项已采用，关闭', '胎爻依北海：干支胎同重，土胎子午两处均留；专项取类和通用天干/五行状态表分开，不改日干通用十二长生。', [(BF,1463)]),
 ('C09', '明确阶段分工，关闭', '《理法简易》985已明确一般视用，吉事已动、凶事已萌之际宜视末。按原问已知阶段直接用；此前“未找到书证”的登记错误已纠正。', [(LF,983)]),
 ('C10', '适用范围/覆盖记录，非已证矛盾', '非所占之类不另起新问；特殊婚姻等组合按专项完整条件用。类不现按占类、成败、属性分路，明确条文直接执行，不要求逐条再确认。', [(BF,4794)]),
 ('C11', '文字校勘队列，非理论裁决', '阴阳吉凶、蚕丝寅卯申、戌亥及“河SA合”等先核版本/上下文；不凭疑字裁决定性结果，也不让用户替模型做文字投票。', [('书籍库/北海闲人/北海闲人-神将释.txt',743),('书籍库/经典古籍/唐宋/六壬心镜-唐-徐道符.txt',940)])
]
audit = '# 矛盾复核：当前做法与原文入口\n\n'+gate+'\n\n本轮未新增已证实的同条件互斥理论命题；这不等于宣称全书无异文或全局已经穷尽审查。原C01—C11按下列状态保留追溯，不再统称待确认。C04是原文措辞复核，C05是程序取法，C11是校勘；均不自动生成待用户裁决的问题。\n\n'
for id, status, practice, refs in rows:
    audit += '## '+id+' '+status+'\n\n当前执行：'+practice+'\n\n原文入口：'+'；'.join(link(rel,line) for rel,line in refs)+'。\n\n'
audit += '行号采用Python splitlines一基行号；引用连续段、编码及原文件SHA256见confirmed-policy-evidence。原书字节保留。执行解释、用户指定口径与原句分别注明，不将分层解释冒称古籍逐字一致。\n'
write(R/'references/pending-conflicts.md', audit)
write(OUT/'矛盾复核与原文入口.md', audit)

# Include source passages supporting the closures in bound, readable evidence modules.
ev = load(R/'references/confirmed-policy-evidence.json')
spans = [(LF,815,819),(LF,6053,6059),(LF,1393,1395),(LF,2709,2715),(LF,3437,3447),(LF,3479,3487),(BF,1463,1467),(LF,983,989)]
for n,(rel,a,b) in enumerate(spans,1):
    src = ROOT/rel; text = src.read_text('utf-8-sig').splitlines()
    row = {'id':f'CL{n:02}', 'path':rel, 'encoding':'utf-8-sig', 'line_mode':'universal',
           'line_start':a,'line_end':b,'quote':'\n'.join(text[a-1:b]),'sha256':sha(src),
           'source_identity':'北海本地整理文本；原句与本轮执行解释分列，非预测效果证据'}
    ev['evidence'].append(row)
ev['source_scope'] = sorted(set(ev['source_scope']) | {s[0] for s in spans})
dump(R/'references/confirmed-policy-evidence.json', ev)
supp = '\n\n## 33版已明确事项的连续原文（CL01—CL08）\n\n'
for row in ev['evidence'][-8:]:
    supp += '### '+row['id']+' '+link(row['path'],row['line_start'])+'\n\n'+ '\n'.join('> '+s for s in row['quote'].splitlines())+'\n\n'
write(R/'references/confirmed-policy-supplements.md', (R/'references/confirmed-policy-supplements.md').read_text('utf-8')+supp)
reg = load(R/'references/confirmed-policy-register.json'); reg['release'] = NEW
reg['pending'] = {'confirmed_same_condition_contradictions':[], 'registry':'pending-conflicts', 'historicalIDs':'C01-C11', 'notAUserConfirmationQueue':True}
reg['clarifications'] = {'C01':'closed-layered-general-specific','C02':'closed-effect-on-subject-not-own-energy','C08':'closed-Beihai-special-fetal-class','C09':'closed-explicit-stage-distinction'}
for row in reg['rules']:
    add = {'U03':['CL01','CL02'], 'U04':['CL07'], 'U10':['CL08'], 'U11':['CL03','CL04','CL05','CL06']}.get(row['id'],[])
    row['evidence'] = list(dict.fromkeys(row['evidence']+add))
dump(R/'references/confirmed-policy-register.json', reg)

host_note = '矛盾登记执行33版U11：'+gate+' 贪生停用按类神对我的作用解释（财难得、父母难生、鬼难害）；通类/分类分层；胎爻依北海（干支胎同重、土胎子午两处），应期视用/末依原文明示阶段。历史C01—C11不是待确认清单，不能机械填入focus_issues。'
for rel in ['.opencode/skills/liuren/daliuren/SKILL.md','integrations/codex/daliuren-codex/SKILL.md','integrations/codex/daliuren-codex/references/host.md']:
    f = ROOT/rel; s = f.read_text('utf-8')
    s = s.replace('具体待确认边界见pending-conflicts的C01—C11，更换模型不等于这些边界或预测效果已经验证。','历史事项的关闭与分类见pending-conflicts；更换模型不等于预测效果已经验证。')
    s = s.replace('真实缺口才列C编号及所缺条件','真实缺口说明所缺条件，不因历史C编号自动重开已定事项')
    write(f, s+'\n\n'+host_note+'\n')
cfg = load(ROOT/'opencode.json')
cfg['agent']['liuren']['prompt'] = cfg['agent']['liuren']['prompt'].replace('focus_issues只留真实条件缺口/C编号','focus_issues只留本问真实未知条件或同条件仍互斥的矛盾，不机械列历史C编号')+'\n'+host_note
# Runtime permissions are versioned too; leave unrelated configured values intact.
dump(ROOT/'opencode.json', json.loads(json.dumps(cfg,ensure_ascii=False).replace(OLD,NEW)))

note = '\n\n33版解释与矛盾登记修订（'+NEW+'，覆盖32版相反的“待确认”措辞）：贪生停用指类神对日主的作用受限，财、父母、鬼分别释义；通类/分类分层，胎爻专项依北海（干支胎同重、土胎子午两处），应期视用/视末按原文明示阶段。主、子智能体共同按U11筛选真正同条件互斥；明确条文自行解释执行，不要求用户再确认。C01—C11已逐项关闭或重新分类，不再作为待确认清单；来源措辞、程序取法和文字校勘另记。工具契约、宿主模型与额度不变，仅本机；OpenCode重启新会话加载，Codex新任务读取活动指针，历史任务沿原绑定版本。记录见output/liuren-clarified-rules-20261108/矛盾复核与原文入口.md。\n'
for rel in ['AGENTS.md','README.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md','docs/本机六壬稳定运行指南.md','docs/Codex大六壬工作流.md']:
    f = ROOT/rel; s = f.read_text('utf-8')
    s = s.replace('32版已确认口径更新（','32版历史记录（现行33版已修订待确认登记；')
    if rel == 'README.md': s = s.replace('指向 `'+OLD+'`','指向 `'+NEW+'`')
    s = s.replace('当前本机32版','当前本机33版').replace('当前32版','当前33版')
    s = s.replace('具体尚未确认的边界见C01—C11','历史C01—C11按33版关闭或重新分类')
    write(f, s+note)
replace(ROOT/'目录总索引.md', 'runtime/liuren/'+OLD+'/', 'runtime/liuren/'+NEW+'/')

# Meaningful regression: current adopted explanations and classification reach actual child packet.
f = ROOT/'tools/tests/liuren-codex.test.mjs'
replace(f, "assert.ok(role.professional_instructions.includes('C01—C11'));", "assert.ok(role.professional_instructions.includes('不是待确认清单'));\n assert.ok(core.shared_method.includes('财难为我得'));\n assert.ok(core.shared_method.includes('父母/生气'));\n assert.ok(core.shared_method.includes('干支胎同等重要'));\n assert.ok(core.shared_method.includes('通类定大方向'));\n assert.ok(core.shared_method.includes('吉事已动、凶事已萌'));\n assert.ok(!core.shared_method.includes('贪生停用能否扩大到财类'));" )
replace(f, "assert.ok(pending.content.includes('C11'));", "assert.ok(pending.content.includes('C11'));assert.ok(pending.content.includes('已明确，关闭'));assert.ok(pending.content.includes('非理论裁决'));" )

# Version and source bindings; publish pointer only after all concrete writes are complete.
policy_meta = {'id':'liuren-clarified-policy-33','rules':'U01-U11','mandatoryCore':True,'pendingRegistry':'pending-conflicts','registryIsConfirmationQueue':False,'sourceConsensus':False,'predictiveValidationCount':0}
for name in ['loader-contract.json','manifest.json']:
    d = load(R/name); d.update(release=NEW,parentRelease=OLD,authoringSource=OUT.relative_to(ROOT).as_posix(),confirmedJudgmentPolicy=policy_meta)
    if 'computeInterface' in d: d['computeInterface']['release'] = NEW
    if 'bookRetrieval' in d: d['bookRetrieval']['compatibleMethodRelease'] = NEW
    if name == 'loader-contract.json': d['sourceHashes'] = {rel:sha(ROOT/rel) for rel in d['sourceHashes']}
    dump(R/name,d)
d = load(R/'references/shensha-policy.json'); d['release'] = NEW; dump(R/'references/shensha-policy.json',d)
d = load(R/'reading-route.json'); d['release'] = NEW; d['labels']['pending-conflicts'] = '历史争点分类与真实矛盾登记'; dump(R/'reading-route.json',d)
m = load(R/'manifest.json'); m['files'] = {rel:sha(R/rel) for rel in m['files']}
m['version'] = hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest(); dump(R/'manifest.json',m)
p.update(release=NEW,runtime=R.relative_to(ROOT).as_posix(),previousRelease=OLD,backup=(OUT/'before').relative_to(ROOT).as_posix(),authoringSource=OUT.relative_to(ROOT).as_posix(),methodVersion=m['version'],confirmedJudgmentPolicy=policy_meta)
if 'bookRetrieval' in p: p['bookRetrieval']['compatibleMethodRelease'] = NEW
if 'computeInterface' in p: p['computeInterface']['release'] = NEW
p['files'] = {rel:sha(ROOT/'.opencode/skills'/rel) for rel in p['files']}
p['workflowImplementation'] = {rel:sha(ROOT/rel) for rel in p['workflowImplementation']}
p['bookRetrieval']['files'] = {rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
assert all(sha(BASE/rel)==h for rel,h in before['frozen32'].items())
assert all(sha(ROOT/rel)==h for rel,h in before['sourceBooks'].items())
assert sha(R/'references/adjudicator-book-evidence.json')==sha(BASE/'references/adjudicator-book-evidence.json')
tmp = ROOT/'.opencode/liuren-active.clarified33.tmp'; dump(tmp,p); os.replace(tmp,ROOT/'.opencode/liuren-active.json')
dump(OUT/'activation.json',{'release':NEW,'methodVersion':m['version'],'previousRelease':OLD,'after':{rel:sha(ROOT/rel) for rel in live},'frozen32Intact':True,'sourceBooksIntact':True,'E01_E22OriginalBytesIntact':True,'paidModelCalls':0,'predictiveValidationCount':0})
write(OUT/'已确认判断规则.md', (R/'references/confirmed-judgment-policy.md').read_text('utf-8'))
print('Published local33; frozen32/books/original E01-E22 unchanged. Installed skill sync and verification still required.')
