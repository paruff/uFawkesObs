# Plan: replace the alertmanager-discord bridge with native discord_configs

**Traces to:** #474 (clear fixable CRITICAL trivy findings so the image-scan gate can block)

## Changes

1. `compose.yaml`: remove the `alertmanager-discord` service (`rogerrum/alertmanager-discord:1.0.7`,
   `notifications` profile). 1.0.7 is its latest release and carries Go stdlib CVE-2025-68121.
2. `config/alertmanager/alertmanager.yml`: the commented Discord recipe now uses Alertmanager's
   native `discord_configs` with `webhook_url_file`, so the webhook URL stays out of the config.
   The recipe stays commented out by default.
3. `.env.example`: drop `DISCORD_WEBHOOK_URL` (the bridge was its only consumer);
   `.gitignore`: ignore `config/alertmanager/discord_webhook_url`.
4. Tests and docs updated to match (version table, healthcheck exemption list, Discord recipe tests,
   operations guide, architecture, impact map, known limitations).

No default behaviour changes: the Discord receiver was never enabled out of the box.

## Verification Strategy

| Criterion                                 | Evidence                                                   | How                                                                                          |
| ----------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Native receiver is valid on our version   | `amtool check-config` accepts a `discord_configs` receiver | Ran amtool from `prom/alertmanager:v0.34.1` against a minimal config with `webhook_url_file` |
| Shipped config still valid                | `make validate-alertmanager` passes                        | Ran locally                                                                                  |
| Compose is consistent without the service | `docker compose --profile '*' config` valid                | Ran locally                                                                                  |
| Unit tests reflect the new recipe         | 663 unit tests pass                                        | `pytest tests/unit` in a clean venv                                                          |
| Image gate no longer sees the CVE         | No `alertmanager-discord` image left to scan               | `docker compose config --images`                                                             |
| Not covered                               | A live Discord delivery                                    | Needs a real webhook; the recipe stays opt-in and untested end to end                        |
