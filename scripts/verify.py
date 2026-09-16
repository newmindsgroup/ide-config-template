#!/usr/bin/env python3
# Version-Timestamp: 2026-09-16 16:02:15 AST
"""Verify a checkout or source archive using Python 3.10+ on all supported OSes."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SECTIONS = (
    'Skill & Command Leverage Protocol',
    'Qualifying Questions Protocol',
    'Engineering Mantra',
    'Proportional Rigor',
    'Attribution & Versioned Outputs',
    'Third-Party Component Trust',
    'Data Handling',
    'Truthfulness & Escalation',
    'Look Around the Corner',
    'Skill-Worthiness Radar',
    'Next Steps & Sequenced Building',
)


def check_spine(root):
    text = (root / 'AGENTS.md').read_text(encoding='utf-8')
    starts = list(re.finditer(r'^<!-- SPINE:START[^\r\n]*-->\s*$', text, re.MULTILINE))
    ends = list(re.finditer(r'^<!-- SPINE:END[^\r\n]*-->\s*$', text, re.MULTILINE))
    if (text.count('<!-- SPINE:START') != 1 or text.count('<!-- SPINE:END') != 1
            or len(starts) != 1 or len(ends) != 1 or starts[0].end() > ends[0].start()):
        raise ValueError('AGENTS.md must contain exactly one ordered, complete SPINE marker pair')
    spine = text[starts[0].end():ends[0].start()]
    headings = re.findall(r'^###\s+(.+)$', spine, re.MULTILINE)
    missing = [name for name in REQUIRED_SECTIONS if not any(name in heading for heading in headings)]
    if missing:
        raise ValueError('Required spine headings missing: ' + ', '.join(missing))
    print('OK - ordered spine markers and all required headings', flush=True)


def python_sources(root):
    return sorted(path for folder in ('scripts', 'tests')
                  for path in (root / folder).rglob('*.py') if '__pycache__' not in path.parts)


def compile_sources(root):
    # compile() validates syntax without creating caches in a source archive.
    sources = python_sources(root)
    if not sources:
        raise ValueError('No Python source files found')
    for path in sources:
        compile(path.read_bytes(), str(path), 'exec')
    print(f'OK - compiled {len(sources)} Python source files without writing caches', flush=True)


def test_commands(root):
    tests = sorted((root / 'tests').glob('test_*.py'))
    if not tests:
        raise ValueError('No test scripts found')
    return [[sys.executable, str(path)] for path in tests]


def main(root=ROOT):
    try:
        if sys.version_info < (3, 10):
            raise ValueError('Python 3.10 or newer is required')
        check_spine(root)
        compile_sources(root)
        commands = [[sys.executable, str(root / 'scripts' / 'check-public-content.py')]]
        commands.extend(test_commands(root))
        # A Windows bash executable may launch WSL. The native Python workflow
        # does not depend on WSL or Git Bash; Unix CI covers optional shell helpers.
        bash = shutil.which('bash') if sys.platform != 'win32' else None
        if bash:
            commands.extend([bash, '-n', str(root / name)]
                            for name in ('bootstrap.sh', 'update.sh', 'scripts/verify.sh'))
        else:
            print('SKIP - optional Bash helpers (not required for native Python setup)', flush=True)
        for command in commands:
            print('RUN - ' + ' '.join(command), flush=True)
            result = subprocess.run(command, cwd=root, check=False,
                                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            if result.returncode:
                print(f'ERROR - check failed with exit status {result.returncode}', file=sys.stderr)
                return result.returncode if result.returncode > 0 else 1
    except (OSError, SyntaxError, ValueError) as exc:
        print('ERROR - ' + str(exc), file=sys.stderr)
        return 1
    print('OK - public template verification complete', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
