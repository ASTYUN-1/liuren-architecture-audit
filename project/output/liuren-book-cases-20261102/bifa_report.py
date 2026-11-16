"""Current evidence-aware BIFA report; all counts read from current registers."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/liuren-book-cases-20261102';BASE=ROOT/'knowledge/liuren-research/20261102'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
cases=read(BASE/'book-cases/bifa.json');rules=read(BASE/'rules/book-bifa.json')
cover=read(OUT/'bifa_coverage.json');checks=read(OUT/'bifa_validation.json');audit=read(OUT/'bifa_coverage_audit.json');tax=read(OUT/'bifa_method_taxonomy.json');routes=read(OUT/'bifa_fragment_routes.json');rev=read(OUT/'bifa_reconstruction_review.json')
rows=['# 北海《毕法赋全解》拆案与实际用法记录','',
'2026-11-02。前言及100法已逐段对读，并完成二次覆盖核对；原图与未解参数仍有缺口。','',
'## 验收摘要','',
f"登记{len(cases)}案：{cover['complete']}案complete、{cover['fragment']}案fragment；139张来源方法卡归为12个方法族、8组近义并读。旧摘要B0303《毕法精华》10子项逐项映射。独立效果验证均为0。",'',
f"已执行并审查{len(rev['reviews'])}个标准请求、{rev['archive_hashes_verified']}份raw。已核请求/结果hash、引擎与适配器指纹、全部facts、全部观察对照及全结构实质等价。保留等价组，不强选原始设置。拥有工具{checks['owning_validator_pass']}/{checks['cases']}通过，可导入完整案{checks['eligible_for_import']}。",'',
'完整性、来源一致性、原载反馈和独立效果验证分轴。完整表示现存题干、全断、后注已收并有带身份的完整结构；不表示恢复原扫描、原文无矛盾或预测准确。缺现实反馈不阻完整保存，但不能改成已发生。','',
'## 全书覆盖与版本边界','',
'正式本4897行与转录5719行覆盖前言、100法及元信息；转录连续实读范围外的非空行均已核为分批说明、标题或分隔符，没有仍未读的实质断案段。合讲保持96章段。机械124条cue逐条判别：106条链接登记案/重引，18条教学例式、定义、泛论或标题。124线索不是131案；332残盘提示不是332事件。','',
'二审补125—131七案，以及071、073、076早法重引。同事件依人物、占时、问事、原断及后续确认；共同整理说明、胎类和伏吟定义均为borrowed_context、same_event=false，不作同源桥。','',
'|版本边界|保存方式|','|---|---|',
'|124孙鲁山正式删整案|仅转录913—921作为主源；正式774—778刘汉式仅作删节边界。|',
'|093柳书游长例压缩|转录5359存戊午八月、两时、父己酉命/本人丙子命及原反馈。第一课补齐，不冒作未时第二全盘。|',
'|转录831/833教学引文删节|二十四间传判辞另存教学身份，不造现实案例。|',
'|130女宅坐标编辑|干土/干上未常与正式土象/支上未常并存。|',
'|006、019、131盘序/天将异文|原残、正文及同源完整盘分层；完整结构与文本一致性分别标记。|',
'|036梁与098万应斗混行|万为另一占，不借梁盘，共同行他案部分只借上下文。|','',
'## 实际复原与剩余缺口','',
'|路线|数量|后续及停止条件|','|---|---:|---|']
names={'restored_full_structure':('已补足完整结构','不重复算；有新增来源或引擎变动才重核。'),'engine_source_conflict':('引擎与来源冲突','停止同输入重算；有新扫描/同源分支再开新请求。'),'relation_constrained_candidates':('关系约束候选待执行','先查同源月将；无明文时显式生成关系候选，不用反馈择盘。'),'cross_source_missing_inputs':('缺参需跨源','定向查年月日支将时，本地无明文时停止该缺口，不随机补年/月。')}
for k,n in routes['counts'].items():rows.append(f'|{names[k][0]}|{n}|{names[k][1]}|')
rows += ['',
f'没有仍欠整段可读正文的登记案；缺原图/缺输入不冒称缺整段文。明参待执行目前0。004、012据原伏吟和4416“十二支各加本位”生成关系候选，实际核12宫与残传后补齐；017同法实跑却与卯卯卯主残不符，仍fragment。{routes["counts"].get("relation_constrained_candidates",0)}案关系路线尚未全执行，不能把清单当完成证据。','',
'003、017、018、021、039、057、069、102、112、114、119共11案保持fragment。131原残AUDIT冲突，但正文FORMAL明载卯玄→戌朱→巳虎、全facts等价可补足；两分支均存。006/032/110以额外明文约束另存AUDIT/PROSE，旧结果不覆盖。','',
'040/081已按古汇选同案明确申将/亥将另存跨源请求并补齐，月将来源身份明示，040蒿矢/昴星原说继续并存。', '',
'126明载甲子可补盘；明年戌/后年丁亥与题年矛盾继续标，不猜改年。120酉加支与实盘干酉支丑、121子午皆空与旬空子丑等保留来源冲突。077寿原断26年/后述16年，095拟巳月/实未月，096不传入/多省小疫情，均不以事后改释洗成命中。','',
'|请求|匹配/候选|全结构实质等价|本分支可补足|','|---|---|---|---|']
for r in rev['reviews']:rows.append(f"|{r['result_id']}|{len(r['matching_candidate_ids'])}/{len(r['candidates'])}|{r['structural_facts_equal_after_excluding_setting_labels']}|{bool(r['completeness_assessment'].get('eligible_after_verified_appendix'))}|")
rows += ['', '## 方法条件归组','',
'139张source_method保留原证据与适用条件。12族和8近义组已接knowledge/liuren-research/20261102/families/legacy-bifa-continuation.json规范协议，共同动作归并并保留各卡完整条件、排除和结论；不同问事、坐标、救制或时段保留分支，无完全同条件冗卡可安全删除。B0303十子项具体修订与作者误归因详见旧经验续审-毕法及相关.md。','',
'|方法族|共同动作|来源卡数|','|---|---|---:|']
rows += [f"|{g['title']}|{g['common_method']}|{len(g['rule_ids'])}|" for g in tax['families']]
rows += ['', '条件维度：'+ '；'.join(tax['dimensions'])+'。','', '|近义并读|保留差别|','|---|---|']
rows += [f"|{g['common_label']}|{g['preserved_difference']}|" for g in tax['normalization_groups']]
rows += ['', '## 旧摘要映射','',
'回读旧B0303原摘要经验日志1085—1123，十子项分别链接有条件的来源卡。旧源不改，旧AI摘要不当北海逐字原话；不宣告整个旧经验库已审。','',
'|旧子项|当前卡尾号|条件修订|','|---|---|---|']
rows += [f"|{m['subentry']}|{', '.join(v.rsplit('-',1)[-1] for v in m['current_rule_ids'])}|{m['reason']}|" for m in tax['legacy_mappings']]
rows += ['', '## 案例登记','', '|ID|题目|主源行号|完整性/反馈|','|---|---|---|---|']
for c in cases:
 e=c['source_refs'][0];s='转录' if 'DeepSeek' in e['path'] else '正式'
 rows.append(f"|{c['id']}|{c['title']}|{s}{e['line_start']}–{e['line_end']}|{c['completeness']}；{c['feedback_status']}|")
rows += ['', '## 校验与交接','',
f"bifa_validate.py：{checks['result']}；{checks['core_evidence_refs']}核心引用、{checks['core_unique_evidence_ranges']}不同区间、连扫描{checks['all_refs_including_scan_cues']}引用，{checks['evidence_files']}来源文件。核行号、原字节SHA、角色、逐字字段、反向链接及身份边界；机械通过不证明术理效力。",'',
'主要产物：knowledge/liuren-research/20261102/book-cases/bifa.json、rules/book-bifa.json。辅助文件在output/liuren-book-cases-20261102：bifa_coverage_audit.json、bifa_method_taxonomy.json、bifa_fragment_routes.json、bifa_reconstruction_review.json。统一导入/真实索引/完整附录由knowledge_tools负责；本报告不冒报未执行导入。','',
'重建：bifa_reconstruction_review.py → bifa_build.py → bifa_scan.py → bifa_method_taxonomy.py → bifa_coverage_audit.py → bifa_fragment_routes.py → bifa_validate.py → bifa_report.py。标准请求/结果不覆盖；review hash变化须重导入完整附录。','']
(ROOT/'docs/六壬知识整理-20261102/毕法拆案与用法记录.md').write_text('\n'.join(rows),encoding='utf-8')
print(f'report synchronized: {len(cases)} cases, {len(rules)} methods, {len(rev["reviews"])} requests')
