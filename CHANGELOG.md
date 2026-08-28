# Changelog

Versions of this template. To pull the latest operating spine into your own copy
without losing your customizations, run `./update.sh`. Watch/star the repo for release
notifications.

## v1.2.0. 2026-08-28

- Required `--confirm` for apply and managed-block removal, added a safe managed-block removal command, and corrected disk-limited local tiers and Cursor fallback guidance.
- Replaced the forceful Claude bootstrap adoption path with a clone-or-clean-update path that refuses to overwrite an existing unmanaged directory.
- Added Windows, macOS, and Linux test coverage in GitHub Actions, a JSON profile schema, security policy, contributor guide, and terminal demo walkthrough.

## v1.1.2. 2026-08-28

- Added a canonical LLM-routing intent that maps routing, fallback, provider, local-model, OpenRouter, token, effort, and speed requests to one safe implementation workflow.
- Added `--focus llm-routing`, agent instructions, documentation, and regression coverage for the routing-focused plan.

## v1.1.1. 2026-08-28

- Rewrote the README as a complete human and AI-agent operating guide for personalized team setup, routing, skills, plugins, local capacity, web instruction packs, safety boundaries, verification, and rollback.

## v1.1.0. 2026-08-28

- Added `scripts/ide-setup.py`, a role-aware wizard with scan, plan, and explicit apply modes.
- Added safe adapters for Codex, Claude Code, and project-scoped Cursor rules, plus copy-ready ChatGPT and Claude web instructions.
- Added non-secret machine capability recommendations, skill recommendations, transparent fallback routing, backups, and no-paid-API defaults.
- Added a profile example, setup guide, tests, local-profile Git ignores, and CI verification.

## v1.0.0 — 2026-06-19
- Cross-IDE `AGENTS.md` spine (the [AGENTS.md](https://agents.md/) standard, read by Claude Code, Codex, Cursor, Antigravity).
- Operating standard: four-pillar engineering mantra (Security · Stability · Reliability · Compliance), proportional rigor, attribution & versioned outputs, third-party-component trust, data handling, truthfulness & escalation, skill-leverage habit, qualifying-questions protocol, look-around-the-corner, skill-worthiness radar, sequenced next steps.
- `update.sh` — refresh the spine from upstream, preserving your edits (spine wrapped in `SPINE` markers).
- IDE-agnostic README with a per-tool how-to.
- Optional Claude Code extras: safety hooks, bootstrap, four-pillar CI review workflow, memory/skills scaffolds.
