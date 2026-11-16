"""Read the active Liuren methods in bounded UTF-8 pages with verifiable receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGE_BYTES = 7600


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def configure_stdout():
    # The receipt describes exactly these UTF-8 bytes, including LF newlines.
    # Windows TextIOWrapper otherwise expands LF to CRLF after hashing.
    sys.stdout.reconfigure(encoding='utf-8', newline='')


def active(root=ROOT):
    root = Path(root).resolve()
    pointer = json.loads((root / '.opencode/liuren-active.json').read_text('utf-8'))
    runtime = (root / pointer['runtime']).resolve()
    if not runtime.is_relative_to(root.resolve()):
        raise ValueError('runtime escapes project')
    manifest = json.loads((runtime / 'manifest.json').read_text('utf-8'))
    if manifest['release'] != pointer['release'] or manifest['version'] != pointer['methodVersion']:
        raise ValueError('active pointer/version mismatch')
    if sha(json.dumps(manifest['files'], sort_keys=True).encode()) != manifest['version']:
        raise ValueError('manifest identity mismatch')
    if 'routingFile' in manifest:
        route_path = (runtime / manifest['routingFile']).resolve()
        if not route_path.is_relative_to(runtime) or not route_path.is_file():
            raise ValueError('invalid reading route file')
        raw = route_path.read_bytes()
        if sha(raw) != manifest['files'].get(manifest['routingFile']):
            raise ValueError('reading route hash mismatch')
        route = json.loads(raw)
        required = [key for stage in route['stages'] for key in stage['required']]
        conditional = {key: item['trigger'] for key, item in route['conditional'].items()}
        if (manifest['required'] != required or manifest['conditional'] != conditional
                or manifest['domains'] != route['domains']):
            raise ValueError('manifest and reading route disagree')
        manifest['readingRoute'] = route
    # Local operation instructions are versioned separately from the immutable
    # research method package. Only this transport module may be overridden.
    overrides = pointer.get('localModuleOverrides', {})
    for key, item in overrides.items():
        if key != 'daliuren-paipan' or key not in manifest['modules']:
            raise ValueError('unsupported local module override: ' + key)
        path = (root / item['file']).resolve()
        if (not path.is_relative_to(root.resolve()) or not path.is_file()
                or sha(path.read_bytes()) != item['sha256']):
            raise ValueError('local module override hash/path mismatch: ' + key)
    if overrides:
        manifest['_localModuleOverrides'] = {
            key: dict(item, absoluteFile=str((root / item['file']).resolve()))
            for key, item in overrides.items()
        }
    return runtime, manifest


def page_text(text, limit=PAGE_BYTES):
    """Exact Unicode-preserving partition; even one overlong line is bounded."""
    parts, current, size = [], [], 0
    for char in text:
        count = len(char.encode('utf-8'))
        if size + count > limit:
            parts.append(''.join(current))
            current, size = [], 0
        current.append(char)
        size += count
    if current:
        parts.append(''.join(current))
    return parts or ['']


def content(runtime, manifest, key):
    if key not in manifest['modules']:
        raise ValueError('unknown module: ' + key)
    override = manifest.get('_localModuleOverrides', {}).get(key)
    if override:
        path = Path(override['absoluteFile'])
        raw = path.read_bytes()
        if sha(raw) != override['sha256']:
            raise ValueError('local module override hash mismatch: ' + key)
        return path, raw.decode('utf-8').replace('\r\n', '\n'), sha(raw)
    relative = manifest['modules'][key]['file']
    path = (runtime / relative).resolve()
    if not path.is_relative_to(runtime.resolve()) or not path.is_file():
        raise ValueError('invalid module file')
    raw = path.read_bytes()
    if manifest['files'].get(relative) != sha(raw):
        raise ValueError('module hash mismatch: ' + key)
    # File identity hashes raw bytes; readable page content uses LF to avoid
    # Windows stdout turning existing CRLF into CRCRLF and duplicating lines.
    return path, raw.decode('utf-8').replace('\r\n', '\n'), sha(raw)


def plan_steps(manifest, domains=(), timing=False, extras=(), nianming=False):
    ordered, visiting, seen = [], set(), set()
    def add(key, stage):
        if key in seen:
            return
        if key in visiting or key not in manifest['modules']:
            raise ValueError('invalid dependency: ' + key)
        visiting.add(key)
        for dep in manifest['modules'][key]['requires']:
            add(dep, stage)
        visiting.remove(key)
        seen.add(key)
        ordered.append(dict(id=key, stage=stage))
    selected = set(extras)
    if timing:
        selected.add('timing')
    if nianming:
        selected.add('nianming')
    unknown = selected.difference(manifest['modules'])
    if unknown:
        raise ValueError('unknown module: ' + ', '.join(sorted(unknown)))
    for key in domains:
        if key not in manifest.get('domains', domains):
            raise ValueError('unknown domain: ' + key)
    if 'readingRoute' in manifest:
        route = manifest['readingRoute']
        if route.get('schemaVersion', 1) >= 2:
            stage_ids = [stage['id'] for stage in route['stages']]
            if len(stage_ids) != len(set(stage_ids)) or any(
                    item['stage'] not in stage_ids for item in route['conditional'].values()):
                raise ValueError('invalid conditional workflow stage')
            for stage in route['stages']:
                number = stage['id']
                # A conditional belongs to its declared logical stage, even
                # when a frozen route names an anchor in another stage. Empty
                # stages must not silently defer selected modules to delivery.
                conditions = {key: item for key, item in route['conditional'].items()
                              if key in selected and item['stage'] == number}
                for key, condition in conditions.items():
                    if condition.get('beforeRequired') not in stage['required']:
                        add(key, number)
                for required in stage['required']:
                    for key, condition in conditions.items():
                        if condition.get('beforeRequired') == required:
                            add(key, number)
                    if required == route.get('extrasBefore', 'report'):
                        for key in extras:
                            add(key, number)
                    add(required, number)
                    if number == route['domainStage'] and required == route.get('domainAfter'):
                        for key in domains:
                            add(key, number)
            return ordered
        for stage in route['stages']:
            number = stage['id']
            for key, condition in route['conditional'].items():
                if key in selected and condition['stage'] == number:
                    add(key, number)
            if number == 11:
                for key in extras:
                    add(key, number)
            for key in stage['required']:
                add(key, number)
            if number == route['domainStage']:
                for key in domains:
                    add(key, number)
        return ordered
    # Compatibility with earlier releases and small test fixtures.
    if 'nianming' in selected:
        add('nianming', 1)
    for key in manifest['required']:
        if key == 'report':
            for extra in extras:
                add(extra, None)
        add(key, None)
        if key == 'evidence':
            for domain in domains:
                add(domain, None)
        if key == 'adjudication' and timing:
            add('timing', 9)
    return ordered


def plan(manifest, domains=(), timing=False, extras=(), nianming=False):
    return [step['id'] for step in plan_steps(manifest, domains, timing, extras, nianming)]


def parse_page_output(raw, procedure=False):
    """Verify the wire bytes without universal-newline or whitespace conversion."""
    prefix = b'LIUREN_PROCEDURE_' if procedure else b'LIUREN_PAGE_'
    begin, remaining = raw.split(b'\n', 1)
    if not begin.startswith(prefix + b'BEGIN '):
        raise ValueError('missing page begin marker')
    meta = json.loads(begin[len(prefix + b'BEGIN '):])
    body, ending = remaining.rsplit(b'\n' + prefix + b'END ', 1)
    end = json.loads(ending.split(b'\n', 1)[0])
    text = body.decode('utf-8')
    if (b'\r' in raw or meta.get('encoding') != 'utf-8' or meta.get('newline') != 'LF'
            or sha(body) != meta['pageSha256'] or meta['pageSha256'] != end['pageSha256']
            or len(text) != meta['chars'] or len(body) != meta['bytes']):
        raise ValueError('page wire bytes or receipt mismatch')
    identity = ('release', 'procedure', 'part', 'page', 'pages') if procedure else ('module', 'page', 'pages')
    if any(meta[key] != end[key] for key in identity):
        raise ValueError('page begin/end identity mismatch')
    return meta, text


def main():
    configure_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Explicit isolated project root; no active mutation')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('plan')
    p.add_argument('--domain', action='append', default=[])
    p.add_argument('--timing', action='store_true')
    p.add_argument('--nianming', action='store_true', help='Read year/life rules at data preparation')
    p.add_argument('--condition', action='append', default=[], help='Select a triggered conditional module')
    p.add_argument('--extra', action='append', default=[])
    p = sub.add_parser('read')
    p.add_argument('module')
    p.add_argument('--page', type=int, required=True)
    args = parser.parse_args()
    runtime, manifest = active(args.root)
    if args.command == 'plan':
        for key in args.condition:
            if key not in manifest['conditional']:
                raise ValueError('unknown condition: ' + key)
        for key in args.domain:
            if key not in manifest['domains']:
                raise ValueError('unknown domain: ' + key)
        rows = []
        extras = args.extra + args.condition
        for step in plan_steps(manifest, args.domain, args.timing, extras, args.nianming):
            key = step['id']
            path, text, hash_ = content(runtime, manifest, key)
            rows.append(dict(id=key, stage=step['stage'], path=str(path), bytes=path.stat().st_size,
                             pages=len(page_text(text)), sha256=hash_))
        print(json.dumps(dict(release=manifest['release'], version=manifest['version'], modules=rows,
                              localModuleOverrides={key: {k: v for k, v in item.items() if k != 'absoluteFile'}
                                  for key, item in manifest.get('_localModuleOverrides', {}).items()},
                              bytes=sum(row['bytes'] for row in rows),
                              readPolicy='Read at the workflow stage; all pages required. Plan is not proof of reading.',
                              conditional=manifest['conditional'],
                              conditionRoutes={key: item | dict(selected=any(row['id'] == key for row in rows))
                                  for key, item in manifest.get('readingRoute', {}).get('conditional', {}).items()}),
              ensure_ascii=False, indent=2))
    else:
        path, text, hash_ = content(runtime, manifest, args.module)
        pages = page_text(text)
        if not 1 <= args.page <= len(pages):
            raise ValueError('page out of range; valid 1..' + str(len(pages)))
        page = pages[args.page - 1]
        receipt = dict(release=manifest['release'], module=args.module, file=str(path),
                       localOverride=manifest.get('_localModuleOverrides', {}).get(args.module, {}).get('version'),
                       page=args.page, pages=len(pages), fileSha256=hash_, pageSha256=sha(page.encode()),
                       chars=len(page), bytes=len(page.encode()), encoding='utf-8', newline='LF',
                       completeModule=(len(pages) == 1))
        print('LIUREN_PAGE_BEGIN ' + json.dumps(receipt, ensure_ascii=False))
        sys.stdout.write(page)
        print('\nLIUREN_PAGE_END ' + json.dumps(dict(module=args.module, page=args.page, pages=len(pages),
                                                    pageSha256=receipt['pageSha256']), ensure_ascii=False))
        if len(pages) > 1:
            print('全模块完整需取得每一页及结束标记；最后一页本身不证明此前页已读取。')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print('LIUREN_LOAD_ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(2)
