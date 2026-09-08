# Efficient routing on your computer

Version-Timestamp: 2026-09-08 18:51:27 AST

## Selective prompt refinement and planning

For substantial work, establish a short task brief: outcome, constraints, relevant evidence and acceptance checks. Reuse clear requirements; do not create a separate self-prompt by default.

Use `prompt-engineering-expert` for prompts/instructions as deliverables, complex bounded handoffs, conflicting requirements needing an execution contract, or evidence of instruction-caused failure. Ordinary coding, design, writing or tool failures alone do not trigger it. Refine once, then execute; revisit only for changed requirements or demonstrated misunderstanding. Preserve intent, privacy and authorization.

Recommend Plan mode for unresolved consequential decisions, broad cross-system changes or costly-to-reverse work. Clear bounded tasks proceed directly; a short checklist needs no mode switch. Never claim prose changed the app mode. Planning grants no implementation or deployment authority.

Resolve consequential decisions with the user before execution, regardless of mode. Neither refinement nor planning automatically raises effort, calls another model or replaces real checks. These are agent-followed rules, not a guaranteed runtime interceptor.

The wizard recommends Astra Low and Standard only when you confirm access. Raise effort when task difficulty, failed attempts or consequence justify it. Availability and subscriptions are destination-specific.

With confirmed included Claude access and extra usage disabled, prefer Fable 5.1 Medium for substantial bounded synthesis, High for complex/consequential work, and Opus 5 for smaller focused reviews. Use one reviewer at a meaningful milestone, a second attempt only for justified new evidence, and stop on persistent failure. These are generated instructions, not executable counters or automatic provider switching.

Keep essential safety, privacy, brand and validation rules. Move specialized recipes into clearly scoped skills loaded only when relevant. Save approved plans, decisions, checks and next steps in project files. Never store credentials or upload private plans to a new service without approval.

Measure ten real completed tasks: opaque ID, model, effort, acceptance, elapsed time and repairs. Optional subscription usage changes are approximate and may include concurrent work. Do not repeat paid work just to benchmark. Test installed local models on your hardware before treating them as reliable fallbacks. Never automatically download models or enable paid APIs.

Prefer APIs/CLIs for deterministic work, browser/computer control when needed, and rendered desktop/mobile evidence for UI changes. At significant milestones, identify up to three blind spots and one next action, not an endless review loop.

The private runtime's SQLite review counter, scorecard and benchmark are not installed by this public wizard. This repository generates portable instructions and manual web guidance. It does not change active model selectors, entitlements or remote access.

Sources: [OpenAI skills](https://learn.chatgpt.com/docs/build-skills), [Claude context and costs](https://code.claude.com/docs/en/costs), [agent evaluation](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), [Ollama context](https://docs.ollama.com/context-length).
