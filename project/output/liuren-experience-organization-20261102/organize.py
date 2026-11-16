"""Bounded inventory of existing experience only. No new source extraction.
Rebuild: python -X utf8 output/liuren-experience-organization-20261102/organize.py
"""
import collections,hashlib,json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
import experience_retrieval as er
import liuren_knowledge_workbench as wb
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def dump(p,o):(ROOT/p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def ref(p,a,b,role='原载作答'):
 raw=(ROOT/p).read_bytes();ls=raw.decode('utf-8-sig').splitlines()
 return dict(path=p,line_start=a,line_end=b,quote='\n'.join(ls[a-1:b]),sha256=hashlib.sha256(raw).hexdigest(),role=role)
base='knowledge/liuren-research/20261102/'
records,errors=wb.load_records(ROOT);assert not errors
rules=[r for r in records if r['schema']=='liuren-rule-card-v1']
audits=[r for r in records if r['schema']=='liuren-audit-v1']
byid={r['id']:r for r in records}
# Only the already reviewed five modern entries and one existing source card.
legacyids=['H0027','H0028','H0034','H0035','H0036']
ruleids=['LR26-LEGACY-006','LR26-LEGACY-007','LR26-LEGACY-008','LR26-BOOK-BIFA-127']
ev=[ref('案例项目库/考试占/case-001-丁卯日教资过关.md',31,40),ref('案例项目库/考试占/case-001-丁卯日教资过关.md',81,87),ref('案例项目库/考试占/case-002-己巳日教资过关.md',32,41),ref('案例项目库/考试占/case-002-己巳日教资过关.md',68,74),ref('案例项目库/考试占/case-008-乙丑日反吟offer.md',32,54),ref('案例项目库/考试占/case-009-己未日反吟考不行.md',31,53),ref('案例项目库/考试占/case-010-癸丑日考研考上.md',31,53),ref('书籍库/北海闲人/毕法赋全解-正式整理本.md',493,505,'原书断语')]
branches=[
 dict(id='A1',rule_id=ruleids[0],legacy_entry_ids=['H0027'],target='教资通过',conditions='原断行年朱雀且课传见丑未；原载癸卯年丁卯日、戌亥空。',feedback='原载过关；无成绩排名。',evidence_indices=[0,1]),
 dict(id='A2',rule_id=ruleids[0],legacy_entry_ids=['H0028'],target='教资通过',conditions='课中丑未相加不空，原作者不拘朱雀；原载癸卯年己巳日。',feedback='原载过关；年命未知。',evidence_indices=[2,3]),
 dict(id='B1',rule_id=ruleids[1],legacy_entry_ids=['H0034'],target='求职offer及入职',conditions='丑未不空，兼本命上神见禄；朱雀及三传空。',feedback='4号offer，11号戌日入职；两种成功标准不可共用应期。',evidence_indices=[4]),
 dict(id='B2',rule_id=ruleids[1],legacy_entry_ids=['H0035'],target='考试发挥',conditions='丑空兼朱雀不佳，原载己未日。',feedback='只说考得不行，不能改成明确落榜。',evidence_indices=[5]),
 dict(id='C1',rule_id=ruleids[2],legacy_entry_ids=['H0036'],target='考研录取',conditions='丑未相加且在课传、朱雀遁丁，原载寅卯空，年命未知。',feedback='只说考上；无分数及过程。',evidence_indices=[6]),
 dict(id='D1',rule_id=ruleids[3],legacy_entry_ids=[],target='北海考试斗鬼法及其修正',conditions='原法丑未互加作年命日干；作者称两三次不中，再提似乎限丑未年日。',feedback='两三次为未给全案的作者概述，不造新增案例或频数验证。',evidence_indices=[7]),
]
decisions=[
 dict(pair=['A1','D1'],decision='术语解释可归并',reason='两原文均明说丑中斗、未中鬼，斗鬼合魁；只统一符号解释，课传见两支与互加所处位置仍须分别核。'),
 dict(pair=['A1','A2'],decision='同族条件分支，不删除卡',reason='A1并行年朱雀，A2原作者不拘朱雀而突出不空；没有同条件对照证明两前提可以互删。'),
 dict(pair=['A2','B1'],decision='目标不同，不合并成同一成败规则',reason='教资通过与取得职位不同；B1多本命禄及通知/入职两阶段，不能以同见丑未抵消差异。'),
 dict(pair=['B1','B2'],decision='保留对照，不能证明空亡唯一决定',reason='考试性质、时间、年命及朱雀条件一起变化，不是只改变空亡的实验；考不行也未说明是否落榜。'),
 dict(pair=['A2','C1'],decision='同族条件分支',reason='C1额外要求入课传和朱雀遁丁；录取反馈不验证AI另加的稼穑必应考研。'),
 dict(pair=['A1','D1'],decision='年日限制主张有张力，暂不合并',reason='A1、A2原载癸卯年丁卯/己巳日过关，与D1若被写成丑未年日必要条件不相容；D1原语只是似乎假说，未详失败案，不能裁成已经证伪或普遍规律。'),
 dict(pair=['B2','D1'],decision='空的对象和方法须保留',reason='D1同段另列德入天门虽空仍中，这是另一成立结构；不能据此取消B2的丑空条件，也不能推出所有空吉神都无妨。'),
]
fid='LF26-E1-CHOUWEI-EXAM'
family=dict(id=fid,title='丑未考试与求职：旧新条件及反证比较',rule_ids=ruleids,legacy_entry_ids=legacyids,merge_type='共同术语归并，适用条件及反证分支保持',common_method='共同术语为丑斗、未鬼合魁；先核两支是否相加及落于干支/课传/年命的坐标，再分考试通过、发挥、录取、offer和入职，核空实与原作者并用条件。只归并符号解释及比较步骤，不统一预测充分必要条件。',preserved_branches=branches,unresolved=[d['reason'] for d in decisions if d['decision']!='术语解释可归并']+['五现代原载后述不是独立核验；北海两三次失败未给完整案例。','原档天将及本命上神歧义沿既有审查保留，本批未重排盘。'],source_refs=ev,comparison_decisions=decisions,independent_validation_count=0,does_not_replace_family_ids=['LF26-LEGACY-CHOUWEI'])
familyfile=base+'families/experience-organization.json';dump(familyfile,[family])
comparison=dict(schema='liuren-existing-method-comparison-v1',review_state='source_checked',scope='仅已审H0027/H0028/H0034/H0035/H0036与四张现有卡；不新增预测规则/案例，不审其他旧条目。',source_refs=ev,branches=branches,decisions=decisions,family_id=fid,new_rule_count=0,new_audit_count=0,independent_validation_count=0)
dump('output/liuren-experience-organization-20261102/semantic-comparison.json',comparison)
# Reuse existing source-backed granularity, without rewriting its tags or cache.
index=er.build_index(ROOT);entries=index['entries']
v=wb.validated_records(ROOT);assert v['summary']['mechanical_valid'] and not v['issues'],v['issues']
families=v['families']
catalog=read('docs/经验库梳理/20261019/data/catalog.json')
oldids={e['id'] for e in entries};assert oldids=={e['id'] for e in catalog['entries']}|{e['id'] for e in entries if e['id'].startswith('U-')}
# Keyword tags describe literal evidence only. They never declare semantic reading.
logic={
 '取用与角色':['类神','取用','角色','干为','支为','日干','本命'],
 '结构与课体':['四课','三传','课体','反吟','返吟','伏吟','相加','格局'],
 '生克与施受':['生克','递生','递克','克干','生干','脱干','夹克'],
 '空实与效力':['空亡','旬空','落空','填实','填空','天空'],
 '旺衰与时令':['旺衰','旺相','休囚','月令','月建','死气'],
 '墓绝与终止':['墓','绝地','德丧','源消根断'],
 '救制与反制':['救神','制鬼','救制','化煞','有救','反制'],
 '神将与并聚':['朱雀','白虎','青龙','贵人','六合','腾蛇','神煞','并聚'],
 '年命与个人定位':['行年','本命','年命'],
 '动静与路径':['动静','出行','进退','驿马','丁马','归支'],
 '应期与尺度':['应期','迟速','填实','年月','月日','期限'],
 '数量与精度':['取数','金额','数理','数量','先天数','河图','洛书'],
 '阶段与分项':['阶段','分项','子问','过程','通知','入职','部分验'],
 '取舍与反证':['取舍','反证','例外','不能一律','权重','优先','不一定'],
 '来源与归因':['原断','愚按','事后','归因','同源','误','反馈'],
}
catwords={'事业占':['工作','求职','升职','官职','仕途'],'学业占':['考试','考研','教资','录取','会试'],'财运占':['求财','买卖','生意','讨薪','欠薪'],'健康占':['疾病','病情','手术','住院'],'感情占':['婚姻','恋爱','分手','夫妻'],'胎产占':['胎产','怀孕','六甲','生产'],'家宅占':['家宅','住宅','坟墓'],'失物占':['失物','丢失','寻狗','失狗'],'出行占':['行人','出行','赴任'],'官讼占':['官讼','诉讼','官司','刑期'],'天时占':['天时','降雨','天气'],'射覆':['射覆'],'推命':['推命','终身'],'来意':['来意']}
aliases={'交易占':'财运占','考试占':'学业占','疾病占':'健康占','行人占':'出行占','胎产':'胎产占','推命占':'推命','射覆占':'射覆','杂事占':'杂事','来意占':'来意'}
def tags(fields,vocabulary):
 out=[]
 for label,words in vocabulary.items():
  hits=[]
  for field,text in fields.items():
   term=next((w for w in words if w in text),None)
   if term:
    pos=text.index(term);hits.append(dict(field=field,matched_term=term,context=text[max(0,pos-22):pos+len(term)+30]))
  if hits:out.append(dict(label=label,state='keyword_candidate_not_semantically_reviewed',evidence=hits[:2]))
 return out
case_records=[c for p in sorted((ROOT/base/'book-cases').glob('*.json')) for c in json.loads(p.read_text(encoding='utf-8'))]
case_map={c['id']:c for c in case_records}
identity_map={i:c for c in case_records for i in [c['source_case_identity']]+c.get('additional_source_case_identities',[])}
def case_links(ids):
 links=[]
 for x in dict.fromkeys(ids):
  c=case_map.get(x) or identity_map.get(x)
  if c:links.append(dict(identity=x,state='registered_book_case',case_id=c['id'],completeness=c['completeness'],method_review=c.get('method_extraction_review',{})))
  elif x.startswith('案例项目库/') and (ROOT/x).is_file():links.append(dict(identity=x,state='existing_case_file_no_new_case_review'))
  else:links.append(dict(identity=x,state='reference_identity_not_resolved_in_this_inventory'))
 return links
mapped=[]
for kind,items in [('legacy',entries),('rule',rules)]:
 for x in items:
  rid=x['id'];isrule=kind=='rule';isfragment=rid.startswith('U-')
  reviews=[a for a in audits if rid in a.get('target_entry_ids',[]) or rid in a.get('replacement_rule_ids',[])]
  linked_rules=[r['id'] for r in rules if rid in r.get('legacy_entry_ids',[])]
  declared={k:x[k] for k in ['categories','method_tags','method_families','logic_stages','kind','verification','annotation_status','status','review_state','claim_origin'] if k in x}
  fields={'title':x['title'],'conditions':'；'.join(x['conditions']),'conclusion':x['conclusion'],'exclusions':'；'.join(x['exclusions'])} if isrule else {'title':x['title'],'summary':x['summary'],'source_excerpt':x['source_excerpt']}
  refs=x['evidence_refs'] if isrule else [dict(path=x['source'],line_start=x['line_start'],line_end=x['line_end'],sha256=x['source_sha256'],quote_sha256=hashlib.sha256(x['source_excerpt'].encode()).hexdigest())]
  fams=[dict(id=f['id'],title=f['title'],merge_type=f['merge_type']) for f in families if rid in f['rule_ids'] or rid in f['legacy_entry_ids']]
  links=case_links(x.get('support_case_ids',[])+x.get('counterexample_case_ids',[]) if isrule else x.get('case_refs',[]))
  mapped.append(dict(id=rid,unit_kind='existing_rule' if isrule else 'automatic_source_fragment' if isfragment else 'historical_curated_entry',title=x['title'],record_file=x.get('_record_file') if isrule else 'docs/经验库梳理/20261019/data/catalog.json' if not isfragment else 'experience_retrieval.build_index',source_refs=[{k:e[k] for k in ['path','line_start','line_end','sha256','role','quote_sha256'] if k in e} for e in refs],original_classification=declared,original_classification_provenance='现有规则卡标签，非本批重新审读' if isrule else '既有动态分段器候选标签，未语义核实' if isfragment else '历史目录原有标签，本批不据其推定精读',normalized_existing_categories=sorted({aliases.get(c,c) for c in x.get('categories',[])}),candidate_categories=tags(fields,catwords),candidate_logic=tags(fields,logic),five_status_axes=dict(case_registration=dict(state='linked_identity_inventory_only',links=links),method_extraction=dict(state='existing_rule_'+x['status'] if isrule else 'raw_fragment_not_extracted' if isfragment else 'historical_annotation_not_reextracted',linked_rule_ids=linked_rules),classification=dict(state='mapped_original_tags_preserved',candidate_tag_state='automatic_literal_match_not_reading'),semantic_review=dict(state='existing_rule_source_checked_declaration' if isrule else 'existing_scoped_audit_link' if reviews else 'no_existing_scoped_audit',audit_scopes=[dict(id=a['id'],action_scope=a.get('action_scope',a['finding']),disposition=a['disposition']) for a in reviews],covers_all_claims=False),rule_merge=dict(state='explicit_family_membership' if fams else 'no_verified_family_membership',families=fams,no_new_equivalence_inferred=True)),legacy_relations=[r for r in index['relations'] if rid in r['members']] if not isrule else x['relations'],independent_validation_count=0))
semantic_path='output/liuren-modern-102-20261102/semantic-classification.json'
semantic_rows=read(semantic_path) if (ROOT/semantic_path).exists() else []
semantic_by_id={x['id']:x for x in semantic_rows}
for item in mapped:
 if item['id'] in semantic_by_id:
  semantic=semantic_by_id[item['id']]
  item['e3_manual_semantic_classification']=semantic
  item['five_status_axes']['classification']['manual_semantic_scope']=semantic['review_scope']
  item['five_status_axes']['classification']['manual_axes_source']='逐作者判断轴及逐卡条件比较，非词匹配'
assert len(mapped)==len(entries)+len(rules) and len({x['id'] for x in mapped})==len(mapped)
dump('output/liuren-experience-organization-20261102/classification.json',mapped)
with (OUT/'classification.jsonl').open('w',encoding='utf-8') as f:
 for x in mapped:f.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
inputs=['docs/经验库梳理/20261019/data/catalog.json',familyfile,'output/liuren-experience-organization-20261102/organize.py']+sorted({r['_record_file'] for r in records})+[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/base/'families').glob('*.json'))]+[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/base/'book-cases').glob('*.json'))]+sorted({e['source'] for e in entries})
if semantic_rows:inputs.append(semantic_path)
reviewed={x for a in audits for x in a['target_entry_ids']}
stats=dict(legacy_index=index['status'],existing_rule_count=len(rules),rule_status_counts=dict(collections.Counter(r['status'] for r in rules)),audit_cards=len(audits),legacy_ids_with_scoped_audit=len(reviewed),curated_ids_with_scoped_audit=len(reviewed&{e['id'] for e in entries if not e['id'].startswith('U-')}),fragment_ids_with_scoped_audit=len(reviewed&{e['id'] for e in entries if e['id'].startswith('U-')}),legacy_units_without_scoped_audit=len(entries)-len(reviewed),mapped_units=len(mapped),mapped_legacy_ids=len(entries),mapped_rule_ids=len(rules),existing_family_count_before=len(families)-1,explicit_family_count_after=len(families),book_case_registration_count=len(case_records),book_case_completeness=dict(collections.Counter(c['completeness'] for c in case_records)),logic_candidate_counts=dict(collections.Counter(t['label'] for x in mapped for t in x['candidate_logic'])),no_logic_keyword_match=sum(not x['candidate_logic'] for x in mapped),new_predictive_rules=0,new_audits=0,new_source_cases=0,independent_validation_count=0)
manifest=dict(schema='liuren-existing-experience-organization-v1',scope=f'只分类当前{len(entries)}旧单元及{len(rules)}规则；候选标签不冒充精读，语义审查仍限原卡子判断。',input_sha256={p:sha(p) for p in sorted(set(inputs))},source_index_fingerprint=index['fingerprint'],counts=stats,logic_vocabulary=logic,category_keyword_vocabulary=catwords,category_aliases=aliases,classification_reading_semantics='已有标签原样继承；规范类别仅显式字面别名映射。关键词标签为候选，不赋予source_checked。',stage_axes=['case_registration','method_extraction','classification','semantic_review','rule_merge'],fresh_semantic_comparison=dict(family_id=fid,old_ids=legacyids,rule_ids=ruleids,branch_count=len(branches),decision_count=len(decisions)),initial_commands=dict(status='E1历史初始：exit 0:958=808+150,430 rules,31 audits,37 families,25 linked old IDs',validate='E1历史初始：exit 0:461/461 pass,0 blocked'),historical_e1_snapshot=dict(date='2026-11-02 E1完成时',legacy_units=958,rules=430,mapped_units=1388,families=38),rebuild_note='2026-11-02 E2十例后仅重建派生分类清单，包含E2已提取新卡；分类词表和E1实质比较未增加。',after_validation=v['summary'])
manifest['rebuild_note']='2026-11-02 E3固定102案后同步。E1字面候选字段与历史快照保留；另接E3人工判断轴、条件比较范围及规范入口路由，未将其余958旧单元冒称精读。'
manifest['e3_manual_semantic_mapping']=dict(path=semantic_path,count=len(semantic_rows),mapped_count=sum('e3_manual_semantic_classification' in x for x in mapped),scope='仅E3源卡、共同操作入口及明确比较的现有卡；不覆盖全部旧单元。',canonical_operations_are_not_predictive_laws=True)
dump('output/liuren-experience-organization-20261102/manifest.json',manifest)
search_result=wb.search(dict(records=records,validation=dict(records=[dict(id=r['id'],eligible_for_search=True) for r in records]),families=families),'丑未',30)
assert any(any(f['id']==fid for f in r['rule_families']) for r in search_result['results'])
compact_search=dict(query='丑未',result_ids=[r['id'] for r in search_result['results']],new_family_visible_on_ids=[r['id'] for r in search_result['results'] if any(f['id']==fid for f in r['rule_families'])],family=fid,ranking_is_not_accuracy=True)
dump('output/liuren-experience-organization-20261102/search-check.json',compact_search)
# Check exact coverage, deterministic tag evidence, source locations, and theme quotes.
for e in entries:
 raw=(ROOT/e['source']).read_bytes();ls=raw.decode('utf-8-sig').splitlines()
 assert hashlib.sha256(raw).hexdigest()==e['source_sha256']
 assert '\n'.join(ls[e['line_start']-1:e['line_end']])==e['source_excerpt']
for e in ev:
 raw=(ROOT/e['path']).read_bytes();ls=raw.decode('utf-8-sig').splitlines();assert sha(e['path'])==e['sha256'] and '\n'.join(ls[e['line_start']-1:e['line_end']])==e['quote']
validation=dict(result='PASS',mapping_count=len(mapped),legacy_id_coverage=f'{len(entries)}/{len(entries)}',historical_catalog_id_coverage=f'{index["status"]["curated_entries"]}/{index["status"]["curated_entries"]}',fragment_id_coverage=f'{index["status"]["unreviewed_fragments"]}/{index["status"]["unreviewed_fragments"]}',rule_id_coverage=f'{len(rules)}/{len(rules)}',missing_ids=[],duplicate_ids=[],legacy_current_source_checks=len(entries),theme_exact_refs_checked=len(ev),owning_overlay_validation=v['summary'],new_family_retrievable=bool(compact_search['new_family_visible_on_ids']),new_predictive_rules=0,independent_validation_count=0)
dump('output/liuren-experience-organization-20261102/validation.json',validation)
lines=['# 已有经验统一整理','', '2026-11-02 E3固定102案后的派生同步。原标签、E1关键词候选和历史快照保留；E3逐作者判断轴、条件比较范围及规范入口另列为人工语义分类，不把未比较的旧条目算精读。','',
 '历史E1完成快照：958旧单元、430规则、1388逐ID映射、38族；其中原初37族，E1增加1个跨旧新比较族。该历史口径不代表E2后当前总量。','',
 f'当前旧经验检索单元{len(entries)}个：{index["status"]["curated_entries"]}历史整理条目、{index["status"]["unreviewed_fragments"]}新增/变更原文自动片段，来自{index["status"]["source_files"]}文件。另有{len(rules)}张现有规则。已完成{len(mapped)}个逐ID映射，原标签不覆盖，自动占类与判断逻辑标签单列为候选。','',
 f'当前规则状态：'+ '、'.join(f'{n}张{state}' for state,n in stats['rule_status_counts'].items())+f'；沿用原卡，未擅改。既有审查{len(audits)}张，关联{len(reviewed)}个不同旧ID；关联只说明明示子判断已审，不说明该条全部主张已复审。其余{len(entries)-len(reviewed)}个旧单元无已核审查关联。当前工作台{v["summary"]["eligible_count"]}/{v["summary"]["record_count"]}记录机械通过、{len(v["issues"])}阻断或缺口，显式族{len(families)}个。候选规则和source_method都不等于预测有效。','',
 '## 五种状态分开','', '|状态|本清单记录|不作的推断|','|---|---|---|',
 '|案例登记|旧case_refs、现有规则支持案例的登记ID/完整性或未解析身份|案例入库不表示方法已提取|',
 f'|方法提取|{index["status"]["curated_entries"]}历史批注、{index["status"]["unreviewed_fragments"]}未提取片段、{len(rules)}现有规则状态及关联|分类不生成新方法卡|',
 '|分类|保留原categories/method_tags/method_families/logic_stages；字面规范别名和候选关键词分栏|自动标签不计精读，不覆盖原标签|',
 '|语义复审|原审查ID、action_scope与处置；现有规则source_checked声明|25个关联ID不等于25条所有内容审完|',
 '|规则归并|显式族成员、原关系与本批7项比较决定|同名、同格、同结论不自动判等价或同源|','',
 '## 实质比较：丑未考试与求职','',
 '只复核已审H0027/H0028/H0034/H0035/H0036及LR26-LEGACY-006/007/008，与LR26-BOOK-BIFA-127比较。未新增预测规则、审查卡或案例。共同的“丑斗、未鬼合魁”符号解释可以归并；成立位置、空实、并用条件和成功标准保持分支。','',
 '|分支|目标|原载条件|反馈范围|','|---|---|---|---|']
lines += [f"|{b['id']}|{b['target']}|{b['conditions']}|{b['feedback']}|" for b in branches]
lines += ['', '|比较|处置|理由|','|---|---|---|']+[f"|{'/'.join(d['pair'])}|{d['decision']}|{d['reason']}|" for d in decisions]
if semantic_rows:
 lines += ['', '## E3人工语义分类同步','',f'{len(semantic_rows)}个明确ID具有E3人工语义映射，范围见`{semantic_path}`。共同操作入口有条件、执行步骤和逐卡差异；预测公式未认整卡等价，源卡完整保留。其余旧经验仍沿原有状态，自动候选标签不提升为已审。','']
lines += ['', 'A1、A2原载癸卯年丁卯/己巳日过关，为北海“似乎只限丑未年日”假说提供需要解释的张力；未独立核现实考试结果，北海失败例也未详全案，不能据此宣布任何普遍定律。朱雀遁丁飞扬与考后朱雀乘丁马的条件、时点不同，不能仅按丁雀二字正反抵消。','',
 '## 文件与重建','',
 '- 完整清单：[classification.json](../../output/liuren-experience-organization-20261102/classification.json)，另有一行一ID的classification.jsonl。',
 '- 口径、词表、输入哈希：[manifest.json](../../output/liuren-experience-organization-20261102/manifest.json)。',
 '- 连续引文与7项比较：[semantic-comparison.json](../../output/liuren-experience-organization-20261102/semantic-comparison.json)。',
 '- 规范族：[experience-organization.json](../../knowledge/liuren-research/20261102/families/experience-organization.json)。现有search-experience/工作台动态检索可见，旧族和原卡不改。',
 '- 校验：[validation.json](../../output/liuren-experience-organization-20261102/validation.json)；检索证据：[search-check.json](../../output/liuren-experience-organization-20261102/search-check.json)。','',
 '```powershell','python -X utf8 output/liuren-experience-organization-20261102/organize.py','python -X utf8 tools/search-experience.py --query "丑未" --limit 5','```','',
 '重建复用experience_retrieval原分段和workbench原校验/检索协议；逐ID覆盖、当前连续原文/哈希与主题引文均核对。关键词候选记录命中字段、字词和上下文，没有把程序切段或检索结果标为精读。','',
 f'{len(logic)}类逻辑候选支持交叉定位，{stats["no_logic_keyword_match"]}个单元未命中逻辑词，保持待分类。{len(reviewed)}个有审查关联的旧ID中，{stats["curated_ids_with_scoped_audit"]}个属历史条目、{stats["fragment_ids_with_scoped_audit"]}个属片段。现有{len(case_records)}书中案例登记（{stats["book_case_completeness"].get("complete",0)}完整、{stats["book_case_completeness"].get("fragment",0)}片段）仅作为状态映射背景，不计作本批新增案例或提炼量。', '',
 f'分类重建不表示已逐条语义复审{len(entries)}个旧单元或{len(rules)}规则；E2十例的方法提取另见《当代汇选十例经验试提》。本次未补未登记案例、未重排盘、未验证预测效果，未处理其他主题的同条件去重。未知分类可留待分类；无关键词命中不表示没有该方法。原书、旧条目和现有规则未覆盖。','']
(ROOT/'docs/六壬知识整理-20261102/已有经验统一整理.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(dict(result='PASS',mapped=len(mapped),curated=index['status']['curated_entries'],fragments=index['status']['unreviewed_fragments'],rules=len(rules),audited_old_ids=len(reviewed),families=len(families),new_family_visible_on_ids=compact_search['new_family_visible_on_ids'],logic_unmatched=stats['no_logic_keyword_match']),ensure_ascii=False))
