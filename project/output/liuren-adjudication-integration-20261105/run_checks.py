"""Capture bounded existing tests/health checks without changing production files."""
from pathlib import Path
import importlib.util
import io
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
modules = ['test_liuren_method_loader','test_liuren_material_scope','test_liuren_local_read',
           'test_liuren_single_method','test_liuren_plan_transport']
stream = io.StringIO()
suite = unittest.defaultTestLoader.loadTestsFromNames(['tools.tests.'+x for x in modules])
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
(HERE/'existing-tests.txt').write_text(stream.getvalue(),'utf-8')
failed_ids = [case.id() for case, _ in result.failures + result.errors]
# Test unchanged loader code against the old method package in memory. The live
# active pointer is never touched. The scope/local-read failures occur in their
# unchanged synthetic fixtures/mocks rather than either real runtime package.
import tools.tests.test_liuren_method_loader as method_tests
pointer = json.loads((ROOT/'.opencode/liuren-active.json').read_text('utf-8'))
old_runtime = ROOT/'runtime/liuren'/pointer['previousRelease']
old_manifest = json.loads((old_runtime/'manifest.json').read_text('utf-8'))
old_manifest['readingRoute'] = json.loads((old_runtime/'reading-route.json').read_text('utf-8'))
baseline_stream = io.StringIO()
baseline_suite = unittest.defaultTestLoader.loadTestsFromNames(failed_ids)
with patch.object(method_tests.loader, 'active', return_value=(old_runtime, old_manifest)):
    baseline = unittest.TextTestRunner(stream=baseline_stream, verbosity=2).run(baseline_suite)
(HERE/'baseline-failing-tests.txt').write_text(baseline_stream.getvalue(),'utf-8')
baseline_ids = [case.id() for case, _ in baseline.failures + baseline.errors]
assert set(baseline_ids) == set(failed_ids), 'some current failures did not reproduce in baseline view'
proc = subprocess.run([sys.executable,'-B','-X','utf8','tools/liuren-workflow.py','doctor'],
                      cwd=ROOT,capture_output=True,timeout=45)
assert proc.returncode == 0, 'doctor failed'
doctor = json.loads(proc.stdout.decode('utf-8'))
assert doctor['ok']
(HERE/'doctor.json').write_text(json.dumps(doctor,ensure_ascii=False,indent=2)+'\n','utf-8')
procedures=[]
for name in ('liuren-cases','liuren-extract'):
    proc=subprocess.run([sys.executable,'-B','-X','utf8','tools/load-liuren-procedure.py','plan',name],
                        cwd=ROOT,capture_output=True,timeout=15)
    assert proc.returncode == 0
    value=json.loads(proc.stdout.decode('utf-8'))
    assert value['release'] == pointer['release'] and len(value['parts']) > 1
    procedures.append(dict(name=name,parts=len(value['parts']),sha256=value['sha256']))
report=dict(testsRun=result.testsRun,passed=result.testsRun-len(failed_ids),failures=len(result.failures),
            errors=len(result.errors),baselineFailuresReproduced=baseline.testsRun,
            baselineMethodView=pointer['previousRelease'],livePointerUntouchedDuringBaseline=True,
            failedTests=failed_ids,doctorOk=True,procedures=procedures,modelCalls=0,
            limitation='Existing suite is not all green; baseline fixtures/11-stage expectation are stale. Full native probes are separate.')
(HERE/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(report,ensure_ascii=False))
