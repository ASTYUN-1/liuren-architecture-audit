"""Curated cross-partition relations, backed by the compared source passages."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parents[1]
entries=[]
for group in ('history','books','new'):
    entries.extend(json.loads((OUT/f'data/{group}.json').read_text(encoding='utf-8-sig'))['entries'])

def at(filename,line):
    matches=[e for e in entries if e['source'].endswith('/'+filename)
             and e['line_start']<=line<=e['line_end']]
    if not matches:
        raise ValueError(f'该原文位置尚无可关联检索单元：{filename}:{line}')
    return min(matches,key=lambda e:e['line_end']-e['line_start'])['id']

relations=[]
def relation(kind,refs,reason):
    members=list(dict.fromkeys(at(name,line) for name,line in refs))
    if len(members)<2:
        raise ValueError('关系至少两个不同条目')
    relations.append(dict(type=kind,members=members,reason=reason))

relation('冲突待核',[
    ('古籍-北海闲人指南问答.md',19),
    ('1-案例库经验提取.md',46),
    ('2026-10-18-交易占-讨欠薪反吟元胎申日亥时全额300元复盘.md',56),
    ('2026-10-18-财运占-raw-anli002-0017-待验证记录.md',43),
], '书籍摘录及旧汇总强调课体大势优先，讨薪反面校正强调类神定结局，新融资候选则要求反吟不作单因。不能将这些改写成一条无条件优先级；先分结果/过程、类神是否实旺、占问对象与救解位置。本次保留竞争解释，不以案例结果倒定通用排序。')

relation('冲突待核',[
    ('六壬经验审查报告.md',59),
    ('2026-06-24-交易占-弹射间传闭店反推.md',22),
    ('2026-10-18-财运占-raw-anli001-0018-待验证记录.md',22),
    ('提取-大六壬应期断诀窍.md',202),
], '闭店“空财取冲不取填实”已被旧审查C-7判无据；新生意记录仍在现存依据中转引该规则，但该文件candidate_count=0、链条仅存档未成立。应期摘录保留出旬/填实路径。这里登记的是旧疑点传播与立场分歧，不把被否决链重新列成可用技巧。')

relation('相似方法',[
    ('2026-10-18-交易占-讨欠薪反吟元胎申日亥时全额300元复盘.md',25),
    ('2026-10-18-官讼占-raw-anli002-0013-待验证记录.md',19),
], '官讼候选明确转引讨薪记录的旺财只压不扣、囚死减半。原案是索取已有工资，新案是协商赔偿；金额基数、事件类型与类神旺衰不同，不能据此称旧规则再次验证，转引壬归也不是本次直查原书。')

relation('相似方法',[
    ('2026-10-18-交易占-讨欠薪反吟元胎申日亥时全额300元复盘.md',42),
    ('2026-10-18-财运占-raw-anli002-0017-待验证记录.md',43),
], '都在讨论反吟是否只解释反复、双象而不单独决定成败；讨薪案已有现实全额反馈，融资仅高质量作业参照，且一个索旧财、一个募新财。相似裁决方法不等于结果可直接迁移。')

relation('条件差异',[
    ('2026-10-18-事业占-名次数取法与官鬼空误读.md',36),
    ('2026-10-18-交易占-讨欠薪反吟元胎申日亥时全额300元复盘.md',46),
    ('2026-10-18-财运占-raw-anli001-0031-待验证记录.md',31),
], '名次、工资金额与房价的取数都存在多个候选体系；河图生数、洛书宫数、大衍数和取数基点不能互换。讨薪卯=3还依赖行年假设，不能用同一个“3”表面吻合宣布固定算法已经验证。')

for audit_line,design_line,label in [
    (53,214,'六壬四化'), (54,165,'天将亮度'), (55,97,'月将调候'),
    (56,362,'三层叠宫'), (62,466,'行年起月逆改顺'),
]:
    relation('冲突待核',[
        ('六壬经验审查报告.md',audit_line),
        ('六壬推命增补方案-八字紫微框架嫁接.md',design_line),
    ], f'{label}在旧审查已有无据/嫁接或与原文方向冲突警示，设计方案自身也留有审查标记。此处把两处位置回链，保留研究设计身份及原警示，不因有步骤、表格或重复引用就列为已验六壬技法；本轮没有重新验证原典或实施该设计。')

findings=[
    '“未验”需区分初判失准与没有反馈。工作调动 raw-anli001-0006 与手机数据 raw-anli002-0010 的关联案例均有现实结果；经验META的“未载/从疑”不能抹去案例反馈，也不能倒过来认证反推链条。应分别保存反馈是否存在、初判是否命中、经验是否独立验证三轴。',
    '跨组重点已核对：课体/类神权重分歧、空财冲填旧疑点传播、讨薪到官讼的规则转引、反吟在旧财/新财场景的边界，以及名次/金额的取数体系错配风险。关系仅作导航和核验线索，不直接改规则。',
]
(OUT/'data/cross-relations.json').write_text(json.dumps(dict(relations=relations,findings=findings),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('cross relations:',len(relations))
