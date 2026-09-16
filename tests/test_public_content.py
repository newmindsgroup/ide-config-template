# Version-Timestamp: 2026-09-16 16:02:15 AST
"""The public package checks work without Git and never print matching secrets."""
import contextlib
import io
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('public_check', ROOT/'scripts/check-public-content.py')
c=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(c)
class PublicContent(unittest.TestCase):
    def test_source_archive_scan(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'README.md').write_text('public documentation')
            with patch.object(c,'ROOT',root):self.assertEqual(c.main(),0)
    def test_source_archive_blocks_runtime_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'.claude').mkdir();(root/'.claude/auth.json').write_text('{}')
            with patch.object(c,'ROOT',root),contextlib.redirect_stderr(io.StringIO()):self.assertEqual(c.main(),1)
    def test_recognizes_additional_token_and_personal_path_formats(self):
        samples=[b'github_'+b'pat_'+b'x'*80, b'/home/'+b'example/private', b'C:\\Users\\'+b'example\\private']
        for sample in samples:self.assertTrue(any(p.search(sample) for p in c.PATTERNS))
if __name__=='__main__':unittest.main()
