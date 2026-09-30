# DORA Alert Runbook

This runbook covers the DORA metric alerts in `config/prometheus/rules/ufawkesobs-dora-metrics.yml` and `ufawkesobs-dora-regression.yml`.

The DORA data flow is:

- `dora-api` exposes the computed metrics (`/metrics`)
- Prometheus scrapes `dora-api:8088`
- `dora-compute` builds the deployment, lead-time, failure, and rework series
- The DORA dashboard and alert rules consume the `dora:*` recording rules

If a DORA alert fires, treat it as a production signal that the deployment pipeline or data quality is degraded.

## Deployment Frequency Low

### Trigger
`DORADeploymentFrequencyLow` fires when `dora:deployment_frequency:raw30d` stays below one deployment per 30 days.

### What to check
- Confirm `dora-api` is still scraping and exporting metrics to Prometheus.
- Check the `dora` profile and recent deploy event flow (`deploy`, `deploy-status`, or equivalent deployment events).
- Confirm that deployment events are still reaching `dora-api` and that the `team_id` label is present.
- Inspect the `dora:deployment_frequency:raw30d` time series in Grafana/Prometheus.

### Triage
1. Verify the DORA profile is enabled and the service is healthy.
2. Check the last successful deploys in the repo or deployment tracker.
3. Check the dora-api scrape target: `up{job="dora-api"}` and `dora_deployment_frequency_per_week`.
4. If no data is flowing, verify the dora-compute/deploy event pipeline before treating the alert as a genuine business slowdown.

### Remediation
- Restore the deploy event ingestion path.
- Confirm the deploy pipeline still emits valid deployment events.
- If the team truly stopped shipping, treat it as a change-management issue and resolve the blocker before resuming feature work.

## Deployment Frequency Absent

### Trigger
`DORADeploymentFrequencyLowAbsent` fires when the raw deployment-frequency series disappears.

### What to check
- `absent(dora:deployment_frequency:raw30d)`
- `up{job="dora-api"}`
- Recent `dora-api` logs and scrape health

### Triage
1. Check whether `dora-api` is up and scraping successfully.
2. Check the DORA profile configuration and whether the service has restarted.
3. Confirm the compute pipeline is still generating `dora_deployment_frequency_per_week`.

### Remediation
- Restart or repair `dora-api` if the metrics endpoint is unreachable.
- Recheck the deploy event source and the profile that feeds DORA metrics.

## Lead Time High

### Trigger
`DORALeadTimeHigh` fires when `dora:lead_time_hours:p50_30d` exceeds 24 hours.

### What to check
- Review recent PRs and merge-to-deploy durations.
- Check whether review/testing queues slowed down.
- Examine the lead-time metric trend and whether it is a real throughput problem or a missing/miscomputed data issue.

### Triage
1. Check the DORA profile and the source deploy/merge events feeding lead-time calculation.
2. Review the last few PRs or merge events for unusually large changes or blocked review processes.
3. Confirm the metric remains present and correct after the deploy flow recovers.

### Remediation
- Shorten review bottlenecks and reduce the size of in-flight changes.
- Fix any data pipeline gap causing the series to misreport.

## Lead Time Absent

### Trigger
`DORALeadTimeHighAbsent` fires when the raw lead-time series is absent.

### What to check
- `absent(dora:lead_time_hours:raw_p50_30d)`
- DORA profile health
- Scrape success from `dora-api`

### Triage
1. Confirm the compute layer still emits lead-time metrics.
2. Check if the metric path or profile is misconfigured.
3. Verify deploy and merge event ingestion is running.

### Remediation
- Restore the DORA compute pipeline and recheck the scrape target.

## Change Failure Rate High

### Trigger
`DORAChangeFailureRateHigh` fires when the change-failure rate exceeds 15% for the configured window.

### What to check
- Recent failed deploys or rollback events.
- Whether the deployment signal quality is valid.
- Whether the DORA profile is still recording successful and failed deploys.

### Triage
1. Check the last few deployment outcomes and whether failed deploys are being classified correctly.
2. Review the DORA profile and deploy event flow for rollback or failure labeling errors.
3. Check whether only a single service or team is impacted.

### Remediation
- Fix the root cause of repeated failed deploys before continuing feature work.
- Review deployment quality gate failures and slow down release cadence if needed.

## Change Failure Rate Critical

### Trigger
`DORAChangeFailureRateCritical` fires when CFR exceeds 30%.

### What to check
- Immediate deploy quality and release safety issues.
- The underlying deployment/failure classification pipeline.
- Whether a team or service is effectively failing most releases.

### Triage
1. Stop feature work if the critical threshold is reached.
2. Use the DORA profile and deploy-event flow to verify the metric is not a data artifact.
3. Investigate the last failed deployments and rollback behavior.

### Remediation
- Halt new features until the failure rate drops.
- Fix the deployment quality issues and revalidate after the data stabilizes.

## Change Failure Rate Absent

### Trigger
`DORAChangeFailureRateHighAbsent` fires when CFR metrics disappear.

### What to check
- `absent(dora:change_failure_rate:raw_ratio30d)`
- `dora-api` scrape health
- Whether the deployment outcome stream is still generating events

### Triage
1. Verify `dora-api` is still scraping.
2. Check whether the DORA profile or deploy parser is failing.
3. Validate the deploy success/failure event stream.

### Remediation
- Restore the deployment outcome feed and recheck the series.

## FDRT High

### Trigger
`DORAFDRTHigh` fires when the failed deployment recovery time exceeds 4 hours.

### What to check
- Check recovery and rollback timing after failed deploys.
- Verify whether deployment failures are being classified and recovered consistently.
- Review the DORA profile to ensure the failed deployment and recovery events are attributed correctly.

### Triage
1. Review the recent deployment failures and rollback actions.
2. Confirm the events are making it through the deployment flow into `dora-api`.
3. Inspect the `dora_fdrt_p50_hours` series for sudden spikes or gaps.

### Remediation
- Reduce recovery time with faster rollback or incident handoff.
- Fix reliability issues in the deployment path that cause prolonged recovery time.

## FDRT Absent

### Trigger
`DORAFDRTHighAbsent` fires when FDRT metrics disappear.

### What to check
- `absent(dora:fdrt_hours:raw_p50_30d)`
- `dora-api` scrape health
- Deployment failure/recovery events

### Triage
1. Confirm the source deployment event flow still emits failure/recovery markers.
2. Check the DORA profile and compute pipeline.
3. Verify the metrics endpoint is still returning values.

### Remediation
- Restore the deploy-failure event pipeline and recheck `dora-api`.

## Rework Rate High

### Trigger
`DORAReworkRateHigh` fires when AI rework rate exceeds 10%.

### What to check
- Which AI-generated changes were reworked or corrected after review.
- Instruction quality in `AGENTS.md` and `PROMPT_LIBRARY.md`.
- Any model/provider drift or prompt regression.

### Triage
1. Inspect recent AI-generated diffs or review notes that required rework.
2. Compare against the DORA profile and recent deploy or evaluation events.
3. Check whether model changes or prompt updates caused a spike.

### Remediation
- Tighten instructions and examples for AI-generated changes.
- Add or improve pre-commit/test gating for generated code.
- Reduce scope until rework rate returns to a healthy band.

## Rework Rate Critical

### Trigger
`DORAReworkRateCritical` fires when AI rework rate exceeds 20%.

### What to check
- The same rework signal as above, but at a severe level.
- Whether instructions and review flow are still protecting code quality.

### Triage
1. Stop new AI-assisted feature work until the issue is understood.
2. Review instruction files and prior review patterns.
3. Confirm the metric is not a transient data-generation issue.

### Remediation
- Correct the instructions and review flow before resuming work.
- Re-run acceptance checks and targeted tests after each fix.

## Rework Rate Absent

### Trigger
`DORAReworkRateHighAbsent` fires when the rework-rate series disappears.

### What to check
- `absent(dora:rework_rate:raw_ratio)`
- DORA profile health
- `dora-api` scrape health

### Triage
1. Check whether the rework metric generation path is stopped or misconfigured.
2. Validate the DORA profile and compute pipeline output.
3. Reconfirm the metrics endpoint is live.

### Remediation
- Restore the rework metric generation path and recheck the `dora-api` scrape.

## Deployment Frequency Drop

### Trigger
`DORARegressionDeploymentFrequencyDrop` fires when the 7-day average drops below 70% of the 30-day average.

### What to check
- Short-term deploy downturn vs. baseline.
- Whether a migration or outage is affecting team shipping.
- Whether the raw metric is missing or the signal is valid.

### Triage
1. Check the current deployment trend and whether it is a genuine channel slowdown.
2. Review recent blocked change or migration work.
3. Reconfirm the DORA profile and event flow before concluding there is a real drop.

### Remediation
- Restore deploy throughput or unblock the pipeline causing the drop.

## Deployment Frequency Drop Absent

### Trigger
`DORARegressionDeploymentFrequencyDropAbsent` fires when `dora_deployment_frequency_per_week` is absent.

### What to check
- `absent(dora_deployment_frequency_per_week)`
- The compute pipeline feeding deployment metrics
- `dora-api` scrape availability

### Triage
1. Verify the DORA profile and compute loop are still running.
2. Check the underlying deployment-event source.
3. Confirm the metrics endpoint is still serving values.

### Remediation
- Restart or repair the compute/export path so deployment metrics resume.

## Lead Time Increase

### Trigger
`DORARegressionLeadTimeIncrease` fires when the 7-day lead-time median exceeds 150% of the 30-day baseline.

### What to check
- Review queue buildup or approval delay.
- Recent change size and release delays.
- Whether the signal is simply missing or misclassified.

### Triage
1. Compare the short-term lead-time pattern to the recent 30-day average.
2. Check for PR bottlenecks or slow review/test stages.
3. Confirm the series is not missing due to a pipeline problem.

### Remediation
- Remove the bottleneck in review or testing and reduce change size.

## Lead Time Increase Absent

### Trigger
`DORARegressionLeadTimeIncreaseAbsent` fires when the lead-time metric is absent.

### What to check
- `absent(dora_lead_time_p50_hours)`
- Underlying deployment and merge event feed
- DORA profile health

### Triage
1. Verify data source availability.
2. Recheck the DORA profile and compute pipeline.
3. Confirm `dora-api` is still scraped.

### Remediation
- Repair the lead-time data source and verify the series returns.

## FDRT Spike

### Trigger
`DORARegressionFDRTSpike` fires when the current FDRT value doubles the 30-day average.

### What to check
- Recovery time after failed deployments.
- Rollback execution path and change quality.
- Whether the metric is being emitted correctly.

### Triage
1. Review the failed deploy and recovery path.
2. Check whether the rollback or corrective action is delayed.
3. Confirm the DORA profile is intact and not silently dropping recovery data.

### Remediation
- Reduce mean time to recover by fixing the rollback path and response process.

## FDRT Spike Absent

### Trigger
`DORARegressionFDRTSpikeAbsent` fires when the FDRT metric is absent.

### What to check
- `absent(dora_fdrt_p50_hours)`
- DORA profile and deployment failure stream
- `dora-api` metrics endpoint

### Triage
1. Verify the failure/recovery event stream still reaches the compute layer.
2. Check the DORA profile and API scrape state.
3. Investigate any compute or exporter crash.

### Remediation
- Restore the compute/export path so FDRT is available again.

## CFR Spike

### Trigger
`DORARegressionCFRSpike` fires when CFR rises more than 5 percentage points above the 30-day average.

### What to check
- Recent deployment quality and rollbacks.
- Whether CFR is being computed from the right event stream.
- If the ratio/percent conversion is correct.

### Triage
1. Check the last several deployments and their outcomes.
2. Correlate with rollback or incident volumes.
3. Ensure the metric is read as a 0-1 ratio and not a percent-like value.

### Remediation
- Fix the failing deploy pattern and reduce release risk.

## CFR Spike Absent

### Trigger
`DORARegressionCFRSpikeAbsent` fires when the CFR metric is absent.

### What to check
- `absent(dora_cfr_pct)`
- DORA profile and deployment outcome stream
- `dora-api` scrape health

### Triage
1. Verify the deployment outcome stream is still ingesting success/failure data.
2. Check the DORA compute pipeline for a crash or misconfiguration.
3. Confirm the metrics endpoint remains live.

### Remediation
- Restore the deployment outcome path and revalidate the metric.

## Rework Rate Climb

### Trigger
`DORARegressionReworkRateClimb` fires when rework rate rises more than 3 percentage points above the 30-day average.

### What to check
- Recent AI-generated changes that required follow-up fixes.
- Prompt and instruction quality.
- Whether the rework metric is being computed correctly.

### Triage
1. Review whether the recent model or instruction changes are creating worse outputs.
2. Inspect PR-level rework and review comments.
3. Validate the metric is using the right ratio scale.

### Remediation
- Adjust AGENTS.md and prompt guidance to reduce rework.
- Reduce AI scope until the trend stabilizes.

## Rework Rate Climb Absent

### Trigger
`DORARegressionReworkRateClimbAbsent` fires when rework-rate data disappears.

### What to check
- `absent(dora_rework_rate_pct)`
- The DORA profile and compute pipeline
- `dora-api` scrape health

### Triage
1. Verify the metric generation path still runs.
2. Check if a compute error or exporter issue stopped data production.
3. Confirm `dora-api` is still scraped.

### Remediation
- Repair the compute/export path and validate the rework metric returns.
