#!/usr/bin/env python3
# Version-Timestamp: 2026-09-16 15:27:25 AST
"""Check publishable files for prohibited paths and recognizable secret patterns.

This limited regression check does not replace staged-diff or history review.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BLOCKED_PARTS = {'.codex', '.claude', '.cursor', '.ide-config', 'projects', 'sessions', 'transcripts'}
BLOCKED_NAMES = {'auth.json', 'credentials.json', 'profile.json'}
PATTERNS = [
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
    re.compile(rb'\bAKIA[A-Z0-9]{16}\b'),
    re.compile(rb'\bsk-[A-Za-z0-9_-]{32,}\b'),
    re.compile(rb'/Users/[A-Za-z0-9._-]+/'),
]

def main():
    result = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT, capture_output=True, check=True)
    failures = []
    for name in set(result.stdout.decode('utf-8').split('\0')) - {''}:
        path = ROOT / name
        parts = Path(name).parts
        if path.is_symlink():
            failures.append(name + ': symlink is not allowed in the public distribution')
            continue
        if not path.is_file():
            continue  # A staged/tracked deletion is not published as content.
        if (BLOCKED_PARTS.intersection(parts) or path.name in BLOCKED_NAMES
                or path.name.endswith(('.local.json', '.pem', '.key', '.p12', '.pfx'))
                or (path.name.startswith('.env') and path.name not in ('.env.example', '.env.sample'))):
            failures.append(name + ': private/runtime path')
        data = path.read_bytes()
        if any(pattern.search(data) for pattern in PATTERNS):
            failures.append(name + ': potential credential or personal machine path')
    for failure in sorted(failures):
        print('ERROR - ' + failure, file=sys.stderr)  # Never print matching secret text.
    if failures:
        return 1
    print('OK - limited public-content checks passed; human privacy review still required')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
