# Personalized Team Setup

Version-Timestamp: 2026-08-28 10:00:00 AST

## What this does

The setup wizard turns this public template into a local configuration plan for one person and one computer. It asks about name, role, goals, main stack, normal work, data sensitivity, IDEs, and available subscriptions. It scans only basic computer capacity and installed command-line tools.

It never asks for passwords, API keys, browser cookies, customer data, or proof of a subscription. It never downloads a local model, enables paid APIs, or changes files until the person runs `--apply --confirm`.

## Start here

Clone or create a repository from this template, then run:

```bash
python3 scripts/ide-setup.py --scan
python3 scripts/ide-setup.py --plan
```

The first command prints a non-secret computer report. The second command starts the guided interview and prints a plan without writing files.

If the plan is correct, run:

```bash
python3 scripts/ide-setup.py --apply --confirm
```

For a team-managed, repeatable install, create a non-secret profile JSON file and use it without prompts:

```bash
python3 scripts/ide-setup.py --plan --non-interactive --profile profile.example.json
python3 scripts/ide-setup.py --apply --confirm --non-interactive --profile profile.example.json --workspace /absolute/project/path
```

## What the wizard writes

| Destination | Behavior |
|---|---|
| `~/.ide-config/` | Local profile, recommendation plan, backup folder, and manual web prompt packs. This folder is personal and should not be committed. |
| `~/.codex/AGENTS.md` | Adds or updates only a marked managed block. Existing instructions are kept. |
| `~/.claude/CLAUDE.md` | Adds or updates only a marked managed block. Existing instructions are kept. |
| `~/.gemini/GEMINI.md` | Adds or updates only a marked managed block when Antigravity is selected. Existing instructions are kept. |
| `<workspace>/.cursor/rules/ide-config-template.mdc` | Creates a project-scoped Cursor rule only when `--workspace` is supplied. |
| `~/.ide-config/manual/` | Copy-ready instructions for ChatGPT, Claude web, task routing, and Cursor when no workspace was supplied. |

Every existing file changed by the wizard is copied first to `~/.ide-config/backups/<timestamp>/`.

## Routing recommendations

The generated plan uses a transparent order:

1. Use deterministic commands for checks, tests, formatting, builds, and search.
2. Keep confidential work local when that is practical and a suitable local model exists.
3. Use an available subscription for ordinary hosted work.
4. Use a subscription premium model only for difficult or high-consequence review.
5. Treat OpenRouter as off by default. If explicitly selected, permit only free models and public or sanitized material.
6. Never enable a paid API fallback automatically.

The local-model tier is only a capacity recommendation. It is capped by free disk as well as memory. Install a local model separately after reviewing its disk, memory, license, and performance requirements.

## Web instructions

ChatGPT and Claude web settings cannot be configured safely by a local script. The wizard creates concise copy blocks for their instruction or project settings. Review and paste the appropriate file manually. Do not paste private machine details, credentials, or customer data into a web service unless it is approved for that data.

## Skill recommendations

The wizard recommends skills from role categories. It does not install skills. Review publisher, permissions, data flow, and license before installing any third-party skill or plugin. A team may maintain an approved skill catalog in its own private repository.

## Rollback

Remove only this template's marked instruction blocks with:

```bash
python3 scripts/ide-setup.py --remove-managed-block --confirm --profile ~/.ide-config/profile.local.json
```

To remove the generated local preference files, delete `~/.ide-config/`. To restore an instruction file, use its timestamped copy under `~/.ide-config/backups/`. Review the difference before restoring it because a file may also contain changes made after the wizard ran.
