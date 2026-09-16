# Personalized Team Setup and Recovery

Version-Timestamp: 2026-09-16 16:02:15 AST

Use the [README setup sequence](../README.md#start-here) with one saved non-secret profile. Planning reads only the selected instruction targets and basic machine capabilities. It does not inspect credentials, customer data or browser sessions. An apply creates local outputs and backups only after `--apply --confirm`.

## Before applying

1. Review the source and profile. Confirm app selection, workspace and available subscriptions.
2. Close editors modifying the affected files. Review `planned_files` and existing instructions for policy conflicts.
3. Review custom app homes carefully. Environment overrides are supported for selected Codex and Claude Code apps; explicit app-home flags take precedence. An explicit --home suppresses environment overrides. Managed company policies and remote environments still require local review.
4. Use `--home /absolute/disposable/home` and a disposable workspace to rehearse without touching live configuration.
5. Apply with exactly the reviewed profile and workspace. Start a fresh app session and check loaded instructions.

## Recovery

Backups live under `~/.ide-config/backups/<timestamp>-<unique-id>/`. Each run has a `manifest.json` mapping numbered backup files to original destinations and modes. A null backup means that destination did not exist before the run.

Ordinary write failures trigger automatic rollback. A process interruption or power loss may require manual recovery. Stop edits, inspect the manifest, compare each current file against its backup and preserve any later user changes before restoring. Never execute a manifest as a script. Do not delete a new file merely because a manifest marks it new if it now contains useful work.

For ordinary removal, preview all tracked destinations, including earlier app selections and Cursor workspaces:

```bash
python3 scripts/ide-setup.py --plan-remove
python3 scripts/ide-setup.py --remove-managed-block --confirm --expect-plan-sha256 HASH_FROM_REMOVAL_PLAN
```

This removes only marked instruction blocks and creates backups of changed files. Other instructions, existing configuration and installed skills remain. Cursor frontmatter or empty instruction files may remain.

To clean up generated preferences, remove only the unwanted profile, plan or manual prompt files after preserving anything useful. **Do not delete the whole `.ide-config` directory while relying on its backups.** The spine updater stores its backup folder beside its target, under `.ide-config/backups`, rather than necessarily under your home.

## Privacy and optional components

Keep all outputs private. The profile may include your name, work goals and local paths even though credentials are forbidden. Do not publish scan output or backup manifests without reviewing them. No model downloads, skill installations, automatic hooks, paid API fallback or web-account modifications occur.

Skill recommendations reference a small pinned public catalog. Review the source and its dependencies before separate installation. Private company workflows and candidate skills are excluded from this template. Existing third-party plugins are outside the wizard's audit scope.
