from pathlib import Path
import copy, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from liuren_book_cases import verify_reconstruction_artifact

BASE = 'output/liuren-book-cases-20261102/'
source = (ROOT / '书籍库/现代著作/当代壬占汇选第五版.md').read_text(encoding='utf-8-sig').splitlines()
assert '己未 壬申' in source[9833] and '子将' in source[9911]
assert '己未 癸酉' in source[9922] and '子将' in source[9971]
excluded = ['nobleman.rule', 'nobleman.requested_zhouye', 'nobleman.actual_zhouye']
notes = {
    98: '逐读9831–9834、9859–9912：原明乙巳戊寅己未壬申，另明子将。8候选均亥卯未曲直，初癸亥大海水、中乙卯大溪水，与原纳音细流关系合。昼贵01/02/05/06为蛇玄龙，夜贵03/04/07/08为合虎后，二组各完整facts实质等价。原9912干上木克土与全候选第一课亥临己不符，干上为亥水非木，保留来源冲突，不重写原句或据医生结石/拉伤筛选；完整不等术理一致。',
    99: '逐读9920–9923、9949–9977：原明乙巳戊寅己未癸酉，另明子将。8组均八专亥戌戌，夜贵03/04/07/08初亥玄武、中末戌太阴、亥地寅天空、戌地丑白虎旬空，逐合9972原载关系。昼贵01/02/05/06初亥蛇中末戌雀，与原天将关系不合但完整并列；两组各完整facts实质等价。仅据原断关系记兼容组，不据戌时或北书房寻获选择唯一盘。主亥将三酉及明镜独足论身份保留。'
}
for n in [98, 99]:
    rid = f'RC26-MODERN-{n:03}-ALT-ZI'
    rp = BASE + f'reconstructions/{rid}.json'
    request_path = BASE + f'reconstruction-request-modern-{n:03}-alt-zi.json'
    result = json.loads((ROOT / rp).read_text(encoding='utf-8-sig'))
    groups = {}
    for c in result['candidates']:
        f = c['facts']
        assert f['day_pillar'] == '己未' and f['month_general'] == '子'
        assert f['hour_branch'] == ('申' if n == 98 else '酉')
        assert f['transmission_sequence'] == ('亥卯未' if n == 98 else '亥戌戌')
        if n == 98:
            assert f['lessons'][0]['tianpan'] == '亥'
            assert '曲直' in f['chart_types']
            assert f['transmissions'][0]['tianGan'] == '癸' and f['transmissions'][1]['tianGan'] == '乙'
        elif c['input']['settings']['zhouye'] == '夜贵':
            hs = {h['di']: h for h in f['heaven_earth']}
            assert '八专' in f['chart_types']
            assert hs['亥']['tian'] == '寅' and hs['亥']['tianjiang'] == '天空'
            assert hs['戌']['tian'] == '丑' and hs['戌']['tianjiang'] == '白虎' and hs['戌']['xungan'] == '空'
            assert [t['tianjiang'] for t in f['transmissions']] == ['玄武', '太阴', '太阴']
        comparable = copy.deepcopy(f)
        for path in excluded:
            one, two = path.split('.')
            comparable[one].pop(two)
        # Every remaining nested facts field participates, not only transmissions.
        key = json.dumps(comparable, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        groups.setdefault(key, []).append(c['id'])
    assert len(groups) == 2 and sorted(len(g) for g in groups.values()) == [4, 4]
    review = dict(schema='liuren-reconstruction-semantic-review-v1', case_id=f'BK26-MODERN-{n:03}', result_id=rid,
                  result_path=rp, result_sha256=hashlib.sha256((ROOT / rp).read_bytes()).hexdigest(),
                  semantic_review_state='source_checked', request_path=request_path, request_sha256=result['request_sha256'],
                  request_file_sha256=hashlib.sha256((ROOT / request_path).read_bytes()).hexdigest(),
                  excluded_setting_label_paths=excluded,
                  equivalent_candidate_groups=[dict(candidate_ids=g) for g in groups.values() if all(cid in result['matching_candidate_ids'] for cid in g)],
                  archived_full_fact_groups=[dict(candidate_ids=g,passes_source_observations=all(cid in result['matching_candidate_ids'] for cid in g)) for g in groups.values()],
                  note=notes[n], selected_candidate_id=None, outcome_feedback_used_for_selection=False,
                  original_image_recovered=False, independent_prediction_validation_count=0)
    review_path = BASE + f'b2-reconstruction-semantic-review-{n:03}.json'
    (ROOT / review_path).write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    link = dict(id=rid, result_path=rp, result_sha256=review['result_sha256'], review_state='source_checked',
                review_path=review_path, review_sha256=hashlib.sha256((ROOT / review_path).read_bytes()).hexdigest())
    verified = verify_reconstruction_artifact(ROOT, link, review['case_id'], review)
    print(json.dumps(dict(n=n, link=link, verified=dict(ok=verified['ok'],raw_archives_verified=verified['raw_archives_verified'],group_count=len(verified['groups']))), ensure_ascii=False))
