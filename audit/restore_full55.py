"""Restore the existing complete baseline to a NEW directory, never in place."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil

PACKAGE = Path(__file__).resolve().parents[1]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify(root):
    pointer=json.loads((root/'.opencode/liuren-active.json').read_text('utf-8-sig'))
    runtime=root/pointer['runtime']
    manifest=json.loads((runtime/'manifest.json').read_text('utf-8-sig'))
    contract=json.loads((runtime/'loader-contract.json').read_text('utf-8-sig'))
    rows=[]
    for label,base,values in [
        ('runtime',runtime,manifest['files']),
        ('implementation',root,pointer.get('workflowImplementation',{})),
        ('loader',root,contract.get('sourceHashes',{})),
        ('skills',root/'.opencode/skills',pointer.get('files',{})),
        ('books',root,pointer.get('bookRetrieval',{}).get('files',{}))]:
        for name,expected in values.items():
            p=base/name
            actual=digest(p) if p.is_file() else None
            rows.append({'group':label,'path':name,'expected':expected,'actual':actual,'ok':actual==expected})
    return {'release':pointer['release'],'ok':all(x['ok'] for x in rows),'checks':rows,
            'migration_note':'Absolute OpenCode read permission paths remain original; rebind separately for another root. No dependencies installed.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--target',required=True,type=Path)
    p.add_argument('--core-only',action='store_true',help='Verification copy: omit historical runtime/output assets, keep the complete 55 core and knowledge sources.')
    a=p.parse_args();target=a.target.resolve()
    if target.exists():raise SystemExit('Target must not exist; refusing overwrite.')
    if target==PACKAGE or target.is_relative_to(PACKAGE):raise SystemExit('Target cannot be inside the package.')
    if (target/'.opencode/liuren-active.json').exists():raise SystemExit('Refusing a live workspace.')
    if os.name=='nt':target=Path('\\\\?\\'+str(target))
    project=PACKAGE/'project'
    if os.name=='nt' and not str(project).startswith('\\\\?\\'):project=Path('\\\\?\\'+str(project))
    for base,ds,fs in os.walk(project):
        rel=Path(base).relative_to(project)
        if a.core_only:
            if rel==Path('.'):ds[:]=[x for x in ds if x!='output']
            if rel==Path('runtime/liuren'):ds[:]=[x for x in ds if x=='20261114-tool-reliability-55']
        for name in fs:
            src=Path(base)/name;dest=target/rel/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
    overlay=PACKAGE/'profiles/full55-overlay'
    if os.name=='nt' and not str(overlay).startswith('\\\\?\\'):overlay=Path('\\\\?\\'+str(overlay))
    for src in overlay.rglob('*'):
        if src.is_file():
            dest=target/src.relative_to(overlay);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
    # Restore exact registered historical reference files even in core-only mode.
    refmap=json.loads((target/'runtime/liuren/20261114-tool-reliability-55/source-read-map.json').read_text('utf-8'))
    for row in refmap.get('aliases',{}).values():
        rel=row['path'];src=project/rel
        if src.is_file() and not (target/rel).is_file():
            dest=target/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
    result=verify(target)
    (target/'RESTORATION-VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'target':str(target),'release':result['release'],'ok':result['ok'],'checks':len(result['checks']),'mismatches':[r['path'] for r in result['checks'] if not r['ok']]},ensure_ascii=False))
    if not result['ok']:raise SystemExit(2)


if __name__=='__main__':main()
