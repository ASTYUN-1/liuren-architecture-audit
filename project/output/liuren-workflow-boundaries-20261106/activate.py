"""Install only the reviewed local files; switch active pointer last."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
before = json.loads((OUT / 'before-manifest.json').read_text('utf-8'))
candidate = OUT / 'candidate-live'
pointer = json.loads((candidate / '.opencode/liuren-active.json').read_text('utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.workflow08-installing')
    if temporary.exists():
        raise ValueError('Refusing to overwrite existing temporary file: ' + str(temporary))
    shutil.copyfile(source, temporary)
    temporary.replace(target)


for path, digest in before['live'].items():
    if sha(ROOT / path) != digest:
        raise ValueError('Active file changed since backup, preserve new edits: ' + path)
for path, digest in before['runtime'].items():
    if sha(ROOT / before['parentRuntime'] / path) != digest:
        raise ValueError('Parent runtime changed: ' + path)
checks = json.loads((OUT / 'candidate-preservation-checks.json').read_text('utf-8'))
if checks['status'] != 'passed' or checks['release'] != pointer['release']:
    raise ValueError('Candidate preservation checks missing')
source_run = OUT / 'candidate-runtime'
manifest = json.loads((source_run / 'manifest.json').read_text('utf-8'))
if manifest['version'] != pointer['methodVersion']:
    raise ValueError('Candidate identity mismatch')
for path, digest in manifest['files'].items():
    if sha(source_run / path) != digest:
        raise ValueError('Candidate changed after checking: ' + path)
for path, digest in pointer['workflowImplementation'].items():
    source = candidate / path if (candidate / path).exists() else ROOT / path
    if sha(source) != digest:
        raise ValueError('Implementation changed after checking: ' + path)
destination = ROOT / pointer['runtime']
if destination.exists():
    raise ValueError('Refusing to overwrite runtime: ' + str(destination))
shutil.copytree(source_run, destination)
paths = [p for p in before['live'] if p != '.opencode/liuren-active.json'] + ['.opencode/liuren-active.json']
installed = []
try:
    for path in paths:
        install(candidate / path, ROOT / path)
        installed.append(path)
    for path in paths:
        if sha(ROOT / path) != sha(candidate / path):
            raise ValueError('Installed bytes mismatch: ' + path)
except Exception:
    for path in reversed(installed):
        install(OUT / 'before' / path, ROOT / path)
    raise
receipt = {
    'status': 'active', 'release': pointer['release'], 'previousRelease': before['parentRelease'],
    'runtime': pointer['runtime'], 'methodVersion': pointer['methodVersion'],
    'files': {path: sha(ROOT / path) for path in paths},
    'runtimeFiles': {path.relative_to(destination).as_posix(): sha(path) for path in destination.rglob('*') if path.is_file()},
    'externalModelCalled': False, 'websiteChanged': False, 'restartOpenCodeRequired': True,
}
(OUT / 'activation-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': receipt['status'], 'release': receipt['release'], 'installedLiveFiles': len(paths)}, ensure_ascii=False))
