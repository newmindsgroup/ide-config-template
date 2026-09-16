# Version-Timestamp: 2026-09-16 15:20:39 AST
"""Public template preservation and privacy regressions."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('wizard', ROOT / 'scripts/ide-setup.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

class PreservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.home = self.root / 'home'; self.home.mkdir()
        self.workspace = self.root / 'project'; self.workspace.mkdir()
        p=self.root/'profile.json';p.write_text(json.dumps({'ides':['codex','claude','cursor'],'name':'Example'}))
        self.profile=w.read_profile(p,False)
        machine={'platform':'test','architecture':'test','ram_gb':16,'free_disk_gb':30,'tools':{},'recommended_local_tier':'none'}
        self.plan=w.make_plan(self.profile,machine,'general')
    def tearDown(self): self.tmp.cleanup()
    def test_exact_user_bytes_survive_apply_and_remove(self):
        p=self.home/'.codex/AGENTS.md';p.parent.mkdir();original=b'\r\n# User\r\n\r\n\r\nNo trailing newline';p.write_bytes(original)
        w.apply(self.profile,self.plan,self.home,self.workspace)
        w.remove_managed_blocks(self.profile,self.home,self.workspace)
        self.assertEqual(p.read_bytes(),original)
    def test_bad_marker_in_later_target_prevents_every_write(self):
        p=self.home/'.claude/CLAUDE.md';p.parent.mkdir();p.write_text(w.MARKER_START+'\nunfinished')
        with self.assertRaises(ValueError): w.apply(self.profile,self.plan,self.home,self.workspace)
        self.assertFalse((self.home/'.ide-config').exists());self.assertFalse((self.home/'.codex').exists())
    def test_unmanaged_cursor_collision_is_not_overwritten(self):
        p=self.workspace/'.cursor/rules/ide-config-template.mdc';p.parent.mkdir(parents=True);p.write_text('My existing rule')
        with self.assertRaises(ValueError):w.apply(self.profile,self.plan,self.home,self.workspace)
        self.assertEqual(p.read_text(),'My existing rule');self.assertFalse((self.home/'.ide-config').exists())
    def test_cursor_user_suffix_and_frontmatter_survive_update(self):
        w.apply(self.profile,self.plan,self.home,self.workspace)
        p=self.workspace/'.cursor/rules/ide-config-template.mdc';p.write_bytes(p.read_bytes()+b'\nCustom suffix\n')
        before=p.read_bytes();w.apply(self.profile,self.plan,self.home,self.workspace)
        self.assertEqual(p.read_bytes(),before)
    def test_symlink_ancestor_rejected(self):
        external=self.root/'outside';external.mkdir()
        try:(self.home/'.codex').symlink_to(external,target_is_directory=True)
        except OSError:self.skipTest('Symlink creation unavailable')
        with self.assertRaises(ValueError):w.apply(self.profile,self.plan,self.home,self.workspace)
        self.assertEqual(list(external.iterdir()),[]);self.assertFalse((self.home/'.ide-config').exists())
    def test_profile_cannot_inject_managed_markers(self):
        p=self.root/'bad.json';p.write_text(json.dumps({'name':w.MARKER_END}))
        with self.assertRaises(ValueError):w.read_profile(p,False)
    def test_profile_rejects_non_schema_version(self):
        for value in [True,2,{},[]]:
            p=self.root/'bad.json';p.write_text(json.dumps({'schema_version':value}))
            with self.assertRaises(ValueError):w.read_profile(p,False)
    def test_failed_apply_rolls_back_existing_files(self):
        p=self.home/'.codex/AGENTS.md';p.parent.mkdir();p.write_bytes(b'original')
        real=w.atomic_write
        def fail(path,data,mode):
            if path.name=='CLAUDE.md':raise OSError('synthetic disk failure')
            return real(path,data,mode)
        with patch.object(w,'atomic_write',side_effect=fail):
            with self.assertRaises(OSError):w.apply(self.profile,self.plan,self.home,self.workspace)
        self.assertEqual(p.read_bytes(),b'original');self.assertFalse((self.home/'.ide-config/profile.local.json').exists())
    def test_remove_preflights_all_targets(self):
        w.apply(self.profile,self.plan,self.home,self.workspace)
        p=self.home/'.codex/AGENTS.md';before=p.read_bytes()
        (self.home/'.claude/CLAUDE.md').write_text(w.MARKER_END+'\n'+w.MARKER_START)
        with self.assertRaises(ValueError):w.remove_managed_blocks(self.profile,self.home,self.workspace)
        self.assertEqual(p.read_bytes(),before)
    def test_end_marker_must_start_its_own_line(self):
        with self.assertRaises(ValueError):
            w.marker_span(w.MARKER_START+'\nuser text '+w.MARKER_END+'\n')
    def test_anchor_rejects_ancestor_link(self):
        real=self.root/'real';real.mkdir();link=self.root/'link'
        try:link.symlink_to(real,target_is_directory=True)
        except OSError:self.skipTest('Symlink creation unavailable')
        with self.assertRaises(ValueError):w.anchor(link/'home')
    def test_unrelated_app_settings_are_untouched(self):
        files=[self.home/'.codex/config.toml',self.home/'.claude/settings.json',self.workspace/'.cursor/settings.json']
        for p in files:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'original settings')
        w.apply(self.profile,self.plan,self.home,self.workspace)
        for p in files:self.assertEqual(p.read_bytes(),b'original settings')
    def test_duplicate_marker_is_rejected(self):
        with self.assertRaises(ValueError):w.marker_span((w.MARKER_START+'\n'+w.MARKER_END+'\n')*2)
    def test_broken_file_link_is_rejected(self):
        p=self.home/'.codex/AGENTS.md';p.parent.mkdir()
        try:p.symlink_to(self.root/'missing')
        except OSError:self.skipTest('Symlink creation unavailable')
        with self.assertRaises(ValueError):w.apply(self.profile,self.plan,self.home,self.workspace)
        self.assertFalse((self.home/'.ide-config').exists())
    def test_hardlink_is_rejected(self):
        import os
        source=self.root/'source';source.write_text('original')
        p=self.home/'.codex/AGENTS.md';p.parent.mkdir()
        try:os.link(source,p)
        except OSError:self.skipTest('Hardlink creation unavailable')
        with self.assertRaises(ValueError):w.apply(self.profile,self.plan,self.home,self.workspace)
        self.assertEqual(source.read_text(),'original')
    def test_backup_permissions_and_manifest(self):
        import os,stat
        p=self.home/'.codex/AGENTS.md';p.parent.mkdir();p.write_bytes(b'original')
        w.apply(self.profile,self.plan,self.home,self.workspace)
        run=next((self.home/'.ide-config/backups').iterdir())
        manifest=json.loads((run/'manifest.json').read_text())
        record=next(x for x in manifest['files'] if x['path']==str(p))
        self.assertEqual((run/record['backup']).read_bytes(),b'original')
        if os.name != 'nt':
            self.assertEqual(stat.S_IMODE(run.stat().st_mode),0o700)
            self.assertEqual(stat.S_IMODE((run/record['backup']).stat().st_mode),0o600)
    def test_inert_settings_and_no_bundled_private_skills(self):
        s=json.loads((ROOT/'settings.json').read_text())
        self.assertFalse(s.get('hooks'));self.assertEqual(s.get('permissions',{}).get('allow',[]),[])
        self.assertEqual(list((ROOT/'skills').rglob('SKILL.md')),[])

if __name__=='__main__':unittest.main()
