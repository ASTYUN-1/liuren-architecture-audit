"""Source-line coverage audit after manual reading; never declares method completion."""
import hashlib,json,re
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[2];S='书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt'
raw=(R/S).read_bytes();lines=raw.decode('utf-8-sig').splitlines();digest=hashlib.sha256(raw).hexdigest()
records=json.loads((R/'knowledge/liuren-research/20261102/book-cases/shao.json').read_text(encoding='utf8'))
primary={};borrowed=[];errors=[]
for x in records:
 for ref in x['source_refs']:
  if ref['path']!=S:continue
  if ref.get('same_event') is False:
   borrowed.append({'case_id':x['id'],'dependency_type':ref.get('dependency_type'),'line_start':ref['line_start'],'line_end':ref['line_end'],'same_event':False});continue
  for n in range(ref['line_start'],ref['line_end']+1):primary.setdefault(n,[]).append(x['id'])
heads=[]
for n,t in enumerate(lines,1):
 m=re.match(r'^\s*(\d{1,3})[）)]',t)
 if m:heads.append({'source_number':int(m.group(1)),'line':n,'title':t,'case_ids':primary.get(n,[])})
for h in heads:
 if len(h['case_ids'])!=1:errors.append({'heading_unmapped_or_multiple':h})
# Manually read uncased source, including provenance preface and all colophons.
ancillary=[]
for n,t in enumerate(lines,1):
 if t.strip() and n not in primary:
  kind='preface_and_book_title' if n<=10 else 'colophon' if n>=2329 else 'section_heading'
  ancillary.append({'line_start':n,'line_end':n,'kind':kind,'path':S,'sha256':digest,'quote':t,
    'evidence_note':'编辑源流/褒誉仅属编者自述，不作独立准确性认证。' if n==5 else '原书非独立案例材料照存。'})
expected_ancillary={2,4,5,6,9,10,37,433,434,1052,1053,1218,1238,1272,1340,1455,1520,1540,1609,1610,1669,1723,1843,1929,2092,2250,2329,2330,2331,2332}
if {x['line_start'] for x in ancillary}!=expected_ancillary:errors.append('非案例行段与人工核定清单不一致，须重读')
overlaps={str(n):v for n,v in primary.items() if len(v)>1}
if overlaps:errors.append({'unapproved_primary_overlaps':overlaps})
counts=Counter(x['source_number'] for x in heads)
report={'schema':'liuren-shao-source-coverage-v1','source':{'path':S,'sha256':digest,'line_count':len(lines)},
 'reading_state':'manual_full_source_read_and_boundary_audit','registry_count':len(records),'completeness':dict(Counter(x['completeness'] for x in records)),
 'regular_heading_count':len(heads),'manual_malformed_heading':{'source_number':151,'line':1541,'case_id':'BK26-SHAO-151'},
 'duplicate_source_numbers':{'141':['BK26-SHAO-141','BK26-SHAO-1411']},'source_numbers_absent':[177,218],
 'additional_unheaded_events':[{'case_id':'BK26-SHAO-1181','lines':[1205,1206],'borrowed_from':'BK26-SHAO-118'}, {'case_id':'BK26-SHAO-1271','lines':[1302,1303],'borrowed_from':'BK26-SHAO-127'}],
 'number_reconciliation':'220常规标题 + 1缺括号151 + 2未编号附案 = 223登记；常规标题内含重复141。原177/218确无文本题头，不补造。',
 'preface_declared_cases':216,'preface_count_note':'弁言自述所辑216例，当前本地重排文本末号222、重复及附案登记223；不把编辑计数强改成历史独立事件数。',
 'primary_case_covered_nonempty_lines':sum(bool(lines[n-1].strip()) for n in primary),'ancillary_covered_nonempty_lines':len(ancillary),'uncovered_nonempty_lines':[],
 'same_event_reoccupations':[['BK26-SHAO-196','BK26-SHAO-197'],['BK26-SHAO-201','BK26-SHAO-202']],
 'intra_case_pointer_audit':[{'line':1120,'note':'同日何子重指针已对应112，非又漏一案。'},{'line':126,'note':'又一人论为无署名异解，非另事件。'},{'line':1712,'note':'因病另论坟属同案子问。'}],
 'tail_general_discussion':{'line':2327,'retained_in':'BK26-SHAO-222','method_card':'LR26-BOOK-SHAO-222','author':'无单独署名附论，未强归邵氏'},
 'source_fragment_queue':[{'case_id':'BK26-SHAO-003','gap':'原文明示断语遗失、结果未载','reconstruction_action':'排盘不能恢复失去的断语；保持fragment，须其他书本或善本补文','complete':False}],
 'method_review_complete':False,'C_review_queue':'output/liuren-book-cases-20261102/shao-method-review-queue.json','independent_validation_count':0,
 'borrowed_dependencies':borrowed,'headings':heads,'ancillary_source_refs':ancillary,'errors':errors,'source_coverage_pass':not errors}
p=R/'output/liuren-book-cases-20261102/shao-full-source-coverage-audit.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:report[k] for k in ['registry_count','completeness','regular_heading_count','number_reconciliation','method_review_complete','source_coverage_pass','errors']},ensure_ascii=False))
