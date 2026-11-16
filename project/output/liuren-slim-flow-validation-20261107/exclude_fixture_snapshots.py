from pathlib import Path
import json,tempfile
OUT=Path(__file__).resolve().parent
p=Path(json.loads((OUT/'host-path.json').read_text('utf-8'))['directory']).resolve()
assert p.parent==Path(tempfile.gettempdir()).resolve() and p.name.startswith('liuren-slim-host-')
(p/'.gitignore').write_text('.opencode/node_modules/\noutput/\n排盘存档/\n','utf-8')
print('Excluded generated fixture files from test snapshots.')
