# Security Policy — uFawkesObs

## Supported versions

| Version | Supported |
|---|---|
| `main` branch | ✅ Active — patches applied here first |
| Tagged releases | ✅ Critical fixes backported where practical |
| Older releases | ❌ No active support |

We follow [Semantic Versioning](https://semver.org). The first stable release
is `v0.1.0`. Check [CHANGELOG.md](./CHANGELOG.md) for what each release
contains.

---

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report privately using one of these channels, in order of preference:

1. **GitHub private vulnerability reporting** (preferred):
   [Security → Report a vulnerability](https://github.com/paruff/uFawkesObs/security/advisories/new)
   — this keeps the report confidential until a fix is published.

2. **Email**: Contact the maintainer via the email address on the
   [paruff GitHub profile](https://github.com/paruff). Use the subject line
   `[uFawkesObs] Security report`.

Include in your report:

- Affected component (e.g. Prometheus config, Grafana provisioning, Makefile)
- Steps to reproduce or a minimal proof of concept
- Your assessment of severity and impact
- Whether you have already disclosed this elsewhere

---

## Response timeline

| Stage | Target |
|---|---|
| Acknowledgement | Within 72 hours of receipt |
| Initial triage and severity assessment | Within 5 business days |
| Fix or mitigation published | Depends on severity (see below) |
| Public disclosure | After fix is available, coordinated with reporter |

**Severity guidelines:**

- **Critical** (CVSS ≥ 9.0): fix targeted within 7 days
- **High** (CVSS 7.0–8.9): fix targeted within 14 days
- **Medium / Low**: addressed in the next scheduled release

We will credit reporters in the release notes and CHANGELOG unless you
request anonymity.

---

## Scope

This policy covers the uFawkesObs repository and its default configuration.
It does not cover:

- Third-party components (Prometheus, Grafana, Loki, Tempo, Alertmanager,
  OpenTelemetry Collector, Alloy). Report upstream vulnerabilities to those
  projects. We will update pinned versions promptly when upstream patches
  are available.
- Deployments where users have modified the default configuration.
- The broader [Fawkes IDP](https://github.com/paruff/fawkes) suite — each
  repo has its own security policy.

---

## Security design notes

These are known constraints in this release. They are documented here rather
than treated as vulnerabilities:

**Single-instance, no multi-tenancy.** All telemetry shares one Prometheus,
Loki, and Tempo instance. Isolation between teams or applications is not
provided. Do not use this stack where tenant isolation is a requirement.

**Credentials in `.env`.** The `.env` file is the credential boundary.
`.env.example` contains only placeholder values; the startup validation in
`make check-env` blocks deployment if defaults are detected. Never commit a
populated `.env` to version control.

**No TLS in the default configuration.** All inter-service communication is
plaintext on localhost. See [docs/production-hardening.md](./docs/production-hardening.md)
for TLS configuration guidance before exposing any port outside localhost.

**Grafana anonymous access is disabled by default.** Authentication is
required for all dashboard access.

---

## Dependency management

Image versions are pinned in `compose.yaml`. We review upstream release notes
for security advisories and update pinned versions as part of each release
cycle. If a critical upstream vulnerability is published between releases, we
will cut a patch release.

To check for outdated images in your local deployment:

```bash
docker compose pull --dry-run
```

---

## AI-generated code policy

See [AI_STANCE.md](./AI_STANCE.md). AI-generated Prometheus alerting rules
and Grafana provisioning configs require human review before merge — alerts
trigger real pagers, and false positives have real cost.
