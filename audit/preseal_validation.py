from pathlib import Path
import hashlib,json,os,re
root=Path(__file__).resolve().parents[1]
if os.name=='nt' and not str(root).startswith('\\\\?\\'):root=Path('\\\\?\\'+str(root))
manifest=json.loads((root/'audit/source-manifest.json').read_text('utf-8'))
issues=[];secrets=[]
strong=re.compile(rb'\b(?:sk|sk-proj)-[A-Za-z0-9_-]{20,}\b|\bgh[pousr]_[A-Za-z0-9]{25,}\b|\bAKIA[A-Z0-9]{16}\b')
for row in manifest:
    p=root/row['path']
    if not p.is_file():issues.append({'path':row['path'],'kind':'missing'});continue
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=row['sha256']:issues.append({'path':row['path'],'kind':'hash-mismatch'})
    if strong.search(raw):secrets.append({'path':row['path'],'kind':'strong-credential-pattern'})
for p in root.rglob('*'):
    if p.is_file():
        rel=p.relative_to(root)
        if any(part in {'node_modules','.git','.portable','private','.env','__pycache__'} for part in rel.parts):issues.append({'path':rel.as_posix(),'kind':'excluded-path-found'})
result={'source_files_checked':len(manifest),'source_export_hash_issues':issues,'strong_credential_pattern_findings':secrets,'ok':not issues and not secrets,'scope':'source files export hashes and strong credential patterns; exclusions checked across package; no model calls'}
(root/'audit/preseal-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
