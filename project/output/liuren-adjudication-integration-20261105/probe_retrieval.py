"""Exercise actual dual retrieval, preserving the active method/overlay identity."""
from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'tools'))
spec=importlib.util.spec_from_file_location('actual_read', ROOT/'tools/liuren-local-read.py')
reader=importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
result, text = reader.parallel_search('考试 奖学金 名次', '考试 等级 发用', '考试占', limit=3)
pointer=json.loads((ROOT/'.opencode/liuren-active.json').read_text('utf-8'))
assert result['context']['release'] == pointer['release']
assert result['context']['methodVersion'] == pointer['methodVersion']
overlay=result['context']['overlayFingerprint']
for key in ('cases','experience'):
    assert result[key]['index_status']['research_overlay']['overlayFingerprint'] == overlay
assert text.startswith('LIUREN_CONTEXT ') and '不代表读过原文' in text
report=dict(ok=True,context=result['context'],caseCandidates=len(result['cases'].get('results',[])),
            experienceCandidates=len(result['experience'].get('results',[])),timing=result['timing'],
            validates='transport identity only; candidates not adopted as professional evidence', modelCalls=0)
(HERE/'retrieval.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
proc=subprocess.run([shutil.which('node'),'--test','tools/tests/liuren-materials-transport.test.mjs'],
                    cwd=ROOT,capture_output=True,timeout=45)
(HERE/'node-tests.txt').write_bytes(proc.stdout+proc.stderr)
assert proc.returncode == 0, 'native materials tests failed; see node-tests.txt'
report['nativeMaterialsTestExitCode']=proc.returncode
(HERE/'retrieval.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(report,ensure_ascii=False))
