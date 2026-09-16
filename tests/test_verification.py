# Version-Timestamp: 2026-09-16 16:02:15 AST
"""Portable verification dispatch and structural regression checks."""
import importlib.util
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('template_verifier', ROOT / 'scripts' / 'verify.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class Verification(unittest.TestCase):
    def test_spine_requires_sections_inside_ordered_markers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            headings = '\n'.join('### ' + name for name in verifier.REQUIRED_SECTIONS)
            for text in (
                '<!-- SPINE:END -->\n' + headings + '\n<!-- SPINE:START -->\n',
                headings + '\n<!-- SPINE:START -->\n<!-- SPINE:END -->\n',
                '<!-- SPINE:START -->\n' + headings + '\n<!-- SPINE:END -->\n<!-- SPINE:END -->\n',
            ):
                (root / 'AGENTS.md').write_text(text, encoding='utf-8')
                with self.assertRaises(ValueError):
                    verifier.check_spine(root)
            (root / 'AGENTS.md').write_text('<!-- SPINE:START -->\n' + headings
                                          + '\n<!-- SPINE:END -->\n', encoding='utf-8')
            verifier.check_spine(root)

    def test_new_test_scripts_are_automatically_included(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tests').mkdir()
            for name in ('test_z.py', 'helper.py', 'test_a.py'):
                (root / 'tests' / name).write_text('', encoding='utf-8')
            commands = verifier.test_commands(root)
            self.assertEqual([Path(command[1]).name for command in commands], ['test_a.py', 'test_z.py'])
            self.assertTrue(all(command[0] == sys.executable for command in commands))

    def test_failures_propagate_and_windows_never_invokes_bash(self):
        with patch.object(verifier, 'check_spine'), patch.object(verifier, 'compile_sources'), \
             patch.object(verifier, 'test_commands', return_value=[['python', 'test_placeholder.py']]), \
             patch.object(verifier.sys, 'platform', 'win32'), \
             patch.object(verifier.shutil, 'which') as which, \
             patch.object(verifier.subprocess, 'run', return_value=subprocess.CompletedProcess([], 7)) as run:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(verifier.main(), 7)
            which.assert_not_called()
            self.assertEqual(run.call_count, 1)

    def test_syntax_compilation_does_not_create_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            (root / 'scripts' / 'simple.py').write_text('print("valid")\n', encoding='utf-8')
            verifier.compile_sources(root)
            self.assertFalse((root / 'scripts' / '__pycache__').exists())
            (root / 'scripts' / 'simple.py').write_text('def broken(\n', encoding='utf-8')
            with self.assertRaises(SyntaxError):
                verifier.compile_sources(root)


if __name__ == '__main__':
    unittest.main()
