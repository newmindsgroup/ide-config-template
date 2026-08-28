# Demo Walkthrough

Version-Timestamp: 2026-08-28 12:00:00 AST

This walkthrough shows the normal safe path. It uses the sample profile and never changes a real home directory.

```bash
# 1. Inspect only.
python3 scripts/ide-setup.py --scan

# 2. Review the routing plan only.
python3 scripts/ide-setup.py --plan --focus llm-routing --non-interactive --profile profile.example.json

# 3. Apply to a disposable home and workspace after review.
demo_home="$(mktemp -d)"
demo_workspace="$(mktemp -d)"
python3 scripts/ide-setup.py --apply --confirm --focus llm-routing --non-interactive --profile profile.example.json --home "$demo_home" --workspace "$demo_workspace"

# 4. Inspect generated outputs.
find "$demo_home/.ide-config" -maxdepth 2 -type f
find "$demo_workspace/.cursor" -type f

# 5. Remove only the generated managed block.
python3 scripts/ide-setup.py --remove-managed-block --confirm --profile "$demo_home/.ide-config/profile.local.json" --home "$demo_home" --workspace "$demo_workspace"
```

On Windows, use a temporary folder created in PowerShell and run `py` or `python` when `python3` is unavailable. Do not run the apply step against a real home directory until the plan has been reviewed.
