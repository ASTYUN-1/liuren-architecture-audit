"""Generate proposed ownership and call timing; do not change runtime or routes."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
active_path = ROOT / '.opencode/liuren-active.json'
active_bytes = active_path.read_bytes()
active = json.loads(active_bytes.decode('utf-8-sig'))
runtime = ROOT / active['runtime']
modules = json.loads((runtime/'manifest.json').read_text('utf-8-sig'))['modules']

groups = [
 ('核题核盘', ['daliuren-paipan','nianming'], '核题后、采用相应数据前', '提供可靠课盘、已核年命；不预判吉凶'),
 ('取用与定侧重', ['class-mapping','positioning'], '初观课势后与对应占类共同使用', '确定角色、主类与相关类，说明切入主线；定位改变则回查依赖'),
 ('贯穿主线的方法', ['relations','liqi','void','structure','movement','shenjiang-use'], '随关键节点连续使用，部分方法按条件触发', '共用一条主线；不是六次独立判吉凶；保留旧必查覆盖，拟调整调用时机'),
 ('综合核查与定点复审', ['bashajiubao','engine-shensha-output','shensha-focus','shensha-use','risk','shensha-tradition'], '基础核查保留；相关项发现时立即参与，收束前再查漏', 'risk不设速断捷径；季煞等仍按原触发条件；未采用神煞不进入风险'),
 ('收束、应期与取数', ['adjudication','timing','quantity'], '主要作用辨清后收束；时间与数量按原问触发', '裁决处理争点与净作用；不以将名四象限统一乘算；应期取数可因主判修订回查'),
 ('参照与交付', ['evidence','report'], '相关方法原文可在争点处早查；两路案例经验在盘面初判后；报告最后', '区分原法核查与类案检索；完整正文交代依据和反证，避免机械重复'),
 ('单事专项', ['finance','recruitment','promotion-salary','relationship','interpersonal','pregnancy','exam','illness','lost-person-object','classical-conflict','home','travel','weather','agriculture'], '明占类即进入，贯穿该问', '不是末尾附录；提供本问取用、宜忌、重要关系和专法；各专项完整性仍待逐条审查'),
 ('泛占与长期专项', ['period-outlook','long-period'], '原问确属阶段或长期时分流', '不把单事流程机械铺成多维；不把长期专项等同出生推命完整规程'),
 ('方法与来源参考库', ['bifa','blade-methods','case-retrieval-v2','daliuren-shensha','experience-retrieval-v2','keti-quanbiao','kundun','liqi-examples','liqi-sources','rule-semantics','shensha-engine-index','shensha-field-meanings','shensha-meaning-sources','shensha-meanings','shensha-other-meanings','shensha-sources','quantity-sources','shen-symbols','jiang-symbols','mapping-provenance'], '遇到该规则、象义、起法或来源争点时定点回查', '参考身份不等于禁止参与判断；通用解释集中维护，专项只存差异；不要求每课读全库'),
 ('维护与可选审计', ['beihai-extend-sop','workflow-contract'], '维护任务或显式结构化审计', '不成为普通断课前置门禁'),
]
per_module = {
 'liqi': ('从前置成败裁判改为全程准则', '维护气态、作用、制救等共同判断准则；不把尚未察类的课体背景先冻结为结果'),
 'relations': ('放在取用后，并随节点复用', '负责坐标与关系事实；关系存在和作用得力分开，不独立给终局'),
 'void': ('嵌入类神及结构的真伪审查', '分空亡事实、作用、实现与应期；不同来源分支不能顺次自动执行'),
 'structure': ('分初观与深核两次用途，同一模块复用', '初观课势不先终判；选中切题结构后核组成关系、占类宜忌和变质'),
 'movement': ('从固定后置深化移到相关作用链旁', '关键作用涉及引动、直接阴神、年命时即时核；无新争点不无限扩层'),
 'shenjiang-use': ('从结论后的描述工具前移到取用和察类', '神将职能及有条件互换可以帮助定对象与辨事；本家映射不改真实课盘坐标和气态'),
 'class-mapping': ('保留取用入口，削弱机械九系统遍历倾向', '九系统用于有依据的候选；本问已有主取后不为齐全而制造全部人物和对象'),
 'positioning': ('侧重选择与返查的唯一维护位置', '明确选择侧重的理由；占类差异由专项给出，不在多处重复颁布全局顺序'),
 'adjudication': ('从吉凶调制改为反证与分歧收束', '保留原书神将组合方法供有条件引用；取消无条件四象限缩放作为候选改动，不删除原文'),
 'risk': ('从凶象速断出口改为相关节点复审', '核凶象的对象、位置、状态、有效制救和结论范围；不因命中凶名跳过全课'),
 'evidence': ('拆清方法原文回查与类案检索时机', '原法不明可即时查原段；类案和经验仍分别在盘面初判后复核，不用反馈替本案定结果'),
 'report': ('移出思维控制，负责最终交付覆盖', '完整判断原文保留；十一项覆盖映射内部使用，同一依据不在多个环节反复抄写'),
 'liqi-sources': ('统一维护具体来源口径', '当前对《笔记》的全局优先条款需随用户北海优先研究方向协调；原法出处与选用口径分开记录'),
 'period-outlook': ('单独的阶段泛占分支', '各维依对应对象判断，背景影响须说明作用；取消安全凶象使所有维度无条件打折的候选规则'),
 'long-period': ('与阶段泛占、出生推命分开', '时间范围及专法逐条核实；不能默认每限都经过将名四象限乘算'),
}
entries = []
for group, ids, timing, duty in groups:
    for module_id in ids:
        meta = modules[module_id]
        action, responsibility = per_module.get(module_id, ('按职责归组，保留ID与路径', duty))
        entries.append({'id': module_id, 'current_file': (runtime/meta['file']).relative_to(ROOT).as_posix(),
                        'proposed_group': group, 'call_timing': timing, 'change': action,
                        'responsibility': responsibility, 'status': '候选位置设计；未修改活动规则，未完成逐条语义验收'})
ids = [x['id'] for x in entries]
assert len(ids) == len(set(ids)) == len(modules)
assert set(ids) == set(modules)
payload = {'release_inspected': active['release'], 'status': '设计稿，未启用',
           'principle': '先调整职责、调用时机和单一维护位置；保留现有模块ID与文件路径，不为外观搬目录',
           'modules': entries}
(OUT/'模块重定位对照.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md = ['# 59个模块的候选重定位', '', payload['principle']+'。本稿不构成当前执行指令。', '',
      '59项无遗漏、无重复只表示位置映射完整；不能据此声称全部正文与来源已审完。现有共同必读和核查覆盖不在本轮删除。', '']
for group, ids, timing, duty in groups:
    md += [f'## {group}', '', f'进入时机：{timing}。', '', duty+'。', '', '| 模块 | 调整 | 负责什么 |', '|---|---|---|']
    for module_id in ids:
        row=next(x for x in entries if x['id']==module_id)
        md.append(f"| [{module_id}](../../{row['current_file']}) | {row['change']} | {row['responsibility']} |")
    md += ['']
md += ['## 四个技能入口与旧规程', '',
       '- daliuren：统一核题核盘、明占类、定侧重、察类与收束；只维护路由和共同行为，细则由对应模块负责。',
       '- liuren-cases：保留查询、反馈复盘和维护职责；只查资料不启动全套研判，判断当前事件时返回daliuren。',
       '- liuren-extract：保留来源提取与归纳职责；提取候选不自行成为活动规则。',
       '- liuren-tuiming：保留出生推命独立规程；只复用核盘及已核共同方法，不直接套单事侧重。',
       '- 三个归档完整规程须单独做条款迁移清单，核旧指令与当前约束；不为流程顺滑删掉归档或复活旧入口。', '',
       '## 单一维护位置', '',
       '共同准则归liqi；取用与侧重归class-mapping/positioning；空亡细则归void；结构条件归structure；具体象义归神将参考；占类差异归domains；争议收束归adjudication；来源选择归liqi-sources等来源文件。其他入口只引用，不重复改写同一条规则。', '',
       '需要同步的指令面包括AGENTS、本机模式提示、入口、reading-route、模块正文、报告和旧规程包装层。候选包完成后同时核一致性；本轮没有改写这些活动来源。']
(OUT/'模块重定位对照.md').write_text('\n'.join(md)+'\n',encoding='utf-8')

sources = [
 ('书籍库/北海闲人/理法简易.txt', 'utf-8-sig', [(2734,2751),(2768,2778),(2798,2804)]),
 ('书籍库/北海闲人/北海闲人，特训班讲义.txt','gb18030',[(70,81)]),
 ('书籍库/经典古籍/佚名/壬归.txt','utf-8-sig',[(283,301)]),
 ((runtime/'methods/void.md').relative_to(ROOT).as_posix(),'utf-8-sig',[(1,14),(28,46)]),
 ((runtime/'references/liqi-sources.md').relative_to(ROOT).as_posix(),'utf-8-sig',[(1,12)]),
]
evidence=[]
for filename, enc, ranges in sources:
    raw=(ROOT/filename).read_bytes()
    lines=raw.decode(enc).split('\n')
    evidence.append({'file':filename,'encoding':enc,'sha256':hashlib.sha256(raw).hexdigest(),
                     'line_convention':'LF一基闭区间；不等同splitlines；显示仅移除行末CR',
                     'windows':[{'lf_start':lo,'lf_end':hi,'text':'\n'.join(s.rstrip('\r') for s in lines[lo-1:hi])} for lo,hi in ranges]})
(OUT/'争议原文证据.json').write_text(json.dumps({'status':'限定原段，不是全书审查完成声明','evidence':evidence},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert active_path.read_bytes()==active_bytes
print(json.dumps({'mapped_modules':len(entries),'unique_groups':len(groups),'evidence_sources':len(evidence),
                  'active_pointer_unchanged':True},ensure_ascii=False))
