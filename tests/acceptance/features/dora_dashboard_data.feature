@full
Feature: DORA dashboard panels have real data (not just provisioned)
  Existing dashboard-provisioning checks only verify a dashboard's UID is
  registered in Grafana — never that its panel queries return real data.
  That gap let dora-overview.json go blank ("No data" on every panel)
  without any acceptance test catching it. These scenarios close that gap
  for the DORA-branded dashboards specifically.

  Background:
    Given the core observability stack is running
    And a real DORA deployment event has been sent

  @dora
  Scenario: DORA Overview ("DORA 2025 framework") shows real data
    # Lead Time / FDRT panels are a real, tracked gap (issue #267), not a
    # test bug: dora_lead_time_p50_hours and dora_fdrt_p50_hours have zero
    # data anywhere in Prometheus, because computing them needs
    # first_commit_at (PR-event data) and incident-duration events, and
    # nothing in this repo sends either yet. Deployment Frequency, Change
    # Failure Rate, and Rework Rate are all genuinely fed and asserted here.
    Then the dashboard "ufawkesobs-dora-overview" panels should return real, labeled data, except known gaps "Lead Time for Changes|Failed Deployment Recovery Time (FDRT)|Lead Time Trend|FDRT Trend"

  # dora-metrics.json ("DORA 2026 — Five Key Metrics") is a KNOWN gap, not
  # tested here on purpose: its panels query an OTel-native pipeline
  # (dora_deployment_succeeded_total, dora_deployment_lead_time_hours_bucket,
  # dora_incident_duration_hours_bucket) that nothing in this repo currently
  # feeds — see issue #266. Its recording rules fall back to an unlabeled
  # `or vector(0)`, which is exactly the failure mode this feature file
  # exists to catch, so asserting against it here would just re-file #266
  # as a permanently-red test. Add a scenario for it once #266 is resolved.

  # No dashboard named "DORA AI report" or "DORA 2026 ROI report" exists in
  # this repo (confirmed: zero "ROI" mentions anywhere in dashboards/,
  # docs/dora/, or docs/product/). The closest match to an "AI" dashboard is
  # dashboards/platform/ai-capabilities.json (uid: platform-ai-capabilities),
  # which isn't DORA-branded and doesn't share the dora-compute pipeline this
  # feature file targets — it's covered by its own existing acceptance
  # coverage, not duplicated here. If a DORA-specific AI or ROI dashboard is
  # wanted, it needs to be designed and built first; this feature file has
  # the reusable step ("the dashboard ... panels should return real, labeled
  # data") ready to cover it once it exists.
