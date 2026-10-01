# DORA Alert Runbook

This runbook covers the DORA alerts defined in `config/prometheus/rules/ufawkesobs-dora-metrics.yml` and `ufawkesobs-dora-regression.yml`.

The DORA data path is:

- `dora-api` exposes the computed DORA metrics on `/metrics`
- Prometheus scrapes `dora-api:8088`
- `dora-compute` produces the deployment, lead-time, failure, and rework series
- The dashboard and alert rules consume the `dora:*` recording rules

When a DORA alert fires, first confirm whether the metric is genuinely low or absent because the compute pipeline stopped producing data. The most common root causes are a broken `dora` profile, a failed `dora-api` scrape, or an interrupted deploy-event flow.

<a id="deployment-frequency-low"></a>

## Deployment Frequency Low

### Trigger

`DORADeploymentFrequencyLow` fires when `dora:deployment_frequency:raw30d` stays below one deployment per 30 days.

### What to check

- `up{job="dora-api"}` and the `dora_deployment_frequency_per_week` series in Prometheus
- recent deploy events and the `dora` profile configuration
- whether the deploy-event pipeline is still recording successful pushes

### Triage steps

1. Verify the DORA profile is enabled and the service is healthy.
2. Check the last successful deploys in the repo or deployment tracker.
3. Confirm the deployment event flow still reaches `dora-api`.
4. If the data is absent or zeroed unexpectedly, validate the compute pipeline before treating it as a genuine shipping slowdown.

### Remediation

- Restore the deploy event pipeline or fix the DORA profile.
- Confirm the deployment source is still emitting valid events.
- If the team truly stopped shipping, resolve the operational blocker before resuming feature work.

<a id="deployment-frequency-absent"></a>

## Deployment Frequency Absent

### Trigger

`DORADeploymentFrequencyLowAbsent` fires when the raw deployment-frequency series disappears.

### What to check

- `absent(dora:deployment_frequency:raw30d)`
- `up{job="dora-api"}`
- recent `dora-api` logs and scrape health

### Triage steps

1. Check whether `dora-api` is up and scraping successfully.
2. Confirm the DORA profile and deploy-event flow are still active.
3. Verify the compute layer is still generating `dora_deployment_frequency_per_week`.

### Remediation

- Restart or repair `dora-api` if the metrics endpoint is unavailable.
- Recheck the deploy event source and fix the source/profile configuration.

<a id="lead-time-high"></a>

## Lead Time High

### Trigger

`DORALeadTimeHigh` fires when `dora:lead_time_hours:p50_30d` exceeds 24 hours.

### What to check

- merge-to-deploy timing and recent PR throughput
- review/test queue backlog
- DORA profile health and event flow for merge/deploy records

### Triage steps

1. Review recent PRs and merge-to-deploy timings.
2. Check whether large changes or review bottlenecks are slowing delivery.
3. Confirm the signal is still present and not a data-quality issue.

### Remediation

- Shorten review bottlenecks and reduce the size of in-flight changes.
- Fix any metric pipeline issue causing lead-time drift or gaps.

<a id="lead-time-absent"></a>

## Lead Time Absent

### Trigger

`DORALeadTimeHighAbsent` fires when the raw lead-time series is absent.

### What to check

- `absent(dora:lead_time_hours:raw_p50_30d)`
- DORA profile health
- `dora-api` scrape success

### Triage steps

1. Confirm the compute layer still emits lead-time metrics.
2. Check whether the DORA profile or metric path is misconfigured.
3. Verify deploy and merge event ingestion is still running.

### Remediation

- Restore the DORA compute pipeline and recheck the metrics scrape.

<a id="change-failure-rate-high"></a>

## Change Failure Rate High

### Trigger

`DORAChangeFailureRateHigh` fires when the change-failure rate exceeds 15%.

### What to check

- recent failed deploys or rollback events
- the deployment outcome stream in the DORA profile
- whether failed deploys are being labeled correctly

### Triage steps

1. Check the last few deployment outcomes and whether failed deploys are being classified correctly.
2. Review the DORA profile and deploy event flow for rollback/failure labeling problems.
3. Check whether one service or team is driving the elevated rate.

### Remediation

- Fix the root cause of repeated failed deploys before continuing feature work.
- Review deployment quality gate failures and slow down release cadence if needed.

<a id="change-failure-rate-critical"></a>

## Change Failure Rate Critical

### Trigger

`DORAChangeFailureRateCritical` fires when CFR exceeds 30%.

### What to check

- immediate deploy quality and release safety issues
- the deployment/failure classification pipeline
- the last failed deploys and rollback behavior

### Triage steps

1. Treat this as a release-risk escalation and stop broad feature work if needed.
2. Use the DORA profile and deploy-event flow to validate that the signal is real.
3. Investigate the most recent failed deployments and any rollback issues.

### Remediation

- Halt new feature work until the failure rate drops.
- Fix the deployment quality issue before resuming work.

<a id="change-failure-rate-absent"></a>

## Change Failure Rate Absent

### Trigger

`DORAChangeFailureRateHighAbsent` fires when CFR metrics disappear.

### What to check

- `absent(dora:change_failure_rate:raw_ratio30d)`
- `dora-api` scrape health
- whether the deployment outcome stream is still creating events

### Triage steps

1. Verify `dora-api` is still scraping.
2. Check whether the DORA profile or deploy parser has stalled.
3. Validate the success/failure deployment stream.

### Remediation

- Restore the deployment outcome feed and recheck the series.

<a id="fdrt-high"></a>

## FDRT High

### Trigger

`DORAFDRTHigh` fires when failed deployment recovery time exceeds 4 hours.

### What to check

- rollback and recovery timing after failed deploys
- deploy failure classification
- DORA profile health and the failed-deploy event stream

### Triage steps

1. Review the recent deployment failures and rollback actions.
2. Confirm the events reach `dora-api` and the metric is not stale or missing.
3. Inspect the `dora_fdrt_p50_hours` time series for sudden spikes or gaps.

### Remediation

- Shorten recovery time with faster rollback or stronger incident handoff.
- Fix developer or deployment path issues that delay recovery.

<a id="fdrt-absent"></a>

## FDRT Absent

### Trigger

`DORAFDRTHighAbsent` fires when FDRT metrics disappear.

### What to check

- `absent(dora:fdrt_hours:raw_p50_30d)`
- `dora-api` scrape health
- deployment failure/recovery events

### Triage steps

1. Confirm the failure/recovery event stream still reaches the compute layer.
2. Check the DORA profile and compute pipeline.
3. Verify the metrics endpoint is still serving values.

### Remediation

- Restore the deploy-failure event flow and recheck `dora-api`.

<a id="rework-rate-high"></a>

## Rework Rate High

### Trigger

`DORAReworkRateHigh` fires when AI rework rate exceeds 10%.

### What to check

- AI-generated changes requiring follow-up fixes
- `AGENTS.md` and `PROMPT_LIBRARY.md` quality
- recent model/provider changes or prompt regressions

### Triage steps

1. Inspect recent AI-generated diffs or review notes that required rework.
2. Compare the trend with the DORA profile and recent deployment or evaluation events.
3. Check whether a model or instruction change caused the spike.

### Remediation

- Tighten AI instructions and examples.
- Add or improve test-first and pre-commit guards for generated code.
- Reduce scope until the rework rate returns to a healthy band.

<a id="rework-rate-critical"></a>

## Rework Rate Critical

### Trigger

`DORAReworkRateCritical` fires when AI rework rate exceeds 20%.

### What to check

- the same rework signal as above, but at a severe level
- whether instructions and review practices still protect code quality

### Triage steps

1. Stop new AI-assisted feature work until the issue is understood.
2. Review instruction files and recent review patterns.
3. Confirm the metric is not a transient data-generation issue.

### Remediation

- Correct the instruction and review flow before resuming work.
- Re-run acceptance checks and targeted tests after each fix.

<a id="rework-rate-absent"></a>

## Rework Rate Absent

### Trigger

`DORAReworkRateHighAbsent` fires when the rework-rate series disappears.

### What to check

- `absent(dora:rework_rate:raw_ratio)`
- DORA profile health
- `dora-api` scrape health

### Triage steps

1. Check whether the rework metric generation path has stopped or misconfigured.
2. Validate the DORA profile and compute pipeline output.
3. Confirm `dora-api` is still scraping.

### Remediation

- Restore the rework metric generation path and recheck the `dora-api` scrape.

<a id="deployment-frequency-drop"></a>

## Deployment Frequency Drop

### Trigger

`DORARegressionDeploymentFrequencyDrop` fires when the 7-day average drops below 70% of the 30-day average.

### What to check

- short-term deploy downturn vs. baseline
- recent migration or release blockers
- whether the raw metric is missing or legitimately low

### Triage steps

1. Check the current deployment trend and whether it is a real throughput issue.
2. Review recent blocked change or migration work.
3. Reconfirm the DORA profile and event flow before concluding there is a real drop.

### Remediation

- Restore deploy throughput or remove the blocker causing the drop.

<a id="deployment-frequency-drop-absent"></a>

## Deployment Frequency Drop Absent

### Trigger

`DORARegressionDeploymentFrequencyDropAbsent` fires when `dora_deployment_frequency_per_week` is absent.

### What to check

- `absent(dora_deployment_frequency_per_week)`
- the compute pipeline feeding deployment metrics
- `dora-api` scrape health

### Triage steps

1. Verify the DORA profile and compute loop are still running.
2. Check the underlying deployment-event source.
3. Confirm the metrics endpoint is still serving values.

### Remediation

- Restart or repair the compute/export path so deployment metrics resume.

<a id="lead-time-increase"></a>

## Lead Time Increase

### Trigger

`DORARegressionLeadTimeIncrease` fires when the 7-day lead-time median exceeds 150% of the 30-day baseline.

### What to check

- queue buildup or approval delay
- recent change size and release delays
- whether the signal is valid or a data pipeline issue

### Triage steps

1. Compare the short-term lead-time pattern to the recent 30-day average.
2. Check for PR bottlenecks or slow review/test stages.
3. Confirm the data is not missing because of a pipeline problem.

### Remediation

- Remove the bottleneck in review or testing and reduce change size.

<a id="lead-time-increase-absent"></a>

## Lead Time Increase Absent

### Trigger

`DORARegressionLeadTimeIncreaseAbsent` fires when the lead-time metric is absent.

### What to check

- `absent(dora_lead_time_p50_hours)`
- underlying deployment and merge-event feed
- DORA profile health

### Triage steps

1. Verify data source availability.
2. Recheck the DORA profile and compute pipeline.
3. Confirm `dora-api` is still scraped.

### Remediation

- Repair the lead-time data source and verify the series returns.

<a id="fdrt-spike"></a>

## FDRT Spike

### Trigger

`DORARegressionFDRTSpike` fires when the current FDRT value doubles the 30-day average.

### What to check

- recovery time after failed deployments
- rollback execution path and change quality
- whether the metric is emitted correctly

### Triage steps

1. Review the failed deploy and recovery path.
2. Check whether the rollback or corrective action is delayed.
3. Confirm the DORA profile is intact and not dropping recovery data.

### Remediation

- Reduce mean time to recover by fixing the rollback flow and response process.

<a id="fdrt-spike-absent"></a>

## FDRT Spike Absent

### Trigger

`DORARegressionFDRTSpikeAbsent` fires when the FDRT metric is absent.

### What to check

- `absent(dora_fdrt_p50_hours)`
- DORA profile and deployment failure stream
- `dora-api` metrics endpoint

### Triage steps

1. Verify the failure/recovery event stream still reaches the compute layer.
2. Check the DORA profile and API scrape state.
3. Investigate any compute or exporter crash.

### Remediation

- Restore the compute/export path so FDRT is available again.

<a id="cfr-spike"></a>

## CFR Spike

### Trigger

`DORARegressionCFRSpike` fires when CFR rises more than 5 percentage points above the 30-day average.

### What to check

- recent deployment quality and rollbacks
- whether CFR is computed from the right event stream
- percentage/ratio conversion correctness

### Triage steps

1. Check the last several deployments and their outcomes.
2. Correlate with rollback or incident volumes.
3. Ensure the metric is interpreted as the correct ratio scale.

### Remediation

- Fix the failing deploy pattern and reduce release risk.

<a id="cfr-spike-absent"></a>

## CFR Spike Absent

### Trigger

`DORARegressionCFRSpikeAbsent` fires when the CFR metric is absent.

### What to check

- `absent(dora_cfr_pct)`
- DORA profile and deployment outcome stream
- `dora-api` scrape health

### Triage steps

1. Verify the deployment outcome stream is still ingesting success/failure data.
2. Check the DORA compute pipeline for a crash or misconfiguration.
3. Confirm the metrics endpoint remains live.

### Remediation

- Restore the deployment outcome path and revalidate the metric.

<a id="rework-rate-climb"></a>

## Rework Rate Climb

### Trigger

`DORARegressionReworkRateClimb` fires when rework rate rises more than 3 percentage points above the 30-day average.

### What to check

- recent AI-generated changes requiring follow-up fixes
- prompt and instruction quality
- whether the rework metric is computed correctly

### Triage steps

1. Review whether recent model or instruction changes are creating worse outputs.
2. Inspect PR-level rework and review comments.
3. Validate the metric is using the correct ratio scale.

### Remediation

- Adjust `AGENTS.md` and prompt guidance to reduce rework.
- Reduce AI scope until the trend stabilizes.

<a id="rework-rate-climb-absent"></a>

## Rework Rate Climb Absent

### Trigger

`DORARegressionReworkRateClimbAbsent` fires when rework-rate data disappears.

### What to check

- `absent(dora_rework_rate_pct)`
- the DORA profile and compute pipeline
- `dora-api` scrape health

### Triage steps

1. Verify the metric generation path still runs.
2. Check for a compute error or exporter issue.
3. Confirm `dora-api` is still scraped.

### Remediation

- Repair the compute/export path and validate the rework metric returns.
