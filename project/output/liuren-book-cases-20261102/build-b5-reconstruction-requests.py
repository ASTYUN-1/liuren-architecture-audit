"""Create independent source-bound requests; never rewrite book registries."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
SOURCE = '书籍库/现代著作/《壬占汇选》.txt'
raw = (ROOT / SOURCE).read_bytes()
sha = hashlib.sha256(raw).hexdigest()
lines = raw.decode('utf-8-sig').splitlines()

def ref(start, end, **extra):
    return dict(path=SOURCE, line_start=start, line_end=end,
                quote='\n'.join(lines[start-1:end]), sha256=sha, role='原书断语', **extra)

def constraint(field, expected, start, end, **extra):
    return dict(field=field, expected=expected, evidence_refs=[ref(start, end)],
                extraction_review_state='source_checked', **extra)

def make(case, suffix, year, month, day, hour, general, heading, constraints, notes):
    rid = f'RC26-ANCIENT-{case}-{suffix}'
    request = dict(schema='liuren-book-reconstruction-request-v1', id=rid,
        case_id=f'BK26-ANCIENT-{case}',
        input=dict(mode='manual-pillars', pillars=dict(year=year, month_branch=month,
            day=day, hour_branch=hour), month_general=general),
        input_evidence=[ref(heading, heading)],
        input_sources={
            'pillars.year': f'原文{heading}明确年柱{year}。',
            'pillars.month_branch': f'原文{heading}所载月份按建寅月序映射为{month}；月支为映射值，不冒充逐字原载。',
            'pillars.day': f'原文{heading}明确{day}日。',
            'pillars.hour_branch': f'原文{heading}明确{hour}时。',
            'month_general': f'原文{heading}明确{general}将。'},
        constraints=constraints,
        settings_mode='enumerate_unverified', max_candidates=8,
        original_source_condition='原文盘式/天将冲突的fragment身份保留；此请求只比较一组观察，不要求互斥两盘同时吻合。',
        notes=notes + ['由B5单独读明示字段与盘列构造；原登记不改，不按作者反馈挑盘，不变更complete。'])
    target = ROOT / 'output/liuren-book-cases-20261102' / f'reconstruction-request-ancient-{case}-{suffix.lower()}.json'
    target.write_text(json.dumps(request, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(target.relative_to(ROOT).as_posix())

make('051', 'MAIN', '辛卯', '寅', '癸酉', '巳', '寅', 1405,
    [constraint('transmission_sequence', '午卯子', 1409, 1413)] +
    [constraint(f'transmissions.{i}.tianjiang', value, row, row)
     for i, value, row in [(0, '天后', 1409), (1, '朱雀', 1411), (2, '青龙', 1413)]],
    ['主盘三传午卯子/后朱龙，与另传卯酉卯、返吟断语分开比较。'])

make('051', 'ALT', '辛卯', '寅', '癸酉', '巳', '寅', 1405,
    [constraint('transmission_sequence', '卯酉卯', 1419, 1423)] +
    [constraint(f'transmissions.{i}.tianjiang', value, row, row)
     for i, value, row in [(0, '太阴', 1419), (1, '勾陈', 1421), (2, '太阴', 1423)]] +
    [constraint('chart_types', '返吟', 1425, 1425, operator='contains')],
    ['另传卯酉卯/阴勾阴与返吟断语成组观察；输入仍只用题头明示，不据返吟倒推时将。'])

make('067', 'MAIN', '戊戌', '酉', '甲戌', '未', '辰', 1689,
    [constraint('transmission_sequence', '申巳寅', 1695, 1699)] +
    [constraint(f'transmissions.{i}.tianjiang', value, row, row)
     for i, value, row in [(0, '天后', 1695), (1, '朱雀', 1697), (2, '青龙', 1699)]],
    ['主盘三传申巳寅/后朱龙；与同前借盘及断语虎勾蛇独立比较。'])

borrowed = [constraint('transmission_sequence', '申巳寅', 1681, 1685)] + [
    constraint(f'transmissions.{i}.tianjiang', value, row, row)
    for i, value, row in [(0, '白虎', 1681), (1, '勾陈', 1683), (2, '腾蛇', 1685)]]
for item in borrowed:
    item['evidence_refs'][0].update(dependency_type='borrowed_chart', same_event=False)
    item['source_conflict_note'] = '1691课式同前承接前案简盘；仅借盘依赖，不合并两个事件。1705断语天将与借前组相应，主盘另有后朱龙。'
make('067', 'BORROWED', '戊戌', '酉', '甲戌', '未', '辰', 1689,
    borrowed,
    ['借前简盘申巳寅/虎勾蛇与1705断语对照。前案来源只作借盘依赖，不当本案发生记录。',
     '互斥两组单独保存，不将任何反馈用于输入或约束选择。'])
