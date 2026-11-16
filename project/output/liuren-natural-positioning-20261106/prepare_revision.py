"""Prepare a new candidate and narrowly scoped live edits; preserve the active frozen release."""
from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
NEW = '20261106-natural-positioning-16'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace(path, old, new):
    text = path.read_text(encoding='utf-8-sig')
    assert old in text, (str(path), old[:90])
    path.write_text(text.replace(old, new), encoding='utf-8')


assert not (OUT / 'before-manifest.json').exists(), 'Already prepared; do not rerun.'
active = load(ROOT / '.opencode/liuren-active.json')
OLD = active['release']
assert OLD == '20261106-event-positioning-15'
files = ['.opencode/liuren-active.json', '.opencode/oh-my-opencode-slim.jsonc',
         '.opencode/plugins/liuren-adjudication.ts', 'opencode.json',
         *['.opencode/skills/liuren/' + n + '/SKILL.md' for n in ['daliuren', 'liuren-cases', 'liuren-extract']],
         'tools/liuren-event-positioning.mjs', 'tools/liuren-deterministic-io.mjs',
         'tools/liuren-flow-control.mjs', 'tools/liuren-adjudication-output.mjs',
         'tools/tests/liuren-flow-control.test.mjs', 'tools/tests/liuren-wire-schema.test.mjs',
         'README.md', 'AGENTS.md', '目录总索引.md', 'docs/本机六壬完整研判流程.md', 'docs/本机六壬高效执行.md']
for rel in files:
    dest = OUT / 'before' / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / rel, dest)
parent = ROOT / active['runtime']
before = {'parentRelease': OLD, 'parentRuntime': active['runtime'], 'newRelease': NEW,
          'live': {rel: sha(ROOT / rel) for rel in files},
          'runtime': {p.relative_to(parent).as_posix(): sha(p) for p in parent.rglob('*') if p.is_file()}}
dump(OUT / 'before-manifest.json', before)
C = OUT / 'candidate-runtime'
shutil.copytree(parent, C)

# Domain classification and full-method transport remain mechanical. Actor choice is model interpretation.
(ROOT / 'tools/liuren-event-positioning.mjs').write_text('''// Classification and versioned method transport only; event roles are interpreted by the model.
import fs from 'node:fs/promises';
import path from 'node:path';
export const EVENT_POLICY='liuren-event-positioning-v1';
export const EVENT_DOMAINS=['finance','recruitment','promotion-salary','relationship','interpersonal','period-outlook','long-period','pregnancy','exam','illness','lost-person-object','classical-conflict','home','travel','weather','agriculture'];
const fail=issues=>{throw new Error('LIUREN_METHOD_HANDOFF: '+JSON.stringify({issues,action:'补齐本问分类或重新保存当前版本文件；程序不判断人物身份或指定干支角色。'}));};
export async function eventPolicy(root){
 const p=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
 return p.eventPositioning?.enabled===true;
}
export async function checkDomainHandoff(root,p){
 if(!await eventPolicy(root))return;
 const pointer=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
 if(p.event_positioning?.schema!==EVENT_POLICY||p.event_positioning.release!==pointer.release)fail([{path:'/event_positioning',code:'rebuild_method_packet',expected:'用当前packet工具重新保存材料；旧裁决仍可领取，不重派'}]);
 const questions=classificationRecord(p);
 if(JSON.stringify(questions)!==JSON.stringify(p.event_positioning.questions))fail([{path:'/event_positioning/questions',code:'classification_record_mismatch'}]);
}
export async function eventDomains(root,p){
 if(!await eventPolicy(root))return [];
 classificationRecord(p);
 return [...new Set(p.questions.map(q=>q.domain))];
}
export function classificationRecord(p){
 const issues=[];
 for(const [i,q] of (p?.questions??[]).entries())if(!EVENT_DOMAINS.includes(q.domain))issues.push({path:'/questions/'+i+'/domain',code:'classification_required',expected:EVENT_DOMAINS});
 if(!p?.questions?.length)issues.push({path:'/questions',code:'questions_required'});
 if(issues.length)fail(issues);
 return p.questions.map(q=>({question_id:q.id,domain:q.domain,subject:q.subject}));
}
''', encoding='utf-8')
replace(ROOT / 'tools/liuren-deterministic-io.mjs', 'eventDomains,checkEventInput', 'eventDomains,classificationRecord')
replace(ROOT / 'tools/liuren-deterministic-io.mjs', ';checkEventInput(p);', ';')
replace(ROOT / 'tools/liuren-deterministic-io.mjs', 'questions:checkEventInput(p)', 'questions:classificationRecord(p)')
replace(ROOT / '.opencode/plugins/liuren-adjudication.ts', 'checkEventDispatch', 'checkDomainHandoff')
replace(ROOT / '.opencode/plugins/liuren-adjudication.ts',
        '考试/疾病必填：考生/患者的现有实体ID，其branch为占日干；代问者不是默认日干',
        '仅兼容旧交接，可省略；事件当事对象和干支取用由模型依原问及分类专法判断，程序不绑定')
replace(ROOT / 'tools/liuren-adjudication-output.mjs', "import {eventOutputIssues} from './liuren-event-positioning.mjs';\n", '')
replace(ROOT / 'tools/liuren-adjudication-output.mjs', ' issues.push(...eventOutputIssues(r,p));\n', '')
flow = ROOT / 'tools/liuren-flow-control.mjs'
s = flow.read_text(encoding='utf-8-sig')
start = s.index('  const roles=')
end = s.index('  for(const [i,q] of p.questions.entries()){', start)
s = s[:start] + s[end:]
old = "error_kind:checked.issues.some(i=>i.code==='event_actor_mapping_changed')?'event_mapping':'format',action:checked.issues.some(i=>i.code==='event_actor_mapping_changed')?'这是具体对象定位错误：在当前子任务纠正考生/患者实体，重核受影响的作用、制救、应期与结论后再提交；不得只改符号保留错误依赖，不新派整轮裁决。':"
assert old in s
s = s.replace(old, "error_kind:'format',action:")
flow.write_text(s, encoding='utf-8')

RULE = ('本版事件定位：主智能体理解原问时，自然分清发生什么事、实际涉及谁或什么、双方职责和目标，'
        '再依该占类的专法确定干支与关键类神。代问者不自动成为事件当事人；考试围绕实际考生，疾病围绕实际患者，'
        '婚配、攻守、胎产等保留专项对待轴。将必要取用理由融入正常分析，不另设角色表、人物身份核验阶段或模型调用。'
        '裁决者在正常研判中沿用事件语境，遇到具体取用错误才纠正并重核受影响作用，不为确认主体另派一轮。'
        '程序不以考试/疾病类别强绑日干，不做亲属称谓推断或输出角色锁定；仅保留资料分类读取、文件版本和确定性盘面/计算校验。')
old_rule = next(line for line in (OUT / 'before/.opencode/skills/liuren/daliuren/SKILL.md').read_text('utf-8-sig').splitlines() if line.startswith('本版事件定位：'))
original_label = '程序保留原问并提示明确亲属标签冲突，不替代专业取用。日干不能改成寄宫支来过校验。'
new_label = '程序完整保留原问，不用亲属称谓正则或角色绑定决定人物取用；日干、寄宫及上神的坐标计算仍由程序分别提供。'
for rel in files:
    if rel.endswith('SKILL.md') or rel in ['README.md', 'AGENTS.md', '目录总索引.md', 'docs/本机六壬完整研判流程.md', 'docs/本机六壬高效执行.md']:
        p = ROOT / rel
        s = p.read_text('utf-8-sig').replace(OLD, NEW).replace(old_rule, RULE).replace(original_label, new_label)
        p.write_text(s, encoding='utf-8')
op = load(ROOT / 'opencode.json')
op['agent']['liuren']['prompt'] = op['agent']['liuren']['prompt'].replace(old_rule, RULE).replace(original_label, new_label)
dump(ROOT / 'opencode.json', op)
shutil.copyfile(ROOT / '.opencode/skills/liuren/daliuren/SKILL.md', C / 'entry.md')

position = C / 'methods/positioning.md'
s = position.read_text('utf-8-sig')
s = s.replace('## 本机执行：以事件为核心定位', '## 理解事件，依分类专法定位')
s = s.replace('每个子问先在本轮已读的分类占中定位，再列“事件—当事对象—目标/问题—日干角色—日支角色—关键类神职责—年命归属”。这里的当事对象可以是人、物或组织；代问者若没有参与事件，不必占用一个课位。类神必须说明是人、成绩、学校、病证、财物、阻碍还是救应，不因六亲名称就当作现实亲属。',
              '主智能体理解原问时，自然分清发生什么事、实际涉及谁或什么、各方职责与目标，再依已读分类专法确定干支、关键类神及年命归属。将会影响判断的取用理由融入正常分析即可，不另填角色表、不新增身份检查阶段；当事对象可以是人、物或组织，代问者没有参与事件时无需安排课位。成绩、学校、病证、医救等各司其职，不因六亲名称就当作现实亲属。')
old = next(line for line in s.splitlines() if line.startswith('交接每问必填domain'))
s = s.replace(old, '交接每问保留domain以读取和传送对应分类占；不要求actor_entity_id，不由程序将考试、疾病实体强绑日干或冻结裁决中的对象取用。程序负责原盘坐标、关系查表、日期算式和资料版本，模型负责理解事件与适用专法。裁决者在正常研判中处理取用，遇到会影响判断的具体错误才纠正，不增设逐人核验或额外派工。')
position.write_text(s, encoding='utf-8')

def replace_first_paragraph(rel, text):
    p = C / rel
    s = p.read_text('utf-8-sig')
    head, tail = s.split('\n\n', 1)
    _, rest = tail.split('\n\n', 1)
    p.write_text(head + '\n\n' + text + '\n\n' + rest, encoding='utf-8')

replace_first_paragraph('methods/adjudication.md', '主智能体在理解事件与准备材料时依分类专法取用，将必要理由放入现有实体与观察中。每问domain用于读取并交接对应分类占；actor_entity_id不要求填写，程序不强绑考试/疾病日干或锁定裁决取用。裁决者按正常研判处理人物与作用，遇到具体取用错误才纠正并重核依赖，不另做一轮主体确认。')
replace_first_paragraph('methods/report.md', '正文自然说明与本问相关的对象和取用依据，不强制另起角色表或逐人身份核验。报告围绕原事件及目标，病证、成绩、学校与当事人各司其职；明确发现取用错误时纠正其依赖，不以无依据折中代替修正。')
replace_first_paragraph('methods/evidence.md', '按本问domain读取对应分类占全文，复用同版已读内容。主智能体理解原问并依专法取用，必要依据自然记录在现有实体与观察中，不另填角色绑定字段或新增身份检查。程序随文件附完整定位及所选分类占，保留原问供正常研判使用。')
replace_first_paragraph('references/adjudicator-contract.md', '每问domain用于当前分类占读取及完整正文交接；actor_entity_id为旧交接兼容字段，可省略。程序不判断谁是当事人，不强绑考试/疾病日干，也不锁定输出对象。裁决者依原问和专法正常研判，具体取用错误才纠正，不额外新增主体核验阶段或调用。')
replace_first_paragraph('references/deterministic-tools.md', '每问questions[].domain用于分类占资料路由。actor_entity_id不必填写；事件理解、当事对象及干支取用由模型完成。event_positioning仅记录分类和资料版本，不记录或验证角色绑定。程序装入完整定位及对应分类占，保留已读回执、坐标/阴神、日期、算式及来源校验，不承担人物身份推断。')
for p in C.rglob('*.md'):
    s = p.read_text('utf-8-sig')
    if original_label in s:
        p.write_text(s.replace(original_label, new_label), encoding='utf-8')
prompt = C / 'references/adjudicator-prompt.md'
s = prompt.read_text('utf-8-sig')
start = s.index('## 本机事件定位规则')
end = s.index('你只负责大六壬占事裁决', start)
s = s[:start] + ('## 事件语境与分类取用\n\n'
    '在正常研判中理解原问的事件、实际涉及对象、各方职责和目标，依M_EVENT_POSITIONING及对应M_DOMAIN_*分类专法取用。'
    '代问者不自动代表事件当事人；考试围绕实际考生、疾病围绕实际患者，婚配、攻守、胎产等保留专项对待轴。'
    '程序不判断人物身份、不要求actor_entity_id、不强绑干支，也不锁定输出取用。'
    '无需另做角色清单或逐人身份检查；发现具体取用错误时，在现有scope_review/entity_checks说明必要修正并重核相关作用，'
    '不为确认主体重复派工。历史亲属异法保留研究身份，不覆盖本机普通单事取法。\n\n') + s[end:]
old = next(line for line in s.splitlines() if line.startswith('工具返回error_kind=event_mapping'))
s = s.replace(old, old[old.index('其他格式issues时，'):].replace('其他格式issues时，', '工具返回格式issues时，', 1))
prompt.write_text(s, encoding='utf-8')
slim = load(ROOT / '.opencode/oh-my-opencode-slim.jsonc')
slim['agents']['liuren-adjudicator']['prompt'] = s
dump(ROOT / '.opencode/oh-my-opencode-slim.jsonc', slim)

policy = {'enabled': True, 'schema': 'liuren-event-positioning-v1', 'mode': 'model-event-interpretation',
          'semanticRoleChecks': False, 'actorReferenceRequired': False, 'domainReadRequired': True,
          'fullDomainHandoff': True, 'source': 'explicit-user-instruction'}
source_policy = load(C / 'references/event-positioning-policy.json')
source_policy.pop('actorAsDayStem', None)
source_policy.update(release=NEW, interpretation='model-event-interpretation', semanticRoleChecks=False,
                     actorReferenceRequired=False, outputRoleLock=False, addedRoleReviewStage=False)
dump(C / 'references/event-positioning-policy.json', source_policy)
route = load(C / 'reading-route.json')
route['eventRolePolicy'] = 'references/event-positioning-policy.json'
dump(C / 'reading-route.json', route)

# Replace role-gate tests with the user-authorized model-led behavior and unchanged mechanical boundaries.
tests = ROOT / 'tools/tests/liuren-flow-control.test.mjs'
s = tests.read_text('utf-8-sig')
start = s.index("test('exam workflow rejects")
end = s.index("test('scoped event packet", start)
s = s[:start] + '''test('exam packets do not require or programmatically bind an actor to the day stem',async t=>{
 const h=await harness(t,{eventPolicy:true});
 for(const branch of ['子','丑','申']){const p=eventPacket(h);delete p.questions[0].actor_entity_id;p.entities[0].branch=branch;const saved=await h.save(p);const body=JSON.parse(await fs.readFile(saved.file_path,'utf8')).packet;assert.equal(body.entities[0].branch,branch);assert.equal(body.event_positioning.questions[0].actor_entity_id,undefined);}
});

test('illness packets leave patient mapping to the model while retaining the original question',async t=>{
 const h=await harness(t,{eventPolicy:true,text:'父亲生病，治疗后能否恢复？'}),p=eventPacket(h,'illness','患病父亲');
 p.questions[0].task_basis[0].request_quote='能否恢复';delete p.questions[0].actor_entity_id;p.entities[0].branch='丑';
 const body=JSON.parse(await fs.readFile((await h.save(p)).file_path,'utf8')).packet;
 assert.equal(body.entities[0].branch,'丑');assert.match(body.input_origin.source_text,/父亲生病/);
});

test('legacy optional actor labels are not interpreted by program semantic rules',async t=>{
 const h=await harness(t,{eventPolicy:true}),p=eventPacket(h);p.questions[0].actor_entity_id='old-optional-label';
 const body=JSON.parse(await fs.readFile((await h.save(p)).file_path,'utf8')).packet;
 assert.equal(body.questions[0].actor_entity_id,'old-optional-label');assert.equal(body.event_positioning.questions[0].actor_entity_id,undefined);
});

''' + s[end:]
s = s.replace("assert.equal(body.event_positioning.questions[0].actor_entity_id,'S1');", "assert.equal(body.event_positioning.questions[0].domain,'exam');assert.equal(body.event_positioning.questions[0].actor_entity_id,undefined);")
start = s.index("test('adjudicator cannot silently replace")
end = s.index("test('event actor IDs survive", start)
s = s[:start] + '''test('adjudicator may correct entity mapping without a program output-role lock',async t=>{
 const h=await harness(t,{eventPolicy:true});await h.save(eventPacket(h));await h.start();await h.read();
 const corrected=h.output();corrected.entity_checks[0].referent='外甥女考生';corrected.entity_checks[0].branch='丑';corrected.entity_checks[0].mapping_review='合成协议测试：由模型解释取用，程序仅核坐标和字段';
 corrected.scope_review.mapping_status='corrected';corrected.scope_review.corrections=['合成测试中修订实体取用；程序不锁定角色'];
 const response=await h.submit(corrected);assert.equal(response.status,'completed',JSON.stringify(response));
});

''' + s[end:]
s = s.replace("test('event actor IDs survive reserved-ID normalization throughout question and generated record'", "test('legacy actor references remain compatible while generated metadata contains no actor binding'")
s = s.replace("assert.equal(body.event_positioning.questions[0].actor_entity_id,body.entities[0].id);", "assert.equal(body.event_positioning.questions[0].actor_entity_id,undefined);")
old = "test('original kinship label cannot silently become a different family relation',async t=>{const h=await harness(t),p=h.input();p.questions[0].subject='侄女';await assert.rejects(()=>h.save(p),/INPUT_PREFLIGHT.*外甥女/);});"
new = "test('kinship wording is preserved for the model rather than rejected by a regex',async t=>{const h=await harness(t),p=h.input();p.questions[0].subject='侄女';const body=JSON.parse(await fs.readFile((await h.save(p)).file_path,'utf8')).packet;assert.equal(body.questions[0].subject,'侄女');assert.match(body.input_origin.source_text,/姐姐的女儿/);});"
assert old in s
s = s.replace(old, new)
tests.write_text(s, encoding='utf-8')
replace(ROOT / 'tools/tests/liuren-wire-schema.test.mjs', 'output/liuren-event-positioning-20261106/current-wire.json', 'output/liuren-natural-positioning-20261106/current-wire.json')
shutil.copyfile(ROOT / 'output/liuren-event-positioning-20261106/probe_opencode.py', OUT / 'probe_opencode.py')
dump(OUT / 'revision.json', {'release': NEW, 'parentRelease': OLD, 'eventPositioning': policy,
    'removed': ['exam/illness actor ID requirement', 'actor-as-day-stem program gate', 'adjudication output role lock', 'kinship regex semantic rejection', 'mandatory role table and extra identity review instructions'],
    'retained': ['event-centered professional methods', '16 domain methods', 'domain reading and full-rule transport', 'deterministic chart/date/arithmetic validation', 'scoped file and result receipt workflow', 'no case/experience retrieval'],
    'externalModelCalled': False, 'predictiveValidationCount': 0})
dump(OUT / 'event-policy.json', policy)
print(json.dumps({'prepared': NEW, 'backedUpFiles': len(files), 'parentRuntimeFiles': len(before['runtime'])}))
