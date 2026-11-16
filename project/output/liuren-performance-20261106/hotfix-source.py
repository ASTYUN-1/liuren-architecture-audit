"""Apply the truncation repair after the first isolated host has exited."""
from pathlib import Path
import json, hashlib, shutil
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
load = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert (OUT/'real-run/run-summary.json').exists(), 'Do not change source during the first run'
pointer = load(ROOT/'.opencode/liuren-active.json')
assert pointer['release'] == '20261106-performance-24'
before = load(OUT/'before.json')
extra = 'tools/liuren-adjudication-output.mjs'
if extra not in before['live']:
    target = OUT/'before'/extra
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT/extra, target)
    before['live'][extra] = sha(ROOT/extra)
    (OUT/'before.json').write_text(json.dumps(before, ensure_ascii=False, indent=2), 'utf-8')
backup = OUT/'before24'
assert not backup.exists()
for rel in before['live']:
    p = backup/rel
    p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT/rel, p)
baseline = {'release': pointer['release'], 'runtime': pointer['runtime'],
            'live': {r: sha(ROOT/r) for r in before['live']},
            'runtimeFiles': {f.relative_to(ROOT/pointer['runtime']).as_posix(): sha(f)
                             for f in (ROOT/pointer['runtime']).rglob('*') if f.is_file()}}
(OUT/'before24.json').write_text(json.dumps(baseline, ensure_ascii=False, indent=2), 'utf-8')
f = ROOT/'.opencode/plugins/liuren-adjudication.ts'
t = f.read_text('utf-8-sig')
t = t.replace('liuren-tools-24', 'liuren-tools-25')
t = t.replace('裁决者保存报告。result接受正文字符串或自由JSON对象', '裁决者保存报告。优先result填写完整Markdown正文字符串，减少长嵌套JSON括号错误；也接受自由JSON对象')
t = t.replace("p.state?.status==='completed'){\n      try{const out=JSON.parse(p.state.output)", "p.state?.status==='completed'&&p.state.metadata?.truncated!==true){\n      try{const out=JSON.parse(p.state.output)")
needle = '  async function binding(sessionID:string){'
helper = '''  async function confirmedRead(sessionID:string,bound:any){
    const loaded=await loadPacket(directory,bound.ref);
    const messages=await client.session.messages({path:{id:sessionID},query:{directory}});
    if(messages.error)throw new Error('LIUREN_ADJUDICATION_SESSION_LOOKUP_FAILED');
    bound.readPages=verifiedPages(messages.data??[],bound.ref,loaded);
    return loaded;
  }
'''
assert needle in t
t = t.replace(needle, helper+needle)
old = 'const bound=await binding(context.sessionID),packet=(await loadPacket(directory,bound.ref)).envelope.packet;'
assert old in t
t = t.replace(old, 'const bound=await binding(context.sessionID),packet=(await confirmedRead(context.sessionID,bound)).envelope.packet;')
old = 'const content=await loadPacket(directory,bound.ref);\n          if(args.page>content.pages)'
assert old in t
t = t.replace(old, 'const content=await confirmedRead(context.sessionID,bound);\n          if(args.page>content.pages)')
t = t.replace('const bound=authorized.get(child)??await binding(child);\n', 'const bound=authorized.get(child)??await binding(child);\n          await confirmedRead(child,bound);\n')
t = t.replace("// Bounded full transport owns truncation. The host's generic 50KB cap\n          // must not cut a batch while recording its pages as completely read.", "// Native custom tools apply host truncation before generic metadata checks.\n          // Project tool_output limits cover bounded batches; submit rechecks actual receipts.")
f.write_text(t, 'utf-8')
f = ROOT/'tools/liuren-adjudication-output.mjs'
t = f.read_text('utf-8-sig').replace('result可为非空正文字符串或自由JSON对象。', '优先提交{result:完整Markdown正文字符串}；也兼容自由JSON对象。不要传value，不把整个工具参数转成JSON字符串；JSON报错只修对应引号/括号，保持原报告，不重新权衡。')
f.write_text(t, 'utf-8')
config = load(ROOT/'opencode.json')
config['tool_output'] = {'max_bytes': 350000, 'max_lines': 20000}
(ROOT/'opencode.json').write_text(json.dumps(config, ensure_ascii=False, indent=2)+'\n', 'utf-8')
f = ROOT/'.opencode/oh-my-opencode-slim.jsonc'
slim = load(f)
slim['agents']['liuren-adjudicator']['prompt'] += '\n提交优先用liuren_adjudication_submit({result: 完整Markdown正文字符串})，正文保留完整判断与依据，避免手写多层长JSON。自由JSON仍兼容。遇语法错误只补对应引号/括号或转为同一报告正文，不重新权衡，不原样重复错误参数。\n'
f.write_text(json.dumps(slim, ensure_ascii=False, indent=2)+'\n', 'utf-8')
# Build another immutable runtime; retain both first-run code and its evidence.
build = (OUT/'build-release.py').read_text('utf-8-sig')
build = build.replace("OUT/'before.json'", "OUT/'before24.json'").replace("NEW='20261106-performance-24'", "NEW='20261106-performance-25'")
build = build.replace("source+'/before'", "source+'/before24'")
build = build.replace('24版提速只减少', '25版提速只减少').replace('tool_contract=liuren-tools-24', 'tool_contract=liuren-tools-25').replace("toolContract='liuren-tools-24'", "toolContract='liuren-tools-25'")
build = build.replace("guide='", "guide='宿主tool_output上限350000字节/20000行，覆盖有界全文合批；提交时重新比对宿主实际返回的每页全文与hash，截断回执不计读完。")
build = build.replace('24版全文合批：', '25版全文合批：')
build = build.replace("dump(OUT/'activation.json'", "dump(OUT/'activation25.json'")
(OUT/'build-release25.py').write_text(build, 'utf-8')
print('Prepared source correction and immutable version 25 builder')
