"""Guarded rollback to the saved parent. Default is read-only; never delete runtime."""
from pathlib import Path
import argparse,hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--apply',action='store_true')
 parser.add_argument('--include-installed',action='store_true',help='Also restore the two synced files outside the workspace; requires filesystem permission')
 args=parser.parse_args();b=load(O/'before.json');a=load(O/'after.json')
 def local(f):
  path=(R/f).resolve();assert path.is_relative_to(R.resolve()),'Path escapes workspace';return path
 assert load(R/'.opencode/liuren-active.json')['release']==a['release'],'Active release changed'
 for f,h in b['files'].items():
  assert sha(O/'before'/f)==h,'Backup changed: '+f
  assert sha(local(f))==a['files'][f],'Refuse to overwrite later edit: '+f
 for f,h in a['new_file_hashes'].items():assert sha(local(f))==h,'New file changed: '+f
 for f,h in b['frozen'].items():assert sha(local(f))==h,'Parent changed: '+f
 installed=Path.home()/'.codex/skills/daliuren-codex'
 external=['SKILL.md','references/host.md']
 for f in external:
  assert (installed/f).read_bytes()==(R/'integrations/codex/daliuren-codex'/f).read_bytes(),'Installed skill changed: '+f
  assert (O/'installed-skill-before'/f).is_file()
 result={'dry_run':not args.apply,'restore_release':b['release'],'restore_files':len(b['files']),
  'remove_only_unchanged_new_tests':list(a['new_file_hashes']),
  'preserve_new_runtime':a['runtime'],'installed_files':external,
  'external_write_permission_required':True}
 print(json.dumps(result,ensure_ascii=False,indent=2))
 if not args.apply:return
 if not args.include_installed:raise SystemExit('Use --include-installed for a consistent rollback; the installed skill also needs restoring. No files changed.')
 # Restore external files first, so a denied external write leaves workspace intact.
 for f in external:shutil.copyfile(O/'installed-skill-before'/f,installed/f)
 pointer='.opencode/liuren-active.json'
 for f in b['files']:
  if f!=pointer:shutil.copyfile(O/'before'/f,local(f))
 for f in a['new_file_hashes']:local(f).unlink()
 shutil.copyfile(O/'before'/pointer,local(pointer))
 print('Restored parent; keep the 52 runtime and audit records for traceability. Restart OpenCode before new tasks.')
if __name__=='__main__':main()
