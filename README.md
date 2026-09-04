# IDE Configuration Template

Version-Timestamp: 2026-09-04 17:52:06 AST

A public, person-aware starting point for configuring AI coding tools and AI work habits. It helps each team member create a safe local setup for their role, computer, subscriptions, projects, and preferred IDEs.

It supports Codex, Claude Code, Cursor, Google Antigravity, ChatGPT web, and Claude web. The template is deliberately generic. It does not contain company data, personal machine paths, credentials, private routing policies, or a required paid API.

## What happens when someone asks an AI agent to use this repository

The agent should not immediately install or overwrite anything. It should follow this sequence:

1. Clone or create a personal copy of this repository. Do not modify the upstream public template for an individual team member.
2. Run a non-secret computer scan.
3. Run the guided planning interview.
4. Explain the proposed configuration, data boundary, routing strategy, recommended skills, and files that would change.
5. Wait for explicit approval.
6. Apply only the approved local changes, create backups, and show the copy-ready web instructions that require manual pasting.
7. Verify the generated files and ask the person to start a new IDE session.

Use this exact agent instruction when sharing the repository with an AI agent:

```text
Help me configure my AI development environment using this repository. Start with the non-writing scan and guided plan. Ask only for non-secret information about my role, goals, work, computer, IDEs, and subscriptions. Explain every recommendation before changing files. Do not read credentials, browser sessions, client data, or secret files. Do not enable paid API fallback, install a local model, or overwrite an existing instruction file. Apply changes only after I explicitly approve the plan.
```

## Start here

Create a repository from this template or clone your team copy. Python 3 is required for the setup wizard.

```bash
git clone https://github.com/YOUR-ORG/YOUR-IDE-CONFIG.git
cd YOUR-IDE-CONFIG

# Inspect the computer. This does not write files.
python3 scripts/ide-setup.py --scan

# Answer the guided interview and view a plan. This does not write files.
python3 scripts/ide-setup.py --plan

# Apply the approved plan. Add a Cursor workspace only when wanted.
python3 scripts/ide-setup.py --apply --confirm --workspace /absolute/path/to/project
```

Use `--workspace` only for a project where a Cursor rule is appropriate. Omit it if the person does not use Cursor or does not want a project rule.

## LLM routing and fallback strategy requests

The following phrases all mean the same thing in this repository: implement a safe LLM routing and fallback strategy for the person and their computer.

- LLM routing or model routing
- Model selection, model choice, provider routing, or AI routing
- Fallback strategy, model fallback, LLM fallback, or multi-model setup
- Local model strategy, local LLM setup, or local-model fallback
- OpenRouter setup, free model fallback, or provider overflow
- Token conservation, usage optimization, model budget, effort selection, or speed selection

When someone uses any of those phrases, an AI agent should use the routing-focused workflow rather than answer with a one-off model list:

```bash
python3 scripts/ide-setup.py --scan
python3 scripts/ide-setup.py --plan --focus llm-routing
```

The plan gives one coherent implementation goal and covers privacy, local capacity, subscriptions, deterministic tools, hosted defaults, premium review, free-only overflow, and when the route must be reconsidered. Apply it only after review:

```bash
python3 scripts/ide-setup.py --apply --confirm --focus llm-routing
```

Read [LLM Routing Implementation](docs/llm-routing-implementation.md) for the complete behavior contract.

## The setup wizard

The wizard has three modes.

| Command | Changes files? | Purpose |
|---|---:|---|
| `--scan` | No | Reports operating system, architecture, memory, free disk, and installed command-line tools. |
| `--plan` | No | Runs the guided interview and prints recommendations. Add `--focus llm-routing` for routing and fallback implementation. |
| `--apply --confirm` | Yes, after the caller explicitly chooses it twice | Stores a local non-secret profile, creates backups, adds managed IDE instructions, and generates manual web prompt packs. |
| `--remove-managed-block --confirm` | Yes, after the caller explicitly chooses it twice | Removes only this template's marked instruction blocks and creates a backup first. |

The guided interview asks only for information that changes the recommendation:

| Topic | Why it matters |
|---|---|
| Name and role | Selects an instruction emphasis and skill recommendations. |
| Goals and main stack | Gives the generated instructions useful project context. |
| Data sensitivity | Defines the default public, internal, or confidential boundary. |
| IDEs | Selects which local adapters are generated. |
| ChatGPT, Claude, Gemini, and Cursor subscriptions | Identifies available subscription paths without checking account credentials. |
| OpenRouter free-only preference | Keeps OpenRouter disabled unless the person explicitly opts in for public or sanitized work. |
| Computer capacity and Ollama availability | Recommends a conservative local-model tier. It never downloads a model. |

Do not enter passwords, API keys, browser cookies, recovery codes, customer data, or private documents into the interview or profile.

## What gets configured

The wizard writes only the files needed for the selected tools.

| Tool or surface | Output | Behavior |
|---|---|---|
| Codex | `~/.codex/AGENTS.md` | Adds or updates one marked managed block. Existing instructions stay in place. |
| Claude Code | `~/.claude/CLAUDE.md` | Adds or updates one marked managed block. Existing instructions stay in place. |
| Cursor | `<workspace>/.cursor/rules/ide-config-template.mdc` | Creates a project-scoped rule only when `--workspace` is supplied. |
| Google Antigravity | `~/.gemini/GEMINI.md` | Adds or updates one marked managed block when selected. |
| ChatGPT web | `~/.ide-config/manual/chatgpt-custom-instructions.md` | Generates a reviewable block for manual copy and paste. |
| Claude web | `~/.ide-config/manual/claude-web-project-instructions.md` | Generates a reviewable block for manual copy and paste. |
| Personal routing guide | `~/.ide-config/manual/task-routing-guide.md` | Explains the person's recommended task-routing policy. |

The wizard creates a timestamped backup before it changes an existing instruction file. Generated personal files stay under `~/.ide-config/` and are ignored by Git.

## Astra and subscription capacity

The interview asks whether Astra is actually selectable in the person's Codex account. A ChatGPT subscription alone does not establish access. The optional profile field `astra_available` defaults to `false`. With confirmed access, substantial work uses Astra Medium at Standard speed. Routine work remains on Terra or Luna when available. High effort is reserved for difficult or high-consequence work.

The wizard generates instructions and recommendations. It does not poll quotas, execute model requests, or automatically switch an active session. When shared OpenAI capacity runs out, save the task state and continue through an approved available Claude subscription or suitable local model. Switching OpenAI models does not reset shared allowance. OpenRouter remains an explicit free-only option.

Before provider handoff, record the objective, acceptance criteria, changed files, decisions, checks, unresolved risks, and exact next action. Verify the working tree before resuming any partially completed operation.

## Routing and fallback strategy

The system makes routing explicit. It does not silently select a paid provider or assume every computer has the same local capacity.

1. Use deterministic tools first for tests, formatting, builds, linting, search, and mechanical checks.
2. Keep confidential work local when a suitable local model exists and the task is appropriate for it.
3. Use an available subscription for ordinary hosted work.
4. Use a stronger subscription model only for difficult architecture, high-consequence synthesis, or independent final review.
5. Use fast mode only when the person explicitly values response time more than usage conservation.
6. Keep OpenRouter off unless the person selects free-only access. If selected, use only free models and public or sanitized material.
7. Never enable automatic paid API fallback.

### Local-model capacity tiers

The scan uses memory, free disk, and Ollama availability to recommend a capacity tier. This is a planning recommendation, not a benchmark or an automatic install. Disk capacity caps the recommendation, so a high-memory computer with little free space is not offered an impractical full local tier.

| Tier | Typical purpose |
|---|---|
| `none` | No local fallback is recommended. |
| `light` | Small private extraction, classification, and short summaries. |
| `standard` | Adds routine local code and document work. |
| `advanced` | Adds private general analysis and bounded image or interface triage. |
| `full` | Intended for a high-memory workstation after reviewing model requirements. |

Model downloads, third-party model licenses, provider keys, and performance tuning are separate decisions. The wizard never performs them automatically.

## Skills, plugins, and instructions

These are different parts of the system.

| Component | Purpose | Wizard behavior |
|---|---|---|
| Instructions | Always-on working rules for the selected IDE or web AI tool. | Generates compact, role-aware instructions. |
| Skills | On-demand methods for a specific task, such as testing, accessibility review, writing, or debugging. | Recommends skills by role. Does not install them. |
| Plugins and connectors | Connections to external products and services. | Does not install or authorize them. Review publisher, permissions, data flow, and cost first. |
| Models and providers | The model route used for a task. | Generates a transparent strategy based on available local capacity and declared subscriptions. |

Recommended skills are suggestions, not proof that a skill is installed or approved. Vet third-party skills and plugins before they touch client data, infrastructure, credentials, or production systems.

## Copy-ready web instructions

Local scripts cannot safely control ChatGPT or Claude web account settings. Instead, the wizard creates instructions to review and paste manually. The generated prompt uses six parts:

1. Role
2. Objective
3. Context and data boundary
4. Requirements
5. Desired output
6. Evaluation criteria

This keeps the instruction focused and avoids a large generic prompt that wastes context or overrides project-specific rules.

## Team-managed setup with a profile file

For repeatable onboarding, start from [profile.example.json](profile.example.json). The profile is deliberately non-secret and accepts only documented fields.

```bash
python3 scripts/ide-setup.py --plan --non-interactive --profile profile.example.json
python3 scripts/ide-setup.py --apply --confirm --non-interactive --profile profile.example.json --workspace /absolute/path/to/project
```

The wizard rejects unknown fields such as `api_key` rather than storing them in a local profile.

## Security and privacy boundaries

The template follows these hard boundaries:

- No credentials, API keys, browser cookies, tokens, or client exports are requested, read, or stored by the wizard.
- No paid API fallback is enabled.
- No local models are downloaded automatically.
- No existing instruction file is replaced wholesale.
- No browser account settings are automated.
- No third-party skills, plugins, or connectors are installed automatically.
- Existing instruction files are backed up before a marked block is changed.

The local profile records personal work preferences. Treat `~/.ide-config/` as private workstation configuration and keep it out of shared repositories.

## How the shared instruction spine works

[AGENTS.md](AGENTS.md) is the portable baseline for working style, engineering quality, safety, data handling, third-party vetting, and truthfulness. It contains `SPINE` markers.

Run this from a fork or team copy to refresh only the shared operating block while preserving profile and project-specific content outside those markers:

```bash
./update.sh
git diff AGENTS.md
```

Use project-level `AGENTS.md` files for repository commands, stack conventions, data classification, and acceptance checks. Do not copy a long global configuration into every project.

## Verify the repository

Run the included checks before committing changes to the template:

```bash
bash scripts/verify.sh
```

This checks the setup wizard, its behavior tests, Python syntax, and the required `AGENTS.md` spine markers. GitHub Actions runs the same verification when the instruction file, scripts, or tests change.

## Rollback and recovery

The wizard stores backups at `~/.ide-config/backups/<timestamp>/`.

To remove the template's managed instruction blocks, run:

```bash
python3 scripts/ide-setup.py --remove-managed-block --confirm --profile ~/.ide-config/profile.local.json
```

To remove only the generated local profile and manual prompt packs, remove `~/.ide-config/`. To restore an IDE instruction file, compare the timestamped backup with the current file and restore only the managed block if appropriate. Do not overwrite later user edits blindly.

## Operating-system notes

The wizard itself uses standard-library Python and stores files under the current account's home directory. On macOS and Linux, use `python3`. On Windows, use `py` or `python` if `python3` is unavailable. The exact IDE setting surfaces can change, so review generated files before relying on them. The repository test suite runs on Ubuntu, macOS, and Windows in GitHub Actions.

## Repository map

| Path | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Portable working-standard spine and AI-agent behavior when this repository is used for setup. |
| [CLAUDE.md](CLAUDE.md) | Claude Code entry point that imports the shared instruction file. |
| [scripts/ide-setup.py](scripts/ide-setup.py) | Scan, interview, plan, apply, backup, adapter, and prompt-pack generator. |
| [scripts/verify.sh](scripts/verify.sh) | Local verification command. |
| [docs/personalized-setup.md](docs/personalized-setup.md) | Detailed setup, output, privacy, and rollback reference. |
| [docs/llm-routing-implementation.md](docs/llm-routing-implementation.md) | Canonical trigger phrases and implementation workflow for routing and fallback requests. |
| [profile.example.json](profile.example.json) | Example non-secret profile for repeatable onboarding. |
| [profile.schema.json](profile.schema.json) | Editor-validatable schema for permitted non-secret profile fields. |
| [settings.json](settings.json) | Optional Claude Code safety hooks and permission baseline. |
| [bootstrap.sh](bootstrap.sh) | Optional Claude Code home-directory bootstrap for a personal fork or team copy. |
| [update.sh](update.sh) | Updates only the portable instruction spine in a copy. |
| [memory/](memory/) | Example persistent-memory structure. |
| [SECURITY.md](SECURITY.md) | Security reporting and disclosure boundary. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution, test, and public-template rules. |
| [docs/demo-walkthrough.md](docs/demo-walkthrough.md) | Short end-to-end terminal walkthrough. |

## Scope and limitations

This repository is a configuration template, not an account manager, package manager, hosted AI service, or central device-management system. It cannot prove a subscription is active, configure a web account without human action, guarantee local-model performance, or replace project-specific engineering and security review.

Use it to establish a strong default. Then adapt project instructions, approved tool catalogs, and validation commands to the actual work.

## License

MIT. Use it, fork it, and adapt it into your team standard.
