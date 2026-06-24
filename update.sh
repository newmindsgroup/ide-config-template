#!/usr/bin/env bash
# update.sh — refresh the shared operating spine in your AGENTS.md from upstream,
# WITHOUT touching your own customizations.
#
# The spine is everything between the <!-- SPINE:START --> / <!-- SPINE:END --> markers
# in AGENTS.md. Your profile, brand, and project sections live outside those markers and
# are preserved. Run from your repo root (or pass the path to your AGENTS.md).
#
# Usage:  ./update.sh            (updates ./AGENTS.md)
#         ./update.sh path/to/AGENTS.md
set -uo pipefail

UPSTREAM="https://raw.githubusercontent.com/newmindsgroup/ide-config-template/main/AGENTS.md"
LOCAL="${1:-AGENTS.md}"

[ -f "$LOCAL" ] || { echo "No '$LOCAL' here. Run from your repo root or pass the path."; exit 1; }
grep -q '^<!-- SPINE:START' "$LOCAL" || {
  echo "'$LOCAL' has no SPINE markers (it predates updatable spines)."
  echo "Re-copy AGENTS.md from the template, then re-apply your customizations once."
  exit 1; }

up="$(curl -fsSL "$UPSTREAM")" || { echo "Could not fetch upstream AGENTS.md (network?)."; exit 1; }
upspine="$(printf '%s\n' "$up" | awk '/^<!-- SPINE:START/{f=1;next} /^<!-- SPINE:END/{f=0} f')"
[ -n "$upspine" ] || { echo "Upstream has no spine block — aborting (nothing changed)."; exit 1; }

# Splice the fresh spine (with markers) into LOCAL, replacing the old marked block.
rf="$(mktemp)"
{ echo '<!-- SPINE:START — shared operating standard, refreshed by update.sh from upstream. -->'
  printf '%s\n' "$upspine"
  echo '<!-- SPINE:END -->'; } > "$rf"
awk -v rf="$rf" '
  /^<!-- SPINE:START/ { while ((getline line < rf) > 0) print line; close(rf); skip=1; next }
  /^<!-- SPINE:END/   { skip=0; next }
  skip==1 { next }
  { print }
' "$LOCAL" > "$LOCAL.tmp" && mv "$LOCAL.tmp" "$LOCAL"
rm -f "$rf"

echo "Updated the operating spine in '$LOCAL' from upstream — your customizations were preserved."
echo "Review the diff before committing: git diff $LOCAL"
