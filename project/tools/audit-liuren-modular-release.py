"""Read-only integration audit of the activated paged method release, without inference."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


loader = load('method_loader_audit', ROOT / 'tools/load-liuren-methods.py')
procedures = load('procedure_loader_audit', ROOT / 'tools/load-liuren-procedure.py')
package, manifest = loader.active()
out = ROOT / 'output/六壬技能结构重整-20261023' / manifest['release']
route = loader.plan(manifest, ['illness'], True, nianming=True)
page_receipts = []
for key in route:
    path, expected, hash_ = loader.content(package, manifest, key)
    parts = []
    for number in range(1, len(loader.page_text(expected)) + 1):
        proc = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'tools/load-liuren-methods.py'),
                               'read', key, '--page', str(number)], cwd=ROOT,
                              capture_output=True, timeout=15)
        if proc.returncode:
            raise ValueError(proc.stderr)
        meta, text = loader.parse_page_output(proc.stdout)
        if meta['fileSha256'] != hash_ or meta['page'] != number:
            raise ValueError('page receipt mismatch: ' + key)
        parts.append(text)
        page_receipts.append(meta)
    if ''.join(parts) != expected:
        raise ValueError('paged reads lost/duplicated content: ' + key)

procedure_receipts = []
for name in procedures.NAMES:
    path, expected, hash_ = procedures.procedure(package, manifest, name)
    recovered = []
    for part in procedures.sections(expected):
        texts = []
        for number in range(1, len(loader.page_text(part['text'])) + 1):
            proc = subprocess.run([sys.executable, str(ROOT / 'tools/load-liuren-procedure.py'),
                                   'read', name, '--part', part['id'], '--page', str(number)],
                                  cwd=ROOT, capture_output=True, timeout=15)
            if proc.returncode:
                raise ValueError(proc.stderr)
            meta, text = loader.parse_page_output(proc.stdout, procedure=True)
            if (meta['sourceSha256'] != hash_ or meta['procedure'] != name
                    or meta['part'] != part['id'] or meta['page'] != number):
                raise ValueError('procedure page identity mismatch')
            texts.append(text)
            procedure_receipts.append(meta)
        if ''.join(texts) != part['text']:
            raise ValueError('procedure section roundtrip differs: ' + name + ' ' + part['id'])
        recovered.extend(texts)
    if ''.join(recovered) != expected:
        raise ValueError('procedure roundtrip differs: ' + name)

focus = (package / 'references/shensha-focus.md').read_text('utf-8')
numbers = re.findall(r'^\| S(\d\d)\b', focus, re.M)
if numbers != [str(n).zfill(2) for n in range(1, 33)]:
    raise ValueError('32-item checklist incomplete')
basha = (package / 'references/bashajiubao.md').read_text('utf-8')
for heading, expected in [('九宝逐项核查', 9), ('八煞逐项核查', 8)]:
    section = basha.split('## ' + heading + '\n', 1)[1].split('\n## ', 1)[0]
    rows = [line for line in section.splitlines() if re.match(r'^\| [\u4e00-\u9fff]+ \|', line)]
    if len(rows) - 1 != expected:  # table header is also Chinese
        raise ValueError('treasure/sha checklist incomplete')

old = ROOT / 'runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime'
old_entry = ROOT / 'output/六壬技能结构重整-20261023/20261023-modular-02/backup/skills/daliuren/SKILL.md'
new_entry = ROOT / '.opencode/skills/liuren/daliuren/SKILL.md'
old_common = [old / x for x in ['core.md', 'evidence.md', 'mechanisms/shensha.md']]
old_full = old_common + [old / x for x in ['mechanisms/state-and-rescue.md', 'mechanisms/movement-and-yinshen.md',
                                          'domains/illness.md', 'mechanisms/timing.md']]
new_common = [package / manifest['modules'][k]['file'] for k in manifest['required']]
new_full = [package / manifest['modules'][k]['file'] for k in route]


def totals(paths):
    return dict(files=len(paths), bytes=sum(p.stat().st_size for p in paths),
                characters=sum(len(p.read_text('utf-8-sig')) for p in paths))


result = dict(release=manifest['release'], inferenceRun=False, checks=dict(
    pagedModules=len(route), pages=len(page_receipts), fullTextRoundTrip=True, rawWireBytesVerified=True,
    procedurePages=len(procedure_receipts), procedureRoundTrips=3, focusItems=32, treasures=9, sha=8),
    profile=dict(oldEntry=totals([old_entry]), newEntry=totals([new_entry]),
                 oldInitialRequired=totals(old_common), newRequired=totals(new_common),
                 oldIllnessWithTiming=totals(old_full), newIllnessWithTimingAndNianming=totals(new_full)),
    profileScope='Static declared files only. Does not include charts, candidate retrieval, conditional lookups or repeated old nested reads. Not token billing or model accuracy.',
    pageReceipts=page_receipts, procedurePageReceipts=procedure_receipts)
(out / 'integration-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k not in ('pageReceipts', 'procedurePageReceipts')}, ensure_ascii=False, indent=2))
