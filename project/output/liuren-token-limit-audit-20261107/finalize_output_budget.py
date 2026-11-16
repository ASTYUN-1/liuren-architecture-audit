"""Finalize release metadata after the initial copy and source updates."""
from pathlib import Path
import hashlib,json,os
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
old='20261107-slim-29';new='20261107-slim-30';cap=393216
p=load(ROOT/'.opencode/liuren-active.json');assert p['release']==old
source=ROOT/p['runtime'];target=ROOT/'runtime/liuren'/new;backup=OUT/'before-output-budget'
initial=load(OUT/'output-budget-before.json');before=initial['files'];frozen=initial['frozen29'];rels=list(before)
assert 'output.maxOutputTokens=393216;' in (ROOT/'.opencode/plugins/liuren-adjudication.ts').read_text('utf-8')
code=(OUT/'activate_output_budget.py').read_text('utf-8')
exec(compile(code[code.index("m=load(target/'manifest.json')"):],str(OUT/'activate_output_budget.py'),'exec'))
