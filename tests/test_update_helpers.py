# Version-Timestamp: 2026-09-16 15:20:39 AST
"""Update helpers must preview, preserve and refuse ambiguous destinations."""
from pathlib import Path
import subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
class Updates(unittest.TestCase):
 def test_spine_preview_apply_and_malformed_refusal(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d).resolve();source=root/'source.md';target=root/'AGENTS.md'
   source.write_text('<!-- SPINE:START -->\nnew rules\n<!-- SPINE:END -->\n')
   original='Profile\r\n<!-- SPINE:START -->\r\nold rules\r\n<!-- SPINE:END -->\r\nSuffix\r\n';target.write_bytes(original.encode())
   cmd=[sys.executable,str(ROOT/'scripts/update-spine.py'),'--source',str(source),'--target',str(target)]
   r=subprocess.run(cmd,capture_output=True);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(target.read_bytes(),original.encode())
   r=subprocess.run(cmd+['--apply','--confirm'],capture_output=True);self.assertEqual(r.returncode,0,r.stderr)
   self.assertTrue(target.read_bytes().startswith(b'Profile\r\n'));self.assertTrue(target.read_bytes().endswith(b'Suffix\r\n'))
   source.write_text('<!-- SPINE:START -->\nbad')
   before=target.read_bytes();r=subprocess.run(cmd+['--apply','--confirm'],capture_output=True);self.assertNotEqual(r.returncode,0);self.assertEqual(target.read_bytes(),before)
 @unittest.skipIf(sys.platform=='win32','Bash helper is optional on Windows')
 def test_bootstrap_refuses_existing_and_normalized_config_paths(self):
  import os
  with tempfile.TemporaryDirectory() as d:
   home=Path(d).resolve();existing=home/'existing';existing.mkdir();(existing/'keep').write_text('keep')
   for destination in [existing,home/'x/../.claude',home/'.codex/child']:
    result=subprocess.run(['bash',str(ROOT/'bootstrap.sh'),'invalid-offline-source',str(destination)],env={**os.environ,'HOME':str(home)},capture_output=True)
    self.assertEqual(result.returncode in (1,2),True,result.stderr)
    self.assertNotIn(b'Cloning into',result.stderr)
   self.assertEqual((existing/'keep').read_text(),'keep');self.assertFalse((home/'.claude').exists())
 def test_public_catalog_has_no_candidates(self):
  import json
  c=json.loads((ROOT/'approved-skills.json').read_text());entries={x['name']:x for x in c['skills']}
  for names in c['roles'].values():
   for name in names:self.assertEqual(entries[name]['status'],'approved-for-scoped-use')
  self.assertNotIn('financial-reporting',entries);self.assertNotIn('vendor-negotiation-prep',entries)
if __name__=='__main__':unittest.main()
