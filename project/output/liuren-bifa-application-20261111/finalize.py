"""Finish the 45 application update in a new immutable build, preserving r1."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import argparse

R = Path(__file__).resolve().parents[2]
O = Path(__file__).resolve().parent
load = lambda p: json.loads(p.read_text('utf-8-sig'))
enc = lambda d: (json.dumps(d, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = load(R / '.opencode/liuren-active.json')
args = argparse.ArgumentParser()
args.add_argument('--from-release', default='20261111-bifa-use-45')
args.add_argument('--to-release', default='20261111-bifa-use-45-final')
options = args.parse_args()
OLD, NEW = options.from_release, options.to_release
assert p['release'] == OLD
interim = {f.relative_to(R).as_posix(): sha(f) for f in (R / p['runtime']).rglob('*') if f.is_file()}
runtime = R / 'runtime/liuren' / NEW
assert not runtime.exists()
shutil.copytree(R / p['runtime'], runtime)
old_bifa = (runtime / 'references/bifa.md').read_text('utf-8')
end = old_bifa.index('## 使用总则') if '## 使用总则' in old_bifa else old_bifa.index('## 查询入口')
section = old_bifa[old_bifa.index('## 毕法赋：'):end]
(runtime / 'references/bifa.md').write_text('''# 毕法赋按号速查

''' + section + '''## 查询入口

- material_id:BF-01至BF-100：百法录，含本盘已列子格、理解、分析线索和北海摘录。
- material_id:BF-B35或BF-D35：北海或《大全》第35法连续原章，其他法号类推。
- module:bifa-basic：已登记基本条件的范围及采用边界。
- module:bifa-statements：固定展示句库，仅是程序描述，不是判断规则。

原先A/B/C等分类速查含构成简化和固定断语，已由上述按号入口替代；原样保留在冻结runtime44的references/bifa.md供追溯，不作为当前成格定义或解课依据。成格定义以已核条件表为准，应用回到本问专项和共用判断规范。
''', encoding='utf-8')
f = runtime / 'methods/structure.md'
text = f.read_text('utf-8').replace(
    '《毕法》课传结构是课体的重要外延，问答录反复以毕法口诀断成败：',
    '以下为《指南》问答录在特定原例中的结构取义摘录，保留原有强语供追溯，不是本盘固定结论。人宅、主客等属于原例定位；当前须依本问重新定位，按上方描述性原则和原有综合方法处理：')
f.write_text(text, encoding='utf-8')
pending = {}
for rel in ['opencode.json', 'README.md', '目录总索引.md']:
    text = (R / rel).read_text('utf-8').replace('runtime/liuren/' + OLD, 'runtime/liuren/' + NEW).replace('指向 `' + OLD + '`', '指向 `' + NEW + '`')
    pending[rel] = text.encode('utf-8')
current_sha = lambda rel: hashlib.sha256(pending[rel]).hexdigest() if rel in pending else sha(R / rel)
# Hash the manifest LAST, after all version-bearing files have been saved.
for name in ['loader-contract.json', 'references/shensha-policy.json', 'references/shensha-authority-evidence.json', 'references/confirmed-policy-register.json', 'reading-route.json', 'manifest.json']:
    d = load(runtime / name)
    d['release'] = NEW
    if name in ['manifest.json', 'loader-contract.json']:
        d['parentRelease'] = OLD
        if 'bookRetrieval' in d:
            d['bookRetrieval']['compatibleMethodRelease'] = NEW
    if name == 'loader-contract.json':
        d['sourceHashes'] = {rel: current_sha(rel) for rel in d['sourceHashes']}
    if name == 'manifest.json':
        d['files'] = {rel: sha(runtime / rel) for rel in d['files']}
        d['version'] = hashlib.sha256(json.dumps(d['files'], sort_keys=True).encode()).hexdigest()
    (runtime / name).write_bytes(enc(d))
p.update(release=NEW, runtime=runtime.relative_to(R).as_posix(), previousRelease=OLD,
         methodVersion=load(runtime / 'manifest.json')['version'])
p['bookRetrieval']['compatibleMethodRelease'] = NEW
p['workflowImplementation'] = {rel: current_sha(rel) for rel in p['workflowImplementation']}
pending['.opencode/liuren-active.json'] = enc(p)
for rel in sorted(pending, key=lambda s: s == '.opencode/liuren-active.json'):
    target = R / rel
    temp = target.with_name(target.name + '.bifa45r2.tmp')
    temp.write_bytes(pending[rel])
    os.replace(temp, target)
before = load(O / 'before.json')
assert all(sha(R / f) == h for f, h in before['frozen'].items())
assert all(sha(R / f) == h for f, h in interim.items())
(O / (OLD + '-frozen.json')).write_bytes(enc(interim))
(O / 'after.json').write_bytes(enc({'release': NEW, 'runtime': p['runtime'], 'methodVersion': p['methodVersion'],
    'files': {f: sha(R / f) for f in before['files']}, 'frozen44_unchanged': True,
    'interim45_unchanged': True, 'models_unchanged': True}))
print('Finalized', NEW, '; runtime44 and interim45 unchanged')
