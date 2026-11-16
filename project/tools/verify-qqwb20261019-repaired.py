"""Independent acceptance checks against original capture and visual observations."""
import collections
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'docs/初级案例整理/初级案例资料/qqwb20261019-有效201例-修订版'
SOURCE = ROOT / '资料来源/qq-homework-20261018/batch_20261019'


def source_copy(historical):
    """Resolve only the preserved capture prefix; keep original fingerprint bytes."""
    old = pathlib.Path(r'C:\Users\QLMa_\WorkBuddy\2026-10-18-12-01-33\qq_homework')
    path = pathlib.Path(historical)
    try:
        relative = path.relative_to(old)
    except ValueError:
        raise ValueError('unregistered external fingerprint source: ' + historical)
    result = (ROOT / '资料来源/qq-homework-20261018' / relative).resolve()
    if not result.is_relative_to((ROOT / '资料来源/qq-homework-20261018').resolve()):
        raise ValueError('invalid fingerprint source path')
    return result


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def jsonl(p):
    return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    manifest = read(PACKAGE / 'analysis_manifest.json')
    source_records = {r['seq']: r for r in jsonl(SOURCE / 'raw/records.jsonl')}
    expected = {seq for seq, r in source_records.items() if r.get('mofan_kind') == 'mofan'}
    rows = manifest['cases']
    assert len(rows) == len(expected) == 201
    assert len({r['case_id'] for r in rows}) == 201
    assert {r['seq'] for r in rows} == expected
    assert {r['seq'] for r in jsonl(PACKAGE / 'raw/records.jsonl')} == expected
    reviewed = 0
    for row in rows:
        case = (PACKAGE / row['case_file']).read_text(encoding='utf-8')
        blocks = re.findall(r'```text\n(.*?)\n```', case, re.S)
        assert len(blocks) == 1, row['case_id']
        for field in ['detail', 'mofan']:
            assert source_records[row['seq']][field].replace('\r\n', '\n') in blocks[0]
        for pathkey, hashkey in [('case_file', 'case_sha256'), ('public_path', 'public_sha256'), ('private_path', 'private_sha256')]:
            assert sha(PACKAGE / row[pathkey]) == row[hashkey]
        public = read(PACKAGE / row['public_path'])
        private = read(PACKAGE / row['private_path'])
        assert private['逐份作答'] and row['has_assignment_reference'] and row['ready_for_first_analysis']
        original_answer = '\n'.join(l.rstrip() for l in source_records[row['seq']]['mofan'].replace('\r\n', '\n').splitlines())
        for card in private['逐份作答']:
            assert card['正文'] in original_answer, row['case_id']
        if len(row['charts']) == 2:
            assert public['schema'] == 'case-public-input-multichart-v1'
            assert len(public['charts']) == 2 and 'facts' not in public
        for index, entry in enumerate(row['charts']):
            chart = read(PACKAGE / entry['chart_file'])
            assert sha(PACKAGE / entry['chart_file']) == entry['chart_sha256']
            assert chart['validation']['ok']
            facts = public['facts'] if len(row['charts']) == 1 else public['charts'][index]['facts']
            assert facts == chart['facts']
            assert 'summary' not in facts and 'key_shensha' not in facts
            if 'source_review' in chart:
                reviewed += 1
                obs = chart['source_review']
                assert facts['pillars'][:3] == obs['printed_pillars'][:3]
                assert facts['month_general'] == obs['month_general']
                assert facts['hour_branch'] == obs['effective_casting_hour_branch']
                assert len(facts['lessons']) == len(obs['lessons']) == 4
                assert len(facts['transmissions']) == len(obs['transmissions']) == 3
                for actual, expected_lesson in zip(facts['lessons'], obs['lessons']):
                    for key in ['tianpan', 'dizhi', 'tianjiang']:
                        assert actual[key] == expected_lesson[key], (row['case_id'], key)
                for actual, expected_transmission in zip(facts['transmissions'], obs['transmissions']):
                    for key in ['diZhi', 'tianjiang']:
                        assert actual[key] == expected_transmission[key], (row['case_id'], key)
                assert sha(PACKAGE / obs['file']) == obs['sha256']
            if row['seq'] == 63:
                assert facts['event_datetime'] is None and chart['conventions']['manual_date_is_placeholder']
            if row['seq'] == 237:
                assert facts['event_datetime'] is None and chart['input']['pillars']['hour_branch'] == '亥'
            if row['seq'] == 201:
                assert facts['transmission_sequence'] == '丑卯巳'
                assert chart['source_review']['printed_pillars'][3] == '戊辰'
                assert facts['hour_branch'] == '寅'
    image_ledger = read(PACKAGE / 'image_ledger.json')['images']
    assert len(image_ledger) == len(jsonl(PACKAGE / 'raw/images.jsonl')) == 216
    assert {i['file'] for i in image_ledger} == {i['file'] for i in jsonl(PACKAGE / 'raw/images.jsonl')}
    for image in image_ledger:
        assert image['seq'] in expected and sha(PACKAGE / image['file']) == image['sha256']
    for item in read(PACKAGE / 'review/来源指纹.json'):
        assert sha(source_copy(item['file'])) == item['sha256']
    assert len(list((PACKAGE / 'cases').glob('*.md'))) == 201
    assert len(list((PACKAGE / 'analysis-ready/public').glob('*.json'))) == 201
    assert len(list((PACKAGE / 'analysis-ready/private').glob('*.json'))) == 201
    assert len(list((PACKAGE / 'charts/v8').glob('*.json'))) == 203
    assert reviewed == 33
    old = read(PACKAGE.parent / 'qqwb20261019-分流-20261019/analysis_manifest.json')
    assert len(old['cases']) == 201 and not any(r['ready_for_first_analysis'] for r in old['cases'])
    result = {'通过': True, '有效来源':201,'剔除无作答':42,'公开私有包配对':201,'程序盘':203,'逐图核心核对':33,'图片哈希':216,
              '原始抓取未改动':True,'完整原文覆盖':True,'作答正文来源匹配':True,'旧清单已停用':True,
              '原始抓取状态':dict(collections.Counter(r['mofan_kind'] for r in source_records.values())),
              '界限':'仅31例异常的33张原图逐图核对；其余170例未宣称逐图复核。作答正确性与现实反馈未验证。'}
    (PACKAGE / 'review/验收结果.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
