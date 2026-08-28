#!/usr/bin/env bash
# Verify the public setup wizard and portable instruction template.
# Version-Timestamp: 2026-08-28 10:00:00 AST

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m py_compile "$ROOT/scripts/ide-setup.py" "$ROOT/tests/test_ide_setup.py"
python3 "$ROOT/tests/test_ide_setup.py"

start="$(grep -c '^<!-- SPINE:START' "$ROOT/AGENTS.md" || true)"
end="$(grep -c '^<!-- SPINE:END' "$ROOT/AGENTS.md" || true)"
[ "$start" = "1" ] && [ "$end" = "1" ] || {
  echo "ERROR - AGENTS.md must contain one balanced SPINE marker pair." >&2
  exit 1
}

echo "OK - public template verification complete"
