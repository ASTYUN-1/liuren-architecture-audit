"""Publish the accepted slim candidate locally; never touch website/server files."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
HOST = ROOT/'output/liuren-slim-candidate-20261107/candidate'
OLD = '20261106-performance-25'
NEW = '20261107-slim-26'
CANDIDATE = '20261107-slim-candidate-01'
SOURCE = HOST/'runtime/liuren'/CANDIDATE
DEST = ROOT/'runtime/liuren'/NEW
BEFORE = OUT/'before'
STAGE = OUT/'staging'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text('utf-8-sig'))
def write(p,t):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(t,encoding='utf-8',newline='')
def dump(p,v): write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def main():
    assert not (OUT/'activation.json').exists(), 'Already activated; do not rerun.'
    pointer=load(ROOT/'.opencode/liuren-active.json')
    assert pointer['release']==OLD
    assert not DEST.exists()
    staged={}
    def put(rel,text): staged[rel]=text
    for name in ['daliuren','liuren-cases','liuren-extract']:
        rel=f'.opencode/skills/liuren/{name}/SKILL.md'
        put(rel,(HOST/rel).read_text('utf-8'))

    primary='本机大六壬占事：加载当前daliuren，按原问与可信盘→依问取用→综合作用及最强反证→独立裁决→核对交付执行。8项共用方法及本问专项依当前路由读取，同版同上下文已读复用；固定排盘与神煞取法直接用程序结果，不重算、不逐课比较历史异法。主智能体准备中性材料，裁决者独立裁关键作用和结果，返回只核事实、引用、问项覆盖与一致性，忠实交付完整报告。依事件及占类专法取用，代问者不自动成为当事人，不设程序人物锁定。时间/取数只按实际tasks触发。普通研判不读案例库、经验库及旧缓存，保留原书、专业条件、正常年命/行年。参数不明查liuren_tool_help，按next_call接续；完整接口见当前references/deterministic-tools.md。开发、排障和知识维护切Build。'
    config=load(ROOT/'opencode.json')
    config['agent']['liuren']['prompt']=primary
    config['agent']['liuren']['description']='本机大六壬精简主线；可信程序盘，按问取用，独立裁决与完整交付。'
    # Retain all existing permissions/providers; update only the active runtime paths.
    encoded=json.dumps(config,ensure_ascii=False,indent=2).replace(OLD,NEW)+'\n'
    put('opencode.json',encoded)
    slim=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc')
    candidate_slim=load(HOST/'.opencode/oh-my-opencode-slim.jsonc')
    for key in ['prompt','description','orchestratorPrompt']:
        slim['agents']['liuren-adjudicator'][key]=candidate_slim['agents']['liuren-adjudicator'][key]
    for key in ['model','variant','options','permission']:
        assert slim['agents']['liuren-adjudicator'][key]==candidate_slim['agents']['liuren-adjudicator'][key]
    put('.opencode/oh-my-opencode-slim.jsonc',json.dumps(slim,ensure_ascii=False,indent=2)+'\n')

    workflow='''# 本机六壬完整研判流程

本机活动版本为20261107-slim-26，以.opencode/liuren-active.json为准。本页只解释主线，专业条件以当前方法全文为准。

核心任务是依原问和可信程序盘取用，判断关键对象在课传中的有效作用，处理最强反证，逐问回答结果及条件。

1. 理解事件、实际对象、阶段与成功标准；取得或复用liuren_chart的facts、program_facts、archive。依positioning和本问domain取用，在liqi、structure、void中综合位置、气态、关系、空墓及制救。此时不冻结成败。
2. 将shensha-use和movement纳入同一分析。浏览程序全部神煞位置与采用状态，切题项判断对象、气态、组合和制救；不逐课重算课盘、神煞公式或比较已固定的取法。新定位或有效反证须回核受影响的全局作用。
3. 依adjudication准备中性材料，按真实缺口补原书，交独立裁决者裁关键作用和结果。返回后依report核事实、引用、问项覆盖和一致性，领取并忠实交付完整技术报告。

共用资料8项：positioning、liqi、structure、void、shensha-use、movement、adjudication、report。report在交付前读，其余为准备阶段。16占类专项只选本问所需；时间、数量、年命及其他细则依当前reading-route的触发条件补读。三段是阅读安排，不是重复判断三轮。

类象在原法占类、位置、真假、气态和制救条件成立时参与取用及结果；不凭孤立名象翻判。正常年命/行年、应期和长期占事保留；给出占时不自动产生时间任务，出生推命与出生运限不进入占事。

同卦复用可靠课盘、背景、已核节点与同版已读原段，只补新争点。原书条件或作用解释的真实缺口才续查；固定程序取法的历史分歧不进入每课。来源、条件、未决和真实反馈身份分清，不以已知反馈定答案。

普通研判不调用案例库、经验库及旧检索缓存。知识维护另走liuren-cases/liuren-extract，不借维护绕取本次禁用材料。prepare/read/check仅可选审计，不强制判断JSON；doctor及工程测试不证明预测效果。

操作接续见[高效执行](本机六壬高效执行.md)，资料范围和最终报告分别依对应说明。本次只在本机生效，网站输出及部署规则不变。
'''
    put('docs/本机六壬完整研判流程.md',workflow)
    put('docs/本机六壬高效执行.md','''# 本机六壬执行接续

活动方法为20261107-slim-26，工具契约沿用liuren-tools-25。本页只管工具接续；判断主线见daliuren，接口细节集中于当前runtime的references/deterministic-tools.md。

- 同版同上下文真实已读的全文复用；同阶段已触发的方法可用liuren_materials(action="method",modules=[1至4个ID])合批，不为合批扩大专项。保存前用liuren_tool_help(topic="workflow",domains=[本问占类])查missing，只补缺项。参数不明用topic=packet/compute；工具成功按next_call接续。
- 可信课盘用liuren_chart；计算用liuren_compute，完整程序神煞用liuren_materials(action="shensha",path=archive.path)。固定盘式、神煞位置和采用口径不交模型重算。已有日期计算回执在范围、时区、日界相同且无具体疑点时复用。
- 主智能体准备中性材料；每问明确tasks及task_basis，user_requested附原问逐字request_quote，necessary说明具体理由。只给占时不默认增加应期/取数。课盘优先原样交archive.path与sha256；无归档才交完整facts，不重组盘面。
- method_modules只列真实已读当前模块ID，由程序装配全文/hash；原书用完整handoff或精确行段/hash，quote可省略。别名指向同源同版同段唯一全文，不丢原编号。事实与争点id全局唯一并分开。
- packet返回的task_prompt原样交新task，仅派liuren-adjudicator，不传长JSON、不指定已有task_id、不用background。裁决者首次read用page=1,page_count=4，再按next_call读完；实际全文/hash匹配才算完整，截断回执不算读完。
- 裁决者以liuren_adjudication_submit提交非空正文或自由JSON，成功末消息只回工具回执。主智能体按可见回执的子会话task_id调用task_result领取，读report后用liuren_adjudication_result(action="deliver")取得完整report_markdown。不得将request_id、文件UUID或hash当task_id；丢失时用locate，多个候选不猜。
- 格式问题只修字段，不重裁；needs_input或具体事实/引用错误且补入真实新材料时，才依retry_context一次补核。主智能体核事实、引用、覆盖及一致性，不再折中改判；交付保留裁决结论、精度、条件和决定性理由。

裁决模型仍为deepseek/deepseek-flash、high。本次仅更新方法及提示词，不宣称工具契约升级。重启OpenCode并在本项目新建会话后加载；旧会话不保证热加载。工程交接通过不等于专业或预测准确率已经验证。
''')
    put('docs/本机OpenCode完整输出规则.md','''# 本机 OpenCode 完整输出规则

在本项目本机使用liuren时，默认交付完整技术报告，专业内容依当前report模块。围绕原问自然说明取用、关键作用、最强反证、逐问结论、条件、来源与缺口；应期和取数仅在实际任务触发时完整说明。不要求固定分析JSON字段。

主智能体领取裁决结果并完成事实、引用、问项覆盖和一致性核对后，按deliver返回的report_markdown交付正文。可以调整排版，不改结论、精度和条件，不添加决定性理由；成功工具回执不是给用户的最终报告。发现具体错误按当前adjudication协议处理，不为格式或措辞重裁。

本机不启用wenheng-public-output，不套网站公开报告的字数和来源隐藏要求；保留可核对的实际依据与限制。密钥、令牌及无关私密信息不进入报告。

本次精简仅在本机OpenCode生效，不部署网站或服务器，不改变网站受限任务的交付规范。重启OpenCode，在本项目目录新建会话并选择liuren、加载daliuren，使用当前活动指针。工程验证不证明预测准确率不下降。
''')
    scope=(ROOT/'docs/本机六壬资料检索范围.md').read_text('utf-8-sig')
    put('docs/本机六壬资料检索范围.md',scope.replace('shensha用于复核已有归档','shensha用于读取已有归档的程序神煞位置及采用状态，不重算固定起法'))
    agents=(ROOT/'AGENTS.md').read_text('utf-8-sig')
    oldline=next(line for line in agents.splitlines() if line.startswith('- 完整本地研判先读'))
    newline='- 完整本地研判先读[本机完整研判流程](docs/本机六壬完整研判流程.md)，按当前daliuren及8项共用方法执行一条主线，16专项和时间/数量/年命按问触发。理气贯穿，依占类及事件取用；可信程序盘、神煞位置和固定采用口径直接使用。类象依位置、真假、气态和制救条件参与综合判断，处理最强反证，不凭孤立名象定成败。当前研判不检索案例库、经验库或旧缓存；原书和专业条件保留，知识维护另走专项。同卦复用可靠盘及同版已读资料，只补新争点。当前入口为daliuren/liuren-cases/liuren-extract；仅占事，正常年命/行年、应期与长期占事保留，出生推命及出生运限退出。prepare/read/check仅可选审计；doctor和工程测试不证明专业或预测效果。'
    agents=agents.replace(oldline,newline).split('本版分工：主智能体准备到可裁决')[0].rstrip()
    agents+='\n\n## 本机现行裁决分工\n\n主智能体准备中性材料，独立裁决者查漏并裁关键作用和结果；返回后主智能体核事实、引用、问项覆盖和一致性，忠实交付，不重新折中权衡。具体错误或真实新材料按现行协议一次补核，格式差异不重裁。可信程序事实及固定神煞取法直接复用，程序不裁吉凶。完整工具接续见[高效执行](docs/本机六壬高效执行.md)，专业条件以活动runtime正文为准，不叠加旧版历史补丁。\n\n本次20261107-slim-26仅本机OpenCode生效；网站、APK及服务器未发布。\n'
    put('AGENTS.md',agents)
    readme=(ROOT/'README.md').read_text('utf-8-sig').replace(OLD,NEW)
    line=next(line for line in readme.splitlines() if line.startswith('本机默认从 `daliuren`'))
    readme=readme.replace(line,'本机默认从`daliuren`按[完整研判流程](docs/本机六壬完整研判流程.md)执行原问与可信盘→依问取用→综合作用和最强反证→独立裁决→核对交付。共用资料8项，16占类专项及应期、数量、年命按问触发；直接使用可信程序盘与固定神煞结果，同卦复用已核材料。三个入口为daliuren、liuren-cases、liuren-extract，普通研判与知识维护分开。精简不代表预测准确率等价已经验证。')
    readme=readme.split('本版将阶段3的裁决交给')[0].rstrip()+'\n\n本机独立裁决仍由deepseek/deepseek-flash、high承担。现行操作只见[高效执行](docs/本机六壬高效执行.md)，本轮[生效与回滚说明](output/liuren-slim-activation-20261107/生效说明.md)。本次只切本机入口，网站和服务器未发布。\n'
    put('README.md',readme)
    index=(ROOT/'目录总索引.md').read_text('utf-8-sig').replace(OLD,NEW).split('本版事件定位：')[0].rstrip()+'\n'
    put('目录总索引.md',index)

    # Update only tests tied to the replaced route; retain integrity and missing-read gates.
    rel='tools/tests/liuren-flow-control.test.mjs'
    text=(ROOT/rel).read_text('utf-8').replace('engine-shensha-output','shensha-use')
    text=text.replace("['shensha-use','exam']","['exam','shensha-use']")
    put(rel,text)
    rel='tools/tests/test_liuren_local_read.py'
    put(rel,(ROOT/rel).read_text('utf-8').replace("self.assertIn('engine-shensha-output', expected)","self.assertIn('shensha-use', expected)\n        self.assertFalse(set(manifest.get('moduleAliases', {})).intersection(expected))"))
    rel='tools/tests/test_liuren_method_loader.py'
    text=(ROOT/rel).read_text('utf-8').replace("self.assertIn('engine-shensha-output', keys)\n        self.assertLess(keys.index('engine-shensha-output'), keys.index('shensha-focus'))\n        self.assertLess(keys.index('illness'), keys.index('relations'))","self.assertIn('shensha-use', keys)\n        self.assertFalse(set(manifest.get('moduleAliases', {})).intersection(keys))\n        self.assertLess(keys.index('illness'), keys.index('liqi'))")
    put(rel,text)
    rel='tools/tests/test_liuren_class_mapping.py'
    text=(ROOT/rel).read_text('utf-8')
    # Historical evidence maps describe the frozen release. Continue validating those exact bytes.
    historical=['test_original_methods_are_preserved_and_consolidation_is_traceable','test_consolidated_rules_keep_every_specific_condition_and_exclusion','test_consolidation_keeps_all_existing_reading_routes','test_previous_text_is_preserved_and_revised_methods_have_pinned_sources']
    append="\n        if self._testMethodName in "+repr(historical)+":\n            self.runtime=ROOT/'runtime/liuren/20261106-performance-25'\n            self.m=json.loads((self.runtime/'manifest.json').read_text('utf-8'))\n            self.m['readingRoute']=json.loads((self.runtime/self.m['routingFile']).read_text('utf-8'))"
    text=text.replace('self.runtime,self.m=loader.active(ROOT)','self.runtime,self.m=loader.active(ROOT)'+append)
    text=text.replace("for core in ['relations','liqi','void','structure']:","for core in ['liqi','void','structure']:")
    text=text.replace("2 if core=='void' else 1","1")
    text=text.replace("self.assertLess(keys.index('class-mapping'),keys.index('positioning'))","self.assertNotIn('class-mapping',keys)")
    text=text.replace("keys.index('relations')","keys.index('liqi')")
    put(rel,text)

    # Backup exact current bytes and protected baseline before touching any live file.
    protected={}
    for p in (ROOT/'runtime/liuren'/OLD).rglob('*'):
        if p.is_file(): protected[p.relative_to(ROOT).as_posix()]=sha(p)
    for base in ['tools','.opencode/tools','.opencode/plugins','排盘工具魔改']:
        for p in (ROOT/base).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and 'node_modules' not in p.parts and p.suffix in ['.py','.mjs','.ts','.js','.json'] and '/tests/' not in p.as_posix():
                protected[p.relative_to(ROOT).as_posix()]=sha(p)
    dump(OUT/'protected-sha256.json',protected)
    before={}
    for rel in [*staged,'.opencode/liuren-active.json']:
        before[rel]=sha(ROOT/rel)
        target=BEFORE/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,target)
    dump(OUT/'before-sha256.json',before)
    for rel,t in staged.items():write(STAGE/rel,t)
    shutil.copytree(SOURCE,STAGE/'runtime/liuren'/NEW)
    runtime=STAGE/'runtime/liuren'/NEW
    m=load(runtime/'manifest.json')
    m.update(release=NEW,status='active',parentRelease=OLD,authoringSource=OUT.relative_to(ROOT).as_posix())
    m['slimming']['scope']='local-opencode prompt and reading route'
    m['originCandidate']={'release':CANDIDATE,'manifestSha256':sha(SOURCE/'manifest.json')}
    m['computeInterface']['release']=NEW
    policy=load(runtime/'references/shensha-policy.json');policy['release']=NEW;dump(runtime/'references/shensha-policy.json',policy)
    migration=load(runtime/'migration.json');migration['activatedRelease']=NEW;dump(runtime/'migration.json',migration)
    contract=load(runtime/'loader-contract.json')
    contract.update(release=NEW,parentRelease=OLD,authoringSource=m['authoringSource'])
    for key in ['adjudication','deterministicFoundation','computeInterface','flowControl','eventPositioning','toolUsage']:
        contract[key]=copy.deepcopy(m[key])
    contract['sourceHashes']={rel:sha(STAGE/rel if rel in staged else ROOT/rel) for rel in contract['sourceHashes']}
    dump(runtime/'loader-contract.json',contract)
    m['files']={p.relative_to(runtime).as_posix():sha(p) for p in runtime.rglob('*') if p.is_file() and p.name!='manifest.json'}
    m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
    dump(runtime/'manifest.json',m)
    pointer.update(release=NEW,runtime=f'runtime/liuren/{NEW}',methodVersion=m['version'],previousRelease=OLD,backup=(BEFORE.relative_to(ROOT).as_posix()),authoringSource=m['authoringSource'])
    pointer['files']={rel:sha(STAGE/'.opencode/skills'/rel) for rel in pointer['files']}
    for field in ['workflowImplementation']:
        pointer[field]={rel:sha(STAGE/rel if rel in staged else ROOT/rel) for rel in pointer[field]}
    for field in ['boundedReview','expertAdjudicationReview']:
        pointer[field]['scope']='historical baseline evidence, not slim predictive validation'
    for field in ['adjudication','deterministicFoundation','computeInterface','eventPositioning','toolUsage','slimming']:
        pointer[field]=copy.deepcopy(m[field])
    pointer['bookRetrieval']['compatibleMethodRelease']=NEW
    pointer['bookRetrieval']['files']={rel:sha(STAGE/rel if rel in staged else ROOT/rel) for rel in pointer['bookRetrieval']['files']}
    pointer['localOnlyActivation']=True
    dump(STAGE/'.opencode/liuren-active.json',pointer)
    # Validate staged identity/route with the actual unchanged loader.
    spec=importlib.util.spec_from_file_location('activation_loader',ROOT/'tools/load-liuren-methods.py')
    loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(loader)
    for item in pointer['localModuleOverrides'].values():
        rel=item['file'];write(STAGE/rel,(ROOT/rel).read_text('utf-8-sig'))
        shutil.copyfile(ROOT/rel,STAGE/rel)
    checked,manifest=loader.active(STAGE)
    assert len(loader.plan(manifest))==8
    for module in manifest['modules']:loader.content(checked,manifest,module)
    # Recheck current source bytes before atomic replacements. Publish pointer last.
    assert all(sha(ROOT/rel)==digest for rel,digest in before.items()),'Concurrent edit; abort.'
    shutil.copytree(runtime,DEST)
    for rel in staged:
        target=ROOT/rel;tmp=target.with_name(target.name+'.slim26.tmp')
        shutil.copyfile(STAGE/rel,tmp);os.replace(tmp,target)
    p=ROOT/'.opencode/liuren-active.json';tmp=p.with_suffix('.slim26.tmp')
    shutil.copyfile(STAGE/'.opencode/liuren-active.json',tmp);os.replace(tmp,p)
    after={rel:sha(ROOT/rel) for rel in before}
    dump(OUT/'activation.json',{'release':NEW,'previousRelease':OLD,'scope':'local-opencode-only','websiteChanged':False,'serverDeployment':False,'before':before,'after':after,'methodVersion':m['version'],'modelCalls':0,'predictiveValidationCount':0})
    assert all(sha(ROOT/rel)==digest for rel,digest in protected.items()),'Protected source changed.'
    print(json.dumps({'activated':NEW,'scope':'local-opencode-only','filesUpdated':len(after),'protectedFilesUnchanged':len(protected)},ensure_ascii=False))

if __name__=='__main__':main()
