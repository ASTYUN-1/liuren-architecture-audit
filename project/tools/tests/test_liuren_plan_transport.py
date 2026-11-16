"""Real UTF-8 output, complete pages and caller-carried context identity, no model claims."""
from contextlib import redirect_stdout
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('plan_transport_reader',ROOT/'tools/liuren-local-read.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)

def cli(*args):
    run=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/liuren-local-read.py'),
                        'methods',*args],cwd=ROOT,capture_output=True,timeout=20)
    if run.returncode:raise AssertionError(run.stderr.decode('utf-8'))
    if b'\r' in run.stdout:raise AssertionError('non-canonical output newlines')
    return run.stdout.decode('utf-8')

def header(text):
    first=text.split('\n',1)[0]
    label,raw=first.split(' ',1)
    return label,json.loads(raw)

def pages(text):
    rows=[]
    for chunk in text.split('LIUREN_TEXT_BEGIN ')[1:]:
        meta,body=chunk.split('\n',1)
        body,end=body.split('\nLIUREN_TEXT_END ',1)
        meta=json.loads(meta)
        if end.split('\n',1)[0]!=meta['pageSha256']:raise AssertionError('end receipt mismatch')
        if reader.loader.sha(body.encode())!=meta['pageSha256']:raise AssertionError('body receipt mismatch')
        rows.append((meta,body))
    return rows

class PlanTransportTests(unittest.TestCase):
    def test_real_full_then_refs_reconstruct_all_selected_text_and_hashes(self):
        initial=cli('--domain','finance','--context-key','test-session-A','--batch','1')
        label,plan=header(initial);self.assertEqual(label,'LIUREN_READING_PLAN')
        token=plan['plan_id'];outputs=[initial]
        for batch in range(2,len(plan['batches'])+1):
            text=cli('--domain','finance','--context-key','test-session-A',
                     '--plan-id',token,'--batch',str(batch))
            self.assertEqual(header(text)[0],'LIUREN_READING_PLAN_REF')
            outputs.append(text)
        rows=[row for text in outputs for row in pages(text)]
        runtime,m=reader.loader.active();keys=reader.loader.plan(m,['finance'])
        self.assertEqual(list(dict.fromkeys(meta['module'] for meta,_ in rows)),keys)
        for key in keys:
            file,expected,digest=reader.loader.content(runtime,m,key)
            selected=[(meta,body) for meta,body in rows if meta['module']==key]
            self.assertEqual(''.join(body for _,body in selected),expected)
            self.assertEqual([meta['page'] for meta,_ in selected],list(range(1,len(selected)+1)))
            self.assertTrue(all(meta['fileSha256']==digest for meta,_ in selected))

    def test_old_calls_full_plan_and_new_session_wrong_token_force_full(self):
        first=cli('--domain','illness','--context-key','A')
        token=header(first)[1]['plan_id']
        for args in [(),('--context-key','B','--plan-id',token),
                     ('--context-key','A','--plan-id','invalid'),('--plan-id',token),
                     ('--context-key','A','--plan-id',token,'--full-plan')]:
            with self.subTest(args=args):
                text=cli('--domain','illness','--batch','2',*args)
                self.assertEqual(header(text)[0],'LIUREN_READING_PLAN')
                self.assertTrue(pages(text))

    def test_missing_batch_is_never_marked_read_and_explicit_reread_is_full_text(self):
        options=('--condition','liqi','--condition','void','--condition','structure')
        first=cli(*options,'--domain','illness','--context-key','A')
        token=header(first)[1]['plan_id']
        skipped=cli(*options,'--domain','illness','--context-key','A','--plan-id',token,'--batch','3')
        self.assertEqual(header(skipped)[1]['selected'],[3])
        self.assertTrue(all('read' not in k for k in header(skipped)[1]))
        later=cli(*options,'--domain','illness','--context-key','A','--plan-id',token,'--batch','2')
        old=cli(*options,'--domain','illness','--batch','2')
        self.assertEqual(pages(later),pages(old))
        self.assertEqual(pages(cli(*options,'--domain','illness','--context-key','A','--plan-id',token,'--batch','2')),pages(old))

    def test_changed_route_version_and_any_page_hash_invalidate_reference(self):
        first=cli('--domain','illness','--context-key','A')
        token=header(first)[1]['plan_id']
        changed=cli('--domain','finance','--context-key','A','--plan-id',token)
        self.assertEqual(header(changed)[0],'LIUREN_READING_PLAN')
        runtime,m=reader.loader.active()
        args=SimpleNamespace(domain=['illness'],timing=False,condition=[],nianming=False,
                             batch=[2],context_key='A',plan_id=token,full_plan=False)
        modified=copy.deepcopy(m);modified['version']='different-release-content'
        out=io.StringIO()
        with patch.object(reader.loader,'active',return_value=(runtime,modified)),redirect_stdout(out):
            reader.print_methods(args)
        self.assertEqual(header(out.getvalue())[0],'LIUREN_READING_PLAN')
        batches=reader.method_batches(runtime,m,['illness'])
        identity=reader.reading_plan(m,batches,'A')[0]
        altered=copy.deepcopy(batches);altered[-1][-1]['pageSha256']='changed-unselected-page'
        self.assertNotEqual(identity,reader.reading_plan(m,altered,'A')[0])
        self.assertNotEqual(identity,reader.reading_plan(m,batches,'B')[0])

    def test_material_bridge_old_request_and_trusted_context_request_match_pages(self):
        def request(data):
            run=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/liuren-materials.py'),
                '--request',json.dumps(data)],cwd=ROOT,capture_output=True,timeout=20)
            self.assertEqual(run.returncode,0,run.stderr)
            return run.stdout.decode('utf-8')
        old=dict(action='methods',domains=['illness'],batch=1)
        self.assertEqual(header(request(old))[0],'LIUREN_READING_PLAN')
        first=request(dict(old,_context_key='trusted-session'))
        following=request(dict(old,_context_key='trusted-session',plan_id=header(first)[1]['plan_id']))
        self.assertEqual(header(following)[0],'LIUREN_READING_PLAN_REF')
        self.assertEqual(pages(first),pages(following))

if __name__=='__main__':unittest.main()
