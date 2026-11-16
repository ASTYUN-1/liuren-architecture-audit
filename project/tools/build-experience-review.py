"""Build and check the additive, line-backed experience navigation.

The input annotations are reviewed in bounded batches by three organizers.
This script only indexes them; it never assigns empirical validity.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/经验库梳理/20261019'
GROUPS = ('history', 'books', 'new')
GROUP_NAMES = {'history':'历史案例与复盘', 'books':'书籍与框架', 'new':'新增 51 案', 'support':'支持文件'}
KINDS = {'技巧', '条件规则', '案例观察', '反例边界', '方法框架', '设计假设', '说明记录', '历史审查标记'}
VERIFICATIONS = {'优秀作业参照待验', '未验证从疑', '单案复盘待泛化', '来源称验未独立核验',
                 '书籍提取未核原典', '历史疑点保留', '设计未验证', '不适用'}
RELATIONS = {'同源复写', '高度重复候选', '相似方法', '条件差异', '冲突待核'}
REQUIRED = {'id', 'source', 'line_start', 'line_end', 'title', 'summary', 'categories',
            'method_tags', 'kind', 'verification', 'evidence_basis', 'source_claim', 'caveat', 'case_refs'}
ALIASES = {'交易占':'财运占', '考试占':'学业占', '疾病占':'健康占', '灾厄占':'健康占',
           '行人占':'出行占', '宅门占':'家宅占', '胎产占':'感情占', '推命占':'推命',
           '射覆占':'射覆', '来意占':'来意', '杂事占':'杂事', '比赛占':'事业占'}
FAMILIES = {
    '取用与类神':r'类神|取用|用神|财官|六亲|人宅',
    '吉凶取舍与权重':r'权重|取舍|主次|优先|大势|结局|气势|裁决|吉凶|救解|救应',
    '空亡墓绝与旺衰':r'空亡|旬空|出空|天空|墓|绝|旺衰|旺相|囚死|月令|十二长生',
    '三传与课体':r'三传|反吟|伏吟|课体|涉害|斩关|元胎|间传|进茹|退茹|格局',
    '应期与迟速':r'应期|迟速|冲合|填实|出旬|月建|应月|应日|时辰',
    '数值与精度':r'取数|数断|数法|数值|比分|分数|金额|折半|数字|数量|精度|名次',
    '取象与射覆':r'取象|类象|物象|射覆|颜色|形状|方位|容器|叠象|定位',
    '天将与神煞':r'天将|神将|神煞|贵人|朱雀|玄武|白虎|青龙|腾蛇|螣蛇|勾陈|天后|太常|驿马|丁马|天德|月德',
    '年命与推命':r'年命|本命|行年|推命|终身|宫位|三限|运限|岁运|六亲',
    '来源与复盘纪律':r'来源|反证|反馈|反推|复盘|引用|核验|校验|边界|过拟合|拟合|迁移|验证',
}

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def write_md(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines).rstrip()+'\n', encoding='utf-8')

def source_page(source):
    return 'sources/'+Path(source).stem+'-'+hashlib.sha1(source.encode()).hexdigest()[:8]+'.md'

def link(path, label, line=None):
    target = (ROOT/path).as_posix()
    if line:
        target += ':'+str(line)
    return f'[{label}](<{target}>)'

def entry_link(e):
    target = (OUT/source_page(e['source'])).as_posix()+'#'+e['id'].lower()
    label=(e['id']+' '+e['title']).replace('\\','\\\\').replace('[','\\[').replace(']','\\]').replace('|','｜').replace('\n',' ')
    return f'[{label}](<{target}>)'

def esc(s):
    return str(s).replace('|','｜').replace('\n',' ')

def table(entries, detail=False):
    lines=['| 条目 | 占类 | 类型 | 验证定位 |'+(' 适用范围与缺口 |' if detail else ''),
           '|---|---|---|---|'+('---|' if detail else '')]
    for e in entries:
        row=f'| {entry_link(e)} | {esc("、".join(e["categories"]))} | {e["kind"]} | {e["verification"]} |'
        if detail:
            row+=' '+esc(e['caveat'])+' |'
        lines.append(row)
    return lines

def clean_ref(ref):
    return ref.strip().replace('\\','/').strip('`。，；; ')

def resolve_ref(ref, case_paths):
    value=clean_ref(ref)
    if value in case_paths:
        return {'reference':ref, 'status':'路径已定位', 'paths':[value]}
    for path in case_paths:
        if path in value:
            return {'reference':ref, 'status':'路径已定位', 'paths':[path]}
    raw_match=re.search(r'raw-(?:anli\d+|qqwb\d+)-[\da-z]+', value)
    if raw_match:
        matches=[p for p in case_paths if raw_match[0] in p]
        if matches:
            return {'reference':ref, 'status':'来源ID候选' if len(matches)>1 else '来源ID已定位', 'paths':matches}
    match=re.search(r'case-\d+', value, re.I)
    if match:
        # Case numbers restart in each category. A bare number must remain ambiguous.
        number=match[0].lower()
        matches=[p for p in case_paths if re.search(re.escape(number)+r'(?!\d)', Path(p).name, re.I)]
        cats=[c for c in {Path(p).parts[1] for p in case_paths} if c in value]
        if cats:
            matches=[p for p in matches if Path(p).parts[1] in cats]
        if matches:
            status='占类与编号已定位' if len(matches)==1 and cats else '编号候选，需核对'
            return {'reference':ref, 'status':status, 'paths':matches}
    return {'reference':ref, 'status':'待定位', 'paths':[]}

def validate_pages(entries):
    """Check generated local targets/anchors, ignoring fenced original quotations."""
    errors=[]
    checked=0
    pages=list(OUT.glob('*.md'))+list((OUT/'sources').glob('*.md'))+[ROOT/'经验日志/_经验导航.md']
    cache={p.resolve():p.read_text(encoding='utf-8-sig') for p in pages}
    for page in pages:
        fence=None
        for line in cache[page.resolve()].splitlines():
            match=re.match(r'^(`{3,})',line)
            if match:
                if fence is None:
                    fence=match[1]
                elif line.strip()==fence:
                    fence=None
                continue
            if fence:
                continue
            for match in re.finditer(r'\]\((?:<([^>]+)>|([^\)]+))\)',line):
                target=match[1] or match[2]
                if re.match(r'^[a-z]+://',target):
                    continue
                base,sep,anchor=target.partition('#')
                base=re.sub(r':\d+$','',base)
                path=Path(base) if Path(base).is_absolute() else page.parent/base
                checked+=1
                if not path.is_file():
                    errors.append(f'链接失效：{page.name} -> {target}')
                elif sep and anchor and path.suffix=='.md':
                    resolved=path.resolve()
                    if resolved not in cache:
                        cache[resolved]=path.read_text(encoding='utf-8-sig')
                    if not re.search(r'id=["\']'+re.escape(anchor)+r'["\']',cache[resolved]):
                        errors.append(f'条目锚点不存在：{target}')
    for e in entries:
        if e['source_excerpt'] not in cache[(OUT/source_page(e['source'])).resolve()]:
            errors.append(f'生成页遗漏原文：{e["id"]}')
    return checked,errors

def build():
    manifest=read_json(OUT/'data/source-manifest.json')
    sources={s['path']:s for s in manifest['sources']}
    errors=[]
    current_logs={p.relative_to(ROOT).as_posix() for p in (ROOT/'经验日志').glob('*.md')
                  if p.name!='_经验导航.md'}
    if current_logs!=set(sources):
        errors.append('日志文件集合已变化，需新快照：'+repr(current_logs.symmetric_difference(sources)))
    current_cases={p.relative_to(ROOT).as_posix() for p in (ROOT/'案例项目库').rglob('*.md')}
    if current_cases!={s['path'] for s in manifest['case_snapshot']}:
        errors.append('案例文件集合已变化，需新快照后重新定位来源')
    for s in manifest['sources']+manifest['case_snapshot']:
        p=ROOT/s['path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=s['sha256']:
            errors.append('来源发生变化或丢失：'+s['path'])
    entries=[]
    dispositions={}
    relations=[]
    findings=[]
    for group in GROUPS:
        payload=read_json(OUT/f'data/{group}.json')
        if payload['group']!=group:
            errors.append('分组不符：'+group)
        expected={s['path'] for s in sources.values() if s['group']==group}
        actual=[s['path'] for s in payload['sources']]
        if set(actual)!=expected or len(actual)!=len(set(actual)):
            errors.append(f'{group}来源覆盖不全或重复：缺{expected-set(actual)}，多{set(actual)-expected}')
        for s in payload['sources']:
            dispositions[s['path']]=s
        for e in payload['entries']:
            missing=REQUIRED-set(e)
            if missing:
                errors.append(f'{e.get("id")}缺字段{missing}')
                continue
            if e['source'] not in expected:
                errors.append(f'{e["id"]}不在负责组中')
                continue
            lines=(ROOT/e['source']).read_text(encoding='utf-8-sig').splitlines()
            a,b=e['line_start'],e['line_end']
            if not isinstance(a,int) or not isinstance(b,int) or not 1<=a<=b<=len(lines):
                errors.append(f'{e["id"]}原文范围不合法：{a}-{b}/{len(lines)}')
                continue
            if e['kind'] not in KINDS or e['verification'] not in VERIFICATIONS:
                errors.append(f'{e["id"]}类型或状态未定义')
            for key in ('categories','method_tags','evidence_basis','case_refs'):
                if not isinstance(e[key],list) or any(not isinstance(x,str) for x in e[key]):
                    errors.append(f'{e["id"]}字段{key}必须为字符串数组')
            e['categories']=list(dict.fromkeys(ALIASES.get(c,c) for c in e['categories']))
            e['group']=group
            e['source_excerpt']='\n'.join(lines[a-1:b])
            e['independent_validation_increment']=0
            e['method_families']=[k for k,pattern in FAMILIES.items()
                                  if re.search(pattern, ' '.join(e['method_tags'])+' '+e['title'])]
            if not e['method_families']:
                e['method_families']=['其他专题']
            entries.append(e)
        relations.extend(payload.get('relations',[]))
        findings.extend(dict(group=group, text=f) for f in payload.get('findings',[]))
    for s in sources.values():
        if s['group']=='support':
            dispositions[s['path']]=dict(path=s['path'], disposition='索引资料' if s['path'].endswith('_metadata_index.md') else '模板及说明', note='支持文件登记，不作为额外经验或独立证据。')
    if (OUT/'data/cross-relations.json').exists():
        payload=read_json(OUT/'data/cross-relations.json')
        relations.extend(payload['relations'])
        findings.extend(dict(group='cross',text=f) for f in payload.get('findings',[]))
    if (OUT/'data/cross-history-new.json').exists():
        payload=read_json(OUT/'data/cross-history-new.json')
        relations.extend(payload['relations'])
        findings.extend(dict(group='cross-history-new',text=f) for f in payload.get('findings',[]))
    ids=[e['id'] for e in entries]
    if len(ids)!=len(set(ids)):
        errors.append('条目ID重复')
    byid={e['id']:e for e in entries}
    for i,r in enumerate(relations,1):
        r['id']=f'R-{i:03}'
        if r['type'] not in RELATIONS or len(set(r['members']))<2:
            errors.append(f'{r["id"]}关系类型/成员数错误')
        if any(m not in byid for m in r['members']):
            errors.append(f'{r["id"]}引用不存在的条目')
    spans=Counter((e['source'],e['line_start'],e['line_end'],e['title']) for e in entries)
    if any(n>1 for n in spans.values()):
        errors.append('同来源范围及标题有完全重复条目')
    covered={e['source'] for e in entries}
    for s in dispositions.values():
        if s['path'] not in covered and s['disposition'] not in {'索引资料','模板及说明','无新增经验记录','审查资料'}:
            errors.append('经验来源没有检索单元：'+s['path'])
    check=dict(checked_at=datetime.now().isoformat(timespec='seconds'), errors=errors,
               source_files=len(sources), case_files_in_snapshot=len(manifest['case_snapshot']),
               annotation_sources=len(dispositions), entries=len(entries), relations=len(relations),
               all_original_hashes_unchanged=not any('来源发生变化' in x for x in errors),
               all_independent_validation_increments_zero=True,
               scope_note='校验覆盖、引用和原文完整性，不证明断法正确或经验泛化有效。')
    write_json(OUT/'data/validation.json',check)
    if errors:
        raise SystemExit('\n'.join(errors))
    case_paths=[s['path'] for s in manifest['case_snapshot'] if Path(s['path']).name.startswith('case-')]
    for e in entries:
        e['case_reference_resolution']=[resolve_ref(ref,case_paths) for ref in e['case_refs']]
    now=datetime.now().isoformat(timespec='seconds')
    catalog=dict(schema_version='experience-review-1', created_at=now,
                 scope=manifest['scope'], independent_validation_increment=0,
                 count_semantics='条目是方法/专题/案例/审查标记的检索单元，不是独立经验数或验证次数。',
                 sources=[dict(**s, **{k:v for k,v in dispositions[s['path']].items() if k!='path'})
                          for s in sources.values()],
                 entries=entries, relations=relations, findings=findings)
    write_json(OUT/'data/catalog.json',catalog)
    with (OUT/'data/catalog.jsonl').open('w',encoding='utf-8') as handle:
        for e in entries:
            handle.write(json.dumps(e,ensure_ascii=False)+'\n')
    bysource=defaultdict(list)
    for e in entries:
        bysource[e['source']].append(e)
    touching=defaultdict(list)
    for r in relations:
        for member in r['members']:
            touching[member].append(r)
    for source,items in bysource.items():
        lines=[f'# {Path(source).name}', '', link(source,'完整来源原文'), '',
               f'来源 SHA-256：`{sources[source]["sha256"]}`', '',
               '以下摘要、分类、核验标记为本次整理意见；引用区逐字取自快照来源。独立验证增量全部为 0。', '']
        for e in items:
            lines.extend([f'<a id="{e["id"].lower()}"></a>', '',f'## {e["id"]} {e["title"]}', '',
                          f'**类型**：{e["kind"]}　**占类**：{"、".join(e["categories"])}　**验证定位**：{e["verification"]}', '',
                          '**方法标签**：'+'、'.join(e['method_tags']), '', e['summary'], '',
                          '**证据来源**：'+'；'.join(e['evidence_basis']), '',
                          '**原资料的验证声明**：'+(e['source_claim'] or '未提供'), '',
                          '**条件及缺口**：'+e['caveat'], '',
                          f'**原文位置**：{link(source, "第 "+str(e["line_start"])+"–"+str(e["line_end"])+" 行",e["line_start"])}', ''])
            if e['case_reference_resolution']:
                lines.extend(['**关联案例（身份定位，不等于多份独立证据）**：',''])
                for ref in e['case_reference_resolution']:
                    targets='；'.join(link(p,Path(p).name) for p in ref['paths'])
                    lines.append(f'- {ref["reference"]}：{ref["status"]}'+('；'+targets if targets else ''))
                lines.append('')
            if touching[e['id']]:
                lines.extend(['**关联方法**：',''])
                for r in touching[e['id']]:
                    others=[entry_link(byid[x]) for x in r['members'] if x!=e['id']]
                    lines.append(f'- {r["id"]} {r["type"]}：'+ '；'.join(others)+'。'+r['reason'])
                lines.append('')
            fence='`'*max(3,max([len(m[0]) for m in re.finditer(r'`+',e['source_excerpt'])] or [0])+1)
            lines.extend(['<details>', '<summary>查看所依据的连续原文</summary>', '',fence+'text',
                          e['source_excerpt'],fence,'','</details>',''])
        write_md(OUT/source_page(source),lines)
    counts=Counter(e['verification'] for e in entries)
    kinds=Counter(e['kind'] for e in entries)
    lines=['# 经验库梳理导航', '',f'整理日期：{now[:10]}。覆盖经验日志原有 **{len(sources)} 个文件**，其中正文与资料 {sum(s["group"]!="support" for s in sources.values())} 个、模板/说明/旧索引 3 个；案例库 {len(manifest["case_snapshot"])} 个 Markdown 文件作来源交叉定位快照。', '',
           f'已建立 **{len(entries)} 个检索单元**、**{len(relations)} 组关联**。检索单元可包含一组子规则，也含反例/审查/未采纳记录，不能等同于新增经验条数或独立验证数。', '',
           '## 从这里查', '',
           '- [按占类查](分类索引.md)：先确定占问场景。',
           '- [按方法与技巧查](技巧索引.md)：区分可操作方法、条件规则、案例观察。',
           '- [技巧速览](技巧速览.md)：先看代表性操作方法与尚缺的验证。',
           '- [验证不足与待核清单](验证与待核.md)：查看证据层级与具体缺口。',
           '- [重复、相似与冲突](重复相似与冲突.md)：查看同源复写及适用条件差异。',
           '- [来源清单](来源清单.md)：逐文件覆盖、出处及来源原文。',
           '- [核验报告](核验报告.md)：范围、数据检查和未解决事项。', '',
           '## 使用边界', '',
           '这是附加的梳理与检索层，原日志、案例及 skill 保留原样。技巧标签表示存在可操作方法，不表示已通过效果验证。优秀作业保留高质量参照价值；现实反馈、书籍出处、参照吻合与反推解释分别标注。本次独立验证增量为 0，不改变旧权重。', '',
           '书籍条目来自现有摘录，本轮未逐句对照书籍库原典；历史“验”沿录为来源声明。旧审查报告所说“有据”是出处审查，不是独立预测效果验证；其原有无据/疑点不因本次分类而取消。', '',
           '## 当前统计', '', '| 类型 | 检索单元数 |','|---|---:|']
    lines.extend(f'| {k} | {n} |' for k,n in kinds.items())
    lines.extend(['','## 检索命令','', '在项目根目录运行：', '', '```powershell',
                  'python -X utf8 tools/build-experience-review.py --search "空亡 填实"',
                  'python -X utf8 tools/build-experience-review.py --search "取数" --category "财运占" --include-general',
                  'python -X utf8 tools/build-experience-review.py --search "反吟" --kind "反例边界"',
                  '```','',
                  '多个词按“同时包含”搜索；搜索摘要、标题、标签及原文。指定占类时，`--include-general` 同时纳入通用方法。`data/catalog.json` 和 `catalog.jsonl` 供后续模型读取，必须一并读取验证定位、条件及缺口，避免只截断语。', '',
                  '## 后续模型如何使用', '',
                  '先读 `经验日志/_经验导航.md`，按占类与具体方法检索少量条目，再读命中条目的连续原文、来源身份、反证和关联关系。无需一次读完整个 JSON 或经验库。引用时记录条目 ID 与原文位置；未验证候选仅作为备选解释，不把技巧分类、作业吻合或重复引用转换成新的验证次数。', '',
                  '输入修订后可运行 `python -X utf8 tools/build-experience-review.py` 重建；会先检查原来源哈希，发现来源变化即停止，需另开快照并复核行号，不能沿用旧行号。'])
    write_md(OUT/'README.md',lines)
    lines=['# 按占类查经验', '', '旧称映射：交易→财运、考试→学业、疾病/灾厄→健康、宅门→家宅、行人→出行、胎产归感情并保留原专题。推命、射覆、来意、杂事单列。多类条目可以出现在多栏，栏位计数不相加。','']
    cats=sorted({c for e in entries for c in e['categories']})
    for category in cats:
        items=[e for e in entries if category in e['categories']]
        lines.extend([f'## {category}（{len(items)}）','']+table(items)+[''])
    write_md(OUT/'分类索引.md',lines)
    lines=['# 方法与技巧索引', '', '“技巧”限于有操作步骤、取舍或修正方法的条目；“条件规则”保留条件与结论；一次事件的断语归案例观察。以下各方法族可能交叉，不是互斥经验总数。','']
    for family in [*FAMILIES,'其他专题']:
        items=[e for e in entries if family in e['method_families']]
        if not items:
            continue
        lines.extend([f'## {family}（{len(items)}）',''])
        for kind in ('技巧','条件规则','方法框架','反例边界','案例观察','设计假设','历史审查标记','说明记录'):
            subset=[e for e in items if e['kind']==kind]
            if subset:
                lines.extend([f'### {kind}（{len(subset)}）','']+table(subset)+[''])
    write_md(OUT/'技巧索引.md',lines)
    quick=[
        ('先拆判断对象', '把载体修复、旧数据保留等目标分开，不用“事成”包办全部子问题。', ['N0083','N0084'], '物件与信息的类神映射仍是候选；本案反馈不能证明所有同课均如此。'),
        ('把过程与结局分层', '反吟反复、拖延与能否得到目标分别论证，保留类神/课体权重的竞争解释。', ['H0195','N0109'], '现有摘录的全局优先级有分歧，不能直接定成无条件铁律。'),
        ('把应期量级与日期分开', '先界定月内/迟速等时间尺度，再生成具体月、日、时；核实发用、中传等适用位置。', ['N0016','N0019'], '旧案应月不能直接搬用；候选日期须在见反馈前确定。'),
        ('先固定取数体系和基数', '区分名次、金额、比例及单位，标明河图/宫数/大衍与取数对象，不从答案倒选算法。', ['H0191','N0093'], '数理体系、年命和金额基数未定者不能精断，也不能把多个近似算法当独立互证。'),
        ('定位先说明类神选择', '比较正类神、物件类神、日支及下临地盘的选择前提，再谈方位和容器。', ['H0190','N0037'], '已有日志的方位优先级未统一；不能只因输出方向接近便宣布整套方法已验。'),
        ('保留反推与反证', '区分原有规则误用纠正、反馈后新假说、未成立链条，记录可替代解释。', ['N0017','H0196'], '这些是可操作的复盘纪律；未采纳说明与反面例子不算成立的新断法。'),
    ]
    lines=['# 技巧速览','', '以下把具有操作步骤的方法整理出来，方便进入详细索引。“可操作”与“已验证有效”分别判断；每条仍须读取自己的来源和边界。完整书籍与专题目录见[技巧索引](技巧索引.md)。','',
           '| 技巧方向 | 如何操作 | 代表入口 | 验证或适用缺口 |','|---|---|---|---|']
    for title,operation,members,caveat in quick:
        links='；'.join(entry_link(byid[m]) for m in members if m in byid)
        lines.append(f'| {title} | {operation} | {links} | {caveat} |')
    write_md(OUT/'技巧速览.md',lines)
    lines=['# 验证情况与待核清单', '', '没有以本次整理代替实证验证。需要区分“原书有记载”“原案有反馈”“本次推理与优秀作业一致”“该细化规则跨独立案例有效”四件事。单案已验也不能证明其中每条链条均成立。所有新增独立验证计数为 0。', '',
           '另须区分三轴：①反馈是否存在；②初判验/部分验/未验；③提取经验是否独立验证。“未验”可能是初判失准，不能自动理解成没有现实反馈；经验META“未载”也不能抹去关联案例已有的结果。工作调动与手机数据案即有这种字段混用，需要连同原文读取。', '',
           '| 验证定位 | 检索单元数 |','|---|---:|']
    lines.extend(f'| {k} | {v} |' for k,v in counts.items())
    lines.extend(['','## 后续核验顺序','',
                  '1. 优先检查历史已判无据/与原典冲突但仍被新记录引用的链条，以及盘面起例/类神身份有争议者。',
                  '2. 对高价值优秀作业候选，固定条件、竞争解释和预先判断，再补独立现实案例；不得以材料份数累计命中。',
                  '3. 对取数、精确应日、具体现代物象等容易反推拟合的规则，先冻结算法及允许误差，再做不知答案的检验。',
                  '4. 对书籍重复例先查共同原案/转引链；出处核对与预测效果验证分别记录。',''])
    order=['历史疑点保留','设计未验证','优秀作业参照待验','未验证从疑','单案复盘待泛化','来源称验未独立核验','书籍提取未核原典','不适用']
    for status in order:
        items=[e for e in entries if e['verification']==status]
        if items:
            lines.extend([f'## {status}（{len(items)}）','']+table(items,True)+[''])
    write_md(OUT/'验证与待核.md',lines)
    lines=['# 重复、相似与冲突关系', '', '这些是整理后的关系组，不是删除或合并指令。相同占类/课体/发用仅用于检索，不能认定规则相同。高度重复候选仍需比较原句、条件与来源；相似方法可以保留各自边界。没有将文本相似分数当作语义定论。','',
           '| 关系类型 | 关系组数 |','|---|---:|']
    relation_counts=Counter(r['type'] for r in relations)
    lines.extend(f'| {t} | {relation_counts[t]} |' for t in ['同源复写','高度重复候选','相似方法','条件差异','冲突待核'])
    lines.extend(['', '每组可能包含多条来源，同一条目也可属于多组；组数不是重复规则数或独立事件数。',''])
    for r in relations:
        lines.extend([f'## {r["id"]} {r["type"]}','',r['reason'],''])
        lines.extend('- '+entry_link(byid[m])+'；'+link(byid[m]['source'],'原文',byid[m]['line_start']) for m in r['members'])
        lines.append('')
    write_md(OUT/'重复相似与冲突.md',lines)
    lines=['# 来源覆盖清单','', '清单登记全部原始文件。索引、审查、方法方案与经验正文分别标注，避免把目录或既有审查的转述再次算作独立经验。','',
           '| 原来源 | 分组 | 资料定位 | 检索单元 | 说明 |','|---|---|---|---:|---|']
    for path,s in sources.items():
        disp=dispositions[path]
        count=len(bysource[path])
        page=link((OUT/source_page(path)).relative_to(ROOT),'条目页') if count else '—'
        lines.append(f'| {link(path,Path(path).name)} | {GROUP_NAMES[s["group"]]} | {disp["disposition"]} | {count}（{page}） | {esc(disp["note"])} |')
    write_md(OUT/'来源清单.md',lines)
    unresolved=[(e,ref) for e in entries for ref in e['case_reference_resolution'] if ref['status'] in {'待定位','编号候选，需核对','来源ID候选'}]
    lines=['# 核验报告','',f'生成于 {now}。','',
           f'- 原经验日志快照 {len(sources)} 文件，案例 Markdown 快照 {len(manifest["case_snapshot"])} 文件；全部 SHA-256 与整理前一致。',
           f'- 三个分组覆盖 {len(dispositions)} 个来源（含 3 个支持文件登记），{len(entries)} 个条目 ID 唯一。',
           '- 每个条目原文区间均在原文件有效行号内；原文区从文件程序化截取，未由模型改写。',
           f'- {len(relations)} 个关系组的成员引用均存在；来源页、分类、技巧与待核索引由同一份 JSON 生成。',
           '- 所有条目独立验证增量为 0；没有将分类结果写回 skill 或旧经验权重。','',
           '## 整理发现','']
    lines.extend('- '+f['text'] for f in findings)
    lines.extend(['','## 尚待定位的案例引用','',
                  '仅列身份定位不充分的引用，不擅自补成真实路径。案例编号在不同占类内重复，只有编号不足以确认同源。',''])
    for e,ref in unresolved:
        lines.append(f'- {entry_link(e)}：`{ref["reference"]}`（{ref["status"]}）')
    if not unresolved:
        lines.append('未发现未定位或歧义的已登记案例引用。')
    lines.extend(['','## 范围限制','',
                  '本轮覆盖经验日志，不重新穷尽提取 247 个案例 Markdown 中尚未写入日志的所有潜在经验；案例用于来源关系与重点同源核对。现有书籍摘录未逐句回查原典。语义相似关系是人工/模型整理结果，可能遗漏隐含同义表达，不构成穷尽去重证明。', '',
                  '条目粒度按独立案例、方法专题或具体候选安排，复杂专题含多条子法；统计用于导航，不作为唯一规则总数。历史审查保留其判定与理由，本次未把所有历史争议重审为最终结论。', '',
                  '新增材料不会自动进入本快照索引。后续继续批处理后，应重新建快照、补语义标注、重新生成，不能只扫描标题自动升级经验。'])
    write_md(OUT/'核验报告.md',lines)
    write_md(ROOT/'经验日志/_经验导航.md',[
        '# 经验梳理导航', '', link((OUT/'README.md').relative_to(ROOT),'打开 2026-10-19 经验分类、技巧、验证与重复关系索引'), '',
        '这是覆盖原有 109 个经验日志文件的附加导航。原文及现有 `_metadata_index.md` 保留，新增索引文件以 `_` 开头，旧 META 索引器会跳过。', '',
        '查用经验时同时读取验证定位、来源、条件与反证。优秀作业是高质量参照；未验证链条保持从疑，本次独立验证增量 0。'])
    checked,page_errors=validate_pages(entries)
    check.update(rendered_links_checked=checked, quoted_ranges_checked=len(entries))
    check['errors'].extend(page_errors)
    write_json(OUT/'data/validation.json',check)
    if page_errors:
        raise SystemExit('\n'.join(page_errors))
    print(json.dumps(dict(entries=len(entries), relations=len(relations), sources=len(dispositions), unresolved_case_references=len(unresolved), verification_counts=counts, kind_counts=kinds),ensure_ascii=False,indent=2))

def search(args):
    payload=read_json(OUT/'data/catalog.json')
    terms=(args.search or '').lower().split()
    found=[]
    for e in payload['entries']:
        if args.category and args.category not in e['categories'] and not (args.include_general and '通用' in e['categories']):
            continue
        if args.kind and args.kind!=e['kind']:
            continue
        text=' '.join([e['title'],e['summary'],e['source_excerpt'],*e['method_tags']]).lower()
        if all(t in text for t in terms):
            found.append(e)
    print(f'命中 {len(found)} 个检索单元；以下最多显示 {args.limit} 个。')
    for e in found[:args.limit]:
        print(f'\n{e["id"]} {e["title"]}\n类型：{e["kind"]}；验证：{e["verification"]}\n{e["summary"]}\n缺口：{e["caveat"]}\n来源：{e["source"]}:{e["line_start"]}\n条目页：{OUT/source_page(e["source"])}#{e["id"].lower()}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--search')
    parser.add_argument('--category')
    parser.add_argument('--kind')
    parser.add_argument('--include-general',action='store_true')
    parser.add_argument('--limit',type=int,default=20)
    args=parser.parse_args()
    if args.search is not None or args.category or args.kind:
        search(args)
    else:
        build()
