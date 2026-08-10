# Support — uFawkesObs

## Where to get help

| Channel | Best for | Response target |
|---|---|---|
| [GitHub Discussions](https://github.com/paruff/uFawkesObs/discussions) | Questions, ideas, show-and-tell | Best effort, typically within a few days |
| [GitHub Issues](https://github.com/paruff/uFawkesObs/issues) | Confirmed bugs and feature requests | Triaged within 5 business days |
| [KNOWN_LIMITATIONS.md](./docs/KNOWN_LIMITATIONS.md) | Known issues and workarounds | Read first — may already be documented |

**Please do not use GitHub Issues for support questions.** Issues are for
confirmed bugs and tracked feature work. Questions in the issue tracker tend
to go unanswered and clutter the backlog for everyone.

---

## Before asking

Check these resources first — most common problems are already documented:

1. **[README.md](./README.md)** — Quick Start, health checks, troubleshooting section
2. **[docs/KNOWN_LIMITATIONS.md](./docs/KNOWN_LIMITATIONS.md)** — Single-instance constraints, permission issues, port conflicts
3. **[docs/production-hardening.md](./docs/production-hardening.md)** — Permission and UID issues in particular
4. **[docs/CHANGE_IMPACT_MAP.md](./docs/CHANGE_IMPACT_MAP.md)** — If something broke after a config change

If you've read the relevant doc and are still stuck, a Discussion thread is
the right place.

---

## How to write a useful question

Include:

- **Operating system and Docker version** (`docker --version`, `docker compose version`)
- **The exact command you ran**
- **The exact error output** (paste it, don't paraphrase)
- **Output of `docker compose ps`** at the time of the failure
- **Output of `docker compose logs [service-name]`** for the failing service

Questions without this information will be asked for it before we can help,
which slows things down for everyone.

---

## Response expectations

uFawkesObs is maintained by a small team. We are committed to:

- **Triaging new issues** within 5 business days
- **Responding to Discussions** on a best-effort basis
- **Shipping a release** on a regular cadence (see [CHANGELOG.md](./CHANGELOG.md))

We are not able to offer:

- Real-time or guaranteed SLA support
- Custom configuration help for heavily modified deployments
- Support for versions of Docker or compose older than those listed in the README prerequisites

---

## Paying it forward

If you solve a problem that isn't documented, please open a PR to add it to
[docs/KNOWN_LIMITATIONS.md](./docs/KNOWN_LIMITATIONS.md) or the README
troubleshooting section. The next person with the same issue will thank you.

---

## Security issues

Do not report security vulnerabilities in Discussions or Issues.
See [SECURITY.md](./SECURITY.md) for the private disclosure process.
