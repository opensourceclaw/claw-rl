# Security Policy

## Reporting

Report vulnerabilities via [GitHub Security Advisories](https://github.com/opensourceclaw/claw-rl/security/advisories/new).
Do not file a public issue.

## Supported Versions

| Version | Status |
|---------|--------|
| v2.x | ✅ Active |
| v1.x | ⚠️ Maintenance only |

## Architecture

claw-rl operates as a local-first reinforcement learning system with zero
network overhead for learning operations. The stdio JSON-RPC bridge ensures
all learning data stays local.
