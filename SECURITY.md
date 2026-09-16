# Security Policy

Version-Timestamp: 2026-08-28 12:00:00 AST

## Report a vulnerability

Do not open a public issue for a vulnerability that could expose credentials, local files, account state, or unsafe configuration behavior. Contact the repository owner privately through the security contact listed in the repository settings, or use GitHub private vulnerability reporting when it is enabled.

Include the affected file or command, a safe reproduction, expected and actual behavior, impact, and any suggested mitigation. Do not include real credentials, customer data, browser cookies, or private configuration files.

## Supported boundary

The setup wizard must not read or store credentials, enable paid API fallback, install models, automate browser settings, or replace instruction files wholesale. Reports that show a violation of those boundaries are security-relevant.

## Public release review

Version-Timestamp: 2026-09-16 16:02:15 AST

Inspect every staged file for private instructions, personal profiles, company workflows, customer data and credentials before publishing. The automated public-content check covers only recognizable patterns and prohibited paths; it is not a full secret or history audit. Keep real evidence and backups outside this public repository. Existing runtime settings must remain untouched.

## Maintained secret scanning

Version-Timestamp: 2026-09-16 16:02:15 AST

CI uses the official [Gitleaks v8.30.1 release](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1). The Linux x64 archive is pinned to SHA256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`, checked against the upstream release metadata before adoption. CI verifies this digest before execution. Updates require reviewing the upstream publisher, release and new digest.

The scanner reads the public checkout and available Git history locally in the CI runner with redacted output. It does not require a provider token, paid API, or findings upload. `release-checks` requires both the platform tests and scans to pass. This third-party scanner finds known secret patterns; it cannot certify that prose contains no confidential information. Human review remains required.

Local previews and installation records can contain private instruction text and absolute paths. Keep them on the computer where they were generated. Do not attach them to public bug reports. Preview hashes detect changed content; they are not signed approvals or protection against a hostile local user modifying files concurrently.
