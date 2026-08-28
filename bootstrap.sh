#!/usr/bin/env bash
# Clone a personal template copy into ~/.claude only when that path is empty.
# Version-Timestamp: 2026-08-28 12:00:00 AST

set -euo pipefail

REPO="${1:-${CLAUDE_CONFIG_REPO:-}}"
CLAUDE_DIR="$HOME/.claude"

say() { printf '%s\n' "$*"; }
fail() { say "ERROR - $*" >&2; exit 2; }

[ -n "$REPO" ] || fail "Usage: bash bootstrap.sh https://github.com/YOU/your-ide-config.git"
command -v git >/dev/null 2>&1 || fail "git is required"

if [ -d "$CLAUDE_DIR/.git" ]; then
  git -C "$CLAUDE_DIR" diff --quiet || fail "~/.claude has uncommitted changes. Review or commit them before running an update."
  say "UPDATING - $CLAUDE_DIR"
  git -C "$CLAUDE_DIR" pull --ff-only
elif [ -e "$CLAUDE_DIR" ]; then
  fail "~/.claude already exists and is not this template's Git checkout. Do not overwrite it. Use scripts/ide-setup.py for a managed instruction block, or choose another empty target."
else
  say "CLONING - $REPO into $CLAUDE_DIR"
  git clone "$REPO" "$CLAUDE_DIR"
fi

say "NEXT - run: python3 $CLAUDE_DIR/scripts/ide-setup.py --scan"
say "NEXT - run: python3 $CLAUDE_DIR/scripts/ide-setup.py --plan"
say "BOUNDARY - review the plan, then use --apply --confirm only with explicit approval."
