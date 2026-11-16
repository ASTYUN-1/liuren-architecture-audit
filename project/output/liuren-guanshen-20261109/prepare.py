"""Prepare a new local frozen runtime; do not change the active pointer."""
from pathlib import Path
import json, hashlib, shutil

ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
OLD='20261109-deterministic-tools-35'; NEW='20261109-guanshen-36'
BASE=ROOT/'runtime/liuren'/OLD; R=ROOT/'runtime/liuren'/NEW
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def dump(p,d):write(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def evidence(p,a,b,topic,role):
 f=ROOT/p; lines=f.read_bytes().decode('utf-8-sig').split('\n')
 return dict(path=p,sha256=sha(f),line_start=a,line_end=b,
             quote='\n'.join(x.rstrip('\r') for x in lines[a-1:b]),topic=topic,role=role)

assert load(ROOT/'.opencode/liuren-active.json')['release']==OLD
assert not R.exists(),'Do not overwrite a prepared runtime'
files=['.opencode/liuren-active.json','.opencode/oh-my-opencode-slim.jsonc','opencode.json',
       'tools/tests/liuren-shensha.test.mjs','AGENTS.md','README.md','目录总索引.md']
before={'release':OLD,'files':{f:sha(ROOT/f) for f in files},
        'frozen':{p.relative_to(BASE).as_posix():sha(p) for p in BASE.rglob('*') if p.is_file()}}
dump(OUT/'before.json',before)
for f in files:
 dst=OUT/'before'/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/f,dst)
shutil.copytree(BASE,R)
guide='书籍库/神煞资料/413711725175564精校大六壬指南(珍藏全本).txt'
beihai='书籍库/北海闲人/理法简易.txt'
bifa='书籍库/北海闲人/毕法赋全解-正式整理本.md'
tanyuan='书籍库/排盘引擎内置资料/大六壬探原.txt'
duanan='书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt'
new_evidence={
 'A24':evidence(guide,2224,2237,'四季关神起表及关神、管神身份','本地古籍电子文本，未校原刻'),
 'A25':evidence(beihai,2481,2496,'出行关墓阻隔、冲关破墓；季关神与罗网分列','北海闲人讲解本电子文本'),
 'A26':evidence(bifa,3300,3310,'关墓组合、旺库及掌管仓库吉用','北海闲人讲解正式整理本，非原刻影印')}
p=load(R/'references/shensha-policy.json');p['release']=NEW
rule=dict(id='S33',name='季关神',basis='season',table=list('丑辰未戌'),sources=list(new_evidence),
          formula='春丑夏辰秋未冬戌',aliases=['关神'],priority='primary',authority_review='source_checked')
assert all(x['id']!='S33' for x in p['rules']);assert '关神' not in p['disabled']
p['rules'].append(rule);dump(R/'references/shensha-policy.json',p)
ev=load(R/'references/shensha-authority-evidence.json');ev['release']=NEW
ev['evidence'].update(new_evidence)
ev['reviews'].append({**{k:rule[k] for k in ['id','name','basis','formula','table']},
 'status':'source_checked','evidence_refs':list(new_evidence),
 'limitations':'本次采用四季关神，不将罗网纳入同一表；阻隔及关墓作用须核对象、位置、状态和冲解；掌管仓库有吉用。与寡宿同表不同义，不重复计证。电子文本核查未校原刻，无独立预测验证。'})
ev['summary'].update(registered=39,direct_source=36);dump(R/'references/shensha-authority-evidence.json',ev)
for f in ['reading-route.json','references/confirmed-policy-register.json']:
 d=load(R/f);d['release']=NEW;dump(R/f,d)
policy='''## 36版新增采用：季关神 S33

用户明确加入关神。可信盘按月建节月定季，寅卯辰春、巳午未夏、申酉戌秋、亥子丑冬；季关神春丑、夏辰、秋未、冬戌，直接使用程序S33，不自行重算。神煞属于天盘支，所临地盘不是其归属支。当前39条规则，原38条起法不变，22个停用名称不变。

关神主阻隔不通。出行关墓临干有难动之象，须结合原段的冲关破墓、用传年命及斩关等条件，不能见关便断不能动。关与墓的组合须分别核定；关神不自动等于入墓、罗网或管神。北海讲解还保留掌管仓库时关神入课的吉用，仓库大小、业务旺等须另核墓旺为库条件；不将它写成一律凶煞。具体原段与版本身份见shensha-authority-evidence的A24—A26及shensha-meanings。S23寡宿与S33同季表而身份、义项有别，不合并，也不把同一落点的两个名称自动算作两份独立证据。是否切题及实际作用仍依现行专业方法裁定。
'''
for f in ['references/judgment-core.md','references/adjudicator-prompt.md','references/confirmed-judgment-policy.md']:
 write(R/f,(R/f).read_text('utf-8')+'\n\n'+policy)
for f in ['shensha-use.md','shensha-authority-review.md','shensha-authority-conflicts.md','shensha-sources.md']:
 target=R/'references'/f;s=target.read_text('utf-8')
 s=s.replace('固定38条规则及常用32项','固定39条规则（原常用32编号族及细分项，另增S33关神）')
 s=s.replace('38项','39项').replace('35项','36项')
 write(target,s+'\n\n'+policy)
target=R/'references/shensha-authority-review.md'
write(target,target.read_text('utf-8')+'\nS33直接依据：A24《神煞指南》LF2224—2237季表；A25《理法简易》LF2481—2496；A26《毕法赋全解》整理本LF3300—3310。39条中36条直接表文/规则、2条旬内推算、1条部分采用；预测验证数仍为0。\n')
target=R/'references/shensha-meanings.md'
write(target,target.read_text('utf-8')+'\n\n'+policy)
target=R/'references/shensha-other-meanings.md'
s=target.read_text('utf-8').replace('| M036 关神 | 行动处受阻、灾滞。 | 出行、办事或关口的阻点须具体定位，区分延迟与最终办不成；不与闭口、入墓混成一个标签。 | ME-05、SF-11；象义转述；取用为条件化整理 |',
 '| M036 关神（已采用S33） | 阻隔不通；与墓相并有专门条件；掌管仓库有吉用。 | 出行核关墓临干及冲解、斩关，不能见关即断不行；仓库事项区分旺库条件和掌管仓库吉用。关神、管神、罗网及寡宿身份分开，同表不重复计证。 | A24—A26；古籍表文与北海讲解分列；当前采用四季关神 |')
write(target,s)
target=R/'references/shensha-engine-index.md'
s=target.read_text('utf-8').replace('| 关神 | ji | 补充释义：[M036](<shensha-other-meanings.md>) | 已录基本象义；同名跨组起法和当前命中仍分别核。 |',
 '| 关神 | ji | 已采用S33季关神；释义：[M036](<shensha-other-meanings.md>) | 春丑夏辰秋未冬戌；天盘归属；关墓、冲解及仓库吉用见A24—A26。 |')
write(target,s)
all_evidence={**new_evidence,
 'D01':evidence(tanyuan,108,116,'德煞八种序言','原书电子文本'),
 'D02':evidence(tanyuan,2102,2194,'德合鬼墓破害刑冲八章正文','原书电子文本，含作者按语'),
 'D03':evidence(beihai,3084,3120,'神煞按占类选取、记忆和象意理解','北海闲人讲解本电子文本'),
 'D04':evidence(beihai,604,612,'多方面事情兼看多个类神','北海闲人讲解本电子文本'),
 'D05':evidence(guide,2083,2106,'神煞指南署名与刑克原句','古籍电子文本，未校原刻'),
 'D06':evidence(duanan,883,891,'毛主簿占前程：破碎与会起冲起','原载案例及析语，现实反馈未独立核验'),
 'D07':evidence(duanan,2169,2177,'陆孔目：本命破碎；题头与断语日支文字不一','原载案例及析语，文字存在待校处'),
 'D08':evidence(tanyuan,2068,2076,'年命为变体门的通行论述','原书电子文本')}
dump(OUT/'原文核查证据.json',{'schema':'liuren-source-check-v1','release':NEW,'evidence':all_evidence,
 'independent_prediction_validation':0,'scope':'本轮连续原段核对，非全书校勘；未将其他推荐神煞接入'})
dump(OUT/'candidate.json',{'release':NEW,'runtime':R.relative_to(ROOT).as_posix(),'rules':39,'direct_source':36,
 'previous_rules_unchanged':p['rules'][:-1]==load(BASE/'references/shensha-policy.json')['rules'],
 'disabled_unchanged':p['disabled']==load(BASE/'references/shensha-policy.json')['disabled']})
print('Prepared',NEW,'; active pointer unchanged')
