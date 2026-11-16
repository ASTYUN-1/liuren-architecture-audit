"""Guarded rollback. Default is dry-run; preserves the new runtime and evidence."""
from pathlib import Path
import json,hashlib,shutil,argparse
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');parser.add_argument('--include-installed',action='store_true');args=parser.parse_args()
 b=load(O/'before.json');a=load(O/'after.json');assert load(R/'.opencode/liuren-active.json')['release']==a['release']
 def local(f):
  v=(R/f).resolve();assert v.is_relative_to(R.resolve());return v
 for f,h in b['files'].items():assert sha(O/'before'/f)==h and sha(local(f))==a['files'][f],f
 for f,h in a['new_file_hashes'].items():assert sha(local(f))==h,f
 for f,h in b['frozen'].items():assert sha(local(f))==h,f
 installed=Path.home()/'.codex/skills/daliuren-codex/SKILL.md'
 assert sha(installed)==a['installed_skill_sha256']
 assert sha(O/'installed-skill-before/SKILL.md')==b['files']['integrations/codex/daliuren-codex/SKILL.md']
 print(json.dumps({'dry_run':not args.apply,'restore_release':b['release'],'restore_files':len(b['files']),'preserve_runtime':a['runtime'],'restore_installed_skill':True},ensure_ascii=False,indent=2))
 if not args.apply:return
 if not args.include_installed:raise SystemExit('须同时--include-installed恢复已安装技能；需要该路径写权限。尚未改动任何文件。')
 shutil.copyfile(O/'installed-skill-before/SKILL.md',installed)
 pointer='.opencode/liuren-active.json'
 for f in b['files']:
  if f!=pointer:shutil.copyfile(O/'before'/f,local(f))
 for f in a['new_file_hashes']:local(f).unlink()
 shutil.copyfile(O/'before'/pointer,local(pointer))
 print('Restored 52; restart OpenCode before new tasks. New runtime and audit evidence retained.')
if __name__=='__main__':main()
