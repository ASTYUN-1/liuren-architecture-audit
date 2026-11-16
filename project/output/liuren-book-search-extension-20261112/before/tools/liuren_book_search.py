"""Three pinned Liuren books: chapter/paragraph retrieval, no model or library calls.

The index is a rebuildable locator, never an extracted theory or reading receipt.
Ordinary searches open it read-only and quote the hash-checked original files.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DATA = Path('knowledge/liuren-book-index/20261105')
SCHEMA = 'liuren-three-books-v1'
EXPECTED_PATHS = {
    'RG': '书籍库/经典古籍/佚名/壬归.txt',
    'LF': '书籍库/北海闲人/理法简易.txt',
    'TY': '书籍库/现代著作/献给六壬天一群的六壬笔记-2023年.txt',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def normalize(text):
    text = unicodedata.normalize('NFKC', text).lower().translate(str.maketrans('剋螣', '克腾'))
    return ''.join(re.findall(r'[\u3400-\u9fffa-z0-9]+', text))


def tokens(text):
    value = normalize(text)
    return set(value[i:i+2] for i in range(len(value)-1))


def pinned_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('book index path escapes project')
    return path


def catalog(root):
    path = pinned_path(root, DATA / 'catalog.json')
    raw = path.read_bytes()
    data = json.loads(raw.decode('utf-8'))
    if data.get('schema') != SCHEMA or {b['id']: b['path'] for b in data['books']} != EXPECTED_PATHS:
        raise ValueError('book catalog must contain exactly the three registered sources')
    return data, sha(raw)


def source_lines(root, book, permitted=None):
    path = pinned_path(root, book['path'])
    if permitted is not None and not permitted(path):
        raise ValueError('book source is outside current material scope')
    raw = path.read_bytes()
    if sha(raw) != book['sha256']:
        raise ValueError('BOOK_SOURCE_CHANGED: 原书字节已变，须核对版本并重建索引：' + book['path'])
    lines = raw.decode(book['encoding']).splitlines()
    if len(lines) != book['line_count']:
        raise ValueError('book source line mapping changed')
    return lines


def sections_for(book, lines):
    sections = []
    starts = book['headings']
    if not starts or starts[0]['line'] != 1:
        raise ValueError('outline must cover from the first original line')
    for i, entry in enumerate(starts):
        start = entry['line']
        end = starts[i+1]['line']-1 if i+1 < len(starts) else len(lines)
        if start > end or not 1 <= entry['level'] <= 4:
            raise ValueError('invalid or unsorted outline')
        if normalize(entry['anchor']) not in normalize(lines[start-1]):
            raise ValueError('heading anchor mismatch: ' + book['id'] + ':' + str(start))
        parents = []
        for old in reversed(sections):
            if old['level'] < entry['level']:
                parents = old['heading_path']
                break
        title = entry['title']
        subtree_end = next((h['line']-1 for h in starts[i+1:] if h['level'] <= entry['level']), len(lines))
        sections.append(dict(id=book['id'] + '-S-' + sha((str(start)+':'+title).encode())[:10],
                             book=book['id'], title=title, level=entry['level'], start=start,
                             end=end, subtree_end=subtree_end,
                             heading_path=parents+[title], kind=entry.get('kind', 'mixed-source'),
                             boundary_review=entry.get('boundary_review', 'heading-anchor-checked')))
    return sections


def paragraph_spans(lines, start, end):
    """Join PDF hard wraps, even when every printed line has a blank after it.

    Stop only at a terminal sentence before a blank, never at a fixed line count.
    Long paragraphs remain indivisible and are explicitly paged at read time.
    """
    spans, first = [], start
    for n in range(start, end+1):
        value = lines[n-1].rstrip()
        if (value and re.search(r'[。！？!?][”’」』）)]?$', value)
                and (n == end or not lines[n].strip())):
            spans.append((first, n))
            first = n+1
    if first <= end:
        spans.append((first, end))
    return spans


def passage_spans(lines, section):
    # Small sections are returned together, preserving local exceptions.
    if sum(len(x) for x in lines[section['start']-1:section['end']]) <= 2200:
        return [(section['start'], section['end'])]
    result, start, size, last = [], None, 0, section['start']
    for a, b in paragraph_spans(lines, section['start'], section['end']):
        amount = sum(len(x) for x in lines[a-1:b])
        if start is not None and size+amount > 1500:
            result.append((start, last))
            start, size = None, 0
        if start is None:
            start = a
        size += amount
        last = b
    if start is not None:
        result.append((start, last))
    return result


def build(root=ROOT):
    root = Path(root).resolve()
    data, identity = catalog(root)
    target = pinned_path(root, DATA / 'index.sqlite3')
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='book-index-', suffix='.sqlite3', dir=target.parent)
    os.close(fd)
    stats = []
    try:
        with closing(sqlite3.connect(temp)) as db, db:
            db.execute('CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)')
            db.executemany('INSERT INTO metadata VALUES (?,?)', [('schema', SCHEMA), ('catalog_sha256', identity)])
            db.execute('CREATE TABLE passages (id TEXT PRIMARY KEY, book TEXT, section TEXT, start INTEGER, end INTEGER, kind TEXT, labels TEXT)')
            db.execute('CREATE VIRTUAL TABLE search USING fts5(title, body, tokenize="unicode61")')
            for book in data['books']:
                lines = source_lines(root, book)
                sections = sections_for(book, lines)
                total = 0
                for section in sections:
                    labels = json.dumps(section, ensure_ascii=False)
                    for a, b in passage_spans(lines, section):
                        pid = section['id'] + '-L' + str(a) + '-' + str(b)
                        title = ' '.join(section['heading_path'])
                        body = '\n'.join(lines[a-1:b])
                        row = db.execute('INSERT INTO passages VALUES (?,?,?,?,?,?,?)',
                            (pid, book['id'], section['id'], a, b, section['kind'], labels)).lastrowid
                        db.execute('INSERT INTO search(rowid,title,body) VALUES (?,?,?)',
                            (row, ' '.join(sorted(tokens(title))), ' '.join(sorted(tokens(body)))))
                        total += 1
                stats.append(dict(book=book['id'], sections=len(sections), passages=total, lines=len(lines)))
            db.execute("INSERT INTO search(search) VALUES ('optimize')")
        os.replace(temp, target)
    finally:
        Path(temp).unlink(missing_ok=True)
    return dict(schema=SCHEMA, catalog_sha256=identity, books=stats, index_sha256=sha(target.read_bytes()),
                semantic_reading_complete=False, predictive_validation_count=0)


class BookSearch:
    def __init__(self, root=ROOT, permitted=None):
        self.root = Path(root).resolve()
        self.data, self.catalog_hash = catalog(self.root)
        self.books = {b['id']: b for b in self.data['books']}
        self.permitted = permitted

    def selected(self, book):
        if book is not None and book not in self.books:
            raise ValueError('book must be RG, LF or TY')
        return [self.books[book]] if book else list(self.books.values())

    def outline(self, book=None):
        result = []
        for item in self.selected(book):
            lines = source_lines(self.root, item, self.permitted)
            row = {k: item[k] for k in ('id', 'title', 'aliases', 'path', 'sha256', 'line_count', 'source_identity')}
            if book:
                row['sections'] = sections_for(item, lines)
            else:
                row['section_count'] = len(item['headings'])
            result.append(row)
        return dict(schema=SCHEMA, books=result, note='目录与切段仅作定位；未声明整书精读或规则一致。')

    def connect(self):
        target = pinned_path(self.root, DATA / 'index.sqlite3')
        if not target.is_file():
            raise ValueError('BOOK_INDEX_MISSING: 在Build模式运行 tools/liuren_book_search.py build')
        db = sqlite3.connect(target.as_uri()+'?mode=ro', uri=True)
        try:
            meta = dict(db.execute('SELECT key,value FROM metadata'))
            if meta.get('schema') != SCHEMA or meta.get('catalog_sha256') != self.catalog_hash:
                raise ValueError('BOOK_INDEX_STALE: 目录或专题已变，须在Build模式重建索引')
        except Exception:
            db.close()
            raise
        return db

    def query_terms(self, query):
        if not isinstance(query, str) or len(query) > 200:
            raise ValueError('book query must be a short string within 200 characters')
        terms = [normalize(x) for x in re.split(r'[\s,，、;；]+', query.strip()) if len(normalize(x)) >= 2]
        if not terms or len(terms) > 16:
            raise ValueError('使用至少两个字符的争点词；每次最多16个词')
        expansion = set(terms)
        for topic in self.data['topics']:
            if any(normalize(alias) in normalize(query) for alias in topic['aliases']):
                expansion.update(normalize(alias) for alias in topic['aliases'])
        return terms, sorted(expansion)

    def search(self, query='', *, queries=None, book=None, limit=4, max_chars=14000):
        if not isinstance(limit, int) or not 1 <= limit <= 12 or not 2000 <= max_chars <= 24000:
            raise ValueError('book search limit within 1..12; max_chars within 2000..24000')
        if queries is not None and query:
            raise ValueError('use query or queries, not both')
        qs = queries if queries is not None else [query]
        if not isinstance(qs, list) or not 1 <= len(qs) <= 4:
            raise ValueError('一次最多集中检索4个争点')
        parsed = [self.query_terms(q) for q in qs]
        selected = self.selected(book)
        # Hash the originals on every request; never emit cached original text.
        sources = {b['id']: source_lines(self.root, b, self.permitted) for b in selected}
        candidates, groups = {}, []
        db = self.connect()
        try:
            for qi, (terms, expansion) in enumerate(parsed):
                needles = sorted(set().union(*(tokens(t) for t in expansion)))
                match = ' OR '.join('"'+token+'"' for token in needles)
                rows = db.execute('SELECT p.*, bm25(search,3.0,1.0) FROM search JOIN passages p ON p.rowid=search.rowid WHERE search MATCH ? ORDER BY bm25(search,3.0,1.0)', (match,)).fetchall()
                ranked = []
                for pid, bid, sid, a, b, kind, labels, fts in rows:
                    if bid not in sources:
                        continue
                    section = json.loads(labels)
                    body = normalize('\n'.join(sources[bid][a-1:b]))
                    title = normalize(' '.join(section['heading_path']))
                    literal = [t for t in terms if t in body or t in title]
                    alias = [t for t in expansion if t in body or t in title]
                    # Character bigrams broaden recall, but do not count as a full term match.
                    if not alias:
                        continue
                    key = (len(literal)==len(terms), len(literal), sum(t in title for t in terms),
                           sum(min(body.count(t), 5) for t in terms), kind=='theory', -fts)
                    ranked.append((key, pid))
                    candidates[pid] = dict(id=pid, book=bid, section=section, start=a, end=b,
                                           kind=kind, matches=candidates.get(pid, {}).get('matches', {}))
                    candidates[pid]['matches'][str(qi)] = dict(literal_terms=literal, alias_terms=alias)
                ranked.sort(key=lambda pair: pair[0], reverse=True)
                # When a passage covers every requested term, partial matches
                # need not fill the answer. Explicit companion sources below
                # preserve registered differing conditions and viewpoints.
                if ranked and ranked[0][0][0]:
                    ranked = [pair for pair in ranked if pair[0][0]]
                groups.append([pid for _, pid in ranked])
        finally:
            db.close()
        # Round-robin prevents the first batched query consuming every result slot.
        order = []
        for offset in range(max((len(g) for g in groups), default=0)):
            for group in groups:
                if offset < len(group) and group[offset] not in order:
                    order.append(group[offset])
        eligible_ids = set(order)
        hits, spans, budget = [], {}, max_chars
        for pid in order:
            if len(hits) >= limit or budget < 500:
                break
            row = candidates[pid]
            bid, a, b = row['book'], row['start'], row['end']
            # Coalesce only overlapping ranges in this same source, never opinions.
            if any(x <= a and b <= y for x, y in spans.get(bid, [])):
                continue
            lines = sources[bid]
            section = row['section']
            # Include the preceding and following paragraph groups when bounded.
            # This is context, not an inferred rule/exception classification.
            neighbors = passage_spans(lines, section)
            at = neighbors.index((a, b))
            left = neighbors[max(0, at-1)][0]
            right = neighbors[min(len(neighbors)-1, at+1)][1]
            if sum(len(x)+1 for x in lines[left-1:right]) <= min(budget, 6000):
                a, b = left, right
            excerpt, returned_end, char_offset = [], a-1, None
            allowance = min(budget, 6000)
            used = 0
            for n in range(a, b+1):
                text = lines[n-1]
                if used+len(text)+1 > allowance:
                    if used == len(excerpt):  # only blank leading lines so far
                        text = text[:max(1, allowance-used-1)]
                        excerpt.append(text)
                        returned_end, char_offset = n, len(text)
                    break
                excerpt.append(text)
                returned_end = n
                used += len(text)+1
            text = '\n'.join(excerpt)
            budget -= len(text)
            partial = returned_end < b or char_offset is not None
            source = self.books[bid]
            # Adjacent context is explicit when a long chapter cannot fit in one result.
            context = dict(section_start=section['start'], section_end=section['end'],
                           before=section['start'] < a, after=returned_end < section['end'],
                           note='相邻段可能包含前提、例外、书例或注解；未自动归纳为通则。')
            refs = [dict(id=e['id'], topic=e['topic'], start=e['start'], end=e['end'], source_identity=e['source_identity'])
                    for e in source.get('checked_locators', []) if e['start'] <= b and e['end'] >= a]
            hits.append(dict(id=pid, book=bid, title=source['title'], path=source['path'],
                             fileSha256=source['sha256'], sourceEncoding=source['encoding'],
                             lineMapping='decoded original splitlines; one-based; no reflow',
                             source_identity=source['source_identity'], content_kind=row['kind'],
                             heading_path=section['heading_path'], section_id=section['id'],
                             start=a, end=returned_end, passage_end=b, text=text,
                             matched_queries=row['matches'], checked_locators=refs,
                             handoff=dict(id='B_'+bid+'_'+str(a)+'_'+str(returned_end), title=source['title'],
                                          source_path=source['path'], line_start=a, line_end=returned_end,
                                          line_mode='universal', sha256=source['sha256']) if not partial else None,
                             context=context, passage_complete=not partial,
                             section_complete=a==section['start'] and returned_end==section['end'] and not partial,
                             continuation=dict(path=source['path'], start=returned_end if char_offset is not None else returned_end+1,
                                               char_offset=char_offset, count=min(300, max(1,b-returned_end))) if partial else None))
            spans.setdefault(bid, []).append((a, returned_end))
        related, related_seen = [], set()
        for topic in self.data['topics']:
            if not any(normalize(alias) in normalize(q) for alias in topic['aliases'] for q in qs):
                continue
            for locator in topic.get('related_locators', []):
                if locator in related_seen:
                    continue
                related_seen.add(locator)
                for source in selected:
                    loc = next((e for e in source.get('checked_locators', []) if e['id']==locator), None)
                    if loc is None:
                        continue
                    # A related cross-reference must not be silently collapsed into a matching doctrine.
                    if any(h['book']==source['id'] and h['start']<=loc['start'] and h['end']>=loc['end'] and not h['continuation'] for h in hits):
                        continue
                    text = '\n'.join(sources[source['id']][loc['start']-1:loc['end']])
                    if len(text) > budget:
                        related.append(dict(id=locator, path=source['path'], start=loc['start'], end=loc['end'],
                                            topic=loc['topic'], text=None, omitted_reason='text budget; use read at this range'))
                        continue
                    budget -= len(text)
                    related.append(dict(id=locator, path=source['path'], start=loc['start'], end=loc['end'],
                                        fileSha256=source['sha256'], source_identity=loc['source_identity'],
                                        topic=loc['topic'], text=text, note='相关原文并列，条件或口径可能不同；不自动合并。'))
        return dict(schema=SCHEMA, action='book_search', queries=qs,
                    coverage=dict(books=list(sources), other_books_searched=False, cases_searched=False, experience_searched=False),
                    hits=hits, related_sources=related, matching_passages=len(eligible_ids), returned=len(hits),
                    literal_query_coverage=[dict(query=q, matching_passages=len(groups[i]),
                        returned_hits=sum(str(i) in h['matched_queries'] for h in hits)) for i,q in enumerate(qs)],
                    omitted_matching_passages=max(0,len(eligible_ids)-len(hits)),
                    text_chars=max_chars-budget, catalog_sha256=self.catalog_hash,
                    note='按原词命中优先、章节及相关性排序；排序不是术理权重或正确率。仅检索三本，未命中可用scan/books查其他原书。上下文未全返时按所示范围read；同版已读复用，不为凑次数重复检索。')


def check(root=ROOT):
    search = BookSearch(root)
    result = search.outline()
    db = search.connect()
    errors = []
    try:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            errors.append('sqlite integrity check failed')
        for book in search.books.values():
            lines = source_lines(search.root, book)
            expected = []
            for section in sections_for(book, lines):
                expected.extend((a,b) for a,b in passage_spans(lines, section))
            actual = db.execute('SELECT start,end FROM passages WHERE book=? ORDER BY start', (book['id'],)).fetchall()
            if actual != expected or not actual or actual[0][0] != 1 or actual[-1][1] != len(lines):
                errors.append(book['id']+': passage coverage mismatch')
            if any(actual[i][1]+1 != actual[i+1][0] for i in range(len(actual)-1)):
                errors.append(book['id']+': noncontiguous coverage')
            for loc in book.get('checked_locators', []):
                if sha('\n'.join(lines[loc['start']-1:loc['end']]).encode()) != loc['quote_sha256']:
                    errors.append(book['id']+': stale checked locator '+loc['id'])
        counts = dict(db.execute('SELECT book,count(*) FROM passages GROUP BY book'))
    finally:
        db.close()
    return dict(ok=not errors, errors=errors, books=result['books'], passages=counts,
                semantic_reading_complete=False, predictive_validation_count=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build','check','search','outline'])
    parser.add_argument('query', nargs='?', default='')
    parser.add_argument('--book', choices=list(EXPECTED_PATHS))
    parser.add_argument('--limit', type=int, default=4)
    args = parser.parse_args()
    if args.action == 'build':
        value = build()
    elif args.action == 'check':
        value = check()
    elif args.action == 'outline':
        value = BookSearch().outline(args.book)
    else:
        value = BookSearch().search(args.query, book=args.book, limit=args.limit)
    print(json.dumps(value, ensure_ascii=False, indent=2))
    if value.get('ok') is False:
        raise SystemExit(2)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', newline='')
    main()
