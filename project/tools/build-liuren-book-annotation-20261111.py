"""Build a source-preserving, user-editable first batch of book annotation copies.

This is a maintenance artifact builder, not a rule importer or a judgment tool.
It refuses to overwrite an existing annotation folder, including user notes.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/liuren-book-annotation-20261111'
ACTIVE_PATH = ROOT / '.opencode/liuren-active.json'
ACTIVE = json.loads(ACTIVE_PATH.read_text(encoding='utf-8-sig'))
RUNTIME = ROOT / ACTIVE['runtime']
BIFA = '书籍库/北海闲人/毕法赋全解-正式整理本.md'
LIFA = '书籍库/北海闲人/理法简易.txt'


def item(id, title, book, start, end, kind, gap, proposed, boundary, cards, refs):
    return dict(id=id, title=title, source_path=book, line_start=start,
                line_end=end, finding_type=kind, observed_gap=gap,
                proposed_action=proposed, boundary=boundary,
                existing_rule_ids=cards, active_reference_queries=refs,
                user_annotation='', decision='awaiting_user_annotation',
                applied_to_active=False)


FINDINGS = [
    item('B01', '末助初：三种六亲路径与占类分支', BIFA, 2402, 2462,
         '摘要失真或过度压缩',
         '活动速查写成“吉助 / 凶助 / 平助三等”。本地整理本把三等具体解释为末子助初财、末财助初鬼、末鬼助初父，并另论年命制末、近远事、空亡、夹克及不同占类。已有较详细知识卡，不能说从未提取。',
         '可将三种实际路径及截断助势的条件补入结构/理气参考，并替换速查的三类标签；在末生初且关系影响本问时触发。',
         '原段婚姻、疾病等强断保持来源身份，不能无条件接入；不凭末传角色编造现实人物。',
         ['LR26-BOOK-BIFA-053'], [('references/bifa.md', 'B6. 末助初')]),
    item('B02', '费有余：得者空、费者实及生扶链中断', BIFA, 3012, 3076,
         '有名目但缺具体条件',
         '活动速查只有“费多而得少，入不敷出”。原段不限现金收支，明确财官印等所“得”与脱鬼玄等所“费”的空实对待，并展示递生链部分落空后只余伤神。已有知识卡。',
         '可补得/费各自对象、空实与通路检查，并分别解释收入、助力、权位或耗损，保留原案中的余神作用。',
         '不把空实比较换成净额公式；强语仍按U01/U08；不同占类的例外不能省略。',
         ['LR26-BOOK-BIFA-072'], [('references/bifa.md', 'H6. 费有余')]),
    item('B03', '鬼临三四：明确课位、全见及时间层', BIFA, 3465, 3496,
         '原文已可补核而执行摘要仍留待核',
         '活动速查H5仍称“三四”所指课位未在本批回源核清。本地整理本3467明确为第三、第四课；还论空鬼当前有声无实与以后条件改变的区别。这里是可补回源的位置，不能直接升级为预测定律。',
         '可按此来源补明支二课均为日鬼的构成；相应更新“未核清”的说明，分别保留当前空实和以后转患条件。',
         '本段天鬼等起法若不在采用表内，不因此自动新增神煞；病死、讼灾强断不作自动开关。',
         ['LR26-BOOK-BIFA-084'], [('references/bifa.md', 'H5. 鬼临三四')]),
    item('B04', '关隔锁与斩关、毁隔、破锁', BIFA, 3498, 3510,
         '已提取但未见专项执行说明',
         '已有知识卡保存门位关隔锁及开破。活动正文检索未见“关隔锁/毁隔/破锁”的完整构成说明；现行S33是季关神，不能将两种机制混为一项。此处“未见”是检索和相关段对读结果，不是全库无同义方法的证明。',
         '可作为门位阻隔与解除的独立候选参考，保留地盘门户、加临构成和所用类神，说明何时适用于出行、访人等问题。',
         '这是本地整理本引述的跨方法用法，不自动等同S33、入墓或斩关课；原文病孕吉语也不直接作现实结果。',
         ['LR26-BOOK-BIFA-085'], [('references/judgment-core.md', '## 36版新增采用')]),
    item('B05', '前后逼迫：比较进、退、守及两种受克位置', BIFA, 3571, 3597,
         '已提取但执行摘要缺展开',
         '活动速查仅写“三传前后逼迫，进退两难”。原段实际比较前进、后退和原地静守，还区分克处回归又受克、全伤坐克和地盘/天将夹克。知识卡已有这些区别。',
         '可补三种行动的比较方法，明确原位置、路线与受克层次；只在本问涉及趋避、行动且有相应结构时使用。',
         '本段混有出生三限讨论，按当前占事边界排除；“有动类仍以动论”要保留，不保证建议行动已能成功。',
         ['LR26-BOOK-BIFA-088'], [('references/bifa.md', 'G7. 前后逼迫')]),
    item('B06', '绝：断绝与解决，继续与了结的不同目标', BIFA, 3951, 4002,
         '有名目但关键分支压缩',
         '活动速查只写“至绝处须决断”，婚恋等处虽有部分绝义，原段更明确区分各自绝、互绝、绝财了结、绝神加生使旧事再起及递互交换，原卡也保留分项。',
         '可补“此事希望继续还是希望了结”的判断分支，以及各自/互相的对象区别；与已有timing的绝处逢生延迟例合并说明，避免重复。',
         '原段称本法依五行绝，与通用U04日干十二气不完全同口径；若采用专项表须另明身份，不能静默覆盖U04。原病死等强断不直接接入。',
         ['LR26-BOOK-BIFA-095'], [('references/bifa.md', 'A6. 干支值绝'), ('methods/timing.md', '绝处逢生反延迟')]),
    item('B07', '传墓入墓：构成与不同占类的反向取义', BIFA, 4032, 4068,
         '已有总原则但专项条件不足',
         '活动速查保留吉入墓为憎、凶入墓为爱的原则，缺少本段初入中墓的构成及行人、人归信至、铸印等例外；原段自身也提醒总原则不能覆盖具体占类，知识卡已提取。',
         '可补传墓构成，并把行人迟来/归来等说法连同对象和上下文列作需裁条件；与现行墓、马、占类规则交叉核对。',
         '不得据原文一个鬼入墓就断无害；原段“财发用必得”等强语及日干长生口径仍服从现行U规则，真实不兼容处先列明。',
         ['LR26-BOOK-BIFA-097'], [('references/bifa.md', 'B9. 传墓入墓')]),
    item('B08', '不行传：实者为断，成否与持续分开', BIFA, 4072, 4092,
         '摘要误导且已有详细提取',
         '活动速查写“三传不动，考初传定应期”。本段先讲初实中末空、以实者论吉凶，并说明独足、杜传不同；不只是定日期，杜传也不必空。已有知识卡保存这些条件。',
         '可替换速查摘要，补查哪些类神实、过程受阻还是迅速结束、初成不久还是似成未成。完整章后例继续备查。',
         '保留U08空亡综合及占类差别；不能把中传空连带改写成末传旬空，也不修改可信程序起传。',
         ['LR26-BOOK-BIFA-098'], [('references/bifa.md', 'B10. 不行传')]),
    item('B09', '六爻现卦：六亲成局与救制，非另起六爻卦', BIFA, 4695, 4755,
         '活动参考之间存在释义不一致',
         '速查B11写“课传演成六爻卦象”，本地整理本4699解释为三传合成六亲局；活动expert-adjudication-excerpts也已有“合局克类神”的解释。应纠正速查的误导，而非再加一套六爻系统。',
         '可统一成本来源的六亲成局、受克对象、干支年命上的泄局/制局救应，并保留传A化B的明确位置定义。',
         '不因成局就自创三合数值权重；原段医学病名及必死强断保留来源身份；懒去取财等作者称未验证的分支须标明。',
         ['LR26-BOOK-BIFA-114'], [('references/bifa.md', 'B11. 六爻现卦'), ('references/expert-adjudication-excerpts.md', '三传合局力大')]),
    item('B10', '常占不应：身份、权限、目标与同课异用', BIFA, 4842, 4870,
         '摘要失去解释条件',
         '速查I3写“常事问而逢吉象为不应”，容易被读成常事见吉就是不应。本段重点是因人事时地解释、仕庶与目标适配，也明列官民同吉同凶的例外。已有知识卡。',
         '可替换为本题角色、实际权限、所求目标及进退需要的适配检查；把例外一起保留。当前core已有占类分工，补的是具体解释。',
         '原文传统等级与人格评价只作来源身份；不把平民遇吉课必灾等古代社会推论直接移植现代。',
         ['LR26-BOOK-BIFA-118'], [('references/bifa.md', 'I3. 常问')]),
    item('B11', '已灾凶逃：作者反对“应过就安全”', BIFA, 4874, 4897,
         '摘要未保留作者否定与特例',
         '活动速查I3只留下“已受灾而见凶逃返无疑”，没有本段4876对“已经发了就没事”的明确反驳。已有知识卡保存否定和脱难形态。现行core虽有阶段/后患总则，速查仍需对齐。',
         '可补既有灾情不保证后面安全；原段入狱后脱难、结绝和以凶制凶均按具体对象、冲制、救应及结果程度使用。',
         '脱禁后谪戍不等于无罪复职；后载课例不是本案现实反馈，不能倒推通则效果。',
         ['LR26-BOOK-BIFA-119'], [('references/bifa.md', 'I3. 常问')]),
    item('L01', '三传进退：与阴阳方向、将顺逆交叉', LIFA, 3093, 3107,
         '参考有部分例子但缺完整定义且需校勘',
         '活动高手摘录已有传入阳方/阴方例子，神煞来源有传进利进传退利退；未见本段进茹、间传、顺逆合与阴阳方向交叉的完整解释，不能说完全未获取。',
         '可先核原书异文，再补结构定义及“传进也可能转入阴方、传退也可能转入阳方”的条件比较，按本问求进/求退解释。',
         '本地3101阳方清单漏列申，需校勘而不能自行填字；3099顺逆合例也应连同原表复核。不自动合化、不数票、不转成成败开关。',
         [], [('references/expert-adjudication-excerpts.md', '传入阳方')]),
    item('L02', '传入传出：内外有两种参照，初中也可成传', LIFA, 3109, 3121,
         '专项有概述但细分参照未充分展开',
         '出行专项已概述内外、进退、空实；高手摘录也有内传外例。原段进一步区分干二课/支二课的内外与四课整体为内，且说明有时初中也构成传入传出。未见活动摘要完整列出这两层。',
         '可补两种内外参照及参与传位，先说明采用哪一种，再判趋内趋外、来归/出发和实虚所限环节，避免固定只看初末。',
         '不把干外支内推广覆盖全部婚恋、胎产等角色轴；传回课上不保证事情已成，仍核类神与有效作用。',
         [], [('domains/travel.md', '北海区分出行'), ('references/bifa.md', 'A2. 彼求我事')]),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lines(path):
    return path.read_text(encoding='utf-8-sig').splitlines()


def link(path, line=None):
    return (ROOT / path).as_posix() + (f':{line}' if line else '')


def main():
    if OUT.exists():
        raise SystemExit('拒绝覆盖已有批注目录；其中可能已有用户批注。请复用该目录或另建明确的新批次。')
    sys.path.insert(0, str(ROOT / 'tools'))
    spec = importlib.util.spec_from_file_location('annotation_workbench', ROOT / 'tools/liuren_knowledge_workbench.py')
    wb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wb)
    status = wb.build(ROOT)
    vmap = {r['id']: r for r in status['validation']['records']}
    sources = {p: dict(sha256=sha(ROOT / p), lines=lines(ROOT / p)) for p in (BIFA, LIFA)}
    protected = {p: sha(ROOT / p) for p in (BIFA, LIFA, '.opencode/liuren-active.json')}
    runtime_hashes = {p.relative_to(ROOT).as_posix(): sha(p) for p in RUNTIME.rglob('*') if p.is_file()}
    for f in FINDINGS:
        src = sources[f['source_path']]
        f['source_sha256'] = src['sha256']
        f['source_identity'] = '本地已整理/转录文本；非古刻影印，作者讲解、引文与整理补释须分别看待'
        f['line_numbering'] = 'UTF-8解码后Python splitlines一基闭区间；不是纸书页码'
        f['quote'] = '\n'.join(src['lines'][f['line_start'] - 1:f['line_end']])
        f['active_refs'] = []
        for rel, needle in f.pop('active_reference_queries'):
            hits = [(i, s) for i, s in enumerate(lines(RUNTIME / rel), 1) if needle in s]
            if not hits:
                raise ValueError(f'活动引用未定位：{f["id"]} {rel} {needle}')
            for i, s in hits:
                f['active_refs'].append(dict(path=(RUNTIME / rel).relative_to(ROOT).as_posix(), line=i, quote=s))
        f['existing_card_validation'] = [dict(id=id, state=vmap[id]['mechanical_state'], errors=vmap[id]['errors']) for id in f['existing_rule_ids']]
        f['existing_extraction_scope'] = '找到已提取知识卡' if f['existing_rule_ids'] else '本批按标题与关键短语未定位到对应独立卡；未穷尽同义卡，不宣称从未提取'

    OUT.mkdir(parents=True)
    output_books = {BIFA: '毕法赋全解-书中批注本.md', LIFA: '理法简易-书中批注本.md'}
    navigation = []
    for book, filename in output_books.items():
        chosen = [f for f in FINDINGS if f['source_path'] == book]
        out_lines = [f'# {Path(book).stem}｜书中批注阅读副本', '',
                     '本书全文保留为阅读底本，调查批注插在对应原段前。只有下列段落完成本批对读，其余正文不代表已经审完。', '',
                     f'来源：[原书文本]({link(book)})；原字节SHA256：`{sources[book]["sha256"]}`。', '',
                     '你可直接在任一原段后写【我的批注：……】，也可填写候选块中的批注。写“加入这个条件”“已有，只改摘要”“不要这一段”或自己的理解都可以。空白表示未决定。', '',
                     '候选块为本次调查解释；原书强断和评价保留原字，不代表当前已采用。原书来源与活动规则均未修改。', '',
                     '## 本批标记', '']
        for f in chosen:
            out_lines.append(f'- {f["id"]}：{f["title"]}（原源 {f["line_start"]}—{f["line_end"]}）')
        out_lines += ['', '<!-- ORIGINAL-BOOK-START -->', '']
        by_start = {f['line_start']: f for f in chosen}
        markers = []
        for i, original in enumerate(sources[book]['lines'], 1):
            if i in by_start:
                f = by_start[i]
                start = len(out_lines) + 1
                out_lines += [f'<!-- INVESTIGATION-NOTE-START {f["id"]} -->', '',
                              f'> **调查批注 {f["id"]}｜{f["title"]}**', '>',
                              f'> 原源行 {f["line_start"]}—{f["line_end"]}；类型：{f["finding_type"]}。', '>',
                              f'> **查到的情况：**{f["observed_gap"]}', '>',
                              f'> **可考虑怎样处理：**{f["proposed_action"]}', '>',
                              f'> **要保留的条件：**{f["boundary"]}', '>']
                if f['existing_rule_ids']:
                    states = '；'.join(f'{v["id"]}（{v["state"]}）' for v in f['existing_card_validation'])
                    out_lines += [f'> 已有提取：{states}。知识卡存在不等于普通占断已加载。', '>']
                for a in f['active_refs']:
                    out_lines += [f'> 现行位置：[{Path(a["path"]).name} 原行{a["line"]}]({link(a["path"], a["line"])})', '>']
                out_lines += [f'> **【我的批注 {f["id"]}：】**', '',
                              f'<!-- INVESTIGATION-NOTE-END {f["id"]} -->', '']
                markers.append(dict(id=f['id'], copy_line=start, source_start=f['line_start'], source_end=f['line_end']))
                f['annotation_copy'] = (OUT / filename).relative_to(ROOT).as_posix()
                f['annotation_line'] = start
                navigation.append(f'- [{f["id"]} {f["title"]}]({(OUT / filename).as_posix()}:{start})')
            out_lines.append(original)
        out_lines += ['', '<!-- ORIGINAL-BOOK-END -->', '']
        text = '\n'.join(out_lines)
        (OUT / filename).write_text(text, encoding='utf-8', newline='\n')
        # Remove only injected blocks and compare all original decoded lines.
        extracted, in_book, in_note = [], False, False
        for s in text.splitlines():
            if s == '<!-- ORIGINAL-BOOK-START -->':
                in_book = True
                continue
            if s == '<!-- ORIGINAL-BOOK-END -->':
                break
            if not in_book:
                continue
            if s.startswith('<!-- INVESTIGATION-NOTE-START '):
                in_note = True
                # The builder adds one spacer after the previous original line.
                continue
            if s.startswith('<!-- INVESTIGATION-NOTE-END '):
                in_note = False
                continue
            if not in_note:
                extracted.append(s)
        # The exact original stream is separately checked by an ordered index map,
        # avoiding ambiguity between source blank lines and inserted spacers.
        stream = []
        cursor = text.index('<!-- ORIGINAL-BOOK-START -->') + len('<!-- ORIGINAL-BOOK-START -->\n\n')
        for i, original in enumerate(sources[book]['lines'], 1):
            if i in by_start:
                ending = f'<!-- INVESTIGATION-NOTE-END {by_start[i]["id"]} -->\n\n'
                cursor = text.index(ending, cursor) + len(ending)
            expected = original + '\n'
            if text[cursor:cursor + len(expected)] != expected:
                raise AssertionError(f'原书流校验失败：{book}:{i}')
            stream.append(original)
            cursor += len(expected)
        assert stream == sources[book]['lines']

    inventory = []
    for parent in ('书籍库', 'books'):
        for p in sorted((ROOT / parent).rglob('*')):
            if p.is_file() and p.suffix.lower() in ('.md', '.txt'):
                inventory.append(dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                                      sha256=sha(p), identity='来源目录文本（包含索引/修订资料，不按文件数宣称书籍数）' if parent == '书籍库' else '整理/索引/衍生材料，非默认原书身份',
                                      has_selected_spans_reviewed_in_this_batch=p.relative_to(ROOT).as_posix() in sources,
                                      reviewed_spans=[dict(line_start=f['line_start'], line_end=f['line_end']) for f in FINDINGS if f['source_path'] == p.relative_to(ROOT).as_posix()],
                                      full_source_reviewed_in_this_batch=False))
    write = lambda name, data: (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report = dict(schema='liuren-book-annotation-investigation-v1', date='2026-11-11',
                  active_release=ACTIVE['release'], active_method_version=ACTIVE.get('methodVersion'),
                  scope='首批两书的十三组段落与活动方法对读；全库文件清点不等于全书语义调查',
                  source_books=[dict(path=p, sha256=sources[p]['sha256'], decoded_line_count=len(sources[p]['lines'])) for p in sources],
                  checked_control_examples=[
                      dict(topic='直接临生合与外来扶助', active='judgment-core U03，已有，不重复加入'),
                      dict(topic='四课/三传不固定为现状/发展', source_path=LIFA, line_start=6685, line_end=6701, active='methods/liqi.md及judgment-core已有类神/课传分工，不列新缺口')],
                  findings=FINDINGS,
                  knowledge_status=dict(coverage=status['coverage'], validation_summary={k: status['validation'][k] for k in ('record_count','passed','blocked','valid','complete')}),
                  next_scope=['理法简易：余下判断总纲、类象分析及神将气势连续段，逐段排除已经覆盖内容',
                              '毕法赋：本批之外各法的正格/类格/反例，与活动速查逐条比较',
                              '壬归：提纲、求财、谋望、婚姻、出行的完整条件，区分本地选择与原法',
                              '六壬金针、特训讲义、神将释、64课经：按来源优先级核新增方法、异文和现行取法兼容性'],
                  not_done=['未逐书逐段调查全库；未确定本地缺少哪些外部书籍',
                            '未将候选加入活动规则；未修改冻结runtime、原书或网站',
                            '未自动修复旧知识卡引用；未进行独立预测验证'])
    write('调查记录.json', report)
    write('本地文本清点.json', inventory)
    readme = [
        '# 直接在书里批注', '',
        '你负责指出哪些原文值得采用、怎样理解；我负责调查遗漏、核对现行方法、整理条件并落实后续修改。你不用先列全套判断逻辑，也不需要懂内部模块名。', '',
        '## 怎么开始', '',
        f'先打开[毕法赋全解批注本]({(OUT / output_books[BIFA]).as_posix()})或[理法简易批注本]({(OUT / output_books[LIFA]).as_posix()})。两份都是全文阅读副本，调查说明插在相关原段旁。', '',
        '在【我的批注】后直接写你的意思。例如：', '',
        '> 加入。这里先看财是否真能为我用，不要看到生就直接论得财。', '>',
        '> 这一整段不要照搬，只保留前面的条件。', '>',
        '> 我想用这个方法，但只用于出行；下面这个例子不加入。', '',
        '也可在其他任何原段后新增【我的批注：……】。无需填写固定表格；不用每条都选，空白保留未决定。改好后告诉我“读取批注本继续”，并指明你编辑的文件。', '',
        '如果你习惯在纸书、PDF或Word里标注，也可按那种方式阅读；后续提供书名、页码/原句及批注意思即可。纸书页码不与这里文本行号混称。', '',
        '## 首批调查发现', '',
        '十三组候选中，十一组已能定位到旧知识卡；这批主要发现“已提取但活动摘要未充分承接、摘要有偏差、条件没有展开”。另两组在活动参考中有部分材料，尚未完整定位到对应独立卡，不能称从未获取。', '',
        '尤其值得先看：B01末助初、B08不行传、B09六爻现卦、B11已灾。它们关系到怎样理解方法本身。B04关隔锁是与S33季关神不同的门位机制候选。L01含明确校勘缺口，暂不能按缺字清单直接接入。', '',
        *navigation, '',
        '## 你批注后我怎样处理', '',
        '先读原段上下文和你的批注，检查同义方法是否已经存在，再整理对象、位置、触发条件、判断作用、反证与例外。已覆盖的补引用或改摘要；缺的补执行正文和触发；真正不兼容的原句并列说明。只有含义会改变采用结果且批注未能消除歧义时，才请你判断那一个具体问题。', '',
        '一般方法可进入按需参考；需要每次共同执行的总原则才考虑进共用核心。不会把所有选段都塞进必读，也不会把书里所有强断自动变成成败开关。用户明确选定并可兼容的内容可继续落实，不重复索取已给的授权；仍保留来源和版本差异。', '',
        '## 这次调查的边界', '',
        '当前对照基线为40版。本批实际对读两书指定段落，并核活动方法和已有卡；没有宣称两书全文或全库已审完。本地清点覆盖书籍库与books的Markdown/TXT文件，含索引和衍生材料，数量不能当成独立书籍数。尚未调查本地未取得的外部文献。', '',
        '“已有卡”也不等于当前可用：例如B01、B08关联卡本次机械校验被未注册案例ID阻断。普通占断本来就不检索两库，不能假设那里的详细卡已自动进入裁决。具体状态见调查记录。', '',
        '原书与活动规则未改；副本只是统一换行为LF并插入调查块，原书文字和顺序已逐行校验。调查建议是候选，不是已经生效的方法或预测效果证明。', '',
        f'机器记录：[调查记录]({(OUT / "调查记录.json").as_posix()})；[本地文本清点]({(OUT / "本地文本清点.json").as_posix()})。', '',
        '后续调查顺序已写进调查记录：两书剩余部分→壬归→金针、特训讲义、神将释、64课经。每批都保留实际已读范围；生成副本或关键词命中不会登记整书已读。', '',
    ]
    (OUT / '先看这里-书中批注说明.md').write_text('\n'.join(readme), encoding='utf-8')
    for p, before in {**protected, **runtime_hashes}.items():
        assert sha(ROOT / p) == before, f'保护文件变化：{p}'
    verification = dict(original_sources_unchanged=True, active_pointer_unchanged=True,
                        active_runtime_files_unchanged=len(runtime_hashes),
                        source_line_streams_preserved=True, annotation_count=len(FINDINGS),
                        no_automatic_adoption=True,
                        output_files=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in OUT.iterdir() if p.is_file()])
    write('文件校验.json', verification)
    print(json.dumps(dict(output=OUT.as_posix(), findings=len(FINDINGS), book_copies=2,
                          existing_card_findings=sum(bool(f['existing_rule_ids']) for f in FINDINGS),
                          inventory_text_files=len(inventory), verified=True), ensure_ascii=False))


if __name__ == '__main__':
    main()
