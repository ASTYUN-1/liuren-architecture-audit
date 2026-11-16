"""Catalog existing meanings without changing the active adoption policy."""
import csv
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent
audit = json.loads((OUT / '神煞清点.json').read_text('utf-8'))
pointer = json.loads((ROOT / '.opencode/liuren-active.json').read_text('utf-8-sig'))
assert pointer['release'] == audit['release']
refs = ROOT / pointer['runtime'] / 'references'
policy = json.loads((refs / 'shensha-policy.json').read_text('utf-8-sig'))
assert hashlib.sha256((refs / 'shensha-policy.json').read_bytes()).hexdigest() == audit['policy_sha256']

# Each name has one catalog home; actual traditional meanings may overlap.
categories = [
 ('医药与病势回转', '日医、返魂、天破', '日医：医药、医治；返魂：病势回转、复苏；天破：来源有病占吉用。三者不等同。'),
 ('孕产、小儿与病患', '浴盆、丧魄、天狗、天鬼、女灾、小煞', '浴盆：病患与胎产分用；天狗：孕产；女灾：传统阴人病患；小煞：小口灾。丧魄、天鬼另有各自病患条件。'),
 ('德解、救助与增吉', '天德、月德、天赦、天解、解神、仪神、福星', '德神助佑、恩赦、解散或消祸增吉；天解有月/日干两法。福星偏求望助益，并非狭义德解。'),
 ('学业、科名与授命文书', '皇书', '皇书有拜命、科名、功名及文书的来源义；不能泛指所有学习能力。'),
 ('官禄、名禄与命令批复', '天书、天诏、天恩、皇恩、天龙', '天书：官迁、财喜；天诏：命令、受恩；天恩/皇恩：庇护、诏命迁转；天龙：求名禄。'),
 ('财物、营求与家宅门户', '天财、圣心、大耗、岁宅、岁破、门煞', '求财、和合营求、耗损、破损重修及门户。岁宅与岁小耗有共表关系，须防新增重复项。'),
 ('信息、察探与行人阶段', '信神、信煞、天鸡、天耳、忧神、泰神、游神、戏神', '消息、远信、听闻、追查、消息虚实及行人未至/在途/将至；忧泰不能按字面直接分坏好。'),
 ('盗失、追捕与人物财物亡失', '游都、鲁都、天盗、时盗、日盗、天贼、亡神、月亡神、支亡、日亡神、天目', '盗贼来去、盗失与人或物亡失；天目有捕盗寻人之义。天盗、天贼跨基准须分法。'),
 ('婚合、人际与阴私隐情', '月合、阴奸、奸门、奸神、奸私、月厌', '月合偏成合；阴私类须有相应所问与组合；月厌有妨嫁娶及病、梦、盗等分支。'),
 ('官讼、刑禁与冤屈相负', '官符、月官符、管神、天刑、天狱、天吏、相负、枉屈', '官事词讼、拘束刑责、催办追呼；相负为辜负，枉屈为冤屈，也可用于契约与人际。'),
 ('出行、交通与行动阻滞', '四废、天车、天坑、飞符、五鬼、游祸', '行动受阻、功能受限、车辆行程及行动风险；飞符另有日德救、朱勾加重的分支。'),
 ('突发灾险、损伤与绳索', '岁煞、岁虎、劫煞、劫杀、灾煞、金神、红沙、大煞、丝麻煞、悬索、长绳、阴煞、阳煞', '灾险、财损物破、血光及绳索物象；阴阳煞另偏人物口舌，阴煞兼病患；大煞另有官用。'),
 ('火患', '火鬼、火烛煞', '火厄、身宅火患；保留并蛇雀、克日或克辰等条件。'),
 ('天时气象', '风煞、风伯、雨师、雷公、雷煞、天怪、晴朗煞', '风、雨、雷电、异常天象与晴朗；仍须神将、旺衰及天时结构。'),
 ('坟墓、覆蔽与昏晦', '岁墓、三丘、五墓、墓门、华盖、黄幡', '坟墓、墓地变动、覆蔽昏晦等；岁墓兼病讼宅灾。现有资料不足以把华盖泛化为才艺学业。'),
 ('神魂、梦寐与传统咒象', '迷惑煞、游魂、天咒', '思虑辨识受扰、神魂不定、梦寐及传统咒诅象；不是现代医学诊断或现实咒诅证据。'),
 ('统领、兵权与人物角色', '将军', '头目、领兵权者；亦用于行人占。不因人物权力象即认胜利或升迁。'),
]
relations = '岁刑、月刑、月害、贵人、日官、日鬼、支刑、支破、支冲、支害'.split('、')
index = {}
index_path = refs / 'shensha-engine-index.md'
for i, line in enumerate(index_path.read_text('utf-8').splitlines(), 1):
    if line.startswith('| '):
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) >= 4:
            index[cells[0]] = {'path': str(index_path.relative_to(ROOT)).replace('\\','/'), 'line_start': i, 'line_end': i, 'quote': line, 'sha256': hashlib.sha256(index_path.read_bytes()).hexdigest()}

mapping = {}
for cat, names, meaning in categories:
    for name in names.split('、'):
        assert name not in mapping, name
        mapping[name] = (cat, meaning)
assert len(mapping) == 99
unselected = [r for r in audit['rows'] if r['status'] != 'adopted_alias']
assert {r['name'] for r in unselected} == set(mapping) | set(relations) | set(policy['disabled'])
assert len(unselected) == 131
records = []
for r in unselected:
    name = r['name']
    if name in mapping:
        cat, meaning = mapping[name]
        state = '未登记，按现有释义记录分类；起法与作用条件仍须逐项复核'
    elif name in relations:
        cat, meaning = '关系或身份标签（另列）', '不应直接当作尚缺的独立神煞；须与现有天将、官鬼或刑冲破害关系层核对。贵人已有天将字段。'
        state = '未登记为神煞，不等于相关计算均未接入'
    else:
        cat, meaning = '定义、释义或字段映射待核（明确停用）', index[name]['quote'].split('|')[-2].strip()
        state = '明确停用；本轮不按近名或字面确定意向'
    records.append({'name': name, 'engine_groups': r['groups'], 'primary_category': cat, 'category_meaning': meaning, 'adoption_state': state, 'source_evidence': index[name]})

sources = ['shensha-engine-index.md', 'shensha-other-meanings.md', 'shensha-field-meanings.md']
result = {'schema':'liuren-unselected-meaning-catalog-v1','release':pointer['release'],'policy_sha256':audit['policy_sha256'],
 'counts':{'unselected_names':131,'classified_meaning_names':99,'relation_identity_labels':10,'disabled_unresolved_names':22},
 'scope':'现有释义记录的分类索引；非新增规则卡、非采用变更、非本轮全量原典校勘',
 'sources':[{'path':str((refs/f).relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256((refs/f).read_bytes()).hexdigest()} for f in sources],
 'limitations':['主类仅为整理入口，义项可能跨类；不可按分类直接判断吉凶。','名称未登记不等于独立术法缺失；共表、别名和不同基准仍须区分。','原引擎以外的地解、日解、天德合、月德合、会神等不混入本次131名。','本轮未完成全部原典校勘，没有预测效果验证。'], 'items':records}
(OUT/'未选用神煞意向分类.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
with (OUT/'未选用神煞意向分类.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['名称','原引擎基准组','主分类','该类意向及边界','当前状态','现有字段释义','来源文件','来源行'])
    for r in records:w.writerow([r['name'],'、'.join(r['engine_groups']),r['primary_category'],r['category_meaning'],r['adoption_state'],r['source_evidence']['quote'].split('|')[-2].strip(),r['source_evidence']['path'],r['source_evidence']['line_start']])
lines=['# 未选用神煞的意向分类','',f"活动版本：{pointer['release']}。核对日期：2026-11-09。",'',
 '按原引擎172个去重名称，剔除现行39条规则已覆盖的41个名称或别名，余131名。这里的“未选用”只指未进入神煞采用表，不把131名都视作独立待增补神煞。99名按现有释义归主类，10个关系/身份标签另列，22个定义不足项保持停用。', '',
 '关神已另行接入S33并从本表移除。本表其他项沿用现有释义记录，没有据分类新增规则或重新校勘全部原典。各类仅为核查入口，实际义项会交叉。', '',
 '| 意向主类 | 名称 | 现有释义与边界 |','|---|---|---|']
for cat,names,meaning in categories:lines.append(f'| {cat}（{len(names.split("、"))}名） | {names} | {meaning} |')
lines += ['', '注意：上一轮建议把华盖列入官禄文书类过宽。本轮按现有六壬来源的覆蔽、昏晦义归类，不套入八字艺术才学解释。皇书才有此处可核的科名义。', '',
 '关系或身份标签10名：'+'、'.join(relations)+'。贵人作为十二天将之一已在正式盘；官鬼及刑冲破害另核关系层，不将这些名称全部视为缺少计算。', '',
 '明确停用且本轮不强分意向的22名：'+'、'.join(policy['disabled'])+'。', '',
 '| 停用名称 | 当前缺口 |','|---|---|']
for name in policy['disabled']:lines.append('| '+name+' | '+index[name]['quote'].split('|')[-2].strip()+' |')
lines += ['', '增补核查时先区分这些情况：', '',
 '- 德解：天德、月德、天赦、天解、解神；仪神可参干奇消祸增吉，福星偏求望助益。解神也可能解散所求之喜事，不能一律定救。',
 '- 医药：日医是直接医药候选；返魂、天破偏病势或转归；浴盆等须按保胎/临产/病患分用。天医、地医已采用，故不重复列入。',
 '- 学业：此轮直接保留皇书的科名义；天书、天诏、皇恩等偏官禄、命令与批复，不能全部混成学习能力。文星、帘幕、旬奇、旬仪已采用。',
 '- 共表不一定需要新增一条证据：岁宅与岁小耗、天恩与皇恩、支亡与日亡神等，要核身份及重复；天解、天盗、天贼等同名跨基准要分列。',
 '- 待核项不凭名字定类：岁德不能直接套日德；天才不能并天财；飞镰不能并飞廉；天史不能并天吏；干胎神/支胎神不直接等同专项胎爻。', '',
 '来源入口：', '',
 *['- '+str((refs/f).relative_to(ROOT)).replace('\\','/') for f in sources], '',
 '同目录CSV含131名逐项分类、原分组、采用状态及字段释义来源行；JSON附源文件SHA256与连续原文行。所有分类均保留原名，不新增引擎之外的神煞。','']
(OUT/'未选用神煞意向分类.md').write_text('\n'.join(lines),'utf-8')
print(json.dumps(result['counts'],ensure_ascii=False))
