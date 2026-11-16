"""Offline acceptance for the integrated workflow; no judgments or model calls."""
import copy
import json
from pathlib import Path
import liuren_workflow as w

OUT = w.ROOT/'output/liuren-consolidation-20261102/workflow'


def main():
    run=OUT/'acceptance-run-final2'
    data=w.load(OUT/'synthetic-input.json')
    data['query']='原已知状态必须明确'
    w.experience.atomic_json(OUT/'acceptance-input.json',data)
    prepared=w.prepare(data,run)
    session=w.load(run/'session.json')
    for module in session['modules']:
        for page in range(1,module['pages']+1):
            w.read(run,'module:'+module['id'],page=page)
    # Read a real new research record, but preserve every applicability unknown.
    research=[(key,item) for key,item in session['candidates'].items() if key.startswith('LR26-')]
    key,item=min(research,key=lambda pair:len(json.dumps(pair[1],ensure_ascii=False)))
    part_receipts=[]
    for part in ('record','source'):
        first=w.read(run,key,part=part)
        part_receipts.append({k:first[k] for k in ('id','part','pages','sha256')})
        for page in range(2,first['pages']+1): w.read(run,key,part=part,page=page)
    rule=item['record']
    reference=dict(id=key,decision='reference',source_refs=list(item['sources']),evidence_parts=['source'],
        strongest_counterexample=dict(status='unknown',missing=['离线程序验收不作术理反例裁决']),
        conditions=[dict(index=i,text=text,role='unknown',status='unknown',missing=['尚未进行本问适用性研判']) for i,text in enumerate(rule.get('conditions',[]))],
        exclusions=[dict(index=i,text=text,role='unknown',status='unknown',missing=['尚未进行本问排除条件研判']) for i,text in enumerate(rule.get('exclusions',[]))])
    record={k:session[k] for k in ('session_id','session_sha256','facts_sha256','stage')}
    record.update(questions=[dict(id=q['id'],rules=[reference] if n==0 else [],chart_evidence=[],**{
        kind:dict(status='unknown',statement='本次仅验证程序链路，不生成占断结论',missing=['人工或模型的专业研判未执行']) for kind in q['requires']})
        for n,q in enumerate(session['questions'])], coverage=dict(candidate_manifest_sha256=w.digest(session['coverage']),
        unreviewed_limitations=['仅程序分页输出并记录凭证；其余候选未逐卡研判，未验证语义或预测效果。']),independent_validation_increment=0)
    w.experience.atomic_json(run/'judgment.json',record)
    accepted=w.check(run,record)
    excluded='LR26-M102B-067-RECONCILE'
    try:
        w.read(run,excluded)
        isolation=dict(ok=False,error='excluded ID was readable')
    except ValueError as error: isolation=dict(ok=True,error=str(error))
    broken=copy.deepcopy(record)
    broken['questions'][0]['rules']=[]
    broken['facts_sha256']='tampered'
    broken['questions'][0].pop('timing',None)
    negative=w.check(run,broken)
    # Preserve the final valid check after the negative controls.
    w.experience.atomic_json(run/'check.json',accepted)
    receipt=dict(schema='liuren-integrated-offline-acceptance-v1',release=session['release'],run=run.relative_to(w.ROOT).as_posix(),
        method_version=session['method_version'],workflow_sources=session['workflow_sources'],
        pillars=session['facts']['pillars'],heaven_earth=len(session['facts']['heaven_earth']),
        facts_sha256=session['facts_sha256'],session_sha256=session['session_sha256'],
        modules=len(session['modules']),module_pages=sum(x['pages'] for x in session['modules']),
        read_record=part_receipts,packet_bytes=(run/'evidence-packet.json').stat().st_size,
        positive=accepted,same_case_isolation=isolation,negative=negative,
        old_release_unchanged=w.load(OUT/'activation.json')['parentInventory']=={
            p.relative_to(w.ROOT/'runtime/liuren/20261027-quantity-02').as_posix():w.file_hash(p)
            for p in (w.ROOT/'runtime/liuren/20261027-quantity-02').rglob('*') if p.is_file()},
        model_calls=0,semantic_inference_performed=False,independent_validation_increment=0)
    receipt['ok']=accepted['ok'] and isolation['ok'] and not negative['ok'] and receipt['old_release_unchanged']
    w.experience.atomic_json(OUT/'offline-acceptance.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    return 0 if receipt['ok'] else 2


if __name__=='__main__': raise SystemExit(main())
