"""Targeted comparison of the two original versions against old B0252."""
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
def ref(path,a,b,role):
 raw=(R/path).read_bytes();ls=raw.decode('utf-8-sig').splitlines()
 return dict(path=path,line_start=a,line_end=b,quote='\n'.join(ls[a-1:b]),sha256=hashlib.sha256(raw).hexdigest(),role=role)
record=dict(schema='liuren-audit-v1',id='LA26-BOOK-SHAO-003',title='B0252：保留权摄食禄，限缩额外填空/冲空月份规则',
 target_entry_ids=['B0252'],target_case_paths=[],disposition='narrow',
 finding='旧卡正确保留官空、禄支合及权摄食禄，但另加待官星填空或冲空之月方能正任。对读断案058与古汇选同案，两处都明确待陈姓退去后得正任，并未明示该月份选择算法。旧课体伏吟/玄胎亦不宜当核实课体沿用，断案标题为元胎、比用、不备。',
 reasoning=['原两书课式、将时、权摄经过与关键断语相合，题头郭/邓为版本差异，不增独立事件。',
  '原书官空解释正任未得，另有禄在支与合解释仍食禄，不能删去后者便强推官空必权摄。',
  '实际叙事以陈提刑替去解除障碍，未写填空或冲空之月法；本轮只判这句未获所引原文支持，不断言其他文献永无该法。'],
 evidence_refs=[ref('经验日志/古籍-壬占汇选.md',15,32,'旧AI归纳'),ref('书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt',583,592,'原书断语'),ref('书籍库/现代著作/《壬占汇选》.txt',8195,8212,'原书断语')],
 replacement_rule_ids=['LR26-BOOK-SHAO-058'],review_state='source_checked',
 limitations=['仅核本条及两处同案版本，未遍查全部应期书。','原书历史结果不是本轮独立验证。'],
 reference_value=['保留原断区分正任、权摄及食禄的逻辑，明确阻碍条件和阶段。'],
 action_scope='仅限缩额外月份算法、无条件必权摄及旧课体标签；不撤销整条方法价值。')
p=R/'knowledge/liuren-research/20261102/audits/book-shao-review.json';d={x['id']:x for x in json.loads(p.read_text(encoding='utf-8'))};d[record['id']]=record;p.write_text(json.dumps(list(d.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(record['id'])
