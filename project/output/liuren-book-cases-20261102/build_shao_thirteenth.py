"""Manual full reading 210–222 to the end; missing source 218 is not fabricated."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];S='书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt'
raw=(R/S).read_bytes();ls=raw.decode('utf-8-sig').splitlines();sha=hashlib.sha256(raw).hexdigest()
def ref(a,b,**extra):return dict(path=S,line_start=a,line_end=b,quote='\n'.join(ls[a-1:b]),sha256=sha,role='原书断语',**extra)
specs=[
 (210,2169,2185,'陆孔目占官事：独足留本州与飞散再配','官讼占','原己未日题与正文今日又是巳日不一致；初本州后润州分阶段。独足不行有行年飞散例外，字像润取法是原析不改算法；与207陆孔目年命年龄不同不据同称合案。'),
 (211,2186,2198,'某占讼：刑德优先与未了一事又起','官讼占','原庚午午龙为刑胜德、中巳助、末罡加身链条保留；果然为笼统原叙，未补杖数或具体新讼。'),
 (212,2199,2211,'某占讼：先枷后释与德合龙救','官讼占','先枷后无事分阶段，原丙申被枷而后释；不因最终无事删最初受拘，也不只抄曲直先曲后直而删日德合末龙。'),
 (213,2212,2224,'打死人解官占：今免与六年后恶死','官讼占','题辛丑子将未时但盘与前206同式，且正文天后发用/盘玄卯不同，全文照存标课文冲突；恩赦编管与六年后二人一缢一刑分阶段，两人不各当独立样本。'),
 (214,2225,2236,'杀死二人占决：乱首夹克与处决','官讼占','原恐死不完尸、后处决只明确死刑，不造不完尸具体方式；上下夹克、自刑及虎墓为原条件，不当现代司法结果保证。'),
 (215,2237,2249,'张大郎占官事：先徒罪后恩赦','官讼占','果然只笼统叙，天喜龙解神与初刑虎分阶段；原课未补课体、丙戌十二月设置保留，非引擎核算通过。'),
 (216,2251,2260,'沈保正占役事：拒役监系与认役平安','事业占','任保正、拒役、认役和晚复役分支分开；原九年再做有反馈但未载精确推九来源，不能从末复做倒补九年算法；亲眷内鬼未独立列实证。'),
 (217,2261,2276,'沈四公争保正：绝中又起与翁墓僧子','事业占','原庚戌出生至戊申59为原载，不擅校历；陋贵子等字样保留。争役已听劝与未听分支、后葬地儿为僧叙事区分，墓地生子因果未独立认证。'),
 (219,2277,2291,'潘道士占住持：先成后失与朱姓异说','事业占','原春炎上说有头无尾是作者取法，原九月与六月至次年二月共九月为时长而非必农历九月；午未像朱与附订离朱雀反驳分开；217后直接219不补218。'),
 (220,2292,2305,'长老常占：库盗与连带三命','杂事占','初原阳刃大吉句与全课凶并存不擅改；旬日内与第七日属于范围相容，三物和三命不同对象，库盗、汪被击、行者狱死、僧杖死为同一连带事件链。'),
 (221,2306,2318,'某占求酒：酒败器破与无酒','杂事占','求酒目标，器破与酒败为原取象；未另载实得不得反馈，不能把理论说明当独立验证。'),
 (222,2319,2328,'蔡京占长星应身：目下挠与后再用','事业占','原后庚寅再入朝，与后按丙戌免丁亥复用史年叙不一致，全保留；2327四上克下无禄与久困发居家出为附通论另标未知署名，不拼为邵氏断该案；书后署记另存覆盖审计。'),
]
records=[]
for n,a,b,title,cat,note in specs:
 records.append(dict(schema='liuren-book-case-v1',id=f'BK26-SHAO-{n:03}',title=title,book_title='六壬断案（本地邵彦和案例集）',category=cat,
  source_case_identity=f'book:{S}:L{a}-L{b}',review_state='source_checked',completeness='complete',boundary_note=f'逐字审读{a}–{b}与相邻标题或书尾；保留未编号附论与源号218缺失，书末署记不当新事件。',
  question='本轮据原题概括：'+title.split('：')[0],authors=['邵彦和（按原载）','爱圅及其他编注者（按署名）'],source_refs=[ref(a,b)],missing_fields=[],
  feedback_status='未载明确反馈' if n==221 else '原载断语与结果混合',method_rule_ids=[],same_event_ids=[],chart_fields={},
  chart_status='现存完整课式文本照存；未引擎复核；冲突另列',notes=[note,'全部历史原载未独立验证；同事件阶段及多人不自动拆算独立样本。'],logic_stages=['问事目标','条件链','阶段反转','反馈差异']))
 if n in (210,222):records[-1]['text_consistency']='conflict'
 if n==213:records[-1]['chart_consistency']='conflict'
by_n={int(x['id'].rsplit('-',1)[1]):x for x in records}
defs=[
 (210,'独足先不行仍有行年并聚飞散导致再外配的例外',2176,2177,
 ['己未独足酉三传、己巳命、原行年并日辰而飞散。'],
 '作者先以独足不行论本州配，后又以行年并聚飞散论再外配；独足不动不能脱离阶段与行年变成永久不外出。',
 ['先存本州不行判断。','行年并聚、末飞解释第二阶段。','酉亥丑西北及润字像是作者附析而非引擎规则。'],['题己未日与正文巳日冲突待校；与195寻婢独足例后续对读。']),
 (211,'官讼先刑德，仍须中助刑末罡的完整作用链',2193,2193,
 ['庚午午龙为用，午火刑胜德，中巳助午，末辰加庚。'],
 '保存作者凡官讼先刑德的取舍顺序及本案中末配合，不能只抄青龙发用吉或单午为刑即所有讼败。',
 ['午刑庚德，比较胜负。','中巳助午伐德。','末罡加日本与一事未了又生分开。'],['果然笼统未逐项另证，未加杖数或判刑期限。']),
 (212,'曲直先曲后直须连德合与末龙救应，先拘后释分阶段',2206,2206,
 ['乙未申勾加身为鬼，又日德合、末未龙。'],
 '原作者将枷拘与后释分段，用申勾鬼解释先曲、德合末龙解释后直；不能只据曲直课名保证胜诉。',
 ['申勾克身先见拘。','日德合及末龙为后救。','原丙申被枷后疏放保持顺序。'],['本案并不支持全程无损或任何曲直皆无罪。']),
 (213,'暂免与六年后恶死为不同阶段，不把救应写成终身免灾',2219,2219,
 ['打死人解官，本次恩赦编管、六年后两人再打死人。'],
 '原断本次免难并存六年后凶，反馈本次恩赦和后来两人异死分别归位；一次免死不是永久免刑。',
 ['本次凶中有免。','六年后二人再犯分开。','一缢一刑同事件链不当两独立验证。'],['正文天后发用与盘玄卯冲突待校，本卡只保存明确阶段逻辑，不选唯一盘法。']),
 (216,'役事要分不认受系、认后安与晚复做的条件分支',2258,2260,
 ['沈保正乙见酉蛇官鬼，初寅空、中未、末子勾。'],
 '原作者按是否认役区分监系与平安，再以末传解释晚年复役；不同条件不能并成不管如何皆平安。',
 ['酉蛇官制身与寅公吏说明不能脱。','中传认后无虑分支。','末子勾为晚复做，九年是反馈而无精确推数。'],['内鬼细断未另证；不将原役制判断当现代任职法律建议。']),
 (219,'住持先以日我支位，先成后失与朱姓两解分开',2284,2286,
 ['潘道士春炎上，日为我支为住持，刃后加支、丑空暗贵。'],
 '作者先定人与住持对象，再区分暗贵空门促成和刃后因妇受责；朱姓原字像说被附订离朱雀说反驳，保留两者署属。',
 ['日我支住持明确对象。','丑空荐贤暗贵取先成。','刃后与传出取后受责，姓氏异说单列。'],['原九月是九个月时长与叙相连，不简化成农历九月精确断应；炎上短暂非普适任期规律。']),
 (222,'四上克下无禄通论仍分久困发与居家出情景',2327,2327,
 ['书末未单署名附论，四上克下纯阳主动。'],
 '附论虽名无禄，仍按久困在下与居家分别论发、出；保存情境取舍，不从无禄课名直接抽成一切不利。',
 ['四上克下原命名。','纯阳主动原解释。','久困发、居家出为不同情境。'],['此为书末通论未知单独署名，不能直接归邵先生已断本案；蔡京史年异文未解决。']),
]
rules=[]
for n,title,a,b,conditions,conclusion,steps,exclusions in defs:
 r=by_n[n];rid=f'LR26-BOOK-SHAO-{n:03}';r['method_rule_ids']=[rid];cr=dict(r['source_refs'][0],case_id=r['source_case_identity'])
 rules.append(dict(schema='liuren-rule-card-v1',id=rid,title=title,categories=[r['category']],claim_origin='原文明示',review_state='source_checked',status='source_method',conditions=conditions,conclusion=conclusion,reasoning_steps=steps,exclusions=exclusions,
  alternatives=['保留原作者/附订/无署名通论的区别；全案精提取与C归并未完成。'],evidence_refs=[ref(a,b)],source_case_refs=[cr],source_case_ids=[cr['case_id']],support_case_ids=[r['id'],cr['case_id']],counterexample_case_ids=[],legacy_entry_ids=[],relations=[],limitations=['历史原载非独立验证；排盘、细数量和古代因果未全面核算。'],independent_validation_count=0,logic_stages=['问事对象','作用取舍','阶段及例外','反馈范围']))
for relative,batch in [('book-cases/shao.json',records),('rules/book-shao.json',rules)]:
 p=R/'knowledge/liuren-research/20261102'/relative;d={x['id']:x for x in json.loads(p.read_text(encoding='utf-8'))};d.update({x['id']:x for x in batch});p.write_text(json.dumps(list(d.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'output/liuren-book-cases-20261102/shao-candidates.json';d=json.loads(p.read_text(encoding='utf-8'));d['reviewed_case_ids']=[x['id'] for x in json.loads((R/'knowledge/liuren-research/20261102/book-cases/shao.json').read_text(encoding='utf-8'))];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
from refresh_shao_coverage import refresh
refresh(R)
print(json.dumps({'new_cases':12,'new_methods':7,'read_range':[2169,2332],'source_number_gap':218},ensure_ascii=False))
