from pathlib import Path
import ast
import hashlib
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def load(p):return json.loads(p.read_text('utf-8-sig'))
record=load(OUT/'activation.json')
assert all(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest for rel,digest in record['after'].items())
assert all(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest for rel,digest in load(OUT/'protected-sha256.json').items())
before=load(OUT/'before/.opencode/liuren-active.json')
after=load(ROOT/'.opencode/liuren-active.json')
old_stage=ast.parse((ROOT/'tools/stage-liuren-quantity-20261027.py').read_text('utf-8-sig'))
allowed={n.targets[0].id:ast.literal_eval(n.value) for n in old_stage.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['PARENT','RELEASE']}
legacy={
 'parallel_search':{'beforeDisabled':before['experiment']['disableCaseExperience'],'afterDisabled':after['experiment']['disableCaseExperience'],'reason':'两库在切换前后均禁用；两项旧检索单元测试仍假设可调用，并非本次路由变化造成。'},
 'quantity_candidate':{'allowedHistoricalReleases':allowed,'beforeRelease':before['release'],'afterRelease':after['release'],'reason':'旧候选测试只接受20261023/20261027版本；切换前的25版同样不在适用范围。'}
}
(OUT/'legacy-check-diagnosis.json').write_text(json.dumps(legacy,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doctor=load(OUT/'doctor.json')
native=load(OUT/'host-config-check.json')
summary={
 'release':after['release'],'scope':'local-opencode-only','websitePublished':False,'serverChanged':False,
 'activeVerification':len(load(OUT/'verification.json')['checks']),
 'syntheticNativeIntegrationChecks':len(load(OUT/'integration-verification.json')['checks']),
 'modelCallsThisActivation':0,'predictiveValidationCount':0,
 'node':{'fullRunTests':209,'initialPassed':207,'initialFailed':2,'affectedRerunPassed':11,'remainingFailures':0,'note':'两处旧措辞/证据路径测试已改为精确全文及明确证据来源校验；其余207项未重复跑。'},
 'python':{'fullRunTests':105,'skipped':2,'failures':1,'errors':2,'affectedRouteAndIntegrityTestsPassed':True,'legacyDiagnosis':'legacy-check-diagnosis.json','note':'一处error为旧候选类setUpClass；不纳入105个已执行方法的通过数。未修改两库门禁或旧候选算法绕过失败。'},
 'doctor':{'ok':doctor['ok'],'errors':doctor['errors'],'runtimeAndFixedChartPassed':doctor['errors']==['research mechanical validation has gaps']},
 'hostConfig':native,'protectedFilesUnchanged':202,'rollbackPreviewPassed':True
}
(OUT/'validation-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
hostline='已用已安装OpenCode的debug config确认主模式与精简prompt实际解析。' if native.get('slimPromptLoaded') else '宿主debug config未成功完成；具体状态见host-config-check.json。活动加载器、真实工具execute及模拟交接已完成，未验证现有桌面会话热加载。'
report=f'''# 本机精简版生效说明

活动指针已从20261106-performance-25切换为**{after['release']}**，运行包位于runtime/liuren/{after['release']}。仅本机OpenCode生效；未部署网站、APK或服务器，也未修改网站输出规范。

## 使用

**重启OpenCode，在C:\\Users\\QLMa_\\Documents\\六壬八字测算中新建会话，选择liuren并加载daliuren。**旧会话不保证热加载。{hostline}

## 实际变化

- 共用必读从14模块归并为8模块；静态正文从44,470字符降至17,560字符，减少约60.5%。这是正文字符比较，不是实际推理token或耗时测量。
- 一条主线：原问与可信盘→依问取用→综合作用与最强反证→独立裁决→核对交付；16专项与应期、数量、年命依实际问项触发。
- 直接用程序盘、固定神煞位置及采用状态，删除逐课重算与异法比较；神煞的切题取用、气态、组合及制救仍须判断。
- 同步三个skill入口、主/裁决prompt、活动路径权限和本机说明，移除入口的历史重复补丁；保留通用开发、知识维护、课程和隐私要求。
- 独立裁决模型仍为deepseek/deepseek-flash、high；工具契约仍为liuren-tools-25。案例库、经验库及旧缓存仍不介入普通研判。

## 验证及边界

活动包106文件hash、59个模块可读、全部8项路由与16专项、19次实际分页读取均通过；350个专项独有段落、E01—E22裁决依据保留。冻结25版与工具程序/引擎共202文件字节未变，神煞policy仅修改发布身份。三入口YAML用现有Node解析器验证通过；Python官方quick_validate因缺PyYAML未通过，未混称通过。

真实插件execute的9项模拟交接通过，包括缺读阻断、全文文件/hash接续、自由正文保存、task_result领取、report门禁与deliver原文一致。本次没有调用预测模型或开展真实占断效果测试。

Node全量209项初次207通过，修正两项对旧措辞/证据目录的测试假设后，相关11项复测全部通过。Python全量执行105项，跳过2项，仍有1失败、2错误：其中两处为旧检索测试与既存无两库门禁冲突，另一处为20261027候选测试只接受旧发布版本；切换前25版同样不满足这些假设，详见legacy-check-diagnosis.json。当前路由、分页、分类保留、资料范围和单模块测试通过。

doctor的运行包、神煞身份及固定课盘检查通过，总结果仍因研究库机械校验缺口为false。本次未修改研究数据以消除该缺口。详细结果见verification.json、integration-verification.json、validation-summary.json及原始测试日志。

**专业条件保留和工程通过，不等于已证明精简前后预测准确率相同。**

## 回滚

切换前19份实际文件字节保存在本目录before/；activation.json记录前后hash。冻结25包原位保留，新包不覆盖旧包。先预览，再执行：

```powershell
python -X utf8 output/liuren-slim-activation-20261107/rollback.py
python -X utf8 output/liuren-slim-activation-20261107/rollback.py --apply
```

回滚会检查后续修改，遇冲突拒绝覆盖，最后恢复活动指针；不删除新旧运行包。回滚后同样重启OpenCode并新建会话。
'''
(OUT/'生效说明.md').write_text(report,encoding='utf-8',newline='')
print(json.dumps({'release':after['release'],'report':str(OUT/'生效说明.md'),'hostConfigLoaded':native.get('slimPromptLoaded',False)},ensure_ascii=False))
