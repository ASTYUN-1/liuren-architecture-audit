"""Local full-text reading batches and parallel case/experience search; no judgment gate."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('liuren_read_loader', ROOT / 'tools/load-liuren-methods.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)


def method_batches(runtime, manifest, domains=(), timing=False, conditions=(), nianming=False):
    """Use the existing route and exact page contents, never summaries or an archive scan."""
    if any(key not in manifest['conditional'] for key in conditions):
        raise ValueError('unknown condition')
    items = []
    for step in loader.plan_steps(manifest, domains, timing, conditions, nianming):
        key = step['id']
        file, text, digest = loader.content(runtime, manifest, key)
        pages = loader.page_text(text)
        for number, page in enumerate(pages, 1):
            items.append(dict(module=key, stage=step['stage'], file=str(file), fileSha256=digest,
                              page=number, pages=len(pages), pageSha256=loader.sha(page.encode()), text=page))
    # Three original 7.6KB pages per response bound transmission without
    # deleting any page or changing which professional modules are required.
    return [items[i:i + 3] for i in range(0, len(items), 3)]


def reading_plan(manifest, batches, context_key=None):
    """A caller-carried identity, never global read state or proof of reading."""
    description = dict(release=manifest['release'], version=manifest['version'],
        batches=[dict(batch=n, pages=[dict(module=p['module'], page=p['page'],
            pages=p['pages'], fileSha256=p['fileSha256'], pageSha256=p['pageSha256']) for p in rows])
            for n, rows in enumerate(batches, 1)])
    identity = dict(context=context_key or '', **description)
    plan_id = loader.sha(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode())
    return plan_id, description


def print_method(key, trial=False):
    """Read one named method whole, without constructing a judgment-wide plan."""
    runtime, manifest = loader.active()
    requested_key=key
    if trial:
        trial_config=manifest.get('classSelectionTrial', {})
        key=trial_config.get('domainModules', {}).get(key, key)
    path, body, digest = loader.content(runtime, manifest, key)
    from liuren_research_overlay import fingerprint
    meta = dict(release=manifest['release'], version=manifest['version'],
                overlayFingerprint=fingerprint(ROOT), module=key,
                file=str(path), fileSha256=digest,
                textSha256=loader.sha(body.encode('utf-8')),
                chars=len(body), bytes=len(body.encode('utf-8')),
                requires=manifest['modules'][key].get('requires', []),
                encoding='utf-8', newline='LF', completeModule=True)
    if key != requested_key:
        meta['requestedModule']=requested_key
        meta['scope']='本机分类取用短答专用；完整占断原模块未改'
    # A directly reusable citation: no model conversion of absolute paths or hashes.
    if path.is_relative_to(runtime):
        meta['handoff'] = dict(id='M_'+key, title=manifest['modules'][key].get('title', key),
                               source_path=path.relative_to(ROOT).as_posix(), sha256=digest)
    else:
        meta['handoff_note'] = '本项为本机操作说明，不作为裁决方法原文交接。'
    print('LIUREN_METHOD_BEGIN ' + json.dumps(meta, ensure_ascii=False))
    sys.stdout.write(body)
    print('\nLIUREN_METHOD_END ' + json.dumps(dict(module=key, textSha256=meta['textSha256']),
                                             ensure_ascii=False))


def print_methods(args):
    runtime, manifest = loader.active()
    batches = method_batches(runtime, manifest, args.domain, args.timing, args.condition, args.nianming)
    selected = args.batch or [1]
    if len(set(selected)) != len(selected) or any(not 1 <= n <= len(batches) for n in selected):
        raise ValueError('batch must be unique and within 1..' + str(len(batches)))
    context_key = getattr(args, 'context_key', None)
    plan_id, _ = reading_plan(manifest, batches, context_key)
    full = (getattr(args, 'full_plan', False) or not context_key
            or getattr(args, 'plan_id', None) != plan_id)
    if full:
        print('LIUREN_READING_PLAN ' + json.dumps(dict(plan_id=plan_id,
        release=manifest['release'], version=manifest['version'],
        batches=[dict(batch=n, pages=[f"{p['module']}:{p['page']}/{p['pages']}" for p in rows])
                 for n, rows in enumerate(batches, 1)], conditional=manifest['conditional'],
        note='All listed pages remain required unless actually read in current context. Output is not proof of understanding.'), ensure_ascii=False))
    else:
        print('LIUREN_READING_PLAN_REF ' + json.dumps(dict(plan_id=plan_id, batches=len(batches),
            selected=selected, note='Reuse the matching full plan in this context; no page is marked read.'), ensure_ascii=False))
    for n in selected:
        print('LIUREN_BATCH_BEGIN ' + str(n))
        for row in batches[n - 1]:
            meta = {k: v for k, v in row.items() if k != 'text'}
            print('LIUREN_TEXT_BEGIN ' + json.dumps(meta, ensure_ascii=False))
            sys.stdout.write(row['text'])
            print('\nLIUREN_TEXT_END ' + row['pageSha256'])
        print('LIUREN_BATCH_END ' + str(n))


def parallel_search(case_query, experience_query, category, limit=8, out=None):
    from liuren_retrieval_policy import require_case_experience
    require_case_experience(ROOT)
    import case_retrieval as cases
    import experience_retrieval as experience

    def case_search():
        start = time.perf_counter()
        result = cases.retrieve(cases.ensure_index(), case_query, {'占类': category}, limit)
        return result, time.perf_counter() - start

    def experience_search():
        start = time.perf_counter()
        result = experience.retrieve(experience.ensure_index(), experience_query, [category] if category else [], limit=limit)
        return result, time.perf_counter() - start

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:
        a, b = pool.submit(case_search), pool.submit(experience_search)
        (case_result, case_seconds), (experience_result, experience_seconds) = a.result(), b.result()
    runtime, manifest = loader.active()
    case_policy = case_result['index_status']['research_overlay']['overlayFingerprint']
    experience_policy = experience_result['index_status']['research_overlay']['overlayFingerprint']
    if case_policy != experience_policy:
        raise ValueError('两路检索的规则版本不一致；请重查，不能混用')
    identity = dict(release=manifest['release'], methodVersion=manifest['version'], overlayFingerprint=case_policy)
    result = dict(context=identity, cases=case_result, experience=experience_result,
                  timing=dict(cases_seconds=case_seconds, experience_seconds=experience_seconds,
                              wall_seconds=time.perf_counter() - start))
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # These are the existing search renderers, including source identity,
    # applicability caveats, rule conditions and review notices. No row cap
    # or character budget beyond the caller's explicit search limit is added.
    text = 'LIUREN_CONTEXT ' + json.dumps(identity, ensure_ascii=False) + '\n' + cases.render(case_result) + '\n' + experience.render(experience_result)
    text += '\n以上是候选定位，不代表读过原文或完成采用裁决。请按来源行号阅读相关原档及上下文。\n'
    if out:
        text += '完整机器记录：' + str(out.resolve()) + '\n'
    return result, text


def main():
    loader.configure_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('method', help='Read one module at the current judgment step, without batches')
    p.add_argument('module')
    p = sub.add_parser('methods')
    p.add_argument('--domain', action='append', default=[])
    p.add_argument('--timing', action='store_true')
    p.add_argument('--nianming', action='store_true')
    p.add_argument('--condition', action='append', default=[])
    p.add_argument('--batch', type=int, action='append', default=[])
    p.add_argument('--plan-id', help='Identity from the full plan in the same current context')
    p.add_argument('--context-key', help='Explicit CLI conversation/context identity; absent always returns full plan')
    p.add_argument('--full-plan', action='store_true', help='Return full plan even when identity matches')
    p = sub.add_parser('search')
    p.add_argument('--case-query', required=True)
    p.add_argument('--experience-query', required=True)
    p.add_argument('--category', default='')
    p.add_argument('--limit', type=int, default=8)
    p.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.command == 'method':
        print_method(args.module)
    elif args.command == 'methods':
        print_methods(args)
    else:
        if args.limit < 1:
            parser.error('--limit must be positive')
        _, text = parallel_search(args.case_query, args.experience_query, args.category, args.limit, args.out)
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
