"""Advance the staged hierarchy with an explicit source-preservation revision map."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
OLD='20261105-liqi-led-01'
NEW='20261105-liqi-led-02'
OUT=ROOT/'output'/OLD
SOURCE=ROOT/'knowledge/liuren-v3/revisions'/NEW


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text('utf-8'))
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def inv(p):return {x.relative_to(p).as_posix():sha(x) for x in p.rglob('*') if x.is_file()}


ptr=ROOT/'.opencode/liuren-active.json'; pointer=load(ptr)
old=ROOT/pointer['runtime']; new=ROOT/'runtime/liuren'/NEW
if pointer['release']!=OLD or new.exists() or SOURCE.exists():raise ValueError('unexpected baseline or existing output')
frozen={name:inv(ROOT/'runtime/liuren'/name) for name in ['20261104-chart-first-02',OLD]}
shutil.copytree(old,new)
shutil.copytree(ROOT/pointer['authoringSource'],SOURCE)
for p in [SOURCE/'entry.md',new/'entry.md']:
    write(p,p.read_text('utf-8').replace(OLD,NEW))
manifest=load(new/'manifest.json')
preserve=load(new/manifest['preservationFile'])
changed=set(load(new/'integration-map.json')['changedFiles'])
for row in preserve['modules']:
    rel=manifest['modules'][row['module_id']]['file']
    if rel in changed:
        row['previous_handling']=row['handling']
        row['handling']='用户指定理气主导修订；原始正文与前版保留'
        row['current_revision']=dict(authoring_source=(SOURCE/rel).relative_to(ROOT).as_posix(),
            sha256=sha(new/rel),previous_active_source=(ROOT/'runtime/liuren/20261104-chart-first-02'/rel).relative_to(ROOT).as_posix(),
            previous_active_sha256=sha(ROOT/'runtime/liuren/20261104-chart-first-02'/rel),
            reason='2026-11-05用户明确指定理气统摄全局、象法只描述，并将关键类神关系纳入理气')
preserve['release']=NEW
write(new/manifest['preservationFile'],preserve)
write(SOURCE/manifest['preservationFile'],preserve)
integration=load(new/'integration-map.json')
integration.update(authoringSource=SOURCE.relative_to(ROOT).as_posix(),
    revisionMap=manifest['preservationFile'], parent=OLD,
    note='在不改动已激活01包的前提下补齐正文修订追溯；语义政策保持01版')
write(new/'integration-map.json',integration)
policy=load(new/manifest['shenshaPolicyFile']);policy['release']=NEW
write(new/manifest['shenshaPolicyFile'],policy)
live=ROOT/'.opencode/skills/liuren'
before_live={p.relative_to(ROOT).as_posix():sha(p) for p in live.rglob('*') if p.is_file()}
for p in live.rglob('*.md'):write(p,p.read_text('utf-8').replace(OLD,NEW))
for rel in ['opencode.json','README.md','目录总索引.md']:
    p=ROOT/rel;write(p,p.read_text('utf-8').replace(OLD,NEW))
p=ROOT/'docs/本机六壬完整研判流程.md'
text=p.read_text('utf-8').replace('环节 3 说明对象、依据、实际位置和所答维度，按条件补读神将同用/互换及神将辞义；环节 4 同时核常用类神与其他相关显象',
    '环节 3 核对象、依据和实际位置，贯通四课三传与关键类神的全局理气；环节 4 按条件补读神将同用/互换及辞义，依已判理气描述常用类神与其他相关显象')
write(p,text)
implementation=dict(pointer['workflowImplementation'])
implementation[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
contract=load(new/'loader-contract.json')
contract.update(sourceHashes=implementation,authoringSource=SOURCE.relative_to(ROOT).as_posix())
write(new/'loader-contract.json',contract)
manifest.update(release=NEW,parentRelease=OLD)
manifest['files']={k:v for k,v in inv(new).items() if k!='manifest.json'}
manifest['version']=hashlib.sha256(json.dumps(manifest['files'],sort_keys=True).encode()).hexdigest()
write(new/'manifest.json',manifest)
for name,expected in frozen.items():
    if inv(ROOT/'runtime/liuren'/name)!=expected:raise ValueError('frozen runtime changed')
pointer.update(release=NEW,previousRelease=OLD,runtime=new.relative_to(ROOT).as_posix(),methodVersion=manifest['version'],
    authoringSource=SOURCE.relative_to(ROOT).as_posix(),workflowImplementation=implementation,
    files={'liuren/'+k:v for k,v in inv(live).items()})
temp=ptr.with_suffix('.new.json');write(temp,pointer);temp.replace(ptr)
receipt=load(OUT/'activation.json')
receipt.update(release=NEW,methodVersion=manifest['version'],intermediateRelease=OLD,
    authoringSource=SOURCE.relative_to(ROOT).as_posix(),
    frozenRuntimesUnchanged=list(frozen),after={rel:sha(ROOT/rel) for rel in receipt['before']})
write(OUT/'activation.json',receipt)
text=(OUT/'回退说明.md').read_text('utf-8').replace('当前版本：20261105-liqi-led-01','当前版本：20261105-liqi-led-02')
write(OUT/'回退说明.md',text)
print(json.dumps(dict(release=NEW,version=manifest['version'],files=len(manifest['files']),frozenUnchanged=list(frozen)),ensure_ascii=False))
