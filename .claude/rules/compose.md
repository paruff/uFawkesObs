---
paths:
  - compose.yaml
---

# compose.yaml Rules

- All service image versions must be **pinned** — no `latest` tags ever.
- Secrets and passwords go in `.env` (gitignored) — never in `compose.yaml`.
- All services must have `healthcheck:` defined, **except**:
  - The image is **distroless** (no shell, no curl, no wget, no python), **AND**
  - The image binary itself provides no health-query subcommand (`validate`, `status`, etc.).
  - When removing a healthcheck, document in the PR description: the image
    name, why it's distroless, and the alternative approach used
    (`condition: service_started`, metrics endpoint, etc.).
- Networks must be explicitly declared — no implicit default network.
- Volumes for persistent data must be named, not anonymous.
- Profiles (`core`, `dora`) must be explicit and validated with
  `docker compose --profile <name> config`.

## Requires PM sign-off before changing (AGENTS.md §5)

Image versions, adding/removing services, exposed port numbers, volume mount
paths, new environment variables.
