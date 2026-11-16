from pathlib import Path
import json, collections, hashlib
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
manifest=read(OUT/'case-manifest.json'); obs=read(OUT/'subjudgments.json'); segs=read(OUT/'author-segments.json')
rules=read(ROOT/'knowledge/liuren-research/20261102/rules/modern-pilot10.json')
families=read(ROOT/'knowledge/liuren-research/20261102/families/modern-pilot10.json')
comps=read(OUT/'substantive-comparisons.json'); validation=read(OUT/'overlay-validation.json')
summary=validation['summary']; sha=manifest[0]['source_refs'][0]['sha256']
def esc(s):return str(s).replace('|','\\|').replace('\n','<br>')
def span(o):
 r=o['evidence_refs'][0]
 return f'L{r["line_start"]}–{r["line_end"]}'
lines=['# 《当代壬占汇选》十例经验试提','',
 '本轮严格处理既有登记中的十个 complete 原案：031、042、044、073、074、075、077、082、087、096。未扩展案例批次。所有结果仍是历史文本中的原载反馈，不是本轮独立预测验证。','',
 f'已逐项处置 {len(obs)} 项判断，保存 {len(segs)} 个作者／阶段段落；新增 {len(rules)} 张具体来源分支卡、{len(families)} 个比较族。六组主题直接复用旧卡，没有为每项判断另造规则。定点比对既有 23 张卡、25 个旧经验单元和 4 个方法族；关键词召回候选不计作全文精读。','',
 'E1 的 430 卡、958 旧单元、38 族是试提前快照。此次附加后，工作台为 **461 规则卡＋31 审查卡＝492 条，43 族**；原 958 旧单元没有被覆盖。旧现代 105–107 三案复审完整保留，现代复审现为这三案加本十案。','',
 '新增的 31 张是可追溯的具体来源卡，不表示发现了 31 条普遍有效的新定律。未发现足以安全删并的完全同条件重复卡，等价合并和删除数均为 0。','',
 '## 来源与分层','',
 f'- 主源：`书籍库/现代著作/当代壬占汇选第五版.md`；SHA-256：`{sha}`。',
 '- 原载群断、复盘／后注、旧经验／旧AI、本轮解释分别记录。群断位于反馈前不等于已核原始发言时间；所有后注保留事后身份。',
 '- 这十个原案未见单列旧AI作答。相关旧经验中的 AI 候选和摘要保存在定点比较文件，不能当本案原断、原反馈或新增独立事件。旧经验标“验”不自动重新认证。',
 '- 病名、症状、病因、生死、阶段、人物、时间与数量按子判断及反馈范围处理；询问和泛论不按预测输赢统计。',
 '- 完整连续引文、行号、哈希在 JSON 中；本报告的链条是本轮忠实概括，不冒充作者逐字原话。没有明示理由的结论只存原话和处置，不补推理。','',
 '## 十案处置总表','',
 '| 案号／原题 | 判断项／新增卡 | 具体处置 |', '|---|---:|---|']
for c in manifest:
 cid=c['case_id']; its=[o for o in obs if o['case_id']==cid]; cr=[r for r in rules if cid in r['source_case_ids']]; comp=next(x for x in comps if x['case_id']==cid)
 lines.append(f'| {cid} {esc(c["title"])} | {len(its)}／{len(cr)} | {esc(comp["disposition"])} |')
lines+=['','## 逐作者、逐子判断','',
 '“原载支持”只支持所列子问；同一项含部分符合及未覆盖处时，详看反馈说明。这里只列可核对的局部反馈，不计算作者命中率。','']
for c in manifest:
 cid=c['case_id']; its=[o for o in obs if o['case_id']==cid]; comp=next(x for x in comps if x['case_id']==cid)
 lines += [f'### {cid}　{c["title"]}','',f'原案身份：`{c["source_case_identity"]}`。','',
  '| 作者／阶段／行号 | 分项判断 | 原文明示的判断链 | 原载反馈覆盖与处置 |', '|---|---|---|---|']
 for o in its:
  chain=' → '.join(o['reasoning_steps']) if o['reasoning_steps'] else '原文无明确理由，不补链'
  link='、'.join(o['rule_ids']) if o['rule_ids'] else '无新增规则'
  lines.append('| '+ ' | '.join(map(esc,[o['author']+'／'+o['phase']+'／'+span(o),o['axis']+'：'+o['judgment'],chain,o['feedback_state']+'：'+o['feedback_note']+'；'+link]))+' |')
 lines+=['', '**与旧知识的实质比较**','',f'已比：卡 `{ "、".join(comp["compared_rule_ids"]) }`；旧单元 `{ "、".join(comp["compared_legacy_entry_ids"]) }`；族 `{ "、".join(comp["compared_family_ids"]) }`。','',comp['common_action'], '',comp['material_difference'],'',f'处置：{comp["disposition"]}','']
lines+=['## 保留的方法分歧与缺口','',
 '- 031：陆长青干为父母、沐尘干为孩子；小区找到不能裁坐标。原午时与三点多不合，后注丑上申和亥四数不冒作事前命中；亥四小时缺计时起点。',
 '- 042：换单位部分对应不等原问方最终能合作；假合同、被迫、内部审查不通过未获证。',
 '- 044：女主动约见不等已复合；拒绝方实际为男冷处理，不能只看“未合好”便认证女不同意。',
 '- 073：胃病反复和胃炎可逐项参照，癌亡强断受本次好转反证；理财压力是原载对话，不能直接确认为医学因果。',
 '- 074：2025-01-01前未调是原问结局；事后蛇年、丑行年和辛巳改期无新跟访。',
 '- 075：青山干男支女与雨田按年命反置干女支男有实质冲突；双方都解释婉拒不证明可任意换位。',
 '- 077：出院反驳死向；不验证“无亥就死”的反事实。明镜遥克轻与明天金箭近射重的力度解释仍不同。',
 '- 082：月建填／不填两说均能解释免罚，暂不裁决；领导出现、喝酒事实、欲罚与实际处分分开。',
 '- 087：原盘伏吟且三传丑戌未，江山后注说“丑加未、未加丑”与空间互加坐标待核，不改盘补格；原560多／580多、560和460均不等616／589。600多是后改。',
 '- 096：得部分答案、考试通过、当次难、未来考过及岗位愿望分别保存；肖遥只填一处为反馈后的修订，不能倒填原可过判断。','',
 '这些缺口已经登记并处理，不要求补脑后才能保留原法。试提完成不等于这些方法问题已解决。','',
 '## 机械校验与检索','',
 f'- 工作台动态校验：mechanical_valid={summary["mechanical_valid"]}；可检索 {summary["eligible_count"]}／{summary["record_count"]} 条；issues={len(validation["issues"])}；族 {summary["explicit_rule_family_count"]}。',
 '- 校验只证明证据定位、原字节哈希和数据关系有效；语义归纳是本轮审读声明。独立效果验证仍为 **0**，全项目 complete 仍为 **false**。',
 '- 实际旧入口检索结果和本批自检见同目录 `final-check.json`；检索相关性不代表准确率。','',
 '## 交付位置','',
 '- `knowledge/liuren-research/20261102/rules/modern-pilot10.json`：31张来源卡。',
 '- `knowledge/liuren-research/20261102/families/modern-pilot10.json`：5个带旧族入口的比较族。',
 '- `knowledge/liuren-research/20261102/method-reviews/modern.json`：保留旧三案，追加十案156项。',
 '- `output/liuren-modern-pilot10-20261102/author-segments.json`、`subjudgments.json`：作者原句和细分判断。',
 '- 同目录 `case-manifest.json`、`targeted-search.json`、`substantive-comparisons.json`：固定清单、召回及实质比对证据。',
 '- 同目录 `final-check.json`、`overlay-validation.json`、`search-*.json`：验证与实际检索记录。','',
 '本批到十例为止；不继续扩批。']
report=ROOT/'docs/六壬知识整理-20261102/当代汇选十例经验试提.md'
report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'report':str(report),'characters':report.stat().st_size},ensure_ascii=False))
