"""Create a read-only inventory and bounded source notes; never edit active rules."""
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def write_json(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

active_path = ROOT / '.opencode/liuren-active.json'
active_sha = sha(active_path)
active = json.loads(active_path.read_text(encoding='utf-8-sig'))
runtime = ROOT / active['runtime']
manifest = json.loads((runtime / 'manifest.json').read_text(encoding='utf-8-sig'))
route = json.loads((runtime / 'reading-route.json').read_text(encoding='utf-8-sig'))
modules = manifest['modules']

focused = {
    'liqi', 'positioning', 'relations', 'structure', 'adjudication',
    'report', 'void', 'period-outlook', 'long-period', 'evidence',
}

def local_links(path):
    raw_text = path.read_text(encoding='utf-8-sig')
    outside, fence = [], None
    for line in raw_text.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)[0]
            fence = None if token == fence else token
            continue
        if fence is None:
            outside.append(line)
    text = '\n'.join(outside)
    links = []
    for match in re.finditer(r'\]\((?:<([^>]+)>|([^\s)]+))\)', text):
        target = match.group(1) or match.group(2)
        if target.startswith('#') or re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', target):
            continue
        raw = unquote(target.split('#', 1)[0])
        resolved = (path.parent / raw).resolve()
        links.append({'target': target, 'exists': resolved.exists(), 'resolved': str(resolved)})
    return links

items = []
for name, meta in modules.items():
    path = runtime / meta['file']
    stages = [s['id'] for s in route['stages'] if name in s['required']]
    conditional = route.get('conditional', {}).get(name)
    role = '共同必读' if meta.get('required') else ('占类专项' if name in route['domains'] else '条件方法/参考/维护')
    items.append({
        'id': name, 'label': route.get('labels', {}).get(name, name),
        'file': rel(path), 'exists': path.exists(), 'sha256': sha(path) if path.exists() else None,
        'role': role, 'current_required_stages': stages, 'route_condition': conditional,
        'manifest_trigger': meta.get('trigger'), 'requires': meta.get('requires', []),
        'semantic_review': '重点正文或相关段核读；未完成逐条溯源审查' if name in focused else '仅完成清点；本轮未登记语义审查完成',
        'local_markdown_links': local_links(path) if path.exists() else [],
    })

entry_items = []
for path in sorted((ROOT / '.opencode/skills/liuren').rglob('SKILL.md')):
    name = path.parent.name
    archive = None
    if name != 'daliuren':
        archive_path = runtime / ('archive/previous-package/.opencode/skills/daliuren/refs/runtime/'
                                  'sources/snapshots/.opencode/skills/' + name + '/SKILL.md')
        archive = {'file': rel(archive_path), 'exists': archive_path.exists(),
                   'sha256': sha(archive_path) if archive_path.exists() else None,
                   'semantic_review': '仅核加载关系；未完成旧规程逐条审查'}
    entry_items.append({'name': name, 'file': rel(path), 'sha256': sha(path),
                        'review': '入口全文已核；不代表全部下游完成',
                        'archive_procedure': archive, 'local_markdown_links': local_links(path)})

unknown_deps = [{'module': k, 'dependency': d} for k, v in modules.items()
                for d in v.get('requires', []) if d not in modules]
cycles = []
def visit(name, stack):
    if name in stack:
        cycles.append(stack[stack.index(name):] + [name])
        return
    for child in modules.get(name, {}).get('requires', []):
        visit(child, stack + [name])
for name in modules:
    visit(name, [])
link_count = sum(len(v['local_markdown_links']) for v in items + entry_items)
missing_links = [{'from': v['file'], **link} for v in items + entry_items
                 for link in v['local_markdown_links'] if not link['exists']]
data = {'date_label': '2026-11-05', 'release': active['release'],
        'active_pointer_sha256': active_sha, 'scope': '首轮静态清点与重点段审查，未完成全套语义审查',
        'counts': {'entries': len(entry_items), 'modules': len(items),
                   'required': sum(x['role'] == '共同必读' for x in items),
                   'domains': sum(x['role'] == '占类专项' for x in items),
                   'local_link_occurrences_checked': link_count},
        'static_checks': {'unknown_dependencies': unknown_deps, 'declared_dependency_cycles': cycles,
                          'missing_local_link_occurrences': missing_links,
                          'limits': '仅检查已登记requires及代码围栏外可解析相对Markdown链接；不证明文本触发完备、语义一致或真实调用成功。',
                          'code_display_followup': 'shensha-field-meanings.md的源码展示含路径样式插入，需回源核对展示保真；不是流程跳转失败或排盘引擎已改变的证据。'},
        'entries': entry_items, 'modules': items, 'current_route': route}
write_json('module-map.json', data)

md = ['# 当前调用清单（首轮）', '',
      f"活动版本：`{active['release']}`。{len(entry_items)}个技能入口、{len(items)}个内部模块。",
      '', '清点、文件存在、声明依赖和链接检查不等于语义精读；下表明确保留未完成状态。', '',
      '```mermaid', 'flowchart TD', '  Q[用户任务] --> A[单事研判 daliuren]',
      '  Q --> B[案例查询与复盘 liuren-cases]', '  Q --> C[资料提取 liuren-extract]',
      '  Q --> D[出生推命 liuren-tuiming]',
      '  A --> R[按当前十一环节读取必读与命中占类]',
      '  R --> M[条件模块与参考资料]', '  R --> E[盘面初判后案例和经验检索]',
      '  B --> O[分段加载各自归档完整规程]', '  C --> O', '  D --> O',
      '  B --> V[只查参照时读取 evidence]', '```', '',
      '以上表示目前入口关系，不是建议的新专业流程。AGENTS、本机模式提示和报告规则也是待协调指令源。', '',
      '## 技能入口', '']
for item in entry_items:
    md.append(f"- `{item['name']}`：[{item['file']}](../../{item['file']})；{item['review']}。")
    if item['archive_procedure']:
        a = item['archive_procedure']
        md.append(f"  加载器：`tools/load-liuren-procedure.py`；旧完整规程存在：{a['exists']}；{a['semantic_review']}。")
md += ['', '## 59个模块', '', '| ID | 角色 | 当前必读环节/触发 | 声明依赖 | 审查状态 |', '|---|---|---|---|---|']
for item in items:
    trigger = ','.join(map(str, item['current_required_stages']))
    if not trigger:
        trigger = '占类命中' if item['role'] == '占类专项' else ((item['route_condition'] or {}).get('trigger') or item['manifest_trigger'] or '未登记')
    md.append(f"| [{item['id']}](../../{item['file']}) | {item['role']} | {trigger} | {', '.join(item['requires']) or '—'} | {item['semantic_review']} |")
md += ['', '## 静态检查范围', '',
       f"共同必读 {data['counts']['required']} 项，占类 {data['counts']['domains']} 项；未知声明依赖 {len(unknown_deps)} 项，声明依赖环 {len(cycles)} 项。",
       f"检查代码围栏外相对Markdown链接出现次数 {link_count}，未找到目标的出现次数 {len(missing_links)}。仅是文件目标存在检查，不判断规则或引用内容是否正确。",
       '', '另见：shensha-field-meanings.md的源码展示含路径样式插入，需回源核对展示保真；不能计为流程跳转失败，也不能据此推断排盘引擎发生改变。',
       '', '完整路径、哈希、依赖、链接记录及路由快照见 [module-map.json](module-map.json)。']
(OUT / '调用清单.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

specs = [
    ('书籍库/北海闲人/理法简易.txt', 'utf-8-sig', [(238, 322)],
     '重点连续段支持理气指导取类察类、课体与类象职责；不是全文完成。原文件CRCRLF，以LF分行，保留原字节不改。'),
    ('书籍库/北海闲人/北海闲人，特训班讲义.txt', 'gb18030', [(6, 101)],
     '重点连续段包含三步走、侧重、显象和分房例。此本强断及原载反馈不等于独立验证；“旺不为空”与其他文本口径待审。'),
    ('书籍库/北海闲人/六壬金针_修正版.md', 'utf-8-sig', [(1, 35), (1132, 1165)],
     'OCR修订本；版本说明和判断段已核，未决字句不当作绝对原版。'),
    ('书籍库/经典古籍/佚名/壬归.txt', 'utf-8-sig', [(5, 5), (273, 301), (355, 363), (389, 389)],
     '气、类、求财主宾及阴神关节重点段；求财具体取法不无条件推广到其他占类。'),
]
notes = []
for filename, encoding, ranges, comment in specs:
    path = ROOT / filename
    raw = path.read_bytes()
    lines = raw.decode(encoding).split('\n')
    windows = []
    for start, end in ranges:
        windows.append({'lf_start': start, 'lf_end': end,
                        'text': '\n'.join(line.rstrip('\r') for line in lines[start-1:end])})
    notes.append({'file': filename, 'sha256': sha(path), 'encoding': encoding,
                  'line_convention': '原字节解码后仅按LF分行，显示时去行尾CR；不等同Python splitlines或知识工作台行号',
                  'comment': comment, 'windows': windows})
write_json('source-notes.json', {'status': '首轮限定原段研读；非规则卡，非全书完成声明', 'sources': notes})
source_md = ['# 原文研读笔记（限定原段）', '',
             '引文保持所读本字句；只去显示行末CR，不修疑字。行号以原字节解码后按LF分行为准，不能直接填入采用splitlines口径的知识工作台证据字段。', '',
             '## 本轮解释与未决', '',
             '- 理气指导取类、察类，不能缩成课体总吉凶；类象不应一律降成事后描述。',
             '- 北海“三步走”适合作专业主线，技术核查与覆盖表围绕它服务；这是拟定的整理方式。',
             '- 《壬归》求财的通类、分类、主宾、本人、阴神与课传应连看，不能以财旺直接等同可取得。',
             '- 北海不同文本中的空亡口径、课体权重与强断仍待专题审查；不自行假设年代先后，不以单例和解。',
             '- 当前模块部分“作者警告”可能是后加评价，身份须溯源。书内反馈、旧AI解释与本轮解释必须分开。',
             '- 本稿没有建立已验证定则；原书极强或绝对断语保留作者身份，不升级成现实可靠性结论。', '']
for note in notes:
    source_md += [f"## {note['file']}", '', f"[项目内原件](../../{note['file']})", '',
                  f"编码：`{note['encoding']}`；原字节SHA256：`{note['sha256']}`。", '', note['comment'], '']
    for window in note['windows']:
        source_md += [f"### LF {window['lf_start']}–{window['lf_end']}", '', '```text']
        source_md += [f'{n}: {line}' for n, line in enumerate(window['text'].split('\n'), window['lf_start'])]
        source_md += ['```', '']
(OUT / '原文研读笔记.md').write_text('\n'.join(source_md) + '\n', encoding='utf-8')
if sha(active_path) != active_sha:
    raise RuntimeError('Active pointer changed during inventory')
print(json.dumps({'output': rel(OUT), 'counts': data['counts'],
                  'missing_links': len(missing_links), 'unknown_dependencies': len(unknown_deps),
                  'dependency_cycles': len(cycles), 'source_files': len(notes),
                  'active_pointer_unchanged': True}, ensure_ascii=False))
