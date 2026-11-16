"""Prove the active search guard runs before either retrieval/index function."""
from pathlib import Path
import importlib.util
import json
import sys
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
spec=importlib.util.spec_from_file_location('variant_reader',ROOT/'tools/liuren-local-read.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
import case_retrieval as cases
import experience_retrieval as experience
with patch.object(cases,'ensure_index',side_effect=AssertionError('case index opened')) as ci, \
     patch.object(experience,'ensure_index',side_effect=AssertionError('experience index opened')) as ei, \
     patch.object(cases,'retrieve',side_effect=AssertionError('cases searched')) as cr, \
     patch.object(experience,'retrieve',side_effect=AssertionError('experience searched')) as er:
    try:reader.parallel_search('考试','等级','考试占')
    except ValueError as exc:assert 'LIUREN_EXPERIMENT_NO_RETRIEVAL' in str(exc)
    else:raise AssertionError('retrieval unexpectedly ran')
    for mocked in [ci,ei,cr,er]:mocked.assert_not_called()
report=dict(ok=True,caseIndexCalls=0,experienceIndexCalls=0,caseRetrieveCalls=0,experienceRetrieveCalls=0,
            verifies='guard before both indexes and searches',modelCalls=0)
(HERE/'no-search-proof.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(report,ensure_ascii=False))
