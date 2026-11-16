"""Apply one reviewed guard-order correction before activation and reseal."""
from build_variant import HERE, ROOT, CAND, j, jb, sha, swap

plan=j(HERE/'switch-plan.json')
assert not (ROOT/plan['runtime']).exists()
rel='tools/liuren_material_scope.py'
p=CAND/rel
text=swap(p.read_text('utf-8'),"            path = (self.root / reference['path']).resolve()\n",
          "            path = (self.root / reference['path']).resolve()\n            if self.no_case_experience and not self.permitted(path):\n                raise ValueError('LIUREN_EXPERIMENT_NO_RETRIEVAL: 对照研判不读取两库历史快照。')\n")
p.write_text(text,'utf-8')
package=CAND/plan['runtime']
contract=j(package/'loader-contract.json');contract['sourceHashes'][rel]=sha(p.read_bytes())
(package/'loader-contract.json').write_bytes(jb(contract))
for row in plan['packageChanges']:
    if row['path']=='loader-contract.json':row['after']=sha((package/'loader-contract.json').read_bytes())
revision=j(package/'no-retrieval-revision.json')
for row in revision['changes']:
    if row['path']=='loader-contract.json':row['after']=sha((package/'loader-contract.json').read_bytes())
(package/'no-retrieval-revision.json').write_bytes(jb(revision))
manifest=j(package/'manifest.json')
manifest['files']={p.relative_to(package).as_posix():sha(p.read_bytes()) for p in sorted(package.rglob('*')) if p.is_file() and p.name!='manifest.json'}
import json
manifest['version']=sha(json.dumps(manifest['files'],sort_keys=True).encode())
(package/'manifest.json').write_bytes(jb(manifest))
ptrpath=CAND/'.opencode/liuren-active.json'
ptr=j(ptrpath);ptr['methodVersion']=manifest['version'];ptrpath.write_bytes(jb(ptr))
plan['methodVersion']=manifest['version']
plan['newRuntimeFiles']={p.relative_to(package).as_posix():sha(p.read_bytes()) for p in package.rglob('*') if p.is_file()}
for row in plan['externalFiles']:row['after']=sha((CAND/row['path']).read_bytes())
(HERE/'switch-plan.json').write_bytes(jb(plan))
print(manifest['version'])
