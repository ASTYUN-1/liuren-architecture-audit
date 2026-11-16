"""Update obsolete live assumptions; preserve frozen compatibility coverage."""
from pathlib import Path
import json, shutil, hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
path=O/'before.json';b=json.loads(path.read_text('utf-8'))
names=['test_liuren_class_mapping.py','test_liuren_local_read.py','test_liuren_plan_transport.py','test_liuren_quantity_candidate.py']
for name in names:
 f='tools/tests/'+name
 if f not in b['files']:
  dest=O/'before'/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/f,dest)
  b['files'][f]=hashlib.sha256(dest.read_bytes()).hexdigest()
path.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def edit(name, old, new):
 p=R/'tools/tests'/name;s=p.read_text('utf-8');assert old in s,(name,old[:90]);p.write_text(s.replace(old,new),encoding='utf-8')
edit(names[0],"""            for core in ['liqi','void','structure']:
                self.assertEqual(next(s['stage'] for s in steps if s['id']==core),1)
                if core=='void':self.assertLess(keys.index(domain),keys.index(core))
                self.assertEqual(keys.count(core),1)
            self.assertLess(keys.index('shenjiang-use'),keys.index('positioning'))
            self.assertLess(keys.index('movement'),keys.index('adjudication'))""","""            for core in ['judgment-core','liqi','shenjiang-use',domain]:
                self.assertEqual(next(s['stage'] for s in steps if s['id']==core),1)
                self.assertEqual(keys.count(core),1)
            self.assertLess(keys.index('judgment-core'),keys.index(domain))
            for optional in ['void','structure','positioning','movement']:
                self.assertNotIn(optional,keys)
            self.assertEqual(keys[-2:],['adjudication','report'])""")
edit(names[0],"""                self.assertLess(keys.index('positioning'),keys.index(domain))
                self.assertLess(keys.index(domain),keys.index('liqi'))""","""                self.assertEqual(keys,['judgment-core',domain,'adjudication','report'])""")
edit(names[0],"            self.assertLess(keys.index(key),keys.index('positioning'))","            self.assertLess(keys.index(key),keys.index('adjudication'))\n        self.assertNotIn('positioning',keys)")
edit(names[1],"        self.assertIn('shensha-use', expected)","""        self.assertNotIn('shensha-use', expected)
        explicit = reader.method_batches(runtime, manifest, ['lost-person-object'], conditions=['shensha-use'])
        self.assertIn('shensha-use', {row['module'] for group in explicit for row in group})""")
edit(names[1],"        with patch.object(cases, 'ensure_index',", "        with patch.object(reader, 'require_case_experience', return_value=None), \\\n+             patch.object(cases, 'ensure_index',")
edit(names[1],"\n\nif __name__ == '__main__':", """
    def test_current_entry_blocks_both_libraries_before_retrieval(self):
        import case_retrieval as cases
        import experience_retrieval as experience
        with patch.object(cases, 'retrieve') as cr, patch.object(experience, 'retrieve') as er:
            with self.assertRaisesRegex(ValueError, 'LIUREN_EXPERIMENT_NO_RETRIEVAL'):
                reader.parallel_search('synthetic', 'synthetic', '失物占')
        cr.assert_not_called()
        er.assert_not_called()


if __name__ == '__main__':""")
# Ensure the transport fixture has three batches without restoring forced reading.
p=R/'tools/tests'/names[2];s=p.read_text('utf-8');a=s.index('    def test_missing_batch_');z=s.index('\n    def test_changed_route_',a)
block=s[a:z].replace("        first=cli", "        options=('--condition','liqi','--condition','void','--condition','structure')\n        first=cli",1).replace("cli('--domain','illness',", "cli(*options,'--domain','illness',")
s=s[:a]+block+s[z:];p.write_text(s,encoding='utf-8')
edit(names[3],"import json\n", "import json\nimport shutil\n")
edit(names[3],"        candidate.verify()\n", "        # Frozen candidate checks must not invoke historical live activation or write old evidence.\n")
p=R/'tools/tests'/names[3];s=p.read_text('utf-8');a=s.index('        _, active = loader.active()');z=s.index("        proc = subprocess.run",a)
s=s[:a]+"""        temporary = tempfile.TemporaryDirectory(prefix='liuren-frozen-quantity-')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        shutil.copytree(candidate.PACKAGE, root/'runtime/candidate')
        (root/'.opencode').mkdir()
        candidate.dump(root/'.opencode/liuren-active.json', dict(release=candidate.RELEASE,
            runtime='runtime/candidate', methodVersion=self.manifest['version']))
        script = ROOT/'tools/load-liuren-methods.py'
        command = [sys.executable, '-X', 'utf8', str(script), '--root', str(root)]
"""+s[z:]
s=s.replace("[sys.executable, '-X', 'utf8', str(script), 'plan',", "[*command, 'plan',").replace("[sys.executable, '-X', 'utf8', str(script), 'read',", "[*command, 'read',")
a=s.index("        candidate.dump(candidate.OUT / 'page-roundtrip.json'");z=s.index('\n    def test_condition_',a)
s=s[:a]+"        self.assertGreater(len(receipts),0)\n"+s[z:]
a=s.index("        if active['release'] == candidate.PARENT:");z=s.index('\n    def test_candidate_pointer',a)
s=s[:a]+"""        selected = loader.plan(active, extras=['quantity-sources'])
        self.assertLess(selected.index('quantity'), selected.index('quantity-sources'))
        self.assertLess(selected.index('quantity-sources'), selected.index('report'))
"""+s[z:]
a=s.index("        candidate.dump(candidate.OUT / 'evidence-roundtrip.json'");z=s.index("\n\n\nif __name__",a)
s=s[:a]+"        self.assertEqual(len(rows),50)"+s[z:]
s=s.replace('test_condition_selection_is_explicit_and_live_release_matches_activation','test_frozen_and_live_quantity_routes_keep_explicit_selection')
p.write_text(s,encoding='utf-8')
print('Updated legacy tests without changing production policy or historical evidence')
