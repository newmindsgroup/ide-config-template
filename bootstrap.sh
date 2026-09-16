#!/usr/bin/env bash
# Version-Timestamp: 2026-09-16 15:20:39 AST
# Clone source outside live IDE configuration. Never update an existing target.
set -euo pipefail
repo="${1:-https://github.com/newmindsgroup/ide-config-template.git}"
destination="${2:-$HOME/code/ide-config-template}"
if [[ -e "$destination" || -L "$destination" ]]; then
  echo "ERROR - destination exists. Review that checkout manually or select an empty source directory." >&2
  exit 2
fi
python3 - "$destination" "$HOME" <<'PYTHON'
from pathlib import Path
import sys
path = Path(sys.argv[1]).expanduser().resolve()
home = Path(sys.argv[2]).resolve()
for name in (".claude", ".codex", ".cursor", ".gemini"):
    forbidden = (home / name).resolve()
    if path == forbidden or forbidden in path.parents:
        raise SystemExit("ERROR - choose a source directory outside live IDE configuration")
PYTHON
git clone -- "$repo" "$destination"
echo "NEXT - inspect the source, then run python3 scripts/ide-setup.py --plan from that directory."
