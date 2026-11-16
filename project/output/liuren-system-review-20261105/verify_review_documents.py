"""Verify the proposal edits and the read-only scope; no runtime tests or writes."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
from urllib.parse import unquote

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence = json.loads((OUT / '方案审查核验.json').read_text(encoding='utf-8'))
    plan = OUT / '大六壬Skill体系整体梳理与重构完整方案.md'
    backup = OUT / '大六壬Skill体系整体梳理与重构完整方案-1.1留档.md'
    report = OUT / '方案审查报告-20261105.md'
    target = OUT / '方案1.2文档验收.json'
    contents = {p: p.read_text(encoding='utf-8-sig') for p in (plan, backup, report)}
    baseline_ids = [m['id'] for m in evidence['effective_modules']]
    ids = re.findall(r'^\| \d+ \| ([a-z0-9-]+) \|', contents[plan], flags=re.M)
    prior_ids = re.findall(r'^\| \d+ \| ([a-z0-9-]+) \|', contents[backup], flags=re.M)
    protected = evidence['protected_file_hashes_before_document_edit']
    changed = [name for name, expected in protected.items()
               if not (ROOT / name).is_file() or sha(ROOT / name) != expected]
    # Old maintenance void is not part of the active revision tree; verify it separately.
    for item in evidence['known_void_error']:
        if item['exists'] and sha(ROOT / item['path']) != item['sha256']:
            changed.append(item['path'])
    links, fence_errors = [], []
    for path in (plan, report):
        fence = None
        for n, line in enumerate(contents[path].splitlines(), 1):
            marker = re.match(r'^\s*(`{3,}|~{3,})', line)
            if marker:
                token = marker[1][0]
                fence = None if token == fence else token
                continue
            if fence:
                continue
            for match in re.finditer(r'\]\((?:<([^>]+)>|([^\s)]+))\)', line):
                destination = match[1] or match[2]
                if destination.startswith('#') or re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', destination):
                    continue
                resolved = (path.parent / unquote(destination.split('#', 1)[0])).resolve()
                links.append(dict(file=path.name, line=n, target=destination,
                                  exists=resolved.exists() or resolved == target.resolve()))
        if fence:
            fence_errors.append(path.name)
    checks = dict(version_1_2='版本：方案1.2' in contents[plan],
                  backup_version_1_1='版本：方案1.1' in contents[backup],
                  backup_original_length=backup.stat().st_size == 49859,
                  module_count_59=len(ids) == 59,
                  module_ids_unique=len(set(ids)) == 59,
                  matches_current_manifest=set(ids) == set(baseline_ids),
                  module_order_preserved=ids == prior_ids,
                  report_findings_12=len(re.findall(r'^### F\d{2} ', contents[report], re.M)) == 12,
                  no_broken_links=all(x['exists'] for x in links),
                  balanced_fences=not fence_errors,
                  protected_files_unchanged=not changed)
    result = dict(checked_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
                  scope='仅文档结构/引用与指定受保护文件检查，不证明专业规则正确或预测有效',
                  checks=checks, passed=all(checks.values()), module_count=len(ids),
                  local_link_occurrences=len(links), broken_links=[x for x in links if not x['exists']],
                  protected_file_count=len(protected), changed_protected_files=changed,
                  additional_known_void_copies_unchanged=not any(x['path'] in changed for x in evidence['known_void_error']),
                  documents=[dict(file=p.name, bytes=p.stat().st_size, sha256=sha(p)) for p in (plan, backup, report)],
                  runtime_tests_run=False, real_opencode_session_tested=False, independent_prediction_validation_added=0)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert target.is_file()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
