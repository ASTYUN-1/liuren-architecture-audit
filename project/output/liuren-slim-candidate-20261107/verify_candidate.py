"""Check actual candidate loading, wire pages, routes and baseline preservation."""
from build_candidate import ROOT, OUT, BASE, HOST, C, NEW, load, sha, dump, write
import importlib.util
import json
import subprocess
import hashlib

def import_file(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
    checks=[]
    def check(name,condition,detail=None):
        assert condition,(name,detail)
        checks.append({'check':name,'passed':True,**({'detail':detail} if detail is not None else {})})
    baseline=load(ROOT/'output/liuren-slim-audit-20261107/baseline-sha256.json')
    changed=[rel for rel,h in baseline.items() if sha(ROOT/rel)!=h]
    check('原活动包及外围113文件未改',not changed,{'checked':len(baseline),'changed':changed})
    check('原活动指针仍为25版',load(ROOT/'.opencode/liuren-active.json')['release']=='20261106-performance-25')
    loader=import_file(HOST/'tools/load-liuren-methods.py','candidate_loader')
    runtime,m=loader.active(HOST)
    check('候选指针与manifest路由一致',runtime==C)
    bad=[rel for rel,h in m['files'].items() if sha(C/rel)!=h]
    check('候选全文件hash一致',not bad,{'files':len(m['files'])})
    for key in m['modules']:loader.content(runtime,m,key)
    check('全部登记模块可读',True,{'modules':len(m['modules'])})
    p0=load(BASE/'references/shensha-policy.json');p1=load(C/'references/shensha-policy.json')
    p0.pop('release');p1.pop('release')
    check('神煞policy只变release元数据',p0==p1)
    copied=[file for file in (HOST/'tools').rglob('*') if file.is_file() and '__pycache__' not in file.parts]
    differences=[f.relative_to(HOST).as_posix() for f in copied if sha(f)!=sha(ROOT/f.relative_to(HOST))]
    check('候选程序源码逐字节未改',not differences,{'files':len(copied),'differences':differences})
    engine=load(ROOT/'tools/liuren-direct/legacy-engine-manifest.json')
    check('测试引擎副本字节未改',all(sha(HOST/'排盘工具魔改'/row['path'])==row['sha256'] for row in engine['files']),{'files':len(engine['files'])})
    default=loader.plan(m)
    check('默认只读8个唯一共用模块',default==m['required'] and len(default)==8)
    legacy=set(m['moduleAliases'])
    check('旧6模块退出必读链',not legacy.intersection(default))
    for domain in m['domains']:
        selected=loader.plan(m,[domain]);assert selected.count(domain)==1;assert set(selected)==set(default)|{domain}
    check('16专项按本问进入且无旁支',True,{'domains':len(m['domains'])})
    for key in m['conditional']:
        selected=loader.plan(m,extras=[key]);assert key in selected
    check('13触发分支可达',True,{'conditions':len(m['conditional'])})
    selected=loader.plan(m,['finance'],timing=True,extras=['quantity','quantity-sources'],nianming=True)
    check('时间数量年命分支保留',{'finance','timing','quantity','quantity-sources','nianming'}.issubset(selected))
    # Read and verify exact actual CLI page bytes, not just in-process source text.
    page_count=0; module_count=0
    for key in default+['exam','illness','finance','timing','quantity','quantity-sources']:
        _,body,_=loader.content(C,m,key)
        pages=loader.page_text(body);actual=[]
        for n in range(1,len(pages)+1):
            out=subprocess.run(['python','-X','utf8',str(HOST/'tools/load-liuren-methods.py'),'read',key,'--page',str(n)],cwd=HOST,capture_output=True,check=True).stdout
            meta,text=loader.parse_page_output(out);actual.append(text);page_count+=1
        assert ''.join(actual)==body;module_count+=1
    check('实际CLI逐页全文与回执一致',True,{'modules':module_count,'pages':page_count})
    # Every domain-specific paragraph is retained literally; remove only the two registered common paragraphs.
    import re
    checked=0
    for original in (BASE/'domains').glob('*.md'):
        text=original.read_text('utf-8-sig');new=(C/'domains'/original.name).read_text('utf-8')
        for p in re.split(r'\n\s*\n',text):
            if p.startswith(('共同规则只按 class-mapping 执行一次。','原专项上下文与历史来源身份见 mapping-provenance。')):continue
            assert p.strip() in new,(original.name,p[:80]);checked+=1
    check('专项独有段落及未决路径原样保留',True,{'paragraphs':checked})
    # E conditions stay exactly in both active configuration and reference counterpart.
    before=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']
    after=load(HOST/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']
    basis=before['prompt'][before['prompt'].index('## 裁决依据'):before['prompt'].index('日干和组合的参照、成员由模型依原法核明')]
    check('裁决依据与E01—E22条件全文保留',basis in after['prompt'])
    check('裁决模型及high未变',all(before.get(key)==after.get(key) for key in ['model','variant','options','permission']))
    baseline_loader=import_file(ROOT/'tools/load-liuren-methods.py','baseline_loader')
    br,bm=baseline_loader.active(ROOT)
    def measure(runtime,manifest,domains=(),timing=False):
        rows=loader.plan(manifest,domains,timing)
        texts=[loader.content(runtime,manifest,key)[1] for key in rows]
        return {'modules':len(rows),'chars':sum(map(len,texts)),'utf8_bytes':sum(len(t.encode()) for t in texts),'pages':sum(len(loader.page_text(t)) for t in texts)}
    measurements={}
    for name,domains,timing in [('共用必读',[],False),('考试',['exam'],False),('疾病',['illness'],False),('财务与应期',['finance'],True)]:
        before_size=measure(br,bm,domains,timing);after_size=measure(C,m,domains,timing)
        measurements[name]={'before':before_size,'after':after_size,'charsReductionPercent':round((1-after_size['chars']/before_size['chars'])*100,2)}
    old_config=load(ROOT/'opencode.json');new_config=load(HOST/'opencode.json')
    def front(root,config):
        return sum(len((root/p).read_text('utf-8-sig')) for p in config['instructions'])+len(config['agent']['liuren']['prompt'])+len((root/'.opencode/skills/liuren/daliuren/SKILL.md').read_text('utf-8-sig'))
    measurements['入口加主prompt加自动instructions']={'beforeChars':front(ROOT,old_config),'afterChars':front(HOST,new_config),'note':'AGENTS is separately compared; this is not measured inference token usage.'}
    measurements['AGENTS']={'beforeChars':len((ROOT/'AGENTS.md').read_text('utf-8-sig')),'afterChars':len((HOST/'AGENTS.md').read_text('utf-8-sig'))}
    measurements['裁决prompt']={'beforeChars':len(before['prompt']),'afterChars':len(after['prompt'])}
    dump(OUT/'verification.json',{'checks':checks,'measurements':measurements,'predictiveValidationCount':0,'nativeModelRun':False,'candidateActivated':False})
    print(json.dumps({'passed':len(checks),'measurements':measurements},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
