"""Persist the manually compared C46–60 branches; never infer semantic completion."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'knowledge/liuren-research/20261102'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

cards = read(BASE / 'rules/book-shao-c-review.json')
old = read(BASE / 'rules/book-shao.json')
by_id = {x['id']: x for x in old + cards}
reviews = read(BASE / 'method-reviews/shao.json')
for card in cards:
    if card['id'] == 'LR26-BOOK-SHAO-C032':
        card['reasoning_steps'][1] = '亥克午、午逃身宅；原书称身能制而宅受害，不补额外作用链。'
for review in reviews:
    if review['case_id'] == 'BK26-SHAO-056':
        for sub in review['subjudgments']:
            sub['judgment'] = sub['judgment'].replace('new衣', '新衣')
    if review['case_id'] in {'BK26-SHAO-048', 'BK26-SHAO-053'}:
        review['external_gap_review'] = {
            'checked_source_scope': '本地邵彦和原书整案题干、断、析与末附原文；连续来源身份见source_refs。',
            'available_methods_preserved': list(dict.fromkeys(r for sub in review['subjudgments'] for r in sub['rule_ids'])),
            'unresolved_actions': review['remaining_actions'],
            'status': '处置已明确，月令/妻符与日干疑句尚未获外源恢复。'}

# Each assignment keeps the actual object and inference conditions, not only a topic label.
maps = {
 'C047': [('DYNAMIC', '三渊远陷空且不回为官程劳与外州终；不等同155动静合生分支。'), ('HUMAN-HOUSE', '申息临午刃、中同类加息、末妻后空分别为子/继子/产危，不由三渊一概推出。')],
 'C048': [('HUMAN-HOUSE', '申妻六合棺临巳、亥4妻数与申马四维4任分对象；寅功曹玄天门另为曹荐刑职。'), ('QUANTITY-OPERATIONS', '亥4妻、四维4任、4年后显的对象和位置分开，不因数字同为4归成一次数法。')],
 'C049': [('QUANTITY-OPERATIONS', '巳长生4，两巳加成8，再乘子9得寿72；未载寿验，与店业四年分开。')],
 'C050': [('HUMAN-HOUSE', '父临妻宫与马破碎、子受身克、申空贵像、妻夹克为四不足；与原050走范破模的科名取舍互补。')],
 'C051': [('DOCUMENT-TIMING', '罗刃回日现在赴与行年子冲午父明年丧分别判断。'), ('QUANTITY-OPERATIONS', '卯6辰5巳4相加15为监司年；后加8共23为寿段，16/17降期原存不补算。')],
 'C052': [('DOCUMENT-TIMING', '癸亥极日初晦、幕贵向日贵转明，行年长生学堂拱为及第支撑；五甲为等第未明数法。')],
 'C053': [('VOID-EXCEPTIONS', '贵多但身初中空与日支投绝，限制官程；上书雀岁贵鬼另为风险。'), ('TEXTUAL', '申妻/辛妻、丁日/丙日绝保留作者层次和异文；不拼成统一妻符。')],
 'C054': [('DYNAMIC', '登三天初有升象，子关、午撞巳止与末申空使升象不落实；不借其他同名课体补升。')],
 'C056': [('CLASS-SYMBOL', '弓巳、箭申、马午须问弓马试且核现隐得地；官照只得虚衔，原风险建议未见发生反馈。')],
 'C057': [('SUBQUESTION', '亥禄常重并可兼任增俸，升转、寻医恋色与监司解任分子问分时段，不能一律判贵或凶。')],
 'C059': [('HUMAN-HOUSE', '行年子生甲与宅午制申先催官而后申绝；寅后恩官的父子尊卑是另一对象链。')],
 'C060': [('VOID-EXCEPTIONS', '学堂亥临戌空、日贵空取虚名，行年亥在后只暂延；不能用暂延抹去空脱。')],
 '046': [('HUMAN-HOUSE', '初妻财寅引中巳长生、末申身禄，妻家起业不等同科名；逐问复用原046。')],
 '048': [('VOID-EXCEPTIONS', '中亥月将官程不论空而少迟、巳寅受生不为空炉；不能扩到免妻凶。')],
 '049': [('CLASS-SYMBOL', '卯空朽木、戌空无模使斫轮科名失败，轮磨余象改落水碓生计；不涵盖寿数。')],
 '050': [('CLASS-SYMBOL', '巳玄加子走范、卯虎加戌破模坠轩，死亡强断另须己卯；不与四不足混为一条。')],
 '055': [('SUBQUESTION', '申禄空否武，末巳雀长生学堂取文，岳庙邀友读书为行动转向；原卡已逐问覆盖。')],
 '058': [('SUBQUESTION', '寅官空否正任，巳禄支合仍食禄，陈姓退才到任；官、禄、障碍和阶段旧卡已覆盖。')],
}
families = read(BASE / 'families/book-shao.json')
family_by_id = {x['id']: x for x in families}
for suffix, branches in maps.items():
    rid = 'LR26-BOOK-SHAO-' + suffix
    card = by_id[rid]
    for name, meaning in branches:
        family = family_by_id['LF26-SHAO-' + name]
        if rid not in family['rule_ids']:
            family['rule_ids'].append(rid)
        family['preserved_branches'] = [x for x in family['preserved_branches'] if x['rule_id'] != rid]
        family['preserved_branches'].append({'rule_id': rid, 'conditions': card['conditions'], 'source_method': meaning})
        source_map = family['canonical_rule']['source_rule_map']
        source_map[:] = [x for x in source_map if x['source_rule_id'] != rid]
        source_map.append({'source_rule_id': rid, 'canonical_family_id': family['id'], 'disposition': meaning})

audit_path = ROOT / 'output/liuren-book-cases-20261102/shao-c-condition-dedup-audit.json'
audit = read(audit_path)
audit['reviewed_case_ids'] = [x['case_id'] for x in reviews]
comparisons = {
 '048': ('月将官程不空少迟、巳受生不为空炉', '申妻合棺及4妻、四维4任、功曹曹姓刑职；和空取舍属于不同问事目标', '同案亥不空仅用于官程，不能移到妻危子克；保留互补分支'),
 '049': ('朽木无模使斫轮科名失败，轮磨转店业水碓', '巳4两巳8再乘子9为72寿；寿未反馈，与转业结果分轴', '科名/生计取舍与寿数计算不等价；保留补充数法'),
 '050': ('巳玄走范卯虎破模，死亡另限己卯', '七杀元辰及父子贵妻四不足；四分项未获同等结果证实', '课体条件否决与家庭四不足互补；不删除原日支死亡限定'),
}
for number, (a, b, disposition) in comparisons.items():
    pair = ['LR26-BOOK-SHAO-' + number, 'LR26-BOOK-SHAO-C' + number]
    audit['pair_comparisons'] = [x for x in audit['pair_comparisons'] if x['source_rule_ids'] != pair]
    audit['pair_comparisons'].append({'source_rule_ids': pair,
        'comparison_dimensions': ['问事对象', '推理环节', '必要条件', '结论/反馈身份'],
        'shared_scope': '同一原事件与原文，支持数不增加',
        'distinct_source_methods': {pair[0]: a, pair[1]: b}, 'disposition': disposition,
        'canonical_family_ids': [f['id'] for f in families if any(r in f['rule_ids'] for r in pair)]})
reuse = {
 '046': '功名否与妻家起业、晚段财禄及后注重禄，原卡已载初中末引生链，逐问复用无新增。',
 '055': '虚武禄、另择文象岳庙、读书行动与己酉/庚戌结果，旧卡已保转向条件；原名次无数法不强增。',
 '058': '官空正任不可得、禄合仍食禄、阻碍人物退后到任均在旧卡；无额外填冲空月法可增。',
}
audit['existing_card_reuse_decisions'] = [x for x in audit.get('existing_card_reuse_decisions', []) if x['case_id'] not in {'BK26-SHAO-' + n for n in reuse}]
audit['existing_card_reuse_decisions'] += [{'case_id': 'BK26-SHAO-' + n, 'rule_id': 'LR26-BOOK-SHAO-' + n, 'reason': reason} for n, reason in reuse.items()]
audit['new_rule_family_maps'] = [{'rule_id': x['id'], 'family_ids': [f['id'] for f in families if x['id'] in f['rule_ids']]} for x in cards]
audit['remaining'] = '已审01–60及11个优先案；尚未逐223案和全部旧卡做同条件比较，不作全书去重完成声明。'
write(BASE / 'rules/book-shao-c-review.json', cards)
write(BASE / 'method-reviews/shao.json', reviews)
write(BASE / 'families/book-shao.json', families)
write(audit_path, audit)
print({'reviewed': len(reviews), 'subjudgments': sum(len(x['subjudgments']) for x in reviews), 'supplemental': len(cards), 'pairs': len(audit['pair_comparisons'])})
