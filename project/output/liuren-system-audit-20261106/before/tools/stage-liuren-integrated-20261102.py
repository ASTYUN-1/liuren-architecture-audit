"""Build and locally activate the integrated Liuren release; never deploys."""
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
RELEASE = '20261102-integrated-01'
PARENT = '20261027-quantity-02'
OUT = ROOT / 'output/liuren-consolidation-20261102/workflow'
OLD = ROOT / ('runtime/liuren/' + PARENT)
NEW = ROOT / ('runtime/liuren/' + RELEASE)
LIVE = ROOT / '.opencode/skills/liuren'


def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(path): return json.loads(path.read_text('utf-8-sig'))
def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
def inventory(root): return {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file()}


CONTRACT = '''# 本机统一会话契约

本模块负责执行资料与验收的程序约束；其余原论、判法和专门步骤全文保留。模型仍须逐条研判，检查通过不证明术理正确或预测准确。

1. 在项目根目录使用唯一主入口：`python -X utf8 tools/liuren-workflow.py prepare --input INPUT.json --out RUN`。INPUT包含chart（现有程序引擎参数）、questions（逐问id/question/target/stage/success_criterion/requires）、domains与按条件选出的modules；requires包含conclusion，涉及应期/数量分别加入timing/quantity。source_id及exclude_sources须填已知原案身份。prepare由现有固定引擎生成facts并校验；不接纳模型重排或未经核对的facts。输入无需反馈，也不应放保留答案。
2. 读取RUN/context.json、evidence-packet.json；会话固定facts哈希、源身份、模块计划和全部候选编号。全部候选与省略编号在coverage.json，context带其稳定hash和数量；不把含全文快照的session.json反复送入模型。默认排除暂停记录。候选排序只表示召回，条件/排除/状态/分支选择不被摘要取代；证据正文以ID、hash、定位、正反角色保全后按需分页读取，未读范围保持局限。
3. 按原十一环节读取所有计划模块的所有页：`python -X utf8 tools/liuren-workflow.py read --run RUN --id module:ID --page N`。计划不是已读凭证，读凭证也不是理解证明。命中候选用同一入口`read --run RUN --id ID --part record --page N`读取完整结构；source/evidence:N/source_case:N分别读取原条目与逐个证据。正文保原字节身份、每页有覆盖标记，不整本回传多案书。采用项在evidence_parts列实际完整读取的证据段。会话外、同案、保留答案不得以按ID绕过排除。`--review`仅可审查身份隔离后仍可见的暂停项，不生成可采用凭证。
4. 对每张卡逐条保留conditions/exclusions原文及index，标role：source_context原案背景、source_outcome原载结果、applicability可迁移成立条件、exclusion排除条件、unknown角色待判。不得把原案反馈变成本问先验；前两类只能source_only，并明确used_as_current_fact=false、迁移边界，不能填当前fact_refs。角色未知只能reference/defer/reject。source_method是来源身份，不代表通用预测规则；采用须另有已辨明的可迁移条件、当前子问与程序fact原值、迁移理由。
5. 判断记录包含session_id/session_sha256/facts_sha256/stage、questions和coverage。逐问按requires分别记录conclusion/timing/quantity的status(supported/conditional/unknown)、statement；未知列missing，条件结论列unresolved。应期列window/trigger/basis，数量列range/unit/basis。chart_evidence及条件引用用facts中的path/value精确原值，不从历史反馈补本问事实。
6. rules每项记录id、decision(adopt/conditional/reference/defer/reject)、conditions/exclusions逐条角色与状态、transfer_rationale、fact_refs；unknown记录missing。排除条件met或前提unmet/unknown不得adopt。来源方法没有已判明适用前提时只reference。application另列本问rationale/fact_refs；strongest_counterexample记录status、assessment/source_refs或未决缺口；完整source_refs与会话源清单相同。同源案例与经验不重复计独立证据。
7. `python -X utf8 tools/liuren-workflow.py check --run RUN --record JUDGMENT.json`检查绑定、原文、源与依赖新鲜度、完整已读模块、逐问覆盖、事实原值和条件状态。coverage.candidate_manifest_sha256确认完整候选覆盖清单，unreviewed_limitations明确未读/未评估范围；也兼容显式candidate_ids全列表。检查失败先修记录或保留unknown，不写“已验”；独立验证增量始终0。通过只表示程序覆盖的结构与证据约束，不证明文字之间的因果关系、术理适用性或现实结果。

旧search/load脚本只作兼容定位与分页；旧批量付费执行不再作为新任务入口。案例维护、资料提取、推命保留原专门规程，普通单事不绕到维护流程重复读取。
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if NEW.exists() or (OUT / 'activation.json').exists(): raise ValueError('release/activation already exists; refuse overwrite')
    pointer_path = ROOT / '.opencode/liuren-active.json'
    pointer = load(pointer_path)
    if pointer['release'] != PARENT: raise ValueError('unexpected active baseline')
    baseline = inventory(OLD)
    old_manifest = load(OLD / 'manifest.json')
    if {k: v for k, v in baseline.items() if k != 'manifest.json'} != old_manifest['files']:
        raise ValueError('old immutable runtime differs from manifest')
    removed = []
    for path in sorted(OLD.rglob('*')):
        if not path.is_file(): continue
        rel = path.relative_to(OLD)
        if any('bazi' in part.lower() or '八字' in part for part in rel.parts):
            removed.append(rel.as_posix()); continue
        target = NEW / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    contract_path = NEW / 'methods/workflow-contract.md'
    contract_path.write_text(CONTRACT, encoding='utf-8', newline='\n')
    # Append the contract without dropping any existing theory or method prose.
    for relative in ['entry.md', 'methods/evidence.md', 'methods/report.md']:
        path = NEW / relative
        text = path.read_text('utf-8').replace(PARENT, RELEASE)
        text += '\n\n## 本机融合执行入口\n\n统一 prepare/read/check 是当前主路线；完整契约见 ' + ('methods/workflow-contract.md' if relative == 'entry.md' else 'workflow-contract.md') + '。原有方法与专门规程全文继续适用，来源背景/原载结果不得冒充新案前提。\n'
        path.write_text(text, encoding='utf-8', newline='\n')
    route = load(NEW / 'reading-route.json')
    route['stages'][0]['required'].insert(0, 'workflow-contract')
    route['labels']['workflow-contract'] = '统一会话与证据边界'
    dump(NEW / 'reading-route.json', route)
    manifest = copy.deepcopy(old_manifest)
    manifest.update(release=RELEASE, parentRelease=PARENT, status='active-local',
        required=[key for stage in route['stages'] for key in stage['required']])
    manifest['modules']['workflow-contract'] = dict(file='methods/workflow-contract.md', required=True, requires=[], trigger='every local judgment')
    dump(NEW / 'loader-contract.json', dict(schema='liuren-integrated-loader-contract-v1',
        entry='tools/liuren-workflow.py', compatibility=['tools/load-liuren-methods.py', 'tools/load-liuren-procedure.py', 'tools/search-experience.py'],
        sourceHashes={str(p.relative_to(ROOT)).replace('\\','/'): sha(p.read_bytes()) for p in
            [ROOT / 'tools/liuren-workflow.py', ROOT / 'tools/liuren_workflow.py', ROOT / 'tools/load-liuren-methods.py', ROOT / 'tools/load-liuren-procedure.py']},
        semanticCorrectness='unverified', independentValidation=0))
    files = inventory(NEW)
    files.pop('manifest.json', None)
    manifest['files'] = files
    manifest['version'] = sha(json.dumps(files, sort_keys=True).encode())
    dump(NEW / 'manifest.json', manifest)
    backup = OUT / 'backup'
    backup.mkdir()
    shutil.copyfile(pointer_path, backup / 'liuren-active.json')
    shutil.copytree(LIVE, backup / 'skills-liuren')
    # Keep local paipan override and all full specialist wrappers; update release links.
    for path in sorted(LIVE.rglob('*.md')):
        text = path.read_text('utf-8')
        path.write_text(text.replace(PARENT, RELEASE).replace('当前liuren/bazi分组映射','当前liuren分组映射'), encoding='utf-8', newline='\n')
    entry = LIVE / 'daliuren/SKILL.md'
    text = entry.read_text('utf-8')
    marker = '\n## 本机统一执行主路线\n\n'
    # The new route appears before the historical framework; no old text is truncated.
    pos = text.index('\n## ')
    text = text[:pos] + marker + CONTRACT.split('\n', 1)[1] + '\n' + text[pos:]
    text = text.replace('本地无网站的 `register_questions`、`record_judgment` 工具。以报告的可核对记录交付；不可声称已执行不存在的调用或程序门禁。', '本机通过统一 CLI 的 prepare/read/check 执行子问登记、来源读取和程序检查；网站工具不在本机调用。交付保留实际检查回执，不把结构检查写成术理验证。')
    entry.write_text(text, encoding='utf-8', newline='\n')
    pointer.update(release=RELEASE, previousRelease=PARENT, runtime='runtime/liuren/' + RELEASE,
        methodVersion=manifest['version'], backup=backup.relative_to(ROOT).as_posix(),
        groups=['liuren'], activeSkillNames=['daliuren', 'liuren-cases', 'liuren-extract', 'liuren-tuiming'],
        files={'liuren/' + k: v for k, v in inventory(LIVE).items()},
        workflowEntry='tools/liuren-workflow.py', websiteChanged=False)
    dump(pointer_path, pointer)
    if inventory(OLD) != baseline: raise ValueError('old release changed')
    receipt = dict(release=RELEASE, parentRelease=PARENT, localOnly=True, websiteChanged=False,
        parentUnchanged=True, parentInventory=baseline, excludedBaziPaths=removed,
        retainedLiurenFiles=len(files), methodVersion=manifest['version'], liveFiles=pointer['files'],
        preservedTheory='all previous files except Bazi-exclusive paths; additions do not remove method prose',
        modelCalls=0, independentValidation=0, semanticCorrectness='unverified')
    dump(OUT / 'activation.json', receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in {'parentInventory', 'excludedBaziPaths', 'liveFiles'}}, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
