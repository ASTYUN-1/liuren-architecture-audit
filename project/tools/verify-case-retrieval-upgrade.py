"""Offline acceptance and transparent old/new retrieval comparisons; no model calls."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from case_retrieval import ROOT, ensure_index, retrieve, evidence_packet

OUT = ROOT / 'output/case-retrieval-upgrade-20261019'
TRIALS = [
    ('换到的新工作会满意吗', '事业占', 'case-008-甲戌女HR'),
    ('秋季招聘企业会发录用通知吗', '事业占', 'case-003-研究生秋招'),
    ('工作调动会在什么时候发生', '事业占', 'case-010-工作调动'),
    ('父亲饮酒身亡，向同饮者索赔，需要走法律程序吗', '官讼占', 'case-003-raw-anli002-0013'),
    ('物业赔偿镯子的费用有多少', '官讼占', 'case-002-raw-anli002-0005'),
    ('国庆前去要工程款，能拿回几成', '财运占', 'case-024-raw-anli001-0032'),
    ('酉命女友是否怀孕，什么时候来月经', '感情占', 'case-012-酉女问怀孕否'),
    ('英语四级考试能过吗', '学业占', 'case-017-壬子日英语四级'),
]


def baseline(fields):
    args = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
            str(ROOT / 'tools/search-cases-legacy.ps1'), '-Scope', 'case', '-Top', '1000']
    for key, flag in [('占类', '-ZhanLei'), ('课体', '-KeTi'), ('发用', '-FaYong'),
                      ('三传', '-SanChuan'), ('日干', '-RiGan'), ('类神', '-LeiShen')]:
        if fields.get(key):
            args += [flag, fields[key]]
    started = time.perf_counter()
    result = subprocess.run(args, cwd=ROOT, capture_output=True, encoding='utf-8', timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr)
    rows = re.findall(r'^\|\s*\d+\s*\|\s*([^|]+)\s*\|\s*case\s*\|', result.stdout, re.M)
    return [r.strip() for r in rows], (time.perf_counter() - started) * 1000


def main():
    index = ensure_index(refresh=True)
    source_hashes = json.loads((OUT / 'before.json').read_text('utf-8'))['raw_hashes']
    changed = [name for name, digest in source_hashes.items()
               if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    if changed:
        raise AssertionError(f'原始资料发生改动：{changed}')
    issues = []
    by_source = {r['source']: r for r in index['cases']}
    for u in index['units']:
        lines = (ROOT / u['source']).read_text('utf-8-sig').splitlines()
        loc = u['question_location']
        if '\n'.join(lines[loc['line_start'] - 1:loc['line_end']]) != loc['text']:
            issues.append(u['id'])
    if issues:
        raise AssertionError(f'问题引文或行号错误：{issues}')
    comparisons = []
    for question, cat, prefix in TRIALS:
        target = next(r for r in index['cases'] if Path(r['source']).name.startswith(prefix))
        number = re.match(r'case-\d+', Path(target['source']).name).group()
        # Legacy index naming may use the normalized category for newly archived cases.
        legacy_key = target['fields'].get('占类', cat) + '/' + number
        for mode in ['仅问题与占类', '问题与完整已载盘面特征']:
            fields = {'占类': cat}
            if mode != '仅问题与占类':
                fields.update({k: target['fields'].get(k, '') for k in ['课体', '发用', '三传', '日干', '类神']})
            old, old_ms = baseline(fields)
            start = time.perf_counter()
            new = retrieve(index, question, fields, limit=1000)
            new_ms = (time.perf_counter() - start) * 1000
            new_sources = [r['case']['source'] for r in new['results']]
            comparisons.append(dict(mode=mode, question=question, expected_source=target['source'],
                                    legacy_key=legacy_key, query_fields=fields,
                                    old_rank=old.index(legacy_key) + 1 if legacy_key in old else None,
                                    new_rank=new_sources.index(target['source']) + 1 if target['source'] in new_sources else None,
                                    old_process_ms=round(old_ms, 2), new_in_process_ms=round(new_ms, 2),
                                    new_first_question=new['results'][0]['unit']['question'] if new['results'] else None))
    exclusion_checks = []
    for r in index['cases']:
        for source_id in r['source_ids']:
            packet = evidence_packet({'question': '工作 反馈 赔偿 考试', 'facts': {}}, source_id, ROOT)
            if any(source_id in ' '.join(row['origin_keys']) for row in packet['results']):
                raise AssertionError('本案排除失败：' + source_id)
            exclusion_checks.append(source_id)
    packet = evidence_packet({'question': '换工作能否满意', 'facts': {}}, '', ROOT)
    data = dict(status='passed', model_calls=0, raw_files_unchanged=len(source_hashes),
                source_coverage=index['status'], source_quote_checks=len(index['units']),
                known_source_exclusion_checks=len(exclusion_checks),
                all_unit_ids_unique=len({u['id'] for u in index['units']}) == len(index['units']),
                legacy_audit=index['legacy_audit'], comparisons=comparisons,
                sample_packet_chars=len(json.dumps(packet, ensure_ascii=False)),
                limitations=['8个有预先指定目标的定位检查，不是盲测、全库召回率或术理正确率评估。',
                             '完整特征来自目标原档，仅测试资料定位；不能代表未知新案的泛化表现。',
                             '旧耗时含PowerShell进程启动，新耗时为内存检索，不能直接据此声称总体提速倍数。',
                             '标题入口、原档历史反馈及程序抽取均未升级为语义核验或独立实证。'])
    (OUT / 'verification.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'legacy-audit.json').write_text(json.dumps(index['legacy_audit'], ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in data.items() if k not in ['legacy_audit', 'comparisons']}, ensure_ascii=False, indent=2))
    for mode in ['仅问题与占类', '问题与完整已载盘面特征']:
        rows = [r for r in comparisons if r['mode'] == mode]
        print(mode, '旧Top3', sum(r['old_rank'] is not None and r['old_rank'] <= 3 for r in rows),
              '新Top3', sum(r['new_rank'] is not None and r['new_rank'] <= 3 for r in rows), '/', len(rows))


if __name__ == '__main__':
    main()
