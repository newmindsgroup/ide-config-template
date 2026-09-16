# Version-Timestamp: 2026-09-16 16:02:15 AST
"""Regression coverage for multiple computers, profiles and workspaces."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('wizard', ROOT / 'scripts/ide-setup.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve()
        self.profile_file = self.home / 'input.json'
        self.profile_file.write_text(json.dumps({'ides':['codex','claude','cursor']}))
        self.profile = w.read_profile(self.profile_file, False)
        self.machine = {'platform':'test','architecture':'test','ram_gb':16,'free_disk_gb':25,'tools':{},'recommended_local_tier':'none'}
    def tearDown(self):
        self.tmp.cleanup()
    def plan(self):
        return w.make_plan(self.profile, self.machine, 'general')
    def cli(self, *args):
        return subprocess.run([sys.executable,str(ROOT/'scripts/ide-setup.py'),'--home',str(self.home),'--profile',str(self.profile_file),*args],capture_output=True,text=True)
    def test_deselected_app_still_removed(self):
        w.apply(self.profile,self.plan(),self.home,None)
        self.profile['ides']=['codex']
        w.apply(self.profile,self.plan(),self.home,None)
        w.remove_managed_blocks(self.profile,self.home,None)
        self.assertNotIn(w.MARKER_START,(self.home/'.claude/CLAUDE.md').read_text())
    def test_multiple_cursor_workspaces_tracked(self):
        for name in ['one','two']:
            w.apply(self.profile,self.plan(),self.home,self.home/name)
        w.remove_managed_blocks(self.profile,self.home,None)
        for name in ['one','two']:
            self.assertNotIn(w.MARKER_START,(self.home/name/'.cursor/rules/ide-config-template.mdc').read_text())
    def test_custom_app_paths_and_preview(self):
        destination=self.home/'custom-codex'
        result=self.cli('--plan','--codex-home',str(destination))
        self.assertEqual(result.returncode,0,result.stderr)
        preview=json.loads(result.stdout)
        self.assertIn(str(destination/'AGENTS.md'),preview['planned_files'])
        self.assertTrue(preview['changes'])
        self.assertEqual(len(preview['plan_sha256']),64)
        self.assertFalse(destination.exists())
    def test_preview_hash_blocks_changed_input(self):
        result=self.cli('--plan');self.assertEqual(result.returncode,0,result.stderr)
        preview=json.loads(result.stdout)
        self.assertIn('plan_sha256',preview)
        self.profile_file.write_text(json.dumps({'ides':['claude'],'name':'changed'}))
        result=self.cli('--apply','--confirm','--expect-plan-sha256',preview['plan_sha256'])
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.home/'.ide-config').exists())
    def test_corrupt_registry_blocks_removal(self):
        w.apply(self.profile,self.plan(),self.home,None)
        before=(self.home/'.codex/AGENTS.md').read_bytes()
        (self.home/'.ide-config/installations.json').write_text('{bad')
        with self.assertRaises(ValueError):w.remove_managed_blocks(self.profile,self.home,None)
        self.assertEqual((self.home/'.codex/AGENTS.md').read_bytes(),before)
    def test_environment_paths_use_current_home_only(self):
        custom=self.home/'from-env'
        with patch.dict(os.environ,{'CODEX_HOME':str(custom)}),patch.object(w.Path,'home',return_value=self.home):
            targets=w.instruction_targets(self.profile,self.home,None)
            self.assertIn((custom/'AGENTS.md',False),targets)
    def test_legacy_backup_adoption(self):
        workspace=self.home/'legacy-project'
        w.apply(self.profile,self.plan(),self.home,workspace)
        (self.home/'.ide-config/installations.json').unlink(missing_ok=True)
        self.profile['ides']=['codex']
        w.remove_managed_blocks(self.profile,self.home,None)
        self.assertNotIn(w.MARKER_START,(workspace/'.cursor/rules/ide-config-template.mdc').read_text())

    def test_approval_hash_accepts_exact_plan_and_remove(self):
        preview=json.loads(self.cli('--plan').stdout)
        result=self.cli('--apply','--confirm','--expect-plan-sha256',preview['plan_sha256'])
        self.assertEqual(result.returncode,0,result.stderr)
        preview=json.loads(self.cli('--plan-remove').stdout)
        self.assertEqual(preview['operation'],'remove')
        result=self.cli('--remove-managed-block','--confirm','--expect-plan-sha256',preview['plan_sha256'])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertNotIn(w.MARKER_START,(self.home/'.codex/AGENTS.md').read_text())
    def test_registry_write_failure_restores_instructions_and_state(self):
        w.apply(self.profile,self.plan(),self.home,None)
        registry=self.home/'.ide-config/installations.json';before=registry.read_bytes()
        instruction=self.home/'.codex/AGENTS.md';original=instruction.read_bytes()
        self.profile['name']='new name'
        real=w.atomic_write
        def fail(path,data,mode):
            if path==registry:raise OSError('synthetic registry failure')
            return real(path,data,mode)
        # Add a workspace so the registry itself changes.
        with patch.object(w,'atomic_write',side_effect=fail):
            with self.assertRaises(OSError):w.apply(self.profile,self.plan(),self.home,self.home/'project')
        self.assertEqual(registry.read_bytes(),before)
        self.assertEqual(instruction.read_bytes(),original)
    def test_explicit_cli_home_ignores_environment(self):
        with patch.dict(os.environ,{'CODEX_HOME':str(self.home/'unwanted')}):
            result=self.cli('--plan')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn(str(self.home/'.codex/AGENTS.md'),json.loads(result.stdout)['planned_files'])
    def test_registry_rejects_arbitrary_filename(self):
        w.apply(self.profile,self.plan(),self.home,None)
        registry=self.home/'.ide-config/installations.json'
        value=json.loads(registry.read_text());value['destinations'][0]['path']=str(self.home/'settings.json')
        registry.write_text(json.dumps(value))
        with self.assertRaises(ValueError):w.remove_managed_blocks(self.profile,self.home,None)
    def test_cursor_can_be_reinstalled_after_removal(self):
        workspace=self.home/'project'
        w.apply(self.profile,self.plan(),self.home,workspace)
        w.remove_managed_blocks(self.profile,self.home,workspace)
        w.apply(self.profile,self.plan(),self.home,workspace)
        self.assertIn(w.MARKER_START,(workspace/'.cursor/rules/ide-config-template.mdc').read_text())

    def test_copied_registry_refuses_different_home(self):
        import shutil
        w.apply(self.profile,self.plan(),self.home,None)
        other=self.home/'other-computer';(other/'.ide-config').mkdir(parents=True)
        shutil.copyfile(self.home/'.ide-config/installations.json',other/'.ide-config/installations.json')
        with self.assertRaises(ValueError):w.remove_managed_blocks(self.profile,other,None)

    def test_custom_override_works_with_unused_default_symlink(self):
        elsewhere=self.home/'elsewhere';elsewhere.mkdir()
        try:(self.home/'.codex').symlink_to(elsewhere,target_is_directory=True)
        except OSError:self.skipTest('Symlinks unavailable')
        result=self.cli('--plan','--codex-home',str(self.home/'custom'))
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(list(elsewhere.iterdir()),[])
    def test_status_ignores_unrelated_environment(self):
        with patch.dict(os.environ,{'CODEX_HOME':'relative-bad-path','HOME':str(self.home),'USERPROFILE':str(self.home)}):
            result=subprocess.run([sys.executable,str(ROOT/'scripts/ide-setup.py'),'--status'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()
