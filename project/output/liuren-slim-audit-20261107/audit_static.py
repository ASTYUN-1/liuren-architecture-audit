"""Read-only inspection of the active package; writes evidence to this directory only."""
from pathlib import Path
import json, hashlib, re, collections, importlib.util

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RT = ROOT / 'runtime/liuren/20261106-performance-25'
DIRS = ['references', 'details', 'domains', 'methods', 'procedures']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((RT/'manifest.json').read_text('utf-8'))
route = json.loads((RT/'reading-route.json').read_text('utf-8'))
rows, paragraphs = [], collections.defaultdict(list)
for folder in DIRS:
    for p in sorted((RT/folder).glob('*')):
        t = p.read_text('utf-8-sig')
        links = []
        for m in re.finditer(r'\[[^\]]*\]\(<?([^\s)>]+)>?\)', t):
            target = m[1].split('#')[0]
            if '://' not in target and target:
                dest = (p.parent/target).resolve()
                links.append({'target': target, 'exists': dest.exists(), 'line': t[:m.start()].count('\n')+1})
        row = {'file': str(p.relative_to(RT)).replace('\\','/'), 'bytes': p.stat().st_size,
               'chars':len(t), 'lines':len(t.splitlines()), 'sha256':sha(p),
               'headings':[s for s in t.splitlines() if s.startswith('#')], 'links':links}
        rows.append(row)
        for match in re.finditer(r'[^\n]+(?:\n(?!\s*\n)[^\n]+)*', t):
            para=match[0].strip()
            if len(para)>=60:
                paragraphs[para].append({'file': row['file'], 'line':t[:match.start()].count('\n')+1})
external = ['AGENTS.md', '.opencode/skills/liuren/daliuren/SKILL.md', 'opencode.json',
            '.opencode/oh-my-opencode-slim.jsonc','docs/本机六壬高效执行.md',
            'docs/本机六壬完整研判流程.md','docs/本机六壬直接排盘.md',
            'docs/本机六壬资料检索范围.md','docs/本机OpenCode完整输出规则.md']
external_rows=[]
for rel in external:
    p=ROOT/rel
    if p.exists():
        t=p.read_text('utf-8-sig'); external_rows.append({'file':rel,'bytes':p.stat().st_size,'chars':len(t),'sha256':sha(p)})
        for m in re.finditer(r'[^\n]+(?:\n(?!\s*\n)[^\n]+)*',t):
            if len(m[0].strip())>=60: paragraphs[m[0].strip()].append({'file':rel,'line':t[:m.start()].count('\n')+1})
spec=importlib.util.spec_from_file_location('loader', ROOT/'tools/load-liuren-methods.py')
loader=importlib.util.module_from_spec(spec); spec.loader.exec_module(loader)
runtime, active=loader.active(ROOT)
plans={}
for name, domains, timing in [('baseline',[],False),('exam',['exam'],False),('illness',['illness'],False),('finance_timing',['finance'],True)]:
    items=[]
    for step in loader.plan_steps(active, domains=domains, timing=timing):
        p,t,h=loader.content(runtime,active,step['id'])
        items.append(dict(id=step['id'],file=str(p.relative_to(ROOT)).replace('\\','/'),chars=len(t),bytes=len(t.encode('utf-8')),stage=step['stage']))
    plans[name]={'items':items,'chars':sum(i['chars'] for i in items),'bytes':sum(i['bytes'] for i in items)}
summary={'release':active['release'],'directories':{},'files':rows,'external':external_rows,
         'modules':active['modules'],'required':active['required'],'plans':plans,
         'duplicate_paragraphs':[{'text':t,'occurrences':v} for t,v in paragraphs.items() if len(v)>1]}
for folder in DIRS:
    selected=[r for r in rows if r['file'].startswith(folder+'/')]
    summary['directories'][folder]={'files':len(selected),'bytes':sum(r['bytes'] for r in selected),'chars':sum(r['chars'] for r in selected)}
(OUT/'inventory.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),'utf-8')
snapshot={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in RT.rglob('*') if p.is_file()}
snapshot.update({r['file']:r['sha256'] for r in external_rows})
(OUT/'baseline-sha256.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({'directories':summary['directories'],'modules':len(active['modules']),'plans':{k:{'count':len(v['items']),'chars':v['chars'],'ids':[x['id'] for x in v['items']]} for k,v in plans.items()},'duplicates':len(summary['duplicate_paragraphs'])},ensure_ascii=False,indent=2))
