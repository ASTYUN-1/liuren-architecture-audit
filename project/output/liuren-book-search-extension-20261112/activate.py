"""Bind the retrieval extension in a fresh runtime; preserve all professional method bytes."""
from pathlib import Path
import hashlib,json,os,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
enc=lambda d:(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(O/'before.json');p=load(R/'.opencode/liuren-active.json')
OLD=before['release'];NEW='20261112-book-search-48'
assert p['release']==OLD
assert all(sha(R/f)==h for f,h in before['frozen'].items())
runtime=R/'runtime/liuren'/NEW;assert not runtime.exists()
shutil.copytree(R/p['runtime'],runtime)
pending={}
for rel in ['opencode.json','README.md','目录总索引.md']:
 pending[rel]=(R/rel).read_text(encoding='utf-8').replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW).replace('指向 `'+OLD+'`','指向 `'+NEW+'`').encode('utf-8')
note=('48版便捷检索扩展：原有三书加北海《指南问答〔完全版〕》《大六门括囊赋略疏》《特训班讲义》《64课经精讲解注》，'
 'book可选RG/LF/TY/QA/KN/TR/KE。检索、普通续读与裁决原文交接按原文件哈希和已核编码处理，不转码或改写原书。'
 '只扩本机查书能力，分类取用规则尚未据本轮研究修改，未发布网站。重启OpenCode加载新工具枚举；历史任务沿原绑定材料。'
 '全行索引不等于全书精读或预测验证。验收及回滚见output/liuren-book-search-extension-20261112/。')
for rel in ['README.md','目录总索引.md']:
 pending[rel]=pending[rel].rstrip()+('\n\n'+note+'\n').encode('utf-8')
pending['AGENTS.md']=((R/'AGENTS.md').read_text(encoding='utf-8').rstrip()+'\n\n'+note+'\n').encode('utf-8')
current_sha=lambda f:hashlib.sha256(pending[f]).hexdigest() if f in pending else sha(R/f)
changed=['tools/liuren_book_search.py','tools/liuren_material_scope.py','tools/liuren-deterministic-io.mjs','.opencode/tools/liuren_materials.ts','tools/liuren-source-encodings.json']
retrieval=dict(p['bookRetrieval'])
retrieval.update(release='20261112-seven-book-search-01',scope='local-opencode-and-codex',books=['RG','LF','TY','QA','KN','TR','KE'],
 catalog='knowledge/liuren-book-index/20261112/catalog.json',index='knowledge/liuren-book-index/20261112/index.sqlite3',
 backup=O.relative_to(R).as_posix()+'/before',rollback=O.relative_to(R).as_posix()+'/rollback.py',compatibleMethodRelease=NEW,
 professionalMethodsChanged=False,originalBytesChanged=False)
retrieval['files']={f:current_sha(f) for f in set(retrieval['files'])|set(changed) if f not in ['knowledge/liuren-book-index/20261105/catalog.json','knowledge/liuren-book-index/20261105/index.sqlite3']}
for f in [retrieval['catalog'],retrieval['index']]:retrieval['files'][f]=current_sha(f)
for name in ['loader-contract.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
 d=load(runtime/name);d['release']=NEW
 if name=='loader-contract.json':
  d.update(parentRelease=OLD,bookRetrieval=retrieval)
  for f in changed:d['sourceHashes'][f]=current_sha(f)
  for f in ['opencode.json','docs/本机六壬资料检索范围.md','integrations/codex/daliuren-codex/references/host.md']:
   if f in d['sourceHashes']:d['sourceHashes'][f]=current_sha(f)
 (runtime/name).write_bytes(enc(d))
m=load(runtime/'manifest.json');m.update(release=NEW,parentRelease=OLD,bookRetrieval=retrieval)
m['files']={f:sha(runtime/f) for f in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
(runtime/'manifest.json').write_bytes(enc(m))
p.update(release=NEW,runtime=runtime.relative_to(R).as_posix(),previousRelease=OLD,methodVersion=m['version'],
 backup=O.relative_to(R).as_posix()+'/before',authoringSource=O.relative_to(R).as_posix(),bookRetrieval=retrieval)
for f in changed:p['workflowImplementation'][f]=current_sha(f)
for f in ['opencode.json','docs/本机六壬资料检索范围.md','integrations/codex/daliuren-codex/references/host.md']:
 if f in p['workflowImplementation']:p['workflowImplementation'][f]=current_sha(f)
pending['.opencode/liuren-active.json']=enc(p)
assert all(sha(R/f)==h for f,h in before['frozen'].items())
professional=[f for f in m['files'] if f.startswith(('methods/','domains/','procedures/')) or f=='references/judgment-core.md']
assert all(sha(runtime/f)==sha(R/before['runtime']/f) for f in professional)
for rel in sorted(pending,key=lambda f:f=='.opencode/liuren-active.json'):
 target=R/rel;temp=target.with_name(target.name+'.book48.tmp');temp.write_bytes(pending[rel]);os.replace(temp,target)
after=dict(release=NEW,runtime=p['runtime'],files={f:sha(R/f) for f in before['files']},
 new_files={f:sha(R/f) for f in ['tools/liuren-source-encodings.json',retrieval['catalog'],retrieval['index']]},
 frozen47_unchanged=True,professional_files_unchanged=professional,model_calls_added=0,predictive_validation_count=0)
(O/'after.json').write_bytes(enc(after))
print(json.dumps(dict(release=NEW,professional_files_unchanged=len(professional),frozen47_unchanged=True),ensure_ascii=False))
