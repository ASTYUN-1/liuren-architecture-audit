from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
LIVE=OUT/'candidate-live';RUN=OUT/'candidate-runtime'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def body(p):return p.read_text('utf-8-sig')
before=read(OUT/'before-manifest.json');candidate=read(OUT/'candidate-manifest.json');pointer=read(LIVE/'.opencode/liuren-active.json');manifest=read(RUN/'manifest.json')
parent=ROOT/before['parentRuntime'];checks=[]
def check(name,result):
 if not result:raise ValueError(name)
 checks.append({'name':name,'status':'passed'})
def effective(rel):return LIVE/rel if (LIVE/rel).is_file() else ROOT/rel
check('10 frozen runtime bytes unchanged',all(sha(parent/r)==h for r,h in before['runtime'].items()))
check('candidate files exact',all(sha(LIVE/r)==h for r,h in candidate['live'].items()))
check('runtime inventory and hashes',candidate['runtime']==manifest['files'] and all(sha(RUN/r)==h for r,h in manifest['files'].items()) and set(manifest['files'])=={p.relative_to(RUN).as_posix() for p in RUN.rglob('*') if p.is_file() and p.name!='manifest.json'})
check('release/version identity',pointer['release']==manifest['release']==candidate['release']==before['newRelease'] and pointer['methodVersion']==manifest['version']==hashlib.sha256(json.dumps(manifest['files'],sort_keys=True).encode()).hexdigest())
check('implementation hashes',all(sha(effective(r))==h for r,h in pointer['workflowImplementation'].items()))
loader=read(RUN/'loader-contract.json')
check('loader hashes and release',loader['release']==pointer['release'] and all(sha(effective(r))==h for r,h in loader['sourceHashes'].items()))
check('shensha policy identity',read(RUN/'references/shensha-policy.json')['release']==pointer['release'])
check('all professional methods byte-identical',all(sha(RUN/r)==h for r,h in before['runtime'].items() if r.startswith(('methods/','domains/','details/'))))
allowed={'entry.md','manifest.json','loader-contract.json','reading-route.json','references/shensha-policy.json','references/deterministic-tools.md','references/adjudicator-prompt.md'}
check('other parent material unchanged',all(sha(RUN/r)==h for r,h in before['runtime'].items() if r not in allowed))
check('fixed E01-E22 unchanged',sha(RUN/'references/adjudicator-book-evidence.json')==sha(parent/'references/adjudicator-book-evidence.json'))
route=read(RUN/'reading-route.json')
check('14 checks 16 topics 11 stages retained',route==json.loads(json.dumps(read(parent/'reading-route.json')).replace(before['parentRelease'],before['newRelease'])) and sum(len(x['required']) for x in route['stages'])==14 and len(route['domains'])==16 and len(route['legacyCoverage'])==11)
check('no case/experience retrieval',read(RUN/'experiment.json')['disableCaseExperience'] is True)
check('three-book integration',pointer['bookRetrieval']['books']==['RG','LF','TY'] and all(sha(effective(r))==h for r,h in pointer['bookRetrieval']['files'].items()))
cfg=read(LIVE/'opencode.json');slim=read(LIVE/'.opencode/oh-my-opencode-slim.jsonc');agent=slim['agents']['liuren-adjudicator']
check('DeepSeek high and slim retained',agent['model']=='deepseek/deepseek-flash' and agent['variant']=='high' and agent['options']['reasoningEffort']=='high' and pointer['adjudication']['plugin']=='oh-my-opencode-slim')
check('same native permissions',agent['permission']==read(OUT/'before/.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']['permission'] and cfg['agent']['liuren']['permission']==read(OUT/'before/opencode.json')['agent']['liuren']['permission'])
check('child prompt current and repairs visible',agent['prompt']==body(RUN/'references/adjudicator-prompt.md') and all('day_boundary="civil-midnight"' in t for t in [agent['prompt'],cfg['agent']['liuren']['prompt'],body(RUN/'entry.md')]))
check('parent full instructions retained',body(RUN/'references/deterministic-tools.md').startswith(body(parent/'references/deterministic-tools.md')) and agent['prompt'].startswith(body(parent/'references/adjudicator-prompt.md')))
check('entry and three skill hashes',sha(RUN/'entry.md')==sha(LIVE/'.opencode/skills/liuren/daliuren/SKILL.md') and all(sha(LIVE/'.opencode/skills'/r)==h for r,h in pointer['files'].items()))
check('new native schema used in direct and packet tools','args:computeSchemas.args' in body(LIVE/'.opencode/plugins/liuren-adjudication.ts') and 's.array(computeSchemas.computation)' in body(LIVE/'.opencode/plugins/liuren-adjudication.ts'))
old_pointer=read(OUT/'before/.opencode/liuren-active.json')
check('overlay dependencies unchanged',all(sha(ROOT/'tools'/n)==old_pointer['workflowImplementation']['tools/'+n] for n in ['liuren-deterministic.mjs','liuren-deterministic-io.mjs','liuren-shensha.mjs']))
check('no extra model stage',pointer['computeInterface']['modelCallsAdded']==0 and pointer['deterministicFoundation']==old_pointer['deterministicFoundation'] and pointer['adjudication']==old_pointer['adjudication'])
env=os.environ.copy();env['LIUREN_TEST_CODE_ROOT']=str(LIVE)
node=Path(shutil.which('node'));node=node.with_suffix('.exe') if os.name=='nt' else node
wire=read(OUT/'fixed-wire.json')
check('actual OpenCode outbound capture matches candidate',wire['exitCode']==0 and wire['realModelCalled'] is False and all(not r['referenceErrors'] for r in wire['requests']) and all(sha(effective(r))==h for r,h in wire['implementationSha256'].items()))
args=[str(node),'--import',(OUT/'candidate-import.mjs').as_uri(),'--test',*['tools/tests/'+f for f in ['liuren-wire-schema.test.mjs','liuren-compute-interface.test.mjs','liuren-deterministic.test.mjs','liuren-adjudication-contract.test.mjs','liuren-adjudication-plugin.test.mjs','liuren-chart-health.test.mjs','liuren-shensha.test.mjs']]]
start=time.monotonic();proc=subprocess.run(args,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',timeout=60)
(OUT/'candidate-tests.log').write_text(proc.stdout,encoding='utf-8')
check('107 integration tests passed',proc.returncode==0 and 'pass 107' in proc.stdout and 'fail 0' in proc.stdout)
result={'status':'passed','release':pointer['release'],'candidateManifestSha256':sha(OUT/'candidate-manifest.json'),'wireCaptureSha256':sha(OUT/'fixed-wire.json'),'checks':checks,'testLogSha256':sha(OUT/'candidate-tests.log'),'passedTests':107,'testSeconds':round(time.monotonic()-start,3),'externalModelCalled':False}
(OUT/'candidate-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','staticChecks':len(checks)-1,'testsPassed':107,'release':pointer['release']}))
