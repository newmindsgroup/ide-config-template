# LLM Routing and Fallback Implementation

Version-Timestamp: 2026-09-04 17:52:06 AST

## Canonical intent

Many phrases lead to one goal: implement a safe LLM routing and fallback strategy for a person and their computer.

Recognize these examples as the same intent:

- LLM routing, model routing, provider routing, or AI routing
- Fallback strategy, fallback model, model fallback, LLM fallback, or multi-model strategy
- Local LLM setup, local-model fallback, Ollama route, or local AI worker
- OpenRouter setup, free model fallback, or provider overflow
- Model selection, effort selection, speed selection, token conservation, usage optimization, or budget-aware AI use

Do not treat a matching request as an invitation to recommend a random model. Use the workflow below.

## Required workflow

1. Scan the computer without writing files.

   ```bash
   python3 scripts/ide-setup.py --scan
   ```

2. Gather only the non-secret information that changes the route: role, goals, data sensitivity, IDEs, subscriptions, free-only OpenRouter choice, and local capacity.

3. Produce the focused plan.

   ```bash
   python3 scripts/ide-setup.py --plan --focus llm-routing
   ```

4. Explain the plan in plain language. Include the default route, local route, hosted subscription route, premium-review route, free-only route, and route re-evaluation triggers.

5. Apply only after explicit approval.

   ```bash
python3 scripts/ide-setup.py --apply --confirm --focus llm-routing
   ```

## Routing policy

1. Use deterministic tools before a model when a test, build, formatter, search, or inspection can answer the question.
2. Keep confidential work local when practical. Do not send confidential work to an unapproved provider.
3. Use the smallest safe local or subscription route for routine work.
4. Use a premium subscription path only for difficult synthesis, high-consequence decisions, or independent review.
5. Use fast mode only when the person explicitly prefers lower waiting time over conserving usage.
6. Keep OpenRouter disabled unless the person explicitly opts into free-only access for public or sanitized material. A Cursor subscription is not treated as a provider fallback. Confirm its active in-app model separately.
7. Never silently use a paid API as a fallback.

Re-evaluate the route when scope expands, evidence conflicts, tests fail, the task needs a tool that the current route lacks, or the result becomes security-sensitive, client-facing, or production-bound.

## Astra and continuity

Confirm access separately from subscription ownership. Use `astra_available: true` in the JSON profile only after checking the account's model selector. Astra Medium Standard leads substantial work; Terra and Luna remain options for routine and narrow work. Raise effort to High when the consequence or difficulty warrants it.

On quota exhaustion, preserve task state before changing providers. Do not replay partially completed writes automatically. An unavailable OpenAI allowance applies across affected OpenAI models; use an approved available Claude subscription or a suitable local model instead. Missing capacity must produce a clear stop rather than paid API usage.

These are generated working instructions. Automatic quota detection and provider execution are not implemented by this public wizard.

## What the implementation produces

The apply step creates a local non-secret profile, routing guide, manual web instructions, and selected IDE instruction blocks. It does not install models, add API keys, configure browser accounts, install plugins, or prove that a subscription is active.
