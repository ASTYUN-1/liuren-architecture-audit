"""Final authorized edits to already-reviewed material; no new source reading."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2]; B=R/'knowledge/liuren-research/20261102'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cards=read(B/'rules/book-shao-c-review.json'); by={x['id']:x for x in cards}; reviews=read(B/'method-reviews/shao.json')

# The source explicitly uses 巳4 for its lifespan product, not for the separate four-year shop date.
c=by['LR26-BOOK-SHAO-C049'];c['title']='四年店屋未明算法，巳4两巳8乘子9为72寿'
c['conditions']=['庚戌案原另断四年后得店屋；寿数段明确巳长生4、两巳8、巳上子9。']
c['conclusion']='四年店屋只有原时断，未明以巳4推得；72寿数明确取两巳4相加8再乘子9，寿未见后叙。斫轮转水碓核心复用原049。'
c['reasoning_steps']=['四年店屋与巳4寿数在原文属不同判断，不把相同数字强连。','两巳各4合8，再乘巳上子9得72为原明确数法。','原39岁与后42得店的年龄叙照存，不擅补虚实岁起算。']
for rv in reviews:
 if rv['case_id']=='BK26-SHAO-049':
  for sub in rv['subjudgments']:
   if sub['rule_ids']==[c['id']]:sub['method_note']='四年店屋有原断无明取数法，不能把寿数段巳4借给它；72明确两巳4合8再乘子9，寿未反馈，39/42年龄叙不硬改。'

# Remove duplicated old-card cores from supplements while preserving each distinct chain.
cuts={
 'C050': ('父子贵妻四不足与七杀元辰的原分问', [0,1]),
 'C067': ('三任铜铁、坑冶、船场的具体位置与寅卯比较', [1,2]),
 'C072': ('催官阻服、兄弟子力与午9酉6寿数差', [0,1]),
 'C094': ('蛇非横、婢仆耗财与官费的晚段风险', [1,2]),
 'C096': ('宅勾久滞转虎丁合马，禄马炉模雀的职务细象', [1,2]),
 'C127': ('男胎行年冲耗、肠血原象与成名后48条件', [1,2]),
 'C134': ('初中末限两套数法与官鬼原通论的保留边界', [1,2,3]),
 'C136': ('巳4戌5合9的朴析数法与第七年争赎期差', [2]),
 'C147': ('30年生官与卯6任、末未勾守土死败', [0,2]),
}
for suffix,(title,indices) in cuts.items():
 card=by['LR26-BOOK-SHAO-'+suffix];card['title']=title
 if not card.get('core_reuse_note'):
  card['reasoning_steps']=[card['reasoning_steps'][i] for i in indices]
 card['core_reuse_note']='与原卡重叠的限定核心由method-reviews相应子问直接复用原卡；本补卡只新增上述具体子链。'

# Actual semantic merge: only the identically conditioned water/land core is normalized.
norm_id='LR26-SHAO-CANON-WATER-LAND'
source_ids=['LR26-BOOK-SHAO-C1271','LR26-BOOK-SHAO-C137']
source_cards=[by[x] for x in source_ids]
evidence=[x['evidence_refs'][0] for x in source_cards]
norm=dict(schema='liuren-rule-card-v1',id=norm_id,title='独足酉六合问远行：兑泽合船利水路，无足不利陆路',
 categories=['出行占','财运占'],claim_origin='本轮归纳',review_state='source_checked',status='candidate',
 conditions=['问远行或远方买卖，原载课式为独足、三传酉乘六合。','两个原段都明确以酉兑泽、六合船解释水路，以独足无足解释陆路。'],
 exclusions=['不迁移到同课问子嗣的五女数；不从本核心推导利润倍数。','127附将时巳将卯时、137酉将亥时分别保存，尚不据同象断同一事件或唯一正确排盘。'],
 conclusion='在这两个原载条件分支中，共同水陆方法只保留一条规范入口：酉兑泽、六合船可取水行，独足无足不利陆行。收益幅度另见各来源分支。',
 reasoning_steps=['比较两段相同问事、独足酉六合、泽船和水陆结论，合并其完全重叠的表达。','十倍无后叙与加倍笼统果应为不同收益证据，不并数法、不增加独立验证。'],
 alternatives=['相同课象不足以证明两案为同一次占问；输入将时差异仍待原书/善本核定。'],
 evidence_refs=evidence,source_case_refs=[x['source_case_refs'][0] for x in source_cards],
 source_case_ids=[x['source_case_ids'][0] for x in source_cards],
 support_case_ids=list(dict.fromkeys(v for x in source_cards for v in x['support_case_ids'])),
 counterexample_case_ids=[],legacy_entry_ids=[],relations=[dict(type='条件分支',target_id=x,reason='共享水陆核心统一到本规范入口；本来源独有收益幅度/反馈保留。') for x in source_ids],
 limitations=['规范表达由本轮归并，保留两个来源原文、将时和收益分支；不是水陆预测效力已验证。'],
 independent_validation_count=0,logic_stages=['问事目标','类神','条件归并','水陆取舍'],
 source_rule_map=[dict(source_rule_id=x,canonical_rule_id=norm_id,scope='仅共同水陆方法；不含收益倍数和事件身份') for x in source_ids])
canonical_path=B/'rules/book-shao-canonical.json';canonical=read(canonical_path) if canonical_path.exists() else []
canonical=[x for x in canonical if x['id']!=norm_id]+[norm]
for suffix,title,conclusion in [
 ('C1271','张姓远行十倍财利：原断数无明算法和后叙','张姓附案的十倍获利仅为原预测，未给取倍算法或后叙。共同水陆方法见规范入口LR26-SHAO-CANON-WATER-LAND，不能用主何案五女数代替十倍财利。'),
 ('C137','商人远行加倍得利：只保笼统果应的反馈粒度','商人远行原载加倍得利、果应，未记路线、账目或实际倍数。共同水陆方法见规范入口LR26-SHAO-CANON-WATER-LAND，不能同十倍分支并为一个收益数。')]:
 card=by['LR26-BOOK-SHAO-'+suffix];card['title']=title;card['conclusion']=conclusion
 card['reasoning_steps']=[conclusion]
 card['canonical_rule_id']=norm_id;card['canonical_scope']='水陆共享核心已归一；本卡只保收益与来源差异。'
 card['relations']=[x for x in card['relations'] if x.get('target_id')!=norm_id]+[dict(type='条件分支',target_id=norm_id,reason='共同水陆核心归入规范卡，本卡保留独有收益/反馈分支。')]
for rv in reviews:
 if rv['case_id'] not in {'BK26-SHAO-1271','BK26-SHAO-137'}:continue
 rv['subjudgments'][0]['rule_ids']=[norm_id]
 rv['subjudgments'][0]['disposition']='linked_canonical_rule'
 rv['subjudgments'][0]['method_note']='两个原段的独足酉六合、兑泽船与水陆结论条件相同，共同核心归一到规范卡；收益幅度与将时身份仍另保。'

cases=read(B/'book-cases/shao.json')
for case in cases:
 if case['id'] in {'BK26-SHAO-1271','BK26-SHAO-137'} and norm_id not in case['method_rule_ids']:case['method_rule_ids'].append(norm_id)
families=read(B/'families/book-shao.json')
for family in families:
 for branch in family['preserved_branches']:
  if branch['rule_id'] in by:
   branch['conditions']=by[branch['rule_id']]['conditions']
   if branch['rule_id'] in source_ids:branch['source_method']=by[branch['rule_id']]['conclusion']
 for mapping in family['canonical_rule']['source_rule_map']:
  if mapping['source_rule_id'] in source_ids:mapping['disposition']=by[mapping['source_rule_id']]['conclusion']
fid='LF26-SHAO-INDEPENDENT-FOOT-WATERLAND'
families=[f for f in families if f['id']!=fid]+[dict(id=fid,title='独足酉合远行的水陆共同核心',rule_ids=[norm_id]+source_ids,legacy_entry_ids=[],
 merge_type='同条件同主张规范归并，来源收益分支保留',common_method=norm['conclusion'],
 preserved_branches=[dict(rule_id=x,conditions=by[x]['conditions'],source_method=by[x]['conclusion']) for x in source_ids]+[dict(rule_id=norm_id,conditions=norm['conditions'],source_method=norm['conclusion'])],
 unresolved=['两案未合事件，原将时与收益幅度保留，不称全书同条件去重完成。'],independent_validation_count=0,
 canonical_rule=dict(statement=norm['conclusion'],identity=norm_id,source_rule_map=norm['source_rule_map']+[dict(source_rule_id=norm_id,canonical_family_id=fid,disposition='共同水陆方法规范检索入口')]))]
audit=read(R/'output/liuren-book-cases-20261102/shao-c-condition-dedup-audit.json')
audit['canonical_rules']=[dict(id=norm_id,source_rule_ids=source_ids,merged_scope='同条件水陆共同方法',preserved_differences=['十倍/加倍','无后叙/笼统果应','将时与事件身份'],source_cards_deleted=False)]
audit['specific_corrections']=['C049撤销四年店屋等于巳4取数的无据连接；寿72的明算法保持。','C032不补午生宅受害因果。']
audit['supplement_core_trims']=[dict(rule_id='LR26-BOOK-SHAO-'+x,note='删去与旧卡重复核心陈述，原子问仍直接链接旧卡，新子链保留') for x in cuts]
audit['new_rule_family_maps']=[dict(rule_id=x['id'],family_ids=[f['id'] for f in families if x['id'] in f['rule_ids']]) for x in cards]
write(B/'rules/book-shao-c-review.json',cards);write(canonical_path,canonical);write(B/'method-reviews/shao.json',reviews);write(B/'book-cases/shao.json',cases);write(B/'families/book-shao.json',families)
write(R/'output/liuren-book-cases-20261102/shao-c-condition-dedup-audit.json',audit)
pending=[x for x in cases if x['id'] not in {r['case_id'] for r in reviews}]
handoff=dict(schema='liuren-shao-stage-handoff-v1',stopped_at='C136–149含原重复141，实际15案；后续未开批',reviewed_cases=len(reviews),subjudgments=sum(len(x['subjudgments']) for x in reviews),original_cards=94,supplemental_source_cards=len(cards),canonical_retrieval_rules=len(canonical),
 unfinished_case_count=len(pending),unfinished_cases=[dict(case_id=x['id'],source_case_identity=x['source_case_identity'],method_rule_ids=x['method_rule_ids']) for x in pending],
 reviewed_with_method_gaps=[dict(case_id=x['case_id'],remaining_actions=x['remaining_actions']) for x in reviews if not x['method_extraction_complete']],
 all_book_method_cards_deduplicated=False,all_book_review_complete=False,independent_validation_count=0,
 resume_note='下一批从151/154/158及164起按未审清单接续；150/152/153/155/156/157/159–163已审勿重复。本阶段停止，须新授权再推进。')
write(R/'output/liuren-book-cases-20261102/shao-stage-handoff.json',handoff)
print({k:v for k,v in handoff.items() if k not in {'unfinished_cases','reviewed_with_method_gaps'}})
