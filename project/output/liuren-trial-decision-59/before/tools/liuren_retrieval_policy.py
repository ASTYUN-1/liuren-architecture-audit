"""Local experiment policy. No model calls; legacy releases default to retrieval on."""
from pathlib import Path
import json

def case_experience_disabled(root):
    pointer = json.loads((Path(root) / '.opencode/liuren-active.json').read_text('utf-8-sig'))
    return pointer.get('experiment', {}).get('disableCaseExperience') is True

def require_case_experience(root):
    if case_experience_disabled(root):
        raise ValueError('LIUREN_EXPERIMENT_NO_RETRIEVAL: 当前对照版不调用案例库、经验库或旧检索缓存；保留方法、书籍与本盘复核。')
