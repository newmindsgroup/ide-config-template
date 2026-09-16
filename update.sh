#!/usr/bin/env bash
# Version-Timestamp: 2026-09-16 15:20:39 AST
# Preview by default; use --apply --confirm to update a reviewed local target.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ $# -gt 0 && "$1" != --* ]]; then
  target="$1"
  shift
  exec python3 "$root/scripts/update-spine.py" --target "$target" "$@"
fi
exec python3 "$root/scripts/update-spine.py" "$@"
