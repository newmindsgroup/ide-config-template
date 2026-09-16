#!/usr/bin/env bash
# Version-Timestamp: 2026-09-16 16:02:15 AST
# Optional Unix wrapper. Windows can run: python scripts/verify.py
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/scripts/verify.py" "$@"
