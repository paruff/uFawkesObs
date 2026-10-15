# SLO Burn-Rate Runbook

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
