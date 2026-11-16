"""Extend locators from verified original bytes; no theory extraction or source rewriting."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from liuren_book_search import DATA,SCHEMA,EXPECTED_PATHS,build,check
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
data=load(R/'knowledge/liuren-book-index/20261105/catalog.json')
data.update(schema=SCHEMA,version='20261112-seven-book-search-01')
definitions={
 'QA':('北海闲人大六壬指南问答〔完全版〕','utf-8-sig',[1,15,63,67]),
 'KN':('北海闲人《大六门括囊赋》略疏','gb18030',[1]),
 'TR':('北海闲人特训班讲义','gb18030',[1,6,103,158,235,302,357,413,458,485,533,596]),
 'KE':('北海闲人大六门64课经精讲解注','gb18030',[
  1,4,483,550,633,649,675,713,745,774,827,872,892,933,1002,1027,1073,
  1129,1131,1178,1227,1248,1250,1315,1337,1340,1342,1419,1520,1598,
  1673,1729,1821,1876,1944,2009,2069,2148,2219,2221,2287,2342,2345,
  2417,2487,2558,2618,2719,2789,2846,2935,3008,3141,3260,3309,3334,
  3387,3487,3623,3773,3883,4156]),
}
for bid,(title,encoding,starts) in definitions.items():
 path=EXPECTED_PATHS[bid];raw=(R/path).read_bytes();lines=raw.decode(encoding).splitlines()
 headings=[]
 for n in starts:
  anchor=lines[n-1].strip()
  headings.append(dict(line=n,level=1 if n==1 else 2,title=anchor or '原文件起始（含空行）',
   anchor=anchor,kind='mixed-source',boundary_review='original-heading-or-file-start; locator-only; not-semantic-review'))
 data['books'].append(dict(id=bid,title=title,aliases=[title],path=path,encoding=encoding,
  sha256=hashlib.sha256(raw).hexdigest(),line_count=len(lines),
  source_identity='北海闲人本地传本文本；作者讲解、转引古籍、整理者文字与书例反馈依原段分别识别；保留疑字、重复与缺篇，不声明版本完整性。',
  headings=headings,checked_locators=[]))
target=R/DATA;target.mkdir(parents=True,exist_ok=True)
assert not (target/'catalog.json').exists(),'Do not overwrite an existing catalog'
(target/'catalog.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result=build(R)
verified=check(R)
assert verified['ok'],verified['errors']
out=Path(__file__).resolve().parent
(out/'index-check.json').write_text(json.dumps(dict(build=result,check=verified),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
