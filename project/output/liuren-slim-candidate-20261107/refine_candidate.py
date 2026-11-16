"""Complete candidate metadata and remove remaining legacy execution branches."""
from build_candidate import ROOT, OUT, BASE, HOST, C, NEW, old, take, load, sha, write, dump
import re
import shutil
import hashlib
import json

def main():
    # Metadata must match the host release. Every other policy value is preserved.
    policy=load(BASE/'references/shensha-policy.json'); policy['release']=NEW
    dump(C/'references/shensha-policy.json',policy)
    for file in ['references/shensha-meanings.md','references/shensha-other-meanings.md']:
        text=old(file)
        text=re.sub(r'本轮38项起法已逐项回查[^\n]*\n\n','',text)
        text=text.replace('起法与基准见 [32项核查表](<shensha-focus.md>)，程序读取及已核差异见 [引擎字段](<engine-shensha-output.md>)。','起法、基准和落点直接用程序结果，取用条件见 [神煞取用](shensha-use.md)。')
        substitutions={
            '先核日支表及作用对象':'按程序支德位置核作用对象',
            '并保留引擎与优先笔记起法的差异':'不因医名预设有效',
            '与天医的起法成对核，不交叉拼配两种表':'位置沿用程序已定结果',
            '当前本地岁病符表与所选起法不符，采用前须保留冲突。':'采用程序已修正岁病符位置。',
            '起法反序分歧继续依清单处理。':'位置以程序所选结果为准。',
            '再与日干分组起法、位置和神将作用合看':'再与程序位置和神将作用合看',
            '与死符、死气各核起法和对象':'与死符、死气分身份、对象及作用',
            '起法与落点分别核对':'程序所给身份与落点分别使用',
        }
        for a,b in substitutions.items():text=text.replace(a,b)
        write(C/file,text)

    # The old general page becomes a use dictionary; formulas/rankings remain in BASE.
    dictionary='''# 神煞组合义补充

固定起法、别名、采用状态和坐标直接用程序结果；本页仅保留旧参考独有的组合候选。普通32项及其他单项义见shensha-use、shensha-meanings、shensha-other-meanings。历史公式和星级已退出执行，原文件留在冻结基线。

组合只在本问、成员位置、气态及制救条件齐备时参与，不把几个名相加当作已发生事件；未采用成员不凑组合。

'''+take('references/daliuren-shensha.md','## 神煞叠加速查','## 神煞状态判断')
    write(C/'references/daliuren-shensha.md',dictionary)
    blade='''# 两刃的取用身份

直接使用程序分列的阳刃与羊刃，不重算禄前位或阴阳顺逆，不因古籍混称互换标签。阳刃为用户指定重点，羊刃次要；相近争斗、刀刃、煎熬、血光义可参，不能作为两份独立证据。具体对象、神将气态、空墓和有效作用仍须成立，不凭一刃保证或排除伤灾、手术或剖产。

阳刃仅采用已定阳干位，阴干逆取停用；羊刃按程序固定十干表。名称身份与取位文献依据分开。历史全表、异说及原文出处保留于冻结基线references/blade-methods.md，只有明确维护或考据时读，不在每课复核。
'''
    write(C/'references/blade-methods.md',blade)
    pos=(C/'methods/positioning.md').read_text('utf-8')
    clause='；涉及土胎取类仍按mapping-provenance D02的未决条件，不双取凑答案'
    pos=re.sub('(?:'+re.escape(clause)+')+',clause,pos)
    if clause not in pos:pos=pos.replace('参照与程序口径见 liqi','参照与程序口径见 liqi'+clause)
    write(C/'methods/positioning.md',pos)

    # Retain meaning and use conditions, discard historical notes in the daily table.
    target=C/'references/shensha-use.md';text=target.read_text('utf-8')
    text=text.replace('死符（岁支/岁干异法）','死符（固定岁干法）')
    text=text.replace('笔记括注“帝旺所冲”存疑，以明确映射核，不改写原文。','')
    text=text.replace('本轮固定岁干表，另一法仅研究，','')
    text=text.replace('选DQ明确表保留出处，不按有利结果换表。','')
    text=text.replace('岁法SF-11、SF-15；月法见shensha-authority-review S08M及《壬归》LF963，旧SF-20异月法保留研究','岁法SF-11、SF-15；月法《壬归》LF963')
    text=text.replace('所采用的阳干支位见《理法简易》LF2656，但该原文明称“羊刃”；不能据支位相同证明古籍已用“阳刃”名称。指南十干表也原称羊刃。阴干逆取仍停用；取位依据与名称身份分开。','《理法简易》LF2656；原文称羊刃，名称身份与程序标签分开。')
    write(target,text)

    # Expose research only through a deliberate source gap, not an automatic hop.
    liqi=(C/'methods/liqi.md').read_text('utf-8')
    timing_note='三传全局、日上当前近事是有来源的时间层读法，使用时分别说明；类神三传与通常三传分列，确有专法需要才展开，不把任意下一传叫阴神。占时先锋仅作本问相关端倪，不无条件否决其他关系。'
    if timing_note not in liqi:
        liqi=liqi.replace('## 主客取与和结果依赖',timing_note+'\n\n## 主客取与和结果依赖')
    liqi=liqi.replace('## 2. 对关键节点检查得气与受伤','## 节点得气与受伤').replace('## 3. 分清五气、十二气和六亲的参照','## 五气、十二气和六亲的参照').replace('## 4. 合、刑冲破害与遁干','## 合、刑冲破害与遁干').replace('## 5. 裁决救制的作用范围','## 救制的作用范围').replace('## 八煞逐项核查','### 八煞的对象与作用')
    write(C/'methods/liqi.md',liqi)
    for name in ['天干参与及奇门参照-补充审阅稿.md','核心归纳-审阅稿.md','原文证据摘录.md','天一群笔记专项核查.md']:
        rel='docs/应期取数归纳-20261027/'+name
        dest=HOST/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
    m=load(C/'manifest.json');pointer=load(HOST/'.opencode/liuren-active.json')
    route=load(C/'reading-route.json')
    route['conditional']['liqi-sources']['trigger']='方法条件或作用解释存在会影响本问的真实分歧；不复议程序固定起法'
    route['conditional']['mapping-provenance']['trigger']='取类条件存在影响本问的真实缺口或D01—D04未决，只补相关原段'
    m['conditional']={key:item['trigger'] for key,item in route['conditional'].items()}
    for key,trigger in m['conditional'].items():m['modules'][key]['trigger']=trigger
    dump(C/'reading-route.json',route)
    loader=load(C/'loader-contract.json')
    loader.update(release=NEW,parentRelease='20261106-performance-25',authoringSource=OUT.relative_to(ROOT).as_posix())
    loader['sourceHashes']={rel:sha(HOST/rel) for rel in loader.get('sourceHashes',{}) if (HOST/rel).is_file()}
    loader['toolUsage']['professionalRulesChanged']='prompt organization changed; predictive equivalence unverified'
    dump(C/'loader-contract.json',loader)
    # Fix the inherited copy's own runtime paths; keep historical evidence maps separate.
    for field in ['boundedReview','expertAdjudicationReview']:
        if field in pointer:pointer[field]['scope']='historical baseline evidence, not candidate validation'
    pointer['computeInterface']['release']=NEW
    m['computeInterface']['release']=NEW
    m['toolUsage']['professionalRulesChanged']='prompt organization changed; predictive equivalence unverified'
    m['moduleAliases']=m['slimming']['aliases']
    m['sourcePolicy']='Current professional methods and original books; case/experience libraries disabled; history retained in baseline.'
    # Runtime dependencies required for deterministic integration checks only.
    engine=load(ROOT/'tools/liuren-direct/legacy-engine-manifest.json')
    for row in engine['files']:
        rel='排盘工具魔改/'+row['path'];f=ROOT/rel;dest=HOST/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
    # This named local Node dependency is needed by the unchanged TypeScript tool schemas.
    # It is intentionally not copied; the integration verifier resolves it from the real host.
    m['files']={f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file() and f.name!='manifest.json'}
    m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
    dump(C/'manifest.json',m)
    pointer['methodVersion']=m['version']
    dump(HOST/'.opencode/liuren-active.json',pointer)
    build=load(OUT/'build.json');build['candidateManifestSha256']=sha(C/'manifest.json');dump(OUT/'build.json',build)
    print('refined '+NEW)

if __name__=='__main__':main()
