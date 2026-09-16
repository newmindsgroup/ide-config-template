# Security Policy

Version-Timestamp: 2026-08-28 12:00:00 AST

## Report a vulnerability

Do not open a public issue for a vulnerability that could expose credentials, local files, account state, or unsafe configuration behavior. Contact the repository owner privately through the security contact listed in the repository settings, or use GitHub private vulnerability reporting when it is enabled.

Include the affected file or command, a safe reproduction, expected and actual behavior, impact, and any suggested mitigation. Do not include real credentials, customer data, browser cookies, or private configuration files.

## Supported boundary

The setup wizard must not read or store credentials, enable paid API fallback, install models, automate browser settings, or replace instruction files wholesale. Reports that show a violation of those boundaries are security-relevant.

## Public release review

Version-Timestamp: 2026-09-16 15:27:25 AST

Inspect every staged file for private instructions, personal profiles, company workflows, customer data and credentials before publishing. The automated public-content check covers only recognizable patterns and prohibited paths; it is not a full secret or history audit. Keep real evidence and backups outside this public repository. Existing runtime settings must remain untouched.
