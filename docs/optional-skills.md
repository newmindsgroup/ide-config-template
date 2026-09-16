# Optional skills: choose only what you need

Version-Timestamp: 2026-09-16 16:02:15 AST

The template works without installing any skills. Its catalog recommends six public, reusable workflows. Recommendations do not grant permission to send messages, access accounts, install dependencies, or share confidential information.

## Approved scope

| Skill | Use when you need | Plugin group |
|---|---|---|
| `customer-research` | Interview plans and synthesis of customer evidence | marketing-growth-curated |
| `cold-email` | Draft prospecting emails for human review | marketing-growth-curated |
| `lead-magnets` | Plan a useful resource for a specific audience | marketing-growth-curated |
| `content-strategy` | Choose topics and build an editorial plan | marketing-growth-curated |
| `copy-editing` | Improve existing copy for clarity and consistency | marketing-growth-curated |
| `business-model-designer` | Compare customers, value, costs and revenue assumptions | business-strategy-curated |

The exact source links and review qualification are in [approved-skills.json](../approved-skills.json). All six links pin source commit `db563b1da6ec6e16a66e4174242845de16e16c1c`. Review covered reusable instructions and narrow synthetic tests. It does not prove that every workflow fits your work or that future versions are safe.

## Add one reviewed skill to one project

1. Open that skill's pinned source link in the catalog. Read `SKILL.md`, referenced files, scripts, permissions, and license before use. Do not substitute a current branch or an unreviewed marketplace package.
2. Check your existing skills and plugins for the same workflow. Keep one maintained owner for the capability. If an existing equivalent works, stop here.
3. Download only that reviewed skill folder and its required references. Keep its license and attribution. Do not run downloaded scripts or install dependencies as part of copying instructions.
4. Choose the project-local destination below. If the destination already exists, compare it manually and keep a backup outside the active skill directory. Do not overwrite or merge blindly.
5. Start a fresh session in the selected app. Confirm the skill is discoverable, invoke it explicitly on a small synthetic example, and inspect its result before using it for real work.
6. Record the skill name, source commit, license, app, and test result in a project record. Store private skill adaptations in a private project repository, never this public template.

| App | Project-local skill destination | Authoritative reference |
|---|---|---|
| OpenAI Codex | `.agents/skills/<skill-name>/SKILL.md` | [Codex skills](https://developers.openai.com/codex/skills/) |
| Claude Code | `.claude/skills/<skill-name>/SKILL.md` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Cursor | `.cursor/skills/<skill-name>/SKILL.md` | [Cursor skills](https://cursor.com/docs/context/skills) |

Use one destination per project. Current Cursor versions also discover `.agents/skills`, so a reviewed shared Codex/Cursor skill can live there without a duplicate `.cursor/skills` copy. Verify discovery in each app before sharing that folder. A compatible file location does not prove the skill's tool references work in that app. If your installed version lacks skill discovery or a required tool, keep the workflow as a reference document and do not claim it is installed.

To remove an optional skill, delete only the folder you added after confirming it contains no later work you need. This wizard never installs, updates, removes, or backs up optional skill folders.

## Updates and public sharing

Review each proposed version change and repeat the small acceptance test before adoption. The template does not follow upstream skill updates automatically. Private company processes, customer data, brand rules, account details, and experimental skills stay in private project repositories. Even a reviewed instruction can produce poor output or request an unsuitable action; normal project approval and data-handling rules still apply.
