"""Active integration: category coverage, conditional cost, transport and scoped access.

These tests validate the reading workflow, never correctness of a prediction.
"""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from liuren_material_scope import MaterialScope
from experience_retrieval import DOMAIN_CATEGORIES

spec=importlib.util.spec_from_file_location('mapping_loader',ROOT/'tools/load-liuren-methods.py')
loader=importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)


class ClassMappingTests(unittest.TestCase):
    def setUp(self):
        self.runtime,self.m=loader.active(ROOT)

    def test_global_liqi_and_structure_precede_optional_symbol_expansion(self):
        for domain in self.m['domains']:
            steps=loader.plan_steps(self.m,[domain],extras=['shen-symbols','jiang-symbols'])
            keys=[s['id'] for s in steps]
            for core in ['relations','liqi','void','structure']:
                self.assertEqual(next(s['stage'] for s in steps if s['id']==core),3)
                self.assertLess(keys.index(domain),keys.index(core))
                self.assertLess(keys.index(core),keys.index('shenjiang-use'))
            self.assertLess(keys.index('movement'),keys.index('adjudication'))
            self.assertEqual(len(keys),len(set(keys)))

    def test_original_methods_are_preserved_and_consolidation_is_traceable(self):
        policy=json.loads((self.runtime/self.m['preservationFile']).read_text('utf-8'))
        rows={r['module_id']:r for r in policy['modules']}
        baseline=ROOT/'runtime/liuren/20261103-local-restore-01'
        original=json.loads((baseline/'manifest.json').read_text('utf-8'))
        scope=MaterialScope(ROOT)
        for key,item in original['modules'].items():
            with self.subTest(module=key):
                self.assertIn(key,self.m['modules'])
                row=rows[key];source=ROOT/row['original_source']
                self.assertTrue(scope.permitted(source))
                self.assertEqual(loader.sha(source.read_bytes()),row['original_sha256'])
                self.assertIn((baseline/item['file']).read_text('utf-8'),source.read_text('utf-8'))
                self.assertTrue(row['retained_aspects'])
                self.assertTrue((self.runtime/row['active_file']).is_file())

    def test_category_rules_precede_positioning_and_selected_domain(self):
        for domain in ['relationship','interpersonal','recruitment','promotion-salary','finance',
                       'exam','illness','pregnancy','home','travel','lost-person-object','weather','agriculture']:
            with self.subTest(domain=domain):
                steps=loader.plan_steps(self.m,[domain])
                keys=[s['id'] for s in steps]
                self.assertLess(keys.index('class-mapping'),keys.index('positioning'))
                self.assertLess(keys.index('positioning'),keys.index(domain))
                self.assertLess(keys.index(domain),keys.index('relations'))
                self.assertEqual(keys[-1],'report')
                self.assertEqual([s['stage'] for s in steps],sorted(s['stage'] for s in steps))

    def test_consolidated_rules_keep_every_specific_condition_and_exclusion(self):
        cards=json.loads((ROOT/'knowledge/liuren-research/20261102/rules/classical-mapping-20261103.json').read_text('utf-8'))
        sj=json.loads((ROOT/'knowledge/liuren-research/20261102/rules/shenjiang-mapping-20261103.json').read_text('utf-8'))
        domains={'relationship':'婚恋伴侣','interpersonal':'人际交往','recruitment':'事业任职',
                 'promotion-salary':'事业任职','finance':'财务经营','exam':'学业考核','illness':'疾病求医',
                 'pregnancy':'胎产生育','home':'家宅地产','travel':'出行行人',
                 'lost-person-object':'失物盗逃','weather':'天时环境','agriculture':'农渔畜养'}
        covered=set()
        def check(card,text):
            self.assertIn(card['id'],text)
            self.assertIn(card['conclusion'],text)
            for field in ['conditions','exclusions','alternatives']:
                for value in card[field]:
                    if value!='具体使用仍以完整专项条件为限；本批无独立效果验证。':
                        self.assertIn(value,text,(card['id'],field))
        for key,label in domains.items():
            text=loader.content(self.runtime,self.m,key)[1]
            for card in cards:
                if '-C' in card['id'] and label in card['categories']:
                    with self.subTest(module=key,card=card['id']):check(card,text)
                    covered.add(card['id'])
            gap={'finance':'D01','pregnancy':'D02','agriculture':'D04'}.get(key)
            if gap:check(next(c for c in cards if c['id'].endswith(gap)),text)
        self.assertEqual(covered,{c['id'] for c in cards if '-C' in c['id']})
        for key,prefix in [('shen-symbols','T'),('jiang-symbols','J')]:
            text=loader.content(self.runtime,self.m,key)[1]
            for card in sj:
                if card['id'].startswith('LR26-SJ-'+prefix):
                    with self.subTest(module=key,card=card['id']):check(card,text)

    def test_consolidation_keeps_all_existing_reading_routes(self):
        baseline=ROOT/'runtime/liuren/20261103-class-mapping-02'
        previous=json.loads((baseline/'manifest.json').read_text('utf-8'))
        previous['readingRoute']=json.loads((baseline/previous['routingFile']).read_text('utf-8'))
        self.assertEqual(set(previous['required']),set(self.m['required']))
        # Preserve coverage while moving global liqi/structure before symbol expansion.
        moved={'liqi','void','structure','evidence'}
        for old,new in zip(previous['readingRoute']['stages'],self.m['readingRoute']['stages']):
            self.assertEqual(old['id'],new['id'])
            self.assertEqual([k for k in old['required'] if k not in moved],
                             [k for k in new['required'] if k not in moved])
        evidence_stage=next(s['id'] for s in self.m['readingRoute']['stages'] if 'evidence' in s['required'])
        self.assertEqual(evidence_stage,10)
        self.assertEqual(previous['domains'],self.m['domains'])
        for key,condition in previous['readingRoute']['conditional'].items():
            expected=dict(condition)
            if key in ['liqi-sources','risk']:expected['stage']=3
            if key in ['shenjiang-use','shen-symbols','jiang-symbols']:expected['stage']=4
            self.assertEqual(expected,self.m['readingRoute']['conditional'][key])
        for domain in previous['domains']:
            for conditions in [[],*[[k] for k in previous['conditional']],list(previous['conditional'])]:
                with self.subTest(domain=domain,conditions=conditions):
                    self.assertEqual(set(loader.plan(previous,[domain],extras=conditions)),
                                     set(loader.plan(self.m,[domain],extras=conditions)))

    def test_previous_text_is_preserved_and_revised_methods_have_pinned_sources(self):
        baseline=ROOT/'runtime/liuren/20261103-class-mapping-02'
        previous=json.loads((baseline/'manifest.json').read_text('utf-8'))
        policy=json.loads((self.runtime/self.m['preservationFile']).read_text('utf-8'))
        rows={r['module_id']:r for r in policy['modules']}
        self.assertEqual(set(rows),set(previous['modules']))
        scope=MaterialScope(ROOT)
        for key,item in previous['modules'].items():
            with self.subTest(module=key):
                row=rows[key];source=ROOT/row['original_source']
                self.assertEqual(source.read_bytes(),(baseline/item['file']).read_bytes())
                response=scope.read(source,count=1)
                self.assertEqual(response['start'],1)
                if 'current_revision' in row:
                    revision=row['current_revision']
                    authored=ROOT/revision['authoring_source']
                    active=self.runtime/self.m['modules'][key]['file']
                    self.assertEqual(authored.read_bytes(),active.read_bytes())
                    self.assertEqual(loader.sha(active.read_bytes()),revision['sha256'])
                    parent=ROOT/revision['previous_active_source']
                    self.assertEqual(loader.sha(parent.read_bytes()),revision['previous_active_sha256'])
                elif row['handling']=='正文不变':
                    self.assertEqual(source.read_bytes(),(self.runtime/self.m['modules'][key]['file']).read_bytes())
        for relative,digest in policy['rules'].items():
            self.assertEqual(loader.sha((ROOT/relative).read_bytes()),digest)

    def test_dictionary_lookup_loads_common_constraints_once_after_global_liqi(self):
        base=loader.plan(self.m,['relationship'])
        for key in ['shenjiang-use','shen-symbols','jiang-symbols']:
            self.assertNotIn(key,base)
        selected=loader.plan_steps(self.m,['relationship'],extras=['shen-symbols','jiang-symbols'])
        keys=[s['id'] for s in selected]
        self.assertEqual(keys.count('shenjiang-use'),1)
        self.assertLess(keys.index('shenjiang-use'),keys.index('shen-symbols'))
        self.assertLess(keys.index('shenjiang-use'),keys.index('jiang-symbols'))
        for key in ['shenjiang-use','shen-symbols','jiang-symbols']:
            self.assertEqual(next(s['stage'] for s in selected if s['id']==key),4)

    def test_new_domain_tags_and_old_supplemental_routes_coexist(self):
        for key,tag in {'home':'家宅占','travel':'出行占','weather':'天时占','agriculture':'农事占'}.items():
            self.assertEqual(DOMAIN_CATEGORIES[key],tag)
            self.assertIn(key,self.m['domains'])
        for key in ['period-outlook','long-period','classical-conflict']:
            self.assertIn(key,loader.plan(self.m,[key]))

    def test_scoped_reader_switches_only_to_the_active_runtime(self):
        scope=MaterialScope(ROOT)
        p=json.loads((ROOT/'.opencode/liuren-active.json').read_text('utf-8'))
        for key in ['class-mapping','shenjiang-use','shen-symbols','jiang-symbols','home','travel','weather','agriculture']:
            path=self.runtime/self.m['modules'][key]['file']
            self.assertTrue(scope.permitted(path))
            self.assertFalse(scope.permitted(ROOT/'runtime/liuren'/p['previousRelease']/self.m['modules'][key]['file']))
        self.assertFalse(scope.permitted(ROOT/'output/神将互换与分类取用接入-20261103/before/.opencode/liuren-active.json'))

    def test_new_module_pages_reconstruct_exact_content_and_pinned_hash(self):
        for key in ['class-mapping','shenjiang-use','shen-symbols','jiang-symbols','home','travel','weather','agriculture']:
            path,text,digest=loader.content(self.runtime,self.m,key)
            pages=loader.page_text(text)
            self.assertEqual(''.join(pages),text)
            self.assertEqual(digest,loader.sha(path.read_bytes()))
            self.assertTrue(all(len(page.encode('utf-8'))<=loader.PAGE_BYTES for page in pages))


if __name__=='__main__':unittest.main()
