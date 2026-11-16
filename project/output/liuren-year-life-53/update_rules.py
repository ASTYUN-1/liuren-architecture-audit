"""Apply the user's input-adoption policy to the new, unpublished runtime only."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];T=R/'runtime/liuren/20261112-year-life-53'
def replace(path,old,new):
 text=path.read_text('utf8');assert old in text,(path,old);path.write_text(text.replace(old,new),'utf8')
p=T/'references/nianming.md';text=p.read_text('utf8')
a=text.index('## 年界、虚岁及坐标校验');b=text.index('## ② 行年',a)
text=text[:a]+'''## 用户输入采用与工具计算（53版）

这是用户已确认的本机输入约定。**用户明确给出的出生年份、本命、行年必须采用；不因缺少出生月份、生日、年龄或所谓“未经独立核验”而弃用，也不要求用户再证明已明确给出的信息。** 输入来源身份与预测准确性是两回事。

- 出生年用`participants:[{"birth_year":"05","sex":"男"}]`，也接受2005、99等。日期盘按占课公历年展开为最近不晚于占年的同尾数年份；2026年课05即2005，99即1999。四柱模式没有公历占年时，固定00—49按2000—2049、50—99按1950—1999，不借主机年或显示参考日期定世纪。
- 只给公历出生年时，按该年编号的常用干支整年映射，如2005→乙酉→酉命。这是工具默认采用约定，不要求出生月日。若用户另报明确本命，以明确本命为先；只有真实出现不一致时才局部记录差异，不以“可能在年界”普遍阻止使用。
- `birth_pillar:"甲子"`、`birth_pillar:"申"`或`birth_branch:"申"`均可。单支已足以采用本命及计算行年支，不能要求补天干或倒猜唯一出生年。
- `xingnian:"戌"`、`xingnian:"甲戌"`或`xingnian_branch:"戌"`是用户明确行年，直接采用；程序预期不同只在conflicts注明，不能静默覆盖或把年命全停用。仅知行年时，给定性别及占课年柱还可反推本命支；完整干支可按60甲子反推。
- 性别决定行年顺逆。缺性别仍照常采用已知本命；工具提供男女行年候选，不能捏造性别，也不能连本命一起不用。用户已报行年时该行年照用，缺性别只影响需要反推的分支。
- 同一人资料放同一对象；兼容participants与declared_life同下标合并。多个人按顺序分别登记，以P1/P2对应实际对象，不传姓名、不把代问者年命借给当事人。

新盘直接读`facts.year_life.participants`。每人分别给birth、xingnian、输入来源、计算口径、坐标、缺项及局部冲突；birth与xingnian内的position列地盘支、天盘上神、所乘将及直接阴神。不再把旧userinfo的`year_life_verified:false`当作新回执不可用的开关；该旧标志仅描述原引擎userinfo。

已有同盘补充年命，用`liuren_compute(action="life",archive=原archive,life={...})`，不重新起课。准备新裁决时把同一life输入放`computation_requests:[{"id":"C_life","action":"life","life":{"birth_year":2005,"sex":"男"}}]`，程序在`program.calculations`携带真实回执；不能只口头说“已知”却不交给裁决者。裁决者已有本任务盘时不另传archive。不得回写历史任务报告。

传统虚岁仍可用`age`与`age_basis:"虚岁"`或兼容`"虚岁-已核"`。不带age_basis的旧age保留为原工具参数，不冒充虚岁；出生年应传birth_year。年龄、生日不是本命/行年支循环计算的前置门槛。

占课年只取可信盘年柱。只知本命支时，以占课年支减本命支所得12支循环步数，男自寅顺、女自申逆；知本命完整干支则用60甲子步数，能导出完整行年干支。此法不需要反推唯一出生年份，不生成无据年龄。

用户已给年命时，应定位其上神，并结合本问主体、主类、作用和制救评估是否相关，不能以“不是专问年命”为由漏用。年命可以支持或反证本问，仍不机械凌驾于分类取用或单项断吉凶。

''' + text[b:]
old='引擎年命/行年口径尚未独立核验，输入、年龄、年界或坐标未齐时保留条件分支，不以程序已导出代替核验。'
assert old in text;text=text.replace(old,'新适配层已提供用户输入采用、循环计算与坐标回执；直接使用，不以旧引擎核验缺口拒用。工具不替代本问吉凶、有效作用和预测准确性的专业判断。')
p.write_text(text,'utf8')
replace(T/'references/judgment-core.md','及已核年命寻类','及用户给定/工具换算的年命寻类')
replace(T/'references/judgment-core.md','有时间、数量、年命任务才补相应方法；','时间、数量按问补相应方法；用户已给出生年/本命/行年即采用并核其本问作用，不要求另有年命子问；')
replace(T/'references/judgment-core.md','正常年命/行年可用且资料需已核，不作出生推命。','用户明确年命/行年直接采用，出生年（05→2005、99→1999）交工具换算；只知本命支也能结合性别和占课年柱算行年支。不得因无生日/出生月、年龄未核或旧userinfo未验证而停用。新盘读year_life，同盘补算用compute life并带回执入裁决材料；缺性别仅列男女行年候选，本命照用。具体输入及坐标见nianming，不作出生推命。')
replace(T/'methods/movement.md','年命/行年只用已核输入，','年命/行年用用户明确输入或新year_life计算回执，不因无生日弃用；')
replace(T/'domains/long-period.md','输入、年界和年龄口径明确时复用可信程序life计算；旧引擎未核字段不得冒充该回执，真实输入冲突具体披露，不由模型静默改盘。','用户给出生年、本命或行年即交新year_life/life工具直接采用或换算；无出生月日不阻断。旧userinfo标志不否定新回执，真实输入冲突只具体披露相应字段，不由模型静默改盘。')
replace(T/'domains/period-outlook.md','已核行年用于当前状态','用户明确或工具换算的行年用于当前状态')
replace(T/'references/deterministic-tools.md','旧userinfo年龄/年命未独立核验，禁止用它自动替代已核年命。','旧userinfo年龄/年命的未核验标志只约束该旧字段。新year_life按用户明确输入采用、工具循环计算和定位，不能被旧标志否定。')
replace(T/'references/deterministic-tools.md','life仅接受明确sex、age整数、age_basis="虚岁-已核"，可带用户已给birth_pillar。按references/nianming.md男一岁丙寅顺数、女一岁壬申逆数；程序不从本命猜出生年、年龄或年界。','life接受birth_year（2005/05/99）、birth_pillar（甲子/申）、birth_branch、xingnian（干支/单支）或xingnian_branch及可选sex；兼容age+age_basis="虚岁"/"虚岁-已核"。用户给定直接采用，无需生日。按nianming男一岁丙寅顺、女一岁壬申逆，占年绑定可信盘年柱。只知本命支能算行年支，缺性别列男女候选且本命照用。新盘读facts.year_life；同盘补充资料可用computation_requests的life请求，把真实回执装入裁决核心。程序不倒造唯一出生年、天干或年龄。')
replace(T/'references/adjudicator-prompt.md','仅按问补时间/数量/年命。','时间/数量按问补；用户给出生年、本命或行年即采用新year_life或life回执，核其本问作用，不因缺生日/年龄未核/旧userinfo标志弃用。单本命支足够计算行年支，缺性别只保留男女候选，本命照用。')
entry=R/'.opencode/skills/liuren/daliuren/SKILL.md'
replace(entry,'年命行年正常采用，出生推命退出。','用户给出生年、本命或行年即交year_life/life采用并核本问作用；05/99按约定展开，单支本命可用，不因无生日弃用，缺性别只影响行年候选。出生推命退出。')
(T/'entry.md').write_bytes(entry.read_bytes())
replace(T/'methods/positioning.md','年命归属明确，未知不借用代问者。','年命归属明确，未知不借用代问者。用户提供出生年/本命/行年即采用并交工具换算定位，不要求出生月日或另问年命；缺性别保留行年候选，本命仍使用。')
doc=R/'docs/本机六壬直接排盘.md';text=doc.read_text('utf8');old=next(l for l in text.splitlines() if l.startswith('- 出生年与性别明确时'))
replace(doc,old,'- 用户给出生年份、本命或行年即传participants，或兼容declared_life：`[{"birth_year":"05","sex":"男"}]`、`[{"birth_pillar":"申","sex":"女"}]`、`[{"xingnian":"戌"}]`均可；2005、05、99无需生日。新回执facts.year_life直接采用；只知本命支也可算行年支。缺性别本命照用，列男女行年候选。旧userinfo的year_life_verified只描述旧原工具，不否定新回执。同人放同一对象，两数组同下标合并，不传姓名；默认年份展开及明确输入优先见活动nianming。')
replace(R/'docs/本机六壬完整研判流程.md','年命、应期和数量按问触发。','应期和数量按问触发；用户已给出生年/本命/行年即交year_life/life采用并核本问作用，无需出生月日。同盘补充用life及computation_requests携带回执，不重新起课。')
for name in ['README.md','目录总索引.md']:
 path=R/name;text=path.read_text('utf8');text=text.replace('20261112-consistency-52','20261112-year-life-53');path.write_text(text,'utf8')
replace(R/'AGENTS.md','正常年命/行年、长期占事与应期保留，','用户明确出生年/本命/行年直接采用，新year_life/life换算定位；05/99按约定展开，单支本命足够，不因无生日或旧userinfo标志弃用，缺性别只影响行年候选。正常年命/行年、长期占事与应期保留，')
c=R/'.opencode/oh-my-opencode-slim.jsonc';data=json.loads(c.read_text('utf8'));data['agents']['liuren-adjudicator']['prompt']=(T/'references/adjudicator-prompt.md').read_text('utf8');c.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
m=json.loads((T/'manifest.json').read_text('utf8'))
m['modules']['nianming']['trigger']='用户提供出生年、本命或行年：直接采用及工具计算，缺生日不阻断；详细算法或坐标按需核对'
m['conditional']['nianming']=m['modules']['nianming']['trigger']
m['modules']['deterministic-tools']={'file':'references/deterministic-tools.md','required':False,'requires':[],'trigger':'确定性工具参数或回执使用有真实缺口时按需查，不增加常规通读'}
m['conditional']['deterministic-tools']=m['modules']['deterministic-tools']['trigger']
(T/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
print('Updated input adoption in rules, prompt, tool guide and local entry')
