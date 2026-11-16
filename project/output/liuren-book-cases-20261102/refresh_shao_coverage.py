"""Explicit method-work coverage; source completeness never implies completion."""
import json
from pathlib import Path

def refresh(root):
    path=root/'knowledge/liuren-research/20261102/book-cases/shao.json'
    records=json.loads(path.read_text(encoding='utf-8'))
    review_path=root/'knowledge/liuren-research/20261102/method-reviews/shao.json'
    reviews={r['case_id']:r for r in json.loads(review_path.read_text(encoding='utf-8'))} if review_path.exists() else {}
    supplemental_path=root/'knowledge/liuren-research/20261102/rules/book-shao-c-review.json'
    supplemental=json.loads(supplemental_path.read_text(encoding='utf-8')) if supplemental_path.exists() else []
    queue=[]
    for record in records:
        # Explicitly compared named events and source quotations, never infer from shared context.
        bifa_same={4:25,5:20,31:32,33:30,110:19}
        source_number=int(record['id'].rsplit('-',1)[1])
        if source_number in bifa_same:
            linked=f"BK26-BIFA-{bifa_same[source_number]:03}"
            record['same_event_ids']=list(dict.fromkeys(record.get('same_event_ids',[])+[linked]))
        added=[r['id'] for r in supplemental if record['id'] in r.get('support_case_ids',[])]
        rules=list(dict.fromkeys(record.get('method_rule_ids',[])+added))
        record['method_rule_ids']=rules
        reviewed=reviews.get(record['id'])
        record['method_coverage']={
            'state':'partial_extracted' if rules else 'pending_detailed_review',
            'state_label':'部分已提取' if rules else '待精提取',
            'rule_ids':rules,
            'scope':'仅已保存当前明确方法，仍待C阶段全案覆盖审查、旧法关联及条件归并。' if rules else
                    '完整原文已保存；本批未产新卡不代表确无可用方法，列C阶段逐案精提取。',
            'all_method_dimensions_complete':False,
            'remaining_review':['逐子判断覆盖审查','旧方法关联与同条件归并','未提取方法、取舍和例外条件复核'],
            'unextracted_reason':'本批先保存有明确条件与取舍的方法，未逐子判断完成全面提取。' if rules else
                                 '本批先保全原文及差异，未完成逐子判断精提取；不宣称确无可用方法。',
        }
        if reviewed:
            record['method_coverage']['subjudgment_review']={
                'review_file':'knowledge/liuren-research/20261102/method-reviews/shao.json',
                'review_state':reviewed['review_state'],
                'subjudgment_count':len(reviewed['subjudgments']),
                'all_subjudgments_dispositioned':reviewed['all_subjudgments_dispositioned'],
                'method_extraction_complete':reviewed['method_extraction_complete'],
                'remaining_actions':reviewed['remaining_actions'],
                'C_condition_deduplication_complete':False,
            }
        queue.append({'case_id':record['id'],'source_case_identity':record['source_case_identity'],
                      'source_refs':[{k:v for k,v in ref.items() if k!='quote'} for ref in record['source_refs']],
                      'case_completeness':record['completeness'],'method_coverage':record['method_coverage'],
                      'priority':'review_existing_extraction_and_link_old_methods' if rules else 'detailed_extraction_pending',
                      'independent_validation_count':0})
    path.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    output={'schema':'liuren-shao-method-coverage-v1','book_source':'书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt',
            'registered_cases':len(records),'with_current_rule_cards':sum(bool(x.get('method_rule_ids')) for x in records),
            'pending_detailed_extraction':sum(not x.get('method_rule_ids') for x in records),
            'C_review_complete':False,'queue':queue}
    (root/'output/liuren-book-cases-20261102/shao-method-review-queue.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {k:v for k,v in output.items() if k!='queue'}

if __name__=='__main__':print(json.dumps(refresh(Path(__file__).resolve().parents[2]),ensure_ascii=False))
