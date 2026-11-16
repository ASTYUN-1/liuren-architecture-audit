"""Create reviewable research artifacts; no writes outside this experiment folder."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
NODE=Path('C:/Users/QLMa_/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text('utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pointer=ROOT/'.opencode/liuren-active.json';active_before=sha(pointer);p=load(pointer)
runtime=ROOT/p['runtime'];manifest_before=sha(runtime/'manifest.json')
archive=ROOT/'排盘存档/六壬/六壬-20261108-180639-次日应聘结果及公司职位辨识-18cea112-d303-4c6f-a54f-d5a1d2e9da84.corrected-7d8f4da2258d400a.json'
archive_before=sha(archive)
command=[str(NODE),str(OUT/'prototype.mjs'),'extract',str(archive),str(OUT/'应聘盘-条件明细.json'),'four-seasons','未']
subprocess.run(command,cwd=ROOT,check=True)
subprocess.run([str(NODE),str(OUT/'prototype.mjs'),'demo','unused',str(OUT/'合成算例-数值核对.json')],cwd=ROOT,check=True)
script="import {composeBase,syntheticModel,sweepCoefficient} from './output/liuren-energy-prototype-20261108/prototype.mjs'; import fs from 'node:fs/promises'; const root='output/liuren-energy-prototype-20261108/'; await fs.writeFile(root+'基点比例-合成算例.json',JSON.stringify(composeBase({baseline:5,adjustments:[{cause_id:'synthetic-add',points:3,parameter_id:'synthetic-a',basis:'算术演示，不是月令系数'}],multipliers:[{cause_id:'synthetic-retention',factor:0.8,parameter_id:'synthetic-r',basis:'算术演示，不是空亡比例'}]}),null,2));await fs.writeFile(root+'敏感性-合成算例.json',JSON.stringify(sweepCoefficient(syntheticModel(),'synthetic-c',[0,0.1,0.2,0.3,0.7]),null,2));"
subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,check=True)
features=load(OUT/'应聘盘-条件明细.json');nodes={n['id']:n for n in features['nodes']}
doc='# 应聘案例：未赋权条件与计算明细\n\n仅供研究开发，已知用户反馈，不是新盲测。未给月令、十二气、空亡或神将编造权重。本页输出关系条件，真实盘最终数值留空。\n\n'
doc+='| 对象 | 月令五气 | 直接状态 | 空亡身份 | 数值 |\n|---|---|---|---|---|\n'
for id in ['G:庚','T:申','J:白虎','T:午','T:戌','T:子','T:酉']:
 n=nodes[id]
 if n['kind']=='日干': state='寄'+n['home']+'为'+n['growth_at_home']+'；上神'+n['upper']+'为'+n['growth_at_upper'];void='日干与寄宫分列'
 elif n['kind']=='天将':state='乘'+n['carried_by']+'为'+n['growth_at_carrier']+'；临'+n['ground']+'为'+n['growth_at_ground'];void='不自动复制乘支空亡效应'
 else:state='临'+n['ground']+'为'+n['growth_at_ground'];void='自身'+('旬空' if n['void_self'] else '不空')+'；坐处'+('空' if n['void_ground'] else '不空')
 doc+=f"| {id} | {n['season']} | {state} | {void} | 待参数 |\n"
doc+='\n## 神将与地盘联合条件\n\n'
for b in ['申','午','戌','子','酉']:
 f=next(f for f in features['local_factors'] if f['participants']['heaven']=='T:'+b)
 tags='、'.join(k for k,v in f['conditions'].items() if v) or '未触发完整内外战/夹生夹克条件'
 doc+=f"- {f['id']}：{f['participants']['general']}—T:{b}—{f['participants']['earth']}；地→神：{f['signature']['ground_to_heaven']}；神→将：{f['signature']['heaven_to_general']}；{tags}。\n"
doc+='\n## 旬空原因与重复计数\n\n'
for root in features['condition_roots']:doc+=f"- {root['id']}：原局身份保留，作用系数待定；同一根条件不另当多个独立证据。\n"
doc+='\n## 局势候选\n\n'
for g in features['group_candidates']:
 doc+=f"- {g['scope']}／{g['type']} {''.join(g['members'])}：实际出现{''.join(g['present'])}，缺{''.join(g['missing']) or '无'}；仅登记成员，尚未判定成局起效或合化。\n"
doc+='\n本盘按four-seasons抽取；申月两套现有季土表的季节结果在本问一致，但其他月份不得自行挑选。实际旬空身份不因最终强度分数而改变；空的影响须进入已登记的联合因子，不能在算完后另加失败否决。\n'
(OUT/'本案计算明细.md').write_text(doc,encoding='utf-8')
register={'schema':'liuren-energy-parameter-register-v0.1','status':'research-unassigned','baseline_display':5,
 'zero_reference_conversion':'Z=E-5; proportional losses act on E, not directly on signed Z',
 'parameters':[
  {'id':'seasonal_delta','value':None,'scope':'月令对本体','basis':'U07、壬归E11；具体点值未定'},
  {'id':'joint_ground_growth_relation','value':None,'scope':'临地十二气与地盘生克的联合条件','basis':'北海E02/E04；防止同一坐处重复扣加'},
  {'id':'joint_general_carrier_ground','value':None,'scope':'神将搭配、神将十二气、完整内外战','basis':'壬归E09/E12，按占类范围'},
  {'id':'conditional_void_retention','value':None,'scope':'分对象、位置、旺衰、生扶受制及时段','basis':'U08；禁止自动归零或事后空亡否决'},
  {'id':'support_leak_control','value':None,'scope':'施受双方强弱、通路及耗益','basis':'需要相应原法和样本校准'},
  {'id':'joint_punishment_union_groups','value':None,'scope':'刑合、生合克合、三合三会','basis':'北海E04及对应专法；不自动合化'},
  {'id':'activation_and_intended_action','value':None,'scope':'发用参与及贪生合对目标作用','basis':'用户要求、U03；无固定倍数'},
  {'id':'temporal_update','value':None,'scope':'保留原盘的评价时段变化','basis':'U10；不重排原盘'}],
 'constraints':['复用相同规则与参数，不按本案答案定系数','同一真实原因不重复计为独立因子',
 '所有数值与公式保留来源身份和假设身份','本体强弱、作用性质、作用目标与事件成败分列']}
dump(OUT/'参数登记.json',register)
ev=load(runtime/'references/adjudicator-book-evidence.json')['evidence']
selected=[row for row in ev if row['id'] in ['E02','E03','E04','E09','E11','E12']]
for row in selected:
 src=ROOT/row['path'];assert sha(src)==row['sha256']
 lines=src.read_text(row.get('encoding','utf-8-sig')).splitlines()
 assert '\n'.join(lines[row['line_start']-1:row['line_end']])==row['quote']
dump(OUT/'依据与边界.json',{'source_evidence':selected,'source_identity':'古籍与北海本地转录，原文逐段核对',
 'math_design_identity':'5基点、范围、加减比例次序、网络方程、制约函数和收敛条件为本轮研究设计',
 'active_release':p['release'],'active_method_version':p['methodVersion'],
 'archive_path':str(archive),'archive_sha256':archive_before,
 'case_exposure':'用户已给任职及A反馈，仅作开发样例，不进行调参命中测试'})
tests=subprocess.run([str(NODE),'--test',str(OUT/'prototype.test.mjs')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
(OUT/'tests.log').write_text(tests.stdout+tests.stderr,encoding='utf-8');assert tests.returncode==0,tests.stdout+tests.stderr
assert sha(pointer)==active_before and sha(runtime/'manifest.json')==manifest_before and sha(archive)==archive_before
dump(OUT/'verification.json',{'research_only':True,'active_pointer_unchanged':True,'runtime_manifest_unchanged':True,
 'chart_archive_unchanged':True,'real_case_score_assigned':False,'calibrated':False,'predictive_validation':False,
 'nodes_extracted':len(features['nodes']),'local_joint_factors':len(features['local_factors']),
 'source_passages_verified':len(selected),'tests_passed':12,'new_model_calls':0})
print('Research prototype built: 12 tests passed; 5/0 coordinates, exact ledgers and sensitivity example; real chart unscored; active workflow unchanged.')
