# Upgrading from 0.4.x to 1.0.0

Written for anyone running a `0.4.x` beta who wants to reach `1.0.0`.

## Short version

**No manual steps are required.** Every `0.4.x` beta, from `v0.4.0-beta.1`
through `v0.4.11-beta.1`, has the same 1.0 public contract as `main`:

| Contract surface | Change from 0.4.x to 1.0.0 |
| ---------------- | -------------------------- |
| Compose service names | None |
| Compose profiles | None |
| Published ports | None |
| `.env.example` variables | None |
| Named volumes | None |

The contract is defined in
[`docs/ai-sdlc/v1.0.0/spec.md`](ai-sdlc/v1.0.0/spec.md). The comparison above
diffs `compose.yaml` and `.env.example` at `v0.4.0-beta.1` and
`v0.4.11-beta.1` against `main`. Re-run it against the `v1.0.0` tag before
release.

## Upgrade steps

```bash
git fetch --tags
git checkout v1.0.0
make up
./scripts/wait-healthy.sh
```

Your existing `.env` keeps working, and your data volumes are kept.

## What may look different

These changes are **outside** the 1.0 contract. A minor release can change
them, and the release notes will say when it does:

- **Image versions.** Pinned images (for example Tempo and alertmanager) moved
  forward during the betas. Compare `compose.yaml` if you build on a specific
  version.
- **Datasource UIDs, dashboard UIDs and DORA metric names.** The contract does
  not cover these. If you built dashboards or alerts on them, check them after
  the upgrade.
- **DORA storage.** DORA ingestion uses SQLite by default, with no external
  database required.

## Rolling back

```bash
git checkout v0.4.11-beta.1
make up
```

The contract is identical, so a rollback needs no other change.
