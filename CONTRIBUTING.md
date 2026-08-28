# Contributing

Version-Timestamp: 2026-08-28 12:00:00 AST

## Public-template rules

Keep this repository person-agnostic. Do not add personal names, private machine paths, customer information, credentials, API keys, browser sessions, private provider configuration, or unreviewed third-party instructions.

Changes to the wizard must preserve scan, plan, apply, backup, and rollback boundaries. Apply and removal actions require explicit confirmation. Do not add automatic paid API fallback, automatic model downloads, or automatic plugin installation.

## Verification

Run the full local check before opening a pull request:

```bash
bash scripts/verify.sh
```

Add behavior tests for every change to `scripts/ide-setup.py`. Update the README and relevant guides when a command, safety boundary, output path, or supported platform changes.

## Releases

Use a versioned changelog entry. Verify the GitHub Actions matrix before publishing a release. Public documentation should state what the tool does, what it does not do, and what requires manual approval.
