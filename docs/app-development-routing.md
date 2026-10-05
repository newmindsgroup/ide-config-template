# Quality-first web and mobile app guidance

Version-Timestamp: 2026-10-05 19:34:30 AST

The wizard generates instructions, not an executable router. It does not install
`llm-route`, a Claude runner, model selectors, accounts, quotas or paid services.
Native mobile toolchains and device acceptance remain project-specific.

## Opt in on each destination

Use the scan and reviewed plan/apply workflow with these optional JSON booleans:

```json
{
  "app_quality_first": true,
  "sol_current_available": false,
  "opus_current_available": false
}
```

All three default false. Existing profiles remain valid. Missing access means
pending or a confirmed Astra route; no declaration is inferred from subscription
ownership. Strict schema rejects unknown fields and non-boolean access values.
The fixed fields refer to GPT-6.1 Sol and `claude-opus-5-5`, not arbitrary model IDs.
Legacy `opus_available` continues to refer to Opus 5 and cannot authorize Opus 5.5.
General synthesis keeps the existing Fable/Opus guidance. The app profile adds a
separate app-code recommendation and does not migrate legacy declarations.

Verify exact subscription execution through the intended current client before
setting either current-model flag true. Reconfirm after client, account or model
changes. A picker entry alone is insufficient. Maintainer-observed execution used
Codex CLI 0.160.0 and Claude Code 2.1.287. Those are conservative tested versions,
not claims about vendor minimums or proof that newer clients have identical behavior.

Claude review also requires declared Claude subscription and
`claude_extra_usage_off: true`. Check included usage and Usage credits OFF within
24 hours of the task and after account, plan or model changes. Declarations are
self-attestations. The wizard does not verify billing live or enforce receipt expiry.
Never copy another person's confirmations, account receipt or authentication.

## Recommendations and acceptance

| App task | Provisional route after access verification |
|---|---|
| Explicitly bounded implementation | GPT-6.1 Sol Medium |
| Complex or ambiguous development | Astra Medium |
| Auth, permissions, PII, payments, migrations or releases | Astra High |
| Focused independent app-code review | Opus 5.5 Medium |
| Complex or consequential independent app-code review | Opus 5.5 High |

Unavailable routes stay pending or require an explicitly approved substitute.
Sol and Astra share affected OpenAI allowance; switching between them does not
reset it. Checkpoint before provider handoff and never replay uncertain writes.
Sonnet 5.5 remains a candidate until destination and task validation establish it.
These are provisional choices, not a universal benchmark winner. Measure ten real
tasks using accepted checks, repairs and elapsed time before revising defaults.

Confidential source needs project-specific approval for the chosen provider.
This profile grants none. Keep approved requirements, tests, security checks,
accessibility, licenses, recovery and actual returned models in project packets.
Render web UI at desktop/mobile widths; test loading/error/focus/keyboard states.
Mobile apps also need their native build, simulator/device and store acceptance.
No model guarantees perfect or bug-free code. Reviews do not authorize deployment.

Design evidence stays project-local. Record feedback source, outcome and checks;
promote shared methods only after repeated results, without publishing client evidence.
The managed blocks retain preview, explicit apply, backup, preservation and removal
behavior. The generated IDE and web instructions describe the same app profile.

## References

[Claude model configuration](https://code.claude.com/docs/en/model-config) explains
exact IDs and changing vendor aliases. [Claude usage credits](https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans)
explains optional usage beyond included limits. Check official documentation and the
actual account rather than assuming every recipient has the same entitlement.

## Rolling back to an older checkout

Version 1.5.0 rejects the new profile keys. Before using an older wizard to remove
managed instructions, provide an explicit minimal profile with only legacy fields
(for example `{"ides": ["codex", "claude", "cursor", "antigravity"]}`). Use that
file with `--plan-remove --profile <minimal-profile>` and the reviewed removal with
`--remove-managed-block --confirm --profile <minimal-profile>`. Keep the original
profile and installation registry backed up. Do not delete an entire app directory.
Each client, including web, needs its own access verification before using guidance.
