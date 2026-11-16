from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
trial=OUT/'real-rerun'
r=load(trial/'experiment-result.json');run=load(trial/'run-summary.json');before=load(OUT/'before.json');p=load(ROOT/'.opencode/liuren-active.json')
for rel,h in before['runtimeFiles'].items():assert sha(ROOT/before['runtime']/rel)==h,rel
for group in [p['workflowImplementation'],p['bookRetrieval']['files']]:
    for rel,h in group.items():assert sha(ROOT/rel)==h,rel
run['fullChainCompleted']=r['fullChainCompleted'];run['completionEvidence']='experiment-result.json (post-run saved delivery collection)';dump(trial/'run-summary.json',run)
changed={}
for f in (OUT/'before').rglob('*'):
    if f.is_file():
        rel=f.relative_to(OUT/'before').as_posix()
        if sha(ROOT/rel)!=sha(f):changed[rel]={'before':sha(f),'after':sha(ROOT/rel)}
pass_run=bool(r['fullChainCompleted'] and not r['toolErrors'] and r['originalSessionUnchanged'] and not r['caseOrExperienceToolsUsed'])
wire=load(OUT/'current-wire.json')
for rel,h in wire['implementationSha256'].items():assert sha(ROOT/rel)==h,rel
activation=load(OUT/'activation.json');activation.update(realModelVerification='passed-zero-tool-errors' if pass_run else 'see-experiment-result',restartOpenCodeRequired=True,changedFiles=changed)
dump(OUT/'activation.json',activation)
doctor=load(OUT/'doctor.json');prior=load(ROOT/'output/liuren-workflow-review-final-20261106/doctor-after.json')
assert doctor['errors']==prior['errors']
note=f'''# 工具调用审查与真实复测

活动版本：{p['release']}；前版{before['release']}冻结文件逐一hash复核未改。专业规则及预测效果不在本轮验收范围。

## 原因与整改

1. 前版task_result领取回执未检查report读取状态，直接推荐deliver，与交付前置校验冲突。现按当前状态返回可执行next_call及delivery_readiness；缺report先读，资料读取回执再指向deliver。result read/locate同样给出正确接续。故意跳过前置步骤仍会报错，未移除校验或伪装成功。
2. 上次隔离实验复制了原工作区的绝对路径权限；本次只在隔离配置中将路径映射至实验工作区，保留案例/经验禁用边界。compute chart返回专用神煞读取入口，减少不必要的通用read。
3. 正式资料工具以前固定使用插件安装目录。现优先使用OpenCode提供的可信context.directory，允许隔离工作区调用正式工具，无需替换execute。本次wrapper仅装配原插件和原资料工具，relay只转发真实接口响应。

## 本次真实结果

- 全链完成：{r['fullChainCompleted']}；零工具报错验收：{pass_run}。
- 耗时{run['elapsedSeconds']}秒；真实模型请求{r['modelRequests']}次；工具成功{r['completedToolCalls']}次、报错{len(r['toolErrors'])}次。
- 原会话未改：{r['originalSessionUnchanged']}；案例/经验检索：{r['caseOrExperienceToolsUsed']}。
- 原始结果：real-rerun/experiment-result.json；真实发出接口schema及实现hash：current-wire.json；报告原文：real-rerun/DeepSeek完整报告.md。

此前首轮复测（real-run/）达到实验器600秒上限后停止，43次工具调用成功、0次工具报错，裁决尚未提交，因此全链未完成。该记录及wire.json原样保留，不能算通过。本轮仅增加实验器预算至1200秒，生产工具及配置未再调整，也未向模型提供先前答案。不能将两轮说成首次全链成功。

## 验收边界

定向测试覆盖缺report时领取、locate/read、读取后交付、原文保留与单次裁决，并保留跳过report时报错的保护测试。资料工具测试覆盖可信会话目录和会话标识传递。另有方法加载、单模块读取及书籍查询回归。测试日志保存在本目录。

doctor仍有此前同一项research mechanical validation has gaps，不是本次新增；不能把整体健康检查说成完全通过。

单次真实零报错只能证明本例在当前环境成功；不能保证所有输入、网络、服务及文件状态下永久零故障。需重启OpenCode并开新会话加载新工具。本次报告内容与预测结论未作全面专业验收。
'''
(OUT/'审查与整改.md').write_text(note,'utf-8')
print(json.dumps({'zeroToolErrors':pass_run,'fullChainCompleted':r['fullChainCompleted'],'completedToolCalls':r['completedToolCalls'],'elapsedSeconds':run['elapsedSeconds'],'changedFiles':len(changed)},ensure_ascii=False))
