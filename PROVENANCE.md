# Provenance

Version-Timestamp: 2026-09-16 15:27:25 AST

This is a public, generic configuration template. Reusable operating practices are adapted through review; private configuration, company workflows, customer records, personal machine paths and credentials must not be copied into it.

`AGENTS.md` contains the portable instruction spine. `CLAUDE.md` is a regular text file importing it with `@AGENTS.md`, not a symlink. Apps differ in instruction discovery and precedence; the setup wizard generates native adapters for selected tools. Forks are independent and do not synchronize back to the maintainer.

`approved-skills.json` identifies six optional reusable workflows and pins their public source commit and license. These are references only. The `skills/` directory contains no bundled skills. Scoped review does not establish universal fitness or authorize tool access. Private or experimental skills are excluded.

Changes to the template require behavior tests, a public-content review and cross-platform CI. Do not regenerate it by copying a live home directory or private repository wholesale.
