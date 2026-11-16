"""Audit examples for the proposed formulas, not a full chart or event solver."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parent
PARAM_BYTES = (ROOT / '候选计算参数.json').read_bytes()
P = json.loads(PARAM_BYTES)
OLD = P['inherited']


def solve_one(base, retention, external_support=0.0, fixed_fire=0.0):
    """An isolated heaven actor; other paths explicitly excluded in this example."""
    score = base * retention
    for _ in range(10000):
        hit = OLD['relations']['control'] * fixed_fire / (1 + score / 5)
        mapped = retention * max(0.0, min(10.0, base + external_support - hit))
        if abs(mapped - score) < 1e-12:
            return {'score': score, 'control_before_void': hit,
                    'control_after_void': hit * retention}
        score = (score + mapped) / 2
    raise RuntimeError('Single-node example failed to converge')


def group_example(member_values, coverage=1):
    integrity = coverage * math.sqrt(min(member_values) * sum(member_values) / len(member_values)) / 10
    return {'member_values': member_values, 'integrity': integrity,
            'cooperative_gate_multiplier': 1 + .10 * integrity,
            'meaning': '合作通路预算前修正；非各成员最终分数乘数，非合化判据'}


def main():
    branch_base = 5 * 1.3 * (.7 * .85 + .3 * .85)
    tiger_base = 5 * 1.3 * (.7 * 1.15 + .3 * .85)
    no_fire = solve_one(branch_base, .85)
    weak_fire = solve_one(branch_base, .85, fixed_fire=3)
    with_yin = solve_one(branch_base, .85, external_support=.20 * .75 * 4.25, fixed_fire=3)
    greedy = min(.5, .5 * .75 * 4.25 / (4.25 + with_yin['score']))
    local_greedy_action = with_yin['score'] * 1.2 * (1 - greedy)
    remote_action = with_yin['score'] * 1.2

    e_closed = 6 * .6
    opening = min(1, 1 / (.6 * e_closed))
    tomb_examples = {
        'closed_no_support': e_closed,
        'closed_with_one_support': (6 + 1) * .6,
        'weak_opener_strength': 1,
        'opening_ratio': opening,
        'after_weak_opening': 6 * (.6 + .4 * opening),
        'strong_opener_strength': 3,
        'after_full_opening': 6 * (.6 + .4 * min(1, 3 / (.6 * e_closed))),
        'reference': '解除前闭藏状态3.6为参照；孤立通路示意，不是本课墓神结论'
    }
    raw_members = [6, 5, 4]
    void_members = [6, 5 * .7, 4 * math.sqrt(.6)]
    data = {
        'model': P['id'],
        'profile_sha256': hashlib.sha256(PARAM_BYTES).hexdigest(),
        'scope': '局部公式复算及构造对照；没有计算全盘、全部神煞、录用或行业答案',
        'shen_hiring_base': {
            'given_coordinates': '申月，申坐午，阴神戌，白虎乘申；非重新起课',
            'branch_base_before_void': branch_base,
            'tiger_base_before_relations': tiger_base,
            'no_fire': no_fire,
            'fixed_ground_fire_3': weak_fire,
            'fire_change': weak_fire['score'] - no_fire['score'],
            'fixed_ground_fire_3_and_assumed_yin_4_25': with_yin,
            'greedy_loss': greedy,
            'action_if_direct_greedy_applicable': local_greedy_action,
            'action_if_same_support_remote': remote_action,
            'assumptions': '午地盘源3可由申月火囚基点取得；阴戌4.25为固定源示意，未求其全盘扶损；其他通路未计，故所有数值均非本课综合终分'
        },
        'void_examples': {
            '旺空8分': 8 * .85,
            '休沐浴弱生0_2且旬空': (5 * .85 * .85 + .2) * .7,
            '同一条件再受制1_5': (5 * .85 * .85 + .2 - 1.5) * .7,
            '死气绝地无其他来源且旬空': 5 * .4 * .4 * .5,
            'interpretation': '休沐浴弱生这一组自身不必然低于2.5；不得为了符合预想强行压低'
        },
        'group_examples': {
            'without_root_void': group_example(raw_members),
            'with_same_root_wu_void_and_yin_sitting_void': group_example(void_members),
            'very_weak_wu': group_example([6, .3, 4]),
            'assumptions': '成员无空前量6/5/4为构造输入；戌月末季土条件午休、寅囚，仅对照同根空改变两成员，不是本课最终成员分数'
        },
        'tomb_examples': tomb_examples,
        'status': 'formula-examples-only-not-complete-chart-validation'
    }
    (ROOT / '局部复算数据.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [
        '# 公式复算与对照', '',
        '2026年11月9日。此处验证候选公式如何结算，未执行全盘完整旺衰模型。数值为研究指数，非预测验证。', '',
        '## 1. 求职案申与白虎的基础量', '',
        f'- 申：5×1.30×(0.7×0.85+0.3×0.85)＝{branch_base:.4f}。',
        f'- 白虎：5×1.30×(0.7×1.15+0.3×0.85)＝{tiger_base:.4f}；尚未计其他扶损。',
        f'- 申仅加自身旬空：{no_fire["score"]:.4f}。',
        f'- 再考虑固定午火源3，其克制随申当前强度联合求解，申为{weak_fire["score"]:.4f}。',
        f'- 本局部比较下降{no_fire["score"] - weak_fire["score"]:.4f}，并非一见午克便归零。', '',
        '午火3对应申月火囚的环境底数。本例暂不计其他通路，不能称为申的全盘最终分数。', '',
        '## 2. 同样生扶，直接临处与别处扶助不同', '',
        '另固定阴戌源4.25，作为局部输入示意，支持量0.20×0.75×4.25＝0.6375；此4.25未经过阴戌全盘求解。',
        f'- 本体计入这份支持及弱午克制后：E＝{with_yin["score"]:.4f}。',
        f'- 若为已适用的直接临生：贪生损失＝{greedy:.4f}，发动按1.2，A＝{local_greedy_action:.4f}。',
        f'- 若同量支持来自远处，不套贪生：A＝{remote_action:.4f}。',
        '- 两种情形使用相同E和同一份生扶，没有再乘一次旬空；差异只来自对该目标的贪生限制。', '',
        '## 3. 空亡不改参数，强弱自然分开', '',
        '| 构造条件 | 空后指数 |', '|---|---:|',
    ]
    lines += [f'| {name} | {value:.4f} |' for name, value in data['void_examples'].items() if isinstance(value, (int, float))]
    lines += [
        '', '特别注意：休气、沐浴、只有0.2弱生并旬空，按原参数仍约2.67，不能强行宣称一定低于1或2.5。加上真实受制后才继续降低。2.5用于研究分档，不删除节点。', '',
        '## 4. 午空与寅坐午空共同影响寅午戌合作', '',
        '以下无空前6/5/4为构造成员分数。季土条件下午休、寅囚；只切换午这个空根时，午乘0.70，寅乘√0.60，不能只改午而遗漏寅坐空，也不能再罚整局一次。', '',
        '| 条件 | 成员值 | 完整度 | 合作通路修正 |', '|---|---|---:|---:|',
    ]
    for name, row in data['group_examples'].items():
        if isinstance(row, dict):
            lines.append(f'| {name} | ' + ' / '.join(f'{x:.3f}' for x in row['member_values']) + f' | {row["integrity"]:.4f} | {row["cooperative_gate_multiplier"]:.4f} |')
    lines += [
        '', '修正作用于合作通路并受共同预算约束，不乘每个成员终分，不据此直接判合化。', '',
        '## 5. 墓与开墓的唯一结算', '',
        f'- 本体参照量6，闭藏保留0.6，E＝{e_closed:.4f}；不是先6×0.6再扣一次。',
        f'- 同一闭藏条件下得1份支持：E＝{tomb_examples["closed_with_one_support"]:.4f}，不再另奖“得生解墓”。',
        f'- 对应专项准许冲开，解除前闭藏状态3.6为参照；有效冲者1，释放度{opening:.4f}，E＝{tomb_examples["after_weak_opening"]:.4f}。',
        f'- 有效冲者3时本例完全解除该限制，E＝{tomb_examples["after_full_opening"]:.4f}；不加开墓奖励。', '',
        '这是新候选机制的孤立算例，不表示原书提供了0.6开墓门槛，也未核本课是否存在该墓与有效冲者。', '',
        '运行：`python -X utf8 output/liuren-strength-candidate-20261109/review_examples.py`。参数及输出均放本候选目录，不修改现行模型。', ''
    ]
    (ROOT / '公式复算与对照.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'shen_base': branch_base, 'shen_void_only': no_fire['score'],
                      'shen_with_weak_ground_fire': weak_fire['score'],
                      'direct_greedy_action': local_greedy_action,
                      'same_support_remote_action': remote_action,
                      'report': str(ROOT / '公式复算与对照.md')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
