"""One-time, reproducible paragraph import from a frozen P0 baseline.

Re-running requires a NEW destination; current maintenance work is never overwritten.
Only byte-identical paragraphs are deduplicated. Historical R/A1/audit remains archived.
"""
import argparse
import json
import os
import re
import shutil
from pathlib import Path
from liuren_runtime import ROOT, sha, write_json

GROUPS = {
    'core': ['daliuren', 'sanbu-duanke', 'leishen-keti'],
    'evidence': ['liuren-cases'],
    'state-and-rescue': ['kongwang-bianzhi', 'jixiong-tiaozhi'],
    'movement-and-yinshen': ['keti-qishi', 'youlu-lilun'],
    'shensha': ['shensha-panduan', 'xiongsha-suduan'],
    'timing': ['yingqi-panduan'],
}
DOMAINS = dict(zip(['finance', 'recruitment', 'promotion-salary', 'relationship', 'interpersonal', 'period-outlook', 'long-period', 'pregnancy', 'exam', 'illness', 'lost-person-object', 'classical-conflict'],
                   ['cailu-panduan', 'yingpin-gongzuo', 'shengzhi-jiaxin', 'lianai-panduan', 'renji-guanxi', 'shiyun-zonghe', 'zhongshen-nianyun', 'yunchan-panduan', 'kaoshi-panduan', 'jibing-panduan', 'shiwu-xunren', 'zhinan-zhanbing']))
GROUPS.update({k: [v] for k, v in DOMAINS.items()})
FILES = {k: k + '.md' if k in ('core', 'evidence') else ('domains/' if k in DOMAINS else 'mechanisms/') + k + '.md' for k in GROUPS}
ENHANCEMENT = '''# 北海三步法的逐问执行核心

这是当前方法的融合增强候选。保留“明占类 → 定侧重 → 看显象”，《壬归》补强对象关系与理气，不另立竞争流程。下列记录方式是工程约束，原书身份见 [来源卡](sources/fusion-sources.md)。

## 明占类：先固定要回答的现实事件

保存用户原问。逐问列对象、事件、阶段、期限、判断维度与成功标准：结果、过程、程度、属性、身份、地点、数量、时间分开。“没有大灾”不能替换“是否任何进水”；面试、录用、通知、入职也不是同一事件。只把题干确认的情况当已知，不从盘象补造背景。

## 定侧重：角色必须用于判断

按本问方法固定日干、日支、类神、相关年命和代问/当事人的角色；不要求每题机械齐用，未用或改用须说明依据。分别记录天盘支、所临地盘、乘将、上神、直接阴神；命支、命宫上神不可互换。每个角色有固定盘字段与取用来源。

主线写成“本对象通过哪条实际盘面关系影响本问结果”，不能只写“类神线”“水势”或“退茹”。支已取宅/车库时，要检查宅及其相关上下关系，并使该对象进入结论依赖；如果采用其他更直接取用，明确解释替代关系。角色出现于表格却未用于任何结论时返回补查。

四课、日辰对待与类神共同定位人事；不因未入传删除相关对象，也不因出现即断实现。财有气不等于本人取得；日辰彼此生克必须落到所问主体和客体。缺成熟专项的家宅、天时、出行沿此核心并查有据源段，不编造新专项。

## 看显象：关系、状态、实际作用分开

对决定结果的关系及最强反证，逐一核：对象/坐标 → 关系 → 双方状态与限制 → 实际作用 → 影响结果、过程、程度还是时间。盘面关系是真实字段；实际效果是须论证的判断，不由程序自动证明。

五气以月令为参照；十二气必须说明以日干、类神还是天将为本及所临地；六亲说明相对于谁。土寄生、顺逆、节月等口径注明来源，敏感结论给分支，不混算、不投票。并核生扶脱耗、神将/内外战、刑冲合害、空墓。相关细则在 [状态与救制](mechanisms/state-and-rescue.md)，采用前读完整条件。

发用检查发端与本问的联系；三传检查转移、归宿或占类规定的角色，不一律当过去现在未来。占时先锋察端倪，不具永久否决权。阴神从已明确坐标取直接一层，新增一层必须解决具体争点，重复或无新增关系则停止；类神三传与通常三传分列，按所用来源有需要才展开。见 [动态与阴神](mechanisms/movement-and-yinshen.md)。

八煞九宝与32项基础核查完整保留，见 [神煞](mechanisms/shensha.md)。核过无关可以不采用，不必逐条对客展开。确定性起法可由原引擎提供，作用仍须核对象、状态和通路；普通神煞辅助不能成为漏查理气关系的借口。

## 制救与裁决

救谁、制谁、解除哪个阻碍？写明救制者和对象、位置/通路、力量、空墓刑合等限制及覆盖范围。关系存在不等于制得住。局部缓解只改变相应过程或损失；关键阻碍确实解除时重新裁决结果；位置、起法或来源冲突未解只能候选，不可登记确认有效救应。

检查同对象、同事件、同阶段的最强相反依据：解释采纳、限制或拒绝的条件。没有发现时如实记录检查范围；不能凑造反证。无永久“课体高于类神”或相反排名，不以吉凶条数投票。同支多标签、同案多转载不能充当独立验证。

结果、程度、时间分项收束。关键依据撤销或问项/关系修订，使依赖它的全部结论（含应期）失效，重新提交。只支持范围时不造精度。时间问题才完整加载 [应期](mechanisms/timing.md)，先事件节点、尺度与方法，再列候选；日期不能反证事件必成。

## 加载、取证与交付

完整读取本核心、[证据纪律](evidence.md)、神煞基础及实际问项所需占类；触发空墓/制救、动态/阴神、应期时读取对应完整机制。一次注册依赖，同版本完整已读可复用，8KB分页和哈希不因合并而省略。争点补读说明目的，回到原问重评。

旧方法名称是模块别名。下附原运行段中的本地 Skill 调用、localhost、文件路径、步骤计数在候选中由模块加载、固定盘与逐问记录承担；不再多跑八个同名入口。此适配只改变执行接口与是否需要时间任务，不改变所载术理条件。structural 版保留旧执行强度，不能与 enhanced 混用作等价实验。

网站使用 register_questions 与 record_judgment 保存可核对摘要；角色事实、方法来源、关系、反证、结论依赖与未定项均可查。不得要求或持久化私下思维草稿。检索规则见证据模块；客户公开输出继续隐藏内部来源、案例ID与路径。教材、合成例、自审及结构校验不算独立预测命中。

## 已曝光的车库反例边界

车库片段仅证明开发中曾发生“角色命名却未用于主判”“无大灾替代无任何水”的错误路径。完整盘与反馈时序未取得，不补造课盘。水不临支、支上火、辰为水库、三传空，均不能单独升级为绝不进水、必然干燥或空库通则；单项不足也不等于该象无效。

---

# 以下为当前运行规则的完整分组迁移

保留条件、反例与来源差异；与上文冲突的接口要求按上文适配，术理分歧回原源核对。迁移对照见 migration-map.json。

'''


def migrate(baseline, dest):
    baseline, dest = Path(baseline).resolve(), Path(dest).resolve()
    if dest.exists():
        raise ValueError('new destination required')
    dest.mkdir(parents=True)
    snapshots = dest / 'sources/snapshots'
    paths = [p for p in sorted((baseline / '.opencode/skills').rglob('*')) if p.is_file() and not re.search(r'test-(prompts|results)', str(p))]
    # Preserve original bytes, relative layout and all existing Markdown-link dependencies.
    queued = [p.relative_to(baseline).as_posix() for p in paths]
    copied = set()
    while queued:
        rel = queued.pop()
        if rel in copied:
            continue
        p = baseline / rel if (baseline / rel).is_file() else ROOT / rel
        if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(ROOT):
            raise ValueError('unsafe or missing source: ' + rel)
        if p.suffix.lower() not in ('.md', '.txt', '.json', '.js', '.py', '.ps1', '.html', '.csv', '.bak'):
            raise ValueError('unsupported source asset: ' + rel)
        target = snapshots / rel; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, target); copied.add(rel)
        if p.suffix != '.md':
            continue
        text = p.read_text('utf-8-sig')
        for link in re.findall(r'\[[^\]\n]+\]\((<[^>]+>|[^\s)]+)\)', re.sub(r'```.*?```', '', text, flags=re.S)):
            name = link.strip('<>').split('#')[0]
            if not name or name.startswith(('http:', 'https:')):
                continue
            q = (ROOT / rel).parent / name
            if q.resolve().is_relative_to(ROOT) and q.is_file():
                queued.append(q.resolve().relative_to(ROOT).as_posix())
    aliases = {name: [key] for key, names in GROUPS.items() for name in names}
    rows, modules, bodies, seen = [], {}, {}, {}
    for key, names in GROUPS.items():
        filename = FILES[key]
        bodies[key] = [f'# {key}：当前规则分组\n\n原书、原例及审计保留为来源；同文段归并，条件不同不合并。旧方法名由清单解析。\n\n']
        seen[key] = {}
        modules[key] = dict(file=filename, requires=[], when='本问涉及' + '/'.join(names))
    # Reference bodies needed together with the mandatory shensha checks stay together.
    embedded = {'bashajiubao.md': 'shensha', 'shensha-focus.md': 'shensha', 'shensha-use.md': 'shensha',
                'liqi-analysis.md': 'state-and-rescue', 'rule-semantics.md': 'evidence', 'judgment-workflow.md': 'evidence'}
    for p in sorted(snapshots.rglob('*.md')):
        rel = p.relative_to(snapshots).as_posix()
        if not rel.startswith('.opencode/skills/'):
            continue
        name = rel.split('/')[2]; key = aliases.get(name, ['evidence'])[0]
        support = p.name != 'SKILL.md'
        if support:
            key = embedded.get(p.name, key)
        text = p.read_bytes().decode('utf-8-sig').replace('\r\n', '\n')
        section = 'preamble'
        for match in re.finditer(r'\S.*?(?=\n\s*\n|\Z)', text, flags=re.S):
            old = match.group(); heads = re.findall(r'^## (.+)', old, re.M)
            if heads:
                section = heads[-1]
            active = name in aliases and ((support and p.name in embedded) or (not support and (section.startswith(('I —', 'E —', 'B —', '理气', '判断流程')))))
            target_file = FILES[key] if active else 'sources/snapshots/' + rel
            rendered = old
            if active:
                # Rewrite actual links, not code pseudo-links; archive every source dependency.
                def link(m):
                    label, raw = m.group(1), m.group(2)
                    raw = raw.strip('<>'); parts = raw.split('#', 1); name = parts[0]
                    if not name or name.startswith(('http:', 'https:')):
                        return m.group()
                    q = ((ROOT / rel).parent / name).resolve()
                    if not q.is_relative_to(ROOT) or not q.is_file():
                        return m.group()
                    src = q.relative_to(ROOT).as_posix()
                    old_name = src.split('/')[2] if src.startswith('.opencode/skills/') else ''
                    out = dest / FILES[aliases[old_name][0]] if old_name in aliases and q.name == 'SKILL.md' else snapshots / src
                    target = Path(os.path.relpath(out, (dest / target_file).parent)).as_posix()
                    # Old anchors belong to the archived source; module targets expose full methods.
                    return f'[{label}](<{target}>)'
                rendered = re.sub(r'\[([^\]\n]+)\]\((<[^>]+>|[^\s)]+)\)', link, old)
                action = 'merged-equivalent' if rendered in seen[key] else 'retained'
                if action == 'retained':
                    bodies[key].append(f'<!-- source: {rel}; section: {section} -->\n\n' + rendered + '\n\n')
                    seen[key][rendered] = True
            else:
                action = 'historical-reference'
            rows.append(dict(sourcePath=rel, sourceHash=sha(p.read_bytes()), section=section, oldTextHash=sha(old.encode()),
                             start=match.start(), end=match.end(), snapshot='sources/snapshots/' + rel,
                             targetModule=key if active else 'source-archive', targetFile=target_file, renderedText=rendered if active else '', action=action,
                             reason='byte-identical body only' if action == 'merged-equivalent' else 'retain full conditions' if active else 'original source/reference or independent maintenance task; not rewritten as a new instruction',
                             sourceIdentity='current-execution' if active else 'archived-source-not-independent-validation'))
    for key, pieces in bodies.items():
        path = dest / FILES[key]; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(''.join(pieces), encoding='utf-8')
    structural = dest / 'sources/structural-core.md'
    structural.write_bytes((dest / 'core.md').read_bytes())
    (dest / 'core.md').write_text(ENHANCEMENT + (dest / 'core.md').read_text('utf-8'), encoding='utf-8')
    write_json(dest / 'migration-map.json', rows)
    # Full archived skills are provenance, not extra auto-trigger entries in this single-event candidate.
    routes = {k: [k] for k in DOMAINS}
    files = {p.relative_to(dest).as_posix(): sha(p.read_bytes()) for p in sorted(dest.rglob('*')) if p.is_file()}
    manifest = dict(schemaVersion=2, maintenanceVersion='20261023-fusion-1', modules=modules, routes=routes, legacyAliases=aliases,
                    independentTasks=['liuren-extract', 'liuren-tuiming'], files=files,
                    scope='single-event', provenancePolicy='archived source and engineering constraints are not independent predictive validation')
    write_json(dest / 'manifest.json', manifest)
    return dict(paragraphs=len(rows), files=len(files), actions={x: sum(r['action'] == x for r in rows) for x in sorted({r['action'] for r in rows})})


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(migrate(a.baseline, a.output), ensure_ascii=False))
