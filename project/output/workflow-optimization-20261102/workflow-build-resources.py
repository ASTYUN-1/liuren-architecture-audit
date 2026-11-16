"""Build a new immutable website release; never changes local methods/baseline.
Run from repository root: python output/workflow-optimization-20261102/workflow-build-resources.py
"""
from pathlib import Path
import hashlib,json,shutil,re,os,argparse
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/workflow-optimization-20261102'
def long(p):
 p=p.resolve()
 return Path('\\\\?\\'+str(p)) if os.name=='nt' and not str(p).startswith('\\\\?\\') else p
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--runtime-baseline');parser.add_argument('--destination',default=str(OUT/'resource-candidate'));args=parser.parse_args()
 baseline=long(OUT/'resource-baseline');dest=long(Path(args.destination))
 if dest.exists():
  assert (dest/'knowledge-manifest.json').read_bytes()==(baseline/'knowledge-manifest.json').read_bytes(), 'completed candidate is immutable'
 else:shutil.copytree(baseline,dest)
 if args.runtime_baseline:shutil.copytree(long(Path(args.runtime_baseline)),dest,dirs_exist_ok=True)
 active=json.loads((ROOT/'.opencode/liuren-active.json').read_text(encoding='utf-8'));local=ROOT/active['runtime']
 source=json.loads((local/'manifest.json').read_text(encoding='utf-8'))
 assert source['version']==active['methodVersion'] and len(source['modules'])==49
 km=json.loads((dest/'knowledge-manifest.json').read_text(encoding='utf-8'))
 old=json.loads((dest/'liuren-runtime.json').read_text(encoding='utf-8'))
 prefix='.opencode/skills/daliuren/refs/runtime/'
 for name,h in source['files'].items():
  raw=long(local/name).read_bytes();assert sha(raw)==h,name
  target=dest/(prefix+name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 (dest/(prefix+'manifest.json')).write_bytes((local/'manifest.json').read_bytes())
 # Preserve the package entry verbatim. The server adds website permissions.
 (dest/'.opencode/skills/daliuren/SKILL.md').write_bytes((local/'entry.md').read_bytes())
 docs=km['documents'];byhash={}
 for d in docs:byhash.setdefault(d['provenance']['sourceHash'],[]).append(d['id'])
 docids={d['id'] for d in docs};links={};published={};queue=[]
 module_ids={(local/m['file']).resolve(): 'skill:daliuren/refs/runtime/'+m['file'] for m in source['modules'].values()}
 module_ids[(local/'entry.md').resolve()]='skill:daliuren/SKILL.md'
 def publish(path):
  path=path.resolve()
  if path in module_ids:return [module_ids[path]]
  if path in published:return published[path]
  raw=long(path).read_bytes();h=sha(raw)
  if h in byhash:published[path]=byhash[h];return byhash[h]
  try:text=raw.decode('utf-8-sig');encoding='utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'
  except UnicodeDecodeError:text=raw.decode('gb18030');encoding='gb18030'
  # The source snapshot plus complete decoded sections retain all bytes and
  # source line provenance; no excerpt or summary replaces the original.
  rel='_workflow_sources/'+h+path.suffix;target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);km['files'][rel]=h
  chunks=[];chunk='';size=0
  for c in text:
   n=len(c.encode())
   if size+n>6000:chunks.append(chunk);chunk='';size=0
   chunk+=c;size+=n
  if chunk:chunks.append(chunk)
  ids=[];start=0;line=1
  for i,part in enumerate(chunks,1):
   data=part.encode();key='reference:'+sha(rel.encode())[:20]+':'+str(i);file='_workflow_sections/'+sha(rel.encode())[:20]+'/'+str(i)+'.txt';p=dest/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);km['files'][file]=sha(data)
   docs.append(dict(id=key,file=file,source=rel,hash=sha(data),kind='reference',title=path.name,meta={},provenance=dict(sourceHash=h,encoding=encoding,feedback='unknown',decodedHash=sha(text.encode()),section=i,sections=len(chunks),decodedByteStart=start,decodedByteEnd=start+len(data),lineStart=line,lineEnd=line+part.count('\n'))))
   ids.append(key);start+=len(data);line+=part.count('\n')
  published[path]=ids;byhash[h]=ids;queue.append((path,ids,text));return ids
 # Parse explicit Markdown links; code array expressions are not links.
 pattern=re.compile(r'\[[^\]\n]+\]\((?:<([^>\n]+)>|([^\s()]+))\)')
 unresolved=[]
 def bind(path,ids,text):
  for match in pattern.finditer(text):
   href=match[1] or match[2]
   if href.startswith(('http:','https:','mailto:','#','skill:')):continue
   raw=re.sub(r':\d+(?:-\d+)?$','',href.split('#',1)[0])
   target=(path.parent/raw).resolve()
   if not target.is_file():
    # Old source includes literal engine-code array syntax in Markdown-like
    # text. These are evidence, not file navigation and remain verbatim.
    if not any(c in raw for c in ['"',"'",'(',')','[',']']):unresolved.append([str(path.relative_to(ROOT)),href])
    continue
   targets=publish(target)
   for sourceid in ids:links.setdefault(sourceid,{})[href]=targets
 for path,id in module_ids.items():bind(path,[id],path.read_text(encoding='utf-8'))
 # Follow only references reached from the active modules, plus exact original
 # sources asserted by the new research evidence; never copy the whole library.
 curated=ROOT/'output/应期取数归纳-20261027/curated-evidence.json'
 curatedids=publish(curated)
 evidence=json.loads(curated.read_text(encoding='utf-8'))
 for item in evidence:
  path=ROOT/item['source'].replace('\\','/');assert sha(path.read_bytes())==item['source_sha256'],item['id']
  ids=publish(path)
  for sourceid in curatedids:links.setdefault(sourceid,{})[item['source']]=ids
 index=0
 while index<len(queue):
  path,ids,text=queue[index];index+=1
  if path.suffix.lower()=='.md':bind(path,ids,text)
 if unresolved:raise RuntimeError('unresolved active links: '+json.dumps(unresolved,ensure_ascii=False))
 dump(dest/'knowledge-links.json',links)
 adapter=dest/'tools/website-retrieval.py';s=adapter.read_text(encoding='utf-8')
 s=s.replace("    bindings =", "    limit = request.get('limit', 8)\n    exclude = request.get('excludeSources', [])\n    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 20 or not isinstance(exclude, list) or len(exclude) > 20 or any(not isinstance(x, str) or not x.strip() or len(x) > 300 for x in exclude):\n        raise ValueError('invalid_retrieval_options')\n    bindings =")
 s=s.replace('fields=fields, limit=5','fields=fields, limit=limit, exclude=exclude').replace('query=query, limit=5, preferred_categories','query=query, limit=limit, exclude=exclude, preferred_categories')
 adapter.write_text(s,encoding='utf-8')
 runtime=dict(schemaVersion=3,mode='enhanced',release=source['release'],localMethodVersion=source['version'],version='',files={},modules={key:dict(file=v['file'],id='skill:daliuren/refs/runtime/'+v['file'],requires=v['requires'],when=v['trigger']) for key,v in source['modules'].items()},required=source['required'],routes={},legacyAliases=old['legacyAliases'],entryId='skill:daliuren/SKILL.md')
 route=json.loads((local/'reading-route.json').read_text(encoding='utf-8'));runtime['routes']={k:[k] for k in route['domains']};runtime['readingRoute']=route
 for name in ['.opencode/skills/daliuren/SKILL.md',prefix+'manifest.json',*[prefix+n for n in source['files']],'knowledge-links.json']:runtime['files'][name]=sha((dest/name).read_bytes());km['files'][name]=runtime['files'][name]
 canonical=json.dumps(dict(files=dict(sorted(runtime['files'].items())),mode=runtime['mode']),ensure_ascii=False,separators=(',',':'))
 runtime['version']=sha(canonical.encode());dump(dest/'liuren-runtime.json',runtime)
 for name in ['liuren-runtime.json','tools/website-retrieval.py']:km['files'][name]=sha((dest/name).read_bytes())
 dump(dest/'knowledge-manifest.json',km)
 changed=[k for k in old['modules'] if sha(long(baseline/(prefix+old['modules'][k]['file'])).read_bytes())!=sha(long(local/source['modules'][k]['file']).read_bytes())]
 receipt=dict(identity='offline-resource-build-no-model-no-deployment',localRelease=active['release'],localMethodVersion=source['version'],websiteVersion=runtime['version'],moduleCount=len(source['modules']),sharedModules=len(old['modules']),unchangedShared=len(old['modules'])-len(changed),changedModules=changed,newModules=sorted(set(source['modules'])-set(old['modules'])),documents=len(docs),sourceTargetsTracked=len(published),sourceFilesAdded=sum(name.startswith('_workflow_sources/') for name in km['files']),linkSources=len(links),linkCount=sum(map(len,links.values())),manifestHash=sha((dest/'knowledge-manifest.json').read_bytes()),unresolvedLinks=unresolved)
 receipt['destination']=str(dest);receipt['runtimeBaseline']=args.runtime_baseline
 dump(OUT/'workflow-resource-receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
