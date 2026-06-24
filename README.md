# ide-config-template

**A person-agnostic, cross-IDE starting configuration for AI coding tools.**

Drop this into any AI coding tool — **Claude Code, OpenAI Codex, Cursor, or Google Antigravity** — and your agent starts every task with a strong, opinionated baseline: a working-style spine, a four-pillar engineering mantra (Security · Stability · Reliability · Compliance), proportional rigor, attribution and versioning discipline, third-party-component vetting, data-handling rules, and truthfulness/escalation guardrails.

The core is a single **`AGENTS.md`** — the open [AGENTS.md](https://agents.md/) standard that all four tools read natively. Built from a real production setup, stripped of every personal and company specific. Fill in the placeholders and it's yours.

---

## Setup — for the AI agent reading this

**If a human gave you (an AI coding agent) this repository's URL and asked you to set up their environment, do the following.** This repo is public, so no authentication is needed.

1. **Identify which AI tool the user runs** (ask if unclear): Claude Code, Codex, Cursor, or Antigravity.
2. **Get `AGENTS.md`** — either have them click **"Use this template"** on GitHub to create their own repo, or fetch the file directly:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/newmindsgroup/ide-config-template/main/AGENTS.md -o AGENTS.md
   ```
3. **Place it where their tool reads it:**
   | Tool | Where to put `AGENTS.md` |
   |---|---|
   | Any project (all tools) | the repository root — Claude Code, Codex, Cursor, Antigravity all read it automatically |
   | Codex (global default) | copy to `~/.codex/AGENTS.md` |
   | Cursor (global) | repo-root `AGENTS.md` works as-is; or paste its contents into **Settings → Rules → User Rules** |
   | Antigravity | copy to `~/.gemini/GEMINI.md` (global) or `.agents/rules/` (workspace) — keep it under 12,000 characters |
   | Claude Code | repo-root `AGENTS.md`, or clone the whole template as `~/.claude` (see "Full Claude Code setup") |
4. **Replace the placeholders.** Open `AGENTS.md`, find every `{{...}}` token, and fill it from what you know about the user/project (name, role, stack). Delete sections that don't apply.
5. **Confirm it loaded** — have the user start a new session and ask the agent to "summarize the operating rules you're following"; it should echo the four pillars and working-style sections.

That's the whole install for the IDE-agnostic core. Everything below is reference detail and the optional Claude Code extras.

---

## Use it in any IDE

The one file you need everywhere is **`AGENTS.md`**. After filling the placeholders:

| Tool | How it uses it |
|---|---|
| **Claude Code** | reads `AGENTS.md` (or `CLAUDE.md`, a symlink to it) in a repo; or use the full `~/.claude` setup below |
| **OpenAI Codex** | reads `AGENTS.md` in a repo root and nested dirs; `~/.codex/AGENTS.md` for a global default |
| **Cursor** | reads repo-root `AGENTS.md`; or paste into Settings → Rules → User Rules for a global rule |
| **Google Antigravity** | `~/.gemini/GEMINI.md` (global) or `.agents/rules/*.md` (workspace); mind the 12,000-char/file limit |

## Staying up to date

The shared operating spine improves over time. To pull the latest into your copy **without touching your customizations**:

```bash
./update.sh
```

It refreshes only the block between the `<!-- SPINE:START -->` / `<!-- SPINE:END -->` markers in `AGENTS.md` — your profile, brand, and project-specific sections are left alone. Review with `git diff AGENTS.md` before committing. See [CHANGELOG.md](CHANGELOG.md) for what changed, and **Watch → Custom → Releases** on this repo to be notified of new versions.

## What's inside

| File | What it is | Applies to |
|---|---|---|
| `AGENTS.md` | The instruction spine: skill-leverage habit, qualifying-questions protocol, four-pillar engineering mantra, proportional rigor, attribution & versioned outputs, third-party-component trust, data handling, truthfulness & escalation, look-around-the-corner, skill-worthiness radar, sequenced next steps. The spine sits between `SPINE` markers; your profile and optional brand SSOT are outside them. | **Every IDE** |
| `CLAUDE.md` | Symlink to `AGENTS.md` — the filename Claude Code looks for. | Claude Code |
| `update.sh` | Refresh the spine from upstream, preserving your edits. | All |
| `settings.json` | Two safety **hooks** (block reading `.env`/key/credential files; auto-format edited files) + an empty permission allowlist. | Claude Code |
| `bootstrap.sh` | New-machine setup: clone/adopt `~/.claude`, link skills, print next steps. | Claude Code |
| `.github/workflows/validate-agents.yml` | CI that fails if the spine markers or required sections get broken. Inherited by repos created from this template. | GitHub |
| `.github/workflows/claude-code-review.yml` | Optional CI that reviews PRs against the four pillars; no-ops until a credential secret exists. | GitHub |
| `memory/`, `skills/` | Scaffolds for persistent memories and user-level skills. | Claude Code |

Everything below the `update.sh` row is a **Claude Code bonus** — useful if you run Claude Code, safely ignorable otherwise. The instructions themselves are universal.

## Full Claude Code setup (optional)

To use the whole repo as your Claude Code home:

1. Install prerequisites: [Claude Code](https://claude.com/claude-code), plus `git`, `jq`, `node` (macOS: `brew install git jq node`).
2. Install it as your `~/.claude` (idempotent, backs up anything it touches):
   ```bash
   curl -fsSL https://raw.githubusercontent.com/YOU/YOUR-REPO/main/bootstrap.sh | bash -s -- https://github.com/YOU/YOUR-REPO.git
   ```
3. Start a new Claude Code session.

## The four pillars

Every piece of code, app, or infrastructure is held to **Security · Stability · Reliability · Compliance** — industry best practice, not personal taste. They're the default in `AGENTS.md` and the rubric the optional CI review uses. Edit them if your team's standard differs.

## Enabling the CI review (optional, Claude Code)

The PR-review workflow stays dormant (green no-op) until you add a credential secret per repo:

- **Claude Pro/Max** (no per-token billing): `claude setup-token`, then `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R YOU/REPO`
- **Or an API key:** `gh secret set ANTHROPIC_API_KEY -R YOU/REPO`

Also install the [Claude GitHub App](https://github.com/apps/claude). The workflow runs only on non-draft, same-repo PRs with comment-only tools.

## Customizing

- **`AGENTS.md`** — the placeholders are the minimum; add your stack conventions, repo patterns, and an optional brand/voice SSOT pointer (a commented template is included). Keep your edits **outside** the `SPINE` markers so `update.sh` never overwrites them.
- **`settings.json`** (Claude Code) — grow `permissions.allow`; tweak or remove either hook. The auto-format hook assumes Prettier.
- **Scheduled routines, MCP servers, plugins** are personal — add them on your machine; they aren't part of this shared template.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, make it your team's standard.
