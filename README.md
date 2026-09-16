# Safe Team Setup for Codex, Claude Code and Cursor

Version-Timestamp: 2026-09-16 16:02:15 AST

[![Template validation](https://github.com/newmindsgroup/ide-config-template/actions/workflows/validate-agents.yml/badge.svg?branch=main)](https://github.com/newmindsgroup/ide-config-template/actions/workflows/validate-agents.yml)

**One shared working standard. Three coding environments. A setup each teammate controls.**

[Quick start](#start-here) · [Setup flow](#how-it-works) · [App destinations](#what-changes) · [Recovery](#preservation-and-recovery) · [Skills and privacy](#skills-and-privacy)

A public, standard-library Python template for adding portable working instructions to a new or existing AI coding setup. Plan first, review the exact destination list, then apply explicitly.

**Existing settings, credentials, MCP connections, installed skills and model selectors are not changed.** The wizard adds one marked instruction block. It does not install applications, plugins, hooks or models, or activate paid services.

## At a glance

| 🧭 Purpose | 👥 Who it helps | 📦 What you get |
|---|---|---|
| Give AI coding tools consistent instructions for planning, privacy, validation and handoffs. | Teammates setting up a new computer or improving an existing coding environment. | A reviewed setup plan, app-specific instruction blocks, backups and optional skill recommendations. |

## How it works

```mermaid
flowchart TD
    A["1. Clone and inspect the public template"] --> B["2. Create your private local profile"]
    B --> C["3. Scan and preview the plan<br/>No configuration changes"]
    C --> D{"Review and approve?"}
    D -->|Revise| B
    D -->|Approve| E["4. Apply with explicit confirmation<br/>Validate destinations and create backups"]
    E --> F["Codex · Claude Code · Cursor<br/>Only selected instruction blocks are added or updated"]
    F --> G["5. Start a new app session<br/>Verify the instructions were loaded"]
```

**In plain language:** clone → personalize → preview → approve → apply → verify. Your profile and recovery copies stay on your computer. Skill recommendations require a separate review and installation.

### What the setup touches

| ✍️ Adds or updates | 🔒 Leaves in place | 🖐️ Requires your action |
|---|---|---|
| This template's marked instruction blocks | Existing text outside those blocks | Approve the plan before applying |
| Local profile, plan and recovery copies | App settings, credentials and MCP connections | Verify instructions in a new app session |
| Manual web-instruction drafts | Installed skills and model selectors | Review optional skills and copy web instructions |

## Start here

For several computers, follow the [multi-computer setup guide](docs/multi-computer-setup.md). Run `python3 scripts/verify.py` first (Windows: `py scripts/verify.py`). Use a fresh profile and review on each computer; keep accounts, installation records and backups machine-local.

Requires Git and Python 3.10 or newer. Clone into a normal source directory, never an application's configuration folder.

```bash
git clone https://github.com/newmindsgroup/ide-config-template.git
cd ide-config-template
cp profile.example.json profile.local.json
```

Edit `profile.local.json` for your role, selected apps and actual subscription access. Use generic goals, not customer information or secrets. This local filename is ignored by Git. Model availability is your declaration, not a live account check.

```bash
python3 scripts/ide-setup.py --scan
python3 scripts/ide-setup.py --plan --non-interactive --profile profile.local.json --workspace /absolute/path/to/project
```

Review the recommendations, `planned_files` and exact diffs. Keep the preview private because it includes existing instruction text. Use the **same profile and workspace**, and the printed `plan_sha256`, when applying:

```bash
python3 scripts/ide-setup.py --apply --confirm --non-interactive --profile profile.local.json --workspace /absolute/path/to/project --expect-plan-sha256 HASH_FROM_YOUR_PLAN
```

Omit `--workspace` for both commands if you do not want a Cursor project rule. On Windows, use `py` or `python` and an absolute Windows project path. Copy the example with PowerShell `Copy-Item` instead of `cp` if needed.

Prefer the saved-profile workflow above. Running `--plan` and `--apply` without a profile starts two separate interviews. An interactive apply does not consume an earlier plan.

## What changes

| Selected app | Destination | Behavior |
|---|---|---|
| Codex | `~/.codex/AGENTS.md` | Adds or replaces only this template's marked block. |
| Claude Code | `~/.claude/CLAUDE.md` | Adds or replaces only this template's marked block. |
| Cursor with workspace | `<workspace>/.cursor/rules/ide-config-template.mdc` | Creates a rule, or updates its existing managed block. Refuses an unmanaged file with that name. |
| Cursor without workspace | `~/.ide-config/manual/cursor-user-rules.md` | Produces instructions for manual review and copying. |
| Optional Antigravity | `~/.gemini/GEMINI.md` | Generates a marked instruction block when selected. Verify support in your app version. |
| Local outputs | `~/.ide-config/` | Profile, recommendation plan, manual web instructions and private backup records. |

Claude Code instructions apply to its coding environment, including supported desktop coding sessions. They do not configure general Claude chat, Cowork, or the web account. ChatGPT and Claude web instructions require manual review and copying.

For selected apps, setup honors `CODEX_HOME` and `CLAUDE_CONFIG_DIR`. Explicit `--codex-home` and `--claude-home` paths take precedence. An explicit `--home` ignores environment overrides for isolated rehearsals. Remote hosts, containers and organization-managed policies need their own local review. Project instructions, organization policies and app precedence can override global instructions. Start a new session and check which instructions the app loaded.

Native references: [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md/), [Claude Code memory](https://code.claude.com/docs/en/memory), [Cursor rules](https://cursor.com/docs/context/rules).

## Preservation and recovery

- Plan and apply validate all selected destinations before writing. Malformed or duplicate markers, linked files, hard-linked files and special files are refused. User-created symlink ancestors are refused; standard macOS root aliases are resolved.
- Existing content outside the managed block is preserved byte for byte, including line endings and whitespace. A repeated apply with unchanged inputs does not duplicate blocks.
- Every changed existing file, including generated local outputs, gets a recovery copy. The manifest records original destinations, modes and whether a file was newly created.
- Writes replace individual files atomically. Ordinary write failures trigger rollback of completed writes. Stop concurrent editors during setup. This is not a cross-file power-loss transaction, a sandbox against hostile filesystem races, or a guarantee against conflicting instruction meaning.
- Backup runs use private POSIX permissions where supported. Windows protection follows the user's filesystem ACLs. Keep backups in your private home directory.

A local installation record remembers previously configured apps and Cursor workspaces even when later profiles deselect them. Preview removal from **all tracked destinations**, then use its approval hash:

```bash
python3 scripts/ide-setup.py --plan-remove
python3 scripts/ide-setup.py --remove-managed-block --confirm --expect-plan-sha256 HASH_FROM_REMOVAL_PLAN
```

Removal preserves unrelated instructions and may leave empty files or Cursor frontmatter. Tracked paths come from this computer's installation record; do not copy that record between computers. It does not uninstall applications or delete skills. See [recovery details](docs/personalized-setup.md#recovery).

## Skills and privacy

See the [optional skill guide](docs/optional-skills.md) for source review, app-specific destinations and a small acceptance test before use.

[approved-skills.json](approved-skills.json) contains **six optional, public reusable recommendations** from two curated plugin groups. Their source URLs pin a reviewed commit. No skill bodies, company-specific plugins, private workflows or experimental candidates are bundled. Role recommendations are deliberately small; an empty list means there is no approved default for that role here.

The catalog records scoped review, not a promise that every workflow has passed real client use. Before adoption, inspect the pinned instructions and dependencies, license, permissions and data flow. Install separately through the app's supported mechanism only when the task needs them. Do not copy an entire personal configuration or bulk-install the upstream library. Project-specific skills belong in their project repository.

Local profiles, project memory, runtime configuration and common secret files are ignored. Git ignore rules do not sanitize tracked content or history. Contributors must inspect the staged diff before publishing. The public-content check catches a limited set of prohibited paths and credential patterns, not every kind of confidential information.

## Updating safely

Review incoming changes in your source checkout before updating it. Re-run plan and apply with your saved profile. Pulling this repository does not change an app's configuration.

For a separate copy of the portable `AGENTS.md` spine, use the local-source updater:

```bash
python3 scripts/update-spine.py --target /absolute/path/to/AGENTS.md
# After reviewing the preview:
python3 scripts/update-spine.py --target /absolute/path/to/AGENTS.md --apply --confirm
```

It preserves text outside the spine and uses the reviewed source checkout, with no remote download. `update.sh` is an optional Bash wrapper. `bootstrap.sh` only clones to a new source directory and refuses existing destinations. Neither helper is needed for normal setup.

## Validation and limits

```bash
python3 scripts/verify.py
```

Tests cover new and existing setups, exact preservation, Cursor collisions, malformed markers, linked destinations, confirmation, idempotency and simulated write-failure recovery. CI runs all tests on Ubuntu, macOS and Windows with Python 3.10 and 3.12. The required `release-checks` gate also includes checksum-pinned Gitleaks scans of files and Git history. These tests exercise temporary files, not live app sessions or provider accounts. The Codex CLI loaded generated global instructions in an isolated native smoke check. Follow the [app acceptance checklist](docs/app-acceptance.md) for the remaining app and computer-specific checks. `python3 scripts/ide-setup.py --status` reports file health without claiming live app acceptance.

`settings.json` is an inert optional example. Do not replace an existing application's settings with it. There are no automatic execution hooks or default secret-bearing review workflows.

Routing guidance is advisory: it cannot switch a model, verify quotas, prove local model performance or enforce review gates. Windows RAM detection is currently unavailable, so the local-model recommendation defaults to none. Use only models actually available in your app. See [routing guidance](docs/routing-efficiency.md).

## Sharing with your team

Send this repository with the instruction: "Clone and inspect it, create a local profile, show me the plan, and wait for my approval before applying." Never send your private profile, backups, tokens, client records or private configuration repository.

Maintainers: read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [PROVENANCE.md](PROVENANCE.md). License: MIT.
