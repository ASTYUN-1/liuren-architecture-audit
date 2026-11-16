from pathlib import Path
import sys,json,hashlib
root=Path.cwd(); out=root/'output/liuren-modern-pilot10-20261102';out.mkdir(exist_ok=True)
sys.path.insert(0,str(root/'tools'))
import liuren_knowledge_workbench as w,experience_retrieval as e
base=w.validated_records(root)
files={p.relative_to(root).as_posix():p.read_bytes() for p in sorted((root/'经验日志').rglob('*.md')) if not p.name.startswith('_') and p.name not in e.STOP_FILES}
idx=e.build_index(root,files=files,catalog_bytes=(root/e.SNAPSHOT).read_bytes())
qs=['走失 干加支 长生','合同 六合 空亡','交车合 复合','胃 稼穑 财库','反吟 升迁','相亲 年命 定位','疾病 长生 虎鬼','月建 填实 空亡','尊卑 干支 定位','考试 丑未 朱雀','考试 数量 分数','炎上 官印 考试']
res=[]
for q in qs:
 terms=q.split(); scored=[]
 for r in base['rules']:
  t=json.dumps({k:r.get(k) for k in ['title','conditions','conclusion','reasoning_steps']},ensure_ascii=False)
  n=sum(t.count(x) for x in terms)
  if n:scored.append((n,r))
 scored.sort(key=lambda x:-x[0]);rs=[r for n,r in scored[:3]]
 old=e.retrieve(idx,q,limit=3)
 fs=[]
 for f in base['families']:
  t=json.dumps({k:f.get(k) for k in ['title','common_method']},ensure_ascii=False)
  n=sum(t.count(x) for x in terms)
  if n:fs.append((n,f))
 fs.sort(key=lambda x:-x[0]);fs=[f for n,f in fs[:2]]
 res.append({'query':q,'rules':rs,'legacy':old['results'],'families':fs})
 print('\nQUERY',q)
 for r in rs:print('RULE',r['id'],r['title'],'条件=',r['conditions'],'断=',r['conclusion'])
 for v in old['results']:
  r=v['entry'];print('OLD',r['id'],r['title'],r['summary'],r['source_excerpt'][:700])
 for f in fs:print('FAMILY',f['id'],f['title'],f['common_method'])
(out/'targeted-search.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'baseline.json').write_text(json.dumps({'summary':base['summary'],'rule_count':len(base['rules']),'legacy_count':len(idx['entries']),'family_count':len(base['families']),'source_sha256':hashlib.sha256((root/'书籍库/现代著作/当代壬占汇选第五版.md').read_bytes()).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
