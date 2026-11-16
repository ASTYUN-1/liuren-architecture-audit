"""Read-only server skill export; never reads credentials or application data."""
import hashlib
import io
import json
import re
import shlex
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath

REMOTE = r'''
import hashlib,io,json,os,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
base=Path('/opt/wenheng/resources/.opencode/skills')
release=Path('/opt/wenheng/current').resolve()
assert base.is_dir(), 'Server skills directory missing'
files={}; skipped=[]; empty=[]
for directory,dirs,names in os.walk(base,followlinks=False):
    parent=Path(directory)
    for name in list(dirs):
        p=parent/name
        if p.is_symlink():
            skipped.append(str(p.relative_to(base))); dirs.remove(name)
    if not dirs and not names:
        empty.append('skills/'+str(parent.relative_to(base))+'/')
    for name in names:
        p=parent/name
        if p.is_symlink() or not p.is_file():
            skipped.append(str(p.relative_to(base))); continue
        files['skills/'+str(p.relative_to(base))]=p.read_bytes()
for name in ['knowledge.ts','runtime.ts','tools.ts']:
    p=release/'src/agent'/name
    if p.is_file() and not p.is_symlink():
        files['website-runtime/'+name]=p.read_bytes()
manifest={
    'source':str(base),'release':str(release),
    'pulledAtUtc':datetime.now(timezone.utc).isoformat(),
    'skippedSymlinksOrSpecialFiles':skipped,
    'files':{name:{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in sorted(files.items())}
}
stream=io.BytesIO()
with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in sorted(files.items()): z.writestr(name,data)
    for name in empty: z.writestr(name,b'')
    z.writestr('server-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8'))
sys.stdout.buffer.write(stream.getvalue())
'''

home = Path.home()
ssh = ['ssh.exe', '-F', 'NUL', '-i', str(home/'.ssh/old-server-control'),
       '-p', '22223', '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes',
       '-o', 'ConnectTimeout=12', '-o', 'StrictHostKeyChecking=yes',
       '-o', f'UserKnownHostsFile={home}/Documents/OldServerControl/linux_known_hosts',
       'slope@192.168.100.8', 'sudo -u wenheng python3 -c '+shlex.quote(REMOTE)]
result = subprocess.run(ssh, capture_output=True, timeout=120)
if result.returncode:
    raise RuntimeError('Read-only server export failed: '+result.stderr.decode('utf-8', errors='replace'))

archive = zipfile.ZipFile(io.BytesIO(result.stdout))
for entry in archive.infolist():
    p = PurePosixPath(entry.filename)
    if p.is_absolute() or '..' in p.parts or '\\' in entry.filename or ':' in entry.filename:
        raise RuntimeError('Unsafe archive path')
manifest = json.loads(archive.read('server-manifest.json'))
for name, expected in manifest['files'].items():
    data = archive.read(name)
    assert len(data) == expected['bytes']
    assert hashlib.sha256(data).hexdigest() == expected['sha256'], name

desktop = home/'Desktop'
assert desktop.is_dir(), 'Expected Desktop directory missing'
destination = desktop/('问衡服务器Skill包-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
destination.mkdir(exist_ok=False)
archive.extractall(destination)
for name, expected in manifest['files'].items():
    assert hashlib.sha256((destination/name).read_bytes()).hexdigest() == expected['sha256'], name

knowledge = (destination/'website-runtime/knowledge.ts').read_text(encoding='utf-8')
required_match = re.search(r'export const REQUIRED_SKILLS\s*=\s*\[(.*?)\]', knowledge, re.S)
allowed_match = re.search(r'const allowedSkills\s*=\s*new Set\(\[(.*?)\]\)', knowledge, re.S)
required = re.findall(r'"([^"\n]+)"', required_match.group(1)) if required_match else []
allowed = re.findall(r'"([^"\n]+)"', allowed_match.group(1)) if allowed_match else []
if allowed_match and '...REQUIRED_SKILLS' in allowed_match.group(1):
    allowed = list(dict.fromkeys(allowed+required))
skill_files = [name for name in manifest['files'] if name.startswith('skills/')]
visible = [name for name in skill_files if name.split('/')[1] in allowed
           and name.endswith('.md') and not PurePosixPath(name).name.startswith('_')
           and not re.search('test-results|test-prompts',name)]
readme = f'''# 问衡服务器 Skill 包（只读拉取）

服务器来源：{manifest['source']}
实际网站版本：{manifest['release']}
拉取时间（UTC）：{manifest['pulledAtUtc']}

## 先看哪里

- `skills/`：从服务器原样下载的完整 skill 目录，共 {len(skill_files)} 个文件；没有改写、裁剪或替换为本机版本。
- `server-manifest.json`：服务器读取时计算的逐文件 SHA256、字节数与来源信息。下载后已逐一校验全部文件。
- `website-runtime/`：当前服务器部署的 knowledge.ts、runtime.ts、tools.ts，单独附上，便于检查网站读取范围、适配提示及工具约束。这些不是原始 skill 内容。

## 服务器存在，不代表网站全部开放

当前 knowledge.ts 白名单对应 {len(allowed)} 个 skill 目录，按当前加载过滤规则可供网站读取的 Markdown 共 {len(visible)} 个。

开放目录：{', '.join(allowed)}

必做技能：{', '.join(required)}

网站读取技能时还会添加 knowledge.ts 中的 prefix 适配提示；这个提示没有写入 skills/ 内的原文件。runtime.ts 和 tools.ts 也会影响实际执行。

本导出只证明服务器文件内容及传输完整性，不证明模型每次完整收到或正确执行了这些内容，也不证明与所有历史原版一致。此前审计发现主 daliuren 技能存在工具输出截断问题；原文件齐全与模型实际读全需要分别核查。

跳过的符号链接或特殊文件：{json.dumps(manifest['skippedSymlinksOrSpecialFiles'], ensure_ascii=False)}

未读取或打包服务器密钥、环境变量、数据库、账户或用户档案。
'''
(destination/'请先阅读.md').write_text(readme,encoding='utf-8-sig')
zip_path = destination.with_suffix('.zip')
with zipfile.ZipFile(zip_path,'x',zipfile.ZIP_DEFLATED) as out:
    for p in sorted(destination.rglob('*')):
        if p.is_file(): out.write(p,p.relative_to(destination).as_posix())
with zipfile.ZipFile(zip_path) as out:
    assert out.testzip() is None
    for name, expected in manifest['files'].items():
        assert hashlib.sha256(out.read(name)).hexdigest() == expected['sha256'], name
print(json.dumps({'folder':str(destination),'zip':str(zip_path),'skillFiles':len(skill_files),
                  'markdownFiles':sum(name.endswith('.md') for name in skill_files),
                  'skillDirectories':len(set(name.split('/')[1] for name in skill_files)),
                  'websiteVisibleMarkdown':len(visible),'verifiedFiles':len(manifest['files']),
                  'skipped':manifest['skippedSymlinksOrSpecialFiles'],'sha256Verified':True},ensure_ascii=False,indent=2))
