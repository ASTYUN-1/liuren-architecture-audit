"""Compare saved handoffs and public metadata; never load private reasoning."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SPECS = [
    ('GPT主＋DeepSeek裁决', 'liuren-real-bus-20261107/run-20261107-163216',
     'ses_e4adcdfb6ffeWmcZw856sbfG6e', 'ses_e4ad9fd64ffeknhqm7zizjbOXJ'),
    ('DeepSeek主＋DeepSeek裁决', 'liuren-real-bus-deepseek-high-20261107/run-20261107-164917',
     'ses_e4acd4b15ffeKq75dQnQWQ5TbI', 'ses_e4ac91e4cffemThLlj0qGaRq30'),
]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stats(messages):
    assistant = [m for m in messages if m['role'] == 'assistant']
    calls = [t for m in assistant for t in m.get('tools', [])]
    reads = [t for t in calls if t['tool'] == 'liuren_adjudication_read']
    return {
        'assistant_turns': len(assistant),
        'models': sorted({(m.get('providerID'), m.get('modelID'), m.get('variant'))
                          for m in assistant}, key=str),
        'tools': dict(Counter(t['tool'] for t in calls)),
        'tool_errors': sum(t['status'] == 'error' for t in calls),
        'reasoning_tokens_metadata_only': sum((m.get('tokens') or {}).get('reasoning', 0) for m in assistant),
        'reader_output_characters_including_receipts': sum(t.get('outputCharacters', 0) for t in reads if t['status'] == 'completed'),
        'reader_calls': [{'input': t['input'], 'status': t['status'],
                          'output_characters': t.get('outputCharacters', 0)} for t in reads],
    }


cores, packets, runs = [], [], []
for label, directory, main_id, child_id in SPECS:
    directory = ROOT / 'output' / directory
    audit = read(directory / 'packet-audit.json')
    envelope_path = Path(audit['file'])
    envelope = read(envelope_path)
    archive_path = envelope_path.parent / envelope['packet_archive']['file']
    archive = read(archive_path)
    assert sha(archive_path) == envelope['packet_archive']['sha256']
    assert hashlib.sha256(envelope['reading_core']['content'].encode()).hexdigest() == envelope['reading_core']['sha256']
    core = json.loads(envelope['reading_core']['content'])
    packet = archive['packet']
    main = read(directory / f'{main_id}-metadata.json')
    child = read(directory / f'{child_id}-metadata.json')
    start = main[0]['time']['created']
    child_start = child[0]['time']['created']
    child_end = max(m['time'].get('completed', 0) for m in child)
    end = max(m['time'].get('completed', 0) for m in main)
    runs.append({
        'label': label, 'main_id': main_id, 'child_id': child_id,
        'directory': str(directory), 'packet': str(envelope_path),
        'packet_sha256': sha(envelope_path), 'archive': str(archive_path),
        'archive_sha256_verified': True, 'core_sha256_verified': True,
        'seconds': read(directory / 'result.json')['seconds'],
        'phase_seconds': {'preparation': (child_start-start)/1000,
                          'adjudication': (child_end-child_start)/1000,
                          'delivery': (end-child_end)/1000,
                          'session_total': (end-start)/1000},
        'core_characters': len(envelope['reading_core']['content']),
        'archive_characters': len(archive_path.read_text(encoding='utf-8')),
        'counts': {k: len(packet[k]) for k in ['facts', 'entities', 'observations', 'focus_issues', 'unknowns', 'method_materials']},
        'materials': [{'id': m['id'], 'title': m.get('title'),
                       'source_path': m.get('source_path'),
                       'characters': len(m.get('quote', '')),
                       'text_sha256': hashlib.sha256(m.get('quote', '').encode()).hexdigest()}
                      for m in packet['method_materials']],
        'main': stats(main), 'child': stats(child),
        'report_characters': len((directory / 'delivered-report.md').read_text(encoding='utf-8-sig')),
    })
    cores.append(core)
    packets.append(packet)

comparison = {
    'scope': 'Saved packets, public tool calls and metadata; no private reasoning or new model run.',
    'runs': runs,
    'identical_core_sections': {k: cores[0][k] == cores[1][k]
                                for k in ['original_question', 'program', 'shared_method', 'specialty_methods']},
    'different_chart_fields': [k for k in cores[0]['chart'] if cores[0]['chart'][k] != cores[1]['chart'][k]],
    'declared_life': [c['chart']['declared_life'] for c in cores],
    'questions': [p['questions'] for p in packets],
    'entities': [p['entities'] for p in packets],
    'observations': [p['observations'] for p in packets],
    'focus_issues': [p['focus_issues'] for p in packets],
}
(OUT / 'comparison.json').write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'identical': comparison['identical_core_sections'],
                  'chart_differences': comparison['different_chart_fields'],
                  'runs': [{k: r[k] for k in ['label', 'seconds', 'phase_seconds', 'core_characters', 'report_characters', 'counts']} for r in runs]}, ensure_ascii=False, indent=2))
