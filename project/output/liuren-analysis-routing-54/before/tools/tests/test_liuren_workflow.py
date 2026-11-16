"""Executable session, source-isolation and condition-state boundaries."""
import copy
from contextlib import ExitStack
import json
from pathlib import Path
import sys
import subprocess
import shutil
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import liuren_workflow as w
import experience_retrieval as ex
from liuren_book_cases import expand_identities


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative, body in [('经验日志/a.md', '反吟主反复。'), ('runtime/m.md', '完整方法\n'),
            ('tools/liuren-direct.mjs', 'adapter'), ('tools/liuren-direct/chart.mjs', 'chart'),
            ('tools/liuren-direct/legacy-engine-worker.mjs', 'worker'),
            ('tools/liuren-direct/legacy-engine-manifest.json', '{"files":[]}')]:
            p = self.root / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, 'utf-8')
        self.entry = dict(id='R1', source='经验日志/a.md', line_start=1, line_end=1,
            title='反吟', summary='主反复', source_excerpt='反吟主反复。', categories=['通用'], kind='审读规则',
            verification='原文已核对', caveat='未验证', annotation_status='来源方法', independent_validation_increment=0,
            source_sha256=w.file_hash(self.root / '经验日志/a.md'), conditions=['课体反吟'], exclusions=['非过程问'],
            evidence_refs=[], research_status='source_method', support_case_ids=['OTHER'], counterexample_case_ids=[],
            claim_origin='原载方法', review_state='source_checked', relations=[], branch_selector={'A':'逐角色'}, case_refs=['OTHER'])
        self.ei = dict(entries=[self.entry], relations=[], status=dict(curated_entries=1, entries=1, unreviewed_fragments=0, stale_annotations=[]))
        self.ci = dict(cases=[], units=[], token_df={}, status={})
        self.facts = dict(chart_types=['反吟'], day_stem='庚', transmissions=[], transmission_sequence='')
        self.manifest = dict(release='test', version='v1', modules={'m':dict(file='m.md',requires=[])}, required=['m'],
            domains=[], files={'m.md':w.file_hash(self.root/'runtime/m.md')})
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(w.methods,'active',return_value=(self.root/'runtime',self.manifest)))
        self.stack.enter_context(patch.object(w,'program_chart',return_value=dict(ok=True,facts=self.facts,input={},validation={'ok':True},provenance={},conventions={})))
        self.stack.enter_context(patch.object(w.cases,'ensure_index',return_value=self.ci))
        self.stack.enter_context(patch.object(w.experience,'ensure_index',return_value=self.ei))
        self.run = self.root/'run'
        self.data = dict(chart={'datetime':'2026-08-04T14:32'}, questions=[dict(id='Q1',question='反吟过程如何',
            target='过程',stage='进行中',success_criterion='明确变化',requires=['conclusion'])])

    def prepare(self): return w.prepare(self.data,self.run,self.root)

    def ready(self):
        self.prepare()
        w.read(self.run,'module:m',self.root,page=1)
        for part in ('record','source'):
            first = w.read(self.run,'R1',self.root,part=part)
            for n in range(2,first['pages']+1): w.read(self.run,'R1',self.root,part=part,page=n)
        session=w.load(self.run/'session.json')
        fact=dict(path='facts.day_stem',value='庚')
        rule=dict(id='R1',decision='adopt', evidence_parts=['source'], source_refs=['经验日志/a.md'],
            application=dict(rationale='测试记录的适用声明，非术理证明',fact_refs=[fact]),
            conditions=[dict(index=0,text='课体反吟',role='applicability',status='met',transfer_rationale='测试用',fact_refs=[fact])],
            exclusions=[dict(index=0,text='非过程问',role='exclusion',status='unmet',transfer_rationale='测试用',fact_refs=[fact])],
            strongest_counterexample=dict(status='none_registered'))
        record={k:session[k] for k in ('session_id','session_sha256','facts_sha256','stage')}
        record.update(questions=[dict(id='Q1', conclusion=dict(status='supported',statement='测试判断'),chart_evidence=[fact],rules=[rule])],
            coverage=dict(candidate_ids=session['coverage']['candidate_ids'],unreviewed_limitations=['语义未验证']))
        return record

    def test_complete_chain_is_structural_only(self):
        result=w.check(self.run,self.ready(),self.root)
        self.assertTrue(result['ok'],result['errors'])
        self.assertEqual(result['semantic_correctness'],'unverified')

    def test_optional_audit_never_certifies_reading_or_investigation(self):
        record = self.ready()
        record['questions'][0]['rules'] = []
        result = w.check(self.run, record, self.root)
        self.assertTrue(result['ok'], result['errors'])
        self.assertEqual(result['process_completeness'], 'unverified')
        self.assertTrue(any('经验调查' in warning for warning in result['warnings']))
        receipt = w.read(self.run, 'R1', self.root, part='source')
        self.assertIn('tool_output_only', receipt['receipt_semantics'])

    def test_optional_audit_rejects_invented_and_unread_case_comparisons(self):
        path = self.root / '案例项目库/感情占/case-001.md'
        path.parent.mkdir(parents=True)
        path.write_text('<!-- META: 占类=感情占 | 课体=反吟 -->\n# 复合\n## 问题\n复合过程如何？\n## 原断\n有反复。\n', encoding='utf-8')
        self.ci.update(w.cases.build_index(self.root, files={path.relative_to(self.root).as_posix(): path.read_bytes()}, rows=[]))
        record = self.ready()
        record['case_comparisons'] = [dict(id='NOT-REAL', source='不存在.md', use='比较', transfer_limit='条件不同')]
        self.assertFalse(w.check(self.run, record, self.root)['ok'])
        case = self.ci['cases'][0]
        record['case_comparisons'][0].update(id=case['id'], source=case['source'])
        self.assertFalse(w.check(self.run, record, self.root)['ok'])
        first = w.read(self.run, case['id'], self.root, part='source')
        for page in range(2, first['pages'] + 1):
            w.read(self.run, case['id'], self.root, part='source', page=page)
        self.assertTrue(w.check(self.run, record, self.root)['ok'])
        record['case_comparisons'][0]['source'] = '另一个来源.md'
        self.assertFalse(w.check(self.run, record, self.root)['ok'])

    def test_local_prepare_passes_declared_domain_and_keeps_all_visible_experience_rows(self):
        self.manifest['domains'] = ['relationship']
        self.manifest['modules']['relationship'] = dict(file='m.md', requires=[])
        self.data['domains'] = ['relationship']
        self.entry['categories'] = ['感情占']
        self.prepare()
        packet = w.load(self.run / 'evidence-packet.json')
        self.assertEqual(packet['cases']['query_fields']['占类'], '感情占')
        self.assertEqual(packet['experience']['category_hints'], ['感情占'])
        self.assertEqual(packet['experience']['omitted_by_packet_budget'], 0)

    def test_unknown_and_unmet_cannot_be_adopted(self):
        record=self.ready()
        condition=record['questions'][0]['rules'][0]['conditions'][0]
        for state in ('unknown','unmet'):
            condition.update(status=state,missing='缺资料')
            self.assertFalse(w.check(self.run,record,self.root)['ok'])

    def test_historical_feedback_is_not_a_current_fact(self):
        record=self.ready()
        condition=record['questions'][0]['rules'][0]['conditions'][0]
        condition.update(role='source_outcome',status='source_only',used_as_current_fact=False)
        self.assertFalse(w.check(self.run,record,self.root)['ok'])
        condition['fact_refs']=[]
        record['questions'][0]['rules'][0]['decision']='reference'
        self.assertTrue(w.check(self.run,record,self.root)['ok'])

    def test_same_case_id_cannot_be_read_even_if_known(self):
        self.data['source_id']='OTHER'
        self.prepare()
        with self.assertRaisesRegex(ValueError,'outside session'): w.read(self.run,'R1',self.root)

    def test_suspended_default_related_filter_and_explicit_audit(self):
        suspended=copy.deepcopy(self.entry)
        suspended.update(id='R2',research_status='suspended')
        self.ei['entries'].append(suspended)
        self.ei['relations']=[dict(type='冲突待核',members=['R1','R2'],reason='待核')]
        self.prepare()
        packet=w.load(self.run/'evidence-packet.json')['experience']
        self.assertNotIn('R2',[x['entry']['id'] for x in packet['results']])
        self.assertFalse(any(rel['id']=='R2' for x in packet['results'] for rel in x['related']))
        review=w.read(self.run,'R2',self.root,review=True)
        self.assertFalse(review['adoption_allowed'])
        with self.assertRaises(ValueError): w.read(self.run,'R2',self.root)

    def test_source_and_dependency_mutation_rejected(self):
        self.prepare()
        self.entry['relations']=[dict(type='依赖',target_id='NEW',reason='changed')]
        with self.assertRaisesRegex(ValueError,'eligibility'): w.read(self.run,'R1',self.root)
        self.entry['relations']=[]
        (self.root/'经验日志/a.md').write_text('changed','utf-8')
        with self.assertRaisesRegex(ValueError,'source changed'): w.read(self.run,'R1',self.root)

    def test_facts_session_and_question_coverage_tampering(self):
        record=self.ready()
        record['facts_sha256']='wrong'
        self.assertFalse(w.check(self.run,record,self.root)['ok'])
        session=w.load(self.run/'session.json');session['facts']['day_stem']='甲'
        w.experience.atomic_json(self.run/'session.json',session)
        with self.assertRaisesRegex(ValueError,'integrity'): w.check(self.run,record,self.root)

    def test_timing_quantity_and_unread_pages_required(self):
        self.data['questions'][0]['question']='何时收到多少款'
        with self.assertRaisesRegex(ValueError,'timing'): self.prepare()
        self.data['questions'][0]['requires']=['conclusion','timing','quantity']
        self.manifest['modules'].update(timing=dict(file='m.md',requires=[]),quantity=dict(file='m.md',requires=[]))
        self.prepare()
        session=w.load(self.run/'session.json')
        record={k:session[k] for k in ('session_id','session_sha256','facts_sha256','stage')}
        record.update(questions=[dict(id='Q1',conclusion=dict(status='unknown',statement='未判',missing=['资料']))],
            coverage=dict(candidate_ids=session['coverage']['candidate_ids'],unreviewed_limitations=['未读']))
        result=w.check(self.run,record,self.root)
        self.assertTrue(any('timing' in x for x in result['errors']))
        self.assertTrue(any('unread module' in x for x in result['errors']))

    def test_condition_only_recall_and_packet_preserves_structure_with_budget(self):
        self.entry['conditions']=['仅此条件可命中']
        self.assertEqual(ex.retrieve(self.ei,'仅此条件可命中')['results'][0]['entry']['id'],'R1')
        self.entry['source_case_refs']=[dict(path='book',line_start=1,line_end=3,quote='长原文'*10000,sha256='hash',role='反例')]
        self.entry['research_record']=copy.deepcopy(self.entry)
        packet=ex.evidence_packet(dict(question='反吟',facts=self.facts),root=self.root)
        self.assertLessEqual(len(json.dumps(packet,ensure_ascii=False)),9000)
        row=packet['results'][0]['entry']
        self.assertEqual(row['conditions'],['仅此条件可命中'])
        self.assertEqual(row['branch_selector'],{'A':'逐角色'})
        self.assertFalse(row['source_case_refs'][0]['quote_body_in_packet'])
        self.assertIn('full_record',row)

    def test_source_identity_closure_keeps_blank_boundaries_and_dependencies(self):
        maps=[dict(keys=['A','book:书籍库/a.md:L1-L3'],ranges=[('书籍库/a.md',1,3,['x','',''])],
                   dependency_keys=['book:书籍库/a.md:L4-L5']),
              dict(keys=['B','book:书籍库/a.md:L4-L5'],ranges=[('书籍库/a.md',4,5,['y',''])],dependency_keys=[])]
        self.assertNotIn('A',expand_identities(['book:书籍库/a.md:L2-L3'],maps))
        self.assertIn('A',expand_identities(['book:书籍库/a.md:L1-L1'],maps))
        self.assertNotIn('B',expand_identities(['A'],maps))
        self.assertIn('B',expand_identities(['A'],maps,include_dependencies=True))

    def test_reconstruction_batch_keeps_individual_strict_failures(self):
        verifier=Path(__file__).resolve().parents[1]/'liuren_book_reconstruction_verify.mjs'
        bad=dict(root=str(self.root),link=dict(id='bad',result_path='invalid'),case_id='C',review={})
        result=subprocess.run([shutil.which('node'),str(verifier)],input=json.dumps(dict(requests=[bad,bad])),
            text=True,encoding='utf-8',capture_output=True,timeout=10)
        value=json.loads(result.stdout)
        self.assertFalse(value['ok'])
        self.assertEqual(len(value['results']),2)
        self.assertTrue(all(not x['ok'] for x in value['results']))


if __name__=='__main__': unittest.main()
