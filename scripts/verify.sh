#!/usr/bin/env bash
# Verify the public setup wizard and portable instruction template.
# Version-Timestamp: 2026-09-16 15:27:25 AST

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m compileall -q "$ROOT/scripts" "$ROOT/tests"
python3 "$ROOT/scripts/check-public-content.py"
python3 "$ROOT/tests/test_ide_setup.py"
python3 "$ROOT/tests/test_safe_setup.py"
python3 "$ROOT/tests/test_update_helpers.py"
bash -n "$ROOT/bootstrap.sh" "$ROOT/update.sh"

start="$(grep -c '^<!-- SPINE:START' "$ROOT/AGENTS.md" || true)"
end="$(grep -c '^<!-- SPINE:END' "$ROOT/AGENTS.md" || true)"
[ "$start" = "1" ] && [ "$end" = "1" ] || {
  echo "ERROR - AGENTS.md must contain one balanced SPINE marker pair." >&2
  exit 1
}

echo "OK - public template verification complete"
