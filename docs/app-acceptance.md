# App acceptance checklist

Version-Timestamp: 2026-09-16 16:02:15 AST

File tests and CI establish installer behavior. Each computer still needs an app-level check because app versions, project overrides, organization rules and account access differ. Record app version, OS, release tag, check date and result locally. Do not commit personal paths or instruction content to this public repository.

## Codex

1. Run setup with the reviewed paths, then `--status`.
2. Start a new local Codex session in a disposable project. Inspect the session's instruction sources and verify that the expected global `AGENTS.md` is included. Check for an `AGENTS.override.md` or project rule that supersedes it.
3. If your Codex CLI offers `codex debug prompt-input`, inspect it locally in that disposable project. It can display private context; never post the output publicly. Check for a distinctive non-secret phrase from the generated block. Do not enable a paid model call merely to test file discovery.
4. Preview removal, remove, and verify that a fresh session no longer includes the template block. Reapply only if desired.

Native evidence for this release: Codex CLI 0.154.0 on macOS successfully loaded the generated global instructions using `debug prompt-input` with an isolated temporary home. No credentials were copied and no model request was made. This does not establish desktop acceptance on every machine.

## Claude Code

1. Start a fresh Claude Code session after setup. Use its memory/instruction view, such as `/memory` when available, to confirm the intended `CLAUDE.md` file is loaded.
2. Check the generated block's role, privacy and validation instructions against the reviewed profile.
3. Test a small synthetic task using existing approved account access. Do not change billing, permissions or account configuration for the test.
4. Preview removal and confirm the marked block disappears while your existing instructions remain. Start a new session for each comparison.

General Claude chat and Cowork are not configured by this adapter. Claude Code app-level acceptance is still a per-computer check, not a completed result recorded by this repository.

## Cursor

1. Open the workspace supplied to setup. Inspect Cursor's rules settings and confirm `ide-config-template.mdc` appears as an always-applied project rule.
2. Start a fresh agent chat and inspect its applied rules/context. Check that the generated block is present and existing rules remain.
3. Preview removal, remove, and confirm the template block disappears. An empty rule scaffold can remain; it contains no template instructions.

Cursor app-level acceptance is still a per-computer check. When setup had no workspace, manually review and copy the generated user-rule draft instead.

## Optional Google Antigravity

Verify the selected home's `.gemini/GEMINI.md` in the app's rules view, then start a new conversation. This adapter is optional and requires a per-computer check. Do not infer acceptance from another app reading the same filename.

References: [Codex instructions](https://developers.openai.com/codex/guides/agents-md/), [Claude Code memory](https://code.claude.com/docs/en/memory), [Cursor rules](https://cursor.com/docs/rules), [Antigravity rules](https://antigravity.google/docs/rules-workflows).
