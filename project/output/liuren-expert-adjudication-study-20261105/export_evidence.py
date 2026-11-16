"""Export the deliberately selected passages inspected in this study.

This records local textual evidence, not independent prediction validation.
"""
from pathlib import Path
import json
from read_sources import passage

HERE = Path(__file__).resolve().parent
SELECTED = [
    ('T01','BHT',6,51,'北海讲义：明占类、定侧重、看显象'),
    ('T02','BHL',265,315,'北海理法：气势、类聚与课体切题范围'),
    ('T03','BHL',510,518,'北海理法：多类分取及神煞变质例外'),
    ('T04','BHL',570,587,'北海理法：多现取舍、质与情势'),
    ('T05','BHL',697,708,'北海对壬归通类、分类宾主的明确异议'),
    ('T06','RG',355,389,'壬归：文书之财、取与、气态、阴神与通路'),
    ('T07','RG',417,421,'壬归：发用、中传、末传与年命'),
    ('T08','TY',4235,4251,'笔记水论：入手气势，未构成统一力量算法'),
    ('T09','BHL',597,619,'北海对指南请缨案的多方面类神分论'),
    ('E01','BHT',70,81,'单位分房：类神空而得气得生，得房与不满意分论'),
    ('E02','BHT',463,469,'返吟求职：禄发用、进气、与干上合，取成'),
    ('E03','BHT',477,482,'无禄长生的应聘：具体官印贵关系支持成'),
    ('E04','BHT',109,116,'是否已孕与随后流产分论'),
    ('E05','BHQA',198,217,'马康庄入相：表面官龙吉象让位于具体败退结构'),
    ('E06','ZNZ',1650,1658,'宋太斗：原断升迁且不久任'),
    ('E06C','BHQA',287,307,'宋太斗：北海答与又按对不久任归因不同'),
    ('E07','DA',349,357,'伊伯廷占宅：长生空，救应链不能完成'),
    ('E08','DA',435,442,'应贡元：魁杜、退茹不按阻隔，辨具体吉格组合'),
    ('E09','DA',444,454,'何秀才父子：同课人物分断与后人析义'),
    ('E10','DA',2277,2286,'潘道士住持：目下成与后来坏分论'),
    ('E11','TY',1601,1623,'子白借款：说借与实借分开'),
    ('E12','TY',1752,1782,'水断美容合作：难成与试用后的未合作反馈'),
    ('E13','TY',3298,3348,'秋招：四作者的不同切入与共同失败反馈'),
    ('E14','TY',2028,2052,'水断骨病：不机械套铸印病凶，检查具体制鬼'),
    ('E15','TY',2748,2766,'辩论赛：原断有奖推胜，反馈输了但有奖'),
    ('E16','TY',1397,1421,'医师资格：好成绩原断与未过反馈；遁干说法冲突'),
    ('E17','BHL',588,596,'北海天勇走失：行年、丁马、月德与未远走'),
    ('E18','ZNZ',1315,1322,'八门生会试：无禄课中按个人条件取戊戌者'),
    ('E19','BHQA',166,194,'公明会试：主次明示，盘文矛盾与读者补议'),
    ('E19C','ZNZ',1364,1376,'同一公明会试案：编注给出另一盘，尚未裁定'),
    ('E20','DA',128,136,'王德卿：二十六与十六年冲突、析者对取数质疑'),
    ('E21','TY',3350,3392,'医院编制：多作者取舍与表格、传位待核'),
    ('E22','TY',3648,3672,'拿手机：水断龙可用，具体替代强度未充分展开'),
    ('E23','DA',11,19,'韩太守祈雪：据占类季节释铸印与空亡'),
]

records = []
parts = ['# 高手断例调查：所核连续原文\n',
         '以下仅登记本轮已实际查看的选段。LF行号与正式splitlines坐标双列；原字节不变。原断、编注、合集补议和原载反馈的身份由研究卡另辨，摘录不自动构成已验证规则。\n']
for ident, key, start, end, title in SELECTED:
    row = passage(key, start, end)
    row.update(id=ident, title=title)
    records.append(row)
    # Remove residual CR from CRCRLF solely for Markdown presentation.
    display_quote = row['quote'].replace('\r', '')
    parts.append(f"## {ident} {title}\n\n来源：`{row['path']}`；LF{start}–{end}；正式splitlines {row['formal_start']}–{row['formal_end']}；编码 {row['encoding']}；SHA256 `{row['sha256']}`。\n\n```text\n{display_quote}\n```\n")
manifest = dict(kind='local-expert-method-study', main_source_files=len({x['path'] for x in records}),
                selected_passages=len(records), case_units=23,
                case_units_are_not_independently_verified_events=True,
                active_changed=False, external_model_calls=0,
                independent_predictive_validation_count=0,
                line_convention='LF matches rg; formal splitlines supplied separately',
                passages=records)
(HERE/'source-evidence.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'所核连续原文.md').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k != 'passages'},ensure_ascii=False))
