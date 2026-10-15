# CFR Rollback Runbook

Alert: `DORACFRRegressionRollback` in `config/prometheus/rules/ufawkesobs-dora-regression.yml` (#502).

Fires when `dora_cfr_pct` (a 0-1 ratio) is above 0.30 **and** more than 0.10
above its 30-day average for 15m.

`.github/workflows/cfr-rollback.yml` polls the alert every 10 minutes from the
self-hosted runner. When it is firing it runs `scripts/rollback-latest-good.sh`
on the deploy host over SSH: checkout `deploy-latest-good`, `docker compose
--profile core up -d`, wait healthy, send a recovery DORA event. Read-only from
git's perspective (no push, no revert), like the rollback job in `deploy.yml`.

- **Off by default.** Set repository variable `CFR_AUTO_ROLLBACK_ENABLED=true`
  only after the manual drill in `docs/ROLLBACK_DRILL.md` (#182) has passed.
- **No loop.** If the host is already on `deploy-latest-good` the script exits 0
  without redeploying.
- **Needs a tag.** With no `deploy-latest-good` tag the script exits 3 and the
  run fails visibly; recover manually per `docs/ROLLBACK_DRILL.md`.

<a id="absent"></a>

## `DORACFRRegressionRollbackAbsent`

`dora_cfr_pct` is missing, so the trigger cannot evaluate. See
`docs/runbooks/dora.md` (`up{job="dora-api"}`, dora-api logs).
