from pathlib import Path
from collections import Counter
import hashlib
import json
import os
import re

base=Path(__file__).resolve().parents[1]
if os.name=='nt' and not str(base).startswith('\\\\?\\'):base=Path('\\\\?\\'+str(base))
project=base/'project'


def load(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data):(base/'audit'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


runtime=[];references=[]
for d in sorted((project/'runtime/liuren').iterdir()):
    mpath=d/'manifest.json'
    if not mpath.is_file():continue
    m=load(mpath);bad=[]
    for name,expected in m.get('files',{}).items():
        p=d/name
        if not p.is_file() or sha(p)!=expected:bad.append({'path':name,'missing':not p.is_file()})
    runtime.append({'release':d.name,'checked':len(m.get('files',{})),'ok':not bad,'issues':bad})
    path=d/'source-read-map.json'
    if path.is_file():
        rows=[]
        for alias,ref in load(path).get('aliases',{}).items():
            p=project/ref['path'];actual=sha(p) if p.is_file() else None
            rows.append({'alias':alias,'path':ref['path'],'ok':actual==ref['sha256'],'missing':not p.is_file()})
        references.append({'release':d.name,'ok':all(x['ok'] for x in rows),'checked':len(rows),'issues':[x for x in rows if not x['ok']]})
dump('frozen-runtime-verification.json',runtime)
dump('registered-source-map-verification.json',references)

books=[]
for cat in sorted((project/'knowledge/liuren-book-index').glob('*/catalog.json')):
    for book in load(cat).get('books',[]):
        p=project/book['path'];books.append({'catalog':str(cat.relative_to(project)).replace('\\','/'),'id':book['id'],'path':book['path'],'ok':p.is_file() and sha(p)==book['sha256']})
dump('registered-book-verification.json',books)

imports=[]
for folder in ['tools','.opencode/plugins','.opencode/tools']:
    for p in (project/folder).rglob('*'):
        if not p.is_file() or p.suffix not in {'.mjs','.js','.ts'}:continue
        body=p.read_text('utf-8-sig')
        for rel in re.findall(r'''(?:from\s*|import\s*\(|require\s*\(|new URL\s*\()\s*["']([^"']+)["']''',body):
            if not rel.startswith('.'):continue
            target=Path(os.path.normpath(str(p.parent/rel)))
            generated=rel.endswith('/') and ('/tmp/' in rel or rel.startswith('./calculations'))
            imports.append({'source':p.relative_to(project).as_posix(),'target':rel,'exists':target.exists(),'generated_directory':generated,'is_test': '/tests/' in p.as_posix()})
dump('local-import-verification.json',imports)

raw=load(base/'audit/unresolved-references.json');kinds=Counter(x['kind'] for x in raw)
groups=Counter(x['source'].split('/')[0] for x in raw)
triage=[]
for x in raw:
    state='historical-or-documentation-reference-requires-context'
    t=x['target'];p=project/t
    if p.is_file():state='present-after-closure'
    elif (project/'经验日志'/Path(t).name).is_file() and '经验' in x['source']:state='experience-relative-link-resolved'
    elif x['source'].startswith(('tools/','.opencode/')) and '/tests/' not in x['source']:state='current-source-reference-review'
    triage.append({**x,'triage':state})
dump('reference-triage.json',triage)

lines=['# 模块与 Skill 索引','', '由导出时实际 manifest 与 Skill 元数据生成。全文保存在下列路径，trigger/requires 不是已执行证明。','']
for release in ['20261114-tool-reliability-55','20261115-class-selection-62','20261105-liqi-led-02','20261102-integrated-01']:
    m=load(project/'runtime/liuren'/release/'manifest.json')
    lines += ['## '+release,'','| 模块ID | 实际作用/触发条件 | 依赖 | 必查/别名 | 正文 |','|---|---|---|---|---|']
    for key,v in m.get('modules',{}).items():
        when=v.get('trigger',v.get('when','按本版入口/reading-route选择；查看正文适用条件'))
        lines.append('| '+key+' | '+str(when).replace('|','／')+' | '+', '.join(v.get('requires',[]))+' | '+str(v.get('required',False))+(' / alias:'+v['aliasOf'] if v.get('aliasOf') else '')+' | `project/runtime/liuren/'+release+'/'+v['file']+'` |')
    lines += ['']
lines += ['## 本机主要 Skill','']
for rel in ['integrations/codex/daliuren-codex/SKILL.md','.opencode/skills/liuren/daliuren/SKILL.md','.opencode/skills/liuren/liuren-cases/SKILL.md','.opencode/skills/liuren/liuren-extract/SKILL.md']:
    p=project/rel;body=p.read_text('utf-8-sig');desc=(re.findall(r'^description:\s*(.*)$',body,re.M) or [''])[0]
    lines += ['- `project/'+rel+'`：'+desc]
lines+=['','全部历史 Skill 原文的路径、name、description、hash另见 skill-catalog.json；历史数量不表示同一流程同时调用这些 Skill。']
(base/'audit/模块与Skill索引.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

promptdir=base/'prompts';promptdir.mkdir(exist_ok=True)
full=load(base/'profiles/full55-overlay/opencode.json');current=load(project/'opencode.json')
for name,text in [('OpenCode-55-主入口原始Prompt.md',full['agent']['liuren']['prompt']),('OpenCode-62-短答试验原始Prompt.md',current['agent']['liuren']['prompt']),('OpenCode-裁决角色配置原始Prompt.md',load(project/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']['prompt']),('55-runtime-裁决角色原文.md',(project/'runtime/liuren/20261114-tool-reliability-55/references/adjudicator-prompt.md').read_text('utf-8'))]:
    (promptdir/name).write_text(text,encoding='utf-8')
diff=[]
for rel in ['entry.md','references/judgment-core.md','methods/adjudication.md','methods/report.md',*['domains/'+x+'.md' for x in load(project/'runtime/liuren/20261114-tool-reliability-55/manifest.json').get('domains',[])]]:
    a=project/'runtime/liuren/20261114-tool-reliability-55'/rel;b=project/'runtime/liuren/20261115-class-selection-62'/rel
    if a.is_file() and b.is_file():diff.append({'path':rel,'full55_sha256':sha(a),'current62_sha256':sha(b),'same_bytes':sha(a)==sha(b)})
dump('full55-vs-current62-content.json',diff)
summary={'runtime_releases':len(runtime),'runtime_hash_checks':sum(x['checked'] for x in runtime),'runtime_issues':[x for x in runtime if not x['ok']],'registered_source_checks':sum(x['checked'] for x in references),'source_map_issues':[x for x in references if not x['ok']],'book_checks':len(books),'book_issues':[x for x in books if not x['ok']],'local_imports':len(imports),'missing_current_imports':[x for x in imports if not x['exists'] and not x['is_test'] and not x['generated_directory']],'missing_test_imports':[x for x in imports if not x['exists'] and x['is_test']],'raw_link_candidates':len(raw),'raw_link_kinds':dict(kinds),'raw_link_roots':dict(groups),'triage_counts':dict(Counter(x['triage'] for x in triage))}
dump('static-audit-summary.json',summary)
print(json.dumps({**{k:v for k,v in summary.items() if k not in {'missing_test_imports'}},'missing_test_import_count':len(summary['missing_test_imports'])},ensure_ascii=False,indent=2))
