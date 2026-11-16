"""Build and activate the user-directed local liqi hierarchy; preserve frozen inputs."""
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
PARENT = '20261104-chart-first-02'
RELEASE = '20261105-liqi-led-01'
OUT = ROOT / 'output' / RELEASE
SOURCE = ROOT / 'knowledge/liuren-v3/revisions' / RELEASE


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text('utf-8'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n',
                    encoding='utf-8', newline='\n')


def inventory(base):
    return {p.relative_to(base).as_posix(): sha(p.read_bytes()) for p in sorted(base.rglob('*')) if p.is_file()}


def replace(text, old, new):
    if text.count(old) != 1:
        raise ValueError('expected one edit anchor: ' + old[:90])
    return text.replace(old, new, 1)


def insert(text, body):
    heading, rest = text.split('\n', 1)
    return heading + '\n\n' + body.strip() + '\n' + rest


def main():
    ptr = ROOT / '.opencode/liuren-active.json'
    pointer = load(ptr)
    old = ROOT / pointer['runtime']
    new = ROOT / 'runtime/liuren' / RELEASE
    if pointer['release'] != PARENT or OUT.exists() or SOURCE.exists() or new.exists():
        raise ValueError('baseline changed or destination exists; refusing overwrite')
    manifest = load(old / 'manifest.json')
    frozen_before = inventory(old)
    if any(frozen_before.get(k) != v for k, v in manifest['files'].items()):
        raise ValueError('parent runtime hash mismatch')
    live = ROOT / '.opencode/skills/liuren'
    editable = [ptr, ROOT / 'opencode.json', ROOT / 'README.md', ROOT / '目录总索引.md',
        ROOT / 'AGENTS.md', ROOT / 'docs/本机六壬完整研判流程.md', ROOT / 'docs/本机六壬高效执行.md',
        ROOT / 'tools/tests/test_liuren_class_mapping.py', *[p for p in live.rglob('*') if p.is_file()]]
    before = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in editable}
    for path in editable:
        dest = OUT / 'before' / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    write(OUT / 'before-manifest.json', before)
    shutil.copytree(old, new)
    changes = {}

    def change(rel, text):
        changes[rel] = text
        write(SOURCE / rel, text)
        write(new / rel, text)

    liqi = (old / 'methods/liqi.md').read_text('utf-8')
    liqi = insert(liqi, '''## 本机裁决总则：理气为骨，象法为肉

2026-11-05 用户明确决定的本机方法层级：理气贯穿全局，统摄事件大势、走向、成败及转折；象法在理气允许的走势内描述人物、事物、表现形式和具体情境，不凭象名或象义改变理气结论。提高权重体现为分析次序、覆盖范围与裁决权限，不设没有验证依据的百分比。本总则是用户选择的执行规范，不冒称原书一致主张或预测效果已证。

理气包括：月令五气、主体与关键类神的临地十二气、旺衰得失、生扶泄耗与克制、合及刑冲破害、旬空空墓、神将内外战、四课三传的结构与传递、直接阴神及已核年命的有效作用、制化救应及其作用范围。四课三传与关键类神构成同一个分析整体；不能把“理气”缩成日干旺衰，也不能把“象法”泛指神将的一切信息。天将/支神的五行、气地与实际生克是理气；名称、形貌、人物/职业及事物辞义是取象。同一节点有两种用途，须分清其依据。

### 全局主线与关键类神

基本取用后，先作全局理气分析，再深化象义；全局结论须包含关键类神，不能先只看课体得一个结论，再把类神当点缀。按下列关系组织一条可核对主线，可用文字或简表，不另造打分表：

| 范围 | 必须落实的关系与判断 |
|---|---|
| 时令与主体 | 月令下日干、日支所定位对象及相关上神谁得气、谁受损；五气、十二气和六亲分别注明参照 |
| 四课 | 干支、干上支上、干阴支阴之间的生克扶损、合刑冲害与空墓；哪一关系构成主要支持或主要阻碍 |
| 三传 | 发用如何承接四课，初中末的生克传递、气势增减、归宿及阻断；不机械当成过去现在未来 |
| 关键类神与课传 | 分类所取主体、目标、作用者、阻碍及救应等实际关键类神，各自与日干支、干上支上、四课和三传有哪些切题的直接或有据间接作用；在课传中何位、不在时依何专法参与 |
| 关键类神之间 | 谁生扶谁、谁克制或耗泄谁、谁合住或冲动谁，双方力量及实际通路如何；同角色多种候选要辨职责，不能合并计票 |
| 制救与变化 | 关键阻碍是否解除、救者自身是否有力、能否到达；动态与年命是否改变前述关系及哪个结果分支 |

逐个关键类神核自身状态、与课传的关系及与其他关键类神的关系；只展开对本问有实际作用的边，不机械穷举所有两两组合，也不凭未入传就删除专法允许的对象。尚未弄清的关键定位或关系保留分支，不能先用象辞填成确定结论。

全局小结说明：本问主要力量与气势方向、主客承受或取得条件、贯穿四课三传和关键类神的作用链、主要阻碍、最强理气反证、有效制救与尚存条件。随后将相关象义逐一挂到这条主线上；若无依据细化就保留描述缺口，不编具体故事。

### 理气与象法冲突时怎样处理

- 理气已支持或不支持某结果时，吉将吉煞名称、凶象名称、形貌/职业象、相似案例断语和象义数量均不能单独翻判，也不能独立决定结果程度。象法只表达已有走势及有据程度，不借“吉中有忧”等辞句另造损失或成功。
- 象义与主线不合，检查象义映射是否适用；必要时复查盘源、对象定位及遗漏关系。若发现真实定位错误、新的有效旺衰生克、通路或救制，更新全局理气后再裁决。不能为了保住初判拒收理气反证，也不能把换象当成已经完成理气改判。
- 理气仍不足以裁决时，保留未定及条件分支；象法不能代替理气填出确定成败。全局与局部出现差异，要比较同一事件阶段、作用对象、力量与关键环节，不预设任何单项课名或类神标签永久最大。

上述层级适用于本机单事及分类占；出生推命按其专门规程另核，不将本轮单事调整默认为其方法验收。''')
    change('methods/liqi.md', liqi)
    text = (old / 'methods/positioning.md').read_text('utf-8')
    text = replace(text, '三者互核，无永久主次。', '三者共同纳入全局理气，由旺衰、生克传递、阻断和制救裁决大势与结果；象义只在该走势内作具体描述。')
    change('methods/positioning.md', insert(text, '定位服务于全局理气，不以角色表或象义清单替代判断。明确主体和关键类神后，按 `liqi` 同时检查其自身状态、与四课三传及彼此之间的关系；定位修订须重核整条作用链。'))
    text = (old / 'methods/class-mapping.md').read_text('utf-8')
    text = replace(text, '无永久九系统、课体或三传优先表；主类神未必是决定结果的作用点。', '九系统提供取用依据，关键类神须与四课三传一起进入理气裁决；不按类神或课名标签直接定结果。')
    change('methods/class-mapping.md', insert(text, '本机采用“理气为骨、象法为肉”。分类取用确定理气所分析的对象；关键类神既看自身旺衰气地，又看其与四课三传及其他关键类神的实际作用。专法中的吉凶象辞保留来源和条件，不能越过共同理气直接裁决成败；具体形象依已判走势表达。'))
    change('methods/relations.md', insert((old / 'methods/relations.md').read_text('utf-8'), '''## 关键类神进入全局关系

坐标核清后，把分类关键类神同时放入四课三传的理气关系中。对每个关键类神，核与日干支、干上支上及相关四课、三传节点的作用，并核关键类神彼此的生克扶损、合刑冲害、空墓与制救。注明施受双方、力量、通路及影响的结果环节；不机械穷举无关关系。主体、目标、阻碍和救应按本问实际需要确定，不强行增补角色。关系矩阵是全局理气的输入，不能只用来贴人物与物品标签。'''))
    text = (old / 'methods/structure.md').read_text('utf-8')
    text = replace(text, '面对的问题是：取不到具体类神（如单位没明说、占宏观走向、占阶段大势），或占问本身就是"向何方向发展"类，这时不能靠单个象点断，而要**读课体的整体气势**。', '所有占类都先将四课三传结构纳入全局理气，不以取不到类神或宏观问题为前提。分类占同时核关键类神与结构的实际作用；课体名称和象辞不能独立决定方向。')
    text = replace(text, '产出：方向性结论——"吉课则吉、凶课则凶"，并给出气势强弱与阻滞点（如干支乘墓＝墓主阻滞、墓覆支＝走下坡路）。', '产出：由实际课传关系、旺衰、关键类神与制救共同支持的方向、强弱与阻滞点；不以“吉课则吉、凶课则凶”作为独立裁决规则。')
    change('methods/structure.md', insert(text, '本模块在理气总纲阶段必读并运用，动态深化后复核已有结构，不等到后段才补全局。以下原法、例断与反例保留来源身份；其课名象辞均受 `liqi` 的理气裁决层级约束。'))
    text = (old / 'methods/movement.md').read_text('utf-8')
    text = replace(text, '被引动的类象=动爻，力量强、显象明确、优先采信；未引动者标为静态弱信号。', '被引动提供变化候选，实际力量及能否成事须回到全局理气；静态对象仍可能构成关键制约，不能自动降低权重。')
    change('methods/movement.md', insert(text, '动态贯穿既有全局理气：追踪四课三传、关键类神及彼此关系如何得助、受阻或受救。阴神、年命与有路中有效的生克和力量变化属于理气，可据此重评走势；由动象联想的行动原因、人物和情节属于象法，只作有条件的描述，不能独立翻判。'))
    text = (old / 'methods/adjudication.md').read_text('utf-8')
    text = replace(text, '课体气势（九宗门/毕法格局）作为先验参与缩放。', '课体的实际关系与气势进入共同理气；不把课名或吉凶将名作为独立先验缩放结果。')
    change('methods/adjudication.md', insert(text, '''## 本机裁决顺序

先综合四课三传、关键类神与彼此关系的理气，裁定大势、结果、过程及有据程度，再用象义表达具体表现。下列四象限、背景缩放及旧例保留方法来源身份；本机不以将名的吉凶乘算、标签数量或比喻独立改变理气结论、损益程度。凶将名称不能把有力生扶改成失败，吉将名称不能把无效救应改成成功。

最强反证必须回到同一全局关系中比较；若新核定位、生克或有效制救改变了关键环节，先更新理气再改判并重核应期。象义有分歧而理气未变时，只修正描述；理气未定时不以象法补成确定结果。'''))
    change('methods/shenjiang-use.md', insert((old / 'methods/shenjiang-use.md').read_text('utf-8'), '本机在基本取用与全局理气之后，按需用神将同用/互换细化对象和表现。互换不转移原节点的真实旺衰、坐标、乘将与生克力量，也不能借本家象义增加一份救应或翻转理气结论。确需修订关键定位时，回 `liqi` 重核与课传及其他关键类神的关系。'))
    change('methods/evidence.md', insert((old / 'methods/evidence.md').read_text('utf-8'), '复核先比全局理气：月令、四课三传的作用链、关键类神与课传及彼此的关系、阻断和有效制救，再比具体象义。相同神将象辞不能压过不同理气；经验若揭示遗漏的有效关系，回本盘重做理气裁决；仅象义不同则修正描述，不据原案结局翻判。'))
    text = (old / 'methods/report.md').read_text('utf-8')
    text = replace(text, '3. **主线与选法**：为何从日辰关系、类神或结构切入；该主线如何直接回答此问。', '3. **全局理气主线与选法**：先说明月令下主体、目标与主要阻碍的力量，四课三传如何贯通，分类关键类神怎样与课传及彼此作用，主要阻断、有效制救及走势结论；再说明取象怎样表达该主线。')
    text = replace(text, '- 主判和最强反证的双方理气是否齐全？是否把关系存在当作制得住，或把吉名当有救？', '- 主判和最强反证是否进入同一全局理气？关键类神自身、与四课三传及彼此的关系是否齐全？是否把关系存在当作制得住、吉名当有救，或用象义单独改变结果？')
    change('methods/report.md', insert(text, '报告先交代贯穿四课三传与关键类神的全局理气，再给依附于该走势的象法描述；不能仅列局部旺衰或象义后写“综合判断”。将理气依据、象法表达与现实已核事实分清。改判注明实际改变的定位或理气关系；单纯换象不能当成改判依据。'))
    change('references/shensha-use.md', insert((old / 'references/shensha-use.md').read_text('utf-8'), '本机以全局理气裁决、象法描述。神煞起法和32项核查保持；神煞名称、吉凶辞义只在理气走势内表达，不单独改变结果。德合、生旺、鬼墓空中确有实际关系和力量者归入理气；不能因为带有神煞名称而漏掉，也不能仅凭名称虚构作用。'))

    entry = (live / 'daliuren/SKILL.md').read_text('utf-8').replace(PARENT, RELEASE)
    entry = replace(entry, '以问题、分类取用及盘面作用为主干', '以理气统摄大势与结果，分类关键类神纳入四课三传，象法描述具体表现')
    entry = replace(entry, '明占类→定侧重→看显象。', '明占类与基本取用→全局理气→依气察象→理气复核裁决。')
    entry = replace(entry, '## 调用方式', '''## 研判层级
理气为骨、象法为肉。理气贯穿全局并裁决大势、走向、成败和有据程度，象法描述其具体形式，不凭吉凶名目或象义改变理气结论。神将的实际旺衰、生克、气地与制救属于理气；名称、形貌和事物辞义属于象法。分类关键类神须核自身状态、与四课三传的关系以及彼此关系；基本取用是确定理气对象，不是先据象定结果。新发现有效生克、救制或定位错误时更新全局理气后再改判，不为维护初判拒绝反证。总则及操作详见必读 `liqi`；本层级是用户指定的本机执行规范，未作独立预测验证。

## 调用方式''')
    entry = replace(entry, '| 3 定侧重 | 明确谁、何物、所问维度；说明干支四课、类神和年命的归属、位置及施受方向；有歧义留分支 | relations |', '| 3 理气总纲 | 核基本定位与课位，先贯通月令、四课三传及关键类神自身、与课传和彼此的关系，给气势、主要阻断及制救条件 | relations, liqi, void, structure |')
    entry = replace(entry, '| 4 看显象 | 先总览四课三传的气势和关键显象，再核主类神与反证的状态、生克和实际作用 | liqi, void |', '| 4 依气察象 | 在全局理气走势内描述具体人物、事物和表现；象义不得单独改变结果；定位发现错误时回核理气 | 复用上步；按条件补神将模块 |')
    entry = replace(entry, '| 7 结构反证 | 九宗门、课体、毕法结构与实际位置互核；课名不能代替成败判断 | structure |', '| 7 全局复核 | 结合动态与制救复核既有课传结构及类神关系；比较最强理气反证，不按课名或象义结案 | 复用 structure、liqi |')
    entry = replace(entry, '整体气势与局部制救互核，不预设某一层永久压倒其他层；', '全局理气统摄裁决，整体气势与关键类神、局部制救互核；象义只能描述，不与理气争夺结果裁决权；')
    for key in ['liqi-sources', 'risk']:
        lines = entry.splitlines()
        entry = '\n'.join(line[:-5] + '| 3 |' if line.startswith('| ' + key + ' |') and line.endswith('| 4 |') else line for line in lines) + '\n'
    for key in ['shenjiang-use', 'shen-symbols', 'jiang-symbols']:
        entry = '\n'.join(line[:-5] + '| 4 |' if line.startswith('| ' + key + ' |') and line.endswith('| 3 |') else line for line in entry.splitlines()) + '\n'
    change('entry.md', entry.replace('(<refs/daliuren-paipan.md>)', '(<../../../docs/本机六壬直接排盘.md>)'))
    route = load(old / 'reading-route.json')
    for stage in route['stages']:
        if stage['id'] == 3:
            stage.update(title='理气总纲', required=['relations', 'liqi', 'void', 'structure'],
                action='基本定位后先贯通月令、四课三传与关键类神自身、与课传及彼此关系，形成全局理气主线', note='理气统摄大势、结果和有据程度；不凭象辞预定结论。')
        elif stage['id'] == 4:
            stage.update(title='依气察象', required=[], action='在全局理气走势内细化人物事物与表现，按需读取神将辞义', note='象法只描述；若发现定位错误或有效理气反证，回核全局理气。')
        elif stage['id'] == 7:
            stage.update(title='全局复核', required=[], action='复用已读结构与理气，结合动态、制救及最强反证重核全课主线', note='不重复加载已读模块，不按课名或象辞翻判。')
        elif stage['id'] == 8:
            stage['action'] = '依据全局理气及有效制救裁定大势、结果与有据程度，再用象法表达具体表现'
    for key in ['liqi-sources', 'risk']:
        route['conditional'][key]['stage'] = 3
    for key in ['shenjiang-use', 'shen-symbols', 'jiang-symbols']:
        route['conditional'][key]['stage'] = 4
    change('reading-route.json', json.dumps(route, ensure_ascii=False, indent=2) + '\n')
    # A method response declares the real dependencies; callers reuse earlier complete reads.
    manifest = copy.deepcopy(manifest)
    for key in ['shenjiang-use', 'adjudication', 'report']:
        manifest['modules'][key]['requires'] = list(dict.fromkeys([*manifest['modules'][key].get('requires', []), 'liqi']))
    policy = load(new / manifest['shenshaPolicyFile'])
    policy['release'] = RELEASE
    write(new / manifest['shenshaPolicyFile'], policy)  # identity only; no table or algorithm change
    write(new / 'integration-map.json', dict(parent=PARENT,
        previousIntegration=load(old / 'integration-map.json'),
        change='用户指定理气统摄、象法表达；关键类神与四课三传及彼此关系一体分析；结构前移，保留十一环节与原方法',
        authoringSource=SOURCE.relative_to(ROOT).as_posix(), changedFiles=sorted(changes), independentValidation=0))
    for path in live.rglob('*.md'):
        body = path.read_text('utf-8').replace(PARENT, RELEASE)
        if path == live / 'daliuren/SKILL.md':
            body = entry
        write(path, body)
    write(live / 'daliuren/refs/shensha-use.md',
        '# 兼容引用\n\n请完整读取[当前方法文件](<../../../../../runtime/liuren/' + RELEASE +
        '/references/shensha-use.md>)。本文件仅作路径兼容，不是规则正文。\n')
    # Only advance the existing runtime allow-list and the local liuren prompt.
    cfg = (ROOT / 'opencode.json').read_text('utf-8').replace(PARENT, RELEASE)
    cfg = replace(cfg, '分类取用→定位→总览气势及关键类神状态→有路、生克、阴神与制救→盘面初判',
        '分类取用与基本定位→全局理气（四课三传、关键类神自身、与课传及彼此关系）→依气察象→动态制救与全局复核→理气裁决形成盘面初判')
    cfg = replace(cfg, '保留专业十一环节、适用方法全文及反证深度。',
        '理气为骨、象法为肉：理气裁决大势、走向、结果和有据程度，象法只描述具体表现，不凭象名翻判；新发现有效理气反证须重核。保留专业十一环节、适用方法全文及反证深度。')
    json.loads(cfg)
    write(ROOT / 'opencode.json', cfg)
    for name in ['README.md', '目录总索引.md']:
        path = ROOT / name
        write(path, path.read_text('utf-8').replace(PARENT, RELEASE))
    for name in ['docs/本机六壬完整研判流程.md', 'docs/本机六壬高效执行.md']:
        path = ROOT / name
        body = path.read_text('utf-8')
        body = insert(body, '2026-11-05 本机方法层级更新：理气为骨、象法为肉。明占类并完成基本取用后，在第3环节读取 relations、liqi、void、structure，贯通月令、四课三传、关键类神自身、与课传及彼此的关系；第4环节依气察象，第7环节复核全局。理气裁决大势、结果和有据程度，象法表达具体形式，不单独翻判；新定位或有效理气反证须回核。此为用户指定的本机规范，非效果验证。')
        body = body.replace('再定位、总览气势、辨状态生克', '再作基本定位、全局理气、依气察象与状态生克核查')
        body = body.replace('再按入口逐步读relations、liqi/void、综合核查、movement、structure、adjudication等', '再按入口于理气总纲读relations、liqi/void、structure，随后依气察象、综合核查、movement、全局复核、adjudication等')
        write(path, body)
    path = ROOT / 'AGENTS.md'
    body = path.read_text('utf-8')
    body = replace(body, '按专业十一环节实际读取、分别检索案例与经验并直接交付完整判断原文。',
        '按专业十一环节实际读取、分别检索案例与经验并直接交付完整判断原文。当前本机以理气为骨、象法为肉：理气贯穿全局并裁决大势与结果，象法描述具体表现，不凭象义改变理气结论；分类关键类神须核自身状态、与四课三传及彼此的关系。新发现定位错误或有效理气反证时回核全局。')
    write(path, body)
    test = ROOT / 'tools/tests/test_liuren_class_mapping.py'
    write(test, replace(test.read_text('utf-8'), "self.assertEqual(next(s['stage'] for s in selected if s['id']==key),3)", "self.assertEqual(next(s['stage'] for s in selected if s['id']==key),4)"))
    manifest.update(release=RELEASE, parentRelease=PARENT, status='active-local',
        required=[key for s in route['stages'] for key in s['required']],
        conditional={key: row['trigger'] for key, row in route['conditional'].items()})
    implementation = dict(pointer['workflowImplementation'])
    implementation[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__).read_bytes())
    contract = load(new / 'loader-contract.json')
    contract.update(sourceHashes=implementation, methodHierarchy='liqi-led-symbols-describe', authoringSource=SOURCE.relative_to(ROOT).as_posix())
    write(new / 'loader-contract.json', contract)
    manifest['files'] = {k:v for k,v in inventory(new).items() if k != 'manifest.json'}
    manifest['version'] = sha(json.dumps(manifest['files'], sort_keys=True).encode())
    write(new / 'manifest.json', manifest)
    pointer.update(release=RELEASE, previousRelease=PARENT, runtime=new.relative_to(ROOT).as_posix(),
        methodVersion=manifest['version'], backup=(OUT/'before').relative_to(ROOT).as_posix(),
        files={'liuren/'+k:v for k,v in inventory(live).items()}, workflowImplementation=implementation,
        methodHierarchy='liqi-led-symbols-describe', authoringSource=SOURCE.relative_to(ROOT).as_posix())
    # Check generated routes, references and preservation before the atomic pointer switch.
    for path in [*live.rglob('*.md'), *[new/k for k in changes if k.endswith('.md')]]:
        body = re.sub(r'```.*?```', '', path.read_text('utf-8'), flags=re.S)
        for target in re.findall(r'\[[^\]\n]+\]\((<[^>]+>|[^\s)]+)\)', body):
            target = target.strip('<>').split('#')[0]
            if target and not target.startswith(('https:', 'http:')) and not (path.parent/target).resolve().is_file():
                raise ValueError('invalid reference: '+str(path)+' -> '+target)
    if inventory(old) != frozen_before:
        raise ValueError('parent runtime changed')
    temp = ptr.with_suffix('.new.json')
    write(temp, pointer)
    temp.replace(ptr)
    after = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in editable}
    write(OUT / 'activation.json', dict(release=RELEASE, parent=PARENT, methodVersion=manifest['version'],
        localOnly=True, websiteChanged=False, originalRuntimeUnchanged=True, before=before, after=after,
        changedMethods=sorted(changes), predictiveAccuracy='unverified', modelCalls=0))
    write(OUT / '回退说明.md', f'''# 本机理气主导调整与回退

当前版本：{RELEASE}；前版：{PARENT}。维护源：`{SOURCE.relative_to(ROOT).as_posix()}`。

回退前先核对 activation.json 的 after 哈希，确认相关文件没有后续修改；如有变化先保留和逐项合并，不覆盖新改动。核对后按 before-manifest.json 的精确清单从 before/ 恢复原文件字节，最后恢复 .opencode/liuren-active.json。原运行包未改；新运行包和源修订可保留供对照，不需删除。重启 OpenCode 或在新会话重新加载入口。

本次不改原书、原案、排盘算法、神煞计算表或网站；政策文件仅推进版本身份。工程验证不代表预测有效。尚未验证运行中 OpenCode 热加载或真实模型执行效果。
''')
    print(json.dumps(dict(release=RELEASE, methods=len(changes), files=len(manifest['files']), version=manifest['version']), ensure_ascii=False))


def resume_staged():
    """Finish the already written candidate after repairing an inherited compatibility link."""
    ptr = ROOT / '.opencode/liuren-active.json'
    pointer = load(ptr)
    before = load(OUT / 'before-manifest.json')
    new = ROOT / 'runtime/liuren' / RELEASE
    old = ROOT / 'runtime/liuren' / PARENT
    if pointer['release'] != PARENT or (OUT / 'activation.json').exists():
        raise ValueError('not an interrupted pre-activation build')
    for rel, expected in before.items():
        if sha((OUT / 'before' / rel).read_bytes()) != expected:
            raise ValueError('backup changed: ' + rel)
    old_manifest = load(old / 'manifest.json')
    if any(sha((old/k).read_bytes()) != v for k,v in old_manifest['files'].items()):
        raise ValueError('parent runtime changed')
    manifest = load(new / 'manifest.json')
    if any(sha((new/k).read_bytes()) != v for k,v in manifest['files'].items()):
        raise ValueError('staged package changed')
    live = ROOT / '.opencode/skills/liuren'
    write(live / 'daliuren/refs/shensha-use.md',
        '# 兼容引用\n\n请完整读取[当前方法文件](<../../../../../runtime/liuren/' + RELEASE +
        '/references/shensha-use.md>)。本文件仅作路径兼容，不是规则正文。\n')
    implementation = dict(pointer['workflowImplementation'])
    implementation[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__).read_bytes())
    contract = load(new / 'loader-contract.json')
    contract['sourceHashes'] = implementation
    write(new / 'loader-contract.json', contract)
    manifest['files'] = {k:v for k,v in inventory(new).items() if k != 'manifest.json'}
    manifest['version'] = sha(json.dumps(manifest['files'], sort_keys=True).encode())
    write(new / 'manifest.json', manifest)
    for path in [*live.rglob('*.md'), *[new/k for k in load(new/'integration-map.json')['changedFiles'] if k.endswith('.md')]]:
        body = re.sub(r'```.*?```', '', path.read_text('utf-8'), flags=re.S)
        for target in re.findall(r'\[[^\]\n]+\]\((<[^>]+>|[^\s)]+)\)', body):
            target = target.strip('<>').split('#')[0]
            if target and not target.startswith(('https:', 'http:')) and not (path.parent/target).resolve().is_file():
                raise ValueError('invalid reference: '+str(path)+' -> '+target)
    pointer.update(release=RELEASE, previousRelease=PARENT, runtime=new.relative_to(ROOT).as_posix(),
        methodVersion=manifest['version'], backup=(OUT/'before').relative_to(ROOT).as_posix(),
        files={'liuren/'+k:v for k,v in inventory(live).items()}, workflowImplementation=implementation,
        methodHierarchy='liqi-led-symbols-describe', authoringSource=SOURCE.relative_to(ROOT).as_posix())
    temp = ptr.with_suffix('.new.json')
    write(temp, pointer)
    temp.replace(ptr)
    write(OUT/'activation.json', dict(release=RELEASE, parent=PARENT, methodVersion=manifest['version'],
        localOnly=True, websiteChanged=False, originalRuntimeUnchanged=True, before=before,
        after={rel:sha((ROOT/rel).read_bytes()) for rel in before},
        changedMethods=load(new/'integration-map.json')['changedFiles'],
        compatibilityRepair='shensha-use: route to current runtime instead of broken sibling links',
        predictiveAccuracy='unverified', modelCalls=0))
    write(OUT/'回退说明.md', '''# 本机理气主导调整与回退

当前版本：20261105-liqi-led-01；前版：20261104-chart-first-02。

回退前核对 activation.json 的 after 哈希；有后续修改先保留并逐项合并，不直接覆盖。按 before-manifest.json 清单从 before/ 恢复原文件字节，最后恢复 .opencode/liuren-active.json。原运行包未改，新包和版本化维护源保留供对照。重启 OpenCode 或在新会话重新加载入口。

本次不改原书、原案、排盘算法、神煞计算表或网站。工程验证不代表预测有效，尚未验证运行中 OpenCode 热加载或真实模型执行效果。
''')
    print(json.dumps(dict(release=RELEASE, files=len(manifest['files']), version=manifest['version']), ensure_ascii=False))


if __name__ == '__main__':
    resume_staged() if sys.argv[1:] == ['--resume'] else main()
