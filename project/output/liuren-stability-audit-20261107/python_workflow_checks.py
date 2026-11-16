"""Run current workflow checks; historical retrieval/candidate tests are separate."""
from pathlib import Path
import json,sys,unittest
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'tools/tests'))
modules=['test_liuren_method_loader','test_liuren_class_mapping','test_liuren_single_method','test_liuren_plan_transport','test_liuren_material_scope','test_liuren_book_search']
names=modules+['test_liuren_local_read.LocalReadTests.test_batches_reconstruct_every_selected_module_without_abridgement','test_liuren_local_read.LocalReadTests.test_condition_routes_remain_intact_and_invalid_conditions_are_rejected']
suite=unittest.defaultTestLoader.loadTestsFromNames(names)
with (OUT/'python-workflow.log').open('w',encoding='utf-8') as log:
 result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
summary={'testsRun':result.testsRun,'failed':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'passed':result.wasSuccessful(),'scope':names,'externalModelCalls':0,'exclusions':'Historical two-library retrieval tests and the 20261027-only publication verifier are not current normal-flow checks; prior full-suite findings remain in activation evidence.'}
(OUT/'python-workflow.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False));raise SystemExit(0 if result.wasSuccessful() else 1)
