from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
ANCIENT = '书籍库/现代著作/《壬占汇选》.txt'
MODERN = '书籍库/现代著作/当代壬占汇选第五版.md'
def ref(source, a, b):
    raw = (ROOT/source).read_bytes()
    return dict(path=source, line_start=a, line_end=b, sha256=hashlib.sha256(raw).hexdigest(),
        quote='\n'.join(raw.decode('utf-8-sig').splitlines()[a-1:b]), role='原书断语')
def c(source, field, expected, a, b, **extra):
    return dict(field=field, expected=expected, evidence_refs=[ref(source,a,b)], extraction_review_state='source_checked', **extra)
def emit(book, n, suffix, pillars, general, refs, sources, constraints, notes):
    request = dict(schema='liuren-book-reconstruction-request-v1', id=f'RC26-{book}-{n}-{suffix}', case_id=f'BK26-{book}-{n}',
        input=dict(mode='manual-pillars', pillars=pillars, month_general=general), input_evidence=refs,
        input_sources=sources, constraints=constraints, settings_mode='enumerate_unverified', max_candidates=8,
        original_source_condition='按来源中一组输入/盘式独立复原；原图未载、异盘及正文冲突身份保留。',
        notes=notes+['不按原载反馈择盘，不自动升级完整性；原书与生成登记均不修改。'])
    target=ROOT/f'output/liuren-book-cases-20261102/reconstruction-request-{book.lower()}-{n}-{suffix.lower()}.json'
    target.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(target.relative_to(ROOT).as_posix())

for suffix, sequence, generals, rows in [('MAIN','子申辰',['腾蛇','青龙','玄武'],[1063,1065,1067]),
                                        ('ALT','戌午寅',['六合','白虎','天后'],[1073,1075,1077])]:
    emit('ANCIENT','033',suffix,dict(year='庚午',month_branch='卯',day='庚午',hour_branch='卯'),'亥',
        [ref(ANCIENT,1059,1059)],
        {'pillars.year':'1059乾隆庚午年，未换算公历。','pillars.month_branch':'1059二月按建寅月序映射卯，非逐字原载月支。',
         'pillars.day':'1059庚午日。','pillars.hour_branch':'1059卯时。','month_general':'1059亥将。'},
        [c(ANCIENT,'transmission_sequence',sequence,rows[0],rows[-1])]+[
         c(ANCIENT,f'transmissions.{i}.tianjiang',g,row,row) for i,(g,row) in enumerate(zip(generals,rows))],
        ['主盘子申辰与另传戌午寅分组比较，1079火局及末后说法另存，不据断语改输入。'])

emit('MODERN','025','ALT',dict(year='甲辰',month_branch='亥',day='壬辰',hour_branch='未'),'卯',
    [ref(MODERN,3622,3622),ref(MODERN,3665,3665)],
    {'pillars.year':'3622四柱甲辰。','pillars.month_branch':'3622乙亥月柱逐字取支亥。','pillars.day':'3622壬辰日。',
     'pillars.hour_branch':'3622丁未时逐字取支未。','month_general':'3665骑牛明确我用卯将；与主盘寅将分开。'},
    [c(MODERN,'transmission_sequence','子申辰',3665,3665),
     c(MODERN,'lessons.0.tianpan','未',3665,3665),c(MODERN,'lessons.0.tianjiang','太阴',3665,3665),
     c(MODERN,'lessons.1.tianjiang','朱雀',3665,3665),c(MODERN,'heaven_earth.未.tianjiang','朱雀',3665,3665)],
    ['阴神按干阴神即第二课观察；朱雀落未按地盘未宫观察，均供人工复核。',
     '十分钟后未时前台找回与原断申时桌上不同，反馈不参与设置或约束。'])

for suffix,hour,note in [('CLOCK','申','2037明示16:16按民用钟表二小时支映射为申；不改成2039乙酉，不宣称已核原地点/时区。'),
                         ('PILLARS','酉','2039明示乙酉时取支酉；不改2037的16:16钟表时间，原文冲突保留。')]:
    emit('MODERN','007',suffix,dict(year='甲辰',month_branch='辰',day='庚申',hour_branch=hour),'戌',
        [ref(MODERN,2037,2039)],
        {'pillars.year':'2039甲辰年。','pillars.month_branch':'2039戊辰月柱取支辰。','pillars.day':'2039庚申日。',
         'pillars.hour_branch':note,'month_general':'2039明示月将戌；与首盘酉将分开。'},
        [c(MODERN,'chart_types','八专',2045,2045,operator='contains'),
         c(MODERN,'lessons.0.tianpan','酉',2045,2045)],
        ['2045干上羊刃、酉为少女按庚日羊刃酉绑定观察；未把内定断语或录取反馈当盘式。',note])
