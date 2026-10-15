# SLO Burn-Rate and CFR Rollback Runbook

Rules: `config/prometheus/rules/ufawkesobs-slo-burn-rate.yml` (#502).

The SLI is scrape availability (share of Prometheus targets that are `up`),
with a 99.5% / 30d objective. Alerts use multi-window burn rates, so each one
needs both a long window (sustained) and a short window (still happening).

<a id="fast-burn"></a>

## Fast burn — `SLOBurnRateFast` (critical)

14.4x burn over 1h and 5m. Find the down targets: `up == 0` in Prometheus.
Fix or restart the service; the alert resolves when the 5m window recovers.

<a id="medium-burn"></a>

## Medium burn — `SLOBurnRateMedium` (critical)

6x burn over 6h and 30m. Same triage as fast burn; usually a flapping target.

<a id="slow-burn"></a>

## Slow burn — `SLOBurnRateSlow` (warning)

3x burn over 1d and 2h. Open a ticket; look for a target that is down for
part of each day (cron restarts, host sleep).

<a id="absent"></a>

## `SLOBurnRateAbsent`

No `up` series at all, so the SLO is unmeasured. Check Prometheus itself.

<a id="cfr-rollback"></a>

## CFR rollback — `DORACFRRegressionRollback` (critical)

Fires when `dora_cfr_pct` (a 0-1 ratio) is above 0.30 **and** more than 0.10
above its 30-day average for 15m.

`.github/workflows/cfr-rollback.yml` polls this alert every 10 minutes from the
self-hosted runner. When it is firing it runs `scripts/rollback-latest-good.sh`
on the deploy host over SSH: checkout `deploy-latest-good`, `docker compose
--profile core up -d`, wait healthy, send a recovery DORA event. It is
read-only from git's perspective (no push, no revert), like the rollback job
in `deploy.yml`.

- **Off by default.** Set repository variable `CFR_AUTO_ROLLBACK_ENABLED=true`
  to enable it, only after the manual drill in `docs/ROLLBACK_DRILL.md` (#182)
  has passed on the live host.
- **No loop.** If the host is already on `deploy-latest-good` the script exits
  0 without redeploying, so a still-firing alert does nothing further.
- **Needs a tag.** With no `deploy-latest-good` tag the script exits 3 and the
  run fails visibly; recover manually per `docs/ROLLBACK_DRILL.md`.
- **Manual run.** Actions → CFR Rollback → Run workflow.
- Rolling back lowers CFR only after new deploys succeed, so the alert can stay
  firing for a while; investigate the failing change rather than waiting.

<a id="cfr-rollback-absent"></a>

## `DORACFRRegressionRollbackAbsent`

`dora_cfr_pct` is missing, so the rollback trigger cannot evaluate. See
`docs/runbooks/dora.md` (`up{job="dora-api"}`, dora-api logs).
