# Install on several computers

Version-Timestamp: 2026-09-16 16:02:15 AST

Use the same tagged source release on each computer, but create a fresh local profile and review on each one. Your accounts, available models, app paths and workspace locations may differ. Never copy credentials, runtime configuration, installation records or backups between computers.

## 1. Get and verify the release

Download the source archive from the repository's release page, or clone and check out the release tag. Use Python 3.10 or newer.

macOS and Linux:

```bash
python3 scripts/verify.py
cp profile.example.json profile.local.json
```

Windows PowerShell:

```powershell
py scripts/verify.py
Copy-Item profile.example.json profile.local.json
```

Verification works without Git metadata. It uses temporary fixtures, does not install into your live app folders and does not download dependencies. The separate Gitleaks scanner runs in GitHub CI. Check the release's successful `release-checks` result before installation.

## 2. Personalize and preview

Edit `profile.local.json`. Select the apps installed on this computer and declare only account/model access you have confirmed here. Keep goals generic and free of customer data. Do not edit the shared example with real personal details.

```bash
python3 scripts/ide-setup.py --plan --profile profile.local.json --workspace /absolute/path/to/project
```

On Windows, substitute `py` and an absolute Windows path, such as `C:\Work\example-project`. Omit `--workspace` when no Cursor project rule is wanted.

The output includes each path, exact text diff, before/after hashes and a `plan_sha256`. This output can reveal existing private instructions. Review it locally; do not paste it into a public issue or commit it.

## 3. Apply the reviewed changes

Use the same profile, workspace and path options. Replace the placeholder with the hash from your own plan:

```bash
python3 scripts/ide-setup.py --apply --confirm --profile profile.local.json --workspace /absolute/path/to/project --expect-plan-sha256 HASH_FROM_YOUR_PLAN
```

If the profile, target content, selected paths or relevant recommendations changed, the hash check refuses the apply before writing. Preview again. The hash is an integrity check, not a digital signature or a transferable authorization. `--apply --confirm` without a hash remains available for older workflows, but the hash-bound workflow is recommended.

## Custom locations and sandbox rehearsals

Default setup honors `CODEX_HOME` and `CLAUDE_CONFIG_DIR` for selected apps. Explicit absolute `--codex-home` and `--claude-home` options take precedence. Use the same options for plan and apply.

An explicit `--home` creates a separate setup scope and ignores both environment overrides, even if the supplied home equals the current home. This keeps disposable rehearsals from reaching your real configuration. Explicit app-home options still apply, so keep those inside the disposable scope when rehearsing. Antigravity uses `.gemini/GEMINI.md` below the selected home.

Linked or ambiguous selected targets require manual review; the wizard does not redirect through them. Project or organization policy can override global instructions. A successful write does not prove those instructions are active in an app.

## 4. Verify each app

```bash
python3 scripts/ide-setup.py --status
```

Use the same `--home` for a rehearsal. Status checks recorded files and markers, not account access or live app behavior. Start a fresh app session and follow the [app acceptance checklist](app-acceptance.md). Keep the results local.

## Updates, deselection and removal

The local `.ide-config/installations.json` remembers all configured app targets and Cursor workspaces. Applying a profile that drops an app does not silently remove that app's instructions. Previously configured destinations remain tracked until explicit removal. Do not copy or edit this record to move an installation.

To remove this template's marked blocks from **all tracked destinations**, including apps no longer selected and earlier Cursor workspaces:

```bash
python3 scripts/ide-setup.py --plan-remove
python3 scripts/ide-setup.py --remove-managed-block --confirm --expect-plan-sha256 HASH_FROM_REMOVAL_PLAN
```

Review the complete removal list. Other instructions, app settings, installed skills and source code remain. Generated profiles/manual exports and recovery copies remain available. Exact empty Cursor scaffolds left by removal can be reinstalled; unrelated Cursor content still requires manual handling.

The registry changes in the same rollback operation as instructions. A copied record for a different home, malformed record, unsafe target or stale approval stops the operation. If a tracked project was moved, preserve the record and backups, inspect the old and new paths, and reconcile manually rather than changing paths blindly.

Older releases without a registry can recover recognized default app targets and Cursor targets recorded in their backup manifests. Arbitrary spine-updater targets are excluded. A manually moved workspace, missing backup history or earlier custom/symlink setup requires manual inspection. Preview makes any recovered destinations visible before removal.

Recovery copies and manifests are machine-local. See [recovery instructions](personalized-setup.md#recovery).
