"""Session-bound local evidence workflow. No model calls or semantic proof."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

import case_retrieval as cases
import experience_retrieval as experience

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('workflow_method_loader', Path(__file__).with_name('load-liuren-methods.py'))
methods = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(methods)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def safe(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('missing or external source: ' + str(relative))
    return path


def program_chart(request, root=ROOT, resolved=False):
    """Run the existing pinned engine without writing an archive or calling a model."""
    module, function = ('liuren-resolved-chart.mjs', 'runResolvedChart') if resolved else ('liuren-direct.mjs', 'runChart')
    script = ("import fs from 'node:fs'; import {"+function+"} from './tools/"+module+"'; const x=await "+function+
              "(JSON.parse(fs.readFileSync(0,'utf8')),{persist:false});process.stdout.write(JSON.stringify(x));")
    executable = shutil.which('node')
    if not executable:
        raise ValueError('Node.js is required for the pinned local chart engine')
    proc = subprocess.run([executable, '--input-type=module', '-e', script], cwd=root,
        input=json.dumps(request, ensure_ascii=False), encoding='utf-8', capture_output=True, check=True)
    result = json.loads(proc.stdout)
    if not result.get('ok') or not result.get('validation', {}).get('ok'):
        raise ValueError('program chart validation failed')
    return result


def questions(data):
    items = data.get('questions')
    if not isinstance(items, list) or not items:
        raise ValueError('questions must explicitly register every subquestion')
    seen = set()
    for q in items:
        if not isinstance(q, dict) or not re.fullmatch(r'Q[1-9][0-9]*', q.get('id', '')) or q['id'] in seen:
            raise ValueError('unique Q1.. IDs required')
        seen.add(q['id'])
        for key in ('question', 'target', 'stage', 'success_criterion'):
            if not isinstance(q.get(key), str) or not q[key].strip():
                raise ValueError('question missing ' + key)
        if not isinstance(q.get('requires'), list) or not set(q['requires']) <= {'conclusion', 'timing', 'quantity'} or 'conclusion' not in q['requires']:
            raise ValueError('requires must include conclusion and optional timing/quantity')
        # Public literal prompts cannot silently drop a requested time/amount.
        if re.search(r'何时|什么时候|多久|应期|几天|几月', q['question']) and 'timing' not in q['requires']:
            raise ValueError('explicit timing question omitted')
        if re.search(r'多少|金额|数额|几成|几元', q['question']) and 'quantity' not in q['requires']:
            raise ValueError('explicit quantity question omitted')
    return copy.deepcopy(items)


def doctor(root=ROOT):
    """Read-only local health check. No services, queues, paid models or business writes."""
    errors, checks, pointer = [], {}, {}
    try:
        runtime, manifest = methods.active(root)
        for relative, expected in manifest['files'].items():
            if file_hash(safe(runtime, relative)) != expected:
                errors.append('runtime hash: ' + relative)
        for key in manifest['modules']:
            methods.content(runtime, manifest, key)
        pointer = load(root / '.opencode/liuren-active.json')
        if manifest.get('shenshaPolicyFile'):
            policy = load(safe(runtime, manifest['shenshaPolicyFile']))
            if policy.get('schema') != 'liuren-shensha-policy-v1' or policy.get('release') != pointer['release']:
                raise ValueError('神煞表版本不一致：活动='+pointer['release']+'，采用表='+str(policy.get('release')))
            checks['shensha_policy'] = dict(release=policy['release'], rules=len(policy['rules']))
        for relative, expected in pointer['files'].items():
            if file_hash(safe(root / '.opencode/skills', relative)) != expected:
                errors.append('live skill hash: ' + relative)
        checks['runtime'] = dict(release=manifest['release'], method_version=manifest['version'],
                                files=len(manifest['files']), modules=len(manifest['modules']), groups=pointer['groups'])
    except (ValueError, OSError, KeyError) as error: errors.append(str(error))
    roots = ['案例项目库','经验日志','书籍库','books','knowledge','资料来源/qq-homework-20261018','materials/vendor/liuren-chart-legacy-20261102']
    checks['data_roots'] = {name:(root/name).is_dir() for name in roots}
    errors += ['missing local root: '+name for name,present in checks['data_roots'].items() if not present]
    try:
        vendor = root/'materials/vendor/liuren-chart-legacy-20261102'
        pinned = load(vendor/'adapters/legacy-engine-manifest.json')
        for row in pinned['files']:
            if file_hash(safe(vendor/'engine/legacy',row['path'])) != row['sha256']: errors.append('vendor engine hash: '+row['path'])
        checks['vendor_engine_files'] = len(pinned['files'])
    except (ValueError, OSError, KeyError) as error: errors.append(str(error))
    checks['system'] = dict(python=sys.version.split()[0], python_executable=sys.executable, node_executable=shutil.which('node'))
    try:
        chart=program_chart(dict(datetime='2026-08-04T14:32',label='doctor'),root,resolved=True)
        checks['program_chart']=dict(ok=chart['validation']['ok'],pillars=chart['facts']['pillars'],heaven_earth=len(chart['facts']['heaven_earth']))
        checks['program_chart']['shensha_release'] = chart.get('shensha_resolution', {}).get('release')
        if checks['program_chart']['shensha_release'] != pointer.get('release'):
            errors.append('resolved chart shensha release mismatch')
        if chart['facts']['pillars'] != ['丙午','乙未','庚戌','癸未'] or len(chart['facts']['heaven_earth']) != 12:
            errors.append('fixed program chart regression')
    except (ValueError, OSError, subprocess.CalledProcessError) as error: errors.append(str(error))
    try:
        from liuren_research_overlay import load as research_load
        research = research_load(root)
        checks['research'] = research['summary']
        checks['research_issues'] = research['issues']
        if not research['summary'].get('mechanical_valid'): errors.append('research mechanical validation has gaps')
    except (ValueError, OSError, KeyError) as error: errors.append(str(error))
    return dict(schema='liuren-workflow-doctor-v1',ok=not errors,checks=checks,errors=errors,
        model_calls=0,services_started=0,semantic_correctness='unverified',predictive_accuracy='unverified')


def source_receipts(record, root):
    refs = [(record['source'], record.get('source_sha256'))]
    refs += [(ref['path'], ref.get('sha256')) for axis in ('evidence_refs', 'source_case_refs', 'source_refs') for ref in record.get(axis, [])]
    if record.get('research_card_path'):
        refs.append((record['research_card_path'], None))
    for key in ('method_review', 'method_dimensions'):
        if key in record:
            refs.append((record[key]['path'], record[key]['sha256']))
    out = {}
    for relative, expected in refs:
        path = safe(root, relative)
        value = file_hash(path)
        if expected and value != expected:
            raise ValueError('stale source: ' + relative)
        out[relative] = value
    return out


def candidate_records(ci, ei, query, facts, exclusions, experience_query=None, preferred_categories=()):
    fields = cases.public_fields(facts)
    if len(preferred_categories) == 1:
        fields['占类'] = preferred_categories[0]
    cr = cases.retrieve(ci, query, fields, 100000, exclusions)
    er = experience.retrieve(ei, experience_query if experience_query is not None else query, limit=100000,
                             exclude=exclusions, preferred_categories=preferred_categories)
    records = {}
    for row in cr['results']:
        for unit in [row['unit'], *row.get('also_matched_units', [])]:
            records[unit['id']] = dict(kind='case', record=row['case'], unit=unit, origin_keys=row['origin_keys'])
        records[row['case']['id']] = dict(kind='case', record=row['case'], unit=row['unit'], origin_keys=row['origin_keys'])
    for row in er['results']:
        for entry in [row['entry']]:
            records[entry['id']] = dict(kind='experience', record=entry, origin_keys=row['origin_keys'])
        for entry_id in row.get('also_matched_ids', []):
            entry = next(e for e in ei['entries'] if e['id'] == entry_id)
            records[entry_id] = dict(kind='experience', record=entry, origin_keys=row['origin_keys'])
    return cr, er, records


def prepare(data, run, root=ROOT):
    run = Path(run)
    if run.exists():
        raise ValueError('run directory must be new')
    qs = questions(data)
    if not isinstance(data.get('chart'), dict):
        raise ValueError('chart request required; supplied facts never substitute for program calculation')
    chart = program_chart(data['chart'], root)
    if 'facts' in data and data['facts'] != chart['facts']:
        raise ValueError('supplied facts differ from program facts')
    runtime, manifest = methods.active(root)
    extras = list(data.get('modules', []))
    if any('quantity' in q['requires'] for q in qs):
        extras.append('quantity')
    plan = methods.plan_steps(manifest, data.get('domains', []), any('timing' in q['requires'] for q in qs), extras,
                              bool(data['chart'].get('participants') or data['chart'].get('declared_life')))
    module_rows = []
    for step in plan:
        path, body, sha = methods.content(runtime, manifest, step['id'])
        module_rows.append(dict(**step, path=path.relative_to(root).as_posix(), sha256=sha,
                                pages=len(methods.page_text(body))))
    ci, ei = cases.ensure_index(root), experience.ensure_index(root)
    source_id = data.get('source_id', '')
    exclusions = list(data.get('exclude_sources', [])) + ([source_id] if source_id else []) + cases.known_exclusions(ci, source_id)
    public = dict(question='；'.join(q['question'] for q in qs), facts=chart['facts'], domains=data.get('domains', []))
    preferred = list(dict.fromkeys(experience.DOMAIN_CATEGORIES[d] for d in public['domains']
                                  if d in experience.DOMAIN_CATEGORIES))
    query = public['question'] + ' ' + ' '.join(chart['facts'].get('chart_types', []))
    ep = experience.evidence_packet(public, source_id, root, exclude_sources=exclusions, index=ei,
        extra_query=' '.join(q['question'] for q in qs) + ' ' + data.get('query', ''),
        preferred_categories=preferred, budget=None)
    cr, er, records = candidate_records(ci, ei, query, chart['facts'], exclusions, ep['query'], preferred)
    for item in records.values():
        item['sources'] = source_receipts(item['record'], root)
        item['record_sha256'] = digest(item['record'])
    # Local shortlists keep each selected row. Paging the source is separate from
    # shrinking the candidate set to a website-oriented character budget.
    shortlist = copy.deepcopy(cr)
    shortlist['results'] = shortlist['results'][:6]
    cp = cases.compact(shortlist, budget=None)
    # Same engine-retrieval API as legacy compatibility packet; full manifest retains omitted IDs.
    # Use one query for manifest and packet, so every packet ID has an eligible full record.
    ep['results'] = [row for row in ep['results'] if row['entry']['id'] in records]
    ep['coverage']['returned_ids'] = [row['entry']['id'] for row in ep['results']]
    ep['coverage']['omitted_ids'] = [key for key, item in records.items() if item['kind'] == 'experience' and key not in ep['coverage']['returned_ids']]
    ep['coverage']['complete'] = not ep['coverage']['omitted_ids']
    engine_paths = ['tools/liuren-direct.mjs', 'tools/liuren-direct/chart.mjs', 'tools/liuren-direct/legacy-engine-worker.mjs',
                    'tools/liuren-direct/legacy-engine-manifest.json']
    engine_paths += ['排盘工具魔改/' + row['path'] for row in load(root / engine_paths[-1])['files']]
    session = dict(schema='liuren-workflow-session-v1', session_id=str(uuid.uuid4()), created_at=datetime.now(timezone.utc).isoformat(),
        stage='initial', source_id=source_id, exclude_sources=exclusions, questions=qs, facts=chart['facts'],
        facts_sha256=digest(chart['facts']), chart_request=data['chart'], program_receipt={k: chart[k] for k in ('input', 'validation', 'provenance', 'conventions')},
        engine_sources={path: file_hash(safe(root, path)) for path in engine_paths},
        workflow_sources={path: file_hash(safe(root, path)) for path in ('tools/liuren-workflow.py','tools/liuren_workflow.py',
            'tools/experience_retrieval.py','tools/case_retrieval.py','tools/liuren_research_overlay.py',
            'tools/liuren_knowledge_workbench.py','tools/liuren_book_cases.py','tools/liuren_book_reconstruction_verify.mjs',
            'tools/liuren_book_reconstruction.mjs','tools/load-liuren-methods.py','tools/load-liuren-procedure.py') if (root/path).is_file()},
        release=manifest['release'], method_version=manifest['version'], modules=module_rows,
        candidates=records, coverage=dict(candidate_ids=sorted(records), case=cp['coverage'], experience=ep['coverage']),
        limitations=['结构与原值核对可执行；条件与盘面之间的术理联系仍由研判者与人工审读负责。', '未知转引同案可能未被身份映射识别。'])
    session['session_sha256'] = digest(session)
    run.mkdir(parents=True)
    experience.atomic_json(run / 'session.json', session)
    experience.atomic_json(run / 'coverage.json', session['coverage'])
    coverage_locator = dict(path='coverage.json', sha256=digest(session['coverage']),
        candidate_count=len(records), complete=False, note='Full IDs and omitted-candidate coverage are in the local manifest; ranking is not applicability.')
    context = {key: session[key] for key in ('schema', 'session_id', 'session_sha256',
        'stage', 'facts', 'facts_sha256', 'questions', 'release', 'method_version', 'modules', 'limitations')}
    context['coverage'] = coverage_locator
    experience.atomic_json(run / 'context.json', context)
    # Do not repeatedly transport every candidate ID; the complete local manifest remains verifiable.
    cp['coverage'] = dict(coverage_locator, returned_ids=[row['unit']['id'] for row in cp['results']],
        omitted_count=max(0,len(cr['results'])-len(cp['results'])))
    ep['coverage'] = dict(coverage_locator, returned_ids=[row['entry']['id'] for row in ep['results']],
        omitted_count=sum(item['kind']=='experience' for item in records.values())-len(ep['results']))
    experience.atomic_json(run / 'evidence-packet.json', dict(session_id=session['session_id'], facts_sha256=session['facts_sha256'], cases=cp, experience=ep))
    experience.atomic_json(run / 'reads.json', dict(session_sha256=session['session_sha256'], records={}, modules={}))
    return dict(session_id=session['session_id'], session_sha256=session['session_sha256'], facts_sha256=session['facts_sha256'],
                run=str(run.resolve()), stage='initial', modules=module_rows, candidates=len(records), coverage=coverage_locator)


def session_load(run, root=ROOT):
    session = load(Path(run) / 'session.json')
    given = session.pop('session_sha256')
    if digest(session) != given or digest(session['facts']) != session['facts_sha256']:
        raise ValueError('session/facts integrity mismatch')
    session['session_sha256'] = given
    runtime, manifest = methods.active(root)
    if manifest['release'] != session['release'] or manifest['version'] != session['method_version']:
        raise ValueError('active method changed; prepare a new session')
    for path, expected in session['engine_sources'].items():
        if file_hash(safe(root, path)) != expected:
            raise ValueError('program engine changed')
    for path, expected in session.get('workflow_sources', {}).items():
        if file_hash(safe(root, path)) != expected: raise ValueError('workflow implementation changed; prepare a new session')
    return session, runtime, manifest


def current_candidate(session, key, root):
    if key not in session['candidates']:
        raise ValueError('ID outside session candidates (same-case, reserved, suspended or unmatched)')
    item = session['candidates'][key]
    for relative, expected in item['sources'].items():
        if file_hash(safe(root, relative)) != expected:
            raise ValueError('source changed since prepare: ' + relative)
    # Fresh overlay validation also covers dependency/replacement eligibility.
    if item['kind'] == 'experience':
        fresh = experience.ensure_index(root)
        matches = [row for row in fresh['entries'] if row['id'] == key]
        if not matches or digest(matches[0]) != item['record_sha256']:
            raise ValueError('rule or dependency eligibility changed')
        if matches[0].get('research_status', matches[0].get('status')) == 'suspended':
            raise ValueError('suspended material cannot be adopted')
    else:
        fresh = cases.ensure_index(root)
        matches = [row for row in fresh['cases'] if row['id'] == item['record']['id']]
        if not matches or digest(matches[0]) != item['record_sha256']:
            raise ValueError('case provenance/review eligibility changed')
    return item


def read(run, key, root=ROOT, page=None, review=False, part='record'):
    session, runtime, manifest = session_load(run, root)
    receipts = load(Path(run) / 'reads.json')
    if receipts.get('session_sha256') != session['session_sha256']:
        raise ValueError('read state bound to another session')
    if review:
        eligible = experience.retrieve(experience.ensure_index(root), limit=100000,
            exclude=session['exclude_sources'], include_suspended=True)
        entry = next((row['entry'] for row in eligible['results'] if row['entry']['id'] == key), None)
        if not entry or entry.get('research_status', entry.get('status')) != 'suspended':
            raise ValueError('review view only accepts identity-eligible suspended record')
        body = json.dumps(experience.reference_locators({k:v for k,v in entry.items() if k != 'research_record'}), ensure_ascii=False, indent=2)
        chunks = methods.page_text(body)
        n = page or 1
        if not 1 <= n <= len(chunks): raise ValueError('invalid review page')
        return dict(session_id=session['session_id'], stage=session['stage'], review_only=True,
                    adoption_allowed=False, page=n, pages=len(chunks), content=chunks[n-1],
                    sources=source_receipts(entry, root))
    if key.startswith('module:'):
        name = key.split(':', 1)[1]
        expected = next((x for x in session['modules'] if x['id'] == name), None)
        if not expected:
            raise ValueError('module outside registered plan')
        path, body, sha = methods.content(runtime, manifest, name)
        chunks = methods.page_text(body)
        if page is None or not 1 <= page <= len(chunks) or sha != expected['sha256']:
            raise ValueError('module page/hash invalid')
        completed = set(receipts['modules'].get(name, []))
        completed.add(page)
        receipts['modules'][name] = sorted(completed)
        result = dict(id=key, page=page, pages=len(chunks), sha256=sha, content=chunks[page - 1])
    else:
        item = current_candidate(session, key, root)
        record = item['record']
        available = ['record', 'source'] + ['evidence:' + str(n) for n in range(len(record.get('evidence_refs', [])))]
        available += ['source_case:' + str(n) for n in range(len(record.get('source_case_refs', [])))]
        if part not in available: raise ValueError('unknown record part; available: ' + ','.join(available))
        if part == 'record':
            projected = copy.deepcopy(item)
            projected['record'].pop('research_record', None)
            body = json.dumps(experience.reference_locators(projected), ensure_ascii=False, indent=2)
        elif part == 'source':
            # Never expose a whole multi-case book to a blind session.
            body = safe(root, record['source']).read_text('utf-8-sig') if item['kind'] == 'case' else record['source_excerpt']
        else:
            axis, number = part.split(':')
            ref = record['evidence_refs' if axis == 'evidence' else 'source_case_refs'][int(number)]
            body = ref.get('quote')
            if body is None:
                lines = safe(root, ref['path']).read_text('utf-8-sig').splitlines()
                body = '\n'.join(lines[ref['line_start']-1:ref['line_end']])
        chunks = methods.page_text(body)
        n = page or 1
        if not 1 <= n <= len(chunks): raise ValueError('invalid record page')
        state = receipts['records'].setdefault(key, dict(identity=digest(item), parts={}))
        completed = set(state['parts'].get(part, []))
        completed.add(n)
        state['parts'][part] = sorted(completed)
        state.setdefault('part_pages', {})[part] = len(chunks)
        result = dict(id=key, part=part, page=n, pages=len(chunks), sha256=digest(body),
                      available_parts=available, content=chunks[n-1], full_record_complete=state['parts'].get('record') == list(range(1, state.get('part_pages', {}).get('record', 0)+1)))
    experience.atomic_json(Path(run) / 'reads.json', receipts)
    return dict(session_id=session['session_id'], facts_sha256=session['facts_sha256'], stage=session['stage'],
                receipt_semantics='tool_output_only; not proof of display, reading, understanding or use', **result)


def fact_value(facts, path):
    parts = path.removeprefix('facts.').split('.')
    value = facts
    for part in parts:
        value = value[int(part)] if isinstance(value, list) and part.isdecimal() else value[part]
    return value


def check(run, record, root=ROOT):
    session, runtime, manifest = session_load(run, root)
    reads = load(Path(run) / 'reads.json')
    errors, warnings = [], []
    def fail(message): errors.append(message)
    for key in ('session_id', 'session_sha256', 'facts_sha256', 'stage'):
        if record.get(key) != session[key]: fail('binding mismatch: ' + key)
    if reads.get('session_sha256') != session['session_sha256']: fail('invalid read state')
    for module in session['modules']:
        try:
            _, _, current_hash = methods.content(runtime, manifest, module['id'])
            if current_hash != module['sha256']: fail('module changed: ' + module['id'])
        except ValueError as error: fail(str(error))
        if reads.get('modules', {}).get(module['id']) != list(range(1, module['pages'] + 1)):
            fail('unread module pages: ' + module['id'])
    q_records = record.get('questions', [])
    if not isinstance(q_records, list): q_records = []
    if {x.get('id') for x in q_records} != {q['id'] for q in session['questions']} or len(q_records) != len(session['questions']):
        fail('missing/duplicate/unregistered question')
    used = set()
    for q in session['questions']:
        result = next((x for x in q_records if x.get('id') == q['id']), {})
        for kind in q['requires']:
            value = result.get(kind, {})
            if not isinstance(value, dict) or value.get('status') not in {'supported', 'conditional', 'unknown'}:
                fail(q['id'] + ': missing status for ' + kind); continue
            if not isinstance(value.get('statement'), str) or not value['statement'].strip(): fail(q['id'] + ': missing ' + kind + ' statement')
            if value['status'] == 'unknown' and not value.get('missing'): fail(q['id'] + ': unknown requires missing information')
            if value['status'] == 'conditional' and not value.get('unresolved'): fail(q['id'] + ': conditional requires unresolved conditions')
            if kind == 'timing' and value['status'] != 'unknown' and not all(value.get(k) for k in ('window', 'trigger', 'basis')): fail(q['id'] + ': incomplete timing')
            if kind == 'quantity' and value['status'] != 'unknown' and not all(value.get(k) for k in ('range', 'unit', 'basis')): fail(q['id'] + ': incomplete quantity')
        for evidence in result.get('chart_evidence', []):
            try:
                if fact_value(session['facts'], evidence['path']) != evidence['value']: fail(q['id'] + ': fact value mismatch')
            except (KeyError, TypeError, IndexError): fail(q['id'] + ': invalid fact path')
        for adoption in result.get('rules', []):
            key = adoption.get('id')
            used.add(key)
            try: item = current_candidate(session, key, root)
            except (ValueError, KeyError) as error: fail(str(error)); continue
            state = reads.get('records', {}).get(key, {})
            if state.get('identity') != digest(item) or not state.get('part_pages', {}).get('record') or state.get('parts', {}).get('record') != list(range(1, state['part_pages']['record']+1)):
                fail('unread full structured record: ' + key)
            rule = item['record']
            if item['kind'] != 'experience': fail('case is a comparison source, not an automatic rule: ' + key); continue
            decision = adoption.get('decision')
            if decision not in {'adopt', 'conditional', 'reference', 'defer', 'reject'}: fail('invalid decision: ' + key)
            unknown = False
            applicable = 0
            for axis, source_key in [('conditions', 'conditions'), ('exclusions', 'exclusions')]:
                expected = rule.get(source_key, [])
                checks = adoption.get(axis, [])
                if len(checks) != len(expected) or {x.get('index') for x in checks} != set(range(len(expected))):
                    fail('not all ' + axis + ' addressed: ' + key)
                for evaluation in checks:
                    index = evaluation.get('index')
                    if not isinstance(index, int) or not 0 <= index < len(expected) or evaluation.get('text') != expected[index]:
                        fail('original condition text missing/changed: ' + key)
                    role = evaluation.get('role')
                    if role not in {'source_context', 'source_outcome', 'applicability', 'exclusion', 'unknown'}:
                        fail('condition role required: ' + key)
                    if role in {'source_context', 'source_outcome'}:
                        if evaluation.get('status') != 'source_only' or evaluation.get('used_as_current_fact') is not False or evaluation.get('fact_refs'):
                            fail('historical source context/outcome cannot be current evidence: ' + key)
                        if not evaluation.get('transfer_rationale'):
                            fail('historical comparison needs transfer boundary: ' + key)
                        continue
                    if role == 'unknown': unknown = True
                    if role == 'applicability': applicable += 1
                    if axis == 'exclusions' and role not in {'exclusion', 'unknown'}: fail('exclusion role mismatch: ' + key)
                    status = evaluation.get('status')
                    if status not in {'met', 'unmet', 'unknown'}: fail('invalid condition state: ' + key)
                    blocking = status != 'met' if axis == 'conditions' else status != 'unmet'
                    unknown |= blocking
                    if status == 'unknown' and not evaluation.get('missing'): fail('unknown condition missing gap: ' + key)
                    refs = evaluation.get('fact_refs', [])
                    if status != 'unknown' and not refs: fail('condition needs program fact reference: ' + key)
                    if status != 'unknown' and not evaluation.get('transfer_rationale'): fail('condition transfer rationale missing: ' + key)
                    for ref in refs:
                        try:
                            if fact_value(session['facts'], ref['path']) != ref['value']: fail('condition fact mismatch: ' + key)
                        except (KeyError, TypeError, IndexError): fail('invalid condition fact reference: ' + key)
            if decision == 'adopt' and unknown: fail('unmet/unknown condition cannot be adopted: ' + key)
            if decision in {'adopt', 'conditional'}:
                evidence_parts = adoption.get('evidence_parts', [])
                if not evidence_parts: fail('adoption needs explicit evidence parts read: ' + key)
                for evidence_part in evidence_parts:
                    total = state.get('part_pages', {}).get(evidence_part, 0)
                    if evidence_part == 'record' or not total or state.get('parts', {}).get(evidence_part) != list(range(1,total+1)):
                        fail('unread source part: ' + key + ':' + evidence_part)
                application = adoption.get('application', {})
                if not application.get('rationale') or not application.get('fact_refs'):
                    fail('adoption requires explicit current-question application: ' + key)
                for ref in application.get('fact_refs', []):
                    try:
                        if fact_value(session['facts'], ref['path']) != ref['value']: fail('application fact mismatch: ' + key)
                    except (KeyError, TypeError, IndexError): fail('invalid application fact reference: ' + key)
                if rule.get('research_status') == 'source_method' and not applicable:
                    fail('source method without identified transferable condition is reference only: ' + key)
            if decision == 'conditional' and not adoption.get('unresolved'): fail('conditional rule needs unresolved: ' + key)
            counter = adoption.get('strongest_counterexample', {})
            if not isinstance(counter, dict) or counter.get('status') not in {'addressed', 'unknown', 'none_registered'}:
                fail('counterexample must be assessed: ' + key)
            if rule.get('counterexample_case_ids') and counter.get('status') == 'none_registered': fail('registered counterexample omitted: ' + key)
            if decision == 'adopt' and counter.get('status') == 'unknown': fail('unresolved counterexample cannot be adopted: ' + key)
            if counter.get('status') == 'addressed' and (not counter.get('assessment') or not counter.get('source_refs')):
                fail('counterexample assessment/source required: ' + key)
            if counter.get('status') == 'addressed' and not set(counter.get('source_refs', [])) <= set(item['sources']):
                fail('counterexample references outside verified source identity: ' + key)
            if counter.get('status') == 'addressed' and rule.get('counterexample_case_ids') and not set(counter.get('case_ids', [])) & set(rule['counterexample_case_ids']):
                fail('registered counterexample identity not assessed: ' + key)
            if counter.get('status') == 'unknown' and not counter.get('missing'): fail('counterexample uncertainty needs explicit gap: ' + key)
            if any(evaluation.get('status') == 'unknown' for axis in ('conditions', 'exclusions') for evaluation in adoption.get(axis, [])):
                if any(result.get(k, {}).get('status') == 'supported' for k in q['requires']) and decision in {'adopt', 'conditional'}:
                    fail(q['id'] + ': unresolved adopted premise cannot yield unconditional supported judgment')
            if set(adoption.get('source_refs', [])) != set(item['sources']): fail('source identity coverage mismatch: ' + key)
        if any(result.get(k, {}).get('status') == 'supported' for k in q['requires']) and not result.get('chart_evidence'):
            fail(q['id'] + ': supported judgment requires program facts')
    comparisons = record.get('case_comparisons', [])
    if not isinstance(comparisons, list):
        fail('case_comparisons must be a list')
        comparisons = []
    for comparison in comparisons:
        if not isinstance(comparison, dict):
            fail('case comparison must be an object')
            continue
        key = comparison.get('id')
        try:
            item = current_candidate(session, key, root)
        except (ValueError, KeyError) as error:
            fail('case comparison: ' + str(error))
            continue
        if item['kind'] != 'case':
            fail('case comparison is not a case: ' + str(key))
            continue
        if comparison.get('source') != item['record']['source']:
            fail('case comparison source mismatch: ' + str(key))
        # A case-level alias may have been opened through a question-unit ID.
        matching_reads = [state for rid, state in reads.get('records', {}).items()
            if rid in session['candidates']
            and session['candidates'][rid]['kind'] == 'case'
            and session['candidates'][rid]['record']['id'] == item['record']['id']
            and state.get('identity') == digest(session['candidates'][rid])]
        if not any(state.get('part_pages', {}).get('source', 0)
                   and state.get('parts', {}).get('source') == list(range(1, state['part_pages']['source'] + 1))
                   for state in matching_reads):
            fail('case comparison source not fully emitted: ' + str(key))
        if not comparison.get('use') or not comparison.get('transfer_limit'):
            fail('case comparison needs use and transfer_limit: ' + str(key))
    if not used:
        warnings.append('未登记经验条目的处理；本回执不能确认经验调查已完成，不强制采用无关经验。')
    if not comparisons:
        warnings.append('未登记案例比较；本回执不能确认案例调查已完成。')
    warnings.append('读取页码只记录工具输出，不能证明正文实际呈现、阅读、理解或采用。')
    coverage = record.get('coverage', {})
    if sorted(coverage.get('candidate_ids', [])) != session['coverage']['candidate_ids'] and coverage.get('candidate_manifest_sha256') != digest(session['coverage']):
        fail('candidate coverage not acknowledged')
    if not coverage.get('unreviewed_limitations'): fail('unreviewed candidates/semantic limits must remain explicit')
    if record.get('independent_validation_increment', 0) != 0: fail('no independent outcome validation in this workflow')
    result = dict(schema='liuren-workflow-check-v1', session_id=session['session_id'], ok=not errors, errors=errors,
        warnings=warnings, scope='structure, source freshness, identity isolation and exact program fact values',
        semantic_correctness='unverified', predictive_accuracy='unverified', independent_validation_increment=0,
        process_completeness='unverified', output_policy='local-original; no website rewriting or release gate',
        note='非空文字和事实引用不证明术理推导成立；通过只代表本检查器覆盖的程序约束。')
    experience.atomic_json(Path(run) / 'check.json', result)
    return result
