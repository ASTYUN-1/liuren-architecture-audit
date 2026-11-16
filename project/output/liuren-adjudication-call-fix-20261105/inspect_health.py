"""Persist bounded health results without dumping the knowledge issue records."""
from pathlib import Path
import json, subprocess, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
r=subprocess.run([sys.executable,'-B','-X','utf8','tools/liuren-workflow.py','doctor'],cwd=ROOT,capture_output=True,encoding='utf-8',timeout=90)
d=json.loads(r.stdout); c=d.get('checks',{})
result={'doctor_ok':d['ok'],'errors':d.get('errors',[]),'runtime':c.get('runtime'),'program_chart':c.get('program_chart'),'knowledge_issue_count':len(c.get('research_issues',[])),'note':'knowledge files not modified by this release; doctor is not all green'}
(HERE/'health-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
